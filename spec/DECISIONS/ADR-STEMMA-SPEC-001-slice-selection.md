# ADR-STEMMA-SPEC-001 — Pilot slice: canonical corpus → deterministic gate → derived export

- **Status:** Decided (executor decision within delegated recovery scope; ratification by SOLE_OWNER pending with baseline)
- **Date:** 2026-09-22 · **Domain:** SPEC · **Authority level:** REPOSITORY_LOCAL

## Context

Protocol v3.1 §1: recover one vertical slice first, not the whole repository.
STEMMA @ fb66dd9 is a data-foundation repository whose system behavior is
dominated by a deterministic validation gate and an export contract, on top of
a 1-entity canonical corpus after the 2026-09-21/22 refoundation and hygiene
sweep.

## Options considered

1. **CORE-GATE-EXPORT slice (chosen)** — `content/ connections/ sources/ schema/`
   → `scripts/validate.py` + `verify_all.py` → `exports/` + CI.
2. Webapp HITL ingestion slice — PDF → candidate → proposal → review.
3. RAG/embeddings derived slice — embed/rag/export_consumers + adapter `/v2/*`.

## Decision

Choose option 1.

## Rationale (reconstructed, not historical — marked accordingly)

- Externally observable contract (`exports/knowledge.json`, export_version 2.2.0)
  consumed by adapter/explorer/external consumers — the primary system interface.
- Contains the system's authoritative trust boundary (canonical vs derived) and
  its fail-closed control (the gate) — architecturally significant (§1).
- Richest existing verification evidence: gate output, 133-test suite, CI jobs.
- The 2026-09-22 drift findings (hardcoded counts/versions across docs) show
  exactly the evidence-vs-claim confusion this protocol tests.

## Consequences

- Webapp/adapters/explorer/RAG quality are explicitly `NOT_YET_ASSESSED`
  (Tier-2 inventory), never implied gap-free (§21.2).
- Cross-repo consumer interface ownership recorded as UNRES-STEMMA-INTEG-001.

## Evidence

EVID-STEMMA-GATE-001, EVID-STEMMA-EXP-001, EVID-STEMMA-CORE-001,
EVID-STEMMA-OPS-004 (see `spec/EVIDENCE_REGISTER.md`).
