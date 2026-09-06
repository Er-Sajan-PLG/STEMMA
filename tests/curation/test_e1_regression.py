"""E1 regression: reviewed-only vs canonical ambiguity cannot return."""
import json, pathlib
ROOT=pathlib.Path(__file__).resolve().parents[2]
def test_e1():
    epi=json.loads((ROOT/"reports/epistemic-summary.json").read_text())
    assert "reviewed_only" in epi, "reviewed_only missing"
    assert "canonical" in epi
    assert "total_reviewed_including_canonical" in epi
    assert epi["reviewed_only"] + epi["canonical"] == epi["total_reviewed_including_canonical"]
    assert epi["canonical"] == 50
    assert epi["reviewed_only"] == 0
    # curation-status too
    cs=json.loads((ROOT/"reports/curation-status.json").read_text())
    assert "reviewed_only" in cs
    assert cs["reviewed_only"] == 0
    assert cs["canonical"] == 50
    print("PASS: E1 reviewed-only vs canonical")
if __name__=="__main__":
    test_e1()
    print("E1 PASS")
