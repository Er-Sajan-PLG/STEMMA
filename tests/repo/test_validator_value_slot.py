import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import validate as val  # noqa: E402


def _conn(cid, **over):
    base = {
        "id": cid,
        "type": "connection",
        "source": "stemma:phys.metre",
        "relation": "corresponds_to",
        "assertion": {"status": "active", "type": "asserted", "review": {"status": "unreviewed"}},
        "provenance": {
            "asserted_by": {"type": "human", "id": "human:curator.001"},
            "generated_by": {"type": "human", "id": "human:curator.001"},
            "method": {"type": "manual"},
            "reviewed_by": [],
            "review_history": [],
        },
    }
    base.update(over)
    return base


ENTITIES = {"stemma:phys.metre": {}, "stemma:phys.mass": {}}
SOURCES = {}


class TestValueSlotXOR(unittest.TestCase):
    """REGRESSION (R4 engine gap): value-slot connections (ADR-0045 value-claims,
    ARCH-V2 3.2: target XOR value) must skip the target-existence check, and a
    connection carrying BOTH target and value must be rejected. The dormant bug
    (pre-R4 corpus had zero valued connections) made every value-claim
    unvalidatable; exercising it is R4 (e) proc. conn.000156.
    """

    def test_value_only_skips_target_check(self):
        errs: list = []
        val.validate_connection(
            _conn("stemma:conn.900001",
                  value={"amount": "299792458", "unit": "qudt:unit-MeterPerSecond"}),
            ENTITIES, SOURCES, errs)
        self.assertFalse([e for e in errs if "target" in e], errs)

    def test_relational_target_still_required_to_resolve(self):
        errs: list = []
        val.validate_connection(
            _conn("stemma:conn.900002", target="stemma:phys.mass"), ENTITIES, SOURCES, errs)
        self.assertFalse([e for e in errs if "target" in e], errs)
        errs.clear()
        val.validate_connection(
            _conn("stemma:conn.900003", target="stemma:phys.nope"), ENTITIES, SOURCES, errs)
        self.assertTrue([e for e in errs if "target does not resolve" in e], errs)

    def test_both_target_and_value_rejected(self):
        errs: list = []
        val.validate_connection(
            _conn("stemma:conn.900004", target="stemma:phys.mass",
                  value={"amount": "1", "unit": "qudt:unit-Uni"}),
            ENTITIES, SOURCES, errs)
        self.assertTrue([e for e in errs if "XOR" in e], errs)

    def test_neither_target_nor_value_fails(self):
        errs: list = []
        val.validate_connection(_conn("stemma:conn.900005"), ENTITIES, SOURCES, errs)
        self.assertTrue([e for e in errs if "target does not resolve" in e], errs)


class TestLiveCorpusValueSlot(unittest.TestCase):
    def test_r4_valued_connection_validates_clean(self):
        import subprocess
        res = subprocess.run([sys.executable, str(ROOT / "scripts" / "validate.py")],
                             cwd=ROOT, capture_output=True, text=True)
        out = res.stdout + res.stderr
        self.assertEqual(res.returncode, 0, out[-800:])
        self.assertNotIn("conn.000156.yaml: target", out)


if __name__ == "__main__":
    unittest.main()
