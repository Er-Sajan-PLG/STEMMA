#!/usr/bin/env python3
"""Phase B integration tests (R2 evidence/sources, R4 relation triage, R6 entity review).

These are headless: they never start the webapp/LLM and never mutate the tracked
canonical tree in place (entity-review tests use a temporary fixture root).
"""
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import validate  # noqa: E402


# --------------------------------------------------------------------------- #
# R2 — evidence gate helpers in validate.py
# --------------------------------------------------------------------------- #
def _conn(**overrides):
    base = {
        "id": "stemma:conn.999999", "type": "connection",
        "source": "stemma:phys.force", "relation": "related_to",
        "target": "stemma:phys.mass", "assertion": {"status": "active", "type": "proposed", "review": {"status": "unreviewed"}},
        "provenance": {"asserted_by": {"type": "human", "id": "human:curator.001"}, "generated_by": {"type": "human", "id": "human:curator.001"}, "method": {"type": "manual"}},
        "_file": "connections/conn.999999.yaml",
    }
    base.update(overrides)
    return base


def test_canonical_requires_evidence():
    errs, warns = [], []
    validate.check_evidence_integrity(
        _conn(assertion={"status": "active", "type": "asserted", "review": {"status": "canonical"}}),
        errs, warns)
    assert any("canonical assertion has no evidence" in e for e in errs), errs
    print("PASS: canonical assertion requires evidence")


def test_axiomatic_marker_allowed_without_conventional_evidence():
    errs, warns = [], []
    conn = _conn(assertion={"status": "active", "type": "asserted", "review": {"status": "canonical"}})
    conn["evidence"] = [{"type": "axiom", "description": "axiomatic definitional fact"}]
    validate.check_evidence_integrity(conn, errs, warns)
    assert not any("canonical assertion has no evidence" in e for e in errs), errs
    print("PASS: explicit axiomatic marker satisfies the evidence gate")


def test_active_empty_evidence_is_advisory():
    errs, warns = [], []
    validate.check_evidence_integrity(_conn(), errs, warns)
    assert not errs
    assert any("no evidence" in w for w in warns), warns
    print("PASS: active empty evidence is an advisory warning, not an error")


def test_rejected_empty_evidence_not_warned():
    errs, warns = [], []
    validate.check_evidence_integrity(
        _conn(assertion={"status": "active", "type": "proposed", "review": {"status": "rejected"}}),
        errs, warns)
    assert not any("no evidence" in w for w in warns), warns
    print("PASS: rejected claims are not nagged for evidence")


# --------------------------------------------------------------------------- #
# R4 — advisory relation reclassification
# --------------------------------------------------------------------------- #
def test_related_to_advisory_suggests_specific_relation():
    registry = validate.load_relation_registry()
    entities = {"stemma:phys.force": {"type": "concept"}, "stemma:phys.mass": {"type": "quantity"}}
    warns = []
    conn = _conn()
    fmt = conn["_file"]
    validate.check_relation_triage_advisory(conn, entities, set(), registry, warns)
    assert any("may be reclassified" in w for w in warns), warns
    assert fmt in warns[0]
    print("PASS: related_to-only edge surfaces a reclassification candidate (advisory)")


def test_pair_with_specific_relation_not_advisory():
    registry = validate.load_relation_registry()
    entities = {"stemma:phys.force": {"type": "concept"}, "stemma:phys.mass": {"type": "quantity"}}
    warns = []
    specific = {frozenset(("stemma:phys.force", "stemma:phys.mass"))}
    validate.check_relation_triage_advisory(_conn(), entities, specific, registry, warns)
    assert not any("may be reclassified" in w for w in warns), warns
    print("PASS: edges with a specific relation are left out of advisory")


def test_relation_triage_report_shape():
    from relation_triage import build_report
    report = build_report(ROOT)
    assert report["advisory"] is True
    assert set(report).issuperset({"total_related_to", "related_to_only_count",
                                   "dependency_pairs", "measurement_candidates",
                                   "already_specific"})
    assert report["total_related_to"] > 0
    print("PASS: relation-triage report shape")


# --------------------------------------------------------------------------- #
# R2 — academic source backfill report (read-only on real tree)
# --------------------------------------------------------------------------- #
def test_academic_sources_report_shape():
    from academic_sources import build_report
    report = build_report(ROOT)
    assert report["advisory"] is True
    assert set(report).issuperset({"source_count", "entity_count",
                                   "unresolved_entity_source_count",
                                   "unresolved_evidence_source_ref_count"})
    assert isinstance(report["unresolved_entity_provenance_sources"], list)
    print("PASS: academic-sources report shape")


# --------------------------------------------------------------------------- #
# R6 — entity review tooling (fixture only; never touches tracked content)
# --------------------------------------------------------------------------- #
def _write_fixture(tmp: pathlib.Path) -> pathlib.Path:
    root = tmp / f"repo-{len(list(tmp.glob('repo-*')))}"
    (root / "schema").mkdir(parents=True)
    (root / "content" / "physics").mkdir(parents=True)
    (root / "schema" / "agent-registry.yaml").write_text(
        "version: '0.1'\nagents:\n- id: human:reviewer.test\n  class: human\n  display_name: Test reviewer\n  external_id: null\n  status: active\n  note: test fixture\n",
        encoding="utf-8")
    (root / "content" / "physics" / "test-concept.md").write_text(
        "---\nid: stemma:phys.test-concept\ntype: concept\nname: Test Concept\ndomain: physics\nstatus: draft\ndefinition: A test concept.\nprovenance:\n  ai_drafted: true\n---\n\nBody.\n",
        encoding="utf-8")
    return root


def test_entity_review_transitions(tmp_path: pathlib.Path):
    from review_entity import transition_entity
    root = _write_fixture(tmp_path)
    # canonical is only legal after human review.
    try:
        transition_entity(root, "stemma:phys.test-concept", "canonicalize", "human:reviewer.test")
    except ValueError as exc:
        assert "forbidden" in str(exc)
    else:
        raise AssertionError("draft -> canonical must be forbidden")
    e = transition_entity(root, "stemma:phys.test-concept", "review", "human:reviewer.test", when="2026-09-07T00:00:00+00:00")
    assert e["status"] == "human_reviewed"
    assert e["provenance"]["reviewer"] == "human:reviewer.test"
    e = transition_entity(root, "stemma:phys.test-concept", "canonicalize", "human:reviewer.test", when="2026-09-07T00:01:00+00:00")
    assert e["status"] == "canonical"
    # No helper/underscore leakage into the file.
    raw = (root / "content" / "physics" / "test-concept.md").read_text(encoding="utf-8")
    assert "_file" not in raw
    print("PASS: entity review transitions")


def test_entity_review_rejects_non_human_reviewer(tmp_path: pathlib.Path):
    from review_entity import transition_entity
    root = _write_fixture(tmp_path)
    try:
        transition_entity(root, "stemma:phys.test-concept", "review", "unknown:not-human")
    except ValueError as exc:
        assert "active human agent" in str(exc)
    else:
        raise AssertionError("non-human reviewer must be rejected")
    print("PASS: entity review requires an active human reviewer")


def test_entity_campaign_batches_deterministic():
    from entity_review_campaign import build_batches
    entities = {
        "stemma:phys.a": {"id": "stemma:phys.a", "domain": "physics", "status": "draft", "type": "concept"},
        "stemma:phys.b": {"id": "stemma:phys.b", "domain": "physics", "status": "draft", "type": "law"},
        "stemma:bio.c": {"id": "stemma:bio.c", "domain": "biology", "status": "draft", "type": "concept"},
        "stemma:bio.d": {"id": "stemma:bio.d", "domain": "biology", "status": "draft", "type": "concept"},
        "stemma:phys.rev": {"id": "stemma:phys.rev", "domain": "physics", "status": "human_reviewed", "type": "concept"},
    }
    b1 = build_batches(entities, per_domain=1, batch_size=10)
    b2 = build_batches(entities, per_domain=1, batch_size=10)
    assert b1 == b2, "campaign batches must be deterministic"
    assert len(b1) >= 1
    seeds = [e["id"] for e in b1[0]]
    assert "stemma:phys.rev" not in seeds
    # Seed pass picks the top pending per domain.
    assert len(set(seeds)) == len(seeds)
    print("PASS: entity campaign batches deterministic and exclude reviewed")


def main() -> int:
    import tempfile

    test_canonical_requires_evidence()
    test_axiomatic_marker_allowed_without_conventional_evidence()
    test_active_empty_evidence_is_advisory()
    test_rejected_empty_evidence_not_warned()
    test_related_to_advisory_suggests_specific_relation()
    test_pair_with_specific_relation_not_advisory()
    test_relation_triage_report_shape()
    test_academic_sources_report_shape()
    test_entity_campaign_batches_deterministic()
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = pathlib.Path(tmp)
        test_entity_review_transitions(tmp_path)
        test_entity_review_rejects_non_human_reviewer(tmp_path)
    print("ALL PHASE B INTEGRITY TESTS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
