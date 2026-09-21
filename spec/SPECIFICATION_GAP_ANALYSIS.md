# SPECIFICATION GAP ANALYSIS — CORE-GATE-EXPORT slice

Protocol §21. All requirements are PROPOSED (unapproved) → findings below are
**preliminary observations** (§21.1); nothing here declares authoritative
nonconformance.

## Tier 1 — Deep pilot findings (inside slice)

| Class | Finding | Evidence | Notes |
|---|---|---|---|
| SPECIFIED_AND_IMPLEMENTED | Deterministic, content-hashed, no-wall-clock export regeneration | EVID-EXP-001/-002 | strongest area of the system |
| SPECIFIED_AND_IMPLEMENTED | Fail-closed gate chain | EVID-GATE-002 | see PARTIAL note on negative test |
| SPECIFIED_AND_IMPLEMENTED | Status truth as a gate | EVID-GATE-006 | |
| SPECIFIED_AND_IMPLEMENTED | Docs-consistency + independence invariants as live gates | EVID-GATE-007/-008 | un-stubbed 2026-09-22 |
| SPECIFIED_AND_IMPLEMENTED | Registry coherence & schema validation in gate | EVID-GATE-001, SCH-003 | |
| SPECIFIED_AND_PARTIAL | Negative-path (fail-closed) CI coverage | EVID-GATE-002 | behavior observed manually once; not encoded as a permanent CI negative test (VERIFICATION.md gap column) |
| SPECIFIED_AND_PARTIAL | HITL enforcement | EVID-HITL-001, CORE-004 | enforced on operator machine; audit evidence not repository-portable → UNRES-STEMMA-HITL-001 |
| SPECIFIED_AND_MISSING | `StemmaRAG` SDK surface referenced in 3 living docs, absent from adapter | EVID-INTEG-001 | either implement or correct docs (owner decision) |
| IMPLEMENTED_AND_UNSPECIFIED | Webapp `deterministic` provider shipped before test/doc alignment | webapp/providers.py (fixed in 6f90c32) | now covered by provider-registry test |
| IMPLEMENTED_AND_UNSPECIFIED | Seven review-aware export variants regenerated in gate; consumption semantics thinly documented | EVID-EXP-003 | docs explain filtering per consumer, not the variant matrix |
| CONTRADICTORY | meta.json `type: faiss` label on JSON fallback store | EVID-EXP-004 | CONFLICT-STEMMA-EXP-001 — OPEN |
| CONTRADICTORY | "no related_to" prose vs registry adopting related_to | EVID-SCH-002 | CONFLICT-STEMMA-SCH-001 — RESOLVED 2026-09-22 via explicit physics-core scoping |
| UNVERIFIABLE (today) | "Deterministic scales to 1000s of PDFs"; embedding "SOTA" quality; RAG retrieval precision/faithfulness claims | docs CLAIM prose | no benchmark/evaluation harness exists; R8 roadmap item; do not cite as capability |
| OBSOLETE | retired-namespace ledger, export-0.1 manifest, old-design v1.0 acquisition docs, 16 stale tests | EVID-OPS-003 | archived 2026-09-22; clean removal recorded |
| UNRESOLVED | Approval path exists but unexercised; 6 UNRES items open | ROLES_AND_AUTHORITY; OPEN_QUESTIONS | approval is the next human action |

## Tier 2 — Repository-wide coverage inventory

| Subsystem | Status | Note |
|---|---|---|
| Canonical corpus (content/connections/sources) | ASSESSED | this pilot |
| JSON Schemas, registries, VERSION.yaml, vocabularies | ASSESSED | this pilot |
| validate.py + verify_all.py gate chain | ASSESSED | this pilot |
| status_truth / docs-consistency / independence invariants | ASSESSED | this pilot |
| Export generation (knowledge.json, variants, embeddings fallback, vector store meta) | ASSESSED | this pilot |
| Consumer export filtering | ASSESSED | behavior observed; intent UNRES |
| CI job definitions + pre-commit config | ASSESSED | definitions inspected; runtime only sampled |
| Security scans (gitleaks, greps) | ASSESSED | in-slice |
| webapp/ (server, core, providers, UI, key handling) | NOT_YET_ASSESSED | recommended second pilot |
| adapters/python (SDK/API/RAG endpoints beyond export surface) | NOT_YET_ASSESSED | version/contract surface only |
| explorer/ | NOT_YET_ASSESSED | consumer app |
| Ingestion internals (pdf_ingest_primary, evolvable_template, semantic_extract, proposal_generate, entity_resolution, verify_claim, conflict_analysis) | NOT_YET_ASSESSED | gate-sampled only |
| RAG internals (embed.py, rag.py, export_consumers.py) | NOT_YET_ASSESSED | meta-label finding only |
| examples/external-rag | OUT_OF_SCOPE | demonstration consumer |
| archive/ | OUT_OF_SCOPE | immutable history (ASM-STEMMA-CORE-001) |
| git-ignored workflow/ contents | OUT_OF_SCOPE | local HITL trail; see UNRES-STEMMA-HITL-001 |

Absence of findings in NOT_YET_ASSESSED areas is not evidence of gap-freeness (§21.2).

## Gate 7 checklist (§31)

- [x] machine references resolve (validator run — see BASELINE.md)
- [x] status-aware gap analysis complete (all findings pre-approval observations)
- [x] deep slice findings complete (Tier 1)
- [x] repository-wide coverage inventory complete (Tier 2)
- [x] unknown areas explicitly identified
