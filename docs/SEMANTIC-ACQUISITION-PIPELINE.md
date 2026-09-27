# AI-Assisted Semantic Acquisition Pipeline for STEMMA — Accepted Proposal Implementation

**Status:** Accepted with Amendments — Implemented 2026-09-21
**Version:** v1.0.0
**Related:** docs/PIPELINES.md, docs/ARCHITECTURE.md, docs/GUIDELINE-EMBEDDER-RAG.md, docs/TESTING.md

## 1. Objective — Accepted

Integrate AI/LLM-based semantic extraction into STEMMA's ingestion architecture so that STEMMA can extract not only raw text from books, papers, and other STEM sources, but also the **semantic scientific information expressed by those sources**.

The goal is not to make STEMMA "LLM-powered" for its own sake.

The goal is to ensure that STEMMA, as the reusable machine-readable kernel of STEM knowledge, does not discard the semantic information contained in primary scientific sources.

The architecture must therefore distinguish:

1. **What the source literally contains** — exact text, page, character offsets, evidence windows
2. **What an AI system interprets the source as meaning** — candidate structured claims with subject relation object conditions
3. **What STEMMA accepts as canonical knowledge** — canonical content/<domain>/*.md with exact definitions, triple verification, HITL

These must never be conflated.

## 2. Core Principle — Accepted with Amendment

Adopt architectural principle:

> **Use AI early for semantic understanding. Trust AI late only through independent verification and explicit canonicalization.**

More concretely:

```text
SOURCE (PDF, textbook, paper, 8 domains)
  ↓
Deterministic acquisition (URL/file handling, content hashing sha256, document identification, file integrity)
  ↓
Evidence-preserving extraction (PDF parsing poppler pdftotext + tesseract OCR, page identification, character offsets, paragraph segmentation, evidence windows)
  ↓
AI-assisted semantic extraction (model selector like DeepSeek harness: local + frontier models, extraction role)
  ↓
Structured candidate claims (subject relation object conditions, quantitative info, evidence link)
  ↓
Normalization (unit syntax validation, identifier validation, datatype validation)
  ↓
Entity Resolution (map to existing STEMMA entities, candidate entity if uncertain)
  ↓
Deterministic validation (schema validation, relation vocabulary from relation-registry.yaml, does entity exist, does equation parse, dimensional constraints)
  ↓
Independent verification (Verifier Model B separate from Extractor Model A + deterministic verification)
  ↓
Conflict / consistency analysis (explicit conflict detection P=10 vs P=12, not forced average, investigation/review)
  ↓
Proposal Generation (proposals/proposal-*.yaml with evidence first-class)
  ↓
Human review where required (HITL mandatory human:curator.001 explicitly edits markdown)
  ↓
Explicit canonicalization (review_entity.py accept + canonicalize, human reviewer)
  ↓
STEMMA canonical knowledge (content/<domain>/<subdomain>/*.md with exact definitions dual verification governed_by history triple verification link+source_refs+external_ids)
  ↓
Deterministic Exports / Indexes (exports/knowledge.json v2.2.0 deterministic content_hash sha256, no wall-clock, byte-identical on rerun, embeddings.jsonl + vector_store/ FAISS meta.json content_hash versioned, consumers/)
```

The LLM is therefore an **extractor/interpreter**, not an authority.

**Amendment:** All stages deterministic, versioned via content_hash, no wall-clock, no randomness, regenerable. Pipeline version, model identifier, prompt version, extraction config recorded in workflow/audit/audit.jsonl with content_hash, not wall-clock in canonical export.

## 3. Why LLMs Are Needed — Accepted

Books and research papers contain semantic information that cannot reliably be recovered by mechanical text extraction alone.

Example:

> "The resistance of a conductor is directly proportional to its length and inversely proportional to its cross-sectional area, provided temperature remains constant."

PDF parser can recover sentence exactly. Embedding model can represent sentence as vector. Neither produces structured scientific meaning:

```yaml
subject: electrical_resistance
relationships:
  - relation: proportional_to
    object: conductor_length
  - relation: inversely_proportional_to
    object: cross_sectional_area
condition:
  temperature: constant
```

STEMMA needs semantic layer because its purpose is not merely document retrieval. It is intended to represent reusable STEM knowledge. Therefore semantic extraction must become first-class ingestion capability.

**Amendment:** Two tracks:
- Track A Deterministic Scales (no LLM): SI Brochure 9th ed., NIST, IUPAC Gold Book, fundamental quantities length mass time — regex + exact constants c=299,792,458 exact, scales to any number, no model cost, no hallucination
- Track B Semantic Prose (LLM required): Biology, chemistry, conditional statements, cross-sentence relationships — LLM extraction with evidence linking

For fundamental quantities like length mass time visible, must show agreed status and source reference: "The meter (symbol: m) is base unit of length in SI scientifically defined as length of path travelled by light in vacuum during 1/299,792,458 s. Exact c=299,792,458 m/s." LLM must not invent when SI Brochure provides exact.

## 4. What Does NOT Need LLM — Accepted

Do not use LLM for deterministic operations where conventional software provides stronger guarantees. The following should remain deterministic wherever practical:

* source acquisition
* URL/file handling
* content hashing sha256
* document identification
* file integrity
* PDF parsing
* text extraction
* page identification
* character offsets
* paragraph segmentation
* sentence segmentation where deterministic tooling sufficient
* metadata extraction
* OCR execution
* basic table extraction
* document deduplication
* schema validation
* datatype validation
* unit syntax validation
* identifier validation
* provenance recording
* evidence linking
* cryptographic hashes
* database constraints
* deterministic transformations
* export generation
* content_hash versioning
* deterministic export byte-identical
* id-domain-map validation
* relation-registry inverse coherence

Presence of AI in STEMMA must not become reason to replace reliable deterministic software.

## 5. Where AI/LLMs ARE Required — Accepted with Amendments

### 5.1 Semantic claim extraction

Convert source prose into candidate structured claims.

Example:

```text
Source:
"At constant temperature, increasing the length of a conductor increases its electrical resistance proportionally."
```

Candidate:

```yaml
claim:
  subject: electrical_resistance
  relation: proportional_to
  object: conductor_length
conditions:
  temperature: constant
evidence:
  source_id: src.halliday-resnick-walker-12th
  document_hash: sha256:...
  page: 823
  text_span: "At constant temperature, increasing the length of a conductor increases its electrical resistance proportionally."
```

AI must retain link to exact source evidence.

Implementation: `scripts/semantic_extract.py` — uses model selector like DeepSeek harness (local + frontier), extraction role, prompt enforces relation vocabulary from `schema/relation-registry.yaml`, outputs candidate claims with evidence.

### 5.2 Entity and concept identification

Identify STEM entities appearing in natural language:

```
Young's modulus, stress, strain, temperature, lithium-ion battery, electrolyte, ionic conductivity
```

and map them to STEMMA entities where existing identity can be established. If identity uncertain, produce candidate entity rather than silently creating canonical one.

Implementation: `scripts/entity_resolution.py` — maps extracted entity strings to existing `content/` ids via exact match, alias, embedding similarity, but candidate entity if uncertain (score < threshold). Never silently creates canonical.

### 5.3 Relationship extraction

Extract relationships such as:

```
causes, depends_on, proportional_to, inversely_proportional_to, composed_of, measured_by, has_unit, increases_with, decreases_with, requires, produces, transforms_into
```

Relationship vocabulary must come from STEMMA's schema rather than allowing LLM to invent arbitrary canonical relationship types.

Implementation: `schema/relation-registry.yaml` has 8+ relations adopted with mutual inverses mirrored domain/range symmetric no inverse non-transitivity guardrails. `scripts/semantic_extract.py` prompt enforces valid relations list, `scripts/verify_claim.py` validates relation in registry.

### 5.4 Conditions and scope

Scientific statements frequently contain conditions that radically change meaning. Example "For an ideal gas at constant temperature..." condition is part of scientific meaning. AI extraction should identify:

```yaml
conditions:
  temperature: constant
  model: ideal_gas
```

rather than extracting only `pressure inversely_proportional_to volume`.

Implementation: `scripts/semantic_extract.py` extracts conditions, `schema/semantic-claim.schema.json` has conditions field.

### 5.5 Quantitative information

Extract numerical values, ranges, units, dimensions, equations, experimental conditions, uncertainty, significant figures, comparisons, thresholds, ratios, mathematical relationships.

Example:

```yaml
property:
  name: ionic_conductivity
  value: 2.1
  unit: mS/cm
conditions:
  temperature:
    value: 25
    unit: °C
```

LLM proposes structure, deterministic validators must verify representation.

Implementation: `scripts/semantic_extract.py` proposes, `scripts/verify_claim.py` deterministic checks: does cited text actually contain claimed value? is unit valid? is numerical representation valid?

### 5.6 Context-dependent meaning

Same term can have different meanings depending on domain and surrounding text: current, stress, work, potential, power, field, capacity. AI can use surrounding context to determine intended scientific concept. This is where conventional extraction alone becomes insufficient.

Implementation: `scripts/semantic_extract.py` uses surrounding context (evidence windows 3 sentences before/after) to disambiguate, maps to domain via `NS_TO_DOMAIN` 8 domains.

### 5.7 Cross-sentence and cross-paragraph relationships

Scientific meaning frequently spans multiple sentences.

```
Sentence 1: A material was heated to 800 °C.
Sentence 2: The resulting phase exhibited higher ionic conductivity.
Sentence 3: This increase was attributed to the formation of oxygen vacancies.
```

Sentence-by-sentence parser may fail to connect material → heating at 800°C → phase transformation → ionic conductivity increase → oxygen vacancies. AI semantic layer can propose these relationships while preserving underlying evidence.

Implementation: `scripts/semantic_extract.py` uses evidence windows (paragraph, section) not just sentence, proposes multi-hop relationships.

## 6. Embeddings Are NOT Replacement — Accepted

Do not treat embedding generation as equivalent to knowledge extraction.

Pipeline may contain both:

```text
Source
  ↓
text extraction
  ├──────────────→ embeddings
  │                   ↓
  │                retrieval
  │
  └──────────────→ semantic extraction
                      ↓
                 candidate claims
                      ↓
                  validation
```

Embeddings are useful for semantic retrieval, similarity search, finding related passages, locating supporting evidence, candidate entity matching, retrieval augmentation. But embedding does not itself constitute explicit STEMMA fact.

Implementation: Already have explicit separation Layer1 Canonical NO embeddings/RAG whole STEMMA, Layer2 Derived YES embeddings derived regenerable deterministic content_hash exports/embeddings.jsonl vector_store FAISS, Layer3 Consumer+RAG YES RAG as consumer mechanism can be out of STEMMA. CI checks no embeddings in canonical.

## 7. Evidence Must Be First-Class — Accepted with Amendment

Every AI-generated candidate claim must retain precise provenance. At minimum:

```yaml
evidence:
  source_id: ...
  document_hash: ...
  page: ...
  section: ...
  text_span: ...
```

Where possible preserve character offsets, page coordinates, figure/table identifiers, equation identifiers, surrounding context, source version, acquisition timestamp, extraction pipeline version, model identifier, extraction prompt/version, extraction output, confidence/uncertainty metadata.

System must answer "Why does STEMMA contain this?" and trace answer back to original evidence.

**Amendment:** Evidence first-class but separated:
- Workflow audit git-ignored `workflow/audit/audit.jsonl`: acquisition timestamp, extraction pipeline version, model identifier, prompt version, extraction output — allowed wall-clock, for reproducibility
- Canonical content git-tracked `content/`: link + source_refs + external_ids + provenance without wall-clock, deterministic, versioned via content_hash
- Evidence windows: `workflow/documents/<doc_id>/evidence_windows.json` with page, section, text_span, char offsets, surrounding context 3 sentences before/after

Implementation: `scripts/semantic_extract.py` outputs evidence with page, text_span, char offsets, surrounding context. `webapp/core.py` stores evidence windows. `schema/semantic-claim.schema.json` has evidence field.

## 8. AI Output Must Be Proposal — Accepted

Never directly write LLM output into `content/, connections/, sources/, ledger/, indexes/` canonical stores. Instead AI → proposal → verification → review → canonicalization. Example `proposals/proposal-000123.yaml` with proposal_id, source document_id document_hash, claim subject relation object, evidence page text_span, extraction model model_version pipeline_version prompt_version, verification status pending. Proposal is not canonical STEMMA knowledge.

Implementation: `workflow/candidates/<doc_id>/*.json` + markdown preview, `workflow/proposals/<slug>.md` staged, NOT written by app, human must verify and run `review.py + verify_all.py` before canonical change. `scripts/proposal_generate.py` generates proposals with evidence first-class.

## 9. Independent Verification — Accepted with Amendment

System must not rely solely on same LLM that generated claim to verify itself. Verification should use multiple mechanisms:

### Deterministic verification

Does cited text actually contain claimed value? Is unit valid? Is numerical representation valid? Does entity exist? Does relationship conform to schema? Does equation parse? Are dimensional constraints satisfied?

Implementation: `scripts/verify_claim.py` deterministic checks.

### Independent model verification

Use separate model/configuration or independently generated extraction when semantic verification required. Extractor Model A → Claim, Verifier Model B → Supported/unsupported/uncertain. Verifier should receive relevant evidence and claim, not blindly trust extractor's reasoning.

Implementation: `scripts/verify_claim.py` with model selector like DeepSeek harness, verifier model B separate from extractor Model A, prompt enforces independent verification.

### Source corroboration

Where appropriate: Paper A Paper B Textbook C Review D → cross-source comparison. Agreement does not automatically establish truth, but disagreement must become visible rather than silently resolved.

Implementation: `scripts/conflict_analysis.py` cross-source comparison.

**Amendment:** Define verification as deterministic + independent model via model selector like DeepSeek harness + source corroboration. Record verifier model id, version, prompt version in provenance.

## 10. Conflict Detection Must Be Explicit — Accepted, Currently Missing, Now Implemented

Scientific sources can disagree. Example Source A X property P=10, Source B P=12, do not force P=11 and do not allow LLM to arbitrarily choose one. Instead Entity X with Source A → P=10 and Source B → P=12 → CONFLICT → investigation/review. Canonical layer should represent uncertainty, conditions, measurement context, competing claims, historical values, source quality, unresolved conflicts rather than flattening literature into one unsupported value.

Implementation: `scripts/conflict_analysis.py` — explicit conflict detection, new fields in `schema/semantic-claim.schema.json` and `concept.schema.json`:
- `conflicts: [{source_id, value, unit, conditions, source_quality, status: unresolved}]`
- `uncertainty: {value, unit, significant_figures, measurement_context}`
- `historical_values: [{value, source, date, superseded_by}]`
- Deterministic validator detects conflicting values for same property and flags CONFLICT not silently resolves.

Current STEMMA has no conflict representation — now implemented.

## 11. Human Review Is Final Authority — Accepted, Matches HITL

Canonicalization boundary should remain explicit: AI → extraction → proposals → verification → conflict analysis → HUMAN REVIEW → CANONICALIZATION. AI may recommend, classify, extract, identify conflicts, must not silently become authority that modifies canonical STEMMA knowledge.

Implementation: HITL mandatory `human:curator.001` explicitly edits markdown, both primary PDF and secondary direct agent addition have HITL before canonical, `hitl_check.py` verifies audit trail candidate_edited by human:*, writer human:*, markdown explicit edit before canonical.

## 12. Recommended Ingestion Architecture — 16 Stages — Accepted with Prioritization

Implement ingestion as separate stages:

```
1. Source Discovery
2. License / Eligibility Gate
3. Acquisition + Hash
4. Manifest
5. Document Parsing / OCR
6. Evidence Windows
7. Semantic AI Extraction
8. Normalization
9. Entity Resolution
10. Deterministic Validation
11. Independent Verification
12. Conflict Analysis
13. Proposal Generation
14. Human Review
15. Explicit Canonicalization
16. Deterministic Exports / Indexes
```

Existing deterministic Phase 1 work should be retained and extended rather than discarded.

**Amendment:** Map to current workflow and prioritize:
- R1 NOW (MVP): 3,5,6,7,10,13,14,15,16 — Acquisition+Hash, Document Parsing/OCR, Evidence Windows, Semantic AI Extraction, Deterministic Validation, Proposal Generation, Human Review, Explicit Canonicalization, Deterministic Exports/Indexes
- R2: 2,8,9,11,12 — License/Eligibility Gate, Normalization, Entity Resolution, Independent Verification, Conflict Analysis
- R3: 1 — Source Discovery + Production RAG conflict-aware retrieval

Current: `scripts/ingest.py` deterministic, `webapp/core.py` Workflow with documents/candidates/proposals/audit, `pdf_ingest_primary.py` primary feeder, `validate.py`, `hitl_check.py`, `export_review_aware.py`, `embed.py`, `rag.py`.

## 13. Model Roles — Accepted with Free Tier

Do not use one generic LLM for every task. Define explicit model roles:

```yaml
models:
  document_vision:
    purpose: [figures, tables, equations, scanned layouts]
  extraction:
    purpose: [semantic claims, entities, relationships, conditions, quantitative data]
  reasoning:
    purpose: [multi-sentence interpretation, contextual analysis, conflict investigation]
  verification:
    purpose: [independent claim verification, evidence comparison]
  embedding:
    purpose: [semantic retrieval, similarity, entity candidate matching]
```

This allows each model to be evaluated against task it actually performs.

Implementation: `schema/llm-registry.yaml` + `schema/embedding-registry.yaml` with role, category, free, local, cost, use_case. Model selector window standard like inference in DeepSeek harness settings with search bar, category tabs All/Frontier/Reasoning/Free/Custom/Local/SOTA, model cards FREE/FRONTIER/REASONING badges, custom input any frontier or your own fine-tuned via OpenRouter/NVIDIA NIM/OpenAI-compatible. Free tier: OpenRouter free DeepSeek R1 free, NVIDIA NIM free Llama 3.3, Gemini free tier, local free All-MiniLM/BGE Large.

## 14. Model-Agnostic Architecture — Accepted, Already Implemented

STEMMA must not become dependent on particular commercial LLM. Ingestion contract should operate at interface level Document → Extraction interface → Structured proposal. Model adapter can provide Gemini Claude GPT Qwen local models future models. Canonical STEMMA layer should not care which model generated proposal. Model identity and version should remain part of provenance.

Implementation: Already have model selector like DeepSeek harness with provider abstraction `webapp/providers.py` supporting deterministic (no LLM), antigravity (official local agent SDK then CLI uses local Google AI Pro session no Gemini API key), gemini_api, vertex_ai, openai_compatible custom bridge/tunnel, openrouter frontier DeepSeek Claude GPT Gemini Llama, nvidia NIM free. Canonical layer doesn't care. `workflow/config/llm.json` git-ignored API key stays git-ignored.

## 15. Reproducibility Requirement — Accepted with content_hash Amendment

AI extraction must be reproducible to extent technically possible. Record source hash, document version, pipeline version, schema version, model provider, model identifier, model version, prompt version, extraction configuration, timestamp, candidate output, verification result. If same source processed again with new model, distinguish old vs new extraction rather than silently overwriting history.

**Amendment:** Reproducibility via content_hash, separated workflow audit vs canonical export:
- source hash sha256 of original PDF
- document version workflow meta created_at
- pipeline version schema/VERSION.yaml + template-registry version
- schema version from VERSION.yaml
- model provider identifier version from llm config
- prompt version from providers.py
- extraction configuration max_tokens top_k domain filter
- candidate output proposal yaml
- verification result deterministic + independent model
All recorded in workflow/audit/audit.jsonl with content_hash deterministic no wall-clock in canonical export.

## 16. Important Architectural Rule — Accepted

Do NOT implement document → LLM → STEMMA. Implement document → evidence → AI semantic interpretation → candidate knowledge → verification → conflict analysis → human decision → STEMMA. Distinction is fundamental.

## 17. Initial Implementation Scope — Vertical Slice — Accepted

For first implementation build vertical slice rather than attempting every STEM domain. Choose small representative corpus containing textbook material, scientific paper, equations, tables, quantitative measurements, conditional statements, multiple related concepts, at least one deliberately conflicting source. Demonstrate source → deterministic evidence extraction → LLM semantic extraction → structured proposal → deterministic validation → independent verification → conflict detection → human review → canonical STEMMA record. Tests must prove each transition. Do not consider feature implemented merely because LLM successfully produced plausible YAML.

**Amendment:** Vertical slice corpus for mediocre all-domain:
- SI Brochure 9th ed. PDF — deterministic scales no LLM exact SI constants
- HRW 12th Ch1-5 — mechanics measurement-units deterministic regex
- Campbell Biology Ch8 Photosynthesis — semantic claim extraction with conditions temperature constant light etc.
- Atkins Physical Chemistry Ch1 Ideal Gas — conditions temperature constant model ideal gas quantitative P=10 vs P=12 conflict deliberately
- CLRS Ch2 Sorting — entity identification algorithm relationship extraction
- Carroll Ostlie Ch — conflicting source for same property to test conflict detection

Covers textbook material scientific paper equations tables quantitative measurements conditional statements multiple related concepts at least one deliberately conflicting source.

## 18. Success Criteria — Accepted with Extensions

Implementation should demonstrate STEMMA can:

1. Preserve exact source evidence.
2. Extract semantic scientific claims from prose.
3. Extract entities and relationships.
4. Preserve conditions and scope.
5. Extract quantitative information.
6. Link every candidate claim to evidence.
7. Validate generated structures deterministically.
8. Independently verify semantic claims.
9. Detect contradictory source claims.
10. Prevent unverified AI output from entering canonical storage.
11. Preserve model and pipeline provenance.
12. Reprocess sources without destroying historical extraction results.
13. Produce deterministic canonical exports from accepted STEMMA data.

**Amendment:** Add:
14. Preserve content_hash versioning deterministic export byte-identical on rerun no wall-clock in canonical export
15. Prevent embeddings in canonical content/ embeddings are derived only in exports/
16. Explorer clean small nodes thin lines manual legend centered zoom 8 domains
17. Strong CI nothing bad gets pushed/merged both GitHub Actions and locally pre-commit pre-push hooks

## 19. Final Design Principle — Accepted

STEMMA should not be designed around assumption "AI knows STEM." It should be designed around assumption **AI is extremely capable at interpreting semantic content of STEM sources, but its interpretations are untrusted computational evidence until independently verified.** Therefore AI aggressive extraction → CANDIDATES → deterministic+AI verification → EVIDENCE → conflict resolution → HUMAN AUTHORITY → CANONICAL STEMMA. This preserves advantages of modern frontier models without allowing probabilistic generation to become source of truth for STEM kernel.

## Implementation Status

- R1 NOW: 1 entity metre via HITL, template-registry v2.0.0 8 domains 97 subdomains 12 entity types, embedding-registry v1.0.0 11 models, consumer-registry v1.0.0 4 consumers, pdf_ingest_primary.py comprehensive, webapp with HITL model selector like DeepSeek harness RAG playground consumer export, explorer clean 8 domains, guideline docs/GUIDELINE-EMBEDDER-RAG.md 81KB, strong CI 10 jobs all-green, verify_strong.py strong verification, Makefile, pre-commit hooks, install_hooks.py
- R2: Semantic extraction pipeline — semantic_extract.py, entity_resolution.py enhanced, verify_claim.py independent verification, conflict_analysis.py explicit conflict detection, proposal_generate.py evidence first-class, llm-registry.yaml model roles, semantic-claim.schema.json, evidence windows, normalization, license gate, manifest, document vision
- R3: Production RAG conflict-aware retrieval, evaluation dataset with deliberately conflicting sources, citation coverage, hosted vector store Qdrant/Pinecone, consistent architecture across all consumers via guideline

## How to Use

```bash
# Check registries comprehensive
python3 scripts/pdf_ingest_primary.py --check-registries

# PDF primary ingestion
python3 scripts/pdf_ingest_primary.py --pdf path/to/SI-Brochure.pdf --provider deterministic
python3 scripts/pdf_ingest_primary.py --pdf path/to/Campbell-Biology.pdf --provider openrouter --model deepseek/deepseek-r1:free

# Semantic extraction
python3 scripts/semantic_extract.py --doc-id <id> --model deepseek/deepseek-r1:free

# Entity resolution
python3 scripts/entity_resolution.py --claim claims.json

# Independent verification
python3 scripts/verify_claim.py --claim claims.json --verifier-model anthropic/claude-3.5-sonnet

# Conflict analysis
python3 scripts/conflict_analysis.py --claims claims.json

# Proposal generation
python3 scripts/proposal_generate.py --doc-id <id>

# HITL
python3 scripts/hitl_check.py --check-workflow

# Validate + strong verify
python3 scripts/validate.py
python3 scripts/verify_all.py
python3 scripts/verify_strong.py --quick
make strong-verify
```

## Related Docs

- docs/PIPELINES.md — beginning no legacy HITL PDF primary
- docs/ARCHITECTURE.md — explicit separation canonical never contains embeddings/RAG + can be out of STEMMA + whose job CONSUMER's job
- docs/GUIDELINE-EMBEDDER-RAG.md — how to build embedder and RAG that imports from STEMMA consistently
- docs/TESTING.md — verification chain
- docs/IMPLEMENTATION-STATUS.md — 1 entity metre via HITL
- Makefile — strong targets
- .github/workflows/ci.yml — strong CI 10 jobs all-green
