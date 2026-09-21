# STEMMA — System Architecture (COMPREHENSIVE ALL-STEM, MEDIOCRE COVERAGE, HITL, PDF PRIMARY, EVOLVABLE, FRONTIER, EMBEDDINGS, RAG, CONSUMER EXPORT)

**Status:** Authoritative, comprehensive all-STEM mediocre coverage (not minimal physics). Now 1 entity (metre) via PDF primary ingestion with HITL, deterministic scales, evolvable templates, model selector like DeepSeek harness (local + frontier models), embeddings, RAG, consumer export for LearningHub, PROFESSOR-J. Old 74 entities archived to archive/beginning-74-entities/. Will grow to mediocre coverage across 8 domains: physics, chemistry, biology, earth-science, astronomy, computer-science, engineering, mathematics.

## 1. System in one picture — comprehensive all-STEM

```
CANONICAL LAYER (source of truth, in git, only after HITL)
  content/<domain>/**/*.md (1 entity now metre via HITL, will grow to mediocre all-domain: physics, chemistry, biology, earth-science, astronomy, computer-science, engineering, mathematics — each with governed_by + source_refs + writer human:* + link + exact definition)
  connections/*.yaml (0 now, will grow, 8 relations only, mandatory evidence source_ref+locator+description)
  sources/*.yaml (3 canonical records with url/isbn + writer, dual verification)

INGESTION LAYER (PRIMARY — PDF, deterministic scales, evolvable, git-ignored workflow/)
  workflow/documents/<doc_id>/ (PDF uploads: SI Brochure 9th ed., HRW 12th ed., Campbell Biology, CLRS, Atkins, Carroll Astrophysics, custom PDFs for all 8 domains)
  workflow/extraction/<doc_id>.txt (deterministic poppler/tesseract, no LLM)
  workflow/candidates/<doc_id>/<slug>.md (markdown preview — deterministic templates from schema/template-registry.yaml v2.0.0 regex + exact constants for all domains — scales to any domain, OR AI draft with frontier model when PDF missing exact definition)
  workflow/proposals/<slug>.md (human-approved markdown after explicit edit)
  workflow/audit/audit.jsonl (HITL audit: candidate_edited by human:curator.001, proposal_staged, etc.)
  workflow/meta/<doc_id>.json (document metadata)

GATE (deterministic, no LLM, includes HITL)
  scripts/validate.py (schema, identity, references, registry)
  scripts/physics_core_profile_check.py (mandatory source_kind, source, writer human:*, link, retrieved_at, source_refs>=1, evidence>=1, historical for law canonical)
  scripts/physics_governing_check.py (every physics entity governed by law from registry, subdomain matches law, no self-governance, deterministic)
  scripts/hitl_check.py (verifies human edited markdown before canonical — audit trail candidate_edited by human:*, writer human:*, markdown explicit)
  scripts/evolvable_template.py (deterministic extraction via regex + exact SI constants, scales to all 8 domains, evolvable, LLM fallback only when PDF missing exact)
  scripts/pdf_ingest_primary.py (primary feeder CLI)
  scripts/embed.py (NEW: embedding generator — local free BGE, All-MiniLM + frontier OpenAI text-embedding-3-large, Cohere, Gemini, NVIDIA NV-Embed, model selector like DeepSeek harness (local + frontier models))
  scripts/rag.py (NEW: RAG system — vector search + LLM generation with model selector like DeepSeek harness (local + frontier models), for LearningHub, PROFESSOR-J)
  scripts/export_consumers.py (NEW: consumer-specific export for LearningHub, PROFESSOR-J, general, explorer)

DERIVED LAYER (regenerable, deterministic, content-hash, no wall clock)
  exports/knowledge.json (v2.1.0, deterministic, content-hash, 1 entity now, will grow to mediocre all-domain)
  exports/knowledge.*.json (review-aware: all, canonical, reviewed, trusted)
  exports/embeddings.jsonl (NEW: embeddings per entity with model id, dimensions, vector, content_hash — deterministic, versioned)
  exports/vector_store/ (NEW: FAISS/Chroma/Qdrant local vector store — meta.json + vectors.npy + ids.json, versioned via content_hash + model id, for RAG)
  exports/consumers/<consumer>/knowledge.<consumer>.json (NEW: consumer-specific filtered exports — LearningHub canonical physics/chem/bio/math, PROFESSOR-J reviewed all domains, etc.)
  exports/openapi.yaml (NEW: OpenAPI schema from schema/api.yaml)
  reports/* (validation-report, curation-status)

CONSUMERS + EXPORT MECHANISM + RAG
  explorer/ (reads export only, clean 3D small nodes 0.32-0.5, thin lines 0.15, legend hidden manual only, zoom centered tight 32-65 centroid, now with domain filter for 8 domains)
  adapters/python/ (reads export only, now v0.2.0 with embeddings + RAG + consumer export endpoints: /v2/embeddings, /v2/rag/search, /v2/rag/query POST, /v2/export?consumer=..., /openapi.yaml)
  webapp/ (ingestion & review UI + RAG playground, PDF primary, deterministic draft no LLM scales + AI draft with model selector like DeepSeek harness (local + frontier models), markdown preview textarea + checklist + Save human edit HITL, NEW: RAG playground with embedding model selector like DeepSeek harness (local + frontier models), vector search, LLM generation with frontier models)
  LearningHub (consumer: canonical physics/chem/bio/math, high-quality embeddings OpenAI text-embedding-3-large, REST API /v2/entities, /v2/search, /v2/rag/query, /v2/embeddings)
  PROFESSOR-J (consumer: reviewed all 8 domains mediocre, offline SOTA embeddings BGE Large, local vector store FAISS, RAG with DeepSeek R1 free, all endpoints)

EMBEDDING + RAG LAYER (NEW — answers your question: do we need embedding model and RAG?)
  YES — embedding model needed for RAG and consumer export, RAG system needed in STEMMA as knowledge foundation
  embedding-registry.yaml (NEW: 12 models — local free All-MiniLM 384 dim fast, MPNet 768, BGE Large SOTA 1024, E5 Large 1024, BGE Small 384 + frontier API OpenAI text-embedding-3-large 3072, text-embedding-3-small 1536, Cohere embed-v3 1024, Gemini text-embedding-004 768 free, NVIDIA nv-embed-v1 SOTA 4096, model selector like DeepSeek harness (local + frontier models) with search, categories Frontier/Free/Local/SOTA, custom model input)
  consumer-registry.yaml (NEW: 4 consumers — LearningHub, PROFESSOR-J, general, explorer — each with domains, review_policy, entity_types, export_formats, embedding_model, api_access, rag config)
  api.yaml (NEW: OpenAPI 3.0.3 schema — /v2/stats, /v2/entities, /v2/connections, /v2/search, /v2/embeddings, /v2/rag/search, /v2/rag/query POST, /v2/export, /openapi.yaml)
  embed.py generates embeddings deterministically (same knowledge.json content_hash + model id → same embeddings, content_hash versioned)
  rag.py does vector search (cosine similarity) + builds context with definitions + connections + sources + calls LLM model selector like DeepSeek harness (local + frontier models: DeepSeek R1 free, Claude 3.5 Sonnet, GPT-4o, Gemini 2.5 Pro, Llama 3.3 70B free, custom) to answer with citations
```

## 2. Components — Comprehensive All-STEM Mediocre, Not Minimal Physics

| Component | Path | Role | Scaling |
|---|---|---|---|
| Entity corpus | `content/<domain>/` | 1 entity now metre via HITL, will grow to mediocre all 8 domains: physics (mechanics, measurement-units, electricity-magnetism, thermal, waves-optics, atomic-nuclear, quantum, relativity, fluid, thermodynamics, optics, condensed), chemistry (general, organic, inorganic, physical, analytical, biochem, polymer, electro, quantum, materials, environmental), biology (general, molecular, cell, genetics, evolution, ecology, physiology, microbiology, neuroscience, anatomy, botany, zoology, immunology, developmental), earth-science (geology, meteorology, oceanography, environmental, geography, climatology, seismology, hydrology, atmospheric, mineralogy), astronomy (astrophysics, cosmology, planetary, stellar, galactic, observational, astrobiology, celestial-mechanics), computer-science (algorithms, data-structures, programming-languages, software-engineering, AI, ML, databases, networks, cybersecurity, OS, theory, architecture, graphics, compilers, distributed), engineering (mechanical, electrical, civil, chemical, aerospace, biomedical, industrial, environmental, materials, software, nuclear, automotive, robotics), mathematics (algebra, geometry, calculus, statistics, probability, number-theory, discrete, linear-algebra, differential-equations, topology, analysis, logic, combinatorics, optimization) — each with governed_by + exact definition | Scales via evolvable templates v2.0.0 |
| Assertion corpus | `connections/` | 0 now, will grow, 8 relations only, mandatory evidence | Scales |
| Source records | `sources/` | 3 records, dual verification, url/isbn | Scales |
| Template registry | `schema/template-registry.yaml` | v2.0.0 comprehensive all-STEM, 8 domains, 12 entity types (concept, quantity, unit, constant, law, principle, theorem, equation, process, structure, algorithm, material), regex rules, exact SI constants, authoritative sources SI Brochure, IUPAC, CRC, HRW, Campbell, CLRS, Atkins, Carroll, embedding config with 8 models | Evolvable without code change, add domain via --evolve |
| Embedding registry | `schema/embedding-registry.yaml` | NEW v1.0.0: 12 models — local free All-MiniLM 384 fast, MPNet 768 quality, BGE Large SOTA 1024 best for RAG, E5 Large 1024 retrieval, BGE Small 384 fast + frontier API OpenAI text-embedding-3-large 3072 best quality, text-embedding-3-small 1536 fast frontier, Ada 002 legacy, Cohere embed-v3 1024, Gemini text-embedding-004 768 free tier, NVIDIA nv-embed-v1 SOTA 4096 free via NIM — model selector like DeepSeek harness (local + frontier models), deterministic content_hash, chunking entity strategy | Scales, deterministic |
| Consumer registry | `schema/consumer-registry.yaml` | NEW v1.0.0: 4 consumers — LearningHub (canonical physics/chem/bio/math, OpenAI text-embedding-3-large, RAG GPT-4o, /v2/entities /v2/search /v2/rag/query), PROFESSOR-J (reviewed all 8 domains mediocre, BGE Large offline SOTA, FAISS vector store, RAG DeepSeek R1 free, all endpoints), general (all domains, All-MiniLM fast local), explorer (3D graph) — export mechanisms file/api/sdk, RAG flow | Defines consumer needs |
| API schema | `schema/api.yaml` | NEW OpenAPI 3.0.3: /v2/stats, /v2/entities, /v2/connections, /v2/search, /v2/embeddings?model=..., /v2/rag/search?q=...&top_k=..., /v2/rag/query POST, /v2/export?consumer=..., /openapi.yaml — for LearningHub, PROFESSOR-J | Versioned, deterministic |
| Governing registry | `schema/physics-governing-registry.yaml` | 23 laws, what goes where, deterministic placement | Deterministic |
| Schemas | `schema/*.schema.json` | v1.2.0 contracts, concept, connection, source | Versioned |
| Gate | `scripts/validate.py` | Schema + identity + refs | Deterministic |
| Physics checks | `physics_core_profile_check.py`, `physics_governing_check.py` | Deterministic, mandatory fields | Deterministic |
| HITL check | `hitl_check.py` | Human edited markdown before canonical, audit trail, writer human:* | Enforces HITL |
| Evolvable template | `evolvable_template.py` | Deterministic extraction regex + exact SI constants, scales to all 8 domains, evolvable, LLM fallback only when PDF missing exact | Scales, evolvable |
| Embedding generator | `scripts/embed.py` | NEW: generates embeddings for entities, supports local free + frontier API, model selector like DeepSeek harness (local + frontier models), deterministic fake embeddings for demo if torch not installed, outputs embeddings.jsonl + vector_store/ meta.json + vectors.npy + ids.json, content_hash versioned, for RAG and consumer export | Deterministic, scales |
| RAG system | `scripts/rag.py` | NEW: vector search (cosine similarity) + context building (definitions + connections + sources) + LLM generation with model selector like DeepSeek harness (local + frontier models: DeepSeek R1 free, Claude 3.5 Sonnet, GPT-4o, Gemini 2.5 Pro, Llama 3.3, custom via OpenRouter), consumer-specific models, for LearningHub, PROFESSOR-J, answers your question: YES we need RAG in STEMMA as knowledge foundation for consumers | RAG with citations |
| Consumer export | `scripts/export_consumers.py` | NEW: filters knowledge.json by consumer (domains, review_policy, entity_types) and generates consumer-specific exports in exports/consumers/<consumer>/, plus embeddings via embed.py, for LearningHub, PROFESSOR-J | Consumer-specific |
| PDF primary | `pdf_ingest_primary.py` | Primary feeder CLI, wraps ingest.py + AI draft | Primary |
| Webapp | `webapp/` | Ingestion & review UI + RAG playground, PDF primary, deterministic draft no LLM scales + AI draft with model selector like DeepSeek harness (local + frontier models) with search, categories Frontier/Reasoning/Free/Custom, 25 frontier models), markdown preview textarea + checklist + Save human edit HITL, NEW: RAG playground with embedding model selector like DeepSeek harness (local + frontier models: local free BGE, All-MiniLM + frontier OpenAI, Cohere, Gemini, NVIDIA), vector search, LLM generation with citations | Scales, frontier, RAG |
| Explorer | `explorer/` | 3D viewer, clean small nodes 0.32-0.5, thin lines 0.15, legend hidden manual only, zoom centered tight 32-65 centroid, now domain filter for 8 domains | Clean |
| Adapter | `adapters/python/` | v0.2.0 reads export only, now with embeddings + RAG + consumer export endpoints: /v2/embeddings?model=...&id=...&domain=..., /v2/rag/search?q=...&top_k=..., POST /v2/rag/query, /v2/export?consumer=..., /openapi.yaml, for LearningHub, PROFESSOR-J | Enhanced |

## 3. Invariants — Comprehensive All-STEM, HITL, Evolvable, Frontier, Embeddings, RAG

1. No legacy — this is beginning comprehensive all-STEM mediocre, old 74 entities archived to archive/beginning-74-entities/, now 1 entity via HITL, will grow to mediocre coverage across 8 domains
2. PDF ingestion PRIMARY, direct LLM addition SECONDARY, both require HITL before canonical — no entity without human explicitly editing markdown
3. Every entity has standard scientific definition with exact value if applicable + reference link + source_refs + external_ids triple verification (e.g., metre = light path 1/299,792,458 s, c=299,792,458 m/s exact, agreed per BIPM 2019; chemical element per IUPAC Gold Book; algorithm per CLRS)
4. Every entity has dual verification: embedded provenance (writer human:*, link, retrieved_at, source_kind, source with exact) + canonical source record in sources/ with url/doi/isbn
5. Every connection has evidence >=1 with source_ref + locator + description
6. No related_to in physics, only 8 adopted relations
7. History timeline optional draft, mandatory law/model/equation when human_reviewed/canonical
8. Deterministic scales: same input → same output any time, no LLM reasoning for placement, uses template-registry.yaml v2.0.0 regex + exact constants, no cost, no hallucination, scales to 1000s PDFs, 8 domains
9. Evolvable: add new domain (e.g., medicine, economics) via `python3 scripts/evolvable_template.py --evolve --new-domain medicine` without code change, templates in YAML v2.0.0
10. LLM fallback only when PDF missing exact definition — then frontier model (DeepSeek R1 free, Claude 3.5 Sonnet, GPT-4o, Gemini 2.5 Pro, Llama 3.3) or custom model via OpenRouter/NVIDIA NIM/OpenAI-compatible, selector like DeepSeek harness (search, categories Frontier/Reasoning/Free/Custom, 25 models), even LLM requires HITL human edit before canonical
11. HITL enforcement: workflow/audit/audit.jsonl must contain candidate_edited by human:* after AI draft, writer must be human:*, markdown file explicit edit, hitl_check.py fails if bypassed
12. Markdown explicit: AI shows data in markdown preview (textarea + rendered + checklist), human explicitly edits markdown file for easy verification
13. Deterministic, content-hash stamped, no wall clock, versioned exports v2.1.0, embeddings versioned via content_hash + model id
14. Embeddings: YES needed — embedding model generates vectors for entities for RAG and consumer export, deterministic same content_hash + model → same embeddings, supports local free (All-MiniLM 384 fast, BGE Large SOTA 1024) + frontier API (OpenAI text-embedding-3-large 3072 best quality, NVIDIA nv-embed-v1 SOTA 4096 free via NIM), model selector like DeepSeek harness (local + frontier models), stored in exports/embeddings.jsonl + vector_store/ FAISS
15. RAG: YES needed in STEMMA — STEMMA is knowledge foundation, RAG is how consumers like LearningHub, PROFESSOR-J use it, without RAG STEMMA is static JSON, with RAG it's queryable knowledge with citations, flow: question → embedding → vector search top_k → context with definitions + connections + sources → LLM model selector like DeepSeek harness (local + frontier models) → answer with citations (source_refs + link)
16. Consumer export: YES needed — export mechanism via file (exports/knowledge.json, embeddings.jsonl, vector_store/, consumers/<consumer>/), API (adapter server /v2/entities, /v2/embeddings, /v2/rag/search, /v2/rag/query POST, /v2/export?consumer=..., /openapi.yaml with OpenAPI schema), SDK (Python adapter Stemma.from_file + StemmaRAG), for LearningHub (canonical physics/chem/bio/math, OpenAI embeddings, GPT-4o RAG), PROFESSOR-J (reviewed all 8 domains mediocre, BGE Large offline SOTA, FAISS, DeepSeek R1 free RAG), general, explorer


## 3.5 Explicit Separation — Canonical vs Derived vs Consumer (NEW 2026-09-21 — Answers: Does STEMMA itself need embeddings/RAG?)

**User insight:** "STEMMA in itself doesn't need them!? But again STEMMA alone existence is useless if we can't use it, so building RAG pipeline is inevitable here!?"

**Answer: YES, exactly right — clean separation:**

### Layer 1: CANONICAL — STEMMA itself, source of truth, in git, only after HITL, NO embeddings/RAG

- **Paths:** `content/<domain>/**/*.md` (1 entity now metre via HITL, will be 400-800 mediocre across 8 domains), `connections/*.yaml` (0 now, will be 500+), `sources/*.yaml` (3 now, will be 20+), `schema/` (JSON Schemas, relation-registry, template-registry v2.0.0, embedding-registry v1.0.0, consumer-registry v1.0.0, api.yaml, governing-registry)
- **Contains:** Only Markdown + YAML with exact definitions, dual verification (embedded provenance writer human:* + canonical source record with url/doi/isbn), governed_by, history timeline, 8 relations only, evidence mandatory source_ref+locator+description, triple verification link+source_refs+external_ids
- **Does NOT contain:** Embeddings, vectors, vector stores, RAG artifacts, FAISS indexes, .npy files, embeddings.jsonl — NEVER in content/, connections/, sources/
- **Why:** Embeddings are model-specific, non-deterministic (different models give different vectors), not time-invariant, would pollute canonical with 384/1024/3072 dim floats, would make content/ non-human-reviewable, would violate "no embeddings, database as source of truth" invariant for canonical (previously in ROADMAP Not on roadmap: embeddings, database as source of truth — meant canonical, not derived)
- **Validation:** `scripts/validate.py` NEVER checks embeddings, only checks schema, identity, references, registry, mandatory fields source_kind, source, writer human:*, link, retrieved_at, source_refs>=1, evidence>=1, historical for law canonical, no forbidden fields — deterministic, no LLM, no embeddings
- **Example:** `content/physics/measurement-units/metre.md` has definition "The metre (symbol: m) is base unit of length... Exact: c=299,792,458 m/s. Agreed per BIPM SI Brochure 9th ed. 2019" + provenance + source_refs + external_ids wd, but NO vector, NO embedding

### Layer 2: DERIVED — regenerable from canonical, deterministic, content-hash, no wall clock, in exports/, YES embeddings here but as derived

- **Paths:** `exports/knowledge.json` v2.1.0 deterministic content-hash sha256:2c007..., `exports/knowledge.*.json` review-aware, `exports/embeddings.jsonl` (NEW: embeddings per entity with model id, dimensions, vector, content, content_hash), `exports/vector_store/` (NEW: FAISS meta.json + vectors.npy + ids.json, versioned via content_hash + model id), `exports/consumers/<consumer>/knowledge.<consumer>.json` (NEW: filtered by domains/review_policy), `exports/openapi.yaml`, `reports/`
- **Contains:** YES embeddings, vectors, vector stores, FAISS indexes, but as DERIVED artifacts, not canonical, regenerable from knowledge.json + embedding model
- **Deterministic:** Same knowledge.json content_hash + model id → same embeddings, content_hash versioned, e.g., embedding record content_hash = sha256(text + model_id + knowledge.json content_hash)[:16], vector_store meta.json content_hash same as knowledge.json, created_at deterministic "no wall clock", version 1.0.0, type faiss, index_type flat, metric cosine, batch_size 32 normalize true, chunking entity strategy max_tokens 512 overlap 50
- **Regenerable:** If you delete exports/, you can regenerate via `python3 scripts/validate.py` (generates knowledge.json) + `python3 scripts/embed.py --model BAAI/bge-large-en-v1.5 --output exports/embeddings.jsonl --vector-store exports/vector_store/` (generates embeddings.jsonl + vector_store/)
- **Versioned:** Via content_hash + model id, deterministic, no wall clock, like compiled binary from source code
- **Validation:** `scripts/verify_all.py` checks embeddings existence as INFO, not FAIL — because embeddings are derived, optional, recommended for consumers but not required for canonical validity. If embeddings missing, prints INFO "run python3 scripts/embed.py --model ...", doesn't fail gate. Gate decides canonical validity, not derived completeness.

### Layer 3: CONSUMER + RAG PIPELINE — how LearningHub, PROFESSOR-J use STEMMA, YES RAG here but as consumer mechanism

- **Paths:** `scripts/embed.py` (embedding generator, local free All-MiniLM/BGE Large + frontier OpenAI Large/NVIDIA NV-Embed, model selector like DeepSeek harness (local + frontier models)), `scripts/rag.py` (RAG system, vector search cosine similarity + context building + LLM generation with model selector like DeepSeek harness (local + frontier models: DeepSeek R1 free, Claude 3.5 Sonnet, GPT-4o, Gemini 2.5 Pro, Llama 3.3, custom) + citations), `scripts/export_consumers.py` (consumer-specific exports), `adapters/python/` v0.2.0 (SDK + CLI + local JSON API with /v2/embeddings, /v2/rag/search, POST /v2/rag/query, /v2/export, /openapi.yaml), `webapp/` (ingestion/review UI + RAG playground with embedding model selector + LLM selector + domain filter + citations), `explorer/` (3D graph), `schema/embedding-registry.yaml` v1.0.0 12 models, `schema/consumer-registry.yaml` v1.0.0 4 consumers, `schema/api.yaml` OpenAPI 3.0.3
- **Contains:** YES RAG pipeline, but as CONSUMER mechanism, not canonical. Without RAG, STEMMA is static JSON, useless for student queries. With RAG, queryable knowledge with citations, grounded answers.
- **Flow:** User question → embedding via embedding model → vector search top_k cosine similarity over FAISS → context definitions + connections + sources + source_refs + links → LLM prompt context + question → answer with citations source_refs + link → {question, answer, citations, retrieved_entities, model_used, embedding_model_used, content_hash}
- **Why inevitable:** STEMMA alone existence is useless if we can't use it, so building RAG pipeline is inevitable here — LearningHub needs to answer "What is Newton's second law?" with citations, PROFESSOR-J needs to answer "Explain photosynthesis" across 8 domains mediocre, offline SOTA BGE Large + FAISS + DeepSeek R1 free reasoning. Without RAG, consumers would build own RAG from scratch, duplicating work, inconsistent retrieval. Therefore RAG pipeline inevitable, but as consumer layer, not canonical.
- **Validation:** `scripts/rag.py --search` and `--question` are INFO checks in verify_all.py, not FAIL — RAG is consumer mechanism, optional for canonical validity, but recommended for usability

### Invariants for separation

1. **Canonical never contains embeddings, vectors, or RAG artifacts** — no .npy, no embeddings.jsonl, no vector_store/ in content/, connections/, sources/, schema/ (except registries that define embedding models, not vectors)
2. **Embeddings and vector stores live only in exports/ as derived artifacts** — regenerable via embed.py, versioned via content_hash + model id, deterministic, no wall clock, batch_size 32 normalize true
3. **RAG lives only in scripts/ and adapters/ and webapp/ as consumer mechanism** — not in canonical, optional for canonical validity, but inevitable for usability
4. **Gate validate.py never checks embeddings** — only checks canonical schema, identity, references, mandatory fields, no embeddings
5. **verify_all.py checks embeddings existence as INFO, not FAIL** — prints OK if exists, INFO "run embed.py" if missing, doesn't fail gate. Gate decides canonical validity, not derived completeness. Same for RAG and consumer export — INFO, not FAIL.
6. **Previously "Not on roadmap: embeddings, database as source of truth" meant canonical, not derived** — now embeddings ARE in derived + consumer layers, which IS on roadmap (R1 comprehensive all-STEM mediocre + embeddings + RAG + consumer export)

### Why this answers user's question

- **Does STEMMA itself need embeddings/RAG? NO** — canonical layer valid without embeddings, without RAG, only Markdown+YAML, deterministic, HITL, versioned, content-hash
- **Is STEMMA alone useless if we can't use it? YES** — static JSON alone not queryable via natural language, no semantic search, no citations for LearningHub, PROFESSOR-J
- **Is building RAG pipeline inevitable here? YES** — as derived + consumer layer, inevitable for usability, but cleanly separated from canonical, optional for canonical validity, deterministic, versioned, with model selector like DeepSeek harness (local + frontier models)



## 3.6 Can Embedding and RAG Be Out of STEMMA? YES — As Connection Layer, Not Containing Whole STEMMA (NEW 2026-09-21 — Answers user's question)

**User question:** "Can i actually have embedding and RAG out of STEMMA!? How do they connect then?? Embedding and RAG doesn't contain the whole STEMMA right!? its just a connection layer!?"

**Answer: YES, exactly right — embedding and RAG can be out of STEMMA, they're just connection layer, not containing whole STEMMA, they connect via exports/knowledge.json + API + SDK + content_hash.**

### STEMMA itself is knowledge foundation, not embedding/RAG

- **STEMMA canonical:** content/<domain>/**/*.md (Markdown+YAML with exact definitions, dual verification, governed_by, history), connections/*.yaml (8 relations, evidence mandatory), sources/*.yaml (url/doi/isbn + writer human:*), schema/ (JSON Schemas, registries) — NO embeddings, NO vectors, NO RAG — pure knowledge, version-controlled, machine-readable, human-reviewable, deterministic, content-hash, HITL
- **Whole STEMMA:** This canonical layer IS whole STEMMA — all concepts, quantities, laws, models, relationships, with provenance, source_refs, external_ids, historical timeline — e.g., metre defined as light path 1/299,792,458 s Exact c=299,792,458 m/s Agreed per BIPM 2019 + writer human:curator.001 + link bipm.org + source_refs + wd Q11573

### Embedding and RAG are connection layer, not whole STEMMA

- **Embedding:** Does NOT contain whole STEMMA — it contains vectors DERIVED from STEMMA definitions, e.g., for metre: chunk "Metre (stemma:phys.metre) Domain: physics/measurement-units Type: unit Definition: The metre... Symbol: m..." → embedding model (All-MiniLM 384 dim or BGE Large 1024 SOTA or OpenAI Large 3072) → vector [0.12, -0.34, 0.56, ...] 384/1024/3072 floats — this vector is NOT whole STEMMA, it's just a semantic fingerprint of one entity's definition for similarity search — stored in exports/embeddings.jsonl as {entity_id, model, dimensions, vector, content, content_hash} — regenerable from knowledge.json + model id, deterministic same content_hash + model → same vector
- **Vector store:** Does NOT contain whole STEMMA — it contains FAISS index of vectors + ids.json + meta.json with model, dimensions, content_hash, entity_count, version — e.g., vectors.npy shape (1, 384) for 1 entity, ids.json ["stemma:phys.metre"] — this is just an index for fast cosine similarity search, NOT whole STEMMA, just connection layer for retrieval
- **RAG:** Does NOT contain whole STEMMA — it contains retrieval logic (embedding query → cosine similarity over FAISS → top_k entities with scores) + generation logic (build context with definitions + connections + sources + source_refs + links → LLM prompt → answer with citations) — e.g., question "What is Newton's second law?" → retrieves [force, mass, newtons-second-law] with scores → context → LLM DeepSeek R1 free → answer with citations entity_id + source_ref + link — this answer is grounded in STEMMA but RAG system itself doesn't contain whole STEMMA, only references entity IDs and definitions as context, whole STEMMA remains in content/
- **Therefore:** Embedding and RAG are connection layer — they connect user question to STEMMA knowledge via vectors + retrieval + LLM + citations, but don't contain whole STEMMA, just derived vectors + retrieval logic + generation logic that references STEMMA

### How do they connect then? Via exports/knowledge.json + API + SDK + content_hash — 3 ways

#### Option A: File-based connection (simplest, deterministic, no server)

- **STEMMA exports:** `exports/knowledge.json` v2.1.0 deterministic content-hash sha256:2c007..., contains entities, connections, sources, content_hash, versions — this IS the interface, whole STEMMA as JSON, versioned, deterministic, no wall clock
- **External RAG (out of STEMMA):** LearningHub or PROFESSOR-J or separate repo STEMMA-RAG copies `exports/knowledge.json` file (or git submodule, or download from release), then runs its own embedding generation externally:
  ```bash
  # In LearningHub repo, out of STEMMA
  cp ../STEMMA/exports/knowledge.json ./data/knowledge.json
  python3 -m stemma_rag.embed --input ./data/knowledge.json --model BAAI/bge-large-en-v1.5 --output ./data/embeddings.jsonl --vector-store ./data/vector_store/
  python3 -m stemma_rag.rag --question "What is Newton's second law?" --top-k 5 --model deepseek/deepseek-r1:free --vector-store ./data/vector_store/
  ```
- **Connection via content_hash:** External RAG checks `knowledge.json` content_hash — if content_hash changed (new entities added via HITL), recompute embeddings (same content_hash + model id → same embeddings, deterministic)
- **Does it contain whole STEMMA? NO** — external RAG's embeddings.jsonl + vector_store/ are derived from knowledge.json, but whole STEMMA remains in STEMMA repo's content/, connections/, sources/ — external RAG only has vectors + index + retrieval logic, not canonical Markdown+YAML

#### Option B: API-based connection (REST API, OpenAPI schema, for LearningHub, PROFESSOR-J production)

- **STEMMA API:** Adapter server v0.2.0 serves `exports/knowledge.json` via REST API with OpenAPI schema `schema/api.yaml` v2.1.0:
  - `GET /v2/stats` — stats entity_count, connection_count, source_count, content_hash, versions, domains 8
  - `GET /v2/entities?domain=physics&status=canonical&limit=1000` — list entities filtered by domain, subdomain, type, status
  - `GET /v2/entities/{id}` — get entity e.g., stemma:phys.metre
  - `GET /v2/search?q=force&domain=physics&limit=10` — keyword search
  - `GET /v2/embeddings?model=BAAI/bge-large-en-v1.5&limit=100` — embeddings if generated inside STEMMA, or external RAG can ignore and generate own
  - `GET /v2/rag/search?q=...&top_k=...` — vector search if embeddings inside STEMMA, or external RAG can implement own
  - `POST /v2/rag/query` — full RAG if inside STEMMA, or external RAG can implement own
  - `GET /v2/export?consumer=learninghub&format=json` — consumer-specific filtered export
  - `GET /openapi.yaml` — OpenAPI schema
- **External RAG (out of STEMMA):** LearningHub or PROFESSOR-J runs as separate service, calls STEMMA API to get entities, generates embeddings externally, builds vector store externally, serves RAG queries:
  ```python
  # In LearningHub, out of STEMMA, Python
  import requests
  # Get entities from STEMMA API
  resp = requests.get("http://stemma-api:8080/v2/entities?domain=physics&status=canonical&limit=1000")
  entities = resp.json()  # list of entities with id, name, domain, definition, provenance, source_refs
  content_hash = requests.get("http://stemma-api:8080/v2/stats").json()["content_hash"]
  # Generate embeddings externally (out of STEMMA)
  from sentence_transformers import SentenceTransformer
  model = SentenceTransformer("BAAI/bge-large-en-v1.5")
  texts = [f"{e['name']} ({e['id']}) Domain: {e['domain']} Definition: {e['definition']}" for e in entities]
  vectors = model.encode(texts, normalize_embeddings=True)
  # Build FAISS externally
  import faiss, numpy as np
  index = faiss.IndexFlatIP(1024)
  index.add(np.array(vectors, dtype='float32'))
  # RAG query externally
  query = "What is Newton's second law?"
  query_vec = model.encode([query], normalize_embeddings=True)
  scores, ids = index.search(np.array(query_vec, dtype='float32'), k=5)
  retrieved = [entities[i] for i in ids[0]]
  context = "\n".join([f"{e['name']} ({e['id']}): {e['definition'][:200]} Source: {e['provenance']['link']}" for e in retrieved])
  # Call LLM externally
  import openai
  answer = openai.ChatCompletion.create(model="gpt-4o", messages=[{"role": "user", "content": f"Context: {context}\n\nQuestion: {query}\nAnswer with citations:"}])
  print(answer.choices[0].message.content)  # with citations entity_id + source_ref + link
  ```
- **Connection via API + content_hash:** External RAG calls /v2/stats to get content_hash, if changed, recomputes embeddings, rebuilds FAISS — deterministic same content_hash + model → same embeddings
- **Does it contain whole STEMMA? NO** — external RAG's vectors + FAISS + retrieval + LLM are connection layer, whole STEMMA remains in STEMMA repo's content/ + API's knowledge.json, external RAG only references entity IDs and definitions as context

#### Option C: SDK-based connection (Python adapter, future TypeScript)

- **STEMMA SDK:** `adapters/python/` pip install ./adapters/python — provides Stemma class that loads knowledge.json and gives stable API without validator stack:
  ```python
  from stemma_adapter import Stemma
  stemma = Stemma.from_file("exports/knowledge.json")  # or from API via Stemma.from_api("http://localhost:8080")
  print(stemma.stats)  # entity_count, connection_count, content_hash
  print(stemma.search("force", domain="physics", limit=5))
  print(stemma.resolve("stemma:phys.metre"))
  ```
- **External RAG (out of STEMMA):** Uses SDK to load STEMMA, then builds its own embeddings/RAG out of STEMMA:
  ```python
  # Out of STEMMA, in LearningHub or STEMMA-RAG repo
  from stemma_adapter import Stemma
  import sys
  sys.path.insert(0, "../STEMMA-RAG")  # external RAG repo
  from stemma_rag import StemmaRAG  # external RAG, out of STEMMA

  stemma = Stemma.from_file("../STEMMA/exports/knowledge.json")
  rag = StemmaRAG.from_stemma(stemma, embedding_model="BAAI/bge-large-en-v1.5", vector_store_path="./data/vector_store/")
  # Generates embeddings out of STEMMA, builds FAISS out of STEMMA
  answer = rag.query("What is Newton's second law?", top_k=5, model="deepseek/deepseek-r1:free", consumer="learninghub")
  print(answer['answer'])  # with citations
  print(answer['citations'])  # entity_id + source_ref + link
  print(answer['retrieved_entities'])  # with scores
  ```
- **Connection via SDK + content_hash:** SDK exposes content_hash, external RAG checks if changed, recomputes embeddings
- **Does it contain whole STEMMA? NO** — external RAG's StemmaRAG contains vectors + FAISS + retrieval + LLM, but whole STEMMA remains in STEMMA repo, external RAG only uses SDK to load STEMMA as needed, connection layer

### Current implementation — optional derived layer inside STEMMA for convenience, but can be out

- **Currently:** We have `scripts/embed.py`, `scripts/rag.py`, `scripts/export_consumers.py`, `exports/embeddings.jsonl`, `exports/vector_store/`, `adapters/python/` v0.2.0 with /v2/embeddings, /v2/rag/search, POST /v2/rag/query, /v2/export, /openapi.yaml, `webapp/` RAG playground — all inside STEMMA repo, but as **derived + consumer layer**, not canonical, optional, INFO not FAIL in verify_all.py
- **Why inside for now:** Convenient for demo, for LearningHub, PROFESSOR-J to see how embedding/RAG connects to STEMMA, for testing retrieval precision + faithfulness + citation coverage, for webapp RAG playground with model selector like DeepSeek harness (local + frontier models)
- **Can be out:** YES, you can have embedding and RAG out of STEMMA — move `scripts/embed.py`, `rag.py`, `export_consumers.py` to separate repo `STEMMA-RAG` or to LearningHub/PROFESSOR-J repos, keep STEMMA core pure with only content/, connections/, sources/, schema/, validate.py — then STEMMA exports knowledge.json + API schema, external RAG consumes via file/API/SDK + content_hash + deterministic regeneration — this is cleaner separation, STEMMA remains pure knowledge foundation, embedding/RAG are external consumers, connection layer, not containing whole STEMMA

### Recommendation

- **Keep canonical pure:** content/, connections/, sources/, schema/ — NO embeddings, NO RAG, NO vectors — validate.py NEVER checks embeddings — this is STEMMA itself, whole STEMMA
- **Keep derived optional inside for convenience, but document that it can be out:** exports/knowledge.json, embeddings.jsonl, vector_store/, consumers/ — derived, regenerable, deterministic, content-hash, INFO not FAIL in verify_all.py — plus scripts/embed.py, rag.py, export_consumers.py as reference implementation of how external RAG can connect via file/API/SDK + content_hash
- **For production LearningHub, PROFESSOR-J:** Have embedding and RAG out of STEMMA — as separate service or part of LearningHub/PROFESSOR-J — that consumes STEMMA via file/API/SDK + content_hash, generates embeddings externally, builds vector store externally, serves RAG queries with citations — this way embedding/RAG doesn't contain whole STEMMA, just connection layer, whole STEMMA remains in STEMMA repo

**Therefore:** YES, you can have embedding and RAG out of STEMMA, they connect via exports/knowledge.json + API + SDK + content_hash, they don't contain whole STEMMA, they're just connection layer — current implementation keeps them inside as optional derived + consumer for convenience and demo, but can be moved out to separate repo or to LearningHub/PROFESSOR-J for cleaner separation.



## 3.7 Whose Job Is To Build Embedding and RAG? CONSUMER's Job, Not STEMMA's Job — STEMMA Provides Reference Implementation (NEW 2026-09-21 — Answers user's question)

**User question:** "whose job is to build embedding and RAG!? STEMMA or CONSUMER!?"

**Answer: CONSUMER's job, not STEMMA's job — STEMMA provides reference implementation as optional derived + consumer layer for convenience and demo, but production embedding and RAG is consumer's job (LearningHub, PROFESSOR-J, general, explorer).**

### STEMMA's job — knowledge foundation, pure, deterministic, HITL, versioned, content-hash, NO embeddings/RAG in canonical

- **Paths:** content/<domain>/**/*.md (Markdown+YAML with exact definitions, dual verification, governed_by, history), connections/*.yaml (8 relations, evidence mandatory), sources/*.yaml (url/doi/isbn + writer human:*), schema/ (JSON Schemas, relation-registry, template-registry v2.0.0 comprehensive all-STEM 8 domains 97 subdomains 12 entity types, embedding-registry v1.0.0 12 models, consumer-registry v1.0.0 4 consumers, api.yaml OpenAPI 3.0.3, governing-registry, VERSION.yaml single source), scripts/validate.py (NEVER checks embeddings, only canonical), scripts/physics_core_profile_check.py, physics_governing_check.py, hitl_check.py, evolvable_template.py, status_truth.py, verify_all.py (checks canonical as FAIL, checks embeddings/RAG/consumer export as INFO not FAIL)
- **Job:** Provide knowledge foundation — concepts, quantities, laws, models, relationships as version-controlled, machine-readable, human-reviewable data, with exact definitions, dual verification, governed_by, history, 8 relations, evidence, triple verification link+source_refs+external_ids, HITL enforced, deterministic, content-hash, versioned, no wall clock, no curriculum, no product, no embeddings, no RAG in canonical — pure knowledge, whole STEMMA is here
- **Exports:** exports/knowledge.json v2.1.0 deterministic content-hash sha256:2c007... (whole STEMMA as JSON, interface for consumers), exports/knowledge.*.json review-aware, exports/openapi.yaml OpenAPI schema, reports/ — these ARE STEMMA's job — provide deterministic versioned exports + API schema + SDK for consumers to use
- **Why NOT embedding/RAG in canonical:** Embeddings are model-specific (All-MiniLM 384 vs BGE Large 1024 vs OpenAI Large 3072 vs NVIDIA NV-Embed 4096 give different vectors), non-deterministic (different models give different vectors), not time-invariant, would pollute canonical with floats, make content/ non-human-reviewable, would require STEMMA to choose one embedding model, one vector store, one LLM, one top_k for all consumers — impossible, because consumers have different needs (LearningHub prefers OpenAI Large 3072 high quality for student queries, PROFESSOR-J prefers BGE Large SOTA 1024 offline capable for AI professor, general prefers All-MiniLM fast local) — therefore embedding and RAG cannot be one-size-fits-all in STEMMA, must be consumer's job

### CONSUMER's job — build embedding and RAG out of STEMMA as connection layer, not containing whole STEMMA

- **Who:** LearningHub, PROFESSOR-J, general, explorer, or separate repo STEMMA-RAG — consumers
- **Paths (out of STEMMA):** In LearningHub repo or PROFESSOR-J repo or separate STEMMA-RAG repo — data/knowledge.json (copied from STEMMA exports/knowledge.json), data/embeddings.jsonl (generated externally via embed.py out of STEMMA), data/vector_store/ FAISS meta.json + vectors.npy + ids.json (built externally out of STEMMA), rag.py (retrieval + generation logic out of STEMMA), or via API calls to STEMMA API /v2/entities, /v2/stats content_hash, /v2/search, etc., or via SDK Stemma.from_file() or from_api()
- **Job:** Build embedding and RAG out of STEMMA as connection layer, not containing whole STEMMA — generate vectors DERIVED from STEMMA definitions via embedding model (local free All-MiniLM/BGE Large + frontier OpenAI Large/NVIDIA NV-Embed, model selector like DeepSeek harness (local + frontier models)), build vector store FAISS/Chroma/Qdrant/Pinecone, serve RAG queries with retrieval + generation + citations — e.g., LearningHub: preferred_model OpenAI text-embedding-3-large 3072 fallback BGE Large, RAG top_k 5 model GPT-4o, endpoints /v2/stats /v2/entities /v2/search /v2/rag/query /v2/embeddings, rate limit 1000/hour api_key, example "What is Newton's second law?" → embedding OpenAI Large → vector search top 5 → context definitions + sources → GPT-4o → answer with citations; PROFESSOR-J: preferred_model BGE Large SOTA 1024 offline fallback All-MiniLM, RAG top_k 10 model DeepSeek R1 free fallback Claude 3.5 Sonnet/GPT-4o/Gemini 2.5 Pro, all endpoints, rate limit 10000/hour, example "Explain photosynthesis and its relation to cellular respiration" → embedding BGE Large → vector search top 10 across biology → context → DeepSeek R1 free → answer with citations
- **Why consumer's job:** Embedding model choice is consumer-specific (LearningHub high quality OpenAI Large 3072 vs PROFESSOR-J offline SOTA BGE Large 1024 vs general fast All-MiniLM 384), RAG top_k and LLM model choice is consumer-specific (LearningHub top_k 5 GPT-4o vs PROFESSOR-J top_k 10 DeepSeek R1 free), vector store type is consumer-specific (FAISS local deterministic vs Chroma vs Qdrant vs Pinecone cloud), domain filter is consumer-specific (LearningHub canonical physics/chem/bio/math vs PROFESSOR-J reviewed all 8 domains mediocre), review_policy is consumer-specific (LearningHub canonical vs PROFESSOR-J reviewed vs general all vs explorer all), rate limiting and auth are consumer-specific — therefore embedding and RAG must be consumer's job, not STEMMA's job, to fit each consumer's needs
- **Does it contain whole STEMMA? NO** — consumer's embeddings.jsonl + vector_store/ + RAG logic are connection layer, NOT whole STEMMA, whole STEMMA remains in STEMMA repo's content/, connections/, sources/, consumer only has vectors + index + retrieval + LLM that references entity IDs and definitions as context

### STEMMA provides reference implementation as optional derived + consumer layer for convenience and demo, but production embedding/RAG is consumer's job

- **Currently inside STEMMA for convenience and demo (optional, INFO not FAIL):** scripts/embed.py (embedding generator, local free + frontier, model selector like DeepSeek harness (local + frontier models), tries sentence-transformers if installed else fake deterministic hash-based for demo), scripts/rag.py (vector search cosine similarity + context building + LLM generation with model selector like DeepSeek harness (local + frontier models) + citations, consumer-specific models), scripts/export_consumers.py (consumer-specific filtered exports), exports/embeddings.jsonl (1 embeddings now deterministic fake for demo), exports/vector_store/ FAISS meta.json + vectors.json + ids.json versioned via content_hash + model id, exports/consumers/<consumer>/knowledge.<consumer>.json filtered, adapters/python/ v0.2.0 with /v2/embeddings, /v2/rag/search, POST /v2/rag/query, /v2/export, /openapi.yaml, webapp/ RAG playground with embedding model selector like DeepSeek harness (local + frontier models) + LLM selector + domain filter + consumer selector + Search + Query buttons + citations + consumer export buttons, examples/external-rag/ with README.md + embed.py + rag.py that are OUT OF STEMMA, connection layer, NOT whole STEMMA, proving embedding and RAG can be out of STEMMA, connecting via file/API/SDK + content_hash
- **Why inside for now:** Convenient for demo, for LearningHub, PROFESSOR-J to see how embedding/RAG connects to STEMMA via file/API/SDK + content_hash, for testing retrieval precision + faithfulness + citation coverage, for webapp RAG playground, for verify_all.py INFO checks — but production embedding/RAG is consumer's job, not STEMMA's job
- **Can be out:** YES, move scripts/embed.py, rag.py, export_consumers.py to separate repo STEMMA-RAG or to LearningHub/PROFESSOR-J repos, keep STEMMA core pure with only content/, connections/, sources/, schema/, validate.py, export_review_aware.py, graph_analysis.py, status_truth.py, verify_all.py (canonical checks as FAIL, embeddings/RAG/consumer export checks as INFO) — then STEMMA exports knowledge.json + API schema + SDK, external RAG in LearningHub/PROFESSOR-J consumes via file/API/SDK + content_hash + deterministic regeneration — cleaner separation, STEMMA remains pure knowledge foundation, embedding/RAG are external consumers, connection layer, not containing whole STEMMA — example in examples/external-rag/ proves it works out of STEMMA

### Recommendation — clear separation

- **STEMMA's job:** Provide knowledge foundation — content/, connections/, sources/, schema/, knowledge.json v2.1.0 deterministic content-hash, openapi.yaml, SDK, validation gate — pure, deterministic, HITL, versioned, NO embeddings/RAG in canonical, NO vectors in content/
- **CONSUMER's job:** Build embedding and RAG out of STEMMA as connection layer — generate embeddings via embedding-registry models, build vector store FAISS/Chroma/Qdrant/Pinecone, serve RAG queries with retrieval + generation + citations, choose embedding model, top_k, LLM model, domain filter, review_policy, rate limiting, auth per consumer needs — LearningHub, PROFESSOR-J, general, explorer, STEMMA-RAG — does NOT contain whole STEMMA, just connection layer, whole STEMMA remains in STEMMA repo
- **STEMMA provides reference implementation:** scripts/embed.py, rag.py, export_consumers.py, exports/embeddings.jsonl, vector_store/, adapters/python/ v0.2.0, webapp RAG playground, examples/external-rag/ — optional, INFO not FAIL, for convenience, demo, testing, but production embedding/RAG is consumer's job

**Therefore:** Embedding and RAG is CONSUMER's job, not STEMMA's job — STEMMA provides knowledge foundation + reference implementation as optional derived + consumer layer for convenience and demo, but production embedding and RAG is consumer's job (LearningHub, PROFESSOR-J, general, explorer, STEMMA-RAG) as connection layer out of STEMMA, not containing whole STEMMA, connecting via exports/knowledge.json + API + SDK + content_hash, with model selector like DeepSeek harness (local + frontier models) for both embedding and LLM.

## 4. Governing Laws Embedded + Evolvable Templates + Embeddings + RAG + Consumer Export

Laws live in 3 places:
- PHYSICS-GOVERNING-LAWS.md human-readable
- physics-governing-registry.yaml machine-readable deterministic
- As entities in content/physics/ with historical timeline

Templates live in:
- template-registry.yaml v2.0.0 comprehensive all-STEM 8 domains, 12 entity types, regex rules, exact constants, authoritative sources, embedding config

Embeddings live in:
- embedding-registry.yaml v1.0.0: 12 models local free + frontier API, model selector like DeepSeek harness (local + frontier models), deterministic content_hash
- Generated via embed.py → exports/embeddings.jsonl + exports/vector_store/ (FAISS meta.json + vectors.npy + ids.json)

RAG lives in:
- rag.py: vector search + context building + LLM generation with model selector like DeepSeek harness (local + frontier models), for LearningHub, PROFESSOR-J
- API: /v2/rag/search (GET vector search), /v2/rag/query (POST full RAG), via adapter server and webapp server
- Webapp RAG playground with embedding model selector and LLM model selector

Consumer export lives in:
- consumer-registry.yaml v1.0.0: 4 consumers with domains, review_policy, embedding_model, api_access, rag config
- export_consumers.py: generates consumer-specific filtered exports
- API: /v2/export?consumer=learninghub&format=json, /v2/embeddings, /openapi.yaml
- SDK: adapters/python/ v0.2.0

See AGENT.md for deterministic addition protocol with HITL + PDF primary + evolvable templates + model selector like DeepSeek harness (local + frontier models) + embeddings + RAG + consumer export.

## 5. Decisions

Baseline: ADR-0040 physics-first (now expanded to comprehensive all-STEM mediocre), 0041 minimal profile, 0042 minimal relations, 0043 mandatory source+history, HITL before canonical, PDF primary, evolvable templates v2.0.0, model selector like DeepSeek harness (local + frontier models), deterministic scales, embeddings, RAG, consumer export for LearningHub, PROFESSOR-J. Old ADRs 0001-0039 archived as legacy. Old 74 entities archived.

## 6. Scaling + Frontier + Embeddings + RAG + Consumer Export

- **Deterministic scales:** No LLM needed, uses template-registry.yaml v2.0.0 regex + exact constants, scales to 1000s PDFs, 8 domains, no cost
- **Evolvable:** Add chemistry, biology, earth-science, astronomy, computer-science, engineering, mathematics domains via YAML without code change, plus new domains like medicine via --evolve
- **LLM only when PDF missing exact definition:** Frontier models DeepSeek R1/V3 free, Claude 3.5 Sonnet/Opus, GPT-4o/o1, Gemini 2.5 Pro/2.0 Flash free, Llama 3.3 70B free, Qwen, Nemotron — via OpenRouter/NVIDIA NIM, selector like DeepSeek harness
- **Even LLM requires HITL:** Human explicitly edits markdown before canonical
- **Embeddings — YES needed:** For RAG and consumer export, embedding model generates vectors for entities, deterministic same content_hash + model → same embeddings, local free All-MiniLM 384 fast 80MB 5x faster, BGE Large SOTA 1024 1.3GB best for RAG MTEB top, plus frontier API OpenAI text-embedding-3-large 3072 best quality MTEB 64.6 $0.00013/1k, NVIDIA nv-embed-v1 SOTA 4096 free via NIM, model selector like DeepSeek harness (local + frontier models) with search, categories Frontier/Free/Local/SOTA, custom model input, stored in exports/embeddings.jsonl + vector_store/ FAISS meta.json + vectors.npy + ids.json, versioned via content_hash + model id, batch_size 32, normalize true
- **RAG — YES needed in STEMMA:** STEMMA is knowledge foundation, RAG is how consumers use it, without RAG static JSON, with RAG queryable knowledge with citations, flow question → embedding via embedding model → vector search top_k cosine similarity over FAISS → context with definitions + connections + sources + source_refs + links → LLM prompt with context + question → answer with citations, supports consumer-specific models LearningHub GPT-4o, PROFESSOR-J DeepSeek R1 free, evaluation retrieval precision + answer faithfulness + citation coverage, API /v2/rag/search GET + /v2/rag/query POST via adapter and webapp, webapp RAG playground with embedding model selector and LLM model selector
- **Consumer export — YES needed:** Export mechanism via file (exports/knowledge.json deterministic content-hash v2.1.0, embeddings.jsonl, vector_store/ FAISS, consumers/<consumer>/knowledge.<consumer>.json filtered by domains/review_policy/entity_types), API (adapter server v0.2.0 with endpoints /v2/stats, /v2/entities?domain=..., /v2/connections, /v2/search?q=..., /v2/embeddings?model=...&id=...&domain=..., /v2/rag/search?q=...&top_k=..., POST /v2/rag/query with question+top_k+model+embedding_model+domain+consumer, /v2/export?consumer=learninghub&format=json&review_policy=..., /openapi.yaml OpenAPI 3.0.3 schema), SDK (Python pip install ./adapters/python — Stemma.from_file + search + resolve + prerequisites + StemmaRAG.from_files + query, future TypeScript adapter), for LearningHub (canonical physics/chem/bio/math, OpenAI text-embedding-3-large 3072, RAG GPT-4o, rate limit 1000/hour api_key, endpoints /v2/stats /v2/entities /v2/search /v2/rag/query /v2/embeddings), PROFESSOR-J (reviewed all 8 domains mediocre, BGE Large offline SOTA 1024, FAISS vector store, RAG DeepSeek R1 free fallback Claude 3.5 Sonnet/GPT-4o/Gemini 2.5 Pro, rate limit 10000/hour, all endpoints), general (all domains, All-MiniLM fast local), explorer (3D graph), auth none local + api_key for LearningHub/PROFESSOR-J + bearer for frontier models via OpenRouter


## Guideline — How to Build Embedder and RAG That Imports From STEMMA Consistently (NEW 2026-09-21 — v1.0.0)

See **[GUIDELINE-EMBEDDER-RAG.md](GUIDELINE-EMBEDDER-RAG.md)** — authoritative 81KB guideline for consumers to build consistent embedder + RAG architecture that imports from STEMMA via file/API/SDK + content_hash.

**What it covers:**
- Direction we are going: comprehensive all-STEM mediocre (8 domains 97 subdomains 12 entity types 400-800 target) + clean separation Layer1 Canonical (NO embeddings/RAG, whole STEMMA), Layer2 Derived (YES embeddings as derived regenerable deterministic content-hash), Layer3 Consumer+RAG (YES RAG as consumer mechanism, can be out of STEMMA)
- New change already implemented (2026-09-21): template-registry v2.0.0 8 domains, embedding-registry v1.0.0 12 models local free + frontier with model selector like DeepSeek harness, consumer-registry v1.0.0 4 consumers LearningHub OpenAI Large 3072 GPT-4o top_k5 PROFESSOR-J BGE Large 1024 offline DeepSeek R1 free top_k10, API schema v2.1.0 OpenAPI 3.0.3, embed.py rag.py export_consumers.py adapter v0.2.0 /v2/embeddings /v2/rag/search POST /v2/rag/query /v2/export /openapi.yaml webapp RAG playground, examples/external-rag/ out-of-STEMMA proving embedding/RAG can be out as connection layer NOT whole STEMMA via file/API/SDK + content_hash
- Future plans: R1 NOW 400-800 + embeddings + RAG + consumer export + guideline + sample, R2 Math Layer + Governing Laws + Embeddings SOTA (BGE-M3, GTE, Jina, E5-Mistral, re-ranking, ColBERT, HyDE) + RAG Evaluation (retrieval precision, faithfulness, citation coverage, re-ranking, multi-hop, HyDE, self-RAG, evaluation dataset) + Consistent Architecture (TypeScript adapter, Python package stemma-rag, consistent import via file/API/SDK + content_hash, model selector, deterministic versioning, context building with citations, API, webapp playground, evaluation metrics) + Production API hosting, R3 Other Domains LATER + Production RAG + Hosted Vector Store Qdrant/Pinecone + Consistent Architecture Across All Consumers via guideline
- Embedder best practices: model selector like DeepSeek harness 12 models, chunking entity strategy 512 tokens deterministic, content-hash sha256(text+model_id+knowledge content_hash)[:16] versioned batch 32 normalize, vector store FAISS flat cosine meta.json v1.0.0, storage embeddings.jsonl + vector_store/
- RAG best practices: retriever vector search cosine FAISS top_k 5 LearningHub 10 PROFESSOR-J domain filter, context building definitions+connections+sources+source_refs+links+scores with citations, generator LLM model selector like DeepSeek harness 25 models DeepSeek R1 free Claude 3.5 Sonnet GPT-4o Gemini 2.5 Pro Llama 3.3 custom citation enforcement, full flow question->embedding->vector search->context->LLM->answer with citations, API /v2/rag/search GET POST /v2/rag/query, webapp RAG playground
- Sample in derived: inside STEMMA scripts/embed.py rag.py exports/embeddings.jsonl vector_store/ meta.json deterministic + out-of-STEMMA examples/external-rag/embed.py rag.py data/embeddings.jsonl data/vector_store/ out-of-STEMMA connection layer NOT whole STEMMA


