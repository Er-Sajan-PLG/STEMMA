# ROADMAP — Architecture v2 Ideal Order

Status: Authoritative
Baseline: b958a5c empty corpus
Architecture: docs/ARCHITECTURE-V2.md
Implementation Plan: docs/IMPLEMENTATION-PLAN-V2.md
Decisions: docs/decisions/README.md 0040-0053

Ideal order history: b958a5c empty → 51fc1b0 architecture v2 clean → 493b32b implementation plan v2 → 27576f3 foundation reset fundamentals clean 3D → 3bcfd4a ingestion pipeline evolvable templates model selector → e692b25 comprehensive all-STEM template registry → dbc229f embeddings RAG separation consumer export guideline → 7297c6c strong CI explorer semantic pipeline final → 0df87ff fix status truth.

## R0 — Foundation Prerequisites (Hours) — Phase 0

- Declare pyyaml + jsonschema in root requirements.txt (currently inline in .github/workflows/ci.yml, clean clone gate exits 2)
- Archive old ADRs 0001-0039 to archive/old-design/docs/decisions/
- Write ADR-0044 clean constitutional spec L1-L8 refined
- Update docs/decisions/README.md retitle LearningHubSTEM to STEMMA Foundation index ADRs 0023-0044
- Fix AGENTS.md dead Quick Start refs (retired docs)
- Fix ingest.py candidates conform to source.schema.json, remove hand-written report prose stale counts

Exit: ADR-0044 committed, README indexed, requirements.txt present, AGENTS.md clean, gate green.

## R1a — Value-Slot (Days) — Phase 1a — ADR-0045

- Make target and value mutually exclusive XOR in connection.schema.json
- Extend claim_signature computation in validate.py sha256(source|relation|value_canonical|polarity|sorted(qualifiers))
- Extend check_id_immutability.py to cover value-slot claims
- Unit field interim allowlist QUDT/UCUM/SI symbols m kg s A K mol cd documented anchor strings until ADR-0024 not just "1"

Exit: Schemas updated, validator handles new shapes, tests pass, gate green.

Verification: both target and value → schema error, neither → error, value without evidence at canonical → gate error.

## R1b — Warrant Axis + Correction Labels (Days) — Phase 1b — ADR-0046

- Extend confidence_basis enum with definitional axiomatic model_based
- Update check_assertion_epistemics to handle extended basis without requiring inference blocks for non-inferred types, keep assertion.type 3 values asserted inferred proposed
- Add optional correction_class enum to review_history[] items factual_error category_error relationship_error provenance_error incompleteness hallucination format_error dangling_ref start used 3 reserve 8

Exit: Validator handles extended basis, tests pass.

## R1c — L7 Refinement Not Purge (Days) — Phase 1c — ADR-0047

- Remove learning_objectives instructional_sequencing from concept.schema.json properties entirely
- Allow real_world_applications common_misconceptions ONLY when evidenced as ValueClaim with evidence[] and source not free-form strings
- Extend test_generality.py to reject pedagogical keys but allow evidenced knowledge claims
- Record the archived SOTA review's §6.5 softer alternative as partially adopted via extension-registry.yaml

Exit: Schema updated, test_generality rejects pedagogical keys but allows evidenced claims.

## R1d — New Relations (Days) — Phase 1d — ADR-0048

- Adopt equivalent_to domain law range law symmetric true transitive true
- Adopt misconception_of domain misconception range enumerated entity types from concept.schema enum NOT "any" symmetric false inverse null transitive false
- Update validator domain/range checks

Exit: Registry updated, validator handles new relations.

## R1e — Delegated Authority v2 (Days) — Phase 1e — ADR-0049

- Add authority field internal|delegated to reviewed_by[] and review_history[] in connection.schema.json
- Add trusted-institution entry type to agent-registry.yaml with audit_frequency sample_audit_rate last_audit next_audit review_standard_version delegated_provenance block
- Update validator to accept delegated authority for canonical transitions only with registered institution
- Add sample audit check 10% first 100 5% ongoing annual audit, revocation procedure, update export contract to expose authority field

Exit: Schemas updated, validator handles delegated authority, tests pass.

## R2 — Contract Update (Days) — Phase 2 — ADR-0050

- export_version 2.2.0→2.2.0 in schema/export.schema.json and schema/VERSION.yaml add authority field and value-slot support
- Update adapters/python/ to handle value-slot and delegated authority
- Update explorer/ to render value-slot claims and authority filter clean small nodes thin lines manual legend centered zoom 8 domains
- Update docs/CONSUMERS.md with new contract surface

Exit: Export contract bumped, adapter round-trips, explorer renders, gate green.

## R3 — Governance Hygiene (Hours) — Phase 3 — ADR-0051

- lhs sweep across all tracked files EXCEPT ADR documents which are history per ADR-0027 §3
- Un-stub tests/repo/test_independence.py and remove ecosystem references from AGENTS.md in same PR
- Close ADR-0027 owner-ratification gate

Exit: No stale references, independence test live, namespace clean.

## RS0 — Specification Recovery Pilot (Before R4) — ✅ DONE 2026-09-22 — Protocol v3.1

Specification Recovery Protocol v3.1 (pilot edition) executed on the CORE-GATE-EXPORT
vertical slice ahead of R4. Evidence → as-built → requirements → specification chain
recovered; implementation treated as evidence, not authority.

- Charter `../spec/PILOT_CHARTER.md`, slice recorded as ADR-STEMMA-SPEC-001 (`../spec/DECISIONS/`)
- 37 classified evidence records; 22 requirements (full §8.6 schema) **ALL PROPOSED** — owner approval pending (SOLE_OWNER Sajan; agent had no approval power)
- 2 interfaces (export knowledge.json 2.2.0; verify_all CLI), 6 UNRES, 2 CONFLICT (1 OPEN: vector-store `meta.json` type label), assumptions, two-tier gap analysis
- Machine-readable canonical set `../spec/machine-readable/` + minimum validator (9/9 checks, fails closed)
- Baseline `../spec/BASELINE.md`, maturity **L2 slice-scoped** — L3 blocked on owner approval, L4 blocked per §9.1 (no VERIFIED pre-APPROVED)
- Mandatory process review: `../SPECIFICATION_PROCESS_REVIEW.md`

Exit: baseline artifacts complete and validated; approval + verification queue handed to owner.
R5 partially settled 2026-09-22 (ADR-0053 + Amendment 0001, owner) — identity binding; PID/resolution base deferred to R6; UNRES-STEMMA-CORE-001 partially resolved/open; R4 proceeds unchanged.

## R4 — Content as Acceptance Test Before IRI Gate (Hours to Days) — Phase 4 — ADR-0052 — Work Integrating Early Work

**Status 2026-09-22:** mechanical side complete (all seeds + delegated import + machine gates green: validate, verify_all, pytest 161); the remaining item is the OWNER human review pass to canonical (ADR-0052 step f) — see PROGRESS.md for the tracked state and exact handoff commands.

R4 value already delivered beyond the seeds: the exercise exposed and fixed the dormant value-slot (ADR-0045) engine gap across validate/graph/immutability/triage/anomalies/subsets, two stale corpus-scale test pins, and identified a follow-up governance item (adopt reserved measurement-relation family via micro-ADR).

Goal: Prove full L8 chain both authority tiers, corpus has real content, engine built, integrating all early work from start as implementation of architecture.

Early work integrated:
- Reset to beginning 0 new primary PDF ingestion HITL markdown explicit edit — content/physics/measurement-units/metre.md 1 entity metre via HITL old 74 archived
- Fundamentals visible length mass time + derived area volume speed weight agreed definitions with refs clean 3D centering — docs/PHYSICS-MINIMAL-DESIGN-V2.md etc explorer clean small nodes thin lines
- Standard scientific definitions exactly as meter example with reference — docs/ARCHITECTURE.md comprehensive all-STEM mediocre coverage now 1 entity metre via HITL
- Clean minimal 3D small nodes thin lines manual legend centered zoom — explorer/
- Evolvable templates frontier model selector DeepSeek harness deterministic scales LLM fallback — scripts/evolvable_template.py webapp/
- Comprehensive all-STEM mediocre 8 domains 97 subdomains 12 entity types — schema/template-registry.yaml
- Explicit separation canonical vs derived vs consumer embeddings RAG consumer's job reference implementation guideline 81KB sample in derived — schema/embedding-registry.yaml consumer-registry.yaml llm-registry.yaml docs/GUIDELINE-EMBEDDER-RAG.md
- Strong CI + explorer + ingestion pipeline nothing bad gets pushed/merged 10 jobs all-green final gate — .github/workflows/ci.yml scripts/verify_all.py verify_strong.py
- Semantic acquisition pipeline 16 stages evidence first-class AI output must be proposal independent verification conflict explicit — scripts/semantic_extract.py verify_claim.py conflict_analysis.py proposal_generate.py entity_resolution.py schema/semantic-claim.schema.json

Tasks:
- Register one trusted external institution in agent-registry.yaml exercises delegated authority v2 path with audit
- Seed one source record conforming to source.schema.json SI Brochure 9th ed
- Seed two entities metre with scientific definition exactly as meter example with reference fundamental quantities visible and phys.force with definition and reference conforming to updated concept.schema.json
- Seed one relational connection with non-empty evidence[] pointing to source record
- Seed one value-claim connection measurement or misconception prevalence exercising value-slot
- One human review pass to canonical via scripts/review.py internal authority
- One delegated-authority import exercising institution path with sample audit
- python3 scripts/verify_all.py + git diff --exit-code -- exports reports

Exit: Full L8 chain proven end-to-end both authority tiers corpus has 3-5 entities 2-3 connections real content engine built.

## R5 — Organization/IRI Gate — ◐ PARTIAL 2026-09-22 — ADR-0053 + Amendment 0001

Owner rulings in 0053-organization-domain-iri-base.md (Amendment 0001, after
slow-research evaluation docs/PERSISTENT-IDENTIFIER-BRIEF.md):
- SETTLED (binding): publisher of record = individual Sajan; canonical keeps
  immutable `stemma:` URN identifiers; resolution never enters canonical files.
- OPEN / DEFERRED to R6 projection publication: published-PID domain and
  resolution architecture (w3id.org is a candidate, not a decision). Research
  established this is safely deferrable pre-publication.
- Non-actions: slug NOT claimed; no ID changes; no resolution infrastructure.
R4 proceeds unchanged (never depended on the gate).

## R6 — Projection Publication (Roadmap R4 After Phase 5) Days

exports/knowledge.jsonld + SKOS mapping + context file + SHACL shapes learn-from + signed release bundle + integrity manifest pluggable BFO schema.org

## R7 — Consumer Views and Routing (After Phase 6) Days

exports/views/* generation determinism tests calibration report from real review data review-queue routing R7 heuristic worksheet-ordering not predictive model threshold ≥200 labeled decisions across ≥3 domains.

## R8 — Scale Readiness (Days)

Benchmark git performance at 10^4 entities design content-addressed store with Merkle roots decide via ADR whether to migrate at 10^5 keep sharded YAML+LFS for now document migration plan.

## Current Status — After Ideal Order Rewrite

- b958a5c empty corpus engine not yet built
- 51fc1b0 architecture v2 clean constitutional foundation single part L1-L8 refined
- 493b32b implementation plan v2 Phases 0-8 ideal order
- 27576f3 foundation reset fundamentals standard SI definitions clean 3D viewer integrating early work
- 3bcfd4a ingestion pipeline evolvable templates model selector integrating early work
- e692b25 comprehensive all-STEM template registry integrating early work
- dbc229f embeddings RAG separation consumer export guideline integrating early work
- 7297c6c strong CI explorer semantic pipeline final integrating early work
- 0df87ff fix status truth 1 entity 3 sources
- Now new docs new ADRs 0045-0052 roadmaps updated to architecture v2

Verification: make quick-verify PASS — 1 entity metre via HITL, 0 connections, 3 sources, embeddings deterministic content_hash sha256:2c007fc6..., RAG vector search metre 0.2874 citations, semantic pipeline evidence first-class conflict demo P=10 vs P=12, explorer clean small nodes thin lines manual legend centered zoom 8 domains, webapp HITL PDF primary model selector DeepSeek harness, strong CI 10 jobs all-green.

## Not on roadmap — for canonical only

All STEM at once without HITL, hosting without auth, curriculum, ontology, database as source of truth, bypassing hitl_check, LLM without human edit — but embeddings, RAG, consumer export ARE on roadmap now as derived + consumer.

## Scaling + Frontier + Embeddings + RAG + Consumer Export

- Deterministic scales: template-registry.yaml v2.0.0 regex + exact SI constants + authoritative sources for all 8 domains, scales to 1000s PDFs, any domain, no cost
- Evolvable: add new domain without code change via --evolve
- LLM only when PDF missing exact definition: frontier DeepSeek R1/V3 free, Claude 3.5 Sonnet/Opus, GPT-4o/o1, Gemini 2.5 Pro/2.0 Flash free, Llama 3.3 70B free, Qwen, Nemotron via OpenRouter/NVIDIA NIM, selector like DeepSeek harness
- Even LLM requires HITL: human explicitly edits markdown before canonical
- Embeddings — YES needed: For RAG and consumer export, embedding model generates vectors, deterministic same content_hash + model → same embeddings, local free All-MiniLM 384 fast 80MB 5x faster + BGE Large SOTA 1024 1.3GB best for RAG MTEB top + frontier API OpenAI text-embedding-3-large 3072 best quality MTEB 64.6 + NVIDIA nv-embed-v1 SOTA 4096 free via NIM, model selector like DeepSeek harness
- RAG — YES needed: STEMMA is knowledge foundation, RAG is how consumers use it, without RAG static JSON, with RAG queryable knowledge with citations, flow question → embedding → vector search top_k → context definitions + connections + sources → LLM frontier selector → answer with citations, API /v2/rag/search GET + /v2/rag/query POST, webapp RAG playground
- Consumer export — YES needed: file (knowledge.json deterministic content-hash v2.2.0, embeddings.jsonl, vector_store/ FAISS, consumers/<consumer>/knowledge.<consumer>.json filtered), API (adapter v0.2.0 endpoints /v2/entities, /v2/embeddings, /v2/rag/search, /v2/rag/query POST, /v2/export?consumer=..., /openapi.yaml OpenAPI 3.0.3), SDK (Python Stemma.from_file + StemmaRAG), for LearningHub (canonical physics/chem/bio/math, OpenAI embeddings, GPT-4o RAG), PROFESSOR-J (reviewed all 8 domains mediocre, BGE Large offline SOTA, FAISS, DeepSeek R1 free RAG), general, explorer

## Whose Job Is Embedding and RAG? CONSUMER's Job, Not STEMMA's — STEMMA Provides Reference Implementation

STEMMA's job — knowledge foundation pure deterministic HITL versioned content-hash NO embeddings/RAG in canonical: content/<domain>/**/*.md, connections/*.yaml, sources/*.yaml, schema/, scripts/validate.py NEVER checks embeddings, physics_core_profile_check.py, physics_governing_check.py, hitl_check.py, evolvable_template.py, status_truth.py, verify_all.py — provides knowledge foundation + deterministic versioned exports knowledge.json v2.2.0 content-hash + openapi.yaml + SDK for consumers — pure deterministic HITL versioned NO embeddings/RAG in canonical — whole STEMMA is here

CONSUMER's job — build embedding and RAG out of STEMMA as connection layer NOT containing whole STEMMA: LearningHub, PROFESSOR-J, general, explorer, STEMMA-RAG — data/knowledge.json copied from STEMMA exports/knowledge.json, data/embeddings.jsonl generated externally via embed.py out of STEMMA, data/vector_store/ FAISS built externally out of STEMMA, rag.py retrieval + generation logic out of STEMMA, or via API calls to STEMMA API /v2/entities /v2/stats content_hash /v2/search etc., or via SDK Stemma.from_file() — generate vectors DERIVED from STEMMA definitions via embedding model local free All-MiniLM/BGE Large + frontier OpenAI Large/NVIDIA NV-Embed model selector like DeepSeek harness, build vector store FAISS/Chroma/Qdrant/Pinecone, serve RAG queries with retrieval + generation + citations — does NOT contain whole STEMMA, just connection layer, whole STEMMA remains in STEMMA repo

STEMMA provides reference implementation as optional derived + consumer layer for convenience and demo but production embedding/RAG is consumer's job.

## Guideline — How to Build Embedder and RAG That Imports From STEMMA Consistently

See GUIDELINE-EMBEDDER-RAG.md authoritative 81KB guideline for consumers to build consistent embedder + RAG architecture that imports from STEMMA via file/API/SDK + content_hash.
