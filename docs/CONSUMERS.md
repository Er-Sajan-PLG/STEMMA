# CONSUMERS — Comprehensive All-STEM, Mediocre Coverage, Embeddings, RAG, Export Mechanism

**Status:** Authoritative, comprehensive all-STEM mediocre (not minimal physics). 1 entity now (metre) via PDF primary ingestion with HITL, will grow to mediocre across 8 domains: physics, chemistry, biology, earth-science, astronomy, computer-science, engineering, mathematics. Old 74 entities archived.

## Consumer Registry — NEW v1.0.0

Defined in `schema/consumer-registry.yaml` — 4 consumers:

### LearningHub
- **Label:** LearningHub — curriculum-agnostic learning platform that consumes STEMMA as knowledge foundation
- **Domains:** physics, chemistry, biology, mathematics — canonical only (physics: mechanics, measurement-units, electricity-magnetism, thermal; chemistry: general, organic, inorganic; biology: cell-biology, genetics; math: algebra, calculus, statistics)
- **Review policy:** canonical
- **Entity types:** concept, quantity, unit, law, principle, theorem, equation, process, structure
- **Export formats:** knowledge.json, embeddings.jsonl, openapi
- **Embedding model:** openai/text-embedding-3-large (frontier, 3072 dim, best quality MTEB 64.6) fallback BGE Large SOTA 1024 — YES embedding model needed for student RAG queries
- **API access:** enabled, endpoints /v2/stats, /v2/entities, /v2/search, /v2/rag/query, /v2/embeddings, rate_limit 1000/hour, auth api_key
- **RAG:** enabled, top_k 5, model GPT-4o — YES RAG system needed, without RAG static JSON, with RAG queryable knowledge with citations for students
- **Example:** "What is Newton's second law?" → embedding → vector search top 5 → context with definitions + sources → GPT-4o → answer with citations

### PROFESSOR-J
- **Label:** PROFESSOR-J — AI professor that answers STEM questions using STEMMA RAG
- **Domains:** all 8 domains mediocre coverage — physics, chemistry, biology, earth-science, astronomy, computer-science, engineering, mathematics — all subdomains
- **Review policy:** reviewed (human_reviewed + canonical)
- **Entity types:** all (concept, quantity, unit, constant, law, principle, theorem, equation, process, structure, algorithm, material)
- **Export formats:** knowledge.json, knowledge.jsonl, embeddings.jsonl, vector_store, openapi
- **Embedding model:** BAAI/bge-large-en-v1.5 (local SOTA 1024 dim, offline capable, best for RAG MTEB top) fallback All-MiniLM-L6-v2 fast 384 dim — YES embedding model needed, offline SOTA for AI professor
- **API access:** enabled, endpoints /v2/stats, /v2/entities, /v2/connections, /v2/search, /v2/neighbors, /v2/prerequisites, /v2/rag/query, /v2/rag/search, /v2/embeddings, /v2/export, rate_limit 10000/hour, auth api_key
- **RAG:** enabled, top_k 10, model DeepSeek R1 free (reasoning 671B) fallback Claude 3.5 Sonnet, GPT-4o, Gemini 2.5 Pro — YES RAG system needed, AI professor needs retrieval + generation with citations
- **Example:** "Explain photosynthesis and its relation to cellular respiration" → embedding BGE Large → vector search top 10 across biology → context → DeepSeek R1 → answer with citations source_refs + links

### STEMMA Explorer (Reference 3D Graph)
- **Label:** Reference 3D graph explorer — visualizes knowledge graph
- **Domains:** all
- **Review policy:** all
- **Export formats:** knowledge.json
- **Needs:** clean 3D small nodes 0.32-0.5 thin lines 0.15 legend hidden manual only zoom centered tight 32-65 centroid, domain filter for 8 domains

### General Consumer
- **Label:** Any app that wants STEMMA via adapter SDK, CLI, or local JSON API
- **Domains:** all
- **Review policy:** all
- **Export formats:** knowledge.json, knowledge.jsonl, openapi
- **Embedding model:** All-MiniLM-L6-v2 fast local 384 dim — YES embedding model for quick RAG
- **API access:** /v2/stats, /v2/entities, /v2/search, rate_limit 100/hour, auth none

## Export Mechanisms — YES needed, 3 ways

### 1. File-based exports (deterministic, versioned, content-hash, no wall clock)
- `exports/knowledge.json` — main export v2.1.0 deterministic content-hash sha256, no wall clock, 1 entity now, will grow to mediocre all-domain
- `exports/knowledge.all.json, canonical.json, reviewed.json, trusted.json` — review-aware
- `exports/embeddings.jsonl` — NEW: embeddings per entity with model id, dimensions, vector, content_hash, content — deterministic same content_hash + model → same embeddings, generated via `python3 scripts/embed.py --model BAAI/bge-large-en-v1.5`
- `exports/vector_store/` — NEW: FAISS/Chroma/Qdrant local vector store — meta.json + vectors.npy + ids.json, versioned via content_hash + model id, for RAG, generated via embed.py
- `exports/consumers/<consumer>/knowledge.<consumer>.json` — NEW: consumer-specific filtered exports — e.g., LearningHub canonical physics/chem/bio/math, PROFESSOR-J reviewed all 8 domains, generated via `python3 scripts/export_consumers.py --consumer learninghub --format json`
- `exports/openapi.yaml` — OpenAPI schema from schema/api.yaml

### 2. REST API (via adapter Python server + webapp server) — NEW with embeddings + RAG + consumer export
- **Base URL:** /v2 for adapter (PYTHONPATH=adapters/python python3 -m stemma_adapter serve exports/knowledge.json --port 8080), /api for webapp (python3 webapp/server.py --port 8081)
- **OpenAPI:** schema/api.yaml v2.1.0 — OpenAPI 3.0.3
- **Endpoints:**
  - `/v2/stats` — stats entity_count, connection_count, source_count, content_hash, versions, domains
  - `/v2/entities?domain=physics&subdomain=mechanics&type=quantity&status=canonical&limit=100` — list entities with filters for 8 domains
  - `/v2/entities/{id}` — get entity e.g., stemma:phys.metre
  - `/v2/connections?source=...&target=...&relation=...` — list connections
  - `/v2/search?q=force&domain=physics&limit=10` — search
  - `/v2/neighbors/{id}` — neighbors
  - `/v2/prerequisites/{id}?policy=canonical` — prereq closure
  - `/v2/relations`, `/v2/relations/{name}`, `/v2/vocabularies` — registries
  - `/v2/embeddings?model=BAAI/bge-large-en-v1.5&id=stemma:phys.metre&domain=physics&limit=100` — NEW: embeddings with model selector like DeepSeek harness (local + frontier models: local free BGE All-MiniLM + frontier OpenAI text-embedding-3-large Cohere Gemini NVIDIA), returns model, dimensions, vector_preview, content_hash
  - `/v2/rag/search?q=What is Newton's second law?&top_k=5&model=BAAI/bge-large-en-v1.5&domain=physics` — NEW: vector search for RAG, embedding query → cosine similarity over FAISS → top_k entities with scores + content
  - `POST /v2/rag/query` — NEW: full RAG query — body {question, top_k, model, embedding_model, domain, consumer} — e.g., {question: "What is Newton's second law?", top_k: 5, model: "deepseek/deepseek-r1:free", embedding_model: "BAAI/bge-large-en-v1.5", domain: "physics", consumer: "learninghub"} → returns {question, answer, citations [{entity_id, source_ref, link}], retrieved_entities [{entity, score, content}], model_used, embedding_model_used, content_hash}
  - `/v2/export?consumer=learninghub&format=json&review_policy=canonical` — NEW: export for specific consumer filtered by domains/review_policy/entity_types, returns preview + hint for full file at exports/consumers/<consumer>/knowledge.<consumer>.json
  - `/openapi.yaml` or `/v2/openapi.yaml` — OpenAPI schema
- **Auth:** none for local, api_key for LearningHub/PROFESSOR-J, bearer for frontier models via OpenRouter (DeepSeek, Claude, GPT-4o, Gemini, Llama)
- **Example curl:**
  ```bash
  curl http://localhost:8080/v2/stats
  curl "http://localhost:8080/v2/search?q=force&domain=physics"
  curl "http://localhost:8080/v2/embeddings?model=BAAI/bge-large-en-v1.5&limit=5"
  curl "http://localhost:8080/v2/rag/search?q=Newton%20second%20law&top_k=5"
  curl -X POST http://localhost:8080/v2/rag/query -H "Content-Type: application/json" -d '{"question":"What is Newton second law?","top_k":5,"model":"deepseek/deepseek-r1:free","consumer":"learninghub"}'
  curl "http://localhost:8080/v2/export?consumer=learninghub&format=json"
  ```

### 3. SDKs
- **Python:** adapters/python/ — pip install ./adapters/python — SDK, CLI, local JSON API server v0.2.0 now with embeddings + RAG
  ```python
  from stemma_adapter import Stemma
  stemma = Stemma.from_file("exports/knowledge.json")
  print(stemma.stats)
  print(stemma.search("force", domain="physics"))
  # RAG
  import sys
  sys.path.insert(0, "scripts")
  import rag
  results = rag.vector_search("What is Newton's second law?", top_k=5)
  answer = rag.rag_query("What is Newton's second law?", top_k=5, model="deepseek/deepseek-r1:free", consumer="learninghub")
  print(answer['answer'])
  ```
- **CLI:**
  ```bash
  stemma-adapter validate exports/knowledge.json
  stemma-adapter stats exports/knowledge.json
  stemma-adapter search exports/knowledge.json force --domain physics --limit 5
  stemma-adapter serve exports/knowledge.json --port 8080
  python3 scripts/embed.py --model BAAI/bge-large-en-v1.5 --output exports/embeddings.jsonl
  python3 scripts/rag.py --question "What is Newton's second law?" --top-k 5 --model deepseek/deepseek-r1:free --consumer learninghub
  python3 scripts/export_consumers.py --consumer learninghub --format json
  python3 scripts/export_consumers.py --all
  ```
- **Future:** TypeScript adapter adapters/typescript/

## Embeddings — YES needed

**Do we need embedding model for embedding? YES.**

Embedding model generates vectors for entities for RAG and consumer export. Without embeddings, STEMMA is static JSON, can't do semantic search. With embeddings, LearningHub students can query "Newton's law" and get relevant entities via vector similarity, PROFESSOR-J can answer questions offline.

- **Models:** 12 models in schema/embedding-registry.yaml v1.0.0 — local free (All-MiniLM-L6-v2 384 dim fast 80MB 5x faster, All-MPNet-Base-V2 768 dim 420MB high quality, BGE Large SOTA 1024 dim 1.3GB best for RAG MTEB top, E5 Large V2 1024 dim 1.3GB retrieval-optimized, BGE Small 384 dim 133MB fast) + frontier API (OpenAI text-embedding-3-large 3072 dim best quality MTEB 64.6 $0.00013/1k, text-embedding-3-small 1536 dim fast frontier $0.00002/1k, Ada 002 legacy 1536, Cohere embed-v3 1024, Gemini text-embedding-004 768 free tier, NVIDIA nv-embed-v1 SOTA 4096 free via NIM MTEB top)
- **Model selector like DeepSeek harness:** Search bar, category tabs All/Frontier/Free/Local/SOTA, model cards with FREE/FRONTIER/LOCAL badges, dimensions, description, custom model input any frontier or your own fine-tuned via OpenRouter/NVIDIA NIM/OpenAI-compatible
- **Deterministic:** Same knowledge.json content_hash + model id → same embeddings, content_hash versioned, batch_size 32, normalize true, chunking entity strategy max_tokens 512 overlap 50
- **Storage:** exports/embeddings.jsonl (entity_id, model, dimensions, vector, content, content_hash) + exports/vector_store/ (FAISS meta.json + vectors.npy + ids.json) — derived artifacts regenerable, versioned via content_hash + model id
- **Consumer-specific:** LearningHub prefers OpenAI text-embedding-3-large 3072 for high quality, PROFESSOR-J prefers BGE Large SOTA 1024 offline, general prefers All-MiniLM fast local
- **Generation:** `python3 scripts/embed.py --model BAAI/bge-large-en-v1.5 --output exports/embeddings.jsonl --vector-store exports/vector_store/` — tries sentence-transformers if installed, else fake deterministic hash-based for demo

## RAG System — YES needed in STEMMA

**Do we need RAG system here in STEMMA? YES.**

STEMMA is knowledge foundation, RAG is how consumers like LearningHub, PROFESSOR-J use it. Without RAG, STEMMA is just static JSON. With RAG, it's queryable knowledge with citations, grounded answers.

- **Components:** Ingestion PDF → deterministic extraction via template-registry v2.0.0 → entity markdown → embedding via embedding-registry → vector_store FAISS/Chroma/Qdrant local path exports/vector_store/ versioned with content_hash → retriever similarity search over entity definitions + connections → generator LLM with model selector like DeepSeek harness (local + frontier models: DeepSeek R1 free 671B reasoning, DeepSeek V3 free 671B, Claude 3.5 Sonnet frontier, Claude 3 Opus reasoning, GPT-4o frontier multimodal, o1 reasoning frontier, Gemini 2.5 Pro frontier, Gemini 2.0 Flash free, Llama 3.3 70B free, custom via OpenRouter/NVIDIA NIM) → answer with citations (source_refs + link)
- **Flow:** User question → embedding via embedding model → vector search top_k cosine similarity → build context with definitions + connections + sources + source_refs + links → LLM prompt with context + question → answer with citations
- **Evaluation:** Retrieval precision top_k relevant, answer faithfulness grounded in retrieved entities, citation coverage every claim has source_ref
- **Versioning:** Vector store versioned via content_hash of knowledge.json + embedding model id, deterministic same knowledge.json + model → same embeddings + same FAISS index, no wall clock
- **API:** /v2/rag/search GET + /v2/rag/query POST via adapter server v0.2.0 and webapp server, webapp RAG playground with embedding model selector like DeepSeek harness (local + frontier models) + LLM model selector + domain filter + consumer selector + citations display
- **Consumer-specific:** LearningHub top_k 5 GPT-4o, PROFESSOR-J top_k 10 DeepSeek R1 free fallback Claude 3.5 Sonnet/GPT-4o/Gemini 2.5 Pro
- **Example:** `python3 scripts/rag.py --question "What is Newton's second law?" --top-k 5 --model deepseek/deepseek-r1:free --consumer learninghub` → retrieves metre, force, mass, time, etc. → builds context → calls DeepSeek R1 via OpenRouter → answer with citations

## Why comprehensive all-STEM mediocre, not minimal physics?

User direction change: from minimal physics to mediocre all domain, add remaining domains, build comprehensive template that can extract from pdf and embed the data.

- **Minimal physics** was v0.1 beginning with 70 entities physics only — proved review bottleneck, 224 entities unreviewable before, but now with HITL + deterministic scales + evolvable templates we can scale
- **Mediocre all-domain** is better foundation: 8 domains × mediocre coverage (e.g., 50-100 entities each = 400-800 total) with deterministic templates that scale, embeddings, RAG, consumer export — more useful for LearningHub, PROFESSOR-J than minimal physics
- **Remaining domains added:** Previously only physics, chemistry, biology, mathematics with few subdomains — now comprehensive: physics 12 subdomains, chemistry 11, biology 14, earth-science 10, astronomy 8, computer-science 15, engineering 13, mathematics 14 — total 97 subdomains, covers all STEM
- **Comprehensive template v2.0.0:** 12 entity types (concept, quantity, unit, constant, law, principle, theorem, equation, process, structure, algorithm, material) with templates, regex extraction_rules for all domains (Length, Mass, Time, Area, Volume, Element, Mole, Cell, DNA, Photosynthesis, Algorithm, Sorting, Machine Learning, Derivative, Integral, Theorem, Earthquake, Black Hole, Stress, etc.), standard_definition_sources (SI Brochure, NIST, IUPAC Gold Book, CRC Handbook, HRW, Campbell Biology, CLRS, Atkins, Carroll Astrophysics), llm_fallback prompt for when PDF missing exact, embedding config with 8 models
- **Evolvable:** Add new domain like medicine, economics via `python3 scripts/evolvable_template.py --evolve --new-domain medicine` without code change

## All good for PR? Yes — but we need to update docs and implement embeddings/RAG/export first (done in this change)


## Explicit Separation — Canonical vs Derived vs Consumer (NEW 2026-09-21 — Answers: Does STEMMA itself need embeddings/RAG?)

**User question:** "Now about RAG system and embedding, STEMMA in itself doesn't need them!? But again STEMMA alone existence is useless if we can't use it, so building RAG pipeline is inevitable here!?"

**Answer: YES, exactly right — clean separation:**

- **Canonical (STEMMA itself) — NO embeddings/RAG:** content/, connections/, sources/, schema/ (except registries that define models, not vectors) — only Markdown+YAML with exact definitions, dual verification, governed_by, history, 8 relations, evidence — NO embeddings, vectors, .npy, embeddings.jsonl, vector_store/ — NEVER — validate.py NEVER checks embeddings — previously "Not on roadmap: embeddings, database as source of truth" meant canonical, not derived — correct, canonical never has embeddings
- **Derived (exports/) — YES embeddings here but as derived, regenerable, deterministic, content-hash:** knowledge.json v2.1.0 content-hash, embeddings.jsonl, vector_store/ FAISS meta.json + vectors.npy + ids.json versioned via content_hash + model id, consumers/<consumer>/knowledge.<consumer>.json, openapi.yaml — deterministic same content_hash + model id → same embeddings, regenerable via validate.py + embed.py, verify_all.py checks embeddings existence as INFO, not FAIL
- **Consumer + RAG Pipeline (scripts/, adapters/, webapp/) — YES RAG here but as consumer mechanism, inevitable for usability:** embed.py local free All-MiniLM/BGE Large + frontier OpenAI Large/NVIDIA NV-Embed with model selector like DeepSeek harness (local + frontier models), rag.py vector search + context + LLM generation with model selector like DeepSeek harness (local + frontier models) + citations, export_consumers.py, adapters/python/ v0.2.0 with /v2/embeddings, /v2/rag/search, POST /v2/rag/query, /v2/export, /openapi.yaml, webapp RAG playground — without RAG static JSON useless, with RAG queryable knowledge with citations for LearningHub, PROFESSOR-J — therefore RAG pipeline inevitable, but as consumer layer, not canonical

**Invariants:**
1. Canonical never contains embeddings, vectors, RAG artifacts
2. Embeddings live only in exports/ as derived, regenerable via embed.py, versioned via content_hash + model id, deterministic
3. RAG lives only in scripts/adapters/webapp as consumer mechanism, optional for canonical validity, inevitable for usability
4. Gate validate.py never checks embeddings
5. verify_all.py checks embeddings existence as INFO not FAIL
6. Previously "Not on roadmap: embeddings" meant canonical, not derived — now embeddings ARE in derived + consumer which IS on roadmap (R1 comprehensive all-STEM mediocre + embeddings + RAG + consumer export)

**Answers:**
- Does STEMMA itself need embeddings/RAG? NO — canonical valid without
- Is STEMMA alone useless if we can't use it? YES — static JSON alone not queryable
- Is building RAG pipeline inevitable? YES — as derived + consumer, inevitable for usability, cleanly separated, optional for canonical validity, deterministic, versioned, with model selector like DeepSeek harness (local + frontier models)


## Can Embedding and RAG Be Out of STEMMA? YES — As Connection Layer, Not Containing Whole STEMMA (NEW 2026-09-21)

**User question:** "Can i actually have embedding and RAG out of STEMMA!? How do they connect then?? Embedding and RAG doesn't contain the whole STEMMA right!? its just a connection layer!?"

**Answer: YES, exactly right — embedding and RAG can be out of STEMMA, they're just connection layer, not containing whole STEMMA, they connect via exports/knowledge.json + API + SDK + content_hash.**

- **STEMMA itself (whole STEMMA):** content/<domain>/**/*.md (Markdown+YAML with exact definitions, dual verification, governed_by, history), connections/*.yaml (8 relations, evidence), sources/*.yaml (url/doi/isbn + writer human:*), schema/ — NO embeddings, NO vectors, NO RAG — pure knowledge foundation, whole STEMMA is here, e.g., metre defined as light path 1/299,792,458 s Exact c=299,792,458 m/s Agreed per BIPM 2019 + writer human:curator.001 + link + source_refs + wd
- **Embedding (connection layer, NOT whole STEMMA):** Does NOT contain whole STEMMA — contains vectors DERIVED from STEMMA definitions, e.g., metre chunk "Metre (stemma:phys.metre) Domain: physics/measurement-units Definition: The metre..." → embedding model All-MiniLM 384 dim or BGE Large 1024 SOTA or OpenAI Large 3072 → vector [0.12, -0.34, ...] 384/1024/3072 floats — semantic fingerprint for similarity search, stored in exports/embeddings.jsonl as {entity_id, model, dimensions, vector, content, content_hash} — regenerable from knowledge.json + model id, deterministic same content_hash + model → same vector — NOT whole STEMMA, just derived vectors
- **Vector store (connection layer, NOT whole STEMMA):** Does NOT contain whole STEMMA — contains FAISS index of vectors + ids.json + meta.json with model, dimensions, content_hash, entity_count — e.g., vectors.npy shape (1, 384), ids.json ["stemma:phys.metre"] — just index for fast cosine similarity, NOT whole STEMMA, just connection layer for retrieval
- **RAG (connection layer, NOT whole STEMMA):** Does NOT contain whole STEMMA — contains retrieval logic (embedding query → cosine similarity over FAISS → top_k entities with scores) + generation logic (build context definitions + connections + sources + source_refs + links → LLM prompt → answer with citations) — e.g., question "What is Newton's second law?" → retrieves [force, mass, newtons-second-law] → context → LLM DeepSeek R1 free → answer with citations entity_id + source_ref + link — grounded in STEMMA but RAG itself doesn't contain whole STEMMA, only references entity IDs and definitions as context, whole STEMMA remains in content/

**How do they connect? Via exports/knowledge.json + API + SDK + content_hash — 3 ways:**

1. **File-based:** STEMMA exports knowledge.json v2.1.0 deterministic content-hash — external RAG (out of STEMMA) in LearningHub or PROFESSOR-J or separate repo STEMMA-RAG copies knowledge.json file, then runs own embedding generation externally: `cp ../STEMMA/exports/knowledge.json ./data/ && python3 -m stemma_rag.embed --input ./data/knowledge.json --model BAAI/bge-large-en-v1.5 --output ./data/embeddings.jsonl --vector-store ./data/vector_store/` — connection via content_hash, if changed recompute embeddings — does NOT contain whole STEMMA, only vectors + index + retrieval logic

2. **API-based:** STEMMA API adapter v0.2.0 serves knowledge.json via REST API with OpenAPI schema api.yaml v2.1.0: /v2/stats content_hash, /v2/entities?domain=physics&status=canonical&limit=1000, /v2/entities/{id}, /v2/search?q=..., /v2/embeddings?model=..., /v2/rag/search?q=...&top_k=..., POST /v2/rag/query, /v2/export?consumer=..., /openapi.yaml — external RAG in LearningHub/PROFESSOR-J calls API to get entities, generates embeddings externally, builds FAISS externally, serves RAG queries with citations — connection via API + content_hash, does NOT contain whole STEMMA, just connection layer

3. **SDK-based:** STEMMA SDK adapters/python/ pip install ./adapters/python — Stemma.from_file("exports/knowledge.json") or Stemma.from_api("http://localhost:8080") — search, resolve, stats with content_hash — external RAG uses SDK to load STEMMA, then builds own embeddings/RAG out of STEMMA: `from stemma_adapter import Stemma; stemma = Stemma.from_file("../STEMMA/exports/knowledge.json"); from stemma_rag import StemmaRAG; rag = StemmaRAG.from_stemma(stemma, embedding_model="BAAI/bge-large-en-v1.5"); answer = rag.query("What is Newton's second law?", top_k=5, model="deepseek/deepseek-r1:free")` — connection via SDK + content_hash, does NOT contain whole STEMMA, just connection layer

**Current implementation:** Optional derived layer inside STEMMA for convenience and demo — scripts/embed.py, rag.py, export_consumers.py, exports/embeddings.jsonl, vector_store/, adapters/python/ v0.2.0 with /v2/embeddings, /v2/rag/search, POST /v2/rag/query, /v2/export, /openapi.yaml, webapp RAG playground — all inside STEMMA repo, but as derived + consumer layer, not canonical, optional, INFO not FAIL in verify_all.py — convenient for demo, for LearningHub, PROFESSOR-J to see how embedding/RAG connects, for testing retrieval precision + faithfulness + citation coverage

**Can be out:** YES, you can have embedding and RAG out of STEMMA — move scripts/embed.py, rag.py, export_consumers.py to separate repo STEMMA-RAG or to LearningHub/PROFESSOR-J repos, keep STEMMA core pure with only content/, connections/, sources/, schema/, validate.py — then STEMMA exports knowledge.json + API schema, external RAG consumes via file/API/SDK + content_hash + deterministic regeneration — cleaner separation, STEMMA remains pure knowledge foundation, embedding/RAG are external consumers, connection layer, not containing whole STEMMA

**Recommendation:** Keep canonical pure (content/, connections/, sources/, schema/ — NO embeddings, NO RAG, validate.py NEVER checks embeddings), keep derived optional inside for convenience (exports/knowledge.json, embeddings.jsonl, vector_store/, consumers/ — derived, regenerable, deterministic, content-hash, INFO not FAIL), but for production LearningHub, PROFESSOR-J have embedding and RAG out of STEMMA as separate service or part of LearningHub/PROFESSOR-J that consumes STEMMA via file/API/SDK + content_hash, generates embeddings externally, builds vector store externally, serves RAG queries with citations — embedding/RAG doesn't contain whole STEMMA, just connection layer, whole STEMMA remains in STEMMA repo

**Therefore:** YES, you can have embedding and RAG out of STEMMA, they connect via exports/knowledge.json + API + SDK + content_hash, they don't contain whole STEMMA, they're just connection layer — current implementation keeps them inside as optional derived + consumer for convenience and demo, but can be moved out to separate repo or to LearningHub/PROFESSOR-J for cleaner separation.


## Whose Job Is To Build Embedding and RAG? CONSUMER's Job, Not STEMMA's Job — STEMMA Provides Reference Implementation (NEW 2026-09-21)

**User question:** "whose job is to build embedding and RAG!? STEMMA or CONSUMER!?"

**Answer: CONSUMER's job, not STEMMA's job — STEMMA provides reference implementation as optional derived + consumer layer for convenience and demo, but production embedding and RAG is consumer's job (LearningHub, PROFESSOR-J, general, explorer, STEMMA-RAG).**

- **STEMMA's job — knowledge foundation, pure, deterministic, HITL, versioned, content-hash, NO embeddings/RAG in canonical:** content/<domain>/**/*.md (Markdown+YAML with exact definitions, dual verification, governed_by, history), connections/*.yaml (8 relations, evidence), sources/*.yaml (url/doi/isbn + writer human:*), schema/ (JSON Schemas, relation-registry, template-registry v2.0.0 comprehensive all-STEM 8 domains 97 subdomains 12 entity types, embedding-registry v1.0.0 12 models, consumer-registry v1.0.0 4 consumers, api.yaml OpenAPI 3.0.3, governing-registry, VERSION.yaml), scripts/validate.py (NEVER checks embeddings, only canonical), physics_core_profile_check.py, physics_governing_check.py, hitl_check.py, evolvable_template.py, status_truth.py, verify_all.py (canonical checks as FAIL, embeddings/RAG/consumer export checks as INFO not FAIL) — provides knowledge foundation + deterministic versioned exports knowledge.json v2.1.0 content-hash + openapi.yaml + SDK for consumers — pure, deterministic, HITL, versioned, NO embeddings/RAG in canonical — whole STEMMA is here
- **Why NOT embedding/RAG in canonical STEMMA's job:** Embeddings are model-specific (All-MiniLM 384 vs BGE Large 1024 vs OpenAI Large 3072 vs NVIDIA NV-Embed 4096 give different vectors), non-deterministic, not time-invariant, would pollute canonical with floats, make content/ non-human-reviewable, would require STEMMA to choose one embedding model, one vector store, one LLM, one top_k for all consumers — impossible, because consumers have different needs (LearningHub prefers OpenAI Large 3072 high quality for student queries, PROFESSOR-J prefers BGE Large SOTA 1024 offline capable for AI professor, general prefers All-MiniLM fast local) — therefore embedding and RAG cannot be one-size-fits-all in STEMMA, must be consumer's job
- **CONSUMER's job — build embedding and RAG out of STEMMA as connection layer, NOT containing whole STEMMA:** LearningHub, PROFESSOR-J, general, explorer, STEMMA-RAG — in LearningHub repo or PROFESSOR-J repo or separate STEMMA-RAG repo — data/knowledge.json copied from STEMMA exports/knowledge.json, data/embeddings.jsonl generated externally via embed.py out of STEMMA, data/vector_store/ FAISS built externally out of STEMMA, rag.py retrieval + generation logic out of STEMMA, or via API calls to STEMMA API /v2/entities, /v2/stats content_hash, /v2/search, etc., or via SDK Stemma.from_file() or from_api() — generate vectors DERIVED from STEMMA definitions via embedding model (local free All-MiniLM/BGE Large + frontier OpenAI Large/NVIDIA NV-Embed, model selector like DeepSeek harness (local + frontier models)), build vector store FAISS/Chroma/Qdrant/Pinecone, serve RAG queries with retrieval + generation + citations — e.g., LearningHub: preferred_model OpenAI Large 3072 fallback BGE Large, RAG top_k 5 model GPT-4o, endpoints /v2/stats /v2/entities /v2/search /v2/rag/query /v2/embeddings, rate limit 1000/hour api_key, example "What is Newton's second law?" → embedding OpenAI Large → vector search top 5 → context definitions + sources → GPT-4o → answer with citations; PROFESSOR-J: preferred_model BGE Large SOTA 1024 offline fallback All-MiniLM, RAG top_k 10 model DeepSeek R1 free fallback Claude 3.5 Sonnet/GPT-4o/Gemini 2.5 Pro, all endpoints, rate limit 10000/hour, example "Explain photosynthesis and its relation to cellular respiration" → embedding BGE Large → vector search top 10 across biology → context → DeepSeek R1 free → answer with citations — why consumer's job: embedding model choice is consumer-specific, RAG top_k and LLM model choice is consumer-specific, vector store type is consumer-specific (FAISS local vs Chroma vs Qdrant vs Pinecone cloud), domain filter is consumer-specific (LearningHub canonical physics/chem/bio/math vs PROFESSOR-J reviewed all 8 domains mediocre), review_policy is consumer-specific (LearningHub canonical vs PROFESSOR-J reviewed vs general all), rate limiting and auth are consumer-specific — therefore embedding and RAG must be consumer's job, not STEMMA's job, to fit each consumer's needs — does NOT contain whole STEMMA, just connection layer, whole STEMMA remains in STEMMA repo
- **STEMMA provides reference implementation as optional derived + consumer layer for convenience and demo, but production embedding/RAG is consumer's job:** Currently inside STEMMA for convenience and demo (optional, INFO not FAIL): scripts/embed.py (local free + frontier, model selector like DeepSeek harness (local + frontier models), tries sentence-transformers if installed else fake deterministic hash-based for demo), scripts/rag.py (vector search + context + LLM generation with model selector like DeepSeek harness (local + frontier models) + citations, consumer-specific), scripts/export_consumers.py, exports/embeddings.jsonl (1 embeddings now deterministic fake for demo), exports/vector_store/ FAISS meta.json + vectors.json + ids.json versioned via content_hash + model id, exports/consumers/<consumer>/knowledge.<consumer>.json filtered, adapters/python/ v0.2.0 with /v2/embeddings, /v2/rag/search, POST /v2/rag/query, /v2/export, /openapi.yaml, webapp RAG playground with embedding model selector like DeepSeek harness (local + frontier models) + LLM selector + domain filter + consumer selector + Search + Query buttons + citations + consumer export buttons, examples/external-rag/ with README.md + embed.py + rag.py that are OUT OF STEMMA, connection layer, NOT whole STEMMA, proving embedding and RAG can be out of STEMMA, connecting via file/API/SDK + content_hash — why inside for now: convenient for demo, for LearningHub, PROFESSOR-J to see how embedding/RAG connects via file/API/SDK + content_hash, for testing retrieval precision + faithfulness + citation coverage, for webapp RAG playground, for verify_all.py INFO checks — but production embedding/RAG is consumer's job, not STEMMA's job — can be out: YES, move to separate repo STEMMA-RAG or to LearningHub/PROFESSOR-J repos, keep STEMMA core pure with only content/, connections/, sources/, schema/, validate.py, export_review_aware.py, graph_analysis.py, status_truth.py, verify_all.py (canonical checks as FAIL, embeddings/RAG/consumer export checks as INFO) — then STEMMA exports knowledge.json + API schema + SDK, external RAG in LearningHub/PROFESSOR-J consumes via file/API/SDK + content_hash + deterministic regeneration — cleaner separation, STEMMA remains pure knowledge foundation, embedding/RAG are external consumers, connection layer, not containing whole STEMMA — example in examples/external-rag/ proves it works out of STEMMA

**Recommendation:**
- STEMMA's job: Provide knowledge foundation — content/, connections/, sources/, schema/, knowledge.json v2.1.0 deterministic content-hash, openapi.yaml, SDK, validation gate — pure, deterministic, HITL, versioned, NO embeddings/RAG in canonical, NO vectors in content/
- CONSUMER's job: Build embedding and RAG out of STEMMA as connection layer — generate embeddings via embedding-registry models, build vector store FAISS/Chroma/Qdrant/Pinecone, serve RAG queries with retrieval + generation + citations, choose embedding model, top_k, LLM model, domain filter, review_policy, rate limiting, auth per consumer needs — LearningHub, PROFESSOR-J, general, explorer, STEMMA-RAG — does NOT contain whole STEMMA, just connection layer, whole STEMMA remains in STEMMA repo
- STEMMA provides reference implementation: scripts/embed.py, rag.py, export_consumers.py, exports/embeddings.jsonl, vector_store/, adapters/python/ v0.2.0, webapp RAG playground, examples/external-rag/ — optional, INFO not FAIL, for convenience, demo, testing, but production embedding/RAG is consumer's job

**Therefore:** Embedding and RAG is CONSUMER's job, not STEMMA's job — STEMMA provides knowledge foundation + reference implementation as optional derived + consumer layer for convenience and demo, but production embedding and RAG is consumer's job (LearningHub, PROFESSOR-J, general, explorer, STEMMA-RAG) as connection layer out of STEMMA, not containing whole STEMMA, connecting via exports/knowledge.json + API + SDK + content_hash, with model selector like DeepSeek harness (local + frontier models) for both embedding and LLM.


## Guideline — How to Build Embedder and RAG That Imports From STEMMA Consistently (NEW 2026-09-21 — v1.0.0)

See **[GUIDELINE-EMBEDDER-RAG.md](GUIDELINE-EMBEDDER-RAG.md)** — authoritative 81KB guideline for consumers to build consistent embedder + RAG architecture that imports from STEMMA via file/API/SDK + content_hash.

**What it covers:**
- Direction we are going: comprehensive all-STEM mediocre (8 domains 97 subdomains 12 entity types 400-800 target) + clean separation Layer1 Canonical (NO embeddings/RAG, whole STEMMA), Layer2 Derived (YES embeddings as derived regenerable deterministic content-hash), Layer3 Consumer+RAG (YES RAG as consumer mechanism, can be out of STEMMA)
- New change already implemented (2026-09-21): template-registry v2.0.0 8 domains, embedding-registry v1.0.0 12 models local free + frontier with model selector like DeepSeek harness, consumer-registry v1.0.0 4 consumers LearningHub OpenAI Large 3072 GPT-4o top_k5 PROFESSOR-J BGE Large 1024 offline DeepSeek R1 free top_k10, API schema v2.1.0 OpenAPI 3.0.3, embed.py rag.py export_consumers.py adapter v0.2.0 /v2/embeddings /v2/rag/search POST /v2/rag/query /v2/export /openapi.yaml webapp RAG playground, examples/external-rag/ out-of-STEMMA proving embedding/RAG can be out as connection layer NOT whole STEMMA via file/API/SDK + content_hash
- Future plans: R1 NOW 400-800 + embeddings + RAG + consumer export + guideline + sample, R2 Math Layer + Governing Laws + Embeddings SOTA (BGE-M3, GTE, Jina, E5-Mistral, re-ranking, ColBERT, HyDE) + RAG Evaluation (retrieval precision, faithfulness, citation coverage, re-ranking, multi-hop, HyDE, self-RAG, evaluation dataset) + Consistent Architecture (TypeScript adapter, Python package stemma-rag, consistent import via file/API/SDK + content_hash, model selector, deterministic versioning, context building with citations, API, webapp playground, evaluation metrics) + Production API hosting, R3 Other Domains LATER + Production RAG + Hosted Vector Store Qdrant/Pinecone + Consistent Architecture Across All Consumers via guideline
- Embedder best practices: model selector like DeepSeek harness 12 models, chunking entity strategy 512 tokens deterministic, content-hash sha256(text+model_id+knowledge content_hash)[:16] versioned batch 32 normalize, vector store FAISS flat cosine meta.json v1.0.0, storage embeddings.jsonl + vector_store/
- RAG best practices: retriever vector search cosine FAISS top_k 5 LearningHub 10 PROFESSOR-J domain filter, context building definitions+connections+sources+source_refs+links+scores with citations, generator LLM model selector like DeepSeek harness 25 models DeepSeek R1 free Claude 3.5 Sonnet GPT-4o Gemini 2.5 Pro Llama 3.3 custom citation enforcement, full flow question->embedding->vector search->context->LLM->answer with citations, API /v2/rag/search GET POST /v2/rag/query, webapp RAG playground
- Sample in derived: inside STEMMA scripts/embed.py rag.py exports/embeddings.jsonl vector_store/ meta.json deterministic + out-of-STEMMA examples/external-rag/embed.py rag.py data/embeddings.jsonl data/vector_store/ out-of-STEMMA connection layer NOT whole STEMMA


