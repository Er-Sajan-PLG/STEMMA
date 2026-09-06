"""B5.6: Canonical vs derived boundary tests."""
import sys
import pathlib
import yaml
import json

ROOT = pathlib.Path(__file__).resolve().parents[2]


def test_canonical_only_explicit():
    # Every connections/*.yaml must be explicit authored, not derived
    for p in (ROOT / "connections").glob("*.yaml"):
        d = yaml.safe_load(p.read_text())
        assert d.get("type") == "connection"
        # No derived:true in canonical
        assert d.get("derived") is None, f"{p.name} has derived in canonical"
        assert d.get("assertion", {}).get("type") in ("asserted", "proposed", "inferred")


def test_inverse_not_in_canonical():
    # Inverse edges should not be written as canonical unless independently authored
    # Check that has_part etc. are not duplicated as canonical without explicit file
    # Our curated bridges are explicit; inverse would be has_part not present
    import collections

    rels = [yaml.safe_load(p.read_text()).get("relation") for p in (ROOT / "connections").glob("*.yaml")]
    # If part_of exists, has_part should not be auto-duplicated in canonical (derived only)
    # We have part_of 10, has_part 0 (correct — inverse is derived)
    c = collections.Counter(rels)
    assert c.get("has_part", 0) == 0, "has_part should be derived, not canonical"
    print("PASS: inverse not in canonical")


def test_transitive_not_in_canonical():
    # Transitive closure must NOT be written to canonical. Derived edges are computed
    # separately (knowledge.extended.json) and never inflate the canonical connection
    # count. The exact closure size depends on the repository's content — the invariant
    # is structural, not a fixed number.
    d = json.loads((ROOT / "exports" / "knowledge.extended.json").read_text())
    # Canonical count == explicit connections only (no derived inflation).
    canonical_files = len(list((ROOT / "connections").glob("*.yaml")))
    assert d["explicit"]["count"] == canonical_files
    assert d["connection_count"] == canonical_files
    # Derived transitive closure is present and positive, and is reported separately —
    # it is never folded into the canonical (explicit) count.
    tc = d["derived"]["transitive_closure"]
    assert isinstance(tc["count"], int) and tc["count"] > 0
    print("PASS: transitive not in canonical")


def test_derived_marked():
    d = json.loads((ROOT / "exports" / "knowledge.extended.json").read_text())
    for e in d["derived"]["inverse_edges"]["edges"][:5]:
        assert e["derived"] is True
        assert "derivation" in e
        assert e["derivation"]["method"] == "inverse"
    for e in d["derived"]["transitive_closure"]["edges"][:5]:
        assert e["derived"] is True
        assert e["derivation"]["method"] == "transitive_closure"
        assert "path" in e["derivation"]
    print("PASS: derived marked")


def test_regeneration_without_canonical_change():
    import subprocess, pathlib, hashlib

    # Hash canonical files
    before = sorted((p.read_text() for p in (ROOT / "connections").glob("*.yaml")))
    subprocess.run([sys.executable, str(ROOT / "scripts/graph_analysis.py")], check=True)
    after = sorted((p.read_text() for p in (ROOT / "connections").glob("*.yaml")))
    assert before == after, "graph_analysis modified canonical files"
    print("PASS: regeneration without canonical change")


if __name__ == "__main__":
    test_canonical_only_explicit()
    test_inverse_not_in_canonical()
    test_transitive_not_in_canonical()
    test_derived_marked()
    test_regeneration_without_canonical_change()
    print("ALL BOUNDARY TESTS PASS")
