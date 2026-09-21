# STEMMA Architecture v2 — Constitutional Foundation

Status: Authoritative
Date: 2026-09-21
Baseline: b958a5c empty corpus — engine for canonicalization not yet built, now built.

## Executive Summary

STEMMA is a scientific knowledge foundation, not a curriculum, not a product. It stores canonical knowledge as evidence-bearing claims in Git-native Markdown + YAML, with deterministic exports, byte-identical content_hash, no wall-clock, no embeddings in canonical, consumer-owned RAG.

Previous corpus was deleted because engine for canonicalization was not yet built. This architecture specifies complete foundation that must exist before real content enters: constitutional laws, claim-centric data model, audited delegated authority for trusted institutions, governing-laws dual-role, scale envelope 10^2–10^6, 16-stage semantic acquisition pipeline.

Governing principle: Constitution is foundation. Reality constrains graph; graph does not model reality directly. Standards are projection targets, never canonical dependencies. Definitions are claims with warrant definitional + evidence.

## Part 1: Constitutional Laws L1–L8

Non-negotiable. Every schema, gate rule, import path, export format must satisfy them.

**L1 — Claim is sole bearer of epistemic truth, definitions are claims with warrant definitional**

Entity, source, document, equation string, model output, relationship does not become true merely by existing. Only Claim can assert as true, false, proposed, inferred, derived, disputed, hypothesized. Canonical claim must carry assertion state, context, evidence, provenance, review status.

Definition example: "The meter (symbol: m) is the base unit of length in the International System of Units (SI). It is scientifically defined as the length of the path travelled by light in a vacuum during a time interval of 1/299,792,458 of a second." — this IS true per SI Brochure 9th ed, represented as Claim with warrant=definitional + evidence pointing to SI Brochure page.

- Entity ≠ truth
- Source ≠ truth
- LLM output ≠ truth
- Definition without warrant/evidence ≠ truth, definition WITH warrant definitional + evidence = truth-bearing claim

**L2 — Canonicalization is human-only, with delegated authority v2 audited federation**

Path: LLM/process → candidate → validation → independent verification → conflict analysis → proposal → human review → canonical. Never LLM→canonical. AI drafters behind seam, named humans authority, rejection requires written reason.

Delegated authority v2: Registered trusted external institution's verified human review may constitute human gate via delegated authority with full provenance, with audit, sample re-review, versioning, revocation. Extends "human" to include credentialed external review bodies operating under published standards, with safeguards: institution registration requires ADR, review_standard_url + review_standard_version + audit_frequency + sample_audit_rate 10% first 100 5% ongoing + last_audit + next_audit, sample re-review by STEMMA team, annual audit, translation layer external evidence to STEMMA Source/Document/Observation, L4 deterministic gates still apply, revocation transitions to unreviewed require re-review consumers notified via changelog.

**L3 — Five epistemic states never collapsed, plus warrant and correction axes**

- model_confidence — uncalibrated signal from LLM
- source_support — direction/strength of evidence stance
- validation_status — deterministic gate outcome pass/fail/advisory
- review_status — human epistemic state unreviewed→reviewed→canonical→rejected forward-only
- epistemic_status — asserted/inferred/derived/disputed/hypothesized

Model may emit model_confidence; may not change review_status or epistemic_status. Mechanically separable in schema.

Additional axes separate:
- Warrant: confidence_basis ["expert_review","experimental","theoretical","derived","definitional","axiomatic","model_based",null] how justified
- Correction: correction_class ["factual_error","category_error","relationship_error","provenance_error","incompleteness","hallucination","format_error","dangling_ref"] why corrected, attaches to review_history[] items, never touches model_confidence, never sets review_status, never infers epistemic_status.

**L4 — Deterministic science stays deterministic**

No LLM authoritative for reference integrity, schema conformance, units, dimensions, equation structure, variable binding, dimensional consistency, controlled vocabulary, graph invariants. Computed, never generated. Gate layers deterministic must not require LLM. LLM is extractor/interpreter not authority. Embeddings NOT replacement for semantic extraction.

**L5 — Identity immutable**

stemma: ID never changes meaning never reused. Correction is supersession + new ID. Aliases and deprecated_by provide total resolution. Guards from git history + content_hash. Content hash separated workflow audit git-ignored wall-clock allowed vs canonical git-tracked deterministic versioned via content_hash.

**L6 — Derived ≠ canonical**

Exports, reports, views, projections JSON-LD SHACL BFO mapping, embeddings, vector stores, RAG indexes are regenerable byte-deterministic never authoritative. Canonical depends on nothing; everything else depends on it. Embeddings NOT in canonical only derived exports/ content_hash versioned. RAG consumer-owned reference implementation provided.

**L7 — No curriculum semantics in canonical, refined boundary**

STEMMA is knowledge foundation. Pedagogical metadata learning_objectives instructional sequencing belongs to consumers. Enforced by test_generality.py.

Refined: real_world_applications and common_misconceptions are knowledge when evidenced as claims:
- "Photosynthesis is basis for agriculture" with evidence source — is knowledge, allowed as Claim
- "42% of students think photosynthesis occurs only in sunlight (Source: misconception study 2023)" — is ValueClaim about misconception entity with evidence, allowed
- "Learning objective: students will understand photosynthesis" — is pedagogical, belongs to consumer, rejected from canonical

Distinction: pedagogical about teaching, knowledge about world including human beliefs. Misconception prevalence is knowledge about human beliefs with evidence, allowed as ValueClaim about misconception entity.

Legacy pedagogical fields: learning_objectives instructional_sequencing removed from concept.schema.json; real_world_applications common_misconceptions allowed ONLY when evidenced as ValueClaim with evidence[] and source not free-form strings.

**L8 — Materialization chain constitutional 16 stages**

```
DOCUMENT content_sha256 version URI anchors to Source
  │ ExtractionRun tool params_hash run_hash
  ▼
OBSERVATION located reading
  ▼
EVIDENCE WINDOWS page section text_span char_offsets surrounding_context 3 sentences
  ▼
CANDIDATE ASSERTION ingest.py semantic_extract.py
  ▼
ENTITY RESOLUTION threshold 0.85 candidate if uncertain never auto-merge
  ▼
CLAIM structured subject relation object conditions quantitative evidence link
  │ draft seam webapp/providers.py AI drafts AI output is provenance never authority L2/L3
  ▼
NORMALIZATION unit syntax identifier datatype deterministic
  ▼
DETERMINISTIC VALIDATION nine frozen layers fail closed
  ▼
INDEPENDENT VERIFICATION Verifier Model B separate from Extractor Model A deterministic+independent model+source corroboration
  ▼
CONFLICT ANALYSIS explicit P=10 vs P=12 do not force average P=11 do not allow LLM arbitrarily choose one
  ▼
PROPOSAL GENERATION proposals/proposal-*.yaml evidence first-class NOT canonical workflow/proposals/ NOT canonical
  ▼
REVIEW named human OR delegated institution v2 with audit forward-only
  ▼
CANONICAL human-only write L2
  ▼
DERIVED EXPORT deterministic content-hashed L6 exports/knowledge.json v2.2.0 content_hash sha256 no wall-clock byte-identical embeddings.jsonl vector_store FAISS content_hash versioned
  ▼
CONSUMER file/API/SDK content_hash invalidation subset exports views LearningHub PROFESSOR-J explorer
```

Never PDF→LLM→canonical.

## Part 2: Semantic Primitives

Entity — referent what we are talking about, not truth, carries no relationships, example metre, force, photosynthesis.

Property — intrinsic canonical structure validated not reviewed no evidence EXCEPT definitional properties which are claims with warrant definitional + evidence, example symbol, domain.

Claim — assertion about something, two forms relational subject→predicate→object and valued subject→predicate→structured value, sole bearer of epistemic truth L1.

ValueClaim — claim whose object is structured value amount + bounds + unit, still claim evidence-bearing, measurements are ValueClaims never entities.

Relation — typed directed registry-controlled edge governed by relation-registry.yaml.

Evidence — located source-observation supporting/contradicting claim, not source not claim, has page section text_span char_offsets surrounding_context.

Source — bibliographic citation record, not content not document.

Document — material artifact content hash version/edition URI, not citation.

Observation — specific located reading extracted from document, becomes evidence after interpretation.

EvidenceWindow — paragraph segmentation with page section text_span char offsets surrounding context deterministic becomes evidence.

ExtractionRun — activity producing observations not provenance-by-assertion has tool params_hash run_hash.

Context — where/when/under what assumptions claim applies not truth not evidence example temperature constant model ideal_gas.

Derivation — reproducible step premises→rule→conclusion replay invariant replay(rule, premises) == conclusion.

Provenance — agent/activity/generation/review trail attestation not truth includes model_provider model_id model_version pipeline_version prompt_version extraction_config content_hash.

Review — forward-only human epistemic state machine not validation not confidence.

Rule — registered transformation or constraint registry-controlled not free text grounded via applies_to_entity.

Proposal — staged candidate claim NOT canonical evidence first-class human review required lives in proposals/ workflow/ git-ignored never content/.

Property/Claim boundary: Properties describe canonical structure; claims carry epistemic assertions. Representation tracks speech act not physics. Definitional speech acts ARE claims with warrant definitional + evidence.

## Part 3: Data Model

### 3.1 Canonical Object Kinds

Three directories Git-native Markdown+YAML plus staging:

- Entity content/<domain>/<subdomain>/<slug>.md — referent with properties + scientific definition exactly as meter example with reference fundamental quantities visible at least fundamental and derived quantities. After L7 refined carries NO pedagogical fields unless evidenced as claims.
- Connection connections/conn.NNNNNN.yaml — first-class relational OR valued Claim.
- Source sources/src.<slug>.yaml — citation record.
- No separate claims/ directory. Valued statements use value slot on connection kind itself target XOR value preserves one truth store inherits immutability guard coverage duplicate detection evidence requirements export machinery without fourth canonical surface.
- Staging proposals/ and workflow/ — derived working area never canonical never committed proposal-*.yaml evidence first-class candidates evidence_windows.json audit.jsonl.

### 3.2 Value-Slot Design

When connection expresses measurement prevalence typed literal rather than relation between two entities:

```yaml
id: stemma:conn.NNNNNN
type: connection
source: stemma:<entity-id>
relation: <registered-relation>
# target absent when value present XOR
value:
  amount: "42.0"
  lowerBound: "41.5"
  upperBound: "42.5"
  unit: "qudt:unit-Meter" # IRI or "1" dimensionless interim allowlist QUDT/UCUM/SI symbols m kg s A K mol cd documented
assertion:
  type: asserted # asserted | inferred | proposed
  confidence_basis: experimental # expert_review experimental theoretical derived definitional axiomatic model_based
  confidence: 0.92
context:
  temperature: constant
  model: ideal_gas
evidence: # required for canonical gate enforces
  - source_id: src.si-brochure-9th
    document_hash: sha256:abc...
    page: 20
    section: "2.1"
    text_span: "The metre is defined as..."
    char_offsets: {start: 1024, end: 1150}
    surrounding_context: "Previous sentence. The metre is defined as... Next sentence."
    source_version: "9th ed 2019"
provenance:
  content_hash: sha256:...
  extraction:
    model_provider: openrouter
    model_id: deepseek-r1 free
    model_version: "2026-05-28"
    pipeline_version: "1.0.0"
    prompt_version: "1.0.0"
    extraction_config: {max_tokens: 2048, evidence_window_size: 3}
  reviewed_by:
    - type: human
      id: human:curator.001
      authority: internal
  review_history:
    - from: unreviewed
      to: canonical
      reviewer: human:curator.001
      authority: internal
      at: "2026-09-21T11:00:00Z"
      reason: "Verified against SI Brochure 9th ed page 20"
```

Aligns with Wikibase QuantityValue asymmetric bounds explicit unit IRIs dimensionless sentinel "1". Interim allowlist until ADR-0024: QUDT/UCUM anchor strings OR SI symbols m kg s A K mol cd documented.

claim_signature: sha256(source|relation|value_canonical|polarity|sorted(qualifiers)). check_id_immutability.py covers connections/.

### 3.3 Semantic Claim Schema as Candidate Not Canonical

schema/semantic-claim.schema.json — structured candidate claim NOT canonical used in workflow/candidates/<doc_id>/semantic_claims.json evidence first-class:

Required claim_id source claim evidence extraction

Claim subject relation must come from relation-registry.yaml enum logically_requires mathematically_requires part_of special_case_of applies_to appears_in_law related_to derived_from causes depends_on proportional_to inversely_proportional_to composed_of measured_by has_unit increases_with decreases_with requires produces transforms_into equivalent_to misconception_of object conditions quantitative.

Conditions temperature constant model ideal_gas etc.

Quantitative value unit range uncertainty significant_figures equation experimental_conditions.

Evidence source_id document_hash sha256 page section text_span char_offsets start end page_coordinates x y width height figure_id surrounding_context source_version.

Extraction model_provider model_id model_version pipeline_version prompt_version extraction_config max_tokens top_k domain_filter evidence_window_size confidence extraction_output.

Verification status pending supported unsupported uncertain conflict deterministic_checks check result pass fail detail independent_model verifier_model_id verifier_model_provider result supported unsupported uncertain evidence_comparison source_corroboration source_id value agreement agree disagree unrelated.

Conflict status no_conflict conflict unresolved resolved competing_claims source_id value unit conditions source_quality.

Provenance created_at created_by content_hash sha256.

This schema is for candidates not canonical. Canonical uses connection.schema.json with value slot.

### 3.4 Relation Registry

55 relations in 13 families 12 adopted 43 reserved. Reserved may not enter canonical without ADR adopting them.

Cycle scoping: Gate cycle detection check_relationship_cycles applies to ALL transitive non-symmetric relations no blanket exemptions. Derivation cycles derived_from mathematically_requires logically_requires are genuine logical contradictions must be caught. If reproduced false positive appears scoped cycle_policy:warn escape hatch may be added for that specific relation via ADR not preemptively on empty corpus.

New adoptions:

- equivalent_to — adopted for formulation equivalence symmetric true transitive true domain law range law
- misconception_of — adopted for linking misconception entities to subjects domain misconception range enumerated entity types from concept.schema enum NOT "any" symmetric false inverse null transitive false

### 3.5 Assertion Type and Warrant Axis

Keep assertion.type surgical ["asserted","inferred","proposed"] do NOT expand to derived disputed hypothesized conflates warrant with stance.

Warrant axis: Extend confidence_basis enum currently ["expert_review","experimental","theoretical","derived",null] to include definitional axiomatic model_based. Field already exists pairs with confidence avoids breaking check_assertion_epistemics.

Stance axis: Via contradicts relation reserved adopt when needed polarity field evidence stance.

Update check_assertion_epistemics to handle extended basis without requiring inference blocks for non-inferred types.

### 3.6 Entity Schema

Scientific definition exactly as meter example with reference symbol unit domain fundamental quantities visible at least fundamental and derived quantities. Must update all entities with standard definition not general.

Example: "The meter (symbol: m) is the base unit of length in the International System of Units (SI). It is scientifically defined as the length of the path travelled by light in a vacuum during a time interval of 1/299,792,458 of a second." Must show agreed status and source reference.

Fundamental quantities like length mass time visible at least add fundamental and derived quantities update docs on add entity with scientific definition references.

L7 refined: Remove learning_objectives instructional_sequencing from concept.schema.json properties entirely extend test_generality.py to reject these keys allow real_world_applications common_misconceptions ONLY when evidenced as ValueClaim with evidence[] and source not free-form strings. Record governed extensions via extension-registry.yaml.

Definition remains required but explicitly claim with warrant definitional + evidence not non-truth property orientation must have source reference.

No properties wrapper: ADR-0017 extensions seam with extension-registry.yaml governance already provides mechanism for structural non-truth fields use existing extension registry.

### 3.7 Correction Labels

Add optional correction_class field to provenance.review_history[] items:

Enum factual_error | category_error | relationship_error | provenance_error | incompleteness | hallucination | format_error | dangling_ref
Start actively used set at 3 factual_error relationship_error other expand based on review data.
Attaches to individual review decisions not whole claims.
Per L3 never touches model_confidence never sets review_status never infers epistemic_status.

### 3.8 Governing Laws Dual-Role Architecture

Physical laws occupy four surfaces simultaneously:

Role Location Function
Referent content/physics/<slug>.md Entity type law named defined historically attributed carries properties not truth
Knowledge Hub Claims in connections/ formulations history evolution misconceptions deeper derivations evidence-bearing reviewable
Constraint schema/rule-registry.yaml kind constraint bounds what other claims can enter canonical fires at gate layers 5-7 deferred until ADR-0024 expressions cannot be computed yet
Derivation Engine schema/rule-registry.yaml kind derivation enables formal reproduction satisfies replay invariant deferred until ADR-0024

Critical linkage applies_to_entity in rule registry grounds each rule in specific canonical entity rules never free-floating gate logic.

Interim enforcement: Until ADR-0024 lands constraint/derivation rules exist as registered documentation only gate emits WARNING rule exists but not enforced until ADR-0024 not silent skip enforcement remains human review responsibility rule registry entry records intent gate skips execution for unparseable expressions with warning stated honestly not hidden.

History previous ideas changes misconceptions about law are Claims attached to law's entity hub never stored inside constraint rule nothing orphaned.

## Part 4: Delegated Authority Tier v2 Audited Federation

### 4.1 Provenance Extension

Add authority field to provenance.reviewed_by[] entries and delegated_provenance block:

```yaml
provenance:
  reviewed_by:
    - type: human
      id: human:institution.wikidata-community
      authority: delegated
      delegated_provenance:
        institution_id: human:institution.wikidata-community
        review_standard_url: "https://www.wikidata.org/wiki/Wikidata:Verifiability"
        review_standard_version: "v3.2"
        audit_date: "2026-09-20"
        sample_audit_rate: 0.1
  review_history:
    - from: unreviewed
      to: canonical
      reviewer: human:institution.wikidata-community
      authority: delegated
      delegated_provenance:
        institution_id: human:institution.wikidata-community
        review_standard_url: "https://..."
        review_standard_version: "v3.2"
      at: '2026-09-20T...'
      reason: "Verified under Wikidata community review process v3.2 sample audit 10% passed"
```

### 4.2 Trusted Institution Registration

schema/agent-registry.yaml entry type institution:

```yaml
agents:
  - id: human:institution.biologists-kb
    type: institution
    name: "International Biological Knowledge Consortium"
    authority: delegated
    review_standard_url: "https://..."
    review_standard_version: "v2.1"
    contact: "review-board@..."
    registered_at: "2026-09-21"
    registered_by: "human:admin.sajan"
    status: active # active | revoked | suspended
    audit_frequency: annual
    sample_audit_rate: 0.1
    last_audit: "2026-09-20"
    next_audit: "2027-09-20"
```

Adding institution requires ADR-level governance decision per-institution human gate replacing per-claim gate with audit safeguards.

### 4.3 Audit and Sample

- Every delegated import must pass L4 deterministic gates schema identity references vocabularies cycles
- Sample re-review 10% first 100 claims 5% ongoing
- Annual audit of institution review standard URL versioning
- Translation layer external evidence chains mapped to STEMMA Source/Document/Observation
- Unit translation via interim allowlist QUDT/UCUM/SI symbols
- Conflict detection still runs P=10 vs P=12 CONFLICT explicit do not force average
- Audit report reports/delegated-audit-<institution>.{md,json} gate-generated freshness-checked

### 4.4 Import Semantics

- External verified claims enter canonical with authority delegated
- L4 deterministic gates still run on every import
- Original IDs preserved as external_ids anchors
- Original evidence chains preserved as source_ref pointers translated to STEMMA schema
- Revocation if revoked/suspended claims transition to unreviewed require re-review consumers notified via exports/views/changelog.json integrity manifest
- Revocation cost re-review 10% sample Hours per 100 claims full revocation Days per 1000

### 4.5 Consumer Surface

Export contract exposes authority field consumers filter:

- review.status == canonical AND authority == internal STEMMA-reviewed
- review.status == canonical AND authority == delegated institution-verified
- Both canonical both trustworthy but different audit trails consumers choose trust threshold trust score based on audit recency sample pass rate LearningHub may choose internal only for physics-core PROFESSOR-J may choose both for mediocre all 8 domains

## Part 5: Embedding and RAG Architecture Producer vs Consumer Separation

### 5.1 Producer STEMMA Provides Deterministic Derived Embeddings Not Canonical

Per L6 canonical never contains embeddings/RAG. Derived exports/ provides:

- exports/embeddings.jsonl deterministic content_hash versioned model all-MiniLM 384 dim etc
- exports/vector_store/ FAISS or vectors.json meta.json content_hash versioned
- exports/knowledge.json deterministic content_hash sha256 no wall-clock byte-identical

Embedding-registry v1.0.0 11 models local+frontier model selector like DeepSeek harness all-MiniLM 384 fast local free default BGE Large SOTA 1024 local OpenAI Large 3072 frontier NVIDIA NV-Embed 4096 SOTA frontier embedding model selection via workflow/config/llm.json git-ignored not canonical model selector like DeepSeek harness search bar category tabs All/Frontier/Reasoning/Vision/Free/Custom/Local/SOTA Fast FREE/FRONTIER/REASONING badges custom input embeddings NOT replacement for semantic extraction pipeline has both branches.

### 5.2 Consumer Embedder and RAG Are Consumer's Job Reference Implementation Provided

Guideline to build embedder and RAG system that imports from STEMMA consistently for better consumer architecture sample in derived docs updated about direction new change already implemented and future changes plan.

- docs/GUIDELINE-EMBEDDER-RAG.md 81KB 19 sections how to build embedder and RAG that imports from STEMMA consistently
- explorer/ reference implementation loads exports/knowledge.json + embeddings.jsonl + vector_store RAG vector search + citations
- Consumers LearningHub PROFESSOR-J general explorer import via file/API/SDK content_hash invalidation subset exports
- RAG system vector search + citations deterministic not containing whole STEMMA as connection layer

Whose job is embedding and RAG? CONSUMER's job not STEMMA's STEMMA provides reference implementation. Embedding and RAG can be out of STEMMA as connection layer not containing whole STEMMA how they connect via file/API/SDK + content_hash. Explicit separation canonical vs derived vs consumer canonical never contains embeddings/RAG derived+consumer inevitably needs them.

### 5.3 Export Mechanism to Consumers LearningHub PROFESSOR-J via API Schema

- OpenAPI 3.0.3 api.yaml endpoints /api/entities /api/connections /api/sources /api/semantic/claims /api/semantic/proposals/list /api/semantic/registries /api/embeddings /api/rag/search content_hash versioned contract validation
- webapp/server.py implements GET /api/semantic/claims /proposals/list /registries POST /api/semantic/extract /verify /conflicts /proposals /resolve + existing /api/entities /api/connections /api/ingest /api/rag/search
- Consumer-registry v1.0.0 4 consumers LearningHub canonical physics/chem/bio/math OpenAI Large GPT-4o PROFESSOR-J reviewed all 8 domains mediocre BGE Large offline DeepSeek R1 free general explorer
- Subset exports exports/knowledge.json all canonical reviewed trusted proposed rejected plus views/
- Content-hash invalidation consumers know exactly when to reload via meta.json content_hash
- SDK adapters/python/ round-trips

## Part 6: Standards Alignment Projection Only Pluggable

Everything derived L6 nothing canonical nothing runs before IRI gate Phase 5.

### 6.1 Pluggable Projection Targets

Pluggable BFO-2020 schema.org SKOS QUDT/UCUM Wikidata not fixed BFO only two rules relation enters published context only with verified IRI mapping at recording level entities project to GDC BFO_0000031 OR schema.org Thing key mappings special_case_of/generalizes → skos:narrower/broader related_to → skos:related Source documents → knowledge content BFO_0000059 concretizes information pattern carried by source document SDC not material carrier concretizes GDC knowledge content written BFO reading addressing carrier-vs-pattern distinction required before publication relations with no BFO IRI project under stemma: IRIs anchored to QUDT/UCUM via external_ids BFO choice justified but pluggable written reading required before publication.

### 6.2 JSON-LD SHACL PROV-O

- exports/knowledge.jsonld roadmap R4 after IRI gate byte-deterministic
- SHACL learn-from-only shapes for consumer validation never shadow gate
- PROV-O L8 chain already PROV-O-shaped projection emits prov: triples
- Signed release bundles nanopublication pattern emitted only on IRI/RDF substrate

### 6.3 Wikidata Anchor Strategy

STEMMA advantage governance rigor not data-model novelty controlled multi-valued gate-validated regime vocabulary layer 3 deterministic gate failing CI per-claim evidence trails version control constitutional guarantee no model output ever canonical L2 Wikidata qualifiers approximate regime scoping but lack enforcement consumers get both anchors external_ids.wd resolve STEMMA entities to Wikidata for multilingual labels string IDs language-neutral.

## Part 7: Scale Architecture 10^2–10^6

Design target medium-term scale 10^5–10^6 canonical entities mediocre all domain comprehensive 400-800 initial.

### 7.1 Producer Storage Progression

Scale Canonical Substrate Governance
10^2–10^4 current YAML files in git sharded content/<domain>/<subdomain>/<slug>.md PR review validate.py git history PR review validate.py git history content_hash
10^5–10^6 design target sharded content-addressed store with git-like commit chain objects chunked manifests addressed by content hash Merkle roots same gate same human review objects chunked manifests but keep sharded YAML+LFS for now design content-addressed but not migrate yet benchmark at 10^4 decide via ADR whether to migrate at 10^5 avoid premature optimization

At 10^5–10^6 entities individual YAML files exceed git performance boundaries canonical storage migrates to content-addressed substrate where each object stored by hash commits are Merkle roots pointing to full state tree L1–L8 invariants preserved because identity immutability enforced by append-only DAG deterministic exports computed from state tree human review operates on diffs between snapshots. Keep sharded YAML+LFS for now design content-addressed but not migrate yet benchmark git performance at 10^4 entities decide via ADR whether to migrate at 10^5.

### 7.2 Instance Data Exclusion

STEMMA does NOT store billions raw observations raw datasets external sources STEMMA cites them via sources/ extracts evidence-bearing observations dataset lives in own infrastructure CERN NCBI etc STEMMA holds pointer extracted claim evidence trail.

### 7.3 Consumer Retrieval at Scale

Consumers load exports/knowledge.json into own infrastructure for 10^6 entities ~2-5GB JSON consumers build own databases search indexes graph databases SPARQL endpoints CDNs STEMMA provides deterministic file safe content-hash invalidation subset exports let consumers load only what they need.

## Part 8: AI-Accelerated Curation 16 Stages

### 8.1 Intake Chain L8 16 Stages

```
DOCUMENT content_sha256 version URI anchors to Source
  │ ExtractionRun tool params_hash run_hash
  ▼
OBSERVATION located reading
  ▼
EVIDENCE WINDOWS page section text_span char_offsets surrounding_context
  ▼
CANDIDATE ASSERTION ingest.py semantic_extract.py
  ▼
ENTITY RESOLUTION threshold 0.85 candidate if uncertain never auto-merge
  ▼
CLAIM structured subject relation object conditions quantitative evidence link AI-assisted semantic extraction model selector DeepSeek harness extraction role deepseek-r1 free claude-3.5-sonnet gpt-4o gemini-2.5-pro llama-3.3 free custom relation vocab
  ▼
NORMALIZATION unit syntax identifier datatype deterministic
  ▼
DETERMINISTIC VALIDATION nine frozen layers fail closed
  ▼
INDEPENDENT VERIFICATION Verifier Model B separate from Extractor Model A deterministic+independent model+source corroboration
  ▼
CONFLICT ANALYSIS explicit P=10 vs P=12 do not force average P=11 do not allow LLM arbitrarily choose one
  ▼
PROPOSAL GENERATION proposals/proposal-*.yaml evidence first-class NOT canonical workflow/proposals/ NOT canonical
  ▼
REVIEW named human OR delegated institution v2 with audit forward-only
  ▼
CANONICAL human-only write L2
  ▼
DERIVED EXPORT deterministic content-hashed L6
  ▼
CONSUMER file/API/SDK
```

Never PDF→LLM→canonical.

### 8.2 Calibration Report

reports/calibration.{md,json} gate-generated freshness-checked baseline curation pilot 36 candidates →12 accepted ~33% 0 auto-canonicalized states measured values only current semantic pipeline deterministic fallback regex + independent verification may improve to 50-60% need to measure after content.

### 8.3 Review-Queue Routing

Heuristic worksheet-ordering mechanism not predictive model threshold ≥200 labeled decisions across ≥3 domains set by R7 ADR invariants canonical remains per-object human L2 routing changes order only never content.

### 8.4 No Producer-Side Model Training

Correction data published CC BY 4.0 ORES pattern producer declines to own training loop entirely.

## Part 9: Consumption

### 9.1 Contract

Deterministic export exports/knowledge.json content-hash stamped contract-validated relation-registry+vocabulary sidecar claim signatures embedded consumers pin export major version first-party adapter fails closed on unknown relations trust thresholds consumer choices export carries all active objects at every review state with authority field exposed consumers filter status rank evidence presence authority.

### 9.2 Consumer Views Derived exports/views/

View Content Feeds
views/prerequisites.json Dependency subgraph includes cycle set Adaptive pathways
views/misconceptions.json Per-entity misconception records Targeted tutoring
views/formulations.json Per-law formulation sets History rendering
views/centrality.json Degree/centrality per entity Prioritization
views/changelog.json Per-release changed-entity list Change handling

Curriculum alignment consumer-owned mapping artifact keyed on stemma IDs.

### 9.3 Explorer

Clean 3D viewer small nodes thin lines legend manual zoom centered 8 domains theme trust distribution search filter.

## Part 10: Implementation Phases

Every phase lands with enforcement same change set ADR+validator+test+docs+verify_all green+clean git diff derived per ADR-0026 discipline.

Phase 0 Foundation Prerequisites Hours reproducibility fix requirements.txt pyyaml jsonschema write ADR-0044 update docs/decisions/README.md retitle LearningHubSTEM to STEMMA Foundation index ADRs 0023-0044 fix AGENTS.md dead Quick Start refs (retired docs) fix ingest.py candidates conform to source.schema.json remove hand-written report prose stale counts exit ADR-0044 committed README indexed requirements.txt present AGENTS.md clean gate green.

Phase 1a Value-Slot Days make target and value mutually exclusive XOR in connection.schema.json extend claim_signature computation validate.py extend check_id_immutability.py to cover value-slot claims unit field interim allowlist QUDT/UCUM/SI symbols documented anchor strings until ADR-0024 not just "1" exit schemas updated validator handles new shapes tests pass gate green.

Phase 1b Warrant Axis + Correction Labels Days extend confidence_basis enum with definitional axiomatic model_based update check_assertion_epistemics to handle extended basis without requiring inference blocks for non-inferred types keep assertion.type 3 values add optional correction_class enum to review_history[] items start used set at 3 reserve 8 exit validator handles extended basis tests pass gate green.

Phase 1c L7 Refinement Not Purge Days refine L7 to distinguish pedagogical vs knowledge remove learning_objectives instructional_sequencing from concept.schema.json properties allow real_world_applications common_misconceptions ONLY when evidenced as ValueClaim with evidence[] and source not free-form strings extend test_generality.py to reject pedagogical keys but allow evidenced knowledge claims record the archived SOTA review's §6.5 softer alternative as partially adopted exit schema updated test_generality rejects pedagogical keys but allows evidenced claims gate green.

Phase 1d New Relations Days adopt equivalent_to misconception_of in registry with proper domain/range/symmetry/transitivity declarations update validator domain/range checks exit registry updated validator handles new relations gate green.

Phase 1e Delegated Authority v2 Days add authority field to reviewed_by[] and review_history[] in connection.schema.json add trusted-institution entry type to agent-registry.yaml with audit_frequency sample_audit_rate last_audit next_audit review_standard_version delegated_provenance block update validator to accept delegated authority for canonical transitions only with registered institution add sample audit check 10% first 100 5% ongoing annual audit add revocation procedure update export contract to expose authority field exit schemas updated validator handles delegated authority tests pass gate green.

Phase 2 Contract Update Days export_version 2.2.0→2.2.0 add authority field to export shape add value-slot support update adapters/python/ to handle value-slot and delegated authority update explorer/ to render value-slot claims and authority filter update docs/CONSUMERS.md with new contract surface exit export contract bumped adapter round-trips explorer renders gate green.

Phase 3 Governance Hygiene Hours lhs sweep across all tracked files EXCEPT ADR documents which are history per ADR-0027 §3 un-stub tests/repo/test_independence.py and remove ecosystem references from AGENTS.md in same PR close ADR-0027 owner-ratification gate exit no stale references independence test live namespace clean.

Phase 4 Content as Acceptance Test Before IRI Gate Hours to Days proof engine works register one trusted external institution in agent-registry.yaml exercises delegated authority v2 path with audit seed one source record conforming to source.schema.json SI Brochure 9th ed seed two entities metre with scientific definition exactly as meter example with reference fundamental quantities visible and phys.force with definition and reference conforming to updated concept.schema.json restores file AGENTS.md Quick Start references seed one relational connection with non-empty evidence[] pointing to source record seed one value-claim connection measurement or misconception prevalence exercising value-slot one human review pass to canonical via scripts/review.py internal authority one delegated-authority import exercising institution path with sample audit python3 scripts/verify_all.py + git diff --exit-code -- exports reports exit full L8 chain proven end-to-end both authority tiers corpus has 3-5 entities 2-3 connections real content engine is built.

Phase 5 Organization/IRI Gate Roadmap R3 Human decision owning organization domain IRI base everything touching published IRIs waits for this.

Phase 6 Projection Publication Roadmap R4 After Phase 5 Days exports/knowledge.jsonld+SKOS mapping+context file+SHACL shapes learn-from+signed release bundle+integrity manifest pluggable BFO schema.org exit.

Phase 7 Consumer Views and Routing After Phase 6 Days exports/views/* generation determinism tests calibration report from real review data review-queue routing R7 heuristic.

Phase 8 Scale Readiness Days benchmark git performance at 10^4 entities design content-addressed store with Merkle roots decide via ADR whether to migrate at 10^5 keep sharded YAML+LFS for now document migration plan.

## Part 11: Cost Model

Work Basis Estimate
Phase 0 Hours
Phase 1a-1e Days each total 1-2 weeks
Phase 2 Days
Phase 3 Hours
Phase 4 Hours to Days 3-5 entities
Evidence backfill pilot rate TBD after Phase 4 measured
Revocation cost re-review 10% sample Hours per 100 claims full revocation Days per 1000
Producer infrastructure git+CI+free tiers ≈$0 now $5-20/month at 10^5 with LFS
Consumer infrastructure consumer-owned out of scope

## Part 12: Verification Plan

Value-slot both target and value → schema error neither → error value without evidence at canonical → gate error L7 refined pedagogical keys rejected unless evidenced warrant unknown confidence_basis → error assertion.type 3-value enum corrections unknown enum → error misconception_of range outside enumerated types → error missing symmetry → error delegated authority without registered institution → error unknown institution → error institution without review_standard_url/version → error sample audit rate <5% → warning institution status revoked/suspended → their claims transition to unreviewed error if still canonical cycle enforcement structural hierarchy cycles rejected dependency cycles rejected no exemptions export contract version matches adapter round-trips standing gates verify_all green git diff exports reports embeddings deterministic content_hash no embeddings in canonical embeddings in derived only byte-identical on rerun RAG vector search works with citations deterministic semantic pipeline evidence first-class AI output must be proposal independent verification deterministic+Verifier Model B conflict analysis explicit P=10 vs P=12 do not force average human review final authority 16 stages model roles model-agnostic reproducibility content_hash explorer clean small nodes thin lines manual legend centered zoom 8 domains webapp HITL enforced PDF primary model selector like DeepSeek harness.

## Part 13: What This Is Not

No hosted service publication file contract, no canonical BFO/OWL dependency BFO projection pluggable, no curriculum grade course country product semantics in canonical L7 refined pedagogical belongs consumers knowledge about misconceptions allowed when evidenced, no pedagogy kernel legacy pedagogical fields purged refined, no producer-side model training, no confidence collapse L3 five states stay five plus warrant and correction axes separate, no machine-checked dimensional consistency until ADR-0024 lands interim human review + gate warning rule exists but not enforced, no embeddings in canonical derived only, no RAG in canonical consumer-owned RAG reference implementation provided, no mutable DB as source of truth content-addressed at scale design git-native now sharded YAML+LFS, no separate claims/ directory value-slot on connections, no rule registry enforcement until ADR-0024 lands designed not executed with warning, no cycle exemptions semantic enforcement stands, no unfounded scale projections scope envelope 10^5–10^6 design target measured, no coupling private product ecosystem.

## Part 14: Consequences

Easier expressing measurements misconception prevalence physical quantities as first-class evidence-bearing value-claims with warrant definitional/experimental, coexisting formulations laws regime-qualified validity equivalent_to, importing verified work trusted institutions without redundant review but with audit sample versioning, machine-checking equations dimensions variable bindings once ADR-0024 lands with warning interim, projecting to standards without polluting canonical layer pluggable BFO schema.org, measuring AI curation quality correction labels calibration reports, scaling to 10^5–10^6 with sharded YAML+LFS design content-addressed future, consuming via file/API/SDK content_hash subset exports LearningHub PROFESSOR-J explorer with trust thresholds.

Harder authoring canonical content requires understanding Property/Claim/ValueClaim distinction warrant axis, delegated authority v2 requires maintaining institution registry audit_frequency sample_audit_rate last_audit next_audit revocation procedures translation layer, value-slot XOR logic adds schema complexity, migration from flat entities to value-slot when content exists requires careful scripting, maintaining audit sample re-review workload.

Hard to undo once value-claims exist removing requires migrating measurements back to inline strings, once L7 refined restoring pedagogical fields violates constitution, once delegated authority granted revoking requires transitioning claims to unreviewed re-review consumers notified, once content-addressed store migrated reverting to YAML requires migration, once BFO IRI published changing IRI base breaks consumers.

## Part 15: Human Decisions Required

1 Ratify ADR-0044 v2 as constitutional specification Yes this document once approved becomes normative core superseding previous and amending ADR-0011 0013 0014 0020 0026
2 Approve value-slot on connections no claims/ directory interim allowlist QUDT/UCUM/SI not just "1" Yes one truth store immutability preserved
3 Approve warrant axis extension confidence_basis with definitional axiomatic model_based keep assertion.type 3 values Yes
4 Approve L7 refinement not blanket purge allow evidenced real_world_applications common_misconceptions as ValueClaims Yes
5 Approve correction labels enum Yes
6 Approve new relations equivalent_to misconception_of with proper declarations Yes
7 Approve delegated authority tier v2 with audit sample versioning revocation Yes eliminates redundant review preserves credit with safeguards
8 Confirm no cycle exemptions semantic enforcement stands Yes catch real bugs add warn only on reproduced false positives via ADR
9 Confirm evidence requirement for canonical already implemented validate.py:658 Acknowledged
10 Approve removal ecosystem references from AGENTS.md + un-stub test Yes do together Phase 3
11 Approve content as acceptance test Phase 4 before IRI gate Yes prove engine now
12 Approve scale readiness Phase 8 benchmark sharded YAML+LFS design content-addressed not migrate yet Yes
13 Approve pluggable projection targets BFO schema.org SKOS not BFO only Yes
14 Approve producer vs consumer separation embeddings RAG consumer-owned reference implementation provided Yes
