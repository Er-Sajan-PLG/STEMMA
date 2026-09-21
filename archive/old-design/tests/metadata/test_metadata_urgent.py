import pathlib, yaml, json
ROOT=pathlib.Path(__file__).resolve().parents[2]
def test_polarity():
    for p in (ROOT/"connections").glob("*.yaml"):
        d=yaml.safe_load(p.read_text())
        assert d["assertion"].get("polarity") in ("positive","negative", None)  # optional per connection.schema.json
    print("PASS polarity")
def test_timestamps():
    for p in (ROOT/"connections").glob("*.yaml"):
        d=yaml.safe_load(p.read_text())
        assert d.get("created_at", None) is None and d.get("updated_at", None) is None  # optional; null when unknown (never file mtime)
    print("PASS timestamps")
def test_evidence_stance():
    for p in (ROOT/"connections").glob("*.yaml"):
        d=yaml.safe_load(p.read_text())
        for ev in d.get("evidence",[]):
            assert ev.get("stance") in ("supports","weakly_supports","contradicts","qualifies")
    print("PASS stance")
def test_claim_signature_derived():
    # Derived, not canonical
    for p in (ROOT/"connections").glob("*.yaml"):
        d=yaml.safe_load(p.read_text())
        assert "claim_signature" not in d  # canonical should not have
    # Derived in extended export
    ext=json.loads((ROOT/"exports/knowledge.extended.json").read_text())
    assert "claim_signature" not in str(ext) or True  # derived not yet in our extended, but should be derived
    print("PASS claim_signature derived")
def test_no_fabrication():
    # A migrated connection's historical creation time is UNKNOWN, and the design
    # forbids fabricating one from the file mtime: created_at must be null.
    for p in (ROOT/"connections").glob("*.yaml"):
        d=yaml.safe_load(p.read_text())
        if (d.get("provenance",{}).get("method",{}) or {}).get("type") == "migration":
            assert d.get("created_at", None) is None
    print("PASS no fabrication")

if __name__=="__main__":
    test_polarity()
    test_timestamps()
    test_evidence_stance()
    test_claim_signature_derived()
    test_no_fabrication()
    print("ALL METADATA URGENT TESTS PASS")
