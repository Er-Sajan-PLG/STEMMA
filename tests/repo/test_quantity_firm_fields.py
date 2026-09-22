import pathlib
import sys
import unittest

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import validate as val  # noqa: E402


def _ent(**over):
    base = {
        "id": "stemma:phys.test", "type": "quantity", "name": "T",
        "domain": "physics", "subdomain": "mechanics", "status": "draft",
        "definition": "x", "provenance": {"ai_drafted": True},
        "_file": "test.md",
    }
    base.update(over)
    return base


class TestQuantityFirmFieldsRule(unittest.TestCase):
    """Owner directive 2026-09-22: quantity entities MUST declare SI class
    (base|derived) and tensorial character (scalar|vector|tensor)."""

    def test_present_and_valid_is_clean(self):
        errs: list = []
        val.validate_entity(_ent(quantity_kind="derived", tensor_character="vector"), errs)
        self.assertFalse([e for e in errs if "quantity_" in e or "tensor_" in e], errs)

    def test_missing_rejected(self):
        errs: list = []
        val.validate_entity(_ent(), errs)
        self.assertIn("quantity requires quantity_kind: base|derived", "\n".join(errs))
        self.assertIn("quantity requires tensor_character: scalar|vector|tensor", "\n".join(errs))

    def test_invalid_values_rejected(self):
        errs: list = []
        val.validate_entity(_ent(quantity_kind="fundamental", tensor_character="space"), errs)
        self.assertTrue([e for e in errs if "quantity_kind" in e], errs)
        self.assertTrue([e for e in errs if "tensor_character" in e], errs)

    def test_non_quantity_unaffected(self):
        e = _ent(type="law")
        errs: list = []
        val.validate_entity(e, errs)
        self.assertFalse([x for x in errs if "quantity_" in x or "tensor_" in x], errs)


CLASS = {
    "force": ("derived", "vector"),
    "length": ("base", "scalar"),
    "mass": ("base", "scalar"),
    "time": ("base", "scalar"),
}


class TestCorpusQuantityClassification(unittest.TestCase):
    """Spot physics assertions the firm fields exist to lock in."""

    def _fm(self, path):
        return yaml.safe_load(pathlib.Path(ROOT / path).read_text().split("---")[1])

    def test_seed_classifications(self):
        for name, (kind, tensor) in CLASS.items():
            loc = (f"content/physics/mechanics/{name}.md" if name == "force"
                   else f"content/physics/measurement-units/{name}.md")
            d = self._fm(loc)
            self.assertEqual(d["type"], "quantity")
            self.assertEqual(d["quantity_kind"], kind, f"{name} kind")
            self.assertEqual(d["tensor_character"], tensor, f"{name} tensor")


if __name__ == "__main__":
    unittest.main()
