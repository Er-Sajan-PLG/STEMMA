"""Q1.2 tests: deterministic YAML duplicate-key detection.

Verifies that scripts/validate.py's load_yaml_strict rejects duplicate mapping
keys (top-level and nested) instead of silently keeping the last value, and that
the repair tool merges duplicate list-valued keys losslessly.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))


def test_validate_rejects_duplicate_top_level_key() -> None:
    import validate

    try:
        validate.load_yaml_strict("a: 1\nb: 2\na: 3\n", where="case")
    except ValueError as exc:
        assert "/a" in str(exc)
    else:
        raise AssertionError("expected ValueError for duplicate top-level key")


def test_validate_rejects_duplicate_nested_key() -> None:
    import validate

    try:
        validate.load_yaml_strict("a:\n  b: 1\n  b: 2\n", where="case")
    except ValueError as exc:
        assert "/a/b" in str(exc)
    else:
        raise AssertionError("expected ValueError for duplicate nested key")


def test_validate_accepts_clean_yaml() -> None:
    import validate

    data = validate.load_yaml_strict("a: 1\nb:\n  c: 2\n", where="case")
    assert data == {"a": 1, "b": {"c": 2}}


def test_no_duplicate_keys_in_extension_registry() -> None:
    """The extension registry must have a single version: key (regression for Q1.2)."""
    text = (ROOT / "schema" / "extension-registry.yaml").read_text(encoding="utf-8")
    version_lines = [ln for ln in text.splitlines() if ln.strip().startswith("version:")]
    assert len(version_lines) == 1, f"expected 1 version: key, found {len(version_lines)}"


def test_repair_merges_duplicate_list_keys_lossless() -> None:
    """The repair tool unions duplicate list-valued keys without losing content."""
    import repair_duplicate_keys

    dup_yaml = "key_experiments:\n- A\n- B\nkey_experiments:\n- B\n- C\nname: X\n"
    repaired, reports = repair_duplicate_keys.merge_document(dup_yaml)
    data = yaml.safe_load(repaired)
    assert set(data["key_experiments"]) == {"A", "B", "C"}
    assert data["name"] == "X"
    # no duplicates reported as last-wins (they were unioned)
    assert all("unioned" in r for r in reports), reports


def test_repair_is_idempotent() -> None:
    """Repairing an already-clean doc changes nothing."""
    import repair_duplicate_keys

    clean = "name: X\nkey_experiments:\n- A\n- B\n"
    repaired, reports = repair_duplicate_keys.merge_document(clean)
    assert reports == []
    assert repaired == clean


def test_validate_passes_on_current_repo() -> None:
    """The authoritative gate passes on the current canonical content + connections.

    This is the integration guarantee that Q1.2/Q2 did not break the gate, and that
    the repaired entities (duplicate-key fix) are schema-valid.
    """
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate.py")],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, f"validate.py failed:\n{r.stderr[-2000:]}"
    assert "224 entities valid" in r.stdout