"""Pins the facts that docs/VERSIONING.md ("Consumer versioning and release policy") relies on.

If one of these fails, either the behaviour regressed or the policy text must change.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "adapters" / "python"))

from stemma_adapter import ExportError, Stemma  # noqa: E402
from stemma_adapter import release as sdk_release  # noqa: E402

EXPORT = json.loads((ROOT / "exports" / "knowledge.json").read_text(encoding="utf-8"))
VERSIONS = yaml.safe_load((ROOT / "schema" / "VERSION.yaml").read_text(encoding="utf-8"))
RELEASE_VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()


# §1 independent numbers --------------------------------------------------------

def test_release_version_is_semver_and_stamped_as_kernel_version():
    assert re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", RELEASE_VERSION)
    assert EXPORT["kernel_version"] == RELEASE_VERSION
    assert EXPORT["export_version"] == VERSIONS["export_version"]
    assert EXPORT["schema_version"] == VERSIONS["schema_version"]


def test_export_version_is_not_aligned_to_release_version():
    """Owner decision: export_version stays on its own line (2.x), not 3.x."""
    assert VERSIONS["export_version"].split(".")[0] == "2"


def test_release_workflow_and_sdk_accept_the_same_tags():
    wf = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
    assert "^v([0-9]+\\.[0-9]+\\.[0-9]+)(-rc[0-9]+)?$" in wf
    assert sdk_release._TAG.pattern == r"v[0-9]+\.[0-9]+\.[0-9]+(?:-rc[0-9]+)?"
    assert 'flag="--draft"' in wf  # final = draft until the owner signs (§7)


# §3 breaking vs additive (SDK forward compatibility) -----------------------------

def _load(mutate):
    data = copy.deepcopy(EXPORT)
    mutate(data)
    return Stemma.from_dict(data)


@pytest.mark.parametrize("label,mutate", [
    ("new top-level member", lambda d: d.__setitem__("future_member", {"x": 1})),
    ("new entity member", lambda d: d["entities"][0].__setitem__("future_field", 1)),
    ("new connection member", lambda d: d["connections"][0].__setitem__("future_field", 1)),
    ("new status value", lambda d: d["entities"][0].__setitem__("status", "future_status")),
    ("higher export minor", lambda d: d.__setitem__("export_version", "2.99.0")),
])
def test_additive_changes_keep_old_readers_working(label, mutate):
    _load(mutate)


def _valued_index():
    return next(i for i, c in enumerate(EXPORT["connections"]) if c.get("value"))


@pytest.mark.parametrize("label,mutate,match", [
    ("new value-slot member",
     lambda d: d["connections"][_valued_index()]["value"].__setitem__("uncertainty", "0.1"), "unknown member"),
    ("next export major", lambda d: d.__setitem__("export_version", "3.0.0"), "unsupported export major"),
])
def test_breaking_changes_are_refused(label, mutate, match):
    with pytest.raises(ExportError, match=match):
        _load(mutate)


def test_value_slot_is_closed_in_the_export_schema_too():
    schema = json.loads((ROOT / "schema" / "export.schema.json").read_text(encoding="utf-8"))
    value = schema["properties"]["connections"]["items"]["properties"]["value"]
    assert value["additionalProperties"] is False


# §4 content_hash definition --------------------------------------------------------

def test_content_hash_covers_exactly_the_canonical_sources():
    hasher = hashlib.sha256()
    for directory in ("content", "connections", "sources"):
        base = ROOT / directory
        if not base.exists():
            continue
        for path in sorted(p for p in base.rglob("*") if p.is_file()):
            hasher.update(str(path.relative_to(ROOT)).encode("utf-8") + b"\x00")
            hasher.update(path.read_bytes() + b"\x00")
    assert EXPORT["content_hash"] == f"sha256:{hasher.hexdigest()}"


# §6 where changes are recorded -----------------------------------------------------

@pytest.mark.parametrize("key", ["export_version", "schema_version", "relation_registry_version"])
def test_current_versions_have_a_migrations_entry(key):
    text = (ROOT / "docs" / "MIGRATIONS.md").read_text(encoding="utf-8")
    value = VERSIONS[key]
    assert any(key in line and value in line for line in text.splitlines()), \
        f"docs/MIGRATIONS.md needs an entry naming {key} {value}"


def test_adapter_version_has_a_changelog_entry():
    import stemma_adapter

    changelog = (ROOT / "adapters" / "python" / "CHANGELOG.md").read_text(encoding="utf-8")
    assert re.search(rf"^## {re.escape(stemma_adapter.__version__)}\b", changelog, re.M)

