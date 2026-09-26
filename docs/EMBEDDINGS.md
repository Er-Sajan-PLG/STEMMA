# EMBEDDINGS — Comprehensive All-STEM, Model Selector Like DeepSeek Harness

**Status:** Authoritative, v1.0.0, comprehensive all-STEM mediocre coverage with embeddings for RAG and consumer export (LearningHub, PROFESSOR-J). Old minimal physics had no embeddings — now YES embedding model needed.

## Do we need embedding model for embedding? YES.

**Answer:** Yes, you need embedding model for embedding and export to consumers like LearningHub, PROFESSOR-J. Without embeddings, STEMMA is static JSON, can't do semantic search. With embeddings, students can query "Newton's law" and get relevant entities via vector similarity, AI professor can answer offline.

## Embedding Registry — v1.0.0 — 11 models, local free + frontier API, model selector like DeepSeek harness (local + frontier models)

Defined in `schema/embedding-registry.yaml` v1.0.0 and `schema/template-registry.yaml` v2.0.0 embedding section:

### Local free models — offline, deterministic, no API key, no cost, good for mediocre all-domain

- **sentence-transformers/all-MiniLM-L6-v2** — 384 dim, 80MB, fast, 5x faster than MPNet, default for quick RAG, free, local, Apache-2.0 — use_case: default quick RAG, general consumer
- **sentence-transformers/all-mpnet-base-v2** — 768 dim, 420MB, high quality, best quality/speed for local, free, local — use_case: high quality local RAG
- **BAAI/bge-large-en-v1.5** — 1024 dim, 1.3GB, SOTA local embedding, MTEB top, MIT, free, local, frontier — use_case: SOTA local RAG best for STEM retrieval, PROFESSOR-J prefers this (offline SOTA)
- **intfloat/e5-large-v2** — 1024 dim, 1.3GB, retrieval-optimized, query prefix, MIT, free, local — use_case: retrieval-optimized
- **BAAI/bge-small-en-v1.5** — 384 dim, 133MB, small fast, MIT, free, local — use_case: fast local fallback

### Frontier API models — via OpenRouter, OpenAI, Cohere, Google, NVIDIA NIM, model selector like DeepSeek harness (local + frontier models)

- **openai/text-embedding-3-large** — 3072 dim, 8191 max tokens, frontier, best quality MTEB 64.6, $0.00013/1k tokens, API openai — use_case: frontier quality for LearningHub production, LearningHub prefers this
- **openai/text-embedding-3-small** — 1536 dim, 8191 max tokens, frontier fast, $0.00002/1k tokens, API openai — use_case: fast frontier cheap
- **openai/text-embedding-ada-002** — 1536 dim, legacy, API openai — use_case: legacy compatibility
- **cohere/embed-english-v3.0** — 1024 dim, 512 max tokens, frontier, API cohere — use_case: Cohere RAG
- **google/text-embedding-004** — 768 dim, 2048 max tokens, frontier free tier, API google — use_case: free frontier
- **nvidia/nv-embed-v1** — 4096 dim, 512 max tokens, SOTA, MTEB top, free via NIM, API nvidia — use_case: SOTA frontier via NVIDIA NIM free

**Default:** All-MiniLM-L6-v2 (fast local), fallback BGE Small

### Model selector like DeepSeek harness — standard inference window

Like DeepSeek harness model selection in settings, embedding model selector has:

- Search bar to filter models by name (e.g., "bge", "openai", "nvidia")
- Category tabs: All, Frontier 🚀 (OpenAI text-embedding-3-large, Cohere, Gemini, NVIDIA NV-Embed, BGE Large), Free 🆓 (All-MiniLM, BGE Large free, Gemini free tier, NVIDIA free), Local 💻 (All-MiniLM, MPNet, BGE Large, E5, BGE Small), SOTA ⭐ (BGE Large, E5 Large, OpenAI Large, NVIDIA NV-Embed), Fast ⚡ (All-MiniLM, BGE Small, OpenAI Small)
- Model cards with badges FREE/FRONTIER/LOCAL/SOTA/FAST, dimensions, description, provider, cost
- Custom model input: any frontier embedding model or your own fine-tuned via OpenRouter/NVIDIA NIM/OpenAI-compatible — e.g., "your-org/your-model" or "http://localhost:8000/embeddings"
- Info boxes: scaling + frontier + deterministic

Implemented in webapp/static/app.js FRONTIER_MODELS for LLM + embedding models list, renderModelList with search + category filter + provider filter.

## Chunking strategy

- **Strategy:** entity — each entity is one chunk (definition + name + domain + subdomain + symbol + unit)
- **Max tokens:** 512
- **Overlap:** 50
- **Separators:** ["\n\n", "\n", ". ", " "]
- Each entity chunk includes: name (id), domain/subdomain, type, definition, symbol, unit — for retrieval

## Vector store configuration

- **Type:** faiss (default) — flat index, cosine metric, local, deterministic
- **Path:** exports/vector_store/ — meta.json + vectors.json (or vectors.json if numpy not available) + ids.json
- **Alternatives:** chroma (exports/chroma/), qdrant (local), pinecone (cloud)
- **Index type:** flat (simple, deterministic, good for mediocre 400-800 entities), alternatives: ivf, hnsw for larger
- **Metric:** cosine

## Policy — deterministic, versioned, content-hash

- **Deterministic:** same knowledge.json content_hash + model id → same embeddings, no wall clock, versioned via content_hash
- **Content hash:** true — embedding record has content_hash = sha256(text + model_id + knowledge.json content_hash)[:16] — ensures deterministic same embeddings for same content + model
- **Versioned:** true — embeddings are derived artifacts regenerable from knowledge.json, but content_hash ensures deterministic
- **Recompute on:** knowledge.json content_hash change, model change
- **Batch size:** 32
- **Normalize:** true — cosine similarity

## Generation — scripts/embed.py

```bash
# List models
python3 scripts/embed.py --list-models

# Generate for all entities with default model (All-MiniLM-L6-v2 fast local)
python3 scripts/embed.py --model sentence-transformers/all-MiniLM-L6-v2 --output exports/embeddings.jsonl --vector-store exports/vector_store/

# Generate with SOTA local BGE Large (best for RAG, PROFESSOR-J prefers)
python3 scripts/embed.py --model BAAI/bge-large-en-v1.5 --output exports/embeddings.jsonl

# Generate with frontier OpenAI text-embedding-3-large (best quality, LearningHub prefers)
python3 scripts/embed.py --model openai/text-embedding-3-large --api-key $OPENAI_API_KEY

# Generate for specific consumer
python3 scripts/embed.py --for-consumer learninghub  # uses LearningHub preferred model OpenAI Large
python3 scripts/embed.py --for-consumer professor-j   # uses PROFESSOR-J preferred BGE Large

# Filter by domain
python3 scripts/embed.py --model BAAI/bge-large-en-v1.5 --domain physics --limit 100
```

**Implementation:** Tries sentence-transformers if installed (pip install sentence-transformers torch), else fake deterministic hash-based embeddings for demo (hash text + model id → deterministic float vector, normalized) — so works without torch for mediocre coverage demo.

**Output:**
- `exports/embeddings.jsonl` — JSONL per entity: {entity_id, model, dimensions, vector, content, content_hash}
- `exports/vector_store/meta.json` — {model, dimensions, content_hash, entity_count, created_at deterministic no wall clock, version 1.0.0, type faiss, index_type flat, metric cosine}
- `exports/vector_store/vectors.json` — numpy array if numpy available, else vectors.json
- `exports/vector_store/ids.json` — entity IDs

## Consumer-specific embedding needs

- **LearningHub:** preferred_model OpenAI text-embedding-3-large 3072 dim fallback BGE Large SOTA 1024 — high quality for student queries, rate limit 1000/hour api_key
- **PROFESSOR-J:** preferred_model BGE Large SOTA 1024 dim fallback All-MiniLM 384 — offline capable, SOTA local, best for RAG, rate limit 10000/hour api_key
- **General:** preferred_model All-MiniLM 384 fast local fallback BGE Small 384 — fast local
- **Explorer:** no embeddings needed (3D graph)

## Why embeddings needed for LearningHub, PROFESSOR-J?

- **LearningHub:** Students query "What is Newton's second law?" — without embeddings, only keyword search. With embeddings, semantic search finds relevant entities (force, mass, acceleration, Newton's laws) via vector similarity, even if query wording differs. High-quality embeddings (OpenAI Large 3072) give better retrieval precision.
- **PROFESSOR-J:** AI professor needs offline SOTA embeddings (BGE Large 1024) for RAG, FAISS vector store local, no API dependency, answers questions with citations from STEMMA.

## Deterministic, versioned, content-hash — no wall clock

Embeddings are derived artifacts, not canonical, regenerable from knowledge.json. But content_hash ensures deterministic same embeddings for same content + model, versioned via knowledge.json content_hash + model id, no wall clock, batch_size 32, normalize true.

## Related docs

- `schema/embedding-registry.yaml` — registry
- `schema/template-registry.yaml` v2.0.0 — embedding config
- `scripts/embed.py` — generator
- `scripts/rag.py` — uses embeddings for retrieval
- `docs/RAG.md` — RAG system
- `docs/CONSUMERS.md` — consumer-specific embedding needs
- `schema/api.yaml` — /v2/embeddings endpoint
- `adapters/python/stemma_adapter/server.py` v0.2.0 — /v2/embeddings endpoint
- `webapp/server.py` — /api/embeddings endpoint + embedding model selector like DeepSeek harness (local + frontier models)


## Explicit Separation — Canonical vs Derived vs Consumer (NEW 2026-09-21 — Answers: Does STEMMA itself need embeddings/RAG?)

**User question:** "Now about RAG system and embedding, STEMMA in itself doesn't need them!? But again STEMMA alone existence is useless if we can't use it, so building RAG pipeline is inevitable here!?"

**Answer: YES, exactly right — clean separation:**

- **Canonical (STEMMA itself) — NO embeddings/RAG:** content/, connections/, sources/, schema/ (except registries that define models, not vectors) — only Markdown+YAML with exact definitions, dual verification, governed_by, history, 8 relations, evidence — NO embeddings, vectors, .npy, embeddings.jsonl, vector_store/ — NEVER — validate.py NEVER checks embeddings — previously "Not on roadmap: embeddings, database as source of truth" meant canonical, not derived — correct, canonical never has embeddings
- **Derived (exports/) — YES embeddings here but as derived, regenerable, deterministic, content-hash:** knowledge.json v2.2.0 content-hash, embeddings.jsonl, vector_store/ FAISS meta.json + vectors.json + ids.json versioned via content_hash + model id, consumers/<consumer>/knowledge.<consumer>.json, openapi.yaml — deterministic same content_hash + model id → same embeddings, regenerable via validate.py + embed.py, verify_all.py checks embeddings existence as INFO, not FAIL
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
- **Vector store (connection layer, NOT whole STEMMA):** Does NOT contain whole STEMMA — contains FAISS index of vectors + ids.json + meta.json with model, dimensions, content_hash, entity_count — e.g., vectors.json shape (1, 384), ids.json ["stemma:phys.metre"] — just index for fast cosine similarity, NOT whole STEMMA, just connection layer for retrieval
- **RAG (connection layer, NOT whole STEMMA):** Does NOT contain whole STEMMA — contains retrieval logic (embedding query → cosine similarity over FAISS → top_k entities with scores) + generation logic (build context definitions + connections + sources + source_refs + links → LLM prompt → answer with citations) — e.g., question "What is Newton's second law?" → retrieves [force, mass, newtons-second-law] → context → LLM DeepSeek R1 free → answer with citations entity_id + source_ref + link — grounded in STEMMA but RAG itself doesn't contain whole STEMMA, only references entity IDs and definitions as context, whole STEMMA remains in content/

**How do they connect? Via exports/knowledge.json + API + SDK + content_hash — 3 ways:**

1. **File-based:** STEMMA exports knowledge.json v2.2.0 deterministic content-hash — external RAG (out of STEMMA) in LearningHub or PROFESSOR-J or separate repo STEMMA-RAG copies knowledge.json file, then runs own embedding generation externally: `cp ../STEMMA/exports/knowledge.json ./data/ && python3 -m stemma_rag.embed --input ./data/knowledge.json --model BAAI/bge-large-en-v1.5 --output ./data/embeddings.jsonl --vector-store ./data/vector_store/` — connection via content_hash, if changed recompute embeddings — does NOT contain whole STEMMA, only vectors + index + retrieval logic

2. **API-based:** STEMMA API adapter v0.2.0 serves knowledge.json via REST API with OpenAPI schema api.yaml v2.2.0: /v2/stats content_hash, /v2/entities?domain=physics&status=canonical&limit=1000, /v2/entities/{id}, /v2/search?q=..., /v2/embeddings?model=..., /v2/rag/search?q=...&top_k=..., POST /v2/rag/query, /v2/export?consumer=..., /openapi.yaml — external RAG in LearningHub/PROFESSOR-J calls API to get entities, generates embeddings externally, builds FAISS externally, serves RAG queries with citations — connection via API + content_hash, does NOT contain whole STEMMA, just connection layer

3. **SDK-based:** STEMMA SDK adapters/python/ pip install ./adapters/python — Stemma.from_file("exports/knowledge.json") or Stemma.from_api("http://localhost:8080") — search, resolve, stats with content_hash — external RAG uses SDK to load STEMMA, then builds own embeddings/RAG out of STEMMA: `from stemma_adapter import Stemma; stemma = Stemma.from_file("../STEMMA/exports/knowledge.json"); from stemma_rag import StemmaRAG; rag = StemmaRAG.from_stemma(stemma, embedding_model="BAAI/bge-large-en-v1.5"); answer = rag.query("What is Newton's second law?", top_k=5, model="deepseek/deepseek-r1:free")` — connection via SDK + content_hash, does NOT contain whole STEMMA, just connection layer

**Current implementation:** Optional derived layer inside STEMMA for convenience and demo — scripts/embed.py, rag.py, export_consumers.py, exports/embeddings.jsonl, vector_store/, adapters/python/ v0.2.0 with /v2/embeddings, /v2/rag/search, POST /v2/rag/query, /v2/export, /openapi.yaml, webapp RAG playground — all inside STEMMA repo, but as derived + consumer layer, not canonical, optional, INFO not FAIL in verify_all.py — convenient for demo, for LearningHub, PROFESSOR-J to see how embedding/RAG connects, for testing retrieval precision + faithfulness + citation coverage

**Can be out:** YES, you can have embedding and RAG out of STEMMA — move scripts/embed.py, rag.py, export_consumers.py to separate repo STEMMA-RAG or to LearningHub/PROFESSOR-J repos, keep STEMMA core pure with only content/, connections/, sources/, schema/, validate.py — then STEMMA exports knowledge.json + API schema, external RAG consumes via file/API/SDK + content_hash + deterministic regeneration — cleaner separation, STEMMA remains pure knowledge foundation, embedding/RAG are external consumers, connection layer, not containing whole STEMMA

**Recommendation:** Keep canonical pure (content/, connections/, sources/, schema/ — NO embeddings, NO RAG, validate.py NEVER checks embeddings), keep derived optional inside for convenience (exports/knowledge.json, embeddings.jsonl, vector_store/, consumers/ — derived, regenerable, deterministic, content-hash, INFO not FAIL), but for production LearningHub, PROFESSOR-J have embedding and RAG out of STEMMA as separate service or part of LearningHub/PROFESSOR-J that consumes STEMMA via file/API/SDK + content_hash, generates embeddings externally, builds vector store externally, serves RAG queries with citations — embedding/RAG doesn't contain whole STEMMA, just connection layer, whole STEMMA remains in STEMMA repo

**Therefore:** YES, you can have embedding and RAG out of STEMMA, they connect via exports/knowledge.json + API + SDK + content_hash, they don't contain whole STEMMA, they're just connection layer — current implementation keeps them inside as optional derived + consumer for convenience and demo, but can be moved out to separate repo or to LearningHub/PROFESSOR-J for cleaner separation.


## Whose Job Is To Build Embedding and RAG? CONSUMER's Job, Not STEMMA's Job — STEMMA Provides Reference Implementation (NEW 2026-09-21)

**User question:** "whose job is to build embedding and RAG!? STEMMA or CONSUMER!?"

**Answer: CONSUMER's job, not STEMMA's job — STEMMA provides reference implementation as optional derived + consumer layer for convenience and demo, but production embedding and RAG is consumer's job (LearningHub, PROFESSOR-J, general, explorer, STEMMA-RAG).**

- **STEMMA's job — knowledge foundation, pure, deterministic, HITL, versioned, content-hash, NO embeddings/RAG in canonical:** content/<domain>/**/*.md (Markdown+YAML with exact definitions, dual verification, governed_by, history), connections/*.yaml (8 relations, evidence), sources/*.yaml (url/doi/isbn + writer human:*), schema/ (JSON Schemas, relation-registry, template-registry v2.0.0 comprehensive all-STEM 8 domains 97 subdomains 12 entity types, embedding-registry v1.0.0 11 models, consumer-registry v1.0.0 4 consumers, api.yaml OpenAPI 3.0.3, governing-registry, VERSION.yaml), scripts/validate.py (NEVER checks embeddings, only canonical), physics_core_profile_check.py, physics_governing_check.py, hitl_check.py, evolvable_template.py, status_truth.py, verify_all.py (canonical checks as FAIL, embeddings/RAG/consumer export checks as INFO not FAIL) — provides knowledge foundation + deterministic versioned exports knowledge.json v2.2.0 content-hash + openapi.yaml + SDK for consumers — pure, deterministic, HITL, versioned, NO embeddings/RAG in canonical — whole STEMMA is here
- **Why NOT embedding/RAG in canonical STEMMA's job:** Embeddings are model-specific (All-MiniLM 384 vs BGE Large 1024 vs OpenAI Large 3072 vs NVIDIA NV-Embed 4096 give different vectors), non-deterministic, not time-invariant, would pollute canonical with floats, make content/ non-human-reviewable, would require STEMMA to choose one embedding model, one vector store, one LLM, one top_k for all consumers — impossible, because consumers have different needs (LearningHub prefers OpenAI Large 3072 high quality for student queries, PROFESSOR-J prefers BGE Large SOTA 1024 offline capable for AI professor, general prefers All-MiniLM fast local) — therefore embedding and RAG cannot be one-size-fits-all in STEMMA, must be consumer's job
- **CONSUMER's job — build embedding and RAG out of STEMMA as connection layer, NOT containing whole STEMMA:** LearningHub, PROFESSOR-J, general, explorer, STEMMA-RAG — in LearningHub repo or PROFESSOR-J repo or separate STEMMA-RAG repo — data/knowledge.json copied from STEMMA exports/knowledge.json, data/embeddings.jsonl generated externally via embed.py out of STEMMA, data/vector_store/ FAISS built externally out of STEMMA, rag.py retrieval + generation logic out of STEMMA, or via API calls to STEMMA API /v2/entities, /v2/stats content_hash, /v2/search, etc., or via SDK Stemma.from_file() or from_api() — generate vectors DERIVED from STEMMA definitions via embedding model (local free All-MiniLM/BGE Large + frontier OpenAI Large/NVIDIA NV-Embed, model selector like DeepSeek harness (local + frontier models)), build vector store FAISS/Chroma/Qdrant/Pinecone, serve RAG queries with retrieval + generation + citations — e.g., LearningHub: preferred_model OpenAI Large 3072 fallback BGE Large, RAG top_k 5 model GPT-4o, endpoints /v2/stats /v2/entities /v2/search /v2/rag/query /v2/embeddings, rate limit 1000/hour api_key, example "What is Newton's second law?" → embedding OpenAI Large → vector search top 5 → context definitions + sources → GPT-4o → answer with citations; PROFESSOR-J: preferred_model BGE Large SOTA 1024 offline fallback All-MiniLM, RAG top_k 10 model DeepSeek R1 free fallback Claude 3.5 Sonnet/GPT-4o/Gemini 2.5 Pro, all endpoints, rate limit 10000/hour, example "Explain photosynthesis and its relation to cellular respiration" → embedding BGE Large → vector search top 10 across biology → context → DeepSeek R1 free → answer with citations — why consumer's job: embedding model choice is consumer-specific, RAG top_k and LLM model choice is consumer-specific, vector store type is consumer-specific (FAISS local vs Chroma vs Qdrant vs Pinecone cloud), domain filter is consumer-specific (LearningHub canonical physics/chem/bio/math vs PROFESSOR-J reviewed all 8 domains mediocre), review_policy is consumer-specific (LearningHub canonical vs PROFESSOR-J reviewed vs general all), rate limiting and auth are consumer-specific — therefore embedding and RAG must be consumer's job, not STEMMA's job, to fit each consumer's needs — does NOT contain whole STEMMA, just connection layer, whole STEMMA remains in STEMMA repo
- **STEMMA provides reference implementation as optional derived + consumer layer for convenience and demo, but production embedding/RAG is consumer's job:** Currently inside STEMMA for convenience and demo (optional, INFO not FAIL): scripts/embed.py (local free + frontier, model selector like DeepSeek harness (local + frontier models), tries sentence-transformers if installed else fake deterministic hash-based for demo), scripts/rag.py (vector search + context + LLM generation with model selector like DeepSeek harness (local + frontier models) + citations, consumer-specific), scripts/export_consumers.py, exports/embeddings.jsonl (1 embeddings now deterministic fake for demo), exports/vector_store/ FAISS meta.json + vectors.json + ids.json versioned via content_hash + model id, exports/consumers/<consumer>/knowledge.<consumer>.json filtered, adapters/python/ v0.2.0 with /v2/embeddings, /v2/rag/search, POST /v2/rag/query, /v2/export, /openapi.yaml, webapp RAG playground with embedding model selector like DeepSeek harness (local + frontier models) + LLM selector + domain filter + consumer selector + Search + Query buttons + citations + consumer export buttons, examples/external-rag/ with README.md + embed.py + rag.py that are OUT OF STEMMA, connection layer, NOT whole STEMMA, proving embedding and RAG can be out of STEMMA, connecting via file/API/SDK + content_hash — why inside for now: convenient for demo, for LearningHub, PROFESSOR-J to see how embedding/RAG connects via file/API/SDK + content_hash, for testing retrieval precision + faithfulness + citation coverage, for webapp RAG playground, for verify_all.py INFO checks — but production embedding/RAG is consumer's job, not STEMMA's job — can be out: YES, move to separate repo STEMMA-RAG or to LearningHub/PROFESSOR-J repos, keep STEMMA core pure with only content/, connections/, sources/, schema/, validate.py, export_review_aware.py, graph_analysis.py, status_truth.py, verify_all.py (canonical checks as FAIL, embeddings/RAG/consumer export checks as INFO) — then STEMMA exports knowledge.json + API schema + SDK, external RAG in LearningHub/PROFESSOR-J consumes via file/API/SDK + content_hash + deterministic regeneration — cleaner separation, STEMMA remains pure knowledge foundation, embedding/RAG are external consumers, connection layer, not containing whole STEMMA — example in examples/external-rag/ proves it works out of STEMMA

**Recommendation:**
- STEMMA's job: Provide knowledge foundation — content/, connections/, sources/, schema/, knowledge.json v2.2.0 deterministic content-hash, openapi.yaml, SDK, validation gate — pure, deterministic, HITL, versioned, NO embeddings/RAG in canonical, NO vectors in content/
- CONSUMER's job: Build embedding and RAG out of STEMMA as connection layer — generate embeddings via embedding-registry models, build vector store FAISS/Chroma/Qdrant/Pinecone, serve RAG queries with retrieval + generation + citations, choose embedding model, top_k, LLM model, domain filter, review_policy, rate limiting, auth per consumer needs — LearningHub, PROFESSOR-J, general, explorer, STEMMA-RAG — does NOT contain whole STEMMA, just connection layer, whole STEMMA remains in STEMMA repo
- STEMMA provides reference implementation: scripts/embed.py, rag.py, export_consumers.py, exports/embeddings.jsonl, vector_store/, adapters/python/ v0.2.0, webapp RAG playground, examples/external-rag/ — optional, INFO not FAIL, for convenience, demo, testing, but production embedding/RAG is consumer's job

**Therefore:** Embedding and RAG is CONSUMER's job, not STEMMA's job — STEMMA provides knowledge foundation + reference implementation as optional derived + consumer layer for convenience and demo, but production embedding and RAG is consumer's job (LearningHub, PROFESSOR-J, general, explorer, STEMMA-RAG) as connection layer out of STEMMA, not containing whole STEMMA, connecting via exports/knowledge.json + API + SDK + content_hash, with model selector like DeepSeek harness (local + frontier models) for both embedding and LLM.


## Guideline — How to Build Embedder and RAG That Imports From STEMMA Consistently (NEW 2026-09-21 — v1.0.0)

See **[GUIDELINE-EMBEDDER-RAG.md](GUIDELINE-EMBEDDER-RAG.md)** — authoritative 81KB guideline for consumers to build consistent embedder + RAG architecture that imports from STEMMA via file/API/SDK + content_hash.

**What it covers:**
- Direction we are going: comprehensive all-STEM mediocre (8 domains 97 subdomains 12 entity types 400-800 target) + clean separation Layer1 Canonical (NO embeddings/RAG, whole STEMMA), Layer2 Derived (YES embeddings as derived regenerable deterministic content-hash), Layer3 Consumer+RAG (YES RAG as consumer mechanism, can be out of STEMMA)
- New change already implemented (2026-09-21): template-registry v2.0.0 8 domains, embedding-registry v1.0.0 11 models local free + frontier with model selector like DeepSeek harness, consumer-registry v1.0.0 4 consumers LearningHub OpenAI Large 3072 GPT-4o top_k5 PROFESSOR-J BGE Large 1024 offline DeepSeek R1 free top_k10, API schema v2.2.0 OpenAPI 3.0.3, embed.py rag.py export_consumers.py adapter v0.2.0 /v2/embeddings /v2/rag/search POST /v2/rag/query /v2/export /openapi.yaml webapp RAG playground, examples/external-rag/ out-of-STEMMA proving embedding/RAG can be out as connection layer NOT whole STEMMA via file/API/SDK + content_hash
- Future plans: R1 NOW 400-800 + embeddings + RAG + consumer export + guideline + sample, R2 Math Layer + Governing Laws + Embeddings SOTA (BGE-M3, GTE, Jina, E5-Mistral, re-ranking, ColBERT, HyDE) + RAG Evaluation (retrieval precision, faithfulness, citation coverage, re-ranking, multi-hop, HyDE, self-RAG, evaluation dataset) + Consistent Architecture (TypeScript adapter, Python package stemma-rag, consistent import via file/API/SDK + content_hash, model selector, deterministic versioning, context building with citations, API, webapp playground, evaluation metrics) + Production API hosting, R3 Other Domains LATER + Production RAG + Hosted Vector Store Qdrant/Pinecone + Consistent Architecture Across All Consumers via guideline
- Embedder best practices: model selector like DeepSeek harness 11 models, chunking entity strategy 512 tokens deterministic, content-hash sha256(text+model_id+knowledge content_hash)[:16] versioned batch 32 normalize, vector store FAISS flat cosine meta.json v1.0.0, storage embeddings.jsonl + vector_store/
- RAG best practices: retriever vector search cosine FAISS top_k 5 LearningHub 10 PROFESSOR-J domain filter, context building definitions+connections+sources+source_refs+links+scores with citations, generator LLM model selector like DeepSeek harness 25 models DeepSeek R1 free Claude 3.5 Sonnet GPT-4o Gemini 2.5 Pro Llama 3.3 custom citation enforcement, full flow question->embedding->vector search->context->LLM->answer with citations, API /v2/rag/search GET POST /v2/rag/query, webapp RAG playground
- Sample in derived: inside STEMMA scripts/embed.py rag.py exports/embeddings.jsonl vector_store/ meta.json deterministic + out-of-STEMMA examples/external-rag/embed.py rag.py data/embeddings.jsonl data/vector_store/ out-of-STEMMA connection layer NOT whole STEMMA


