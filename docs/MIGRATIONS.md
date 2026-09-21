# MIGRATIONS (BEGINNING, NO LEGACY)

**Status:** Beginning, no legacy. Old migrations archived to archive/old-design/.

## 2026-09-21 — Beginning: physics-core v2 minimal with dual verification + governing laws

- **Tag:** ADR-0040/0041/0042/0043 · **Kind:** breaking? No, beginning, no old data
- **Changed:** New minimal design: every entity has governed_by, source_refs, writer, link, retrieved_at, source_kind, source; every connection evidence>=1; governing registry 23 laws; deterministic placement without LLM
- **Old data:** None — this is beginning, 0 entities before, 17 now
- **Consumer impact:** None — new beginning


## 2026-09-21 — Reset to Beginning Clean, PDF Primary with HITL, Evolvable Templates, model selector like DeepSeek harness (local + frontier models)

- **Changed:** Archived 74 entities + 150 connections to archive/beginning-74-entities/, reset content/physics/ to 1 entity (metre) via PDF primary ingestion with HITL
- **Added:** PDF primary ingestion with HITL before canonical — PDF (SI Brochure 9th ed., HRW 12th ed., custom) → ingest.py deterministic → AI draft to markdown preview → human explicitly edits markdown → stage → validate (including hitl_check.py) → review_entity accept/canonicalize
- **Added:** Deterministic scales — uses schema/template-registry.yaml with regex rules + exact SI constants c,h,ΔνCs,e,k,N_A,K_cd, no LLM, no cost, scales to any domain (physics, chemistry, biology, math), evolvable without code change via `python3 scripts/evolvable_template.py --evolve`
- **Added:** LLM fallback only when PDF missing exact SI — frontier models DeepSeek R1/V3 free, Claude 3.5 Sonnet/Opus, GPT-4o/o1, Gemini 2.5 Pro/2.0 Flash free, Llama 3.3 70B free, Qwen, Nemotron via OpenRouter/NVIDIA NIM, selector like DeepSeek harness (search, categories Frontier/Reasoning/Free/Custom, 25 models, custom model input), even LLM requires HITL
- **Added:** scripts/hitl_check.py (enforces human edited markdown before canonical), scripts/pdf_ingest_primary.py (primary feeder), scripts/evolvable_template.py (deterministic extraction + evolvable), schema/template-registry.yaml (evolvable, domain-agnostic)
- **Updated:** webapp/ with model selector like DeepSeek harness (local + frontier models) with search, categories, frontier models, custom input), deterministic draft (no LLM, scales) + AI draft with frontier buttons, markdown preview textarea + checklist + Save human edit HITL
- **Updated:** All docs (ARCHITECTURE, CONSUMERS, DOMAIN-MODEL, GOVERNANCE, VISION, README, CURATION-PROTOCOL, SCHEMA-SPECIFICATION, METADATA-SPECIFICATION, STANDARDS, TESTING, VERSIONING, IMPLEMENTATION-STATUS, ROADMAP, PIPELINES, AGENT, INGESTION-PRIMARY) to reflect 1 entity via HITL, deterministic scales, evolvable templates, frontier selector
- **Verification:** validate.py OK 1, physics_core_profile_check OK 0, physics_governing_check OK 0, hitl_check OK HITL satisfied, verify_all OK — beginning clean, HITL enforced, PDF primary deterministic scales, evolvable, frontier
