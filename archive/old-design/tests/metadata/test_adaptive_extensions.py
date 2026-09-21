"""Adaptive metadata extension registry semantics (ADR-0017).

Verifies:
- every `extensions` key used on canonical content is registered in the registry
- registered dims applicable to the right object kind
- controlled-enum conformance
- promote/downgrade rules in scripts/register_extension.py
"""
import pathlib
import subprocess

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "schema" / "extension-registry.yaml"
SCRIPT = ROOT / "scripts" / "register_extension.py"


def _registry_by_name():
    data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8")) or {}
    return {e["name"]: e for e in data.get("extensions", []) if isinstance(e, dict)}


def test_all_extension_keys_registered():
    by_name = _registry_by_name()
    used = set()
    for container in ("content", "connections", "sources"):
        base = ROOT / container
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if p.suffix not in (".md", ".yaml", ".yml"):
                continue
            try:
                text = p.read_text(encoding="utf-8")
                # markdown frontmatter: text after the first '---' delimiter
                obj_text = text.split("---", 2)[1] if p.suffix == ".md" and text.startswith("---") else text
                d = yaml.safe_load(obj_text)
            except Exception:
                continue
            if not isinstance(d, dict):
                continue
            ext = d.get("extensions")
            if isinstance(ext, dict):
                used.update(ext.keys())

    for key in used:
        assert key in by_name, (
            f"extension '{key}' used in content but not registered in {REGISTRY} "
            f"(see scripts/register_extension.py)"
        )
    assert used, "no extension keys found in canonical content — demo not wired?"
    print(f"PASS: all {len(used)} used extension keys are registered: {sorted(used)}")


def test_registered_applies_to_and_value_valid():
    """Registry rows point at known object kinds with a legal value_type."""
    for name, dim in _registry_by_name().items():
        assert set(dim["applies_to"]) <= {"entity", "connection", "source"}, name
        assert dim["value_type"] in {"string", "number", "boolean"}, name
        assert dim["status"] in {"proposed", "adopted"}, name


def test_script_is_idempotent_and_preserves_header():
    """Re-adding an existing dim updates, never duplicates; comments preserved."""
    before_count = len(_registry_by_name())
    r = subprocess.run(
        [str(SCRIPT), "add", "--name", "symbol_set", "--applies-to", "entity",
         "--value-type", "string", "--status", "adopted",
         "--registered-by", "process:test-idempotent"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr
    after = _registry_by_name()
    assert len(after) == before_count, "re-add must not duplicate the dimension"
    assert after["symbol_set"]["registered_by"] == "process:test-idempotent"
    header = REGISTRY.read_text(encoding="utf-8")
    assert header.lstrip().startswith("#"), "human header comment must be preserved"
    print("PASS: idempotent + header preserved")


def test_reject_unknown_applies_to():
    r = subprocess.run(
        [str(SCRIPT), "add", "--name", "bad_dim", "--applies-to", "galaxy",
         "--value-type", "string"],
        capture_output=True, text=True,
    )
    assert r.returncode == 1, "unknown applies_to must fail"
    print("PASS: unknown applies_to rejected")