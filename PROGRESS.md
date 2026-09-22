# STEMMA Progress Tracker

> Live counts are owned by `scripts/status_truth.py` (README status block) —
> this file tracks *work*, not corpus counts, to avoid drift.

## Current State (verified 2026-09-22)

- **Canonical corpus:** 1 entity (metre, `draft`), 0 connections, 3 source records
- **Architecture:** v2 (ADR-0044), contract **export_version 2.2.0** (ADR-0050), schema 1.2.0
- **Gate:** `verify_all.py` ✅ green · full `pytest tests/` ✅ green (16 stale old-design
  tests archived 2026-09-22) · `test_docs_consistency` + `test_independence` live (un-stubbed per ADR-0051)
- **Specification:** recovered pilot baseline (protocol v3.1) at `spec/` — maturity **L2**
  slice-scoped; 22 requirements **PROPOSED** awaiting owner approval; nothing self-approved
- **CI:** validate + freshness + docs-consistency + independence + pytest suite + explorer + webapp + embeddings/RAG + determinism

## ✅ Done

- **Docs-system guard incidents recorded as successful enforcement** (owner direction, 2026-09-22):
  contract-registry caught the unregistered research brief; independence invariant caught a
  prompt-carried forbidden name; both repaired via registered roots. Recorded in
  docs/DOCUMENTATION-SYSTEM.md "Verified enforcement incidents".

- [x] Refoundation: architecture v2 + ADR-0040–0052 + strong CI (PR #47)
- [x] Old corpus archived (`archive/beginning-74-entities/`), old design archived (`archive/old-design/`)
- [x] **Governance hygiene sprint (ADR-0051 / R0 / R3), 2026-09-22:**
  - [x] `requirements.txt` + `requirements-dev.txt` (R0 reproducibility)
  - [x] Old-design v1.0 docs retired (byte-identical copies were duplicated live; archive keeps them)
  - [x] `ingestion_webapp/`, `n8n/`, `redteam/` archived; `docker-compose.yml` moved to archive
  - [x] 17 zero-reference old-design scripts archived (`archive/old-design/scripts/`)
  - [x] Stale evidence ledger (retired ID namespace) and `authority/exports-manifest.yaml` (export 0.1) archived
  - [x] retired-namespace sweep in AGENTS.md + `.agents/skills/` (ADR-0051)
  - [x] Dead Quick-Start refs fixed (NORTHSTAR/SPECIFICATION/force.md per ADR-0051 verification)
  - [x] `test_docs_consistency.py` + `test_independence.py` un-stubbed and wired into CI
  - [x] CI runs full pytest suite; broken stale tests archived, live tests fixed
  - [x] Adapter aligned with docs at **v0.2.0**; `schema/api.yaml` 2.2.0; `exports_manifest` removed
  - [x] Doc count drift fixed: 11 embedding models, export 2.2.0, `export_version: 2.2.0` in CONSUMERS.md
- [x] Webapp consolidation (ADR-0036): stdlib `webapp/` is the only ingestion UI;
  free-model catalog contract restored (all entries `:free`)
- [x] **Specification recovery pilot (protocol v3.1), 2026-09-22 (pre-R4):**
  - [x] Pilot charter + slice ADR (`spec/PILOT_CHARTER.md`, ADR-STEMMA-SPEC-001)
  - [x] 37 classified evidence records; as-built; external constraints; assumptions
  - [x] 22 requirements (full §8.6 schema) all PROPOSED — none self-approved
  - [x] Specification v0.1.0-pilot + 2 interface contracts + verification design (all UNVERIFIED per §9.1)
  - [x] Two-tier gap analysis + machine-readable registries + minimum validator (9/9 PASS, fail-closed)
  - [x] Baseline BASELINE-STEMMA-2026-09-22-PILOT-CORE-GATE-EXPORT — maturity L2; process review at root
- [x] **Documentation synchronization & enforcement system, 2026-09-22** (scoped to this repo):
  - [x] Phase-1 audit: 220-artifact taxonomy census with per-artifact disposition (`docs/meta/doc-taxonomy.yaml`, census generated at `docs/meta/documentation-coverage.md`)
  - [x] Machine-readable docs contract: ownership kinds CANONICAL/DERIVED/GENERATED/REFERENCE/INDEX + sources + depends_on (`docs/docs-contract.yaml`)
  - [x] Engine `scripts/docs.py`: `impact` (direct + transitive + unmapped-conservative), `sync` (idempotent), `validate` (contract integrity + broken links + generated drift), `check` (CI-equivalent), `coverage`
  - [x] Integrated existing gates as declared checks (docs-consistency 12, independence, recovery validator) — no replacement, single canonical command
  - [x] CI verify-docs now runs sync → `git diff --exit-code` → check (deleted duplicated shell "required docs" list)
  - [x] Found + fixed: 4 real broken links in CONTRIBUTING.md, `status_truth.py --write` non-idempotency bug (+4 blank lines per run)
  - [x] Engine self-tests (14) in `tests/repo/test_docs_engine.py` — suite now 147
  - [x] **Completion pass (same day):** Tier-1 artifacts created (`webapp/README.md`, `adapters/README.md`, `explorer/README.md`, PR template, 2 issue templates, `.env.example` + `.env` git-ignored); new mechanical invariants: `api_surface` (12 endpoints ↔ docs), `env_surface` (env vars ↔ `.env.example`/WEBAPP.md), tier-strict enforcement `[0,1]`; hooks wiring (pre-commit: impact+validate; pre-push: sync+diff+check); AGENTS.md docs mandate; +9 engine/integration tests → suite now 156
  - [x] Invariants caught real gaps on first run: `/v2/stats` undocumented in adapter README, 4 provider env vars undocumented (docs/WEBAPP.md section added), `OPENAI_API_KEY` missing from `.env.example`

## 🔄 In Progress (R4 — Content Acceptance Test, ADR-0052)

Prove the full L8 chain end-to-end with both authority tiers:

- [ ] Register one trusted external institution in `agent-registry.yaml` (delegated authority path)
- [ ] Seed `phys.force` entity + one relational connection with non-empty `evidence[]`
- [ ] Seed one value-claim connection (value-slot XOR, ADR-0045)
- [ ] One human review pass to canonical via `scripts/review.py` (internal tier)
- [ ] One delegated-authority import with sample audit
- [ ] Exit: 3–5 entities, 2–3 connections, `verify_all.py` green, `git diff --exit-code -- exports reports` clean

## 📋 Backlog

- [x] **R5 — Organization/IRI gate: identity SETTLED, PID base DEFERRED 2026-09-22
      (ADR-0053 + Amendment 0001, owner).** Binding: publisher = individual Sajan; canonical
      keeps immutable `stemma:` URNs. Under review after slow research
      (docs/PERSISTENT-IDENTIFIER-BRIEF.md) and deferred to R6 projection publication:
      PID domain/resolution choice. UNRES-STEMMA-CORE-001 partially resolved/open.
      Non-actions: slug NOT claimed; no ID changes; no resolution infra.
- [ ] R6 — Projection publication (knowledge.jsonld, SKOS, SHACL, signed release bundle)
- [ ] R7 — Consumer views + routing (calibration from real review data, ≥200 labeled decisions)
- [ ] R8 — Scale readiness (10^4-entity git benchmark; content-addressed store ADR)
- [ ] Trim derived export variants (`exports/knowledge.*.json`) once R4 settles the review-flow shapes
- [ ] Option: move reference RAG out of repo to a separate STEMMA-RAG package (per ARCHITECTURE-V2 Part 5; can stay as convenience until then)

## Ground rules for this file

- Update on every merged change of *status*, never to repeat machine-owned counts
  (entities/connections/sources live in the README status-truth block).
- Dated entries only; no stale branch/port references.
