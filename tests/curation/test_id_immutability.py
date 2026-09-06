"""B3 (Scope B): TDD cases for ID immutability (scripts/check_id_immutability.py).

The invariant (ADR-0003, plan v4.0): once an `stemma:` identifier has represented a canonical
entity, it can never later represent a different entity or meaning. The plan's six cases:

    1. new                  -> PASS
    2. unchanged identity   -> PASS
    3. deprecated           -> PASS
    4. aliased              -> PASS (alias references must be valid)
    5. reassigned           -> FAIL (same id now means a different entity)
    6. deleted-and-reused   -> FAIL (id deleted, then a different entity reused it)

The detection core `detect_violations(history, live)` is pure (dict-in, list-out), so these
cases are exercised directly without needing to construct git fixtures.
"""
import importlib.util
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("idcheck", ROOT / "scripts" / "check_id_immutability.py")
idcheck = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(idcheck)
detect = idcheck.detect_violations


def _v(commit, name, domain, status="draft", **extra):
    d = {"commit": commit, "name": name, "domain": domain, "status": status}
    d.update(extra)
    return d


def _ent(id_, name, domain, status="draft", **extra):
    d = {"id": id_, "name": name, "domain": domain, "status": status}
    d.update(extra)
    return d


def test_new_id_passes():
    hist = {"stemma:phys.a": [_v("1", "A", "physics")]}
    live = {"stemma:phys.a": _ent("stemma:phys.a", "A", "physics")}
    assert detect(hist, live) == []
    print("PASS: case 1 new id")


def test_unchanged_identity_passes():
    # name/domain identical across all versions (only prose could differ — not captured)
    hist = {"stemma:math.f": [_v("1", "Function", "mathematics"), _v("2", "Function", "mathematics")]}
    live = {"stemma:math.f": _ent("stemma:math.f", "Function", "mathematics")}
    assert detect(hist, live) == []
    print("PASS: case 2 unchanged identity")


def test_deprecated_passes():
    # deprecated ids are reserved forever; deprecation is the legal retirement path.
    hist = {"stemma:phys.old": [_v("1", "Old Model", "physics", "draft"), _v("2", "Old Model", "physics", "deprecated")]}
    live = {"stemma:phys.new": _ent("stemma:phys.new", "New Model", "physics")}  # old id deprecated, gone from HEAD
    assert detect(hist, live) == []
    print("PASS: case 3 deprecated")


def test_aliased_passes():
    # id A aliases (points to) B which is a known id; alias validity holds.
    hist = {"stemma:phys.b": [_v("1", "B", "physics")]}
    live = {
        "stemma:phys.a": _ent("stemma:phys.a", "B (old name)", "physics", "deprecated", deprecated_by="stemma:phys.b"),
        "stemma:phys.b": _ent("stemma:phys.b", "B", "physics"),
    }
    assert detect(hist, live) == [], detect(hist, live)
    print("PASS: case 4 aliased")
    # ... but an alias to a nonexistent id must FAIL
    bad = {
        "stemma:phys.a": _ent("stemma:phys.a", "A", "physics", "deprecated", deprecated_by="stemma:does-not-exist"),
    }
    assert any("[alias-invalid]" in m for m in detect(hist, bad))
    print("PASS: case 4b invalid alias fails")


def test_reassigned_fails():
    # same id now means a DIFFERENT entity (name changed) -> must fail.
    hist = {"stemma:phys.x": [_v("1", "Classical Mechanics", "physics"), _v("2", "Quantum Mechanics", "physics")]}
    live = {"stemma:phys.x": _ent("stemma:phys.x", "Quantum Mechanics", "physics")}
    vs = detect(hist, live)
    assert any("[reassigned]" in m for m in vs), vs
    print("PASS: case 5 reassigned fails")


def test_deleted_and_reused_fails():
    # id present, deleted, then a DIFFERENT entity reused the same id -> must fail.
    hist = {"stemma:phys.y": [_v("1", "First Meaning", "physics"), _v("3", "Different Meaning", "physics")]}
    live = {"stemma:phys.y": _ent("stemma:phys.y", "Different Meaning", "physics")}
    vs = detect(hist, live)
    assert any("[reassigned]" in m for m in vs), vs
    print("PASS: case 6 deleted-and-reused fails")


def test_deleted_without_deprecation_fails():
    # id silently dropped from HEAD without status: deprecated -> flagged.
    hist = {"stemma:chem.z": [_v("1", "Z", "chemistry", "draft")]}
    live = {}  # gone without deprecation
    assert any("[deleted-without-deprecation]" in m for m in detect(hist, live))
    print("PASS: case 6b deleted-without-deprecation fails")


if __name__ == "__main__":
    test_new_id_passes()
    test_unchanged_identity_passes()
    test_deprecated_passes()
    test_aliased_passes()
    test_reassigned_fails()
    test_deleted_and_reused_fails()
    test_deleted_without_deprecation_fails()
    print("ALL ID-IMMUTABILITY TESTS PASS")