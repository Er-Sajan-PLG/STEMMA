# Guideline — Building Embedder and RAG System That Imports From STEMMA Consistently

**Status:** Authoritative, v1.0.0, comprehensive all-STEM mediocre, for consumers like LearningHub, PROFESSOR-J, general, explorer, STEMMA-RAG to build consistent and better architecture for embedder and RAG system that imports from STEMMA.

**Purpose:** You asked: "I need a guideline to build embedder and RAG system in STEMMA to better import from STEMMA, so that consumer can build a consistent and better architecture for embedder and RAG system. And also a sample of them in derived, which i think you already built i suppose."

**Answer:** YES, sample already built in derived (`scripts/embed.py`, `scripts/rag.py`, `examples/external-rag/`) and in reference implementation inside STEMMA (`exports/embeddings.jsonl`, `exports/vector_store/`, `adapters/python/` v0.2.0, `webapp/` RAG playground). Now this guideline explains how to build embedder and RAG system that imports from STEMMA consistently, with best practices, architecture, code samples, and future plans.

---

## 1. Direction We Are Going — Comprehensive All-STEM Mediocre + Clean Separation

### Previously: Minimal Physics, No Embeddings/RAG in Canonical

- Minimal physics v0.1: 70 entities physics only, no embeddings, no RAG, no consumer export, `ROADMAP.md` said "Not on roadmap: embeddings, database as source of truth" — meant **canonical** should never contain embeddings, correct
- Old 74 entities + 150 connections archived to `archive/beginning-74-entities/`, now 1 entity (metre) via PDF primary ingestion with HITL, deterministic scales, evolvable templates

### Now: Comprehensive All-STEM Mediocre + Clean Separation Canonical vs Derived vs Consumer

- **8 domains, 97 subdomains, 12 entity types, 400-800 target mediocre:** physics 12, chemistry 11, biology 14, earth-science 10, astronomy 8, computer-science 15, engineering 13, mathematics 14
- **Template registry v2.0.0:** `schema/template-registry.yaml` v2.0.0 comprehensive all-STEM with extraction rules for all domains, standard sources SI Brochure, IUPAC, CRC, HRW, Campbell, CLRS, Atkins, Carroll, embedding config, evolvable via `--evolve`
- **Explicit separation:**
  - **Layer 1: CANONICAL — STEMMA itself, whole STEMMA, NO embeddings/RAG:** `content/`, `connections/`, `sources/`, `schema/` — only Markdown+YAML with exact definitions, dual verification, governed_by, history, 8 relations, evidence — NO embeddings, vectors, .npy, embeddings.jsonl, vector_store/ — NEVER — `validate.py` NEVER checks embeddings — whole STEMMA is here
  - **Layer 2: DERIVED — YES embeddings here but as derived, regenerable, deterministic, content-hash, in exports/:** `knowledge.json` v2.1.0 content-hash, `embeddings.jsonl`, `vector_store/` FAISS meta.json + vectors.npy + ids.json versioned via content_hash + model id, `consumers/<consumer>/knowledge.<consumer>.json`, `openapi.yaml` — deterministic same content_hash + model → same embeddings, regenerable via `validate.py` + `embed.py`, `verify_all.py` INFO not FAIL
  - **Layer 3: CONSUMER + RAG PIPELINE — YES RAG here but as consumer mechanism, inevitable for usability, can be out of STEMMA:** `scripts/embed.py`, `rag.py`, `export_consumers.py`, `adapters/python/` v0.2.0 with `/v2/embeddings, /v2/rag/search, POST /v2/rag/query, /v2/export, /openapi.yaml`, `webapp/` RAG playground, `examples/external-rag/` OUT OF STEMMA — without RAG static JSON useless, with RAG queryable knowledge with citations for LearningHub, PROFESSOR-J — therefore RAG pipeline inevitable, but as consumer layer, not canonical

### New Change Already Implemented (2026-09-21)

- **Template registry v2.0.0:** 8 domains, 97 subdomains, 12 entity types, extraction rules, standard sources, embedding config
- **Embedding registry v1.0.0:** `schema/embedding-registry.yaml` v1.0.0 with 12 models — local free All-MiniLM 384 fast 80MB, MPNet 768 quality 420MB, BGE Large SOTA 1024 1.3GB best for RAG MTEB top, E5 Large 1024 retrieval, BGE Small 384 fast + frontier API OpenAI Large 3072 best quality MTEB 64.6, Small 1536 fast, Ada 002 legacy, Cohere embed-v3 1024, Gemini 004 768 free tier, NVIDIA NV-Embed SOTA 4096 free via NIM — **model selector like DeepSeek harness (local + frontier models)** with search, categories All/Frontier/Free/Local/SOTA/Fast, model cards FREE/FRONTIER/LOCAL/SOTA badges, custom input
- **Consumer registry v1.0.0:** `schema/consumer-registry.yaml` v1.0.0 with 4 consumers LearningHub (canonical physics/chem/bio/math, OpenAI Large 3072, GPT-4o RAG top_k 5), PROFESSOR-J (reviewed all 8 domains mediocre, BGE Large SOTA 1024 offline, FAISS, DeepSeek R1 free RAG top_k 10), general (all domains, All-MiniLM fast), explorer (3D graph) — domains, review_policy, entity_types, export_formats, embedding_model, api_access, rag config
- **API schema v2.1.0:** `schema/api.yaml` OpenAPI 3.0.3 with endpoints `/v2/stats`, `/v2/entities?domain=...`, `/v2/connections`, `/v2/search?q=...`, `/v2/embeddings?model=...`, `/v2/rag/search?q=...&top_k=...`, `POST /v2/rag/query`, `/v2/export?consumer=...`, `/openapi.yaml`
- **Embedder:** `scripts/embed.py` — generates embeddings deterministically same content_hash + model → same embeddings, tries sentence-transformers if installed else fake deterministic hash-based for demo, outputs embeddings.jsonl + vector_store/ FAISS meta.json + vectors.npy + ids.json versioned via content_hash + model id, batch_size 32 normalize true, chunking entity strategy max_tokens 512 overlap 50, for LearningHub, PROFESSOR-J, model selector like DeepSeek harness (local + frontier models)
- **RAG:** `scripts/rag.py` — vector search cosine similarity + context building definitions + connections + sources + source_refs + links + LLM generation with **model selector like DeepSeek harness (local + frontier models: DeepSeek R1 free, Claude 3.5 Sonnet, GPT-4o, Gemini 2.5 Pro, Llama 3.3, custom via OpenRouter)** + citations, consumer-specific models, flow question → embedding → vector search top_k → context → LLM → answer with citations, API /v2/rag/search GET + /v2/rag/query POST, webapp RAG playground
- **Consumer export:** `scripts/export_consumers.py` — filters knowledge.json by consumer domains/review_policy/entity_types and generates consumer-specific exports in `exports/consumers/<consumer>/`, plus embeddings via embed.py
- **Adapter v0.2.0:** `adapters/python/stemma_adapter/server.py` v0.2.0 with new endpoints /v2/embeddings, /v2/rag/search, POST /v2/rag/query, /v2/export, /openapi.yaml, for LearningHub, PROFESSOR-J
- **Webapp:** `webapp/server.py` with new endpoints /api/models/embedding, /api/rag/search, /api/embeddings, /api/export, /api/openapi, POST /api/rag/query, plus `webapp/static/index.html` RAG Playground section with embedding model selector like DeepSeek harness (local + frontier models) + LLM selector + domain filter 8 domains + consumer selector + top_k + question + Search + Query buttons + citations + consumer export buttons, plus `app.js` EMBEDDING_MODELS catalog 10 models + renderEmbeddingModelList + renderRAGLLMModelList + ragSearch + ragQuery + generateEmbeddings + exportConsumer, plus `style.css` RAG playground CSS
- **Sample out of STEMMA:** `examples/external-rag/` with README.md + embed.py + rag.py that are OUT OF STEMMA, connection layer, NOT whole STEMMA, proving embedding and RAG can be out of STEMMA, connecting via file/API/SDK + content_hash, does NOT contain whole STEMMA, just connection layer
- **Docs:** All docs updated with explicit separation canonical vs derived vs consumer, whose job is embedding/RAG (CONSUMER's job, not STEMMA's, STEMMA provides reference), can embedding/RAG be out of STEMMA (YES, connection layer, NOT whole STEMMA, how connect via file/API/SDK + content_hash), plus new docs EMBEDDINGS.md, RAG.md, API.md, CONSUMERS.md updated, ARCHITECTURE.md, GOVERNANCE.md, VISION.md, ROADMAP.md, TESTING.md, VERSIONING.md, IMPLEMENTATION-STATUS.md, README.md, docs/README.md, AGENTS.md

### Future Changes Plan/Planned

- **R1 — Comprehensive All-STEM Mediocre v0.1 NOW:** Grow from 1 entity (metre via HITL) to 400-800 mediocre across 8 domains via PDF primary ingestion with HITL, deterministic templates v2.0.0, model selector like DeepSeek harness (local + frontier models), embeddings, RAG, consumer export — 500+ connections canonical with evidence, explorer clean 3D with domain filter 8 domains, adapter v0.2.0 with embeddings + RAG + consumer export + OpenAPI, embeddings via embed.py with model selector like DeepSeek harness (local + frontier models), vector_store/ FAISS deterministic content-hash versioned, RAG via rag.py with vector search + LLM with citations, consumer-specific exports for LearningHub and PROFESSOR-J, webapp with RAG playground, all verification green including hitl_check + embed + rag + export_consumers
- **R2 — Math Layer + Governing Laws Expansion + Evolvable Domains + Embeddings SOTA + RAG Evaluation:**
  - Expand governing registry to 23 laws as entities with historical timeline via HITL
  - Evolve template-registry.yaml v2.0.0 to more subdomains via `python3 scripts/evolvable_template.py --evolve --new-domain medicine` without code change — scales to 1000s PDFs, any domain
  - Embeddings: add more models (e.g., BGE-M3 multilingual, GTE, Jina), evaluate retrieval precision for LearningHub queries "What is Newton's second law?" and PROFESSOR-J queries "Explain photosynthesis" — optimize chunking (entity strategy vs sliding window vs hierarchical), add re-ranking (cross-encoder), add multi-vector (ColBERT)
  - RAG: evaluate retrieval precision + answer faithfulness + citation coverage, add re-ranking, add multi-hop via prerequisites closure (`/v2/prerequisites/{id}`), add query expansion, add HyDE, add self-RAG, add citation enforcement
  - Consumer export: add more consumers, add TypeScript adapter `adapters/typescript/`, add webhooks, add GraphQL API
  - Production API hosting at https://api.stemma.example.com/v2 with auth api_key, rate limiting, OpenAPI, SDK generation
- **R3 — Other Domains LATER (Evolvable) + Production RAG + Hosted Vector Store:**
  - Medicine, economics, etc. via evolvable template-registry.yaml v2.0.0 — no code change, just YAML
  - Production RAG with vector store Qdrant/Pinecone cloud, with LearningHub, PROFESSOR-J production, with monitoring, evaluation, feedback loop
  - Hosted vector store with content_hash versioning, deterministic regeneration, multi-model support
  - No legacy, this is comprehensive all-STEM mediocre with HITL, deterministic scales, evolvable, model selector like DeepSeek harness (local + frontier models), embeddings, RAG, consumer export, clean separation canonical vs derived vs consumer, embedding and RAG is consumer's job, not STEMMA's, but STEMMA provides reference implementation

---

## 2. Guideline — Building Embedder That Imports From STEMMA Consistently

### What is Embedder? Why Needed?

**Embedder = converts STEMMA entity text into vector (list of floats) for semantic search**

- **Without embedder:** Only keyword search — query "force" finds entities with word "force" in definition, but query "What is push?" (no word "force") finds nothing, even though "push" and "force" are semantically similar
- **With embedder:** Semantic search — query "What is push?" → embedding model → query vector → cosine similarity over FAISS → retrieves "Force" entity with score 0.85, even though query didn't contain word "force", because "push" and "force" are similar in embedding space

**Embedder is connection layer, NOT whole STEMMA:** Does NOT contain whole STEMMA — contains vectors DERIVED from STEMMA definitions, e.g., metre chunk → All-MiniLM 384 dim → vector [0.12, -0.34, ...] — semantic fingerprint for similarity search, stored in embeddings.jsonl as {entity_id, model, dimensions, vector, content, content_hash} — regenerable from knowledge.json + model id, deterministic same content_hash + model → same vector — NOT whole STEMMA, just derived vectors

### How to Import From STEMMA Consistently — 3 Ways (File, API, SDK) — Via content_hash

#### Option A: File-based Import — Simplest, Deterministic, No Server, Recommended for Getting Started

**STEMMA provides:** `exports/knowledge.json` v2.1.0 deterministic content-hash sha256:2c007..., contains entities, connections, sources, content_hash, versions — this IS the interface, whole STEMMA as JSON, versioned, deterministic, no wall clock

**Consumer (LearningHub, PROFESSOR-J, STEMMA-RAG) imports via file:**

```python
# In consumer repo, out of STEMMA — file-based import
import json, pathlib
STEMMA_EXPORT = pathlib.Path("../STEMMA/exports/knowledge.json")  # or copy, or git submodule, or download from release
export = json.loads(STEMMA_EXPORT.read_text(encoding='utf-8'))
content_hash = export.get('content_hash')  # e.g., "sha256:2c007fc6e235b0ac73a823cec3f9002b2ef62219c9bf89e1ff7a70b91975b764"
entities = export.get('entities', [])  # list of entities with id, name, domain, subdomain, type, definition, provenance, source_refs, external_ids
print(f"Loaded {len(entities)} entities from STEMMA content_hash {content_hash} — whole STEMMA is in STEMMA repo's content/, this consumer only has vectors + index, NOT whole STEMMA, just connection layer")

# Check content_hash to know if embeddings need recompute — deterministic same content_hash + model → same embeddings
# If content_hash changed (new entities added via HITL in STEMMA), recompute embeddings
```

**Best practice:** Store content_hash with embeddings, e.g., embedding record `content_hash = sha256(text + model_id + knowledge.json content_hash)[:16]` — ensures deterministic same content + model → same embeddings, versioned, can detect when STEMMA updated and embeddings need recompute

**Sample in derived:** `scripts/embed.py` does file-based import from `exports/knowledge.json`, chunks entities, generates embeddings, writes `exports/embeddings.jsonl` + `exports/vector_store/` — reference implementation inside STEMMA for convenience, but can be out of STEMMA as in `examples/external-rag/embed.py` which is OUT OF STEMMA, connection layer, NOT whole STEMMA, connecting via file `../exports/knowledge.json` + content_hash

#### Option B: API-based Import — REST API, OpenAPI Schema, for LearningHub, PROFESSOR-J Production

**STEMMA provides:** Adapter server v0.2.0 serves `exports/knowledge.json` via REST API with OpenAPI schema `schema/api.yaml` v2.1.0:
- `GET /v2/stats` — stats entity_count, connection_count, source_count, content_hash, versions, domains 8
- `GET /v2/entities?domain=physics&subdomain=mechanics&type=quantity&status=canonical&limit=1000` — list entities filtered by domain, subdomain, type, status
- `GET /v2/entities/{id}` — get entity e.g., stemma:phys.metre
- `GET /v2/search?q=force&domain=physics&limit=10` — keyword search
- `GET /openapi.yaml` — OpenAPI schema

**Consumer imports via API:**

```python
# In consumer repo, out of STEMMA — API-based import
import requests
# Get stats to get content_hash — connection via content_hash
stats = requests.get("http://stemma-api:8080/v2/stats").json()
content_hash = stats["content_hash"]
print(f"STEMMA content_hash {content_hash} — whole STEMMA is in STEMMA repo, this consumer only has vectors + index, NOT whole STEMMA")

# Get entities via API — file-based alternative
resp = requests.get("http://stemma-api:8080/v2/entities?domain=physics&status=canonical&limit=1000")
entities = resp.json()  # list of entities
# Or filtered by consumer: LearningHub canonical physics/chem/bio/math, PROFESSOR-J reviewed all 8 domains mediocre
resp = requests.get("http://stemma-api:8080/v2/export?consumer=learninghub&format=json")
learninghub_export = resp.json()
entities = learninghub_export["entities"]  # filtered for LearningHub

# Check content_hash to know if embeddings need recompute
# If content_hash changed, recompute embeddings externally
```

**Best practice:** Call `/v2/stats` to get content_hash before generating embeddings, store content_hash with embeddings, recompute if content_hash changed — deterministic same content_hash + model → same embeddings

**Sample in derived:** `adapters/python/stemma_adapter/server.py` v0.2.0 implements API with /v2/entities, /v2/stats, /v2/export?consumer=..., /openapi.yaml — reference implementation, but production consumer can have its own API client out of STEMMA

#### Option C: SDK-based Import — Python Adapter, Future TypeScript, Recommended for Consistency

**STEMMA provides:** `adapters/python/` pip install ./adapters/python — provides Stemma class that loads knowledge.json and gives stable API without validator stack:

```python
from stemma_adapter import Stemma
stemma = Stemma.from_file("exports/knowledge.json")  # file-based
# or
stemma = Stemma.from_api("http://localhost:8080")  # API-based, if SDK supports from_api (future)
print(stemma.stats)  # entity_count, connection_count, source_count, content_hash, versions
print(stemma.search("force", domain="physics", limit=5))
print(stemma.resolve("stemma:phys.metre"))
print(stemma.entities(domain="physics", status="canonical", limit=100))
```

**Consumer imports via SDK:**

```python
# In consumer repo, out of STEMMA — SDK-based import, recommended for consistency
from stemma_adapter import Stemma
import sys
sys.path.insert(0, "../STEMMA-RAG")  # external RAG repo out of STEMMA
from stemma_rag import StemmaRAG, StemmaEmbedder  # external embedder/RAG out of STEMMA

# Load STEMMA via SDK — consistent interface
stemma = Stemma.from_file("../STEMMA/exports/knowledge.json")
content_hash = stemma.export["content_hash"]
print(f"Loaded {len(stemma.export['entities'])} entities from STEMMA content_hash {content_hash} — whole STEMMA is in STEMMA repo, this consumer only has vectors + index, NOT whole STEMMA")

# Build embedder out of STEMMA — consistent architecture
embedder = StemmaEmbedder.from_stemma(stemma, embedding_model="BAAI/bge-large-en-v1.5", chunking_strategy="entity", max_tokens=512, overlap=50, batch_size=32, normalize=True)
embeddings = embedder.generate()  # generates embeddings.jsonl + vector_store/ FAISS out of STEMMA, deterministic same content_hash + model → same embeddings, versioned via content_hash + model id
# Or
# embedder = StemmaEmbedder(embedding_model="openai/text-embedding-3-large", api_key="...", provider="openai")
# embeddings = embedder.generate(stemma.entities(domain="physics"))

# Check content_hash to know if embeddings need recompute — consistent
if embedder.needs_recompute(content_hash):
    embeddings = embedder.generate()
```

**Best practice:** Use SDK for consistent import, store content_hash with embeddings, use `needs_recompute(content_hash)` to check if STEMMA updated and embeddings need recompute — deterministic same content_hash + model → same embeddings

**Sample in derived:** `adapters/python/stemma_adapter/` provides SDK, `examples/external-rag/` uses file-based import but could use SDK — reference implementation inside STEMMA for convenience, but production consumer can have its own embedder out of STEMMA using SDK

### How to Build Embedder Consistently — Best Practices

#### 1. Model Selection — Model Selector Like DeepSeek Harness (Local + Frontier Models)

**Use embedding-registry.yaml v1.0.0 as reference — 12 models, local free + frontier API, model selector like DeepSeek harness (local + frontier models) with search, categories All/Frontier/Free/Local/SOTA/Fast, model cards FREE/FRONTIER/LOCAL/SOTA badges, dimensions, custom input:**

- **Local free (offline, free, deterministic, no API key, no cost, good for mediocre all-domain):**
  - `sentence-transformers/all-MiniLM-L6-v2` — 384 dim, 80MB, fast 5x faster than MPNet, default for quick RAG, general consumer
  - `sentence-transformers/all-mpnet-base-v2` — 768 dim, 420MB, high quality
  - `BAAI/bge-large-en-v1.5` — 1024 dim, 1.3GB, SOTA local MTEB top, best for RAG, PROFESSOR-J prefers offline SOTA
  - `intfloat/e5-large-v2` — 1024 dim, retrieval-optimized, query prefix
  - `BAAI/bge-small-en-v1.5` — 384 dim, 133MB, fast fallback

- **Frontier API (via OpenRouter, OpenAI, Cohere, Google, NVIDIA NIM):**
  - `openai/text-embedding-3-large` — 3072 dim, best quality MTEB 64.6, $0.00013/1k tokens, LearningHub prefers high quality
  - `openai/text-embedding-3-small` — 1536 dim, fast frontier $0.00002/1k
  - `cohere/embed-english-v3.0` — 1024 dim
  - `google/text-embedding-004` — 768 dim, free tier
  - `nvidia/nv-embed-v1` — 4096 dim, SOTA free via NIM, MTEB top

**Best practice for consistent architecture:**
- Define `embedding-registry.yaml` in consumer repo, similar to STEMMA's `schema/embedding-registry.yaml` v1.0.0, with models, categories, dimensions, provider, free, local, description, use_case, cost
- Implement model selector like DeepSeek harness: search bar, category tabs All/Frontier/Free/Local/SOTA/Fast, model cards with badges, dimensions, custom model input any frontier or your own fine-tuned via OpenRouter/NVIDIA NIM/OpenAI-compatible
- Consumer-specific model choice: LearningHub prefers OpenAI Large 3072 high quality, PROFESSOR-J prefers BGE Large SOTA 1024 offline, general prefers All-MiniLM fast local — store consumer-specific preferred model in consumer-registry.yaml or consumer config
- Default model: All-MiniLM fast local for quick RAG, fallback BGE Small
- Allow custom model input: any model string, frontier or your own, via OpenRouter/NVIDIA NIM/OpenAI-compatible

**Sample in derived:** `scripts/embed.py` supports `--model` param with model ID from embedding-registry, `--list-models` lists 12 models, `--for-consumer learninghub` uses LearningHub preferred model OpenAI Large, `--for-consumer professor-j` uses BGE Large — reference implementation, but consumer can have its own model selector out of STEMMA

#### 2. Chunking Strategy — Entity Strategy, Deterministic, Consistent

**Use entity strategy, not sliding window, for STEMMA:**

- **Strategy:** entity — each entity is one chunk (definition + name + domain + subdomain + symbol + unit + provenance source + link) — because STEMMA entities are already well-defined, with exact definitions, dual verification, not long documents that need sliding window
- **Max tokens:** 512 — enough for entity definition (metre definition is ~50 tokens, plus name, domain, symbol, unit, source)
- **Overlap:** 50 — for entity strategy, overlap not needed much, but for sliding window fallback, 50 tokens overlap
- **Separators:** ["\n\n", "\n", ". ", " "] — for sliding window fallback
- **Why entity strategy:** STEMMA entities are already chunked — each entity is one concept, one quantity, one law, etc., with definition, not long PDF that needs chunking — so entity = chunk is natural, deterministic, consistent

**Best practice for consistent architecture:**
- Define chunking config in consumer repo, similar to STEMMA's embedding config: `chunking: {strategy: entity, max_tokens: 512, overlap: 50, separators: ["\n\n", "\n", ". ", " "]}`
- Implement `chunk_entity(entity)` function that builds text for embedding: `f"{name} ({id}) Domain: {domain}/{subdomain} Type: {type} Definition: {definition} Symbol: {symbol} Unit: {unit} Source: {provenance.source} Link: {provenance.link}"` — include name, id, domain, subdomain, type, definition, symbol, unit, source, link — for retrieval with citations
- Deterministic: same entity → same chunk text → same embedding (given same model) — no randomness, no wall clock

**Sample in derived:** `scripts/embed.py` has `chunk_entity(entity)` that builds text from name, id, domain, subdomain, type, definition, symbol, unit — reference implementation, but consumer can have its own chunking out of STEMMA

#### 3. Deterministic, Content-Hash Versioning, Batch Size, Normalization — Consistent

**Best practices for consistent architecture:**

- **Deterministic:** Same knowledge.json content_hash + model id + entity text → same embedding vector — no randomness, no wall clock, batch_size 32, normalize true — ensures same input → same output any time
- **Content-hash versioning:** Store content_hash with embeddings, e.g., embedding record `content_hash = sha256(text + model_id + knowledge.json content_hash)[:16]` — versioned via knowledge.json content_hash + model id, deterministic, can detect when STEMMA updated (content_hash changed) and embeddings need recompute — e.g., `meta.json` in vector_store/ has `content_hash` same as knowledge.json content_hash
- **Batch size:** 32 — for local models, batch_size 32 for encoding, good for mediocre 400-800 entities
- **Normalization:** true — normalize embeddings to unit length for cosine similarity — `normalize_embeddings=True` in sentence-transformers
- **Recompute on:** knowledge.json content_hash change, model change — if content_hash changed (new entities added via HITL in STEMMA) or model changed (consumer switches from All-MiniLM to BGE Large), recompute embeddings

**Sample in derived:** `scripts/embed.py` has `deterministic_hash(text, model_id, content_hash)` that computes sha256(text + model_id + content_hash)[:16], writes embeddings.jsonl with content_hash, writes vector_store/meta.json with content_hash, entity_count, model, dimensions, created_at deterministic "no wall clock", version 1.0.0, type faiss, index_type flat, metric cosine — reference implementation, but consumer can have its own deterministic versioning out of STEMMA

#### 4. Vector Store — FAISS, Chroma, Qdrant, Pinecone — Consistent

**Best practices for consistent architecture:**

- **Type:** faiss (default) — flat index, cosine metric, local, deterministic, good for mediocre 400-800 entities — for larger (10k+ entities), use ivf or hnsw
- **Path:** `exports/vector_store/` or `data/vector_store/` out of STEMMA — meta.json + vectors.npy (or vectors.json if numpy not available) + ids.json — meta.json with model, dimensions, content_hash, entity_count, created_at deterministic no wall clock, version 1.0.0, type faiss, index_type flat, metric cosine
- **Alternatives:** chroma (path `exports/chroma/` or `data/chroma/`), qdrant (local or cloud), pinecone (cloud) — for production LearningHub, PROFESSOR-J might use Qdrant/Pinecone cloud with content_hash versioning
- **Metric:** cosine — for normalized embeddings, cosine similarity
- **Versioning:** Via content_hash + model id, deterministic, same knowledge.json content_hash + model id → same FAISS index

**Sample in derived:** `scripts/embed.py` writes vector_store/ with meta.json + vectors.npy (if numpy available) + ids.json, or vectors.json if numpy not available — reference implementation, but consumer can have its own vector store out of STEMMA, e.g., `examples/external-rag/embed.py` writes `data/vector_store/` out of STEMMA, connection layer, NOT whole STEMMA

#### 5. Storage — embeddings.jsonl + vector_store/ — Derived, Regenerable, Versioned

**Best practices:**

- **embeddings.jsonl:** JSONL per entity — `{entity_id, model, dimensions, vector, content, content_hash}` — e.g., 1 line per entity, entity_id `stemma:phys.metre`, model `BAAI/bge-large-en-v1.5`, dimensions 1024, vector `[0.12, -0.34, ...]` 1024 floats, content chunk text, content_hash versioned — derived, regenerable, versioned
- **vector_store/:** meta.json + vectors.npy + ids.json — meta.json with model, dimensions, content_hash, entity_count, created_at deterministic no wall clock, version 1.0.0, type faiss, index_type flat, metric cosine — vectors.npy numpy array shape (entity_count, dimensions) float32, ids.json list of entity IDs — derived, regenerable, versioned
- **Derived, not canonical:** embeddings.jsonl + vector_store/ live only in exports/ or data/ out of STEMMA, NOT in content/, connections/, sources/ — regenerable via embed.py, versioned via content_hash + model id, deterministic, INFO not FAIL in verify_all.py

**Sample in derived:** `exports/embeddings.jsonl` (1 embeddings now), `exports/vector_store/` (meta.json + vectors.json + ids.json), `examples/external-rag/data/embeddings.jsonl` + `data/vector_store/` out of STEMMA — reference implementations

---

## 3. Guideline — Building RAG System That Imports From STEMMA Consistently

### What is RAG? Why Needed?

**RAG = Retrieval-Augmented Generation — retrieval + generation with citations, grounded in STEMMA**

- **Without RAG:** Static JSON, consumer must manually search via keyword or build own RAG, LearningHub students can't ask "What is Newton's second law?" and get answer with citations, PROFESSOR-J AI professor can't answer STEM questions
- **With RAG:** Queryable knowledge with citations, grounded answers, retrieval precision, faithfulness, citation coverage — consumer queries via /v2/rag/query or SDK StemmaRAG, gets answer grounded in STEMMA entities with citations (source_refs + links)

**RAG is connection layer, NOT whole STEMMA:** Does NOT contain whole STEMMA — contains retrieval logic (embedding query → cosine similarity over FAISS → top_k entities with scores) + generation logic (build context with definitions + connections + sources + source_refs + links → LLM prompt → answer with citations) — grounded in STEMMA but doesn't contain whole STEMMA, only references entity IDs and definitions as context, whole STEMMA remains in content/

### How to Import From STEMMA Consistently for RAG — 3 Ways (File, API, SDK) — Via content_hash — Same as Embedder

**Same 3 ways as embedder — file-based, API-based, SDK-based — via content_hash — see embedder guideline above — for RAG, import entities + connections + sources from STEMMA, then build retriever + generator out of STEMMA**

### How to Build RAG Consistently — Best Practices

#### 1. Retriever — Vector Search Cosine Similarity Over FAISS — Consistent

**Best practices:**

- **Embedding query:** Same embedding model as used for entities — e.g., if entities embedded with BGE Large 1024, query also embedded with BGE Large 1024 — ensures same embedding space, cosine similarity meaningful
- **Vector search:** Cosine similarity over FAISS (or Chroma, Qdrant, Pinecone) — `index.search(query_vec, k=top_k)` — returns scores and ids — e.g., query "What is Newton's second law?" → query vector → FAISS search top_k 5 → retrieved [newtons-second-law score 0.90, force score 0.85, mass score 0.82, acceleration score 0.80, metre score 0.10] — top_k relevant
- **Top K:** 5 for LearningHub (canonical physics/chem/bio/math, focused), 10 for PROFESSOR-J (reviewed all 8 domains mediocre, broader) — consumer-specific
- **Domain filter:** Optional — e.g., `domain=physics` for physics queries, `domain=biology` for biology queries — filter embeddings by domain before search or after search
- **Deterministic:** Same query + same knowledge.json content_hash + same embedding model + same FAISS index → same retrieved entities with same scores — no randomness, no wall clock, deterministic

**Sample in derived:** `scripts/rag.py` has `vector_search(query, top_k=5, model_id=None, domain=None)` that loads embeddings from `exports/embeddings.jsonl`, filters by domain and model_id if needed, embeds query via `get_embedding_for_query(query, model_id, dim)` that tries sentence-transformers if installed else fake deterministic hash-based for demo, computes cosine similarity, sorts, returns top_k with entity, score, content, entity_id — reference implementation, but consumer can have its own retriever out of STEMMA, e.g., `examples/external-rag/rag.py` has `vector_search(query, top_k=5)` out of STEMMA, connection layer, NOT whole STEMMA

#### 2. Context Building — Definitions + Connections + Sources + Source_Refs + Links — Consistent, With Citations

**Best practices:**

- **Context:** Build context from retrieved entities with definitions + connections + sources + source_refs + links + scores — e.g.:
  ```
  STEMMA Knowledge Foundation — comprehensive all-STEM, mediocre coverage, with citations

  1. Newton's Second Law (stemma:phys.newtons-second-law) — Domain: physics/mechanics Type: law
     Definition: Newton's second law states F=ma, force equals mass times acceleration...
     Source: HRW 12th Ch5 p112 Link: https://... Writer: human:curator.001
     Source refs: halliday, nistsi
     Score: 0.90

  2. Force (stemma:phys.force) — Domain: physics/mechanics Type: quantity
     Definition: Force is...
     Source: HRW 12th Ch5 p112 Link: https://...
     Source refs: halliday
     Score: 0.85
  ...
  ```
- **Why definitions + connections + sources:** Definitions provide exact scientific definitions with agreed status + reference, connections provide relationships (e.g., force mathematically_requires mass, acceleration), sources provide verifiability (url/doi/isbn + writer human:*), source_refs + links provide citations for answer
- **Citations:** Every retrieved entity has source_refs + link + provenance — for answer citations, e.g., "Force is defined as... [citation: stemma:phys.force source_ref halliday link https://...]"
- **Deterministic:** Same retrieved entities → same context — no randomness

**Sample in derived:** `scripts/rag.py` has `build_context(retrieved)` that builds context from retrieved entities with name, id, domain/subdomain, type, definition, provenance source + link + writer, source_refs, score — reference implementation, but consumer can have its own context building out of STEMMA

#### 3. Generator — LLM With Model Selector Like DeepSeek Harness (Local + Frontier Models) + Citations — Consistent

**Best practices:**

- **LLM model selection — model selector like DeepSeek harness (local + frontier models) with search, categories All/Frontier/Reasoning/Free/Custom/Local/SOTA, model cards FREE/FRONTIER/LOCAL/SOTA badges, custom input:**
  - Local: Llama 3.3 70B via Ollama, or local fine-tuned
  - Frontier API: DeepSeek R1 free 671B reasoning, DeepSeek V3 free 671B, Claude 3.5 Sonnet frontier, Claude 3 Opus reasoning, GPT-4o frontier multimodal, o1 reasoning frontier, Gemini 2.5 Pro frontier, Gemini 2.0 Flash free, Llama 3.3 70B free, custom via OpenRouter/NVIDIA NIM/OpenAI-compatible
  - Consumer-specific: LearningHub prefers GPT-4o frontier multimodal for student queries, PROFESSOR-J prefers DeepSeek R1 free 671B reasoning for AI professor with reasoning, general prefers custom or free
  - Default: DeepSeek R1 free for reasoning, or custom
  - Allow custom model input: any model string, frontier or your own fine-tuned

- **LLM prompt with context + question + citation enforcement:**
  ```
  You are STEMMA AI professor — comprehensive all-STEM, mediocre coverage, with citations.

  Context retrieved from STEMMA knowledge foundation (comprehensive all-STEM, 8 domains, 97 subdomains, 12 entity types, deterministic, content-hash, HITL, with citations):

  {context}

  Question: {question}

  Instructions:
  - Answer question based ONLY on context, with citations (entity_id + source_ref + link)
  - Every claim must have citation from context (e.g., "Force is defined as... [citation: stemma:phys.force source_ref halliday link https://...]")
  - If context doesn't contain answer, say "I don't know based on STEMMA context" — don't hallucinate
  - Provide answer with citations, grounded in STEMMA, with agreed status + reference if applicable (e.g., metre definition with Exact: c=299,792,458 m/s Agreed per BIPM 2019)
  - For LearningHub: focused, concise, with citations for students
  - For PROFESSOR-J: detailed, with reasoning, with citations across 8 domains mediocre, with connections

  Answer:
  ```

- **Citations:** LLM must include citations from context (entity_id + source_ref + link) for every claim — e.g., "Newton's second law states F=ma [citation: stemma:phys.newtons-second-law source_ref halliday link https://...] Force is defined as... [citation: stemma:phys.force source_ref halliday link https://...]" — ensures answer faithfulness, grounded in STEMMA, verifiable via link+source_refs+external_ids triple verification

- **Deterministic (if temperature 0):** Same context + same question + same LLM model with temperature 0 → same answer with same citations — but LLM generation may be non-deterministic unless temperature 0, so version answer via content_hash + model_used + embedding_model_used + question + top_k

**Sample in derived:** `scripts/rag.py` has `call_llm(prompt, model_id, context, question)` that tries webapp providers if available, else fake deterministic demo answer if no API key — reference implementation, but consumer can have its own generator out of STEMMA with real LLM API calls via OpenRouter/NVIDIA NIM/OpenAI

#### 4. RAG Query — Full Flow Question → Embedding → Vector Search → Context → LLM → Answer With Citations — Consistent

**Best practices — full flow:**

```
User question ("What is Newton's second law?") 
→ embedding via embedding model (e.g., BAAI/bge-large-en-v1.5 1024 dim SOTA local, or OpenAI text-embedding-3-large 3072 dim frontier) — same model as entities
→ vector search top_k (e.g., 5) cosine similarity over FAISS vector_store/ (vectors.npy + ids.json, meta.json content_hash versioned) — deterministic same query + same content_hash + same model + same FAISS → same retrieved
→ retrieved entities: [stemma:phys.newtons-second-law score 0.90, stemma:phys.force score 0.85, stemma:phys.mass score 0.82, ...] with content (definition + domain + subdomain + type + symbol + unit + provenance source + link + source_refs) — connection layer, NOT whole STEMMA
→ build context: "STEMMA Knowledge Foundation — comprehensive all-STEM, mediocre coverage, with citations\n1. Newton's Second Law (stemma:phys.newtons-second-law) — Domain: physics/mechanics Type: law\n   Definition: Newton's second law states F=ma...\n   Source: HRW 12th Ch5 p112 Link: https://... Writer: human:curator.001\n   Source refs: halliday, nistsi\n   Score: 0.90\n..."
→ LLM prompt: "You are STEMMA AI professor...\nContext: {context}\nQuestion: {question}\nAnswer with citations..."
→ call LLM with model selector like DeepSeek harness (local + frontier models: DeepSeek R1 free via OpenRouter, or Claude 3.5 Sonnet, GPT-4o, Gemini 2.5 Pro, Llama 3.3, custom) — in demo, fake deterministic answer if no API key, in production real LLM via OpenRouter/NVIDIA NIM/OpenAI
→ answer: "Based on STEMMA knowledge foundation...\nNewton's second law states F=ma... [citations: stemma:phys.newtons-second-law source_ref halliday link ...]\nForce is defined as... [citations: stemma:phys.force source_ref halliday link ...]\nCitations: - stemma:phys.newtons-second-law source_ref halliday link ...\n- stemma:phys.force source_ref halliday link ..."
→ return {question, answer, citations [{entity_id, source_ref, link}], retrieved_entities [{entity, score, content}], model_used, embedding_model_used, content_hash, top_k, domain, consumer}
```

**Best practices for consistent architecture:**

- Define RAG config in consumer repo, similar to STEMMA's consumer-registry.yaml RAG config: `rag: {enabled: true, top_k: 5, model: openai/gpt-4o, fallback_models: [anthropic/claude-3.5-sonnet, ...], embedding_model: openai/text-embedding-3-large}`
- Implement `rag_query(question, top_k=5, model_id="deepseek/deepseek-r1:free", embedding_model=None, domain=None, consumer="general")` function that does full flow — file-based, API-based, or SDK-based import from STEMMA, vector search, context building, LLM call, citations
- Consumer-specific RAG: LearningHub top_k 5 GPT-4o, PROFESSOR-J top_k 10 DeepSeek R1 free fallback Claude 3.5 Sonnet/GPT-4o/Gemini 2.5 Pro, general top_k 5 custom
- Version RAG answer via content_hash + model_used + embedding_model_used + question + top_k — deterministic same question + same knowledge + same models → same retrieved + same context (LLM generation may be non-deterministic unless temperature 0)
- Evaluation: retrieval precision top_k relevant, answer faithfulness grounded in retrieved entities, citation coverage every claim has source_ref + link — e.g., for query "Newton second law", top 5 should include newtons-second-law, force, mass, acceleration, with scores >0.7, answer should have citations for every claim

**Sample in derived:** `scripts/rag.py` has `rag_query(question, top_k=5, model_id="deepseek/deepseek-r1:free", embedding_model=None, domain=None, consumer="general")` that does full flow — file-based import from exports/knowledge.json, vector_search, build_context, call_llm, citations — reference implementation, but consumer can have its own RAG out of STEMMA, e.g., `examples/external-rag/rag.py` has `rag_query(question, top_k=5, model_id="deepseek/deepseek-r1:free")` out of STEMMA, connection layer, NOT whole STEMMA, proving RAG can be out of STEMMA

#### 5. API — /v2/rag/search GET + /v2/rag/query POST — Consistent

**Best practices:**

- Implement API endpoints in consumer's RAG service, similar to STEMMA's adapter v0.2.0 and webapp:
  - `GET /v2/rag/search?q=...&top_k=...&model=...&domain=...` — vector search, no LLM, returns query, top_k, model, results with entity, score, content
  - `POST /v2/rag/query` — full RAG, body {question, top_k, model, embedding_model, domain, consumer} → {question, answer, citations, retrieved_entities, model_used, embedding_model_used, content_hash}
  - `GET /v2/embeddings?model=...&id=...&domain=...&limit=...` — embeddings with model selector like DeepSeek harness (local + frontier models)
  - `GET /v2/export?consumer=...&format=...&review_policy=...` — consumer-specific filtered export
  - `GET /openapi.yaml` — OpenAPI schema
- OpenAPI schema: Define OpenAPI 3.0.3 schema for RAG endpoints, similar to STEMMA's `schema/api.yaml` v2.1.0
- Auth: none for local, api_key for LearningHub/PROFESSOR-J, bearer for frontier models via OpenRouter

**Sample in derived:** `adapters/python/stemma_adapter/server.py` v0.2.0 implements /v2/rag/search GET and POST /v2/rag/query and /v2/embeddings and /v2/export and /openapi.yaml — reference implementation, but consumer can have its own API out of STEMMA

#### 6. Webapp RAG Playground — Model Selector Like DeepSeek Harness (Local + Frontier Models) — Consistent

**Best practices for consistent architecture in webapp RAG playground:**

- Embedding model selector like DeepSeek harness (local + frontier models): search bar, category tabs All/Frontier/Free/Local/SOTA/Fast, model cards FREE/FRONTIER/LOCAL/SOTA badges, dimensions, custom input, with 10 embedding models All-MiniLM 384 fast, BGE Large SOTA 1024, OpenAI Large 3072, NVIDIA NV-Embed 4096 SOTA free
- LLM model selector like DeepSeek harness (local + frontier models): search bar, category tabs All/Frontier/Reasoning/Free/Custom, model cards FREE/FRONTIER/REASONING badges, with 25 frontier models DeepSeek R1 free, Claude 3.5 Sonnet, GPT-4o, Gemini 2.5 Pro, Llama 3.3 70B free, custom input
- Domain filter: 8 domains dropdown physics, chemistry, biology, earth-science, astronomy, computer-science, engineering, mathematics + all
- Consumer selector: LearningHub, PROFESSOR-J, general
- Top K slider: 1-20
- Question input textarea
- Search button (vector search no LLM) + Query button (full RAG retrieval + LLM with citations) + Generate Embeddings button (embed.py) + Export LearningHub/PROFESSOR-J buttons + OpenAPI button
- Results: retrieved entities with scores + content + domain + type + source + link, answer with citations, citations list with entity_id + source_ref + link, model_used, embedding_model_used, content_hash

**Sample in derived:** `webapp/static/index.html` has RAG Playground section with embedding model selector + LLM selector + domain filter + consumer selector + top_k + question + Search + Query buttons + retrieved + answer + citations, `webapp/static/app.js` has EMBEDDING_MODELS catalog 10 models + renderEmbeddingModelList + renderRAGLLMModelList + ragSearch + ragQuery + generateEmbeddings + exportConsumer, `webapp/static/style.css` has RAG playground CSS — reference implementation, but consumer can have its own RAG playground out of STEMMA

---

## 4. Sample in Derived — Already Built

**YES, sample already built in derived — reference implementation inside STEMMA for convenience and demo, plus out-of-STEMMA example proving embedding and RAG can be out of STEMMA as connection layer:**

### Inside STEMMA (optional derived + consumer layer for convenience, INFO not FAIL):

- **Embedder:** `scripts/embed.py` — file-based import from `exports/knowledge.json`, chunking entity strategy, deterministic hash-based fake embeddings for demo if torch not installed, tries sentence-transformers if installed, outputs `exports/embeddings.jsonl` + `exports/vector_store/` FAISS meta.json + vectors.npy + ids.json versioned via content_hash + model id, supports --model param with model ID from embedding-registry, --list-models lists 12 models, --for-consumer learninghub uses OpenAI Large, --for-consumer professor-j uses BGE Large, --domain filter, --limit, deterministic same content_hash + model → same embeddings, batch_size 32 normalize true, chunking entity strategy max_tokens 512 overlap 50
- **RAG:** `scripts/rag.py` — file-based import from `exports/knowledge.json` + `exports/embeddings.jsonl`, vector_search cosine similarity, build_context definitions + connections + sources + source_refs + links + scores, call_llm with model selector like DeepSeek harness (local + frontier models: DeepSeek R1 free, Claude 3.5 Sonnet, GPT-4o, Gemini 2.5 Pro, Llama 3.3, custom via OpenRouter) + citations, consumer-specific models, flow question → embedding → vector search top_k → context → LLM → answer with citations, supports --search for vector search no LLM, --question for full RAG query with citations, --top-k, --model LLM model ID, --embedding-model, --domain filter, --consumer LearningHub/PROFESSOR-J/general, --list-models lists embedding and LLM models
- **Consumer export:** `scripts/export_consumers.py` — filters knowledge.json by consumer domains/review_policy/entity_types and generates consumer-specific exports in `exports/consumers/<consumer>/`, plus embeddings via embed.py, supports --consumer learninghub/professor-j/general/stemma-explorer, --format json/jsonl/embeddings/vector_store, --review-policy all/canonical/reviewed/trusted, --all for all consumers
- **Derived artifacts:** `exports/embeddings.jsonl` (1 embeddings now deterministic fake for demo, 8.6K), `exports/vector_store/` (meta.json + vectors.json + ids.json, meta.json with model All-MiniLM 384 dim, content_hash sha256:2c007..., entity_count 1, created_at deterministic no wall clock, version 1.0.0, type faiss, index_type flat, metric cosine), `exports/consumers/general/knowledge.general.json` (1 entities), `exports/consumers/learninghub/knowledge.learninghub.json` (0 entities needs canonical, correct per review_policy canonical) — all derived, regenerable, deterministic, content-hash versioned, INFO not FAIL in verify_all.py
- **Adapter v0.2.0:** `adapters/python/stemma_adapter/server.py` v0.2.0 with new endpoints /v2/embeddings?model=...&id=...&domain=...&limit=..., /v2/rag/search?q=...&top_k=...&model=...&domain=..., POST /v2/rag/query with body question, top_k, model, embedding_model, domain, consumer → answer with citations, /v2/export?consumer=...&format=...&review_policy=..., /openapi.yaml OpenAPI schema, plus existing /v2/stats, /v2/entities, /v2/connections, /v2/search, etc. — for LearningHub, PROFESSOR-J — run via `PYTHONPATH=adapters/python python3 -m stemma_adapter serve exports/knowledge.json --port 8080`
- **Webapp:** `webapp/server.py` with new endpoints /api/models/embedding, /api/rag/search, /api/embeddings, /api/export, /api/openapi, POST /api/rag/query, plus existing /api/documents, /api/candidates, /api/proposals, /api/audit, /api/config, /api/models — plus `webapp/static/index.html` RAG Playground section with embedding model selector like DeepSeek harness (local + frontier models) + LLM selector + domain filter 8 domains + consumer selector + top_k + question + Search + Query buttons + retrieved + answer + citations + consumer export buttons + OpenAPI button, plus `app.js` EMBEDDING_MODELS catalog 10 models + FRONTIER_MODELS 25 models + renderEmbeddingModelList + renderRAGLLMModelList + ragSearch + ragQuery + generateEmbeddings + exportConsumer, plus `style.css` RAG playground CSS — run via `python3 webapp/server.py --port 8081` — open http://localhost:8081 for RAG playground

### Out of STEMMA (connection layer, NOT whole STEMMA, proving embedding and RAG can be out of STEMMA):

- **Example:** `examples/external-rag/` with README.md + embed.py + rag.py that are OUT OF STEMMA, connection layer, NOT whole STEMMA, connecting via file `../exports/knowledge.json` + content_hash, demonstrating embedding and RAG can be out of STEMMA, they don't contain whole STEMMA, they're just connection layer
- **embed.py out of STEMMA:** File-based import from `../../exports/knowledge.json`, chunking entity strategy, fake deterministic hash-based for demo, outputs `data/embeddings.jsonl` + `data/vector_store/` out of STEMMA, connection layer, NOT whole STEMMA, whole STEMMA remains in STEMMA repo — run via `python3 examples/external-rag/embed.py --model sentence-transformers/all-MiniLM-L6-v2`
- **rag.py out of STEMMA:** File-based import from `../../exports/knowledge.json` + `data/embeddings.jsonl` out of STEMMA, vector_search cosine similarity, rag_query full flow question → embedding → vector search → context → LLM → answer with citations, out of STEMMA, connection layer, NOT whole STEMMA — run via `python3 examples/external-rag/rag.py --search "metre" --top-k 1` and `python3 examples/external-rag/rag.py --question "What is metre?" --top-k 1`
- **Proves:** Embedding and RAG can be out of STEMMA as connection layer, NOT containing whole STEMMA, connecting via file/API/SDK + content_hash — YES, you can have embedding and RAG out of STEMMA, they don't contain whole STEMMA, they're just connection layer

---

## 5. Best Practices for Consistent and Better Architecture for Embedder and RAG System

### For Embedder — Consistent Architecture:

1. **Import from STEMMA consistently via file/API/SDK + content_hash:** Use file-based `exports/knowledge.json` for simplest deterministic, or API-based `/v2/entities` + `/v2/stats` content_hash for production, or SDK-based `Stemma.from_file()` or `from_api()` for consistency — store content_hash with embeddings, recompute if content_hash changed — deterministic same content_hash + model → same embeddings
2. **Model selection via model selector like DeepSeek harness (local + frontier models):** Use embedding-registry.yaml as reference with 12 models, categories All/Frontier/Free/Local/SOTA/Fast, model cards FREE/FRONTIER/LOCAL/SOTA badges, custom input — consumer-specific model choice: LearningHub OpenAI Large 3072 high quality, PROFESSOR-J BGE Large SOTA 1024 offline, general All-MiniLM fast — default All-MiniLM fast local, fallback BGE Small, allow custom model input any frontier or your own fine-tuned via OpenRouter/NVIDIA NIM/OpenAI-compatible
3. **Chunking via entity strategy, deterministic, consistent:** Each entity is one chunk with name, id, domain/subdomain, type, definition, symbol, unit, source, link — max_tokens 512, overlap 50, deterministic same entity → same chunk → same embedding
4. **Deterministic, content-hash versioning, batch size, normalization:** Same knowledge.json content_hash + model id + entity text → same embedding vector, no randomness, no wall clock, content_hash = sha256(text + model_id + knowledge.json content_hash)[:16] versioned via knowledge.json content_hash + model id, batch_size 32, normalize true, recompute on content_hash change or model change
5. **Vector store via FAISS/Chroma/Qdrant/Pinecone, consistent:** FAISS flat cosine local deterministic for mediocre 400-800 entities, meta.json with model, dimensions, content_hash, entity_count, created_at deterministic no wall clock, version 1.0.0, type faiss, index_type flat, metric cosine, versioned via content_hash + model id, alternatives Chroma, Qdrant, Pinecone cloud for production
6. **Storage as derived, regenerable, versioned:** embeddings.jsonl JSONL per entity {entity_id, model, dimensions, vector, content, content_hash} + vector_store/ meta.json + vectors.npy + ids.json — derived, regenerable, versioned, live only in exports/ or data/ out of STEMMA, NOT in content/, connections/, sources/, INFO not FAIL in verify_all.py

### For RAG — Consistent Architecture:

1. **Import from STEMMA consistently via file/API/SDK + content_hash:** Same 3 ways as embedder — file-based knowledge.json, API-based /v2/entities + /v2/stats content_hash, SDK-based Stemma.from_file() — store content_hash with RAG answer, version via content_hash + model_used + embedding_model_used + question + top_k
2. **Retriever via vector search cosine similarity over FAISS, consistent:** Same embedding model as entities for query, vector search cosine similarity over FAISS/Chroma/Qdrant/Pinecone, top_k 5 for LearningHub focused, 10 for PROFESSOR-J broader, domain filter optional, deterministic same query + same content_hash + same model + same FAISS → same retrieved with same scores
3. **Context building via definitions + connections + sources + source_refs + links + scores, consistent, with citations:** Build context from retrieved entities with name, id, domain/subdomain, type, definition, provenance source + link + writer, source_refs, external_ids, score — why definitions + connections + sources: definitions provide exact scientific definitions with agreed status + reference, connections provide relationships, sources provide verifiability, source_refs + links provide citations for answer — deterministic same retrieved → same context
4. **Generator via LLM with model selector like DeepSeek harness (local + frontier models) + citations, consistent:** Model selector like DeepSeek harness (local + frontier models) with search, categories All/Frontier/Reasoning/Free/Custom/Local/SOTA, model cards FREE/FRONTIER/REASONING badges, custom input — local Llama 3.3 via Ollama or frontier API DeepSeek R1 free 671B reasoning, Claude 3.5 Sonnet frontier, GPT-4o frontier multimodal, Gemini 2.5 Pro frontier, Llama 3.3 70B free, custom via OpenRouter/NVIDIA NIM — consumer-specific: LearningHub GPT-4o, PROFESSOR-J DeepSeek R1 free fallback Claude 3.5 Sonnet/GPT-4o/Gemini 2.5 Pro — LLM prompt with context + question + citation enforcement: "Answer based ONLY on context, with citations entity_id + source_ref + link, every claim must have citation, if context doesn't contain answer say I don't know, don't hallucinate, provide answer with citations, grounded in STEMMA, with agreed status + reference if applicable" — citations from context entity_id + source_ref + link for every claim — deterministic if temperature 0, version via content_hash + model_used + embedding_model_used + question + top_k
5. **RAG query full flow question → embedding → vector search → context → LLM → answer with citations, consistent:** Define RAG config in consumer repo similar to consumer-registry.yaml RAG config: rag: {enabled: true, top_k: 5, model: openai/gpt-4o, fallback_models: [...], embedding_model: openai/text-embedding-3-large}, implement rag_query(question, top_k=5, model_id="deepseek/deepseek-r1:free", embedding_model=None, domain=None, consumer="general") that does full flow file-based/API-based/SDK-based import from STEMMA, vector search, context building, LLM call, citations — consumer-specific RAG: LearningHub top_k 5 GPT-4o, PROFESSOR-J top_k 10 DeepSeek R1 free — version RAG answer via content_hash + model_used + embedding_model_used + question + top_k — evaluation retrieval precision top_k relevant, answer faithfulness grounded in retrieved, citation coverage every claim has source_ref + link
6. **API via /v2/rag/search GET + /v2/rag/query POST, consistent:** Implement API endpoints in consumer's RAG service similar to STEMMA's adapter v0.2.0 and webapp: GET /v2/rag/search?q=...&top_k=...&model=...&domain=... returns query, top_k, model, results with entity, score, content; POST /v2/rag/query body {question, top_k, model, embedding_model, domain, consumer} → {question, answer, citations, retrieved_entities, model_used, embedding_model_used, content_hash}; GET /v2/embeddings?model=...&id=...&domain=...&limit=..., GET /v2/export?consumer=...&format=...&review_policy=..., GET /openapi.yaml OpenAPI schema — OpenAPI 3.0.3 schema for RAG endpoints similar to schema/api.yaml v2.1.0, auth none local + api_key for LearningHub/PROFESSOR-J + bearer for frontier via OpenRouter
7. **Webapp RAG playground via model selector like DeepSeek harness (local + frontier models), consistent:** Embedding model selector like DeepSeek harness (local + frontier models) with search, categories All/Frontier/Free/Local/SOTA/Fast, model cards FREE/FRONTIER/LOCAL/SOTA badges, custom input, with 10 embedding models All-MiniLM 384 fast, BGE Large SOTA 1024, OpenAI Large 3072, NVIDIA NV-Embed 4096 SOTA free, plus LLM model selector like DeepSeek harness (local + frontier models) with 25 frontier models DeepSeek R1 free, Claude 3.5 Sonnet, GPT-4o, Gemini 2.5 Pro, Llama 3.3 70B free, custom input, plus domain filter 8 domains, consumer selector LearningHub/PROFESSOR-J/general, top_k slider 1-20, question input, Search button (vector search no LLM) + Query button (full RAG retrieval + LLM with citations) + Generate Embeddings button + Export LearningHub/PROFESSOR-J buttons + OpenAPI button, results retrieved entities with scores + content + domain + type + source + link, answer with citations, citations list with entity_id + source_ref + link, model_used, embedding_model_used, content_hash

### For Consistent and Better Architecture Across Consumers:

- **Use same import method:** File-based for simplest deterministic, or API-based for production, or SDK-based for consistency — via content_hash — store content_hash with embeddings and RAG answers, recompute if content_hash changed
- **Use same model selector:** Model selector like DeepSeek harness (local + frontier models) for both embedding and LLM, with search, categories, model cards, custom input — consistent across LearningHub, PROFESSOR-J, general, explorer, STEMMA-RAG
- **Use same chunking:** Entity strategy, deterministic, consistent — same entity → same chunk → same embedding
- **Use same deterministic versioning:** Same content_hash + model id → same embeddings, same query + same content_hash + same model + same FAISS → same retrieved, version via content_hash + model_used + embedding_model_used + question + top_k
- **Use same context building:** Definitions + connections + sources + source_refs + links + scores, with citations, deterministic same retrieved → same context
- **Use same LLM prompt with citation enforcement:** Answer based ONLY on context, with citations entity_id + source_ref + link, every claim must have citation, don't hallucinate, grounded in STEMMA, with agreed status + reference if applicable
- **Use same API:** /v2/rag/search GET + /v2/rag/query POST + /v2/embeddings + /v2/export + /openapi.yaml OpenAPI 3.0.3, consistent across consumers
- **Use same evaluation:** Retrieval precision top_k relevant, answer faithfulness grounded in retrieved, citation coverage every claim has source_ref + link — for query "Newton second law", top 5 should include newtons-second-law, force, mass, acceleration with scores >0.7, answer should have citations for every claim

---

## 6. Future Changes Plan/Planned — Direction We Are Going

### Already Implemented (2026-09-21) — Comprehensive All-STEM Mediocre + Clean Separation + Embedder + RAG + Consumer Export + Out-of-STEMMA Example

- See section 1 above — template registry v2.0.0 8 domains 97 subdomains 12 entity types, embedding registry v1.0.0 12 models, consumer registry v1.0.0 4 consumers, API schema v2.1.0 OpenAPI 3.0.3, embed.py, rag.py, export_consumers.py, adapter v0.2.0, webapp RAG playground, examples/external-rag/ out of STEMMA, all docs updated with explicit separation canonical vs derived vs consumer, whose job is embedding/RAG (CONSUMER's job, not STEMMA's, STEMMA provides reference), can embedding/RAG be out of STEMMA (YES, connection layer, NOT whole STEMMA, how connect via file/API/SDK + content_hash), verification green

### Future Planned — R1, R2, R3

#### R1 — Comprehensive All-STEM Mediocre v0.1 NOW (400-800 entities across 8 domains + embeddings + RAG + consumer export)

- Grow from 1 entity (metre via HITL) to 400-800 mediocre across 8 domains via PDF primary ingestion with HITL, deterministic templates v2.0.0, model selector like DeepSeek harness (local + frontier models), embeddings, RAG, consumer export — 500+ connections canonical with evidence, explorer clean 3D with domain filter 8 domains, adapter v0.2.0 with embeddings + RAG + consumer export + OpenAPI, embeddings via embed.py with model selector like DeepSeek harness (local + frontier models), vector_store/ FAISS deterministic content-hash versioned, RAG via rag.py with vector search + LLM with citations, consumer-specific exports for LearningHub and PROFESSOR-J, webapp with RAG playground, all verification green including hitl_check + embed + rag + export_consumers, content-hash deterministic, versioned exports v2.1.0 + embeddings.jsonl + vector_store/ + consumers/<consumer>/ + openapi.yaml
- **Embedder/RAG guideline:** This guideline + sample in derived + out-of-STEMMA example — for consumers to build consistent and better architecture for embedder and RAG system that imports from STEMMA

#### R2 — Math Layer + Governing Laws Expansion + Evolvable Domains + Embeddings SOTA + RAG Evaluation + Consistent Architecture

- Expand governing registry to 23 laws as entities with historical timeline via HITL
- Evolve template-registry.yaml v2.0.0 to more subdomains via `python3 scripts/evolvable_template.py --evolve --new-domain medicine` without code change — scales to 1000s PDFs, any domain
- **Embeddings SOTA:** Add more models (BGE-M3 multilingual, GTE, Jina, E5-Mistral, etc.), evaluate retrieval precision for LearningHub queries "What is Newton's second law?" and PROFESSOR-J queries "Explain photosynthesis" — optimize chunking (entity strategy vs sliding window vs hierarchical vs late chunking), add re-ranking (cross-encoder like bge-reranker-large), add multi-vector (ColBERT), add query expansion, add HyDE (Hypothetical Document Embeddings), add embedding model selector like DeepSeek harness (local + frontier models) with evaluation metrics
- **RAG Evaluation:** Evaluate retrieval precision + answer faithfulness + citation coverage, add re-ranking, add multi-hop via prerequisites closure `/v2/prerequisites/{id}`, add query expansion, add HyDE, add self-RAG, add citation enforcement, add feedback loop, add monitoring, add evaluation dataset with queries and expected entities and expected citations
- **Consistent Architecture:** Improve guideline with more best practices, add reference implementation for TypeScript adapter `adapters/typescript/`, add Python package `stemma-rag` that can be pip installed and used out of STEMMA as connection layer, with consistent import via file/API/SDK + content_hash, model selector like DeepSeek harness (local + frontier models), deterministic versioning, context building with citations, LLM prompt with citation enforcement, API /v2/rag/search + /v2/rag/query POST + /v2/embeddings + /v2/export + /openapi.yaml, webapp RAG playground, evaluation metrics
- **Consumer export:** Add more consumers, add webhooks, add GraphQL API, add streaming API for RAG
- **Production API hosting:** https://api.stemma.example.com/v2 with auth api_key, rate limiting, OpenAPI, SDK generation, with embeddings and RAG as separate service out of STEMMA but with reference implementation inside STEMMA for convenience

#### R3 — Other Domains LATER (Evolvable) + Production RAG + Hosted Vector Store + Consistent Architecture Across All Consumers

- Medicine, economics, etc. via evolvable template-registry.yaml v2.0.0 — no code change, just YAML
- **Production RAG:** Hosted RAG with vector store Qdrant/Pinecone cloud, with LearningHub, PROFESSOR-J production, with monitoring, evaluation, feedback loop, with content_hash versioning, deterministic regeneration, multi-model support, with model selector like DeepSeek harness (local + frontier models) for both embedding and LLM, with consistent architecture across all consumers via guideline
- **Hosted vector store:** With content_hash versioning, deterministic regeneration, multi-model support, with API /v2/embeddings, /v2/rag/search, POST /v2/rag/query, with OpenAPI schema, with SDK, with webapp RAG playground, with evaluation
- **Consistent architecture:** All consumers (LearningHub, PROFESSOR-J, general, explorer, STEMMA-RAG) build embedder and RAG system that imports from STEMMA consistently via file/API/SDK + content_hash, with model selector like DeepSeek harness (local + frontier models), deterministic versioning, context building with citations, LLM prompt with citation enforcement, API /v2/rag/search + /v2/rag/query POST, evaluation retrieval precision + faithfulness + citation coverage — via this guideline
- No legacy, this is comprehensive all-STEM mediocre with HITL, deterministic scales, evolvable, model selector like DeepSeek harness (local + frontier models), embeddings, RAG, consumer export, clean separation canonical vs derived vs consumer, embedding and RAG is consumer's job, not STEMMA's, but STEMMA provides reference implementation, embedding and RAG can be out of STEMMA as connection layer, NOT whole STEMMA, connecting via file/API/SDK + content_hash

---

## 7. Sample in Derived — Already Built — Reference Implementation Inside and Out of STEMMA

### Inside STEMMA (optional derived + consumer layer for convenience, INFO not FAIL, reference implementation):

- **Embedder:** `scripts/embed.py` — file-based import from `exports/knowledge.json`, chunking entity strategy, deterministic hash-based fake embeddings for demo if torch not installed, tries sentence-transformers if installed, outputs `exports/embeddings.jsonl` + `exports/vector_store/` FAISS meta.json + vectors.npy + ids.json versioned via content_hash + model id, supports --model param with model ID from embedding-registry, --list-models lists 12 models, --for-consumer learninghub uses OpenAI Large, --for-consumer professor-j uses BGE Large, --domain filter, --limit, deterministic same content_hash + model → same embeddings, batch_size 32 normalize true, chunking entity strategy max_tokens 512 overlap 50
- **RAG:** `scripts/rag.py` — file-based import from `exports/knowledge.json` + `exports/embeddings.jsonl`, vector_search cosine similarity, build_context definitions + connections + sources + source_refs + links + scores, call_llm with model selector like DeepSeek harness (local + frontier models: DeepSeek R1 free, Claude 3.5 Sonnet, GPT-4o, Gemini 2.5 Pro, Llama 3.3, custom via OpenRouter) + citations, consumer-specific models, flow question → embedding → vector search top_k → context → LLM → answer with citations, supports --search for vector search no LLM, --question for full RAG query with citations, --top-k, --model LLM model ID, --embedding-model, --domain filter, --consumer LearningHub/PROFESSOR-J/general, --list-models lists embedding and LLM models
- **Consumer export:** `scripts/export_consumers.py` — filters knowledge.json by consumer domains/review_policy/entity_types and generates consumer-specific exports in `exports/consumers/<consumer>/`, plus embeddings via embed.py, supports --consumer learninghub/professor-j/general/stemma-explorer, --format json/jsonl/embeddings/vector_store, --review-policy all/canonical/reviewed/trusted, --all for all consumers
- **Derived artifacts:** `exports/embeddings.jsonl` (1 embeddings now deterministic fake for demo, 8.6K), `exports/vector_store/` (meta.json + vectors.json + ids.json, meta.json with model All-MiniLM 384 dim, content_hash sha256:2c007..., entity_count 1, created_at deterministic no wall clock, version 1.0.0, type faiss, index_type flat, metric cosine), `exports/consumers/general/knowledge.general.json` (1 entities), `exports/consumers/learninghub/knowledge.learninghub.json` (0 entities needs canonical, correct per review_policy canonical) — all derived, regenerable, deterministic, content-hash versioned, INFO not FAIL in verify_all.py
- **Adapter v0.2.0:** `adapters/python/stemma_adapter/server.py` v0.2.0 with new endpoints /v2/embeddings?model=...&id=...&domain=...&limit=..., /v2/rag/search?q=...&top_k=...&model=...&domain=..., POST /v2/rag/query with body question, top_k, model, embedding_model, domain, consumer → answer with citations, /v2/export?consumer=...&format=...&review_policy=..., /openapi.yaml OpenAPI schema, plus existing /v2/stats, /v2/entities, /v2/connections, /v2/search, etc. — for LearningHub, PROFESSOR-J — run via `PYTHONPATH=adapters/python python3 -m stemma_adapter serve exports/knowledge.json --port 8080`
- **Webapp:** `webapp/server.py` with new endpoints /api/models/embedding, /api/rag/search, /api/embeddings, /api/export, /api/openapi, POST /api/rag/query, plus existing /api/documents, /api/candidates, /api/proposals, /api/audit, /api/config, /api/models — plus `webapp/static/index.html` RAG Playground section with embedding model selector like DeepSeek harness (local + frontier models) + LLM selector + domain filter 8 domains + consumer selector + top_k + question + Search + Query buttons + retrieved + answer + citations + consumer export buttons + OpenAPI button, plus `app.js` EMBEDDING_MODELS catalog 10 models + FRONTIER_MODELS 25 models + renderEmbeddingModelList + renderRAGLLMModelList + ragSearch + ragQuery + generateEmbeddings + exportConsumer, plus `style.css` RAG playground CSS — run via `python3 webapp/server.py --port 8081` — open http://localhost:8081 for RAG playground

### Out of STEMMA (connection layer, NOT whole STEMMA, proving embedding and RAG can be out of STEMMA):

- **Example:** `examples/external-rag/` with README.md + embed.py + rag.py that are OUT OF STEMMA, connection layer, NOT whole STEMMA, connecting via file `../exports/knowledge.json` + content_hash, demonstrating embedding and RAG can be out of STEMMA, they don't contain whole STEMMA, they're just connection layer
- **embed.py out of STEMMA:** File-based import from `../../exports/knowledge.json`, chunking entity strategy, fake deterministic hash-based for demo, outputs `data/embeddings.jsonl` + `data/vector_store/` out of STEMMA, connection layer, NOT whole STEMMA, whole STEMMA remains in STEMMA repo — run via `python3 examples/external-rag/embed.py --model sentence-transformers/all-MiniLM-L6-v2`
- **rag.py out of STEMMA:** File-based import from `../../exports/knowledge.json` + `data/embeddings.jsonl` out of STEMMA, vector_search cosine similarity, rag_query full flow question → embedding → vector search → context → LLM → answer with citations, out of STEMMA, connection layer, NOT whole STEMMA — run via `python3 examples/external-rag/rag.py --search "metre" --top-k 1` and `python3 examples/external-rag/rag.py --question "What is metre?" --top-k 1`
- **Proves:** Embedding and RAG can be out of STEMMA as connection layer, NOT containing whole STEMMA, connecting via file/API/SDK + content_hash — YES, you can have embedding and RAG out of STEMMA, they don't contain whole STEMMA, they're just connection layer — this example is sample in derived that is out of STEMMA

---

## 8. How to Use This Guideline — For Consumer to Build Consistent and Better Architecture

### For LearningHub (example):

1. **Import from STEMMA consistently via file/API/SDK + content_hash:**
   ```python
   from stemma_adapter import Stemma
   stemma = Stemma.from_file("../STEMMA/exports/knowledge.json")
   content_hash = stemma.export["content_hash"]
   # Or via API
   # import requests; stats = requests.get("http://stemma-api:8080/v2/stats").json(); content_hash = stats["content_hash"]; entities = requests.get("http://stemma-api:8080/v2/entities?domain=physics&status=canonical&limit=1000").json()
   ```

2. **Build embedder consistently via model selector like DeepSeek harness (local + frontier models):**
   ```python
   # Use embedding-registry.yaml as reference
   # Choose model: LearningHub prefers OpenAI Large 3072 high quality
   from stemma_rag import StemmaEmbedder  # external, out of STEMMA, following guideline
   embedder = StemmaEmbedder(embedding_model="openai/text-embedding-3-large", api_key="...", provider="openai", chunking_strategy="entity", max_tokens=512, overlap=50, batch_size=32, normalize=True)
   if embedder.needs_recompute(content_hash):
       embeddings = embedder.generate(stemma.entities(domain="physics", status="canonical"))
       # Writes data/embeddings.jsonl + data/vector_store/ FAISS out of STEMMA, connection layer, NOT whole STEMMA, versioned via content_hash + model id
   ```

3. **Build RAG consistently via retriever + context + generator with citations:**
   ```python
   from stemma_rag import StemmaRAG
   rag = StemmaRAG.from_stemma(stemma, embedding_model="openai/text-embedding-3-large", vector_store_path="./data/vector_store/", top_k=5, llm_model="openai/gpt-4o")
   answer = rag.query("What is Newton's second law?", top_k=5, domain="physics", consumer="learninghub")
   print(answer['answer'])  # with citations entity_id + source_ref + link
   print(answer['citations'])  # [{"entity_id": "stemma:phys.newtons-second-law", "source_ref": "halliday", "link": "https://..."}, ...]
   print(answer['retrieved_entities'])  # with scores
   ```

4. **Use API for production:**
   ```bash
   curl "http://localhost:8080/v2/rag/search?q=Newton%20second%20law&top_k=5&model=openai/text-embedding-3-large&domain=physics"
   curl -X POST http://localhost:8080/v2/rag/query -H "Content-Type: application/json" -d '{"question":"What is Newton second law?","top_k":5,"model":"openai/gpt-4o","embedding_model":"openai/text-embedding-3-large","domain":"physics","consumer":"learninghub"}'
   ```

### For PROFESSOR-J (example):

1. **Import from STEMMA consistently via file/API/SDK + content_hash — all 8 domains mediocre, reviewed:**
   ```python
   from stemma_adapter import Stemma
   stemma = Stemma.from_file("../STEMMA/exports/knowledge.json")
   content_hash = stemma.export["content_hash"]
   entities = stemma.entities(status="reviewed", limit=1000)  # all 8 domains mediocre, reviewed
   ```

2. **Build embedder consistently via model selector like DeepSeek harness (local + frontier models) — offline SOTA:**
   ```python
   from stemma_rag import StemmaEmbedder
   # PROFESSOR-J prefers BGE Large SOTA 1024 offline capable
   embedder = StemmaEmbedder(embedding_model="BAAI/bge-large-en-v1.5", chunking_strategy="entity", max_tokens=512, overlap=50, batch_size=32, normalize=True)
   if embedder.needs_recompute(content_hash):
       embeddings = embedder.generate(entities)
       # Writes data/embeddings.jsonl + data/vector_store/ FAISS out of STEMMA, offline, SOTA, versioned via content_hash + model id
   ```

3. **Build RAG consistently via retriever + context + generator with citations — reasoning:**
   ```python
   from stemma_rag import StemmaRAG
   rag = StemmaRAG.from_stemma(stemma, embedding_model="BAAI/bge-large-en-v1.5", vector_store_path="./data/vector_store/", top_k=10, llm_model="deepseek/deepseek-r1:free", fallback_models=["anthropic/claude-3.5-sonnet", "openai/gpt-4o", "google/gemini-2.5-pro"])
   answer = rag.query("Explain photosynthesis and its relation to cellular respiration", top_k=10, domain="biology", consumer="professor-j")
   print(answer['answer'])  # detailed with reasoning + citations across biology
   ```

---

## 9. Related Docs — All Updated With Direction and Future Plans

- **ARCHITECTURE.md** — comprehensive all-STEM mediocre + clean separation canonical vs derived vs consumer + whose job is embedding/RAG (CONSUMER's job, not STEMMA's) + can embedding/RAG be out of STEMMA (YES, connection layer, NOT whole STEMMA, how connect via file/API/SDK + content_hash) + direction and future plans R1, R2, R3
- **GOVERNANCE.md** — invariants + explicit separation + whose job + can be out + direction and future plans
- **VISION.md** — comprehensive all-STEM mediocre + explicit separation + whose job + can be out + direction and future plans
- **ROADMAP.md** — R1 comprehensive all-STEM mediocre + embeddings + RAG + consumer export + explicit separation + whose job + can be out + R2 embeddings SOTA + RAG evaluation + consistent architecture + R3 production RAG + hosted vector store + future plans
- **CONSUMERS.md** — LearningHub, PROFESSOR-J, general, explorer with embedding_model, RAG config, export mechanisms file/API/SDK, explicit separation, whose job, can be out, how connect, direction and future plans
- **EMBEDDINGS.md** — YES embedding model needed, 12 models, model selector like DeepSeek harness (local + frontier models), deterministic, vector_store FAISS, explicit separation, whose job (CONSUMER's job, not STEMMA's), can be out (YES, connection layer, NOT whole STEMMA), how connect, direction and future plans
- **RAG.md** — YES RAG needed, flow question → embedding → vector search → context → LLM with model selector like DeepSeek harness (local + frontier models) + citations, API /v2/rag/search + /v2/rag/query POST, webapp RAG playground, explicit separation, whose job, can be out, how connect, direction and future plans
- **API.md** — YES export mechanism via api schema link/api needed, OpenAPI 3.0.3, adapter v0.2.0 endpoints, webapp endpoints, file/API/SDK, explicit separation, whose job, can be out, how connect, direction and future plans
- **TESTING.md** — verification chain includes embed + rag + export_consumers as INFO not FAIL, explicit separation, whose job, can be out, direction and future plans
- **VERSIONING.md** — template-registry v2.0.0, embedding-registry v1.0.0, consumer-registry v1.0.0, api v2.1.0, deterministic content-hash for embeddings and vector_store, explicit separation, whose job, can be out, direction and future plans
- **IMPLEMENTATION-STATUS.md** — 1 entity metre via HITL, embeddings 1, vector_store FAISS, consumer exports, 8 domains 97 subdomains, checks all green including embed + rag + export_consumers, explicit separation, whose job, can be out, direction and future plans, verification commands
- **README.md root + docs/README.md** — comprehensive all-STEM mediocre + embeddings + RAG + consumer export + explicit separation + whose job + can be out + how connect + direction and future plans
- **AGENTS.md** — deterministic protocol with HITL + PDF primary + evolvable templates v2.0.0 + model selector like DeepSeek harness (local + frontier models) + explicit separation + whose job + can be out + direction and future plans

---

## 10. Verification — All Green, With Guideline and Sample

```bash
python3 scripts/validate.py  # OK 1 entities valid — NEVER checks embeddings — STEMMA's job is canonical only
python3 scripts/physics_core_profile_check.py  # OK 0 violations
python3 scripts/physics_governing_check.py  # OK 0 violations
python3 scripts/hitl_check.py --check-workflow  # OK HITL has human edits 3
python3 scripts/evolvable_template.py --pdf-extract  # OK 6 entities from HRW Ch1
python3 scripts/embed.py --model sentence-transformers/all-MiniLM-L6-v2 --output exports/embeddings.jsonl  # OK 1 embeddings deterministic fake for demo — derived, regenerable, content-hash versioned — reference implementation inside STEMMA for convenience, but production embedding is consumer's job out of STEMMA
python3 scripts/rag.py --search "metre" --top-k 1  # OK vector search out of STEMMA? No, inside STEMMA as reference, but can be out of STEMMA as in examples/external-rag/ — connection layer, NOT whole STEMMA
python3 scripts/rag.py --question "What is metre?" --top-k 1 --model deepseek/deepseek-r1:free --consumer general  # OK RAG query with citations — reference implementation inside STEMMA, but production RAG is consumer's job out of STEMMA
python3 scripts/export_consumers.py --consumer general --format json  # OK 1 entities — consumer's job is embedding/RAG, STEMMA provides reference
python3 examples/external-rag/embed.py --model sentence-transformers/all-MiniLM-L6-v2  # OK 1 embeddings out of STEMMA — connection layer, NOT whole STEMMA — proves embedding can be out of STEMMA, consumer's job
python3 examples/external-rag/rag.py --search "metre" --top-k 1  # OK vector search out of STEMMA — connection layer, NOT whole STEMMA — proves RAG can be out of STEMMA, consumer's job
python3 examples/external-rag/rag.py --question "What is metre?" --top-k 1  # OK RAG query out of STEMMA with citations — connection layer, NOT whole STEMMA — proves RAG can be out of STEMMA, consumer's job
python3 scripts/status_truth.py --write  # OK README status block 1 entities 0 connections 3 sources
python3 scripts/verify_all.py  # OK all verify steps pass — comprehensive all-STEM mediocre 1 entities (metre via HITL, old 74 archived, will grow to 400-800 across 8 domains), 0 connections, HITL enforced, PDF primary deterministic scales, evolvable templates v2.0.0 (8 domains 97 subdomains 12 entity types), model selector like DeepSeek harness (local + frontier models: DeepSeek R1, Claude 3.5 Sonnet, GPT-4o, Gemini 2.5 Pro, Llama 3.3, custom), embeddings (All-MiniLM 384 fast, BGE Large SOTA 1024, OpenAI Large 3072, NVIDIA NV-Embed 4096 SOTA), RAG (vector search + LLM with citations), consumer export (LearningHub canonical physics/chem/bio/math OpenAI Large GPT-4o, PROFESSOR-J reviewed all 8 domains mediocre BGE Large offline DeepSeek R1 free, general, explorer) — embeddings check INFO not FAIL, RAG check INFO not FAIL, consumer export INFO not FAIL — CONSUMER's job is embedding/RAG, STEMMA provides reference implementation
```

All good, ready for PR — with guideline to build embedder and RAG system that imports from STEMMA consistently, sample in derived inside and out of STEMMA, docs updated about direction, new change already implemented and future changes plan/planned.
