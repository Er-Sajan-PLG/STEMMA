# SYSTEM SPECIFICATION — STEMMA CORE-GATE-EXPORT slice (pilot)

Version `0.1.0-pilot.CORE-GATE-EXPORT` · Baseline commit `fb66dd9` · 2026-09-22
Authority state: everything here is **PROPOSED** pending SOLE_OWNER approval.
Sections marked ⟦recovered-unapproved⟧ describe evidence-backed behavior not
yet approved as requirement; uncertainty is not disguised as prose (§13).

## 1. Purpose

STEMMA is an open, structured, reusable STEM knowledge foundation: canonical
science content as version-controlled Markdown+YAML, validated by a
deterministic gate, published as deterministic machine-readable exports.
This specification covers only the pilot slice: canonical corpus → gate → export.

## 2. Scope & non-goals

**In scope:** canonical object model, identity, gate behavior, export contract,
freshness/determinism, slice security invariants, HITL gating.

**Non-goals (explicit):** RAG answer quality; embedding model performance;
webapp UI; explorer rendering; adapter API surface beyond the export contract;
content breadth (corpus growth is R4 work, not this baseline); performance/scale
claims (R8).

## 3. Actors & context

- **Curator (human):** the only actor allowed to move content toward canonical;
  identified in metadata as `human:*`.
- **Executor agents/programs:** may draft, propose, validate, regenerate —
  never approve their own drafts into canonical (HITL invariant).
- **Consumers (external systems/users):** read exports only
  (IFACE-STEMMA-EXP-001); declared set: learninghub, professor-j,
  stemma-explorer, general (registry CLAIM — unverified against running
  consumers).
- **CI:** executes the same gate as local developers; merge requires all-green.

## 4. System behavior (layered contracts)

### 4.1 Canonical layer ⟦recovered-unapproved: REQ-CORE-001..004⟧

Three object kinds: entities (Markdown+YAML frontmatter), connections (one YAML
per assertion, mandatory evidence), sources (citation records). Identity:
`stemma:`-namespaced, immutable, supersede-don't-edit. Forbidden: embeddings,
curriculum semantics, secrets. Current corpus: 1 draft entity, 0 connections,
3 sources (2 unreferenced) — a state, not a requirement.

### 4.2 Gate ⟦recovered-unapproved: REQ-GATE-001..005; REQ-SCH-001..003⟧

Deterministic chain (see IFACE-STEMMA-GATE-001). Properties:
fail-closed (observed), no wall clock, no randomness (CI-checked),
schema-conformant objects only, registry coherence, status honesty,
docs consistency, ecosystem independence.

### 4.3 Export layer ⟦recovered-unapproved: REQ-EXP-001..004⟧

Deterministic regenerable artifacts: `knowledge.json` (export_version 2.2.0,
content_hash), review-aware variants, embeddings + vector store (deterministic
fallback), consumer-filtered exports, `reports/validation-report.json`.
Contract rule: additive within major version; versions single-sourced.
**Known defect-in-waiting (recorded, not resolved):** CONFLICT-STEMMA-EXP-001 —
meta.json `type: faiss` on the JSON fallback.

### 4.4 Data semantics (§14) ⟦recovered-unapproved⟧

- **Identity & lifecycle:** IDs immutable; corrections supersede; review status
  is data (`draft` → reviewed → canonical), not folder location.
- **Ownership:** canonical data owned by the foundation; derived artifacts
  owned by the pipeline; consumed copies owned by consumers.
- **Invariants:** evidence ≥1 per connection; `writer: human:*`; no dangling
  references (validator resolves source_refs/external_ids patterns).
- **Versioning/compatibility:** export_version additive-semantic; vocabulary
  versions in VERSION.yaml.
- **Sensitive data:** none in canonical layer; PDF corpora and API keys live
  outside git (XC-3, XC-5).

## 5. Failure behavior ⟦recovered-unapproved⟧

- Invalid canonical data or drifted status/docs/independence → gate exits
  non-zero; nothing ships (observed fail-closed, EVID-STEMMA-GATE-002).
- Missing gate dependencies → clear exit-2 error (pre-requirements.txt
  behavior; now declared, REQ-STEMMA-OPS-001).
- Derived-layer absence (embeddings etc.) → INFO, gate continues (explicit
  INFO-not-FAIL policy, EVID-STEMMA-GATE-010).
- **Not specified (gap):** retry/idempotency/backpressure/timeout behavior is
  not applicable to a batch CLI gate; recorded as NOT_APPLICABLE rather than
  invented (§13).

## 6. Interfaces

- IFACE-STEMMA-EXP-001 — `exports/knowledge.json` export contract (file, 2.2.0).
- IFACE-STEMMA-GATE-001 — verification-chain CLI contract (exit-code semantics).
See `spec/INTERFACES/`.

## 7. Security properties ⟦recovered-unapproved⟧

Secret-free canonical layer (CI); HITL-gated canonical mutation; immutable IDs;
no secrets/keys committed (XC-5 → REQ-SEC-002, webapp deep-check NOT_YET_ASSESSED).

## 8. Assumptions / unresolved / conflicts

`spec/ASSUMPTIONS.md` (5), `spec/OPEN_QUESTIONS.md` (6 open UNRES),
`spec/CONFLICTS.md` (1 open, 1 resolved). None resolved by assertion.

## 9. Acceptance criteria & conformance

Only after owner approval do REQ-* statements authorize conformance judgments.
Verification mapping lives in `spec/VERIFICATION.md`; traceability in
`spec/machine-readable/traceability.yaml`.

---

## Gate 4 checklist (§31)

- [x] approved requirements represented — N/A (none approved; PROPOSED set represented explicitly)
- [x] scope/non-goals represented (§2)
- [x] interfaces represented (§6 + spec/INTERFACES)
- [x] data semantics represented (§4.4)
- [x] failure/error behavior represented, incl. explicit NOT_APPLICABLE (§5)
- [x] compatibility represented (§4.3/4.4)
