#!/usr/bin/env python3
"""Tests for the documentation-sync engine (scripts/docs.py).

Covers the repo-relevant Phase 7 scenarios: direct + transitive + cross-category
impact, negative case, generated-doc determinism, sync idempotency, stale- and
missing-doc detection, contract completeness.
"""
from __future__ import annotations

import importlib.util
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("docs_engine", ROOT / "scripts" / "docs.py")
docs = importlib.util.module_from_spec(spec)
sys.modules.setdefault("docs_engine", docs)
spec.loader.exec_module(docs)


class TestModelLayer(unittest.TestCase):
    def setUp(self):
        self.contract = docs.load_contract()
        self.taxonomy = docs.load_taxonomy()

    def test_contract_parses_and_kinds_known(self):
        self.assertTrue(docs.artifacts(self.contract))
        for art in docs.artifacts(self.contract):
            self.assertIn(art["kind"], self.contract["kinds"])
            self.assertIn(art["cat"], self.contract["categories"])

    def test_taxonomy_has_220_unique_ids_valid_statuses(self):
        ids = [a["id"] for a in self.taxonomy["artifacts"]]
        self.assertEqual(len(ids), 220)
        self.assertEqual(len(set(ids)), 220)
        for a in self.taxonomy["artifacts"]:
            self.assertIn(a["status"], docs.STATUSES)

    def test_all_contract_artifacts_exist(self):
        for art in docs.artifacts(self.contract):
            self.assertTrue((ROOT / art["path"]).exists(), art["path"])

    def test_no_orphan_toplevel_docs(self):
        declared = {a["path"] for a in docs.artifacts(self.contract)}
        for f in (ROOT / "docs").glob("*.md"):
            self.assertIn(f"docs/{f.name}", declared)


class TestImpactEngine(unittest.TestCase):
    def setUp(self):
        self.contract = docs.load_contract()

    def test_direct_and_cross_category_impact(self):
        hits = docs.direct_impact(["schema/api.yaml"], self.contract)
        self.assertIn("docs/API.md", hits)                  # §5 API docs
        self.assertIn("docs/SCHEMA-SPECIFICATION.md", hits) # §2 schema docs — cross-category
        self.assertIn("docs/VISION.md", hits)               # schema/ described in vision
    def test_transitive_impact_closure(self):
        hits = docs.direct_impact(["PROGRESS.md"], self.contract)
        self.assertIn("docs/ROADMAP.md", hits)             # progress tracked in roadmap
        closure = docs.transitive_impact(hits, self.contract)
        self.assertIn("PROGRESS.md", closure)
        self.assertIn("docs/ROADMAP.md", closure)

    def test_unknown_file_directs_nothing(self):
        hits = docs.direct_impact(["some/novel/path.bin"], self.contract)
        self.assertEqual(hits, {})


class TestCoverageDeterminism(unittest.TestCase):
    def test_render_deterministic(self):
        c, t = docs.load_contract(), docs.load_taxonomy()
        self.assertEqual(docs.render_coverage(c, t), docs.render_coverage(c, t))

    def test_coverage_file_fresh(self):
        rendered = docs.render_coverage(docs.load_contract(), docs.load_taxonomy())
        current = (ROOT / docs.COVERAGE_PATH).read_text(encoding="utf-8")
        self.assertEqual(rendered, current, "coverage doc stale — run scripts/docs.py sync")


class TestSyncIdempotency(unittest.TestCase):
    def test_sync_twice_second_run_no_changes(self):
        first: list[str] = []
        second: list[str] = []
        for gen_id, gen in docs.load_contract().get("generators", {}).items():
            first += docs.run_generator(gen_id, gen, write=True)
        for gen_id, gen in docs.load_contract().get("generators", {}).items():
            second += docs.run_generator(gen_id, gen, write=True)
        self.assertEqual(second, [], f"sync not idempotent: {second}")


class TestValidatePositiveAndNegative(unittest.TestCase):
    def test_real_repo_validates_clean(self):
        self.assertEqual(docs.validate(), [])

    def _fixture(self):
        tmp = Path(tempfile.mkdtemp(prefix="docs-engine-test-"))
        (tmp / "docs" / "meta").mkdir(parents=True)
        (tmp / "docs" / "decisions").mkdir(parents=True)
        shutil.copy(ROOT / "docs" / "docs-contract.yaml", tmp / "docs" / "docs-contract.yaml")
        shutil.copy(ROOT / "docs" / "meta" / "doc-taxonomy.yaml", tmp / "docs" / "meta" / "doc-taxonomy.yaml")
        shutil.copy(ROOT / "docs" / "meta" / "documentation-coverage.md", tmp / "docs" / "meta" / "documentation-coverage.md")
        return tmp

    def test_missing_contract_artifact_detected(self):
        tmp = self._fixture()
        try:
            problems = docs.validate(root=tmp)
            self.assertTrue(any("does not exist" in p for p in problems), problems)
        finally:
            shutil.rmtree(tmp)

    def test_broken_link_detected(self):
        tmp = self._fixture()
        try:
            (tmp / "README.md").write_text("# X\n[bad](DOES-NOT-EXIST.md)\n", encoding="utf-8")
            problems = docs.validate(root=tmp)
            self.assertTrue(any("broken link" in p for p in problems), problems)
        finally:
            shutil.rmtree(tmp)

    def test_stale_generated_detected(self):
        tmp = self._fixture()
        try:
            tgt = tmp / "docs" / "meta" / "documentation-coverage.md"
            tgt.write_text(tgt.read_text(encoding="utf-8") + "\nmanually drifted line\n", encoding="utf-8")
            problems = docs.validate(root=tmp)
            self.assertTrue(any("generated drift" in p for p in problems), problems)
        finally:
            shutil.rmtree(tmp)


if __name__ == "__main__":
    unittest.main()
