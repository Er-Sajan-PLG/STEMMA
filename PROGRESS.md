# STEMMA Progress Tracker

> Live counts are owned by `scripts/status_truth.py` (README status block) —
> this file tracks *work*, not corpus counts, to avoid drift.

## Current State (verified 2026-09-22)

- **Canonical corpus:** 1 entity (metre, `draft`), 0 connections, 3 source records
- **Architecture:** v2 (ADR-0044), contract **export_version 2.2.0** (ADR-0050), schema 1.2.0
- **Gate:** `verify_all.py` ✅ green · full `pytest tests/` ✅ green (16 stale old-design
  tests archived 2026-09-22) · `test_docs_consistency` + `test_independence` live (un-stubbed per ADR-0051)
- **CI:** validate + freshness + docs-consistency + independence + pytest suite + explorer + webapp + embeddings/RAG + determinism

## ✅ Done

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

## 🔄 In Progress (R4 — Content Acceptance Test, ADR-0052)

Prove the full L8 chain end-to-end with both authority tiers:

- [ ] Register one trusted external institution in `agent-registry.yaml` (delegated authority path)
- [ ] Seed `phys.force` entity + one relational connection with non-empty `evidence[]`
- [ ] Seed one value-claim connection (value-slot XOR, ADR-0045)
- [ ] One human review pass to canonical via `scripts/review.py` (internal tier)
- [ ] One delegated-authority import with sample audit
- [ ] Exit: 3–5 entities, 2–3 connections, `verify_all.py` green, `git diff --exit-code -- exports reports` clean

## 📋 Backlog

- [ ] **R5 — Organization/IRI gate (HUMAN DECISION):** owning organization, domain, IRI base.
      Everything touching published IRIs waits on this. Decide before R4 content grows further.
- [ ] R6 — Projection publication (knowledge.jsonld, SKOS, SHACL, signed release bundle)
- [ ] R7 — Consumer views + routing (calibration from real review data, ≥200 labeled decisions)
- [ ] R8 — Scale readiness (10^4-entity git benchmark; content-addressed store ADR)
- [ ] Trim derived export variants (`exports/knowledge.*.json`) once R4 settles the review-flow shapes
- [ ] Option: move reference RAG out of repo to a separate STEMMA-RAG package (per ARCHITECTURE-V2 Part 5; can stay as convenience until then)

## Ground rules for this file

- Update on every merged change of *status*, never to repeat machine-owned counts
  (entities/connections/sources live in the README status-truth block).
- Dated entries only; no stale branch/port references.
