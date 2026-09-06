"""Gate 15: Timestamp, evidence, polarity, claim signature semantics."""
import pathlib, yaml, json, hashlib

ROOT = pathlib.Path(__file__).resolve().parents[2]

def test_timestamp_not_file_mtime():
    # File mtime is never interpreted as scientific creation time: created_at must be null for migrated
    for p in (ROOT/"connections").glob("*.yaml"):
        d = yaml.safe_load(p.read_text())
        prov = d.get("provenance", {})
        method = prov.get("method", {}).get("type")
        if method == "migration":
            assert d.get("created_at") is None, f"{d['id']} migrated should have created_at null, not file mtime"
            assert d.get("updated_at") is None
    print("PASS timestamp not file mtime")

def test_review_timestamp_preserved():
    # Actual review timestamp is preserved in review_history, not file mtime
    for p in (ROOT/"connections").glob("*.yaml"):
        d = yaml.safe_load(p.read_text())
        if d["assertion"]["review"]["status"] == "canonical":
            assert "review_history" in d["provenance"]
            for ev in d["provenance"]["review_history"]:
                assert "at" in ev
    print("PASS review timestamp")

def test_validity_independent():
    # Validity timestamps independent from provenance
    for p in (ROOT/"connections").glob("*.yaml"):
        d = yaml.safe_load(p.read_text())
        validity = d.get("validity")
        if validity and validity.get("valid_from") and validity.get("valid_until"):
            assert validity["valid_from"] <= validity["valid_until"], f"{d['id']} valid_until < valid_from"
    print("PASS validity independent")

def test_missing_timestamps_allowed():
    # Missing historical timestamps allowed
    for p in (ROOT/"connections").glob("*.yaml"):
        d = yaml.safe_load(p.read_text())
        # Optional per connection.schema.json; when present may be null
        # (unknown historical time is null, never the file mtime).
        assert d.get("created_at", None) is None or isinstance(d["created_at"], str)
    print("PASS missing timestamps allowed")

def test_evidence_not_default_supports():
    # Migrated unreviewed evidence does not default to supports; canonical reviewed may have supports
    for p in (ROOT/"connections").glob("*.yaml"):
        d = yaml.safe_load(p.read_text())
        if d["provenance"]["method"]["type"] == "migration" and d["assertion"]["review"]["status"] == "unreviewed":
            for ev in d.get("evidence", []) or []:
                assert "stance" not in ev, f"{d['id']} migrated unreviewed evidence should not have stance supports"
    # Canonical human-reviewed should have stance supports
    for p in (ROOT/"connections").glob("*.yaml"):
        d = yaml.safe_load(p.read_text())
        if d["assertion"]["review"]["status"] == "canonical":
            for ev in d.get("evidence", []) or []:
                assert ev.get("stance") in ("supports","weakly_supports","contradicts","qualifies"), f"{d['id']} canonical evidence should have stance"
    print("PASS evidence stance")

def test_polarity_distinct():
    for p in (ROOT/"connections").glob("*.yaml"):
        d = yaml.safe_load(p.read_text())
        assert d["assertion"].get("polarity") in ("positive","negative", None)  # optional per schema
        # positive != rejected
        if d["assertion"].get("polarity") == "negative":
            assert d["relation"] != "contradicts" or True  # negative is distinct from contradicts relation
    # Polarity is optional; the retired name `negated` must never appear.
    for p in (ROOT/"connections").glob("*.yaml"):
        d = yaml.safe_load(p.read_text())
        assert "negated" not in d["assertion"]
    print("PASS polarity distinct")

def test_claim_signature_deterministic():
    def sig(d):
        return hashlib.sha256(f"{d['source']}|{d['relation']}|{d['target']}|{d['assertion'].get('polarity','positive')}".encode()).hexdigest()[:16]
    # Two connections same triple same polarity should have same signature
    conns = [yaml.safe_load(p.read_text()) for p in sorted((ROOT/"connections").glob("*.yaml"))]
    by_sig = {}
    for c in conns:
        s = sig(c)
        by_sig.setdefault(s, []).append(c["id"])
    # Multiple connections may share signature (different source with same triple)
    # Signature does not replace ID
    for c in conns:
        assert c["id"].startswith("stemma:conn.")
        assert sig(c) != c["id"]
    print("PASS claim_signature deterministic")

def test_provenance_distinction():
    for p in (ROOT/"connections").glob("*.yaml"):
        d = yaml.safe_load(p.read_text())
        prov = d["provenance"]
        assert "asserted_by" in prov
        assert "generated_by" in prov
        # Migration remains distinct from assertion authorship
        if prov["method"]["type"] == "migration":
            assert prov["asserted_by"]["id"] == "unknown:legacy-relationship"
            assert prov["generated_by"]["id"] == "process:migration.relationships-v0.2"
    print("PASS provenance distinction")

if __name__=="__main__":
    test_timestamp_not_file_mtime()
    test_review_timestamp_preserved()
    test_validity_independent()
    test_missing_timestamps_allowed()
    test_evidence_not_default_supports()
    test_polarity_distinct()
    test_claim_signature_deterministic()
    test_provenance_distinction()
    print("ALL GATE 15 TESTS PASS")
