"""Connection-triple immutability tests — plan v2 E4.5, ADR-0026.

`stemma:conn.NNNNNN` identifies one assertion. What it *means* is the triple
(source, relation, target): editing that triple in place silently rewrites history for
every consumer holding the id. The legal correction path is supersession —
`assertion.status: superseded` + `lifecycle.replaced_by` — plus a NEW id for the new claim.

`detect_connection_violations(history, live)` is pure (dict-in, list-out), so the cases below
are exercised without constructing git fixtures. `scripts/check_id_immutability.py` supplies
the real history from git in CI (checkout with `fetch-depth: 0`).
"""
import importlib.util
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "idcheck", ROOT / "scripts" / "check_id_immutability.py"
)
idcheck = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(idcheck)

detect = idcheck.detect_connection_violations
parse = idcheck.parse_connection


def _v(commit, source, relation, target, status="active", replaced_by=None):
    return {"commit": commit, "source": source, "relation": relation, "target": target,
            "status": status, "replaced_by": replaced_by}


def test_new_connection_passes():
    hist = {"stemma:conn.000001": [_v("1", "stemma:phys.mass", "part_of", "stemma:phys.matter")]}
    live = {"stemma:conn.000001": _v("1", "stemma:phys.mass", "part_of", "stemma:phys.matter")}
    assert detect(hist, live) == []
    print("PASS: case 1 new connection")


def test_unchanged_triple_passes():
    """Review status / evidence / context may change freely — the claim itself may not."""
    hist = {
        "stemma:conn.000001": [
            _v("1", "stemma:phys.mass", "part_of", "stemma:phys.matter", "active"),
            _v("2", "stemma:phys.mass", "part_of", "stemma:phys.matter", "active"),
        ]
    }
    live = {"stemma:conn.000001": _v("2", "stemma:phys.mass", "part_of", "stemma:phys.matter")}
    assert detect(hist, live) == []
    print("PASS: case 2 unchanged triple (metadata-only edits) passes")


def test_supersession_passes():
    hist = {
        "stemma:conn.000001": [
            _v("1", "stemma:phys.mass", "part_of", "stemma:phys.matter", "active"),
            _v("2", "stemma:phys.mass", "part_of", "stemma:phys.matter", "superseded",
               replaced_by="stemma:conn.000002"),
        ]
    }
    live = {"stemma:conn.000002": _v("2", "stemma:phys.mass", "part_of", "stemma:phys.body")}
    assert detect(hist, live) == [], detect(hist, live)
    print("PASS: case 3 correction via supersede + new id passes")


def test_triple_edited_in_place_fails():
    hist = {
        "stemma:conn.000001": [
            _v("1", "stemma:phys.mass", "mathematically_requires", "stemma:phys.force", "active"),
            _v("2", "stemma:phys.mass", "mathematically_requires", "stemma:phys.energy", "active"),
        ]
    }
    live = {"stemma:conn.000001": hist["stemma:conn.000001"][-1]}
    violations = detect(hist, live)
    assert any("[connection-triple-changed]" in m for m in violations), violations
    assert any("supersede" in m.lower() for m in violations), violations
    print("PASS: case 4 in-place triple edit fails with remediation guidance")


def test_deleted_without_supersession_fails():
    hist = {"stemma:conn.000001": [_v("1", "stemma:phys.mass", "part_of", "stemma:phys.matter", "active")]}
    violations = detect(hist, {})
    assert any("[connection-deleted-without-supersession]" in m for m in violations), violations
    print("PASS: case 5 connection deleted without supersession fails")


def test_deprecated_deletion_passes():
    hist = {"stemma:conn.000001": [_v("1", "stemma:phys.mass", "part_of", "stemma:phys.matter", "deprecated")]}
    assert detect(hist, {}) == []
    print("PASS: case 6 deprecated-then-removed connection passes")


def test_parse_connection_extracts_identity_fields():
    """The history walker is dependency-free; make sure its parser reads the real shape."""
    sample = (ROOT / "connections" / "conn.000001.yaml").read_text(encoding="utf-8")
    parsed = parse(sample)
    assert parsed["id"] == "stemma:conn.000001", parsed
    assert parsed["relation"], parsed
    assert parsed["source"].startswith("stemma:") and parsed["target"].startswith("stemma:"), parsed
    assert parsed["assertion.status"] == "active", parsed
    assert "lifecycle.replaced_by" not in parsed or parsed["lifecycle.replaced_by"] in (None, "null")
    print("PASS: dependency-free connection parser reads id/source/relation/target/status")


def test_live_connections_cover_every_connection_file():
    live = idcheck.live_connections()
    files = list((ROOT / "connections").glob("*.yaml"))
    assert len(live) == len(files) > 600, f"{len(live)} parsed vs {len(files)} files"
    assert all(cid.startswith("stemma:conn.") for cid in live), list(live)[:3]
    assert all(c["source"] and c["relation"] and c["target"] for c in live.values())
    print(f"PASS: {len(live)} live connections parsed with complete triples")


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
    print("ALL CONNECTION-IMMUTABILITY TESTS PASS")
