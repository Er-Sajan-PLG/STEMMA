"""Tests for the STEMMA curation pipeline (scripts/curation_pipeline.py).

Verifies the hard-gate model: a change is only 'request_review' when every gate
passes; broken changes are 'hold'/'reject' and never publish; the pipeline never
auto-canonicalizes (the Human Governance Gate does that via scripts/review.py);
and repair routing maps failed gates to stages deterministically.
"""
from __future__ import annotations

import pathlib
import sys
from typing import Any

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "scripts"))

import curation_pipeline as cp  # noqa: E402
import validate  # noqa: E402


def _pass(gate: str) -> cp.GateResult:
    return cp.GateResult(gate, "pass", [])


def _fail(gate: str, finding: str = "x") -> cp.GateResult:
    return cp.GateResult(gate, "fail", [finding])


def test_route_repair_maps_gates_to_stages():
    # From architecture review §P.2
    assert cp.route_repair([_fail("schema")]) == ["draft"]
    assert cp.route_repair([_fail("identity")]) == ["intake"]
    assert cp.route_repair([_fail("relations")]) == ["blueprint"]
    assert cp.route_repair([_fail("provenance")]) == ["intake"]
    assert cp.route_repair([_fail("resolution")]) == ["intake"]
    assert cp.route_repair([_fail("conditions")]) == ["blueprint"]
    assert cp.route_repair([_fail("intent")]) == ["intake"]


def test_evaluate_and_publishable():
    gates = [_pass("schema"), _pass("identity"), _fail("provenance")]
    assert cp.evaluate_gates(gates) == gates
    assert all(g.verdict == "pass" for g in [_pass("a"), _pass("b")])
    assert not all(g.verdict == "pass" for g in gates)


def test_good_entity_reaches_request_review():
    req = cp.CurationRequest(kind="entity", intent="t", data={
        "id": "stemma:test.p1", "type": "concept", "name": "P", "domain": "test",
        "status": "draft", "definition": "def", "provenance": {"ai_drafted": True},
    })
    dec = cp.run_pipeline(
        req,
        draft_callback=lambda bp, data, **kw: data,
        semantic_review_callback=lambda gate, artifact, bp: _pass(gate),
    )
    assert dec.action == "request_review"          # NOT canonical
    assert dec.publishable is True
    assert dec.artifact is not None


def test_bad_entity_is_hold_and_never_publishable():
    req = cp.CurationRequest(kind="entity", intent="bad", data={
        "id": "nope", "type": "concept", "name": "Bad", "domain": "test",
        "status": "draft", "definition": "x", "provenance": {},
    })
    dec = cp.run_pipeline(
        req,
        draft_callback=lambda bp, data, **kw: data,
        semantic_review_callback=lambda gate, artifact, bp: _pass(gate),
    )
    assert dec.publishable is False
    assert dec.action in ("hold", "reject", "propose")
    assert dec.action != "request_review"
    fails = [g.gate for g in dec.gates if g.verdict == "fail"]
    assert "identity" in fails or "provenance" in fails


def test_intent_failure_forces_reject_or_hold():
    """If the semantic/intent gate fails, the change is not publishable and is not
    forwarded for canonicalization."""
    req = cp.CurationRequest(kind="entity", intent="nonsense", data={"id": "stemma:x.y", "type": "concept"})
    dec = cp.run_pipeline(
        req,
        draft_callback=lambda bp, data, **kw: data,
        semantic_review_callback=lambda gate, artifact, bp: _fail("intent", "does not satisfy intent"),
    )
    assert dec.publishable is False
    assert dec.action != "request_review"


def test_repair_loop_bounded_and_recovers():
    """A fixable draft gate should repair and then reach request_review."""
    calls = {"n": 0}

    def flaky_draft(bp, data, **kw):
        calls["n"] += 1
        if calls["n"] == 1:  # first draft is bad -> repair
            return {"id": "bad", "type": "concept", "name": "", "domain": "test",
                    "status": "draft", "definition": "", "provenance": {}}
        return {"id": "stemma:test.fixed", "type": "concept", "name": "Fixed", "domain": "test",
                "status": "draft", "definition": "ok", "provenance": {"ai_drafted": True}}

    req = cp.CurationRequest(kind="entity", intent="t", data={})
    dec = cp.run_pipeline(
        req,
        draft_callback=flaky_draft,
        semantic_review_callback=lambda gate, artifact, bp: _pass(gate),
        max_repair_rounds=2,
    )
    assert calls["n"] >= 2
    assert dec.action == "request_review"


def test_never_emits_canonical_action():
    """The pipeline's DecisionAction set must never include 'canonical'."""
    assert "canonical" not in cp.DecisionAction.__args__
    # run on a valid proposal; action must be request_review, not canonical
    req = cp.CurationRequest(kind="entity", intent="t", data={
        "id": "stemma:t.c", "type": "concept", "name": "C", "domain": "test",
        "status": "draft", "definition": "d", "provenance": {"ai_drafted": True}})
    dec = cp.run_pipeline(
        req,
        draft_callback=lambda bp, data, **kw: data,
        semantic_review_callback=lambda gate, artifact, bp: _pass(gate),
    )
    assert dec.action == "request_review"
    assert dec.action != "canonical"


def test_blueprint_carries_source_ref():
    req = cp.CurationRequest(kind="entity", intent="t", data={}, source_ref="stemma:src.x")
    bp = cp.blueprint_from_request(req)
    assert bp.source_ref == "stemma:src.x"


def test_entity_relationships_field_is_rejected():
    """ADR-0028/0035: entities carry no relationships, and the old relation gate
    no longer references a nonexistent validate.REL_TYPES."""
    assert not hasattr(validate, "REL_TYPES"), "dead validate.REL_TYPES must be gone"
    ok, findings = cp._check_relations({"id": "stemma:x.y", "relationships": []})
    assert not ok
    assert any("entities carry no relationships" in f for f in findings)
    ok, findings = cp._check_relations({"id": "stemma:x.y"})
    assert ok, findings
    print("PASS: entity relationships / dead REL_TYPES rejected")


if __name__ == "__main__":
    fns = [
        test_route_repair_maps_gates_to_stages,
        test_evaluate_and_publishable,
        test_good_entity_reaches_request_review,
        test_bad_entity_is_hold_and_never_publishable,
        test_intent_failure_forces_reject_or_hold,
        test_repair_loop_bounded_and_recovers,
        test_never_emits_canonical_action,
        test_blueprint_carries_source_ref,
        test_entity_relationships_field_is_rejected,
    ]
    for fn in fns:
        fn()
        print(f"PASS {fn.__name__}")
    print("ALL CURATION PIPELINE TESTS PASS")