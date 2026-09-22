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


class TestPhase5BInvariants(unittest.TestCase):
    """api_surface / env_surface / tier-strict — positive on real repo, negative on fixtures."""

    def test_api_surface_real_repo(self):
        problems: list[str] = []
        docs._validate_api_surface(docs.load_contract(), ROOT, problems)
        self.assertEqual(problems, [])

    def test_env_surface_real_repo(self):
        problems: list[str] = []
        docs._validate_env_surface(docs.load_contract(), ROOT, problems)
        self.assertEqual(problems, [])

    def test_api_surface_negative(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            (tmp / "schema").mkdir()
            (tmp / "schema" / "api.yaml").write_text("paths:\n  /v2/new-endpoint:\n    get: {}\n", encoding="utf-8")
            (tmp / "docs").mkdir()
            (tmp / "docs" / "API.md").write_text("# API\n", encoding="utf-8")
            contract = {"invariants": {"api_surface": {"spec": "schema/api.yaml", "must_appear_in": ["docs/API.md"]}}}
            problems: list[str] = []
            docs._validate_api_surface(contract, tmp, problems)
            self.assertTrue(any("/v2/new-endpoint" in p for p in problems), problems)

    def test_env_surface_negative(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            (tmp / "webapp").mkdir()
            (tmp / "webapp" / "x.py").write_text('import os\nk = os.environ.get("SOME_NEW_VAR")\n', encoding="utf-8")
            (tmp / ".env.example").write_text("OTHER=\n", encoding="utf-8")
            contract = {"invariants": {"env_surface": {
                "scan_files": ["webapp/x.py"], "must_appear_in": [".env.example"],
                "capture": ['os\\.environ\\.get\\(["\']?([A-Z][A-Z0-9_]+)']}}}
            problems: list[str] = []
            docs._validate_env_surface(contract, tmp, problems)
            self.assertTrue(any("SOME_NEW_VAR" in p for p in problems), problems)

    def test_tier_strict_negative(self):
        contract = {"enforcement": {"strict_tiers": [0, 1]}}
        taxonomy = {"artifacts": [{"id": 999, "cat": "A11", "tier": 1, "name": "PR template", "status": "missing"}]}
        problems: list[str] = []
        docs._validate_tier_strict(contract, taxonomy, problems)
        self.assertEqual(len(problems), 1)

    def test_tier_strict_allows_higher_tiers(self):
        contract = {"enforcement": {"strict_tiers": [0, 1]}}
        taxonomy = {"artifacts": [{"id": 998, "cat": "A14", "tier": 4, "name": "Style guide", "status": "missing"}]}
        problems: list[str] = []
        docs._validate_tier_strict(contract, taxonomy, problems)
        self.assertEqual(problems, [])


class TestCrossPhaseIntegration(unittest.TestCase):
    def test_non_local_impact(self):
        hits = docs.direct_impact(["adapters/python/stemma_adapter/__init__.py"], docs.load_contract())
        self.assertIn("adapters/README.md", hits)      # near doc
        self.assertIn("docs/API.md", hits)             # §5 — distant doc, same graph

    def test_ci_equivalence(self):
        ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        self.assertIn("python3 scripts/docs.py sync", ci)
        self.assertIn("python3 scripts/docs.py check", ci)

    def test_broken_dependency_edge_detected(self):
        contract = {"artifacts": [
            {"path": "a.md", "cat": "A1", "tier": 0, "kind": "CANONICAL", "sources": [], "depends_on": ["b.md"]},
            {"path": "b.md", "cat": "A1", "tier": 0, "kind": "CANONICAL", "sources": []},
        ], "kinds": ["CANONICAL"], "categories": {"A1": "g"}}
        import tempfile as _tf, shutil as _sh
        tmp = Path(_tf.mkdtemp(), )
        try:
            (tmp / "a.md").write_text("a", encoding="utf-8")
            problems: list[str] = []
            docs._validate_contract_vs_disk(contract, {"artifacts": []}, tmp, problems)
            self.assertTrue(any("b.md" in p for p in problems), problems)
        finally:
            _sh.rmtree(tmp)


if __name__ == "__main__":
    unittest.main()
