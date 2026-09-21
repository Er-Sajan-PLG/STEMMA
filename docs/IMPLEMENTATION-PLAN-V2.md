# STEMMA Implementation Plan v2 — Architecture → Plan → Work Integrating Early Work

Status: Authoritative
Date: 2026-09-21
Baseline: b958a5c empty corpus
Architecture: docs/ARCHITECTURE-V2.md

## Order

This plan follows requested order: New Architecture → Implementation Plan → Work integrating early work as implementation.

## Phase 0 — Foundation Prerequisites (Hours)

Goal: Reproducibility, clean namespace, ADR-0044 ratified.

Tasks:
- Declare pyyaml + jsonschema in root requirements.txt (currently inline in .github/workflows/ci.yml, clean clone gate exits 2)
- Archive old ADRs 0001-0039 to archive/old-design/docs/decisions/
- Write docs/decisions/0044-integrated-foundation-v2.md clean constitutional spec (this architecture)
- Update docs/decisions/README.md retitle LearningHubSTEM Foundation to STEMMA Foundation index ADRs 0023-0044
- Fix AGENTS.md dead Quick Start references (retired docs per ADR-0027; stray force-entity doc deleted by PR #41)
- Fix ingest.py candidates conform to source.schema.json, remove hand-written report prose stale counts

Exit: ADR-0044 committed, README indexed, requirements.txt present, AGENTS.md clean, gate green.

Verification: python3 scripts/verify_all.py green, git diff --exit-code -- exports reports

## Phase 1a — Value-Slot on Connection Kind (Days)

Goal: Measurements as first-class evidence-bearing ValueClaims.

Tasks:
- Make target and value mutually exclusive XOR in connection.schema.json
- Extend claim_signature computation in validate.py sha256(source|relation|value_canonical|polarity|sorted(qualifiers))
- Extend check_id_immutability.py to cover value-slot claims
- Unit field interim allowlist QUDT/UCUM/SI symbols m kg s A K mol cd documented anchor strings until ADR-0024 not just "1"

Exit: Schemas updated, validator handles new shapes, tests pass, gate green on empty corpus.

Verification: connection with both target and value → schema error, neither → error, value without evidence at canonical → gate error.

## Phase 1b — Warrant Axis + Correction Labels (Days)

Goal: Surgical assertion.type + warrant taxonomy + correction tracking.

Tasks:
- Extend confidence_basis enum with definitional axiomatic model_based
- Update check_assertion_epistemics to handle extended basis without requiring inference blocks for non-inferred types, keep assertion.type 3 values asserted inferred proposed
- Add optional correction_class enum to review_history[] items factual_error category_error relationship_error provenance_error incompleteness hallucination format_error dangling_ref start used 3 factual_error relationship_error other reserve 8

Exit: Validator handles extended basis, tests pass.

Verification: unknown confidence_basis → error, unknown correction_class → error, assertion.type remains 3-value enum.

## Phase 1c — L7 Refinement Not Purge (Days)

Goal: Distinguish pedagogical vs knowledge.

Tasks:
- Remove learning_objectives instructional_sequencing from concept.schema.json properties entirely
- Allow real_world_applications common_misconceptions ONLY when evidenced as ValueClaim with evidence[] and source not free-form strings
- Extend test_generality.py to reject pedagogical keys but allow evidenced knowledge claims
- Record the archived SOTA review's §6.5 softer alternative as partially adopted via extension-registry.yaml

Exit: Schema updated, test_generality rejects pedagogical keys but allows evidenced claims, gate green.

Verification: learning_objectives key → error, real_world_applications free-form without evidence → error, real_world_applications as ValueClaim with evidence[] → pass.

## Phase 1d — New Relations (Days)

Goal: Formulation equivalence + misconception linking.

Tasks:
- Adopt equivalent_to in registry domain law range law symmetric true transitive true
- Adopt misconception_of domain misconception range enumerated entity types from concept.schema enum NOT "any" symmetric false inverse null transitive false
- Update validator domain/range checks

Exit: Registry updated, validator handles new relations.

Verification: misconception_of with range outside enumerated types → error, missing symmetry declaration → error.

## Phase 1e — Delegated Authority v2 (Days)

Goal: Audited federation.

Tasks:
- Add authority field internal|delegated to reviewed_by[] and review_history[] in connection.schema.json
- Add trusted-institution entry type to agent-registry.yaml with audit_frequency sample_audit_rate last_audit next_audit review_standard_version delegated_provenance block
- Update validator to accept delegated authority for canonical transitions only with registered institution
- Add sample audit check 10% first 100 5% ongoing annual audit
- Add revocation procedure claims transition to unreviewed require re-review consumers notified via changelog
- Update export contract to expose authority field

Exit: Schemas updated, validator handles delegated authority, tests pass.

Verification: authority delegated without registered institution → error, unknown institution → error, institution without review_standard_url/version → error, sample audit rate <5% → warning, revoked/suspended institution claims still canonical → error.

## Phase 2 — Contract Update (Days)

Goal: Export version bump + adapter + explorer.

Tasks:
- export_version 2.2.0→2.2.0 in schema/export.schema.json and schema/VERSION.yaml add authority field and value-slot support to export shape
- Update adapters/python/ to handle value-slot claims and delegated authority
- Update explorer/ to render value-slot claims and authority filter small nodes thin lines manual legend centered zoom 8 domains
- Update docs/CONSUMERS.md with new contract surface

Exit: Export contract bumped, adapter round-trips, explorer renders, gate green.

Verification: export_version matches schema/VERSION.yaml, adapter round-trips value-slot and authority, explorer renders.

## Phase 3 — Governance Hygiene (Hours)

Goal: Clean namespace.

Tasks:
- lhs sweep across all tracked files EXCEPT ADR documents which are history per ADR-0027 §3
- Un-stub tests/repo/test_independence.py and remove ecosystem references from AGENTS.md in same PR
- Close ADR-0027 owner-ratification gate

Exit: No stale references, independence test live, namespace clean.

## Phase 4 — Content as Acceptance Test Before IRI Gate (Hours to Days) — Work Integrating Early Work

Goal: Prove full L8 chain both authority tiers, corpus has real content, engine built, integrating all early work from start as implementation of architecture.

This phase integrates early work done from start as implementation:

Early work from sandbox start to fea770a:
- Reset to beginning 0 new primary PDF ingestion HITL markdown explicit edit
- Fundamentals visible length mass time + derived area volume speed weight agreed definitions with refs clean 3D centering
- Standard scientific definitions 74 entities agreed SI exact then archived to 1 entity metre via HITL
- Clean minimal 3D small balls thin lines no cartoon glow ultra-clean minimal fast load center zoom entity+relations legend manual only
- Evolvable templates frontier model selector DeepSeek harness deterministic scales LLM fallback only when needed
- Comprehensive all-STEM mediocre 8 domains 97 subdomains 12 entity types
- Explicit separation canonical vs derived vs consumer, embedding and RAG as connection layer file/API/SDK content_hash, whose job is embedding and RAG consumer's job not STEMMA's reference implementation, guideline to build embedder and RAG imports consistently sample in derived
- Strong CI + explorer + ingestion pipeline nothing bad gets pushed/merged 10 jobs all-green final gate
- Semantic acquisition pipeline 16 stages evidence first-class char_offsets surrounding_context AI output must be proposal NOT canonical independent verification deterministic 7 checks + Verifier Model B separate + source corroboration conflict explicit P=10 vs P=12 do not force average human review final authority llm-registry 5 roles 13 models

Tasks integrating early work:
- Register one trusted external institution in agent-registry.yaml exercises delegated authority v2 path with audit (early work: agent-registry existed but no delegated authority)
- Seed one source record conforming to source.schema.json SI Brochure 9th ed (early work: sources/src.nist-si-brochure-9th.yaml existed)
- Seed two entities metre with scientific definition exactly as meter example with reference fundamental quantities visible and phys.force with definition and reference conforming to updated concept.schema.json restores AGENTS.md Quick Start references (early work: content/physics/measurement-units/metre.md 1 entity via HITL, standard definitions)
- Seed one relational connection with non-empty evidence[] pointing to source record (early work: 0 connections, now 1+)
- Seed one value-claim connection measurement or misconception prevalence exercising value-slot (early work: no value-slot, now new)
- One human review pass to canonical via scripts/review.py internal authority (early work: HITL enforced)
- One delegated-authority import exercising institution path with sample audit (early work: no delegated authority)
- python3 scripts/verify_all.py + git diff --exit-code -- exports reports

Exit: Full L8 chain proven end-to-end both authority tiers corpus has 3-5 entities 2-3 connections real content engine built.

Verification: verify_all green 1-5 entities 0-3 connections embeddings deterministic content_hash RAG vector search with citations, semantic pipeline evidence first-class conflict demo P=10 vs P=12, explorer clean small nodes thin lines manual legend centered zoom 8 domains, webapp HITL PDF primary model selector DeepSeek harness.

## Phase 5 — Organization/IRI Gate (Roadmap R3) Human decision

Human decision on owning organization domain IRI base everything touching published IRIs waits for this.

## Phase 6 — Projection Publication (Roadmap R4 After Phase 5) Days

exports/knowledge.jsonld + SKOS mapping + context file + SHACL shapes learn-from + signed release bundle + integrity manifest pluggable BFO schema.org

## Phase 7 — Consumer Views and Routing (After Phase 6) Days

exports/views/* generation determinism tests calibration report from real review data review-queue routing R7 heuristic worksheet-ordering not predictive model threshold ≥200 labeled decisions across ≥3 domains.

## Phase 8 — Scale Readiness (Days)

Benchmark git performance at 10^4 entities design content-addressed store with Merkle roots decide via ADR whether to migrate at 10^5 keep sharded YAML+LFS for now document migration plan.

## Cost Model

Phase 0 Hours, Phase 1a-1e Days each total 1-2 weeks, Phase 2 Days, Phase 3 Hours, Phase 4 Hours to Days 3-5 entities, evidence backfill pilot rate TBD after Phase 4 measured, revocation cost re-review 10% sample Hours per 100 claims full revocation Days per 1000, producer infra git+CI+free tiers ≈$0 now $5-20/month at 10^5 with LFS, consumer infra consumer-owned out of scope.

## Verification Plan

Value-slot both target and value → schema error neither → error value without evidence at canonical → gate error L7 refined pedagogical keys rejected unless evidenced warrant unknown confidence_basis → error assertion.type 3-value enum corrections unknown enum → error misconception_of range outside enumerated types → error missing symmetry → error delegated authority without registered institution → error unknown institution → error institution without review_standard_url/version → error sample audit rate <5% → warning revoked/suspended claims still canonical → error cycle enforcement structural hierarchy cycles rejected dependency cycles rejected no exemptions export contract version matches adapter round-trips standing gates verify_all green git diff exports reports embeddings deterministic content_hash no embeddings in canonical embeddings in derived only byte-identical on rerun RAG vector search works with citations deterministic semantic pipeline evidence first-class AI output must be proposal independent verification deterministic+Verifier Model B conflict analysis explicit P=10 vs P=12 do not force average human review final authority 16 stages model roles model-agnostic reproducibility content_hash explorer clean small nodes thin lines manual legend centered zoom 8 domains webapp HITL enforced PDF primary model selector DeepSeek harness.

## What This Is Not

No hosted service publication file contract, no canonical BFO/OWL dependency BFO projection pluggable, no curriculum grade course country product semantics in canonical L7 refined pedagogical belongs consumers knowledge about misconceptions allowed when evidenced, no pedagogy kernel legacy pedagogical fields purged refined, no producer-side model training, no confidence collapse L3 five states stay five plus warrant and correction axes separate, no machine-checked dimensional consistency until ADR-0024 lands interim human review + gate warning rule exists but not enforced, no embeddings in canonical derived only, no RAG in canonical consumer-owned RAG reference implementation provided, no mutable DB as source of truth content-addressed at scale design git-native now sharded YAML+LFS, no separate claims/ directory value-slot on connections, no rule registry enforcement until ADR-0024 lands designed not executed with warning, no cycle exemptions semantic enforcement stands, no unfounded scale projections scope envelope 10^5–10^6 design target measured, no coupling private product ecosystem.
