"""Claim identity tests — plan v2 E4.3 (claim signature + duplicate-claim gate), ADR-0026.

A connection is a *record*; the claim it asserts is (source, relation, target, polarity,
qualifiers). The signature identifies the claim, so two active connections sharing one
signature are the same claim asserted twice — a gate failure, not a style nit.

The signature is DERIVED: never stored in canonical YAML, emitted into the export so
consumers can deduplicate without recomputing.
"""
import json
import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import validate as v  # noqa: E402


def _conn(cid="stemma:conn.000001", source="stemma:phys.mass", relation="mathematically_requires",
          target="stemma:phys.force", polarity="positive", qualifiers=(), status="active"):
    return {
        "id": cid,
        "type": "connection",
        "source": source,
        "relation": relation,
        "target": target,
        "assertion": {
            "status": status,
            "type": "proposed",
            "review": {"status": "unreviewed"},
            "polarity": polarity,
        },
        "context": {"domain": "physics", "subdomain": "mechanics",
                    "qualifiers": list(qualifiers)},
        "provenance": {},
    }


def test_signature_is_deterministic():
    a = v.claim_signature(_conn())
    b = v.claim_signature(_conn())
    assert a == b, "claim signature must be deterministic"
    assert a.startswith("sha256:") and len(a) == 71, a
    print("PASS: claim signature is deterministic and well-formed")


def test_signature_covers_every_claim_component():
    base = v.claim_signature(_conn())
    assert base != v.claim_signature(_conn(source="stemma:phys.acceleration"))
    assert base != v.claim_signature(_conn(relation="part_of"))
    assert base != v.claim_signature(_conn(target="stemma:phys.energy"))
    assert base != v.claim_signature(_conn(polarity="negative"))
    assert base != v.claim_signature(_conn(qualifiers=[{"type": "condition", "value": "vacuum"}]))
    print("PASS: signature covers source/relation/target/polarity/qualifiers")


def test_qualifier_order_is_irrelevant():
    q1 = [{"type": "condition", "value": "vacuum"}, {"type": "system", "value": "closed"}]
    q2 = list(reversed(q1))
    assert v.claim_signature(_conn(qualifiers=q1)) == v.claim_signature(_conn(qualifiers=q2))
    print("PASS: qualifier ordering does not change the claim signature")


def test_missing_polarity_defaults_to_positive():
    conn = _conn()
    del conn["assertion"]["polarity"]
    assert v.claim_signature(conn) == v.claim_signature(_conn(polarity="positive"))
    print("PASS: absent polarity defaults to positive (connection.schema.json default)")


def test_duplicate_active_claims_are_rejected():
    errors = []
    connections = {
        "stemma:conn.000001": _conn(cid="stemma:conn.000001"),
        "stemma:conn.000002": _conn(cid="stemma:conn.000002"),
    }
    v.check_duplicate_claims(connections, errors)
    assert len(errors) == 1 and "duplicate claim" in errors[0], errors
    assert "stemma:conn.000001" in errors[0] and "stemma:conn.000002" in errors[0]
    print("PASS: two active connections asserting one claim fail the gate")


def test_distinct_claims_pass():
    errors = []
    connections = {
        "stemma:conn.000001": _conn(cid="stemma:conn.000001"),
        "stemma:conn.000002": _conn(cid="stemma:conn.000002", target="stemma:phys.energy"),
    }
    v.check_duplicate_claims(connections, errors)
    assert errors == [], errors
    print("PASS: distinct claims pass")


def test_superseded_duplicate_is_allowed():
    """A retired duplicate is history, not a live contradiction."""
    errors = []
    connections = {
        "stemma:conn.000001": _conn(cid="stemma:conn.000001", status="superseded"),
        "stemma:conn.000002": _conn(cid="stemma:conn.000002"),
    }
    signatures = v.check_duplicate_claims(connections, errors)
    assert errors == [], errors
    assert "stemma:conn.000001" not in signatures, "retired connections carry no active signature"
    print("PASS: a superseded duplicate does not fail the gate")


def test_canonical_tree_has_no_duplicate_active_claims():
    connections = {}
    for path in sorted((ROOT / "connections").glob("*.yaml")):
        conn = yaml.safe_load(path.read_text(encoding="utf-8"))
        conn["_file"] = str(path.relative_to(ROOT))
        connections[conn["id"]] = conn
    assert len(connections) > 600, f"unexpected connection count: {len(connections)}"
    errors = []
    v.check_duplicate_claims(connections, errors)
    assert errors == [], errors[:5]
    print(f"PASS: no duplicate active claims among {len(connections)} canonical connections")


def test_export_carries_derived_claim_signatures():
    """The committed export must carry the derived signature for every connection.

    Freshness is guaranteed by the CI gate `git diff --exit-code -- exports/` (E5.2), so a
    missing field here means the export was generated before E4.3 — regenerate it.
    """
    export = json.loads((ROOT / "exports" / "knowledge.json").read_text(encoding="utf-8"))
    bad = [c["id"] for c in export["connections"] if not str(c.get("claim_signature", "")).startswith("sha256:")]
    assert not bad, f"connections missing a derived claim_signature: {bad[:5]} — run python3 scripts/validate.py"
    ids = [c["claim_signature"] for c in export["connections"]]
    active = [c for c in export["connections"] if c["assertion"]["status"] == "active"]
    active_sigs = [c["claim_signature"] for c in active]
    assert len(active_sigs) == len(set(active_sigs)), "active connections share a claim signature"
    print(f"PASS: export carries {len(ids)} derived claim signatures (no active duplicates)")


def test_policy_views_carry_claim_signatures():
    for policy in ("all", "reviewed", "canonical", "trusted"):
        path = ROOT / "exports" / f"knowledge.{policy}.json"
        if not path.exists():
            continue
        view = json.loads(path.read_text(encoding="utf-8"))
        missing = [c["id"] for c in view["connections"] if not str(c.get("claim_signature", "")).startswith("sha256:")]
        assert not missing, f"{path.name}: connections without claim_signature: {missing[:5]}"
    print("PASS: review-aware policy exports carry derived claim signatures")


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
    print("ALL CLAIM-IDENTITY TESTS PASS")
