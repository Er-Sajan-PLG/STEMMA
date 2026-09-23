import json
import pathlib
import re
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]


class TestReleaseBundleAndGate(unittest.TestCase):
    """R6 increment 2: deterministic bundle, SHACL contract enforcement,
    Amendment-0001 publication gate."""

    def _run(self, *argv, expect_code=0):
        r = subprocess.run([sys.executable, str(ROOT / "scripts" / argv[0]), *argv[1:]],
                           capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(r.returncode, expect_code, f"{argv}: {(r.stdout + r.stderr)[-400:]}")
        return r

    def test_bundle_build_is_deterministic(self):
        r1 = self._run("build_release_bundle.py", "--print-name")
        name1 = r1.stdout.strip().splitlines()[-1]
        r2 = self._run("build_release_bundle.py", "--print-name")
        self.assertEqual(name1, r2.stdout.strip().splitlines()[-1])
        self.assertTrue(name1.startswith("R6-bundle-"))
        self.assertTrue(re.fullmatch(r"R6-bundle-[0-9a-f]{12}", name1))

    def test_bundle_contents_and_verification(self):
        name = self._run("build_release_bundle.py", "--print-name").stdout.strip().splitlines()[-1]
        bundle = ROOT / "release" / name
        for f in ("knowledge.jsonld", "knowledge.canonical.json", "stemma-shapes.ttl",
                  "SHA256SUMS.txt", "manifest.json"):
            self.assertTrue((bundle / f).exists(), f)
        self._run("build_release_bundle.py", "--verify", str(bundle))
        m = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(m["entity_count"], 7)
        self.assertEqual(m["assertion_count"], 2)
        self.assertIn("BLOCKED", m["amendment_0001_gate"])

    def test_shacl_shapes_validate(self):
        self._run("validate_shacl_shapes.py")

    def test_shacl_ttl_and_enforcer_parity(self):
        """Every sh:path in the TTL is enforced by the runner (no dead shapes)."""
        ttl = (ROOT / "schema/projection/stemma-shapes.ttl").read_text(encoding="utf-8")
        ttl_paths = len(re.findall(r"sh:path", ttl))
        self.assertGreater(ttl_paths, 3)
        # runner must load every constraint present in the ttl (property + XOR paths)
        out = self._run("validate_shacl_shapes.py").stdout
        m = re.search(r"(\d+) property constraints, (\d+) XOR paths", out)
        self.assertIsNotNone(m)
        self.assertEqual(int(m.group(1)) + int(m.group(2)), ttl_paths)

    def test_publication_gate_blocked_until_owner_decision(self):
        """Gate must exit 1 with the amendment block while no decision record exists."""
        self.assertFalse((ROOT / "docs/decisions/r6-identifier-base.md").exists())
        r = self._run("publication_gate.py", expect_code=1)
        self.assertIn("BLOCKED", r.stdout)
        self.assertIn("w3id", r.stdout)
        self.assertIn("datacite-doi", r.stdout)

    def test_signing_requires_owner_key(self):
        "Signing without gpg/--key must fail with setup guidance (exit 2), never fake."
        name = self._run("build_release_bundle.py", "--print-name").stdout.strip().splitlines()[-1]
        import shutil, subprocess, sys
        cmd = [sys.executable, str(ROOT / "scripts/sign_release_bundle.py"),
               f"release/{name}", "--key", "nonexistent@example.invalid"]
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
        if shutil.which("gpg"):
            # with gpg, a bogus key must fail hard, without producing a .sig
            self.assertEqual(r.returncode, 1)
            self.assertFalse((ROOT / "release" / name / "SHA256SUMS.sig").exists())
        else:
            self.assertEqual(r.returncode, 2)
            self.assertIn("SETUP", r.stdout)

    def test_publication_gate_explain_lists_candidates(self):
        r = self._run("publication_gate.py", "--explain")
        for base in ("w3id", "datacite-doi", "ark-n2t", "stemma-urn-only"):
            self.assertIn(base, r.stdout)


if __name__ == "__main__":
    unittest.main()
