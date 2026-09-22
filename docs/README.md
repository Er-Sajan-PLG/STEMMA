# STEMMA — Documentation — Architecture v2 Ideal Order

Status: Authoritative
Baseline: b958a5c empty corpus — engine for canonicalization not yet built, now built.
Architecture: docs/ARCHITECTURE-V2.md clean constitutional foundation single part L1-L8 refined
Implementation Plan: docs/IMPLEMENTATION-PLAN-V2.md Phases 0-8 ideal order architecture → plan → work integrating early work
Decisions: docs/decisions/README.md 0040-0053
Roadmap: docs/ROADMAP.md Phases 0-8 ideal order
Specification recovery (pilot): ../spec/BASELINE.md CORE-GATE-EXPORT slice recovered 2026-09-22 per protocol v3.1 — maturity L2 slice-scoped, 22 requirements PROPOSED awaiting owner approval, process review at ../SPECIFICATION_PROCESS_REVIEW.md

Ideal order history: b958a5c empty → 51fc1b0 architecture v2 clean → 493b32b implementation plan v2 → 27576f3 foundation reset fundamentals clean 3D → 3bcfd4a ingestion pipeline evolvable templates model selector → e692b25 comprehensive all-STEM template registry → dbc229f embeddings RAG separation consumer export guideline → 7297c6c strong CI explorer semantic pipeline final → 0df87ff fix status truth.

All early work from start included as implementation of new architecture, not pre-architecture work.

## Reading order (new engineer, deterministic, architecture v2)

1. **[ARCHITECTURE-V2.md](ARCHITECTURE-V2.md)** — authoritative clean single part constitutional foundation L1-L8 refined, data model value-slot XOR, semantic primitives, delegated authority v2 audited, scale 10^2–10^6, 16-stage semantic acquisition pipeline, embedding and RAG producer vs consumer separation, standards alignment pluggable, consumption
2. **[IMPLEMENTATION-PLAN-V2.md](IMPLEMENTATION-PLAN-V2.md)** — Phases 0-8 ideal order architecture → plan → work integrating early work, verification plan, cost model, what-is-not, consequences, human decisions
3. **[decisions/README.md](decisions/README.md)** — ADRs 0040-0053 beginning no legacy, old 0001-0039 archived to archive/old-design/
4. **[VISION.md](VISION.md)** — what STEMMA is, knowledge foundation not curriculum not product, 8 domains mediocre 400-800 target, embeddings RAG consumer export via file/API/SDK content_hash. Note: the SDK ships `Stemma`/`load_export`; `StemmaRAG` is specified but not yet implemented (SPECIFIED_AND_MISSING — see ../spec/SPECIFICATION_GAP_ANALYSIS.md)
5. **[DOMAIN-MODEL.md](DOMAIN-MODEL.md)** — entities, connections, sources with governed_by, 8 domains physics/chemistry/biology/earth-science/astronomy/computer-science/engineering/mathematics, 97 subdomains, 12 entity types
6. **[SCHEMA-SPECIFICATION.md](SCHEMA-SPECIFICATION.md)** — JSON Schemas, relation-registry, template-registry v2.0.0, embedding-registry v1.0.0, consumer-registry v1.0.0, llm-registry v1.0.0, api.yaml OpenAPI 3.0.3
7. **[PIPELINES.md](PIPELINES.md)** — 16 stages DOCUMENT→OBSERVATION→EVIDENCE WINDOWS→CANDIDATE→ENTITY RESOLUTION threshold 0.85→CLAIM→NORMALIZATION→DETERMINISTIC VALIDATION→INDEPENDENT VERIFICATION Verifier Model B→CONFLICT ANALYSIS explicit P=10 vs P=12→PROPOSAL→REVIEW→CANONICAL→DERIVED EXPORT→CONSUMER never PDF→LLM→canonical
8. **[GOVERNANCE.md](GOVERNANCE.md)** — invariants L1-L8, HITL, deterministic, identity immutable, derived ≠ canonical, no curriculum refined boundary, materialization chain constitutional
9. **[CONSUMERS.md](CONSUMERS.md)** — LearningHub canonical physics/chem/bio/math OpenAI Large 3072 GPT-4o top_k5, PROFESSOR-J reviewed all 8 domains mediocre BGE Large 1024 offline DeepSeek R1 free top_k10, general, explorer 3D clean small nodes thin lines manual legend centered zoom
10. **[EMBEDDINGS.md](EMBEDDINGS.md)** — embedding model needed YES, 11 models local free + frontier API, model selector DeepSeek harness, deterministic content_hash versioned vector_store FAISS
11. **[RAG.md](RAG.md)** — RAG system needed YES, retrieval + generation + citations, flow question → embedding → vector search top_k → context → LLM frontier selector → answer with citations, API /v2/rag/search + /v2/rag/query POST, webapp RAG playground
12. **[API.md](API.md)** — export mechanism via api schema link/api YES, OpenAPI 3.0.3 schema/api.yaml, adapter v0.2.0 endpoints /v2/entities /v2/embeddings /v2/rag/search /v2/rag/query POST /v2/export?consumer=... /openapi.yaml file/API/SDK content_hash
13. **[GUIDELINE-EMBEDDER-RAG.md](GUIDELINE-EMBEDDER-RAG.md)** — 81KB guideline how to build embedder and RAG that imports from STEMMA consistently via file/API/SDK + content_hash, sample in derived inside and out of STEMMA, direction and future plans
14. **[SEMANTIC-ACQUISITION-PIPELINE.md](SEMANTIC-ACQUISITION-PIPELINE.md)** — 81KB 19 sections 16 stages evidence first-class model roles document_vision extraction reasoning verification embedding model-agnostic reproducibility vertical slice corpus 6 PDFs SI Brochure HRW Campbell Atkins CLRS Carroll
15. **[IMPLEMENTATION-STATUS.md](IMPLEMENTATION-STATUS.md)** — current counts 1 entity metre via HITL 0 connections 3 sources, checks all green, template registry 8 domains, embedding registry 11 models, consumer registry 4 consumers, API schema, webapp PDF primary + deterministic draft + AI draft frontier + markdown preview + HITL + RAG playground + consumer export, explorer clean
16. **[ROADMAP.md](ROADMAP.md)** — Phases 0-8 ideal order R0 foundation prerequisites, R1a value-slot ADR-0045, R1b warrant axis correction labels ADR-0046, R1c L7 refinement ADR-0047, R1d new relations ADR-0048, R1e delegated authority v2 ADR-0049, R2 contract update 2.2.0 ADR-0050, R3 governance hygiene ADR-0051, R4 content acceptance test before IRI gate ADR-0052 work integrating early work, R5 org/IRI gate ADR-0053 decided 2026-09-22, R6 projection, R7 views routing, R8 scale readiness

## Reference set — architecture v2

| Subject | Document |
|---|---|
| Architecture v2 authoritative clean single part | [ARCHITECTURE-V2.md](ARCHITECTURE-V2.md) |
| Implementation Plan v2 Phases 0-8 ideal order | [IMPLEMENTATION-PLAN-V2.md](IMPLEMENTATION-PLAN-V2.md) |
| Decisions beginning no legacy 0040-0053 | [decisions/README.md](decisions/README.md) |
| Vision | [VISION.md](VISION.md) |
| Domain model | [DOMAIN-MODEL.md](DOMAIN-MODEL.md) |
| Schema contracts | [SCHEMA-SPECIFICATION.md](SCHEMA-SPECIFICATION.md) |
| Metadata | [METADATA-SPECIFICATION.md](METADATA-SPECIFICATION.md) |
| Relationships | [RELATIONSHIP-SPECIFICATION.md](RELATIONSHIP-SPECIFICATION.md) |
| Pipelines 16 stages | [PIPELINES.md](PIPELINES.md) |
| Implementation status | [IMPLEMENTATION-STATUS.md](IMPLEMENTATION-STATUS.md) |
| Roadmap Phases 0-8 ideal order | [ROADMAP.md](ROADMAP.md) |
| Testing | [TESTING.md](TESTING.md) |
| Standards | [STANDARDS.md](STANDARDS.md) |
| Governance L1-L8 | [GOVERNANCE.md](GOVERNANCE.md) |
| Consumers LearningHub PROFESSOR-J | [CONSUMERS.md](CONSUMERS.md) |
| Guideline Embedder + RAG 81KB | [GUIDELINE-EMBEDDER-RAG.md](GUIDELINE-EMBEDDER-RAG.md) |
| Embeddings YES needed 11 models | [EMBEDDINGS.md](EMBEDDINGS.md) |
| RAG YES needed retrieval+generation+citations | [RAG.md](RAG.md) |
| API export mechanism YES file/API/SDK content_hash | [API.md](API.md) |
| Semantic Acquisition Pipeline 16 stages evidence first-class | [SEMANTIC-ACQUISITION-PIPELINE.md](SEMANTIC-ACQUISITION-PIPELINE.md) |
| Specification recovery program (pilot charter, roles/authority, domain registry) | [../spec/PILOT_CHARTER.md](../spec/PILOT_CHARTER.md) |
| Recovered specification baseline (L2, 22 PROPOSED requirements, 2 interfaces, validator) | [../spec/BASELINE.md](../spec/BASELINE.md) |
| Recovery process review (mandatory, root) | [../SPECIFICATION_PROCESS_REVIEW.md](../SPECIFICATION_PROCESS_REVIEW.md) |
| Documentation sync & enforcement system (contract, impact, census) | [DOCUMENTATION-SYSTEM.md](DOCUMENTATION-SYSTEM.md) |
| Ingestion Primary PDF primary HITL | [INGESTION-PRIMARY.md](INGESTION-PRIMARY.md) |
| Agent deterministic protocol HITL | [AGENT.md](AGENT.md) |
| Reset and HITL Guide beginning clean | [RESET-AND-HITL-GUIDE.md](RESET-AND-HITL-GUIDE.md) |
| Versioning | [VERSIONING.md](VERSIONING.md) |
| Migrations | [MIGRATIONS.md](MIGRATIONS.md) |
| Curation protocol | [CURATION-PROTOCOL.md](CURATION-PROTOCOL.md) |

## Supplementary docs

| Subject | Document |
|---|---|
| Deprecated architecture pointer | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Physics governing laws | [PHYSICS-GOVERNING-LAWS.md](PHYSICS-GOVERNING-LAWS.md) |
| Physics minimal design v2 | [PHYSICS-MINIMAL-DESIGN-V2.md](PHYSICS-MINIMAL-DESIGN-V2.md) |
| Security/integrity/provenance | [SECURITY-INTEGRITY-PROVENANCE.md](SECURITY-INTEGRITY-PROVENANCE.md) |
| Ingestion & review webapp | [WEBAPP.md](WEBAPP.md) |
| Contributing | [CONTRIBUTING.md](CONTRIBUTING.md) |
| Glossary | [GLOSSARY.md](GLOSSARY.md) |

Old-design v1.0 acquisition docs (KNOWLEDGE-ACQUISITION, CANONICAL-ADMISSION,
EVIDENCE-MODEL, PROVENANCE, SOURCE-POLICY, INGESTION, SOURCES, SOTA-REVIEW,
DEEP-DIVE-RECOMMENDATIONS, AUDIT-INGESTION-BASELINE, ACQUISITION-OPERATIONS,
STEMMA-CONSUMER-SEAM) were retired 2026-09-22 — byte-identical copies live in
`archive/old-design/docs/`. Current equivalents: PIPELINES.md +
SEMANTIC-ACQUISITION-PIPELINE.md (acquisition), METADATA-SPECIFICATION.md
(provenance semantics), connection.schema.json (evidence).

## Ground rule — architecture v2 ideal order

**Architecture v2 ideal order:** b958a5c empty → 51fc1b0 architecture v2 clean constitutional foundation single part L1-L8 refined → 493b32b implementation plan v2 Phases 0-8 → 27576f3 foundation reset fundamentals standard SI definitions clean 3D viewer integrating early work → 3bcfd4a ingestion pipeline evolvable templates model selector integrating early work → e692b25 comprehensive all-STEM template registry integrating early work → dbc229f embeddings RAG separation consumer export guideline integrating early work → 7297c6c strong CI explorer semantic pipeline final integrating early work → 0df87ff fix status truth.

**All early work from start included as implementation of new architecture, not pre-architecture work.** Early work mapping:
- Reset to beginning 0 → L5 identity immutable + L8 16 stages Phase 0
- Fundamentals visible length mass time + derived + standard SI definitions exactly as meter example with reference The meter (symbol: m) is base unit of length in SI scientifically defined as length of path travelled by light in vacuum during 1/299,792,458 second with reference → L1 claim sole bearer truth definitions are claims warrant definitional Part 3.6 entity schema fundamental quantities visible
- Clean minimal 3D small nodes thin lines manual legend centered zoom → Part 9.3 explorer consumer views
- PDF primary HITL markdown explicit edit both primary+secondary → L2 human-only + L8 intake chain
- Evolvable templates deterministic scales LLM fallback → L4 deterministic template-registry v2.0.0 8 domains
- Comprehensive all-STEM mediocre 8 domains 97 subdomains 12 entity types → Scale architecture 10^2–10^6 consumer-registry
- Explicit separation canonical vs derived vs consumer embeddings RAG consumer's job reference implementation guideline 81KB sample in derived → L6 derived ≠ canonical Part 5 producer vs consumer separation export mechanism LearningHub PROFESSOR-J via API
- Strong CI nothing bad gets pushed 10 jobs all-green final gate → Verification Plan standing gates verify_all green git diff exports reports
- Semantic acquisition pipeline evidence first-class char_offsets surrounding_context AI output must be proposal NOT canonical independent verification conflict explicit P=10 vs P=12 → L1-L3 Part 2 primitives Part 3 data model Part 8 AI curation

**Constitutional Laws L1-L8 refined:**
- L1 Claim sole bearer truth definitions are claims warrant definitional
- L2 Human-only + delegated authority v2 audited federation audit_frequency sample_audit_rate 10%/5% versioning revocation
- L3 Five states never collapsed model_confidence source_support validation_status review_status epistemic_status + warrant confidence_basis definitional axiomatic model_based + correction correction_class
- L4 Deterministic science stays deterministic LLM extractor not authority embeddings NOT replacement
- L5 Identity immutable content_hash
- L6 Derived ≠ canonical embeddings NOT in canonical only derived content_hash versioned RAG consumer-owned reference implementation
- L7 No curriculum semantics refined boundary pedagogical about teaching vs knowledge about world including human beliefs misconception prevalence ValueClaim about misconception entity with evidence allowed
- L8 Materialization chain 16 stages DOCUMENT→OBSERVATION→EVIDENCE WINDOWS→CANDIDATE→ENTITY RESOLUTION threshold 0.85→CLAIM→NORMALIZATION→DETERMINISTIC VALIDATION→INDEPENDENT VERIFICATION Verifier Model B→CONFLICT ANALYSIS explicit P=10 vs P=12→PROPOSAL→REVIEW→CANONICAL→DERIVED EXPORT→CONSUMER never PDF→LLM→canonical

**Data Model New Architecture v2:**
- Canonical Object Kinds content/connections/sources no separate claims/ directory value-slot XOR target/value interim allowlist QUDT/UCUM/SI claim_signature sha256 semantic-claim schema candidate not canonical relation registry 55 relations 13 families 12 adopted 43 reserved cycle scoping no exemptions new adoptions equivalent_to misconception_of assertion type surgical warrant axis confidence_basis definitional axiomatic model_based entity schema scientific definition exactly as meter example fundamental quantities visible correction labels governing laws dual-role 4 surfaces Referent Knowledge Hub Constraint Derivation Engine linkage applies_to_entity interim warning rule exists but not enforced until ADR-0024
- Delegated Authority v2 provenance extension authority field internal|delegated delegated_provenance block institution_id review_standard_url review_standard_version audit_date sample_audit_rate institution registration ADR audit_frequency sample_audit_rate last_audit next_audit status active|revoked|suspended audit and sample 10% first 100 5% ongoing annual audit translation layer unit translation interim allowlist conflict detection P=10 vs P=12 import semantics external verified claims enter canonical with authority delegated L4 gates still run original IDs external_ids anchors evidence chains source_ref pointers revocation transitions to unreviewed consumer surface export contract exposes authority field trust thresholds trust score audit recency sample pass rate
- Embedding and RAG producer vs consumer separation deterministic derived embeddings reference implementation export mechanism LearningHub PROFESSOR-J via OpenAPI file/API/SDK content_hash invalidation
- Standards alignment projection only pluggable BFO-2020 schema.org SKOS QUDT/UCUM Wikidata JSON-LD SHACL PROV-O Wikidata anchors
- Scale architecture 10^2–10^6 sharded YAML+LFS now content-addressed design later instance data exclusion consumer retrieval
- AI-accelerated curation 16 stages calibration report review-queue routing no producer-side training
- Consumption contract deterministic export content-hash consumer views prerequisites misconceptions formulations centrality changelog explorer clean 3D

**Verification:** make quick-verify PASS — 1 entity metre via HITL, 0 connections, 3 sources, embeddings deterministic content_hash sha256:2c007fc6..., RAG vector search metre 0.2874 citations, semantic pipeline evidence first-class conflict demo P=10 vs P=12, explorer clean small nodes thin lines manual legend centered zoom 8 domains, webapp HITL PDF primary model selector DeepSeek harness, strong CI 10 jobs all-green.

## New docs for architecture v2

- **ARCHITECTURE-V2.md** — authoritative clean single part constitutional foundation L1-L8 refined, data model value-slot XOR, semantic primitives, delegated authority v2 audited, scale 10^2–10^6, 16-stage semantic acquisition pipeline, embedding and RAG producer vs consumer separation, standards alignment pluggable, consumption
- **IMPLEMENTATION-PLAN-V2.md** — Phases 0-8 ideal order architecture → plan → work integrating early work, verification plan, cost model, what-is-not, consequences, human decisions
- **decisions/0044-integrated-foundation-v2.md** — clean constitutional spec L1-L8 refined
- **decisions/0045-value-slot.md** — value-slot XOR target/value interim allowlist QUDT/UCUM/SI
- **decisions/0046-warrant-axis-correction-labels.md** — warrant axis definitional axiomatic model_based + correction_class
- **decisions/0047-l7-refinement.md** — L7 refined not blanket purge allow evidenced real_world_applications common_misconceptions as ValueClaims
- **decisions/0048-new-relations.md** — equivalent_to misconception_of
- **decisions/0049-delegated-authority-v2.md** — delegated authority v2 audited federation audit_frequency sample_audit_rate 10%/5% versioning revocation
- **decisions/0050-contract-update-2.2.0.md** — contract 2.2.0 value-slot + delegated authority export_version 2.2.0→2.2.0
- **decisions/0051-governance-hygiene.md** — lhs sweep fix AGENTS.md dead refs un-stub test_independence
- **decisions/0052-content-acceptance-test.md** — content as acceptance test before IRI gate 3-5 entities 2-3 connections both authority tiers work integrating early work
- **ROADMAP.md** — Phases 0-8 ideal order R0 foundation prerequisites, R1a value-slot ADR-0045, R1b warrant axis correction labels ADR-0046, R1c L7 refinement ADR-0047, R1d new relations ADR-0048, R1e delegated authority v2 ADR-0049, R2 contract update 2.2.0 ADR-0050, R3 governance hygiene ADR-0051, R4 content acceptance test before IRI gate ADR-0052 work integrating early work, R5 org/IRI gate ADR-0053 decided 2026-09-22, R6 projection, R7 views routing, R8 scale readiness
- **IMPLEMENTATION-STATUS.md** — architecture v2 ideal order current counts 1 entity metre via HITL 0 connections 3 sources checks all green template registry 8 domains embedding registry 11 models consumer registry 4 consumers API schema webapp PDF primary + deterministic draft + AI draft frontier + markdown preview + HITL + RAG playground + consumer export explorer clean
- **GUIDELINE-EMBEDDER-RAG.md** — 81KB guideline how to build embedder and RAG that imports from STEMMA consistently via file/API/SDK + content_hash sample in derived inside and out of STEMMA direction and future plans
- **SEMANTIC-ACQUISITION-PIPELINE.md** — 81KB 19 sections 16 stages evidence first-class model roles document_vision extraction reasoning verification embedding model-agnostic reproducibility vertical slice corpus 6 PDFs SI Brochure HRW Campbell Atkins CLRS Carroll
- **INGESTION-PRIMARY.md** — PDF primary ingestion with HITL markdown explicit edit
- **AGENT.md** — deterministic protocol HITL + PDF primary + evolvable templates v2.0.0 + model selector like DeepSeek harness + embeddings + RAG + consumer export
- **RESET-AND-HITL-GUIDE.md** — beginning clean PDF primary human is you
- **EMBEDDINGS.md** — YES embedding model needed 11 models local free + frontier API model selector DeepSeek harness deterministic content_hash vector_store FAISS
- **RAG.md** — YES RAG system needed retrieval + generation + citations flow question → embedding → vector search top_k → context → LLM frontier selector → answer with citations API /v2/rag/search + /v2/rag/query POST webapp RAG playground
- **API.md** — YES export mechanism via api schema link/api needed OpenAPI 3.0.3 schema/api.yaml adapter v0.2.0 endpoints /v2/entities /v2/embeddings /v2/rag/search /v2/rag/query POST /v2/export?consumer=... /openapi.yaml file/API/SDK content_hash

All docs updated to architecture v2 ideal order with new ADRs roadmaps etc.
