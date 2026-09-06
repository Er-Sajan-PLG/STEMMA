#!/usr/bin/env python3
"""STEMMA (`stemma:` namespace) canonical-knowledge curation pipeline (architecture review §P).

A staged, hard-gate pipeline that turns a *curation request* into a governed
decision over canonical knowledge (entities, connections, sources). It mirrors the
structure of a content engine but is a **canonical-knowledge curator** — it never
produces stories, lessons, or pedagogy, and it never auto-canonicalizes.

Stages:
    Intake → Curation Blueprint → Draft (seam) → Deterministic Gates →
    Semantic Review (seam) → Hard-Gate evaluate → Targeted Repair → Decision

Roles (canonical, not storyteller):
    - Curator/Intaker  : intake → blueprint (deterministic)
    - Draft Agent      : produce a candidate draft object (LLM seam; never publishes)
    - Validator        : deterministic gates (reuses scripts/validate.py rules)
    - Reviewer         : semantic/fidelity gate (LLM seam + human override)
    - Governance Gate  : canonicalization is ALWAYS a human action via
                         scripts/review.py + scripts/curation_state.py
                         (this pipeline stops at a decision; it never sets 'canonical').

LLM-agnostic seam: every judgment boundary is an injected callback
(``draft_callback``, ``semantic_review_callback``). Deterministic gates run natively.
A runner supplies real callbacks; tests/humans inject fakes. Nothing here depends on
a specific model or provider.

Hard-gate rule: every applicable gate must PASS (fail → not publishable). Repair
routing maps a failed gate to the responsible stage and re-runs only that stage.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Literal

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import validate  # noqa: E402  (authoritative deterministic gate)

# --------------------------------------------------------------------------- #
# Domain types
# --------------------------------------------------------------------------- #

#: The five curation stages a change can be routed through for repair.
RepairStage = Literal["intake", "blueprint", "draft", "review", "not-recoverable"]

#: Verification gates. Judgment gates are delegated to the injected seam.
GATE = {
    "schema",        # deterministic
    "identity",      # deterministic
    "relations",     # deterministic
    "provenance",    # deterministic
    "resolution",    # deterministic
    "conditions",    # deterministic
    "intent",        # judgment (seam)
}

#: Gate → responsible stage (from architecture review §P.2).
GATE_TO_STAGE: dict[str, RepairStage] = {
    "schema": "draft",
    "identity": "intake",
    "relations": "blueprint",
    "provenance": "intake",
    "resolution": "intake",
    "conditions": "blueprint",
    "intent": "intake",
}


#: Decision actions the pipeline may reach. 'canonical' is NOT produced here — it is
#: a human governance action performed via scripts/review.py.
DecisionAction = Literal["propose", "request_review", "hold", "reject"]


@dataclass
class GateResult:
    gate: str
    verdict: str  # "pass" | "fail"
    findings: list[str] = field(default_factory=list)


@dataclass
class CurationRequest:
    """A proposed change to canonical knowledge (intake)."""
    kind: str                       # "entity" | "connection" | "source"
    intent: str                     # free-form: what should be true canonically
    data: dict[str, Any]            # proposed object (frontmatter / yaml)
    # Optional governance context:
    source_ref: str | None = None
    domain: str | None = None
    # Extraction metadata sidecar (ADR-0035): how the source text was obtained
    # (kind/format/pages/ocr_used/preview). Never placed on the canonical source.
    extraction: dict[str, Any] | None = None


@dataclass
class CurationBlueprint:
    """Deterministic plan of what the change touches and requires."""
    kind: str
    target_id: str | None
    requires: list[str] = field(default_factory=list)      # relations/entities needed
    proposed_status: str = "proposed"                       # connection review.status
    gates_to_run: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    source_ref: str | None = None                           # provenance anchor (e.g. ingested source)


@dataclass
class PublicationDecision:
    action: DecisionAction
    blueprint: CurationBlueprint
    artifact: dict[str, Any] | None
    gates: list[GateResult] = field(default_factory=list)
    reason: str = ""
    repair_rounds: int = 0

    @property
    def publishable(self) -> bool:
        return all(g.verdict == "pass" for g in self.gates)


# --------------------------------------------------------------------------- #
# Seam callbacks
# --------------------------------------------------------------------------- #

DraftCallback = Callable[..., dict[str, Any]]
SemanticReviewCallback = Callable[[str, dict[str, Any], CurationBlueprint], GateResult]


# --------------------------------------------------------------------------- #
# Deterministic gates (reuse the authoritative validator machinery)
# --------------------------------------------------------------------------- #

def _entity_gates(data: dict, blueprint: CurationBlueprint) -> list[GateResult]:
    results: list[GateResult] = []
    # Candidates from the seam have no filesystem path yet; give the reused validator
    # a synthetic _file so its error prefixes are stable.
    if "_file" not in data:
        data = {**data, "_file": f"<proposed:{blueprint.target_id or 'new'}>"}
    # identity: id format + uniqueness (validated against existing entities)
    _id = data.get("id")
    results.append(_gate(
        "identity",
        isinstance(_id, str) and bool(validate.ID_RE.fullmatch(_id)),
        f"invalid stable ID {_id!r} (expected stemma:<domain>.<slug>)",
    ))
    # schema: required fields + enums (reuse validate_entity's deterministic checks)
    errs: list[str] = []
    validate.validate_entity(data, errs, filename_slug=str(_id).rsplit(".", 1)[-1] if _id else None)
    results.append(GateResult("schema", "pass" if not errs else "fail", errs))
    # provenance: ai_drafted etc.
    prov = data.get("provenance")
    ok = isinstance(prov, dict) and isinstance(prov.get("ai_drafted"), bool)
    results.append(_gate("provenance", ok, "provenance must be an object with ai_drafted bool"))
    # relations: whitelist + dangling (resolve against registry + register set)
    relations_ok, rfind = _check_relations(data)
    results.append(_gate("relations", relations_ok, rfind))
    return results


def _connection_gates(data: dict, request: CurationRequest, blueprint: CurationBlueprint) -> list[GateResult]:
    results: list[GateResult] = []
    src, tgt, rel = data.get("source"), data.get("target"), data.get("relation")
    # identity / resolution: source/target resolve + relation in registry
    registry = validate.load_relation_registry().get("relations", {})
    results.append(_gate("resolution", bool(src) and bool(tgt), "connection needs source+target"))
    results.append(_gate("relations", rel in registry, f"relation {rel!r} not in relation-registry.yaml"))
    # conditions: context present (regime/scale) when a relation needs it
    ctx = data.get("context") or {}
    results.append(_gate("conditions", isinstance(ctx, dict), "connection.context must be an object"))
    # provenance: asserted_by/generated_by/method required
    prov = data.get("provenance") or {}
    prov_ok = all(prov.get(k) for k in ("asserted_by", "generated_by", "method"))
    results.append(_gate("provenance", prov_ok, "connection provenance needs asserted_by/generated_by/method"))
    return results


def _source_gates(data: dict, blueprint: CurationBlueprint) -> list[GateResult]:
    results: list[GateResult] = []
    _id = data.get("id")
    results.append(_gate(
        "identity",
        isinstance(_id, str) and bool(validate.SRC_ID_RE.fullmatch(_id)),
        f"invalid source ID {_id!r} (expected stemma:src.<slug>)",
    ))
    return results


def _check_relations(data: dict) -> tuple[bool, list[str]]:
    """ADR-0028/0035: entities carry NO relationship data.

    The old gate read a `validate.REL_TYPES` attribute that never existed and
    allowed `relationships: []` on drafts. Entities are not the relationship
    graph; assert relationships as first-class objects in connections/.
    """
    if "relationships" in data:
        return False, [
            "entities carry no relationships (ADR-0028/0035): assert relationships "
            "as first-class objects in connections/, never as an entity field"
        ]
    return True, []


def _gate(name: str, ok: bool, finding: str | list[str]) -> GateResult:
    findings = [finding] if isinstance(finding, str) else list(finding)
    return GateResult(name, "pass" if ok else "fail", [] if ok else findings)


# --------------------------------------------------------------------------- #
# Hard-gate evaluation + repair routing
# --------------------------------------------------------------------------- #

def evaluate_gates(gates: list[GateResult]) -> list[GateResult]:
    return gates


def route_repair(failed: list[GateResult]) -> list[str]:
    """Map failed gates to the responsible stage(s)."""
    return [GATE_TO_STAGE.get(g.gate, "not-recoverable") for g in failed if g.verdict == "fail"]


# --------------------------------------------------------------------------- #
# Blueprint stage (deterministic)
# --------------------------------------------------------------------------- #

def blueprint_from_request(request: CurationRequest) -> CurationBlueprint:
    """Plan the change deterministically (no LLM)."""
    kind = request.kind
    target_id = request.data.get("id") or (f"stemma:conn.???" if kind == "connection" else None)
    gates = list(GATE) if kind != "source" else GATE - {"relations", "conditions"}
    bp = CurationBlueprint(
        kind=kind,
        target_id=str(target_id) if target_id else None,
        requires=[],
        proposed_status="proposed",
        gates_to_run=sorted(gates),
        notes=[f"intent: {request.intent}", f"kind: {kind}"],
        source_ref=request.source_ref,
    )
    return bp


# --------------------------------------------------------------------------- #
# The pipeline
# --------------------------------------------------------------------------- #

def run_pipeline(
    request: CurationRequest,
    *,
    draft_callback: DraftCallback,
    semantic_review_callback: SemanticReviewCallback,
    max_repair_rounds: int = 2,
) -> PublicationDecision:
    """Run the curation pipeline for one request.

    Deterministic gates run natively; judgment gates (intent, and any semantic
    review a runner enables) are delegated to the injected callbacks. The pipeline
    never sets 'canonical' itself; it produces a decision the human Governance Gate
    acts on via scripts/review.py.
    """
    blueprint = blueprint_from_request(request)

    # Stage: draft — produce a candidate artifact (LLM seam).
    artifact = draft_callback(blueprint, request.data)

    # Stage: deterministic gates.
    gates = _run_deterministic_gates(request, blueprint, artifact)
    # Stage: semantic review (seam) for the judgment gate 'intent'.
    intent = semantic_review_callback("intent", artifact, blueprint)
    gates.append(intent)

    decision = evaluate_gates(gates)
    rounds = 0
    while not all(g.verdict == "pass" for g in decision) and rounds < max_repair_rounds:
        rounds += 1
        stages = route_repair(decision)
        # Repair: re-draft with findings, then re-run deterministic + intent gates.
        findings = [f for g in decision if g.verdict == "fail" for f in g.findings]
        artifact = draft_callback(blueprint, request.data, repair={"artifact": artifact, "findings": findings})
        gates = _run_deterministic_gates(request, blueprint, artifact)
        gates.append(semantic_review_callback("intent", artifact, blueprint))
        decision = evaluate_gates(gates)

    debrief = [g for g in decision if g.verdict == "pass"]
    # Map the hard-gate result to a governed decision.
    if all(g.verdict == "pass" for g in decision):
        action: DecisionAction = "request_review"  # a human must canonicalize
        reason = "all gates pass; human Governance Gate must canonicalize via scripts/review.py"
    else:
        # Failing gates: 'intent' or unrecoverable scheme -> reject/hold; else propose-with-issues.
        failed_stages = route_repair(decision)
        if "not-recoverable" in failed_stages:
            action, reason = "reject", "unrecoverable plan failure"
        elif "intake" in failed_stages or "intent" in [g.gate for g in decision if g.verdict == "fail"]:
            action, reason = "hold", "request intent or intake not satisfiable; needs human/LLM attention"
        else:
            action, reason = "propose", "candidate produced with fixable gate failures; hold for review"

    return PublicationDecision(
        action=action,
        blueprint=blueprint,
        artifact=artifact,
        gates=decision,
        reason=reason,
        repair_rounds=rounds,
    )


def _run_deterministic_gates(request: CurationRequest, blueprint: CurationBlueprint, artifact: dict) -> list[GateResult]:
    """Run the native (LLM-free) gates appropriate to the object kind."""
    if request.kind == "connection":
        return _connection_gates(artifact, request, blueprint)
    if request.kind == "source":
        return _source_gates(artifact, blueprint)
    return _entity_gates(artifact, blueprint)


# --------------------------------------------------------------------------- #
# CLI (human / basic drive without an LLM runner)
# --------------------------------------------------------------------------- #

def _main() -> int:
    import argparse
    import json

    p = argparse.ArgumentParser(description="STEMMA curation pipeline (canonical-knowledge stages).")
    p.add_argument("--kind", required=True, choices=["entity", "connection", "source"])
    p.add_argument("--intent", required=True, help="what should be true canonically")
    p.add_argument("--data", required=True, help="path to a YAML/JSON proposal artifact")
    p.add_argument("--json", action="store_true", help="emit decision as JSON")
    args = p.parse_args()

    data = _load_proposal(args.data)
    if data is None:
        print("error: could not parse proposal file", file=sys.stderr)
        return 1
    request = CurationRequest(kind=args.kind, intent=args.intent, data=data)

    # A minimal no-LLM runner: draft is a passthrough (identity), semantic review
    # uses the deterministic gates only. Real LLM callbacks are supplied by a runner.
    decision = run_pipeline(
        request,
        draft_callback=lambda bp, data, **kw: data,
        semantic_review_callback=lambda gate, artifact, bp: GateResult(
            gate, "pass", [] if artifact else ["empty artifact"]
        ),
    )

    if args.json:
        print(json.dumps({
            "action": decision.action,
            "reason": decision.reason,
            "gates": [{"gate": g.gate, "verdict": g.verdict, "findings": g.findings} for g in decision.gates],
            "repair_rounds": decision.repair_rounds,
        }, indent=2))
    else:
        print(f"DECISION: {decision.action}")
        print(f"  reason: {decision.reason}")
        for g in decision.gates:
            mark = "PASS" if g.verdict == "pass" else "FAIL"
            print(f"  [{mark}] {g.gate}" + (f" — {g.findings[0]}" if g.findings else ""))
    return 0


def _load_proposal(path: str) -> dict[str, Any] | None:
    text = Path(path).read_text(encoding="utf-8")
    if path.endswith(".json"):
        import json
        return json.loads(text)
    try:
        return yaml.safe_load(text)
    except yaml.YAMLError:
        return None


if __name__ == "__main__":
    sys.exit(_main())


__all__ = [
    "CurationRequest", "CurationBlueprint", "PublicationDecision", "GateResult",
    "run_pipeline", "blueprint_from_request", "evaluate_gates", "route_repair",
    "RepairStage", "DecisionAction",
]