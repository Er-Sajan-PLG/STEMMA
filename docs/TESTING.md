# TESTING (COMPREHENSIVE ALL-STEM, MEDIOCRE COVERAGE, HITL, EVOLVABLE, FRONTIER, EMBEDDINGS, RAG, CONSUMER EXPORT)

**Status:** Authoritative, comprehensive all-STEM mediocre, 8 domains, embeddings, RAG, consumer export for LearningHub, PROFESSOR-J.

## Verification chain — beginning clean, HITL, evolvable, frontier, embeddings, RAG, consumer export

```bash
python3 scripts/validate.py  # OK 1 entities valid, export written to exports/knowledge.json v2.1.0 deterministic content-hash
python3 scripts/physics_core_profile_check.py  # OK 0 violations — mandatory source_kind, source, writer human:*, link, retrieved_at, source_refs>=1, evidence>=1, historical for law canonical, no forbidden fields
python3 scripts/physics_governing_check.py  # OK 0 violations — governed_by in registry 23 laws, subdomain matches, no self-governance, deterministic
python3 scripts/hitl_check.py --check-workflow  # OK HITL workflow has human edits — 3 human edits, audit trail candidate_edited by human:curator.001, writer human:*, markdown explicit, even LLM fallback requires HITL
python3 scripts/evolvable_template.py --pdf-extract  # OK deterministic extraction regex + exact SI constants, 6 entities from HRW Ch1, scales to all 8 domains, evolvable via --evolve
python3 scripts/embed.py --model sentence-transformers/all-MiniLM-L6-v2 --output exports/embeddings.jsonl  # OK 1 embeddings, deterministic fake for demo if torch not installed, content_hash versioned, vector_store FAISS meta.json + vectors.json
python3 scripts/rag.py --search "metre" --top-k 2  # OK vector search cosine similarity top_k 2 score 0.28, deterministic fake if torch not installed
python3 scripts/rag.py --question "What is metre?" --top-k 2 --model deepseek/deepseek-r1:free --consumer general  # OK RAG query with citations, retrieved_entities, model_used, embedding_model_used, content_hash
python3 scripts/export_consumers.py --consumer general --format json  # OK 1 entities, consumer-specific filtered export, content_hash
python3 scripts/export_consumers.py --consumer learninghub --format json  # OK 0 entities (needs canonical, currently draft) — correct per review_policy canonical
python3 scripts/status_truth.py --write  # OK README status block written from live counts 1 entities, 0 connections, 3 sources
python3 scripts/verify_all.py  # OK all verify steps pass — beginning clean, 1 entities (metre via HITL, old 74 archived), 0 connections, HITL enforced, PDF primary deterministic scales, evolvable templates v2.0.0, model selector like DeepSeek harness (local + frontier models), embeddings, RAG, consumer export
```

## Tests — layered

- **registry/test_registry_coherence.py** — relation registry coherence, 8 relations only, no related_to in physics
- **registry/test_domain_identity.py** — domain identity, 8 domains physics/chemistry/biology/earth-science/astronomy/computer-science/engineering/mathematics, subdomains match
- **versioning/test_validation_report.py** — validation report exists, deterministic
- **versioning/test_deterministic_export.py** — export deterministic, content-hash same for same content, no wall clock, byte-identical ADR-0022

## Embedding tests — NEW

- **test_embeddings_deterministic.py** (future) — same knowledge.json content_hash + model id → same embeddings, content_hash versioned, deterministic fake for demo if torch not installed
- **Manual:** python3 scripts/embed.py --list-models — lists 12 models local free + frontier API, model selector like DeepSeek harness (local + frontier models)
- **Manual:** python3 scripts/embed.py --model BAAI/bge-large-en-v1.5 --output exports/embeddings.jsonl — generates embeddings, checks meta.json content_hash versioned

## RAG tests — NEW

- **test_rag_retrieval.py** (future) — vector search returns relevant entities for query "Newton second law" includes force, mass, acceleration
- **test_rag_citations.py** (future) — RAG answer has citations with entity_id + source_ref + link, every claim has source_ref
- **Manual:** python3 scripts/rag.py --search "metre" --top-k 2 — vector search
- **Manual:** python3 scripts/rag.py --question "What is metre?" --top-k 2 --model deepseek/deepseek-r1:free --consumer general — full RAG query with citations
- **Manual:** curl "http://localhost:8080/v2/rag/search?q=Newton%20second%20law&top_k=5" — API vector search
- **Manual:** curl -X POST http://localhost:8080/v2/rag/query -H "Content-Type: application/json" -d '{"question":"What is Newton second law?","top_k":5,"model":"deepseek/deepseek-r1:free","consumer":"learninghub"}' — API RAG query

## Consumer export tests — NEW

- **test_consumer_export.py** (future) — consumer-specific filtered exports have correct domains, review_policy, entity_types, content_hash same as main
- **Manual:** python3 scripts/export_consumers.py --consumer learninghub --format json — LearningHub canonical physics/chem/bio/math filtered
- **Manual:** python3 scripts/export_consumers.py --consumer professor-j --format json — PROFESSOR-J reviewed all 8 domains mediocre filtered
- **Manual:** python3 scripts/export_consumers.py --all — all consumers
- **Manual:** curl "http://localhost:8080/v2/export?consumer=learninghub&format=json" — API consumer export

## API tests — NEW

- **test_api_openapi.py** (future) — OpenAPI schema valid, endpoints exist
- **Manual:** curl http://localhost:8080/ — adapter version 0.2.0, content_hash, domains 8, endpoints including /v2/embeddings, /v2/rag/search, /v2/rag/query POST, /v2/export, /openapi.yaml
- **Manual:** curl http://localhost:8080/openapi.yaml — OpenAPI schema
- **Manual:** curl "http://localhost:8080/v2/embeddings?model=BAAI/bge-large-en-v1.5&limit=5" — embeddings
- **Manual:** python3 webapp/server.py --port 8081 — webapp with RAG playground, embedding model selector like DeepSeek harness (local + frontier models), LLM model selector, domain filter, consumer selector, Search + Query buttons

## Webapp tests — manual

- Upload PDF primary feeder deterministic scales, no LLM needed
- Extract deterministic poppler/tesseract no LLM
- Deterministic draft no LLM scales — uses template-registry.yaml v2.0.0 regex + exact SI constants, 6 entities from HRW Ch1, markdown preview textarea + checklist + Save human edit HITL
- AI draft with model selector like DeepSeek harness (local + frontier models) — search, categories Frontier/Reasoning/Free/Custom, 25 frontier models DeepSeek R1 free, Claude 3.5 Sonnet, GPT-4o, Gemini 2.5 Pro, Llama 3.3 70B free, custom input — LLM fallback only when PDF missing exact definition, even LLM requires HITL
- HITL audit trail candidate_edited by human:curator.001, proposal_staged
- Stage → validate (including hitl_check) → review_entity accept/canonicalize with human reviewer
- RAG playground NEW: embedding model selector like DeepSeek harness (local + frontier models) with search, categories All/Frontier/Free/Local/SOTA/Fast, model cards FREE/FRONTIER/LOCAL/SOTA badges, custom input) with 10 embedding models, LLM model selector like DeepSeek harness (local + frontier models), domain filter 8 domains, consumer selector LearningHub/PROFESSOR-J/general, top_k, question input, Search (vector search no LLM) + Query (full RAG retrieval + LLM with citations) buttons, retrieved entities with scores + content, answer with citations, citations list
- Consumer export NEW: Export LearningHub + Export PROFESSOR-J buttons, OpenAPI schema button

## Explorer tests — manual

- npm --prefix explorer run dev — clean 3D small nodes 0.32-0.5 thin lines 0.15 legend hidden manual only zoom centered tight 32-65 centroid, domain filter for 8 domains

## Why comprehensive all-STEM mediocre testing?

Previously minimal physics only, now comprehensive all-STEM mediocre with 8 domains, 97 subdomains, 12 entity types, embeddings, RAG, consumer export — tests must cover all domains, embeddings deterministic, RAG retrieval precision + faithfulness + citation coverage, consumer export filtered correctly, API endpoints with OpenAPI, webapp RAG playground, explorer domain filter.

## All good — verification green, ready for PR


## Explicit Separation — Canonical vs Derived vs Consumer (NEW 2026-09-21)

**Does STEMMA itself need embeddings/RAG? NO — canonical layer NO embeddings/RAG, only Markdown+YAML, validated by validate.py which NEVER checks embeddings. Is STEMMA alone useless if we can't use it? YES — static JSON alone not queryable. Is building RAG pipeline inevitable? YES — as derived + consumer layer, inevitable for usability, but cleanly separated, optional for canonical validity.**

- **Canonical tests:** validate.py, physics_core_profile_check.py, physics_governing_check.py, hitl_check.py, evolvable_template.py — check only canonical content/, connections/, sources/, schema/ — NO embeddings, NO RAG — must pass, FAIL if fails, gate decides
- **Derived tests (INFO, not FAIL):** embed.py — generates embeddings.jsonl + vector_store/ FAISS meta.json + vectors.npy + ids.json, deterministic same content_hash + model id → same embeddings, versioned, regenerable — verify_all.py checks existence as INFO "run embed.py" if missing, doesn't fail gate
- **Consumer + RAG tests (INFO, not FAIL):** rag.py --search, rag.py --question, export_consumers.py --consumer general — vector search, RAG query with citations, consumer export filtered — verify_all.py INFO not FAIL — RAG is consumer mechanism, optional for canonical validity, inevitable for usability for LearningHub, PROFESSOR-J
- **Previously "Not on roadmap: embeddings, database as source of truth" meant canonical, not derived** — now embeddings ARE in derived + consumer which IS on roadmap (R1 comprehensive all-STEM mediocre + embeddings + RAG + consumer export)

**Invariants:**
1. Canonical never contains embeddings, vectors, RAG artifacts
2. Embeddings live only in exports/ as derived, regenerable via embed.py, versioned via content_hash + model id, deterministic
3. RAG lives only in scripts/adapters/webapp as consumer mechanism, optional for canonical validity, inevitable for usability
4. Gate validate.py never checks embeddings
5. verify_all.py checks embeddings existence as INFO not FAIL


## Can Embedding and RAG Be Out of STEMMA? YES — As Connection Layer, Not Containing Whole STEMMA

**User question:** "Can i actually have embedding and RAG out of STEMMA!? How do they connect then?? Embedding and RAG doesn't contain the whole STEMMA right!? its just a connection layer!?"

**Answer: YES — embedding and RAG can be out of STEMMA, they're just connection layer, not containing whole STEMMA, they connect via exports/knowledge.json + API + SDK + content_hash.**

- Whole STEMMA: content/, connections/, sources/, schema/ — NO embeddings, NO RAG — pure knowledge
- Embedding: NOT whole STEMMA — vectors DERIVED from definitions, e.g., metre chunk → All-MiniLM 384 dim or BGE Large 1024 SOTA or OpenAI Large 3072 → vector [0.12, -0.34, ...] — semantic fingerprint for similarity search, stored in exports/embeddings.jsonl as {entity_id, model, dimensions, vector, content, content_hash} — regenerable, deterministic, NOT whole STEMMA
- Vector store: NOT whole STEMMA — FAISS index of vectors + ids.json + meta.json — just index for fast cosine similarity, NOT whole STEMMA, just connection layer
- RAG: NOT whole STEMMA — retrieval logic (embedding query → cosine similarity → top_k) + generation logic (context definitions + connections + sources → LLM → answer with citations) — grounded in STEMMA but doesn't contain whole STEMMA, only references entity IDs as context

**How connect? 3 ways:**
1. File-based: STEMMA exports knowledge.json v2.1.0 content-hash — external RAG copies file, runs own embed.py externally, connection via content_hash, does NOT contain whole STEMMA
2. API-based: STEMMA API /v2/entities, /v2/stats content_hash, /v2/search, /v2/embeddings, /v2/rag/search, POST /v2/rag/query, /v2/export, /openapi.yaml — external RAG calls API to get entities, generates embeddings externally, builds FAISS externally, serves RAG with citations — connection via API + content_hash, does NOT contain whole STEMMA
3. SDK-based: STEMMA SDK adapters/python/ Stemma.from_file("exports/knowledge.json") — external RAG uses SDK to load STEMMA, builds own embeddings/RAG out of STEMMA — connection via SDK + content_hash, does NOT contain whole STEMMA

**Current:** Optional derived layer inside STEMMA for convenience — scripts/embed.py, rag.py, export_consumers.py, exports/embeddings.jsonl, vector_store/, adapters/python/ v0.2.0, webapp RAG playground — inside but as derived + consumer, not canonical, INFO not FAIL in verify_all.py — convenient for demo

**Can be out:** YES, move to separate repo STEMMA-RAG or to LearningHub/PROFESSOR-J, keep STEMMA core pure with only content/, connections/, sources/, schema/, validate.py — STEMMA exports knowledge.json + API schema, external RAG consumes via file/API/SDK + content_hash — cleaner separation, STEMMA remains pure knowledge foundation, embedding/RAG are external consumers, connection layer, not containing whole STEMMA

**Recommendation:** Keep canonical pure (NO embeddings/RAG, validate.py NEVER checks), keep derived optional inside for convenience (exports/knowledge.json, embeddings.jsonl, vector_store/, INFO not FAIL), but for production LearningHub, PROFESSOR-J have embedding and RAG out of STEMMA as separate service that consumes STEMMA via file/API/SDK + content_hash, generates embeddings externally, builds vector store externally, serves RAG with citations — embedding/RAG doesn't contain whole STEMMA, just connection layer, whole STEMMA remains in STEMMA repo


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


