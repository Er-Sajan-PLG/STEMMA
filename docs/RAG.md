# RAG — Retrieval-Augmented Generation for STEMMA — Comprehensive All-STEM, LearningHub, PROFESSOR-J

**Status:** Authoritative, v1.0.0, comprehensive all-STEM mediocre coverage with RAG system for consumers like LearningHub, PROFESSOR-J. Old minimal physics had no RAG — now YES RAG system needed in STEMMA.

## Do we need RAG system here in STEMMA? YES.

**Answer:** Yes, we need RAG system in STEMMA. STEMMA is knowledge foundation (concepts, quantities, laws, models, relationships as version-controlled, machine-readable, human-reviewable data). RAG is how consumers like LearningHub, PROFESSOR-J use it. Without RAG, STEMMA is just static JSON export. With RAG, it's queryable knowledge with citations, grounded answers, retrieval + generation.

- **Without RAG:** Consumer gets knowledge.json (1 entity now, will be 400-800 mediocre all-domain) and must manually search via keyword or build own RAG. LearningHub students can't ask "What is Newton's second law?" and get answer with citations. PROFESSOR-J AI professor can't answer STEM questions.
- **With RAG:** Consumer queries via /v2/rag/query or via SDK StemmaRAG, gets answer grounded in STEMMA entities with citations (source_refs + links), retrieval precision, faithfulness, citation coverage.

## RAG Architecture — comprehensive, for LearningHub, PROFESSOR-J

### Components

1. **Ingestion:** PDF → deterministic extraction via template-registry v2.0.0 (regex + exact constants for all 8 domains) → entity markdown preview → human explicitly edits markdown (HITL) → stage → validate (including hitl_check) → canonical → knowledge.json deterministic content-hash

2. **Embedding:** Entity → chunking (entity strategy, definition + name + domain + subdomain + symbol + unit, max_tokens 512, overlap 50) → embedding via embedding-registry model (local free All-MiniLM 384 fast, BGE Large SOTA 1024 best for RAG, frontier API OpenAI text-embedding-3-large 3072 best quality, NVIDIA NV-Embed SOTA 4096 free via NIM) → embeddings.jsonl + vector_store/ FAISS (meta.json + vectors.json + ids.json) versioned via content_hash + model id, deterministic same content + model → same embeddings

3. **Vector store:** FAISS (default flat index cosine metric local deterministic) path exports/vector_store/, alternatives Chroma exports/chroma/, Qdrant local, Pinecone cloud — meta.json with model, dimensions, content_hash, entity_count, created_at deterministic no wall clock, version 1.0.0, type faiss, index_type flat, metric cosine — versioned via content_hash of knowledge.json + embedding model id

4. **Retriever:** Query → embedding via same embedding model → vector search cosine similarity over FAISS (or fake deterministic hash-based if torch not installed for demo) → top_k entities with scores + content (definition + domain + sources) — e.g., query "What is Newton's second law?" → retrieves force, mass, acceleration, Newton's second law, etc.

5. **Generator:** Retrieved entities → build context with definitions + connections + sources + source_refs + links → LLM prompt with context + question → call LLM with model selector like DeepSeek harness (local + frontier models: DeepSeek R1 free 671B reasoning, DeepSeek V3 free 671B, Claude 3.5 Sonnet frontier, Claude 3 Opus reasoning, GPT-4o frontier multimodal, o1 reasoning frontier, Gemini 2.5 Pro frontier, Gemini 2.0 Flash free, Llama 3.3 70B free, custom via OpenRouter/NVIDIA NIM/OpenAI-compatible) → answer with citations (entity_id + source_ref + link)

6. **API:** /v2/rag/search GET (vector search) + /v2/rag/query POST (full RAG) via adapter server v0.2.0 and webapp server — for LearningHub, PROFESSOR-J

7. **Webapp RAG playground:** Embedding model selector like DeepSeek harness (local + frontier models) with search, categories Frontier/Free/Local/SOTA/Fast, model cards FREE/FRONTIER/LOCAL badges, custom input) + LLM model selector like DeepSeek harness (local + frontier models: DeepSeek R1 free, Claude 3.5 Sonnet, GPT-4o, Gemini 2.5 Pro, Llama 3.3, custom) + domain filter (8 domains) + consumer selector (LearningHub, PROFESSOR-J, general) + top_k + question input + answer display with citations + retrieved entities with scores

### Flow

```
User question ("What is Newton's second law?") 
→ embedding via embedding model (e.g., BAAI/bge-large-en-v1.5 1024 dim SOTA local, or OpenAI text-embedding-3-large 3072 dim frontier)
→ vector search top_k (e.g., 5) cosine similarity over FAISS vector_store/ (vectors.json + ids.json, meta.json content_hash versioned)
→ retrieved entities: [stemma:phys.force score 0.85, stemma:phys.mass score 0.82, stemma:phys.newtons-second-law score 0.90, etc.] with content (definition + domain + subdomain + type + symbol + unit + provenance source + link + source_refs)
→ build context: "STEMMA Knowledge Foundation — comprehensive all-STEM, mediocre coverage, with citations\n1. Force (stemma:phys.force) — Domain: physics/mechanics Type: quantity\n   Definition: Force is...\n   Source: HRW 12th Ch5 p112 Link: https://... Writer: human:curator.001\n   Source refs: nistsi, halliday\n   Score: 0.85\n..."
→ LLM prompt: "You are STEMMA AI professor. Answer question based on context with citations. Context: {context}\nQuestion: {question}\nProvide answer with citations (entity_id + source_ref + link). Must be grounded in context."
→ call LLM model selector like DeepSeek harness (local + frontier models: DeepSeek R1 free via OpenRouter, or Claude 3.5 Sonnet, GPT-4o, Gemini 2.5 Pro, Llama 3.3, custom) — in demo, fake deterministic answer if no API key
→ answer: "Based on STEMMA knowledge foundation...\nNewton's second law states F=ma... [citations: stemma:phys.force source_ref halliday link ...]\nCitations: - stemma:phys.force source_ref halliday link ..."
→ return {question, answer, citations [{entity_id, source_ref, link}], retrieved_entities [{entity, score, content}], model_used, embedding_model_used, content_hash, top_k, domain, consumer}
```

### Evaluation

- **Retrieval precision:** top_k relevant entities — does vector search retrieve relevant entities for query? Measured via score threshold, e.g., top 5 should include Newton's second law for query "Newton second law"
- **Answer faithfulness:** answer grounded in retrieved entities, not hallucinated — LLM must use only context, with citations, no outside knowledge
- **Citation coverage:** every claim has source_ref + link — e.g., "Force is defined as..." must have citation to halliday source_ref + link https://...

### Versioning — deterministic, content-hash, no wall clock

- **Vector store versioned via content_hash of knowledge.json + embedding model id** — same knowledge.json content_hash + model id → same embeddings + same FAISS index, deterministic, no wall clock
- **Embeddings versioned via content_hash** — content_hash = sha256(text + model_id + knowledge.json content_hash)[:16]
- **RAG answer versioned via content_hash + model_used + embedding_model_used** — deterministic same question + same knowledge + same models → same retrieved + same context (but LLM generation may be non-deterministic unless temperature 0)

## API — /v2/rag/search GET + /v2/rag/query POST

Defined in `schema/api.yaml` OpenAPI 3.0.3 and implemented in `adapters/python/stemma_adapter/server.py` v0.2.0 and `webapp/server.py`:

### GET /v2/rag/search?q=...&top_k=...&model=...&domain=...

- **Query:** q (required) e.g., "What is Newton's second law?", top_k (default 5), model (embedding model ID e.g., BAAI/bge-large-en-v1.5), domain (filter e.g., physics)
- **Response:** {query, top_k, model, results: [{entity, score, content, entity_id}]}
- **Example:** `curl "http://localhost:8080/v2/rag/search?q=Newton%20second%20law&top_k=5&model=BAAI/bge-large-en-v1.5&domain=physics"`
- **Implementation:** Calls rag.vector_search (cosine similarity) if embeddings exist, else falls back to text search via adapter search

### POST /v2/rag/query

- **Body:** {question (required), top_k (default 5), model (LLM model ID e.g., deepseek/deepseek-r1:free), embedding_model (e.g., BAAI/bge-large-en-v1.5), domain, consumer (learninghub, professor-j, general)}
- **Response:** {question, answer, citations [{entity_id, source_ref, link}], retrieved_entities [{entity, score, content}], model_used, embedding_model_used, content_hash, top_k, domain, consumer}
- **Example:**
  ```bash
  curl -X POST http://localhost:8080/v2/rag/query -H "Content-Type: application/json" -d '{
    "question": "What is Newton second law?",
    "top_k": 5,
    "model": "deepseek/deepseek-r1:free",
    "embedding_model": "BAAI/bge-large-en-v1.5",
    "domain": "physics",
    "consumer": "learninghub"
  }'
  ```
- **Implementation:** Calls rag.rag_query — vector_search + build_context + call_llm (tries webapp providers, else fake deterministic demo if no API key)

## SDK — Python

```python
import sys
sys.path.insert(0, "scripts")
import rag

# Vector search
results = rag.vector_search("What is Newton's second law?", top_k=5, model_id="BAAI/bge-large-en-v1.5", domain="physics")
for res in results:
    print(f"{res['entity_id']} score={res['score']:.4f} {res['entity'].get('name')}")

# Full RAG query
answer = rag.rag_query(
    "What is Newton's second law?",
    top_k=5,
    model_id="deepseek/deepseek-r1:free",
    embedding_model="BAAI/bge-large-en-v1.5",
    domain="physics",
    consumer="learninghub"
)
print(answer['answer'])
print(answer['citations'])
```

Future: `from stemma_adapter.rag import StemmaRAG; rag = StemmaRAG.from_files("exports/knowledge.json", "exports/vector_store/"); answer = rag.query("What is Newton's second law?", top_k=5, model="deepseek/deepseek-r1:free")`

## CLI

```bash
# List embedding and LLM models
python3 scripts/rag.py --list-models

# Vector search
python3 scripts/rag.py --search "force" --top-k 5 --embedding-model BAAI/bge-large-en-v1.5 --domain physics

# Full RAG query
python3 scripts/rag.py --question "What is Newton's second law?" --top-k 5 --model deepseek/deepseek-r1:free --embedding-model BAAI/bge-large-en-v1.5 --domain physics --consumer learninghub

# With consumer-specific model
python3 scripts/rag.py --question "Explain photosynthesis" --top-k 10 --model deepseek/deepseek-r1:free --consumer professor-j
```

## Consumer-specific RAG config

Defined in `schema/consumer-registry.yaml` v1.0.0:

- **LearningHub:** top_k 5, model GPT-4o (frontier multimodal), embedding_model OpenAI text-embedding-3-large 3072, domains physics/chem/bio/math canonical, rate limit 1000/hour api_key, example "What is Newton's second law?"
- **PROFESSOR-J:** top_k 10, model DeepSeek R1 free 671B reasoning fallback Claude 3.5 Sonnet/GPT-4o/Gemini 2.5 Pro, embedding_model BGE Large SOTA 1024 offline, domains all 8 mediocre reviewed, rate limit 10000/hour api_key, example "Explain photosynthesis and its relation to cellular respiration"
- **General:** top_k 5, no specific LLM, embedding_model All-MiniLM fast local
- **Explorer:** no RAG (3D graph)

## Why RAG needed for LearningHub, PROFESSOR-J?

- **LearningHub:** Learning platform needs to answer student questions with citations from STEMMA. Without RAG, students get static JSON. With RAG, they ask natural language, get grounded answer with citations (source_refs + links), retrieval precision high with OpenAI Large embeddings, generation quality high with GPT-4o.
- **PROFESSOR-J:** AI professor needs to answer STEM questions across 8 domains mediocre coverage, offline capable (BGE Large SOTA local, FAISS local), reasoning (DeepSeek R1 free 671B), citations for trust. RAG provides retrieval + generation + citations.

## Webapp RAG playground — NEW

In webapp UI (http://localhost:8081), new section RAG Playground:

- Embedding model selector like DeepSeek harness (local + frontier models): search bar, category tabs All/Frontier/Free/Local/SOTA/Fast, model cards with badges, custom input
- LLM model selector like DeepSeek harness (local + frontier models): DeepSeek R1 free, Claude 3.5 Sonnet, GPT-4o, Gemini 2.5 Pro, Llama 3.3, custom
- Domain filter: 8 domains dropdown (physics, chemistry, biology, earth-science, astronomy, computer-science, engineering, mathematics) + all
- Consumer selector: LearningHub, PROFESSOR-J, general
- Top K slider: 1-20
- Question input textarea
- Search button (vector search) + Query button (full RAG)
- Results: retrieved entities with scores + content + domain + type + source + link, answer with citations, model_used, embedding_model_used, content_hash

Implemented in webapp/static/app.js + index.html + style.css — new RAG section with model selectors.

## Related docs

- `schema/embedding-registry.yaml` — embedding models
- `schema/consumer-registry.yaml` — consumer RAG config
- `schema/api.yaml` — /v2/rag/search and /v2/rag/query endpoints
- `scripts/embed.py` — generates embeddings for RAG
- `scripts/rag.py` — RAG system
- `docs/EMBEDDINGS.md` — embeddings
- `docs/CONSUMERS.md` — consumer-specific RAG
- `adapters/python/stemma_adapter/server.py` v0.2.0 — RAG endpoints
- `webapp/server.py` — RAG endpoints + RAG playground


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


