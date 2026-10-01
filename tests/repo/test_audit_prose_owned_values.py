#!/usr/bin/env python3
"""The OPS-002 per-release audit instrument must actually measure something.

`scripts/audit_prose_owned_values.py` is the owner-ruled instrument for
REQ-STEMMA-OPS-002. It is not a gate, so nothing else would catch it silently
rotting into a script that returns empty results and makes the "trend" look
flat because it stopped looking.

These tests pin its contract:
  * it reads machine-owned counts from the gated README status block, not a
    second source;
  * it actually finds prose count-mentions in this repository (non-vacuous);
  * exemption rules work, so the number is a bounded review surface and not
    a firehose of historical records;
  * it never writes to the repository.
"""
from __future__ import annotations

import importlib.util
import pathlib
import re
import subprocess

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "audit_prose_owned_values.py"


def _load():
    spec = importlib.util.spec_from_file_location("audit_prose_owned_values", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


audit_mod = _load()


def test_reads_counts_from_the_gated_status_block():
    """The counts must come from the status block, not be invented."""
    counts = audit_mod.live_counts_at("HEAD")
    assert counts, "no machine-owned counts read from README's status block"
    assert set(counts) == {"entities", "connections", "sources"}, counts
    for name, value in counts.items():
        assert isinstance(value, int) and value >= 0, (name, value)


def test_audit_is_non_vacuous_at_head():
    """If this returns nothing, the instrument has stopped measuring."""
    rec = audit_mod.audit("HEAD")
    assert rec["machine_owned_counts"], "counts empty"
    mentions = rec["prose_count_mentions"]
    assert mentions["occurrences"] > 0, (
        "the audit found zero prose count-mentions in the whole repository — "
        "either the corpus lost all prose, or the detector broke"
    )
    assert mentions["files"] > 0


def test_exempt_paths_are_respected():
    """Historical records and the single source must not inflate the surface."""
    for path in ("README.md", "CHANGELOG.md", "PROGRESS.md",
                 "docs/decisions/0050-contract-update-2.2.0.md",
                 "docs/MIGRATIONS.md"):
        assert audit_mod._is_exempt(path), f"{path} should be exempt"
    for path in ("docs/VISION.md", "docs/GOVERNANCE.md"):
        assert not audit_mod._is_exempt(path), f"{path} should be audited"


def test_count_pattern_does_not_match_unrelated_numbers():
    """'12 entity types' is a type count, not an entity count — the pattern must
    still match it (it is prose), but the point here is that the counter
    distinguishes the kind label: '3 sources' is sources, '3 entities' is
    entities."""
    entities = audit_mod.COUNT_PATTERNS["entities"].findall("we have 3 entities")
    assert entities == ["3"]
    assert audit_mod.COUNT_PATTERNS["sources"].findall("we have 3 entities") == []
    assert audit_mod.COUNT_PATTERNS["sources"].findall("3 sources") == ["3"]


def test_stale_classification_compares_against_live_counts():
    rec = audit_mod.audit("HEAD")
    live = rec["machine_owned_counts"]
    for item in rec["stale_prose_mentions"]["items"]:
        assert item["kind"] in live
        assert item["value"] != live[item["kind"]]


def test_instrument_never_writes():
    """Read-only: no write/open-for-write/checkout in the source."""
    src = SCRIPT.read_text(encoding="utf-8")
    for forbidden in ("write_text", "open(", '"w"', ".write(", "git checkout",
                      "checkout ", "subprocess.run([\"git\", \"checkout"):
        assert forbidden not in src, f"instrument must be read-only: found {forbidden!r}"


def test_run_at_a_release_tag_returns_a_record():
    """The documented invocation must work against a real tag."""
    tags = subprocess.run(["git", "tag", "--list"], cwd=ROOT, capture_output=True,
                          text=True).stdout.split()
    if not tags:
        pytest.skip("no tags in this clone")
    rec = audit_mod.audit(sorted(tags)[0])
    assert rec["revision"] == sorted(tags)[0]
    assert rec["machine_owned_counts"]


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
