import json
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]


class TestJsonldProjection(unittest.TestCase):
    """R6 increment 1: canonical -> knowledge.jsonld must be deterministic,
    valid, and canonical-only (ADR-0007; ADR-0053 Amendment 0001 external
    base still deferred — checked at publication gate)."""

    def _run(self, *argv):
        r = subprocess.run([sys.executable, str(ROOT / "scripts" / argv[0]), *argv[1:]],
                           capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(r.returncode, 0, f"{argv}: {r.stderr[-300:]}")
        return r

    def test_export_regeneration_is_byte_identical(self):
        self._run("export_jsonld.py", "--check")

    def test_projection_validates(self):
        self._run("validate_jsonld.py")

    def test_projection_declares_vocabulary_and_canonical_only(self):
        d = json.loads((ROOT / "exports" / "knowledge.jsonld").read_text(encoding="utf-8"))
        ctx = d["@context"]
        for prefix in ("skos", "qudt", "dcterms", "owl"):
            self.assertIn(prefix, ctx)
        self.assertEqual(ctx["@vocab"], "stemma:")
        for node in d["@graph"]:
            if isinstance(node["@type"], list):
                self.assertEqual(node["status"], "canonical")
            else:
                self.assertEqual(node["reviewStatus"], "canonical")

    def test_quantity_firm_fields_projected(self):
        d = json.loads((ROOT / "exports" / "knowledge.jsonld").read_text(encoding="utf-8"))
        force = next(n for n in d["@graph"] if n["@id"] == "stemma:phys.force")
        self.assertEqual(force["quantityKind"], "derived")
        self.assertEqual(force["tensorCharacter"], "vector")
        self.assertIn("weight", force["sameDimensionalQuantities"])
        metre = next(n for n in d["@graph"] if n["@id"] == "stemma:phys.metre")
        self.assertIn("qudt:Unit", metre["@type"])

    def test_value_slot_connection_projects_value(self):
        d = json.loads((ROOT / "exports" / "knowledge.jsonld").read_text(encoding="utf-8"))
        conn = next(n for n in d["@graph"] if n["@id"] == "stemma:conn.000156")
        self.assertIsNone(conn.get("object"))
        self.assertIsNotNone(conn.get("value"))
        rel = next(n for n in d["@graph"] if n["@id"] == "stemma:conn.000157")
        self.assertEqual(rel["object"], "stemma:phys.mass")
        self.assertEqual(rel["predicate"], "mathematically_requires")

    def test_wikidata_external_ids_as_iris(self):
        d = json.loads((ROOT / "exports" / "knowledge.jsonld").read_text(encoding="utf-8"))
        length = next(n for n in d["@graph"] if n["@id"] == "stemma:phys.length")
        self.assertEqual(length["externalIds"]["wikidata"],
                         "http://www.wikidata.org/entity/Q11433")


if __name__ == "__main__":
    unittest.main()
