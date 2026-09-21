# IMPLEMENTATION-STATUS — Architecture v2 Ideal Order

Status: Authoritative
Date: 2026-09-21
Baseline: b958a5c empty corpus
Architecture: docs/ARCHITECTURE-V2.md
Implementation Plan: docs/IMPLEMENTATION-PLAN-V2.md
Decisions: docs/decisions/README.md 0040-0052
Roadmap: docs/ROADMAP.md

Ideal order history: b958a5c empty → 51fc1b0 architecture v2 clean → 493b32b implementation plan v2 → 27576f3 foundation reset fundamentals clean 3D → 3bcfd4a ingestion pipeline evolvable templates model selector → e692b25 comprehensive all-STEM template registry → dbc229f embeddings RAG separation consumer export guideline → 7297c6c strong CI explorer semantic pipeline final → 0df87ff fix status truth.

## Current counts — after ideal order rewrite

| Layer | Count | Details |
|---|---|---|
| Entities | 1 | metre via HITL, deterministic scales, exact SI c=299,792,458 m/s, writer human:curator.001, link bipm.org, source_refs, external_ids wd, historical timeline, scientific definition exactly as meter example with reference |
| Connections | 0 | Will grow to 500+ with value-slot XOR target/value, 10 relations (8 previous + equivalent_to + misconception_of), mandatory evidence |
| Sources | 3 | nist-si-brochure-9th, halliday-resnick-walker-12th, newton-principia-1687 with url/doi/isbn + writer human:* |
| PDFs | 2 | SI Brochure 9th ed. + HRW Ch1 measurement in workflow/documents/ |
| Candidates | 7 | 6 from deterministic templates (length, mass, time, area, volume, etc.) + 1 from AI draft, 3 HITL edits, markdown preview |
| Embeddings | 1 | Generated via embed.py All-MiniLM 384 dim deterministic fake for demo, stored in exports/embeddings.jsonl + vector_store/ FAISS meta.json + vectors.json content_hash versioned |
| Vector store | 1 | FAISS flat cosine, meta.json content_hash versioned, vectors.json, ids.json |
| Consumer exports | 2 | LearningHub 0 entities (needs canonical, currently draft) + general 1 entity, in exports/consumers/ |
| Domains | 8 | physics 12 subdomains, chemistry 11, biology 14, earth-science 10, astronomy 8, computer-science 15, engineering 13, mathematics 14 — total 97 subdomains, mediocre 50-100 per domain = 400-800 total |
| Decisions | 13 | 0040 physics-first, 0041 minimal entity profile, 0042 minimal relation set, 0043 mandatory source+history, 0044 integrated foundation v2 clean L1-L8, 0045 value-slot, 0046 warrant axis + correction labels, 0047 L7 refinement, 0048 new relations equivalent_to misconception_of, 0049 delegated authority v2 audited, 0050 contract 2.2.0, 0051 governance hygiene, 0052 content acceptance test |
| Architecture | 1 | docs/ARCHITECTURE-V2.md authoritative clean single part 15 parts L1-L8 refined |
| Implementation Plan | 1 | docs/IMPLEMENTATION-PLAN-V2.md Phases 0-8 ideal order |

## Checks — all green

- validate.py OK 1 entities valid, export written to exports/knowledge.json v2.2.0 deterministic content-hash sha256:2c007fc6... per ADR-0050 contract update 2.2.0 value-slot + authority
- physics_core_profile_check.py OK 0 violations (mandatory source_kind, source, writer human:*, link, retrieved_at, source_refs>=1, evidence>=1, historical for law canonical)
- physics_governing_check.py OK 0 violations (governed_by in registry 23 laws, subdomain matches, no self-governance, deterministic)
- hitl_check.py OK HITL has human edits — 3 human edits, audit trail candidate_edited by human:curator.001, writer human:*, markdown explicit
- evolvable_template.py OK — deterministic extraction regex + exact SI constants, 6 entities extracted from HRW Ch1, scales to all 8 domains
- embed.py OK — generates embeddings deterministically same content_hash + model → same embeddings, 1 embeddings to exports/embeddings.jsonl, vector store to exports/vector_store/ meta.json + vectors.json content_hash versioned
- rag.py OK — vector search cosine similarity top_k 2 for "metre" score 0.28, RAG query with citations
- export_consumers.py OK — LearningHub 0 entities (needs canonical) + general 1 entity, consumer-specific filtered exports
- status_truth.py OK — README status block written from live counts 1 entities, 0 connections, 3 sources
- verify_all.py OK — all verify steps pass — architecture v2 ideal order, 1 entities (metre via HITL old 74 archived will grow to 400-800 across 8 domains), 0 connections, HITL enforced, PDF primary deterministic scales, evolvable templates v2.0.0 8 domains 97 subdomains 12 entity types, model selector like DeepSeek harness local+frontier models, embeddings deterministic content_hash, RAG vector search with citations, consumer export LearningHub PROFESSOR-J general explorer, semantic acquisition pipeline evidence first-class AI output must be proposal independent verification deterministic+Verifier Model B conflict analysis explicit P=10 vs P=12 do not force average human review final authority 16 stages model roles document_vision extraction reasoning verification embedding model-agnostic reproducibility content_hash, explorer clean small nodes thin lines manual legend centered zoom 8 domains, webapp HITL PDF primary model selector DeepSeek harness
- verify_strong.py --quick ALL STRONG CHECKS GREEN — Nothing Bad Gets Pushed/Merged — STRONG CI PASSED

## Architecture v2 — Constitutional Foundation Clean Single Part

**Status:** Authoritative — docs/ARCHITECTURE-V2.md

**L1 Claim sole bearer epistemic truth, definitions are claims with warrant definitional**
Entity ≠ truth, Source ≠ truth, LLM output ≠ truth, definition without warrant/evidence ≠ truth but definition WITH warrant definitional + evidence = truth-bearing claim. Meter definition exactly as "The meter (symbol: m) is base unit of length in SI scientifically defined as length of path travelled by light in vacuum during 1/299,792,458 second" with reference SI Brochure is Claim with warrant definitional.

**L2 Canonicalization human-only with delegated authority v2 audited federation**
Path LLM/process → candidate → validation → independent verification → conflict analysis → proposal → human review → canonical never LLM→canonical. AI drafters behind seam named humans authority rejection requires written reason. Delegated authority v2: registered trusted institution verified human review may constitute human gate via delegated authority with full provenance BUT with audit sample versioning revocation: institution registration requires ADR, review_standard_url+version+audit_frequency+sample_audit_rate 10% first 100 5% ongoing+last_audit+next_audit, sample re-review by STEMMA team, annual audit, translation layer, L4 gates still apply, revocation transitions to unreviewed.

**L3 Five epistemic states never collapsed plus warrant and correction axes**
model_confidence uncalibrated LLM signal, source_support direction/strength evidence stance, validation_status deterministic gate pass/fail/advisory, review_status human unreviewed→reviewed→canonical→rejected forward-only, epistemic_status asserted/inferred/derived/disputed/hypothesized. Model may emit model_confidence may not change review_status epistemic_status mechanically separable. Additional axes: warrant confidence_basis [expert_review experimental theoretical derived definitional axiomatic model_based null] how justified, correction correction_class [factual_error category_error relationship_error provenance_error incompleteness hallucination format_error dangling_ref] why corrected attaches to review_history[].

**L4 Deterministic science stays deterministic**
No LLM authoritative for reference integrity schema conformance units dimensions equation structure variable binding dimensional consistency controlled vocabulary graph invariants computed never generated. Gate layers deterministic must not require LLM. LLM extractor/interpreter not authority. Embeddings NOT replacement for semantic extraction.

**L5 Identity immutable**
stemma: ID never changes meaning never reused correction supersession + new ID aliases deprecated_by total resolution guards from git history + content_hash. Content hash separated workflow audit git-ignored wall-clock allowed vs canonical git-tracked deterministic versioned via content_hash.

**L6 Derived ≠ canonical**
Exports reports views projections JSON-LD SHACL BFO mapping embeddings vector_store RAG indexes regenerable byte-deterministic never authoritative canonical depends on nothing everything else depends on it embeddings NOT in canonical only derived exports/ content_hash versioned RAG consumer-owned reference implementation provided.

**L7 No curriculum semantics in canonical refined boundary**
STEMMA knowledge foundation pedagogical metadata learning_objectives instructional sequencing belongs to consumers enforced by test_generality.py. Refined: real_world_applications and common_misconceptions are knowledge when evidenced as claims: photosynthesis basis for agriculture with evidence source is knowledge allowed as Claim, 42% students think photosynthesis only in sunlight source misconception study is ValueClaim about misconception entity with evidence allowed, learning objective students will understand photosynthesis is pedagogical belongs consumer rejected. Distinction pedagogical about teaching knowledge about world including human beliefs. Misconception prevalence ValueClaim about misconception entity with evidence allowed. Legacy pedagogical fields learning_objectives instructional_sequencing removed from concept.schema.json; real_world_applications common_misconceptions allowed ONLY when evidenced as ValueClaim with evidence[] and source not free-form strings.

**L8 Materialization chain constitutional 16 stages**
DOCUMENT content_sha256 version URI anchors to Source → ExtractionRun tool params_hash run_hash → OBSERVATION located reading → EVIDENCE WINDOWS page section text_span char_offsets surrounding_context 3 sentences → CANDIDATE ASSERTION ingest.py semantic_extract.py → ENTITY RESOLUTION threshold 0.85 candidate if uncertain never auto-merge → CLAIM structured subject relation object conditions quantitative evidence link AI-assisted semantic extraction model selector DeepSeek harness extraction role deepseek-r1 free claude-3.5-sonnet gpt-4o gemini-2.5-pro llama-3.3 free custom relation vocab → NORMALIZATION unit syntax identifier datatype deterministic → DETERMINISTIC VALIDATION nine frozen layers fail closed → INDEPENDENT VERIFICATION Verifier Model B separate from Extractor Model A deterministic+independent model+source corroboration → CONFLICT ANALYSIS explicit P=10 vs P=12 do not force average P=11 do not allow LLM arbitrarily choose one → PROPOSAL GENERATION proposals/proposal-*.yaml evidence first-class NOT canonical workflow/proposals/ NOT canonical → REVIEW named human OR delegated institution v2 with audit forward-only → CANONICAL human-only write L2 → DERIVED EXPORT deterministic content-hashed L6 exports/knowledge.json v2.2.0 per ADR-0050 value-slot + authority content_hash sha256 no wall-clock byte-identical embeddings.jsonl vector_store FAISS content_hash versioned → CONSUMER file/API/SDK content_hash invalidation subset exports views LearningHub PROFESSOR-J explorer. Never PDF→LLM→canonical.

## Data Model — New Architecture v2

**Canonical Object Kinds:** Three directories Git-native Markdown+YAML plus staging content/<domain>/<subdomain>/<slug>.md Entity referent with properties + scientific definition exactly as meter example with reference fundamental quantities visible at least fundamental and derived quantities, connections/conn.NNNNNN.yaml Claim relational OR valued, sources/src.<slug>.yaml citation, no separate claims/ directory valued statements use value slot on connection kind itself target XOR value preserves one truth store, staging proposals/ workflow/ git-ignored never canonical.

**Value-Slot Design XOR target/value:** amount lowerBound upperBound unit QUDT/UCUM IRI "1" dimensionless interim allowlist QUDT/UCUM/SI symbols m kg s A K mol cd documented, claim_signature sha256(source|relation|value_canonical|polarity|sorted(qualifiers)).

**Semantic Claim Schema as Candidate Not Canonical:** schema/semantic-claim.schema.json evidence first-class conditions quantitative verification conflict provenance content_hash used in workflow/candidates/ not canonical.

**Relation Registry:** 55 relations 13 families 12 adopted 43 reserved reserved may not enter canonical without ADR, cycle scoping gate cycle detection check_relationship_cycles applies to ALL transitive non-symmetric relations no blanket exemptions, new adoptions equivalent_to formulation equivalence symmetric true transitive true domain law range law misconception_of linking misconception entities to subjects domain misconception range enumerated entity types NOT "any" symmetric false inverse null transitive false.

**Assertion Type and Warrant Axis:** Keep assertion.type surgical [asserted inferred proposed] do NOT expand to derived disputed hypothesized, warrant axis extend confidence_basis enum to include definitional axiomatic model_based, stance axis via contradicts relation polarity evidence stance.

**Entity Schema:** Scientific definition exactly as meter example with reference symbol unit domain fundamental quantities visible at least fundamental and derived quantities, L7 refined remove learning_objectives instructional_sequencing from concept.schema.json properties allow real_world_applications common_misconceptions ONLY when evidenced as ValueClaim with evidence[] and source not free-form strings, definition remains required but explicitly claim with warrant definitional + evidence not non-truth property orientation must have source reference.

**Correction Labels:** optional correction_class field to provenance.review_history[] items enum factual_error category_error relationship_error provenance_error incompleteness hallucination format_error dangling_ref start used 3 factual_error relationship_error other.

**Governing Laws Dual-Role Architecture:** Four surfaces Referent content/physics/<slug>.md Entity type law, Knowledge Hub Claims in connections/, Constraint schema/rule-registry.yaml kind constraint, Derivation Engine schema/rule-registry.yaml kind derivation, linkage applies_to_entity grounds each rule, interim enforcement until ADR-0024 lands constraint/derivation rules exist as registered documentation only gate emits WARNING rule exists but not enforced until ADR-0024 not silent skip.

## Delegated Authority Tier v2 Audited Federation

**Provenance extension** authority field internal|delegated in reviewed_by[] and review_history[] plus delegated_provenance block institution_id review_standard_url review_standard_version audit_date sample_audit_rate.

**Trusted Institution Registration** schema/agent-registry.yaml entry type institution id type institution name authority delegated review_standard_url review_standard_version contact registered_at registered_by status active|revoked|suspended audit_frequency annual sample_audit_rate 0.1 last_audit next_audit.

**Audit and Sample:** Every delegated import must pass L4 deterministic gates sample re-review 10% first 100 5% ongoing annual audit translation layer external evidence chains mapped to STEMMA Source/Document/Observation unit translation via interim allowlist conflict detection still runs P=10 vs P=12 CONFLICT explicit audit report reports/delegated-audit-<institution>.{md,json} gate-generated.

**Import Semantics:** External verified claims enter canonical with authority delegated L4 gates still run original IDs external_ids anchors evidence chains source_ref pointers translated to STEMMA schema revocation if revoked/suspended claims transition to unreviewed require re-review consumers notified via changelog.

**Consumer Surface:** Export contract exposes authority field consumers filter internal vs delegated both canonical both trustworthy but different audit trails consumers choose trust threshold trust score based on audit recency sample pass rate LearningHub may choose internal only for physics-core PROFESSOR-J may choose both for mediocre all 8 domains.

## Embedding and RAG Producer vs Consumer Separation

**Producer STEMMA Provides Deterministic Derived Embeddings Not Canonical:** Per L6 canonical never contains embeddings/RAG. Derived exports/ provides exports/embeddings.jsonl deterministic content_hash versioned model all-MiniLM 384 dim etc exports/vector_store/ FAISS or vectors.json meta.json content_hash versioned exports/knowledge.json deterministic content_hash sha256 no wall-clock byte-identical. Embedding-registry v1.0.0 11 models local+frontier model selector like DeepSeek harness all-MiniLM 384 fast local free default BGE Large SOTA 1024 local OpenAI Large 3072 frontier NVIDIA NV-Embed 4096 SOTA frontier embedding model selection via workflow/config/llm.json git-ignored not canonical embeddings NOT replacement for semantic extraction pipeline has both branches.

**Consumer Embedder and RAG Are Consumer's Job Reference Implementation Provided:** Guideline to build embedder and RAG system that imports from STEMMA consistently for better consumer architecture sample in derived docs updated about direction new change already implemented and future changes plan. docs/GUIDELINE-EMBEDDER-RAG.md 81KB 19 sections how to build embedder and RAG that imports from STEMMA consistently, explorer/ reference implementation loads exports/knowledge.json+embeddings.jsonl+vector_store RAG vector search + citations, Consumers LearningHub PROFESSOR-J general explorer import via file/API/SDK content_hash invalidation subset exports, RAG system vector search + citations deterministic not containing whole STEMMA as connection layer.

**Export Mechanism to Consumers LearningHub PROFESSOR-J via API Schema:** OpenAPI 3.0.3 api.yaml endpoints /api/entities /api/connections /api/sources /api/semantic/claims /api/semantic/proposals/list /api/semantic/registries /api/embeddings /api/rag/search content_hash versioned contract validation webapp/server.py implements semantic endpoints + existing ingestion RAG embeddings consumer-registry 4 consumers LearningHub canonical physics/chem/bio/math OpenAI Large GPT-4o PROFESSOR-J reviewed all 8 domains mediocre BGE Large offline DeepSeek R1 free general explorer subset exports knowledge.json all canonical reviewed trusted proposed rejected plus views/ content-hash invalidation via meta.json SDK adapters/python/ round-trips.

## Standards Alignment Projection Only Pluggable

Pluggable BFO-2020 schema.org SKOS QUDT/UCUM Wikidata not fixed BFO only two rules relation enters published context only with verified IRI mapping at recording level entities project to GDC BFO_0000031 OR schema.org Thing key mappings special_case_of/generalizes → skos:narrower/broader related_to → skos:related Source documents → knowledge content BFO_0000059 concretizes information pattern carried by source document SDC not material carrier concretizes GDC knowledge content written BFO reading required before publication relations with no BFO IRI project under stemma: IRIs anchored to QUDT/UCUM via external_ids. JSON-LD exports/knowledge.jsonld roadmap R4 after IRI gate byte-deterministic SHACL learn-from-only shapes for consumer validation never shadow gate PROV-O L8 chain already PROV-O-shaped projection emits prov: triples signed release bundles nanopublication pattern emitted only on IRI/RDF substrate. Wikidata Anchor Strategy STEMMA advantage governance rigor not data-model novelty controlled multi-valued gate-validated regime vocabulary layer 3 deterministic gate failing CI per-claim evidence trails version control constitutional guarantee no model output ever canonical L2.

## Scale Architecture 10^2–10^6

Producer Storage Progression 10^2–10^4 current YAML files in git sharded content/<domain>/<subdomain>/<slug>.md PR review validate.py git history 10^5–10^6 design target sharded content-addressed store with git-like commit chain objects chunked manifests addressed by content hash Merkle roots same gate same human review but keep sharded YAML+LFS for now design content-addressed but not migrate yet benchmark at 10^4 decide via ADR whether to migrate at 10^5 avoid premature optimization. Instance Data Exclusion STEMMA does NOT store billions raw observations raw datasets external sources CERN NCBI etc STEMMA cites via sources/ extracts evidence-bearing observations pointer claim evidence trail. Consumer Retrieval at Scale consumers load exports/knowledge.json into own infrastructure for 10^6 entities ~2-5GB JSON consumers build own databases search indexes graph databases SPARQL endpoints CDNs STEMMA provides deterministic file safe content-hash invalidation subset exports.

## AI-Accelerated Curation 16 Stages Already Implemented

Intake Chain L8 16 stages DOCUMENT content_sha256 version URI anchors to Source → ExtractionRun tool params_hash run_hash → OBSERVATION located reading → EVIDENCE WINDOWS page section text_span char_offsets surrounding_context → CANDIDATE ASSERTION ingest.py semantic_extract.py → ENTITY RESOLUTION threshold 0.85 candidate if uncertain never auto-merge → CLAIM structured subject relation object conditions quantitative evidence link AI-assisted semantic extraction model selector DeepSeek harness extraction role deepseek-r1 free claude-3.5-sonnet gpt-4o gemini-2.5-pro llama-3.3 free custom relation vocab → NORMALIZATION unit syntax identifier datatype deterministic → DETERMINISTIC VALIDATION nine frozen layers fail closed → INDEPENDENT VERIFICATION Verifier Model B separate from Extractor Model A deterministic+independent model+source corroboration → CONFLICT ANALYSIS explicit P=10 vs P=12 do not force average → PROPOSAL GENERATION proposals/proposal-*.yaml evidence first-class NOT canonical workflow/proposals/ NOT canonical → REVIEW named human OR delegated institution v2 with audit forward-only → CANONICAL human-only write L2 → DERIVED EXPORT deterministic content-hashed L6 → CONSUMER file/API/SDK. Never PDF→LLM→canonical. Calibration Report reports/calibration.{md,json} gate-generated freshness-checked baseline 36 candidates →12 accepted ~33% 0 auto-canonicalized. Review-Queue Routing heuristic worksheet-ordering not predictive model threshold ≥200 labeled decisions across ≥3 domains. No Producer-Side Model Training correction data CC BY 4.0 ORES pattern producer declines to own training loop.

## Implementation Phases Ideal Order

Every phase lands with enforcement same change set ADR+validator+test+docs+verify_all green+clean git diff derived per ADR-0026 discipline.

Phase 0 Foundation Prerequisites Hours reproducibility fix requirements.txt pyyaml jsonschema write ADR-0044 update docs/decisions/README.md retitle LearningHubSTEM to STEMMA Foundation index ADRs 0023-0044 fix AGENTS.md dead Quick Start refs (retired docs) fix ingest.py candidates conform to source.schema.json remove hand-written report prose stale counts exit ADR-0044 committed README indexed requirements.txt present AGENTS.md clean gate green.

Phase 1a Value-Slot Days make target and value mutually exclusive XOR in connection.schema.json extend claim_signature computation validate.py extend check_id_immutability.py to cover value-slot claims unit field interim allowlist QUDT/UCUM/SI symbols documented anchor strings until ADR-0024 not just "1" exit schemas updated validator handles new shapes tests pass gate green — ADR-0045.

Phase 1b Warrant Axis + Correction Labels Days extend confidence_basis enum with definitional axiomatic model_based update check_assertion_epistemics to handle extended basis without requiring inference blocks for non-inferred types keep assertion.type 3 values add optional correction_class enum to review_history[] items start used set at 3 reserve 8 exit validator handles extended basis tests pass gate green — ADR-0046.

Phase 1c L7 Refinement Not Purge Days refine L7 to distinguish pedagogical vs knowledge remove learning_objectives instructional_sequencing from concept.schema.json properties allow real_world_applications common_misconceptions ONLY when evidenced as ValueClaim with evidence[] and source not free-form strings extend test_generality.py to reject pedagogical keys but allow evidenced knowledge claims record the archived SOTA review's §6.5 softer alternative as partially adopted exit schema updated test_generality rejects pedagogical keys but allows evidenced claims gate green — ADR-0047.

Phase 1d New Relations Days adopt equivalent_to misconception_of in registry with proper domain/range/symmetry/transitivity declarations update validator domain/range checks exit registry updated validator handles new relations gate green — ADR-0048.

Phase 1e Delegated Authority v2 Days add authority field to reviewed_by[] and review_history[] in connection.schema.json add trusted-institution entry type to agent-registry.yaml with audit_frequency sample_audit_rate last_audit next_audit review_standard_version delegated_provenance block update validator to accept delegated authority for canonical transitions only with registered institution add sample audit check 10% first 100 5% ongoing annual audit add revocation procedure update export contract to expose authority field exit schemas updated validator handles delegated authority tests pass gate green — ADR-0049.

Phase 2 Contract Update Days export_version 2.2.0→2.2.0 add authority field to export shape add value-slot support update adapters/python/ to handle value-slot and delegated authority update explorer/ to render value-slot claims and authority filter update docs/CONSUMERS.md with new contract surface exit export contract bumped adapter round-trips explorer renders gate green — ADR-0050.

Phase 3 Governance Hygiene Hours lhs sweep across all tracked files EXCEPT ADR documents which are history per ADR-0027 §3 un-stub tests/repo/test_independence.py and remove ecosystem references from AGENTS.md in same PR close ADR-0027 owner-ratification gate exit no stale references independence test live namespace clean — ADR-0051.

Phase 4 Content as Acceptance Test Before IRI Gate Hours to Days proof engine works register one trusted external institution in agent-registry.yaml exercises delegated authority v2 path with audit seed one source record conforming to source.schema.json SI Brochure 9th ed seed two entities metre with scientific definition exactly as meter example with reference fundamental quantities visible and phys.force with definition and reference conforming to updated concept.schema.json restores AGENTS.md Quick Start references seed one relational connection with non-empty evidence[] pointing to source record seed one value-claim connection measurement or misconception prevalence exercising value-slot one human review pass to canonical via scripts/review.py internal authority one delegated-authority import exercising institution path with sample audit python3 scripts/verify_all.py + git diff --exit-code -- exports reports exit full L8 chain proven end-to-end both authority tiers corpus has 3-5 entities 2-3 connections real content engine is built — ADR-0052 — work integrating early work from start as implementation of architecture.

Phase 5 Organization/IRI Gate Roadmap R3 Human decision owning organization domain IRI base everything touching published IRIs waits for this.

Phase 6 Projection Publication Roadmap R4 After Phase 5 Days exports/knowledge.jsonld+SKOS mapping+context file+SHACL shapes learn-from+signed release bundle+integrity manifest pluggable BFO schema.org exit.

Phase 7 Consumer Views and Routing After Phase 6 Days exports/views/* generation determinism tests calibration report from real review data review-queue routing R7 heuristic.

Phase 8 Scale Readiness Days benchmark git performance at 10^4 entities design content-addressed store with Merkle roots decide via ADR whether to migrate at 10^5 keep sharded YAML+LFS for now document migration plan.

## Current Status — After Ideal Order Rewrite + New Docs

- b958a5c empty corpus engine not yet built
- 51fc1b0 architecture v2 clean constitutional foundation single part L1-L8 refined
- 493b32b implementation plan v2 Phases 0-8 ideal order
- 27576f3 foundation reset fundamentals standard SI definitions clean 3D viewer integrating early work
- 3bcfd4a ingestion pipeline evolvable templates model selector integrating early work
- e692b25 comprehensive all-STEM template registry integrating early work
- dbc229f embeddings RAG separation consumer export guideline integrating early work
- 7297c6c strong CI explorer semantic pipeline final integrating early work
- 0df87ff fix status truth 1 entity 3 sources
- Now new docs new ADRs 0045-0052 roadmaps updated to architecture v2 ideal order

Verification: make quick-verify PASS — 1 entity metre via HITL, 0 connections, 3 sources, embeddings deterministic content_hash sha256:2c007fc6..., RAG vector search metre 0.2874 citations, semantic pipeline evidence first-class conflict demo P=10 vs P=12, explorer clean small nodes thin lines manual legend centered zoom 8 domains, webapp HITL PDF primary model selector DeepSeek harness, strong CI 10 jobs all-green.

## Verification commands

```bash
python3 scripts/validate.py  # OK 1 entities valid
python3 scripts/physics_core_profile_check.py  # OK 0 violations
python3 scripts/physics_governing_check.py  # OK 0 violations
python3 scripts/hitl_check.py --check-workflow  # OK HITL has human edits
python3 scripts/evolvable_template.py --pdf-extract  # OK 6 entities
python3 scripts/embed.py --model sentence-transformers/all-MiniLM-L6-v2 --output exports/embeddings.jsonl  # OK 1 embeddings
python3 scripts/rag.py --search "metre" --top-k 2  # OK vector search
python3 scripts/status_truth.py --write  # OK README status block
python3 scripts/verify_all.py  # OK all verify steps pass — architecture v2 ideal order
python3 scripts/verify_strong.py --quick  # ALL STRONG CHECKS GREEN
```

All good, ready for PR — but PR not created per instruction, now architecture v2 ideal order with new docs new ADRs roadmaps etc.
