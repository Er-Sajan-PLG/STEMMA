# STEMMA Ingestion System — Forensic Audit Baseline

Date: 2026-09-09
Auditor: Hermes (autonomous)
Scope: ingestion system readiness (user goal: "I mainly want ingestion system of STEMMA ready. I want to test STEMMA later tonight.")

## 1. Executive Summary

STEMMA's ingestion system has a **correct, well-tested core** (`scripts/ingest.py`,
`scripts/ingest_to_proposals.py`, `scripts/curation_pipeline.py`, and the ADR-0036
`webapp/`) but carries a **stale, governance-violating sibling** (`ingestion_webapp/`)
that must be retired. The core is production-ready; the consolidation is the remaining
work.

## 2. Architecture Inventory

### Correct / tested (KEEP)
| Component | Role | Test state |
|-----------|------|-----------|
| `scripts/ingest.py` | deterministic extraction (PDF/poppler+pypdf, image/tesseract+pillow, text) | 12/12 pass |
| `scripts/ingest_to_proposals.py` | CLI runner, fail-closed Draft seam (ADR-0035) | all pass |
| `scripts/curation_pipeline.py` | hard-gate curation (schema/identity/relations/provenance/conditions/intent) | all pass |
| `webapp/` (stdlib, :8081) | ADR-0036 human-in-the-loop review app | webapp-core pass |

### Stale / divergent (RETIRE)
| Component | Role | Problem |
|-----------|------|---------|
| `ingestion_webapp/` (FastAPI, :8002) | "LLM Studio" superset | (1) NO ADR, (2) zero tests, (3) no source frontend (minified index.html only), (4) **writes canonical directly** via `canonicalize_proposal`, (5) uses legacy `lhs:` namespace |

## 3. Governance Violations Found (evidence)

**V1 — `ingestion_webapp/backend/main.py` writes canonical directly.**
- L561-631 `canonicalize_proposal` writes `content/`, `connections/`, `sources/`
  and shells out `scripts/validate.py`.
- Violates ADR-0035 ("never auto-canonicalizes"), ADR-0036 ("never writes canonical"),
  AGENTS.md ("canonicalization is ALWAYS a human action via scripts/review.py +
  scripts/curation_state.py").

**V2 — namespace drift (`lhs:` vs `stemma:`).**
- `ingestion_webapp` uses `lhs:src.`/`lhs:conn.` (legacy).
- Canonical schema only accepts `stemma:` (validate.py SRC_ID_RE, source.schema.json).
- `webapp/` correctly uses `stemma:`.

## 4. Test Baseline

- Ingestion + curation + webapp-core: ALL PASS.
- Failures are unrelated to ingestion (empty-KB assertions in
  test_connection_immutability >600, test_e1_regression canonical==50,
  test_phase_b_integrity total_related_to>0).
- Tests run as plain python3 scripts (no pytest); each has a __main__ driver.

## 5. Plan (NOW / SEAM / LATER)

NOW:
1. Retire `ingestion_webapp/` (it violates governance; superseded by webapp/).
2. Port the genuinely-missing LLM Studio features into `webapp/`:
   - multi-provider free-model fetch (OpenRouter/NVIDIA live listing)
   - provider model listing is already present; add the free-tier model catalog.
3. Make end-to-end ingestion testable (add a coverage gap test for the consolidated
   webapp provider model-list against the free-model catalog).
4. Run full verify chain.

SEAM: document-only — `lhs:` ↔ `stemma:` namespace handling in provider models.

LATER: ADR for webapp consolidation (already tracked in PROGRESS.md backlog).