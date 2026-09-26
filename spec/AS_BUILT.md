# AS-BUILT — CORE-GATE-EXPORT slice

Protocol §5. Every substantive claim cites `EVID-` records. Claims about
*intent* are marked CLAIM/INFERENCE and never merge into FACT (§0.1).

## 1. Canonical corpus (as present)

- The corpus holds exactly **1 entity** (`stemma:phys.metre`, type `unit`,
  **status `draft`**), **0 connections**, **3 source records**, of which 2 are
  unreferenced. [EVID-STEMMA-CORE-001, EVID-STEMMA-CORE-002]
- All canonical identity is in the `stemma:` namespace, enforced by pattern in
  the entity/source JSON Schemas. [EVID-STEMMA-CORE-003]
- The single entity declares human authorship (`ai_drafted: false`,
  `writer: human:curator.001`) with BIPM SI Brochure provenance in frontmatter.
  [EVID-STEMMA-HITL-002, EVID-STEMMA-CORE-001]

## 2. The deterministic gate (as behaves)

- `scripts/verify_all.py` executes: validate → status_truth → physics profile
  + governing checks → hitl_check → graph_analysis → export_review_aware →
  registry/domain/versioning tests → semantic-pipeline schema/evidence checks;
  embeddings/RAG/consumer checks are **INFO-only** by design. It passes at the
  baseline commit. [EVID-STEMMA-GATE-001, EVID-STEMMA-GATE-010]
- The chain **fails closed**: a failing step terminates with non-zero exit.
  [EVID-STEMMA-GATE-002]
- `validate.py` both validates canonical data and regenerates the derived
  export + validation report. [EVID-STEMMA-GATE-003]
- Gate dependencies are declared (`requirements.txt`); absent deps previously
  exited 2 with a clear error. [EVID-STEMMA-GATE-004]
- Honesty invariants are themselves machine gates: status_truth (README status
  block), docs-consistency (ADR-0029), independence (ADR-0027/0051).
  [EVID-STEMMA-GATE-006, -007, -008]
- CI previously did not run the full test suite (16 silent failures); the
  2026-09-22 hygiene commit added a pytest job required by the all-green gate.
  [EVID-STEMMA-GATE-009, EVID-STEMMA-GATE-005]

## 3. Export layer (as produced)

- `exports/knowledge.json` is `export_version 2.2.0` with a deterministic
  `content_hash`, regenerates byte-identically (no wall clock). Version data
  is single-sourced from `schema/VERSION.yaml`; the OpenAPI document tracks it
  at 2.2.0. [EVID-STEMMA-EXP-001, -002, EVID-STEMMA-SCH-001, -004]
- Seven review-aware variant exports (all/reviewed/canonical/trusted/
  proposed/rejected/extended) are regenerated from the same corpus in the
  gate. [EVID-STEMMA-EXP-003]
- The vector store today is a **deterministic JSON fallback**
  (`vectors.json` + `meta.json` + `ids.json`) whose `meta.json` nevertheless
  says `"type": "faiss"` — label/behavior divergence (CONFLICT-STEMMA-EXP-001).
  Embeddings (1 record, 384-dim) are produced by a deterministic hash fallback
  when real models are absent. [EVID-STEMMA-EXP-004, -005]
- Consumer exports: `learninghub` 0 entities (policy `canonical`, corpus all
  draft; intent-justified in docs — CLAIM, UNRES-STEMMA-EXP-001), `general`
  includes the draft. [EVID-STEMMA-EXP-006, -007]

## 4. Human-in-the-loop (as evidenced)

- The gate's `hitl_check` passes by reading an audit trail under `workflow/`
  which is **git-ignored**; the HITL evidence for the metre entity is therefore
  not part of the repository. [EVID-STEMMA-HITL-001, EVID-STEMMA-CORE-004]

## 5. Security surface (in-slice)

- Secret scanning (gitleaks) + canonical no-secrets grep + no-embeddings-in
  canonical check run in CI. [EVID-STEMMA-SEC-001, -002]

## 6. Naming/coverage reality (in-slice)

- Docs reference an SDK class `StemmaRAG` that the adapter does not contain.
  [EVID-STEMMA-INTEG-001]

## Intent recovered (CLAIM/INFERENCE — not behavior)

- Next milestone (R4/ADR-0052): 3–5 entities, 2–3 connections, both authority
  tiers proven. [EVID-STEMMA-CORE-005]
- Named consumers and their intended usage are declared, not observed.
  [EVID-STEMMA-INTEG-002, -003]
- Drift mechanism inference: prose-embedded counts/versions;
  countermeasure inference: machine-owned single sources. [EVID-STEMMA-OPS-004]

---

## Gate 1 checklist (§31)

- [x] substantive claims have evidence (each numbered claim cites EVID)
- [x] locators reproducible (file:line / command+observed output)
- [x] fact/inference separated (classes per item; intent section explicit)
- [x] confidence recorded (HIGH/MEDIUM/LOW per item)
- [x] no silent conflict resolution (CONFLICT-STEMMA-EXP-001 recorded, not resolved)
