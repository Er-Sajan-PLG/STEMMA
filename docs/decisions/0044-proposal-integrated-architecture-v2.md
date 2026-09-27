# STEMMA Integrated Knowledge Graph Architecture v2 — Constitutional Foundation + Semantic Acquisition + Federated Trust + Scale-Ready

Status: **Ratified** as [ADR-0044](0044-integrated-foundation-v2.md) (2026-09-21) — this proposal is preserved as the decision's full-length rationale; the normative text is ADR-0044 + [docs/ARCHITECTURE-V2.md](../ARCHITECTURE-V2.md). Moved from `docs/PROPOSAL-INTEGRATED-ARCHITECTURE-V2.md` on 2026-09-22.
Author: Arena Agent (on behalf of Principal Architect Sajan)
Date: 2026-09-21
Baseline: arena/01a0c072-stemma@fea770a — 1 entity metre via HITL, semantic acquisition pipeline implemented (16 stages, evidence first-class, independent verification, explicit conflict P=10 vs P=12), 8 domains 97 subdomains template-registry v2.0.0, embedding-registry 11 models, consumer-registry 4 consumers, llm-registry v1.0.0 5 roles 13 models, semantic-claim schema, strong CI 10 jobs ALL GREEN, explorer clean small nodes thin lines manual legend centered zoom.
Highest ratified ADR: 0039 archived, new ADRs 0040-0043 proposed in beginning no legacy.
Supersedes: Previous Integrated Proposal 2026-09-21 (empty corpus baseline) — rebased onto current implementation.

## Executive Summary

The previous integrated proposal correctly identified that STEMMA's flat entity/connection model cannot express evidence discipline, valued claims, epistemic warrant separation, regime-scoped formulations, or pedagogical boundaries. PR #41 correctly deleted old test corpus because engine for canonicalization was not yet built.

Since then, foundation HAS been built:

- Semantic Acquisition Pipeline implemented: 16 stages, evidence first-class (source_id, document_hash, page, section, text_span, char_offsets, page_coordinates, figure_id, surrounding_context, source_version), AI output must be proposal never canonical, independent verification (deterministic 7 checks + Verifier Model B separate from Extractor Model A + source corroboration), explicit conflict detection P=10 vs P=12 do not force average, human review final authority HITL, deterministic exports content_hash sha256 no wall-clock byte-identical.
- Template-registry v2.0.0 expanded to all STEM domains: 8 domains physics chemistry biology earth-science astronomy computer-science engineering mathematics, 97 subdomains, 12 entity types.
- Embedding-registry v1.0.0: 11 models local+frontier model selector like DeepSeek harness search bar category tabs All/Frontier/Reasoning/Vision/Free/Custom/Local/SOTA Fast, FREE/FRONTIER/REASONING badges, defaults all-MiniLM 384 fast, BGE Large SOTA 1024, OpenAI Large 3072, NVIDIA NV-Embed 4096 SOTA.
- Consumer-registry v1.0.0: 4 consumers LearningHub (canonical physics/chem/bio/math OpenAI Large GPT-4o), PROFESSOR-J (reviewed all 8 domains mediocre BGE Large offline DeepSeek R1 free), general, explorer.
- llm-registry v1.0.0: 5 roles document_vision extraction reasoning verification embedding, 13 models DeepSeek R1 free default extraction/reasoning/verification free via OpenRouter, Claude 3.5 Sonnet frontier, GPT-4o frontier multimodal vision, Gemini 2.5 Pro frontier 1M context, Llama 3.3 70B free, Qwen 2.5 72B, etc., provenance required fields model_provider model_id model_version prompt_version pipeline_version extraction_config source_hash document_version schema_version.
- Guideline to build embedder and RAG that imports from STEMMA consistently for better consumer architecture, sample in derived, docs updated about direction new change already implemented and future changes plan.
- Explorer and ingestion pipeline updated: clean 3D viewer small nodes thin lines legend manual zoom centered, PDF primary ingestion AI extract to markdown preview human explicitly edits before canonical both primary and secondary HITL, deterministic templates evolvable scalable, frontier+custom model selector like DeepSeek harness.
- Strong CI: 10 jobs all-green final gate nothing bad gets pushed/merged, both GitHub Actions and locally pre-commit pre-push hooks.

This v2 proposal integrates every architectural decision from four debate rounds + current implementation into single coherent design: constitutional laws refined, claim-centric data model with value-slot, delegated authority v2 with audit/sample/versioning/revocation, governing-laws dual-role architecture with honest interim, scale envelope 10^2–10^6 with sharded YAML+LFS now content-addressed design later, phased implementation where content serves as acceptance test BEFORE IRI gate, embedding/RAG producer vs consumer separation, export mechanism to consumers via OpenAPI.

Governing principle refined: The constitution is the foundation. Reality constrains the graph; the graph does not model reality directly. Standards are projection targets, never canonical dependencies. Definitions ARE claims with warrant definitional, not mere orientation. Knowledge about human misconceptions IS knowledge when evidenced, not automatically pedagogy.

---

## Part 1: Constitutional Laws (L1–L8) Refined

These eight laws are non-negotiable. Every schema, gate rule, import path, export format must satisfy them. They supersede prior prose that conflicts.

### L1 — Claim is sole bearer of epistemic truth, definitions are claims with warrant definitional

An entity, source, document, equation string, model output, or relationship does not become true merely by existing. Only a Claim can assert something as true, false, proposed, inferred, derived, or disputed. A canonical claim must carry: assertion state, context, evidence, provenance, review status.

Refinement from previous proposal: Definition string IS a claim when it has warrant definitional and evidence. Example: "The meter (symbol: m) is the base unit of length in SI. It is scientifically defined as the length of the path travelled by light in vacuum during 1/299,792,458 of a second." — this is not mere orientation, it IS true per SI Brochure 9th ed with reference. It must be represented as ValueClaim or relational Claim with warrant=definitional, evidence pointing to SI Brochure page, not as non-truth Property without evidence.

- Entity ≠ truth
- Source ≠ truth
- LLM output ≠ truth
- Definition without warrant/evidence ≠ truth, but definition WITH warrant definitional + evidence = truth-bearing claim

### L2 — Canonicalization is human-only, with delegated authority v2 (audited federation)

Path always: LLM/process → candidate → validation → independent verification → conflict analysis → proposal → human review → canonical. Never: LLM → canonical. AI agents are drafters behind a seam; named humans are authority. Rejection requires written reason (ADR-0031).

Amendment v2: A registered trusted external institution's verified human review may constitute human gate via delegated authority, with full provenance preserved, BUT with audit, sample re-review, versioning, and revocation. This does not weaken L2 — it extends "human" to include credentialed external review bodies operating under published standards, with safeguards.

Previous proposal had delegated authority without audit. v2 adds:

- Institution registration requires ADR-level governance decision
- review_standard_url + review_standard_version + audit_frequency + sample_audit_rate (10% first 100 claims, 5% ongoing) + last_audit + next_audit
- Sample re-review by STEMMA team
- Annual audit
- Revocation procedure: claims transition to unreviewed, require re-review, consumers notified via changelog
- Translation layer: external evidence chains mapped to STEMMA Source/Document/Observation
- L4 deterministic gates still apply to every imported object

### L3 — Five distinct epistemic states, never collapsed, plus warrant and correction axes

- model_confidence — uncalibrated signal from LLM (e.g., extraction confidence 0.92)
- source_support — direction/strength of evidence stance (supporting, contradicting, neutral)
- validation_status — deterministic gate outcome pass/fail/advisory
- review_status — human epistemic state unreviewed → reviewed → canonical → rejected (forward-only)
- epistemic_status — asserted / inferred / derived / disputed / hypothesized

A model may emit model_confidence; it may not change review_status or epistemic_status. These five states must remain mechanically separable in schema.

Additional axes (not collapsed into five, but separate):

- Warrant axis: confidence_basis enum ["expert_review","experimental","theoretical","derived","definitional","axiomatic","model_based",null] — how justified
- Correction axis: correction_class enum ["factual_error","category_error","relationship_error","provenance_error","incompleteness","hallucination","format_error","dangling_ref"] — why rejected/corrected, attaches to review_history[] items, per L3 never touches model_confidence, never sets review_status, never infers epistemic_status.

### L4 — Deterministic science stays deterministic

No LLM is authoritative for: reference integrity, schema conformance, units, dimensions, equation structure, variable binding, dimensional consistency, controlled vocabulary, graph invariants. These are computed, never generated. Gate layers deterministic must not require LLM. LLM is extractor/interpreter not authority. Embeddings are NOT replacement for semantic extraction — pipeline has both branches.

### L5 — Identity is immutable

A stemma: ID never changes meaning and is never reused. Correction is supersession + new ID. Aliases and deprecated_by provide total resolution. Identity guards enforced from git history + content_hash, not by assertion. Content hash separated workflow audit git-ignored audit.jsonl wall-clock allowed vs canonical content git-tracked content/ link source_refs external_ids provenance without wall-clock deterministic versioned via content_hash.

### L6 — Derived ≠ canonical

Exports, reports, views, projections (JSON-LD, SHACL, BFO mapping), embeddings, vector stores, RAG indexes are regenerable, byte-deterministic, never authoritative. Canonical layer depends on nothing; everything else depends on it. Embeddings are NOT in canonical, only derived exports/ with content_hash versioning. RAG is consumer-owned, but STEMMA provides reference implementation guideline.

### L7 — No curriculum, grade, course, country, product semantics in canonical, refined boundary

STEMMA is knowledge foundation. Pedagogical metadata (learning_objectives, instructional sequencing) belongs to consumers. Enforced by tests/curation/test_generality.py.

Refinement v2: real_world_applications and common_misconceptions are NOT automatically pedagogical. They are knowledge when evidenced as claims:

- "Photosynthesis is basis for agriculture" with evidence source — is knowledge, allowed as Claim, not pedagogical.
- "42% of students think photosynthesis occurs only in sunlight (Source: misconception study 2023)" — is ValueClaim about misconception entity with evidence, allowed.
- "Learning objective: students will understand photosynthesis" — is pedagogical, belongs to consumer, rejected from canonical.

Distinction: pedagogical = about teaching, knowledge = about world including human beliefs. Misconception prevalence is knowledge about human beliefs, with evidence, allowed as ValueClaim. Misconception itself as Entity (referent) with relation misconception_of linking to subject.

Legacy pedagogical fields purged refined: learning_objectives, instructional sequencing removed; real_world_applications, common_misconceptions allowed only when evidenced as claims with evidence[] and source, not as free-form strings.

Record SOTA-REVIEW §6.5 softer alternative (governed extensions) as partially adopted via extension-registry.yaml.

### L8 — Materialization chain is constitutional, 16 stages already implemented

```
DOCUMENT (content_sha256, version, URI; anchors to Source)
  │ ExtractionRun (tool, params_hash, run_hash)
  ▼
OBSERVATION (located reading)
  ▼
EVIDENCE WINDOWS (page, section, text_span, char_offsets, surrounding_context 3 sentences)
  ▼
CANDIDATE ASSERTION ← scripts/ingest.py, ingest_to_proposals.py, semantic_extract.py
  ▼
ENTITY RESOLUTION ← scripts/entity_resolution.py threshold 0.85 candidate if uncertain never auto-merge
  ▼
CLAIM (structured subject relation object conditions quantitative evidence link)
  │ draft seam: webapp/providers.py (ADR-0038) AI drafts; AI output is provenance never authority L2/L3
  ▼
NORMALIZATION (unit syntax validation identifier validation datatype validation deterministic)
  ▼
DETERMINISTIC VALIDATION ← nine frozen layers, fail closed: cited text contains value? unit valid? numerical valid? entity exists? relation conforms schema? equation parses? dimensional constraints?
  ▼
INDEPENDENT VERIFICATION ← Verifier Model B separate from Extractor Model A, deterministic+independent model+source corroboration
  ▼
CONFLICT ANALYSIS ← explicit P=10 vs P=12 do not force average P=11 do not allow LLM arbitrarily choose, represent uncertainty conditions measurement context competing claims source quality unresolved
  ▼
PROPOSAL GENERATION ← proposals/proposal-*.yaml evidence first-class NOT canonical workflow/proposals/ NOT canonical
  ▼
REVIEW ← named human OR delegated institution v2 with audit, forward-only
  ▼
CANONICAL ← human-only write L2
  ▼
DERIVED EXPORT ← deterministic, content-hashed L6 exports/knowledge.json v2.1.0 content_hash sha256 no wall-clock byte-identical embeddings.jsonl vector_store FAISS content_hash versioned
  ▼
CONSUMER ← file/API/SDK content_hash invalidation subset exports views LearningHub PROFESSOR-J explorer
```

Never: PDF → LLM → canonical.

---

## Part 2: Semantic Primitives Refined

| Primitive | Definition | Boundary |
|-----------|------------|----------|
| Entity | A referent. What we are talking about. | Not truth. Carries no relationships. Example: metre, force, photosynthesis. |
| Property | Intrinsic canonical structure of what an entity is, validated not reviewed, no evidence EXCEPT definitional properties which are claims with warrant definitional. | Structural: symbol, domain, but definition with warrant definitional IS claim with evidence. |
| Claim | An assertion about something. Two forms: relational (subject → predicate → object) and valued (subject → predicate → structured value). | Sole bearer of epistemic truth L1. |
| ValueClaim | Claim whose object is structured value (amount + bounds + unit). | Still claim, evidence-bearing. Measurements are ValueClaims never entities. |
| Relation | Typed, directed, registry-controlled edge. | Governed by schema/relation-registry.yaml. |
| Evidence | Located source-observation supporting/contradicting claim. | Not source, not claim. Has page section text_span char_offsets surrounding_context. |
| Source | Bibliographic citation record. | Not content, not document. |
| Document | Material artifact (content hash, version/edition, URI). | Not citation. |
| Observation | Specific located reading extracted from document. | Becomes evidence after interpretation. |
| EvidenceWindow | Paragraph segmentation with page section text_span char offsets surrounding context. | Deterministic, becomes evidence. |
| ExtractionRun | Activity producing observations. | Not provenance-by-assertion, has tool params_hash run_hash. |
| Context | Where/when/under what assumptions claim applies. | Not truth, not evidence. Example: temperature constant, model ideal_gas. |
| Derivation | Reproducible step premises → rule → conclusion. | Replay invariant: replay(rule, premises) == conclusion. |
| Provenance | Agent/activity/generation/review trail attestation not truth. | Includes model_provider model_id model_version pipeline_version prompt_version extraction_config content_hash. |
| Review | Forward-only human epistemic state machine. | Not validation, not confidence. |
| Rule | Registered transformation or constraint. | Registry-controlled, not free text, grounded via applies_to_entity. |
| Proposal | Staged candidate claim NOT canonical, evidence first-class, human review required. | Lives in proposals/ workflow/proposals/ git-ignored, never content/. |

Property/Claim boundary refined: Properties describe canonical structure; claims carry epistemic assertions. Representation tracks speech act not physics. But definitional speech acts ARE claims with warrant definitional + evidence.

---

## Part 3: Data Model

### 3.1 Canonical Object Kinds

Three directories as Git-native Markdown + YAML, plus staging:

- Entity (content/<domain>/<subdomain>/<slug>.md) — referent with properties + scientific definition exactly as meter example with reference, fundamental quantities visible, at least fundamental and derived quantities. After Phase 1c, carries NO pedagogical fields unless evidenced as claims L7 refined.
- Connection (connections/conn.NNNNNN.yaml) — first-class relational OR valued Claim.
- Source (sources/src.<slug>.yaml) — citation record.
- No separate claims/ directory. Valued statements use value slot on connection kind itself (target XOR value). Preserves one truth store, inherits immutability guard coverage, duplicate detection, evidence requirements, export machinery without fourth canonical surface.
- Staging (proposals/ and workflow/) — derived working area never canonical never committed, proposal-*.yaml evidence first-class, candidates, evidence_windows.json, audit.jsonl.

### 3.2 Value-Slot Design

When connection expresses measurement, prevalence, typed literal rather than relation between two entities:

```yaml
id: stemma:conn.NNNNNN
type: connection
source: stemma:<entity-id>
relation: <registered-relation>
# target: absent when value is present (XOR)
value:
  amount: "42.0"          # decimal string Wikibase-aligned
  lowerBound: "41.5"      # optional
  upperBound: "42.5"      # optional
  unit: "qudt:unit-Meter" # IRI per ADR-0024, or "1" dimensionless, interim allowlist QUDT/UCUM/SI symbols
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
  created_by: human:curator.001
  created_at: "2026-09-21T10:00:00Z" # not in canonical export, only in workflow audit
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
      correction_class: null
```

Aligns with Wikibase QuantityValue asymmetric bounds explicit unit IRIs dimensionless sentinel "1". Until ADR-0024 lands, unit values allowed: "1" OR QUDT/UCUM anchor strings OR SI symbols (m, kg, s, A, K, mol, cd) documented as interim allowlist in schema.

claim_signature extends to cover value-slot claims: sha256(source | relation | value_canonical | polarity | sorted(qualifiers)). check_id_immutability.py already covers connections/ so no new root needed.

### 3.3 Semantic Claim Schema as Candidate (Not Canonical)

schema/semantic-claim.schema.json — structured candidate claim NOT canonical, used in workflow/candidates/<doc_id>/semantic_claims.json evidence first-class:

Required: claim_id, source, claim, evidence, extraction

Claim: subject, relation (must come from relation-registry.yaml enum logically_requires mathematically_requires part_of special_case_of applies_to appears_in_law related_to derived_from causes depends_on proportional_to inversely_proportional_to composed_of measured_by has_unit increases_with decreases_with requires produces transforms_into equivalent_to misconception_of), object, conditions, quantitative.

Conditions: temperature constant, model ideal_gas, etc.

Quantitative: value, unit, range, uncertainty, significant_figures, equation, experimental_conditions.

Evidence: source_id, document_hash sha256, page, section, text_span, char_offsets start end, page_coordinates x y width height, figure_id, surrounding_context, source_version.

Extraction: model_provider, model_id, model_version, pipeline_version, prompt_version, extraction_config max_tokens top_k domain_filter evidence_window_size, confidence, extraction_output.

Verification: status pending supported unsupported uncertain conflict, deterministic_checks check result pass fail detail, independent_model verifier_model_id verifier_model_provider result supported unsupported uncertain evidence_comparison, source_corroboration source_id value agreement agree disagree unrelated.

Conflict: status no_conflict conflict unresolved resolved, competing_claims source_id value unit conditions source_quality.

Provenance: created_at, created_by, content_hash sha256.

This schema is for candidates, not canonical. Canonical uses connection.schema.json with value slot.

### 3.4 Relation Registry

55 relations in 13 families, 12 adopted, 43 reserved. Reserved may not enter canonical without ADR adopting them.

Cycle scoping: Gate cycle detection check_relationship_cycles applies to ALL transitive non-symmetric relations. No blanket exemptions. Derivation/dependency cycles derived_from mathematically_requires logically_requires are genuine logical contradictions must be caught. If reproduced false positive appears during Phase 5, scoped cycle_policy: warn escape hatch may be added for that specific relation via ADR — but not preemptively on empty corpus.

New adoptions scheduled Phase 1d:

- equivalent_to (currently reserved) — adopted for formulation equivalence, symmetric true, transitive true, domain law, range law
- misconception_of (new) — adopted for linking misconception entities to subjects. Domain: misconception. Range: enumerated entity types from concept.schema enum NOT "any". Explicitly declare symmetric false inverse null transitive false.

Future adoptions: requires, produces, transforms_into for process relations.

### 3.5 Assertion Type and Warrant Axis

Keep assertion.type surgical: ["asserted","inferred","proposed"]. Do NOT expand to include derived, disputed, hypothesized — these conflate warrant (how justified) with stance (how held).

Warrant axis: Extend confidence_basis enum currently ["expert_review","experimental","theoretical","derived",null] to serve as warrant taxonomy. Add definitional, axiomatic, model_based. This field already exists, already pairs with confidence, avoids breaking check_assertion_epistemics.

Stance axis: Expressed through existing mechanisms — contradicts relation reserved adopt when needed, polarity field, evidence stance.

Update check_assertion_epistemics to handle extended confidence_basis values without requiring inference blocks for warrant types other than inferred.

### 3.6 Entity Schema Changes L7 Refined

L7 refined purge vs allow:

- Remove learning_objectives, instructional_sequencing from concept.schema.json properties entirely. Extend test_generality.py to reject these keys in frontmatter.
- Allow real_world_applications, common_misconceptions ONLY when evidenced as claims with evidence[] and source, not as free-form strings. If present as free-form without evidence, gate error. If present as ValueClaim with evidence, allowed and exported as claim, not as property.
- Record SOTA-REVIEW §6.5 softer alternative governed extensions as partially adopted via extension-registry.yaml.

Definition: Remains required but is explicitly claim with warrant definitional + evidence, not non-truth property orientation. Must have source reference. Example meter definition must show agreed status and source reference. Document in schema description.

Scientific definition exactly as meter example: "The meter (symbol: m) is the base unit of length in the International System of Units (SI). It is scientifically defined as the length of the path travelled by light in a vacuum during a time interval of 1/299,792,458 of a second." Must update all entities with standard definition not general.

Fundamental quantities like length mass time visible, at least add fundamental and derived quantities, update docs on add entity with scientific definition references.

No properties wrapper: ADR-0017 extensions seam with extension-registry.yaml governance already provides mechanism for structural non-truth fields. Use existing extension registry.

### 3.7 Correction Labels

Add optional correction_class field to provenance.review_history[] items:

Enum: factual_error | category_error | relationship_error | provenance_error | incompleteness | hallucination | format_error | dangling_ref
Start actively used set at 3 (factual_error, relationship_error, other); expand based on Phase 5 review data.
Attaches to individual review decisions not whole claims.
Per L3: never touches model_confidence, never sets review_status, never infers epistemic_status.

### 3.8 Governing Laws — Dual-Role Architecture with Honest Interim

Physical laws occupy four architectural surfaces simultaneously:

| Role | Location | Function |
|------|----------|----------|
| Referent | content/physics/<slug>.md (Entity, type: law) | Named, defined, historically attributed. Carries properties, not truth. |
| Knowledge Hub | Claims in connections/ | Formulations, history, evolution, misconceptions, deeper derivations. All evidence-bearing, all reviewable. |
| Constraint | schema/rule-registry.yaml (kind: constraint) | Bounds what other claims can enter canonical. Fires at gate layers 5–7. Deferred until ADR-0024 lands — expressions cannot be computed yet. |
| Derivation Engine | schema/rule-registry.yaml (kind: derivation) | Enables formal reproduction. Satisfies replay invariant. Deferred until ADR-0024 lands. |

Critical linkage: applies_to_entity in rule registry grounds each rule in specific canonical entity. Rules never free-floating gate logic.

Interim enforcement v2: Until ADR-0024 lands, constraint/derivation rules exist as registered documentation only. Gate emits WARNING "rule exists but not enforced until ADR-0024" not silent skip, enforcement remains human review responsibility. Rule registry entry records intent, gate skips execution for unparseable expressions with warning. This is stated honestly not hidden.

History, previous ideas, changes, misconceptions about law are Claims attached to law's entity hub — never stored inside constraint rule. Nothing orphaned.

---

## Part 4: Delegated Authority Tier v2 (Audited Federation)

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
      reason: "Verified under Wikidata community review process v3.2, sample audit 10% passed"
```

### 4.2 Trusted Institution Registration

schema/agent-registry.yaml gains trusted-institution entry type:

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
    status: active  # active | revoked | suspended
    audit_frequency: "annual" # monthly | quarterly | annual
    sample_audit_rate: 0.1 # 10% first 100, 5% ongoing
    last_audit: "2026-09-20"
    next_audit: "2027-09-20"
```

Adding institution requires ADR-level governance decision. This is per-institution human gate replacing per-claim gate for their verified work, but with audit safeguards.

### 4.3 Audit and Sample

- Every delegated import must pass L4 deterministic gates (schema, identity, references, vocabularies, cycles)
- Sample re-review: 10% of first 100 claims from new institution re-reviewed by STEMMA team, then 5% ongoing
- Annual audit of institution review standard URL versioning
- Translation layer: external evidence chains mapped to STEMMA Source/Document/Observation via adapter
- Unit translation via interim allowlist QUDT/UCUM/SI symbols
- Conflict detection still runs: if institution A says P=10 and institution B says P=12, CONFLICT explicit, do not force average
- Audit report: reports/delegated-audit-<institution>.{md,json} gate-generated freshness-checked

### 4.4 Import Semantics

- External verified claims from registered institutions enter as canonical with authority delegated
- L4 deterministic gates still run on every import
- Original IDs preserved as external_ids anchors
- Original evidence chains preserved as source_ref pointers translated to STEMMA schema
- Revocation: if institution registration revoked/suspended, their claims transition to unreviewed and require STEMMA-team re-review, consumers notified via exports/views/changelog.json and integrity manifest
- Revocation cost: re-review 10% sample Hours per 100 claims, full revocation Days per 1000 claims

### 4.5 Consumer Surface

Export contract exposes authority field so consumers can filter:

- review.status == canonical AND authority == internal (STEMMA-reviewed)
- review.status == canonical AND authority == delegated (institution-verified)
- Both are canonical, both trustworthy but with different audit trails, consumers choose trust threshold
- Trust score based on audit recency and sample pass rate
- Example: LearningHub may choose internal only for physics-core, PROFESSOR-J may choose both for mediocre all 8 domains

---

## Part 5: Embedding and RAG Architecture (Producer vs Consumer Separation)

### 5.1 Producer: STEMMA Provides Deterministic Derived Embeddings, Not Canonical

Per L6, canonical never contains embeddings/RAG. Derived exports/ provides:

- exports/embeddings.jsonl — deterministic, content_hash versioned, model all-MiniLM 384 dim etc
- exports/vector_store/ — FAISS or vectors.json, meta.json content_hash versioned
- exports/knowledge.json — deterministic content_hash sha256 no wall-clock byte-identical

Embedding-registry v1.0.0: 11 models local+frontier model selector like DeepSeek harness:

- all-MiniLM 384 fast local free default
- BGE Large SOTA 1024 local
- OpenAI Large 3072 frontier
- NVIDIA NV-Embed 4096 SOTA frontier
- etc.

Embedding model selection via workflow/config/llm.json git-ignored, not in canonical. Model selector like DeepSeek harness search bar category tabs All/Frontier/Reasoning/Vision/Free/Custom/Local/SOTA Fast, FREE/FRONTIER/REASONING badges, custom input.

Embeddings are NOT replacement for semantic extraction — pipeline has both branches text extraction → embeddings → retrieval AND text extraction → semantic extraction → candidate claims → validation.

### 5.2 Consumer: Embedder and RAG Are Consumer's Job, Reference Implementation Provided

Guideline to build embedder and RAG system that imports from STEMMA consistently for better consumer architecture, sample in derived, docs updated about direction new change already implemented and future changes plan.

- docs/GUIDELINE-EMBEDDER-RAG.md 81KB 19 sections how to build embedder and RAG that imports from STEMMA consistently
- explorer/ reference implementation loads exports/knowledge.json + embeddings.jsonl + vector_store, RAG vector search + citations
- Consumers LearningHub, PROFESSOR-J, general, explorer import via file/API/SDK content_hash invalidation subset exports
- RAG system needed in STEMMA? No, RAG is consumer-owned, but STEMMA provides reference implementation and deterministic derived artifacts that make consumer RAG safe.

Whose job is embedding and RAG? CONSUMER's job, not STEMMA's — STEMMA provides reference implementation. Embedding and RAG can be out of STEMMA as connection layer not containing whole STEMMA — how they connect via file/API/SDK + content_hash. Explicit separation canonical vs derived vs consumer — canonical never contains embeddings/RAG, derived + consumer inevitably needs them.

### 5.3 Export Mechanism to Consumers Like LearningHub, PROFESSOR-J via API Schema Link/API

- OpenAPI 3.0.3 api.yaml, endpoints /api/entities /api/connections /api/sources /api/semantic/claims /api/semantic/proposals/list /api/semantic/registries /api/embeddings /api/rag/search, content_hash versioned, contract validation
- webapp/server.py already implements GET /api/semantic/claims /proposals/list /registries POST /api/semantic/extract /verify /conflicts /proposals /resolve + existing /api/entities /api/connections /api/ingest /api/rag/search
- Consumer-registry v1.0.0 4 consumers: LearningHub canonical physics/chem/bio/math OpenAI Large GPT-4o, PROFESSOR-J reviewed all 8 domains mediocre BGE Large offline DeepSeek R1 free, general, explorer
- Subset exports: exports/knowledge.json (all), exports/knowledge.canonical.json, reviewed, trusted, proposed, rejected, plus views/
- Content-hash invalidation: consumers know exactly when to reload via meta.json content_hash
- SDK: adapters/python/ round-trips

---

## Part 6: Standards Alignment (Projection Only, Pluggable)

Everything here is derived L6. Nothing canonical. Nothing runs before IRI gate Phase 5.

### 6.1 Pluggable Projection Targets

Previous proposal fixed BFO-2020 as projection target. v2 makes pluggable: BFO-2020, schema.org, SKOS, QUDT/UCUM, Wikidata.

Two rules:

- Relation enters published context only with verified IRI
- Mapping at recording level: entities project to GDC (BFO_0000031) OR schema.org Thing

Key mappings:

- special_case_of / generalizes → skos:narrower / skos:broader
- related_to → skos:related
- Source documents → knowledge content: BFO_0000059 "concretizes" — information pattern carried by source document SDC not material carrier concretizes GDC knowledge content. Written BFO reading addressing carrier-vs-pattern distinction required before publication.
- Relations with no BFO IRI → project under stemma: IRIs. Anchored to QUDT/UCUM via external_ids.
- BFO choice justified but pluggable, written reading required before publication.

### 6.2 JSON-LD, SHACL, PROV-O

- exports/knowledge.jsonld — roadmap R4 after IRI gate, byte-deterministic
- SHACL — learn-from-only. Shapes for consumer validation never shadow gate
- PROV-O — L8 chain already PROV-O-shaped. Projection emits it as prov: triples
- Signed release bundles follow nanopublication pattern emitted only on IRI/RDF substrate

### 6.3 Wikidata Anchor Strategy

STEMMA advantage over Wikidata is governance rigor not data-model novelty:

- Controlled multi-valued gate-validated regime vocabulary layer 3
- Deterministic gate failing CI on conformance
- Per-claim evidence trails version control
- Constitutional guarantee no model output ever canonical L2

Wikidata qualifiers approximate regime scoping but lack enforcement. Consumers get both: anchors external_ids.wd resolve STEMMA entities to Wikidata for multilingual labels. String IDs language-neutral.

---

## Part 7: Scale Architecture (10^2–10^6 Entities)

Design target: Medium-term scale 10^5–10^6 canonical entities, mediocre all domain comprehensive 400-800 initial.

### 7.1 Producer Storage Progression

| Scale | Canonical Substrate | Governance |
|-------|---------------------|------------|
| 10^2–10^4 (current) | YAML files in git sharded content/<domain>/<subdomain>/<slug>.md PR review validate.py git history | PR review, validate.py, git history, content_hash |
| 10^5–10^6 (design target) | Sharded content-addressed store with git-like commit chain objects chunked manifests addressed by content hash Merkle roots | Same gate same human review objects in chunked manifests, but keep sharded YAML+LFS for now, design content-addressed but not migrate yet, benchmark at 10^4 |

At 10^5–10^6 entities, individual YAML files exceed git performance boundaries. Canonical storage migrates to content-addressed substrate where each object stored by hash commits are Merkle roots pointing to full state tree. L1–L8 invariants preserved because identity immutability enforced by append-only DAG deterministic exports computed from state tree human review operates on diffs between snapshots.

v2 refinement: Keep sharded YAML + LFS for now, design content-addressed but not migrate yet, benchmark git performance at 10^4 entities, decide via ADR whether to migrate at 10^5. Avoid premature optimization.

### 7.2 Instance Data Exclusion

STEMMA does NOT store billions raw observations. Raw datasets external sources, STEMMA cites them via sources/ and extracts specific evidence-bearing observations. Dataset lives in own infrastructure CERN NCBI etc. STEMMA holds pointer extracted claim evidence trail.

### 7.3 Consumer Retrieval at Scale

Consumers load exports/knowledge.json into own infrastructure. For 10^6 entities ~2-5GB JSON consumers build own databases search indexes graph databases SPARQL endpoints CDNs. STEMMA provides deterministic file that makes all safe. Content-hash invalidation ensures consumers know exactly when to reload. Subset exports let consumers load only what they need.

---

## Part 8: AI-Accelerated Curation (16 Stages Already Implemented)

### 8.1 Intake Chain L8 16 Stages

```
DOCUMENT (content_sha256, version, URI; anchors to Source)
  │ ExtractionRun (tool, params_hash, run_hash)
  ▼
OBSERVATION (located reading)
  ▼
EVIDENCE WINDOWS (page, section, text_span, char_offsets, surrounding_context)
  ▼
CANDIDATE ASSERTION ← scripts/ingest.py, ingest_to_proposals.py, semantic_extract.py
  ▼
ENTITY RESOLUTION ← scripts/entity_resolution.py threshold 0.85 candidate if uncertain never auto-merge
  ▼
CLAIM ← draft seam: webapp/providers.py (ADR-0038) AI drafts; AI output is provenance never authority L2/L3
  │ AI-assisted semantic extraction model selector like DeepSeek harness local+frontier extraction role deepseek-r1 free claude-3.5-sonnet gpt-4o gemini-2.5-pro llama-3.3 free custom relation vocab from relation-registry.yaml 8+ relations
  ▼
NORMALIZATION (unit syntax validation identifier validation datatype validation deterministic)
  ▼
DETERMINISTIC VALIDATION ← nine frozen layers fail closed: cited text contains value? unit valid? numerical valid? entity exists? relation conforms schema? equation parses? dimensional constraints?
  ▼
INDEPENDENT VERIFICATION ← Verifier Model B separate from Extractor Model A deterministic+independent model+source corroboration
  ▼
CONFLICT ANALYSIS ← explicit P=10 vs P=12 do not force average P=11 do not allow LLM arbitrarily choose one, represent uncertainty conditions measurement context competing claims source quality unresolved
  ▼
PROPOSAL GENERATION ← proposals/proposal-*.yaml evidence first-class NOT canonical workflow/proposals/ NOT canonical
  ▼
REVIEW ← named human OR delegated institution v2 with audit, forward-only
  ▼
CANONICAL ← human-only write L2
  ▼
DERIVED EXPORT ← deterministic, content-hashed L6
  ▼
CONSUMER ← file/API/SDK
```

Never: PDF → LLM → canonical.

Known gaps Phase 0 work: ingest.py candidates don't conform to source.schema.json; hand-written report prose embeds stale counts — fix before anything else.

### 8.2 Calibration Report

reports/calibration.{md,json} — gate-generated freshness-checked. Baseline curation pilot 36 candidates →12 accepted ~33% 0 auto-canonicalized states measured values only. Current semantic pipeline with deterministic fallback regex + independent verification may improve to 50-60% need to measure after Phase 4 content.

### 8.3 Review-Queue Routing Roadmap R7

Heuristic worksheet-ordering mechanism not predictive model. Threshold ≥200 labeled decisions across ≥3 domains set by R7 ADR. Invariants: canonical remains per-object and human L2; routing changes order only never content.

### 8.4 No Producer-Side Model Training

Correction data published CC BY 4.0. ORES pattern with deliberate difference producer declines to own training loop entirely.

---

## Part 9: Consumption

### 9.1 Contract

Deterministic export exports/knowledge.json: content-hash stamped contract-validated relation-registry+vocabulary sidecar claim signatures embedded. Consumers pin export major version. First-party adapter fails closed on unknown relations.

Trust thresholds consumer choices: export carries all active objects at every review state with authority field exposed. Consumers filter on status rank evidence presence authority.

### 9.2 Consumer Views Derived exports/views/

| View | Content | Feeds |
|------|---------|-------|
| views/prerequisites.json | Dependency subgraph includes cycle set | Adaptive pathways |
| views/misconceptions.json | Per-entity misconception records | Targeted tutoring |
| views/formulations.json | Per-law formulation sets | History rendering |
| views/centrality.json | Degree/centrality per entity | Prioritization |
| views/changelog.json | Per-release changed-entity list | Change handling |

Curriculum alignment consumer-owned mapping artifact keyed on stemma: IDs.

### 9.3 Explorer

Clean 3D viewer small nodes thin lines legend manual zoom centered, 8 domains theme, trust distribution, search filter, already implemented.

---

## Part 10: Implementation Phases Refined (Sequential Enforcement, Content Before IRI Gate)

Every phase lands with enforcement in same change set ADR+validator+test+docs+verify_all green+clean git diff derived per ADR-0026 discipline. Phases sequential deferring moves it never silently drops precondition.

### Phase 0 — Foundation Prerequisites (Hours)

(a) Reproducibility fix. Declare pyyaml + jsonschema in root requirements.txt. Currently dependencies exist only inline in .github/workflows/ci.yml. Clean clone gate exits 2. Fix before anything else.

(b) Write ADR-0044 v2 into docs/decisions/. This proposal becomes ratified document. Includes supersession list amends ADR-0011 0013 0014 0020 0026 plus previous integrated proposal.

(c) Update docs/decisions/README.md. Retitle from LearningHubSTEM Foundation to STEMMA Foundation. Index ADRs 0023–0044.

(d) Fix AGENTS.md dead Quick Start references NORTHSTAR.md STEMMA-SPECIFICATION.md retired by ADR-0027 force.md deleted by PR #41.

(e) Fix ingest.py candidates conform to source.schema.json; remove hand-written report prose stale counts.

Exit: ADR-0044 committed README indexed requirements.txt present AGENTS.md clean gate green.

### Phase 1a — Value-Slot on Connection Kind (Days)

Land schema+validator+tests together.

Make target and value mutually exclusive XOR in connection.schema.json. Extend claim_signature computation in validate.py. Extend check_id_immutability.py to cover value-slot claims. Unit field interim allowlist QUDT/UCUM/SI symbols documented anchor strings until ADR-0024 not just "1".

Exit: Schemas updated validator handles new shapes tests pass gate green on current corpus 1 entity.

### Phase 1b — Warrant Axis + Correction Labels (Days)

Extend confidence_basis enum with definitional axiomatic model_based. Update check_assertion_epistemics to handle extended basis without requiring inference blocks for non-inferred types. Keep assertion.type at 3 values. Add optional correction_class enum to review_history[] items start used set at 3 reserve 8.

Exit: Validator handles extended basis tests pass gate green.

### Phase 1c — L7 Refinement Not Purge (Days)

Refine L7 to distinguish pedagogical vs knowledge. Remove learning_objectives instructional_sequencing from concept.schema.json properties. Allow real_world_applications common_misconceptions ONLY when evidenced as ValueClaim with evidence[] and source not free-form strings. Extend test_generality.py to reject pedagogical keys but allow evidenced knowledge claims. Record SOTA-REVIEW §6.5 softer alternative as partially adopted.

Exit: Schema updated test_generality rejects pedagogical keys but allows evidenced claims gate green.

### Phase 1d — New Relations (Days)

Adopt equivalent_to and misconception_of in registry with proper domain/range/symmetry/transitivity declarations. Update validator domain/range checks.

Exit: Registry updated validator handles new relations gate green.

### Phase 1e — Delegated Authority v2 (Days)

Add authority field to reviewed_by[] and review_history[] in connection.schema.json. Add trusted-institution entry type to agent-registry.yaml with audit_frequency sample_audit_rate last_audit next_audit review_standard_version delegated_provenance block. Update validator to accept delegated authority for canonical transitions only with registered institution. Add sample audit check 10% first 100 5% ongoing annual audit. Add revocation procedure. Update export contract to expose authority field.

Exit: Schemas updated validator handles delegated authority tests pass gate green.

### Phase 2 — Contract Update (Days)

(a) export_version 2.1.0 → 2.2.0 in schema/export.schema.json and schema/VERSION.yaml. Add authority field and value-slot support to export shape.

(b) Update adapters/python/ to handle value-slot claims and delegated authority.

(c) Update explorer/ to render value-slot claims and authority filter.

(d) Update docs/CONSUMERS.md with new contract surface.

Exit: Export contract bumped adapter round-trips explorer renders gate green.

### Phase 3 — Governance Hygiene (Hours)

(a) lhs sweep across all tracked files EXCEPT ADR documents which are history per ADR-0027 §3.

(b) Un-stub tests/repo/test_independence.py and remove ecosystem references from AGENTS.md in same PR.

(c) Close ADR-0027 owner-ratification gate.

Exit: No stale references independence test live namespace clean.

### Phase 4 — Content as Acceptance Test (Before IRI Gate) (Hours to Days)

This is proof engine works — thing PR #41 said doesn't exist yet now does but extend to prove full L8 chain both authority tiers.

(a) Register one trusted external institution in agent-registry.yaml exercises delegated authority v2 path with audit.

(b) Seed one source record conforming to source.schema.json SI Brochure 9th ed.

(c) Seed two entities: metre with scientific definition exactly as meter example with reference fundamental quantities visible, and phys.force with definition and reference, conforming to updated concept.schema.json. Restores file AGENTS.md Quick Start references.

(d) Seed one relational connection with non-empty evidence[] pointing to source record.

(e) Seed one value-claim connection measurement or misconception prevalence exercising value-slot.

(f) One human review pass to canonical via scripts/review.py internal authority.

(g) One delegated-authority import exercising institution path with sample audit.

(h) python3 scripts/verify_all.py + git diff --exit-code -- exports reports.

Exit: Full L8 chain proven end-to-end both authority tiers. Corpus has 3-5 entities 2-3 connections real content. Engine is built.

### Phase 5 — Organization/IRI Gate (Roadmap R3) (Human decision)

Human decision on owning organization domain IRI base. Everything touching published IRIs waits for this.

### Phase 6 — Projection Publication (Roadmap R4 After Phase 5) (Days)

exports/knowledge.jsonld + SKOS mapping + context file + SHACL shapes learn-from + signed release bundle + integrity manifest pluggable BFO schema.org.

### Phase 7 — Consumer Views and Routing (After Phase 6) (Days)

exports/views/* generation + determinism tests + calibration report from real review data + review-queue routing R7 heuristic.

### Phase 8 — Scale Readiness (Days)

Benchmark git performance at 10^4 entities, design content-addressed store with Merkle roots, decide via ADR whether to migrate at 10^5, keep sharded YAML+LFS for now, document migration plan.

---

## Part 11: Cost Model Realistic

| Work | Basis | Estimate |
|------|-------|----------|
| Phase 0 (ADR + index + requirements + AGENTS fix) | Documentation | Hours |
| Phase 1a-1e (schema overhaul split) | Code + tests | 1-2 weeks total |
| Phase 2 (contract update) | Code + tests | Days |
| Phase 3 (governance hygiene) | Code + tests | Hours |
| Phase 4 (seed content) | One source, two entities, two connections, two reviews, one delegated import | Hours to Days |
| Phase 5 (org/IRI gate) | Human decision | Days to Weeks (external) |
| Phase 6 (projection) | Code + docs | Days |
| Phase 7 (views + routing) | Code + tests | Days |
| Phase 8 (scale readiness benchmark + design) | Code + docs | Days |
| Evidence backfill (future corpus) | Pilot rate TBD after Phase 4 | Measured after seed |
| Revocation cost | Re-review 10% sample Hours per 100 claims, full revocation Days per 1000 | Measured |
| Producer infrastructure | git + CI + free tiers + LFS | ≈ $0 now, $5-20/month at 10^5 with LFS |
| Consumer infrastructure | Consumer-owned | Out of scope |

---

## Part 12: Verification Plan Extended

- Value-slot: connection with both target and value → schema error. Connection with neither → schema error. Value without evidence at canonical → gate error.
- L7 refined: test_generality.py rejects learning_objectives instructional_sequencing keys. Allows real_world_applications common_misconceptions only when evidenced as ValueClaim with evidence[] and source, otherwise error. Negative tests per key.
- Warrant axis: unknown confidence_basis value → error. assertion.type remains 3-value enum.
- Corrections: unknown correction_class enum → error.
- Misconceptions: misconception_of with range outside enumerated types → error. Missing symmetry declaration → error.
- Delegated authority v2: authority delegated without registered institution in agent-registry → error. Unknown institution ID → error. Institution without review_standard_url/version → error. Sample audit rate <5% → warning. Institution status revoked/suspended → their claims transition to unreviewed error if still canonical.
- Cycle enforcement: structural hierarchy cycles still rejected. Dependency cycles still rejected. No exemptions.
- Export contract: export_version matches schema/VERSION.yaml. Adapter round-trips value-slot and authority.
- Standing gates: verify_all.py green + git diff --exit-code -- exports reports.
- Embeddings: deterministic content_hash versioned, no embeddings in canonical, embeddings in derived only, byte-identical on rerun.
- RAG: vector search works with citations, deterministic.
- Semantic pipeline: evidence first-class, AI output must be proposal, independent verification deterministic+Verifier Model B, conflict analysis explicit P=10 vs P=12 do not force average, human review final authority, 16 stages, model roles, model-agnostic, reproducibility content_hash.
- Explorer: clean small nodes thin lines manual legend centered zoom 8 domains.
- Webapp: HITL enforced, PDF primary, model selector like DeepSeek harness.

---

## Part 13: What This Is Not (Closed List Refined)

- No hosted service. Publication is file contract.
- No canonical BFO/OWL dependency, no OWL reasoning. BFO is projection pluggable.
- No curriculum, grade, course, country, product semantics in canonical data L7 refined pedagogical belongs consumers knowledge about misconceptions allowed when evidenced.
- No pedagogy in kernel. Legacy pedagogical fields purged refined.
- No producer-side model training.
- No confidence collapse L3. Five states stay five plus warrant and correction axes separate.
- No machine-checked dimensional consistency until ADR-0024 lands. Interim review responsibility + gate warning rule exists but not enforced.
- No embeddings in canonical data, no RAG in canonical. Derived embeddings reference implementation provided, consumer-owned RAG.
- No mutable database as source of truth L6. Content-addressed at scale design, git-native now sharded YAML+LFS.
- No separate claims/ directory. Value-slot on connections.
- No rule registry enforcement until ADR-0024 lands. Designed not executed with warning.
- No cycle exemptions. Semantic enforcement stands.
- No unfounded scale projections. Scope envelope 10^5–10^6 design target measured.
- No coupling to any private product ecosystem.

---

## Part 14: Options Considered and Rejected Refined

| Option | Why rejected |
|--------|--------------|
| Content-first ordering when foundation weak | Foundation has demonstrated weakness previous test corpus. Content against broken schemas re-proves defects doesn't discover new ones. Foundation must be built deliberately then tested. BUT now foundation exists semantic pipeline strong CI green, so content as acceptance test Phase 4 BEFORE IRI gate is middle path content-first after foundation built. |
| Separate claims/ directory | Escapes immutability guard check_id_immutability.py walks only content/ and connections/. Creates fourth truth surface. Re-creates ADR-0020 two truths defect. Value-slot on connections inherits all existing machinery. |
| Expand assertion.type to 6 values | Conflates warrant how justified with stance how held. Breaks check_assertion_epistemics which requires inference block only for inferred. Warrant belongs on confidence_basis. |
| Blanket cycle_scope exempt for dependency relations | derived_from/mathematically_requires/logically_requires cycles ARE logical contradictions. Exempting them disables one check that catches their only structural bug. |
| Rule registry with unevaluable expressions | Gate that cannot fail is governance by document not mechanism. Violates ADR-0026 discipline. Deferred until ADR-0024 makes expressions computable with warning. |
| Per-claim re-review of external institutional work | Redundant labor. Their verified work reviewed by qualified humans under published standards. Delegated authority preserves trust while eliminating duplication. Credit given provenance preserved. BUT pure institution-level gate too coarse, v2 adds audit sample versioning. |
| Map external verified to STEMMA proposed | Dishonest. Their verification IS verification just performed by different authorized body. Mapping to proposed erases work forces redundant effort. |
| Map external verified to canonical without audit | Trust dilution. No audit no sample no versioning no revocation. v2 adds safeguards. |
| L7 blanket purge | Too rigid loses knowledge about misconceptions real_world_applications which are knowledge when evidenced. Refined to allow evidenced knowledge claims. |
| Property definition as non-truth orientation | Definition IS truth with warrant definitional + evidence SI Brochure. Refined to claim with warrant definitional. |
| Scale migration immediate to content-addressed store | Premature optimization no prototype. Keep sharded YAML+LFS design content-addressed but not migrate yet benchmark at 10^4. |
| BFO as only projection target | Not justified. Make pluggable BFO schema.org SKOS QUDT Wikidata. |
| Producer-side RAG | L6 derived ≠ canonical. Producer RAG would be derived not canonical but still producer-owned model. Consumer-owned RAG reference implementation allowed. Clarified. |

---

## Part 15: Consequences

What becomes easier:

- Expressing measurements, misconception prevalence, physical quantities as first-class evidence-bearing value-claims with warrant definitional/experimental.
- Coexisting formulations of laws with regime-qualified validity equivalent_to.
- Importing verified work from trusted institutions without redundant review but with audit sample versioning.
- Machine-checking equations dimensions variable bindings once ADR-0024 lands with warning interim.
- Projecting to standards ecosystems without polluting canonical layer pluggable BFO schema.org.
- Measuring AI curation quality through correction labels and calibration reports.
- Scaling to 10^5–10^6 with sharded YAML+LFS design content-addressed future.
- Consuming via file/API/SDK content_hash subset exports LearningHub PROFESSOR-J explorer with trust thresholds.

What becomes harder:

- Authoring canonical content requires understanding Property/Claim/ValueClaim distinction warrant axis.
- Delegated authority v2 requires maintaining institution registry audit_frequency sample_audit_rate last_audit next_audit revocation procedures translation layer.
- Value-slot XOR logic adds schema complexity over simple target field.
- Migration from flat entities to value-slot when content exists requires careful scripting.
- Maintaining audit sample re-review workload.

What is hard to undo:

- Once value-claims exist in connections removing requires migrating all measurements back to inline strings.
- Once L7 refined restoring pedagogical fields violates constitution.
- Once delegated authority granted revoking requires transitioning claims to unreviewed re-review consumers notified.
- Once content-addressed store migrated reverting to YAML requires migration.
- Once BFO IRI published changing IRI base breaks consumers.

---

## Part 16: Human Decisions Required

| # | Decision | Proposed Answer |
|---|----------|-----------------|
| 1 | Ratify ADR-0044 v2 as constitutional specification | Yes — this document once approved becomes normative core superseding previous proposal and amending ADR-0011 0013 0014 0020 0026 |
| 2 | Approve value-slot on connections no claims/ directory interim allowlist QUDT/UCUM/SI not just "1" | Yes — one truth store immutability preserved |
| 3 | Approve warrant axis extension confidence_basis with definitional axiomatic model_based keep assertion.type 3 values | Yes |
| 4 | Approve L7 refinement not blanket purge allow evidenced real_world_applications common_misconceptions as ValueClaims | Yes |
| 5 | Approve correction labels enum | Yes |
| 6 | Approve new relations equivalent_to misconception_of with proper declarations | Yes |
| 7 | Approve delegated authority tier v2 with audit sample versioning revocation | Yes — eliminates redundant review preserves credit with safeguards |
| 8 | Confirm no cycle exemptions semantic enforcement stands | Yes — catch real bugs add warn only on reproduced false positives via ADR |
| 9 | Confirm evidence requirement for canonical already implemented validate.py:658 | Acknowledged |
| 10 | Approve removal ecosystem references from AGENTS.md + un-stub test | Yes — do together Phase 3 |
| 11 | Approve content as acceptance test Phase 4 before IRI gate | Yes — prove engine now |
| 12 | Approve scale readiness Phase 8 benchmark sharded YAML+LFS design content-addressed not migrate yet | Yes |
| 13 | Approve pluggable projection targets BFO schema.org SKOS not BFO only | Yes |
| 14 | Approve producer vs consumer separation embeddings RAG consumer-owned reference implementation provided | Yes |

---

## Appendix: Current Implementation Already Satisfies Parts of Proposal

- Semantic Acquisition Pipeline 16 stages implemented docs/SEMANTIC-ACQUISITION-PIPELINE.md 81KB
- llm-registry.yaml v1.0.0 5 roles 13 models model selector DeepSeek harness
- semantic-claim.schema.json evidence first-class
- scripts/semantic_extract.py evidence windows char offsets surrounding_context relation vocab 8 domains deterministic fallback regex
- scripts/verify_claim.py deterministic 7 checks + independent model verifier + source corroboration
- scripts/conflict_analysis.py explicit conflict P=10 vs P=12 do not force average demo-conflict
- scripts/proposal_generate.py evidence first-class NOT canonical human review required
- scripts/entity_resolution.py threshold 0.85 candidate if uncertain never auto-merge
- webapp/server.py semantic endpoints GET /api/semantic/claims /proposals/list /registries POST /extract /verify /conflicts /proposals /resolve
- webapp/static/index.html semantic pipeline card 16 stages vertical slice corpus 6 PDFs
- verify_all.py + verify_strong.py semantic pipeline checks 5 roles 13 models evidence first-class conflict demo P=10 vs P=12
- explorer clean small nodes thin lines manual legend centered zoom 8 domains
- template-registry v2.0.0 8 domains 97 subdomains
- embedding-registry v1.0.0 11 models
- consumer-registry v1.0.0 4 consumers
- api.yaml OpenAPI 3.0.3
- GUIDELINE-EMBEDDER-RAG.md 81KB reference implementation

This proposal builds on that foundation, refines L7, adds delegated authority v2 with audit, makes projection pluggable, splits Phase 1, moves content acceptance before IRI gate, and adds scale readiness benchmarking.

