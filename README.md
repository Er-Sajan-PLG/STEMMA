# STEMMA

> An **open, structured, reusable knowledge foundation for STEM** — concepts,
> quantities, laws, models, and the relationships between them, expressed as
> version-controlled, machine-readable, human-reviewable data.
> Curriculum is external. Products are external. AI systems are consumers like LearningHub, PROFESSOR-J.

## What this is — comprehensive all-STEM mediocre, not minimal physics, with embeddings, RAG, consumer export

STEMMA solves a data problem: established science and mathematics knowledge
is abundant in prose but scarce as *data*. STEMMA represents it as a governed
knowledge graph —

- **1 entity now (metre) via PDF primary ingestion with HITL, will grow to mediocre 400-800 across 8 domains** (`content/`) — physics, chemistry, biology, earth-science, astronomy, computer-science, engineering, mathematics — concepts, quantities, laws, units, constants, principles, theorems, equations, processes, structures, algorithms, materials as Markdown + validated YAML with exact definitions (e.g., metre = light path 1/299,792,458 s, c=299,792,458 m/s exact, agreed per BIPM 2019; chemical element per IUPAC Gold Book; algorithm per CLRS), will grow via primary PDF ingestion (SI Brochure 9th ed., HRW 12th ed., Campbell Biology, CLRS, Atkins, Carroll Astrophysics, custom PDFs for all 8 domains) with deterministic templates v2.0.0 that scale + LLM fallback only when PDF missing exact definition (model selector like DeepSeek harness (local + frontier models): DeepSeek R1 free, Claude 3.5 Sonnet, GPT-4o, Gemini 2.5 Pro, Llama 3.3 70B free, custom) + HITL human explicitly edits markdown before canonical + embeddings + RAG + consumer export,
- **0 first-class relationship assertions now, will grow to 500+** (`connections/`) — each claim is its own object with evidence source_ref+locator+description, context, confidence, review status, 8 relations only (mathematically_requires, derived_from, appears_in_law, applies_to, generalizes, special_case_of, part_of, approximates), mandatory evidence,
- **3 source records now, will grow to 20+** (`sources/`) — citations those assertions point to with url/doi/isbn + writer human:*, dual verification,

— validated by a strict gate (validate.py + physics_core_profile_check.py + physics_governing_check.py + hitl_check.py + evolvable_template.py + embed.py + rag.py + export_consumers.py + status_truth.py + verify_all.py) and published as deterministic, versioned exports (knowledge.json v2.1.0 content-hash sha256 no wall clock, embeddings.jsonl, vector_store/ FAISS, consumers/<consumer>/knowledge.<consumer>.json filtered, openapi.yaml) + REST API (adapter v0.2.0 endpoints /v2/entities, /v2/embeddings, /v2/rag/search, /v2/rag/query POST, /v2/export?consumer=..., /openapi.yaml OpenAPI 3.0.3) + SDK (Python Stemma.from_file + StemmaRAG) that any curriculum, application, or AI system like LearningHub, PROFESSOR-J can build on.

**Old 74 entities + 150 connections archived to archive/beginning-74-entities/ — this is beginning clean comprehensive all-STEM mediocre, deterministic scales, evolvable templates v2.0.0, model selector like DeepSeek harness (local + frontier models), PDF primary, HITL before canonical, embeddings, RAG, consumer export.**

### Do we need embedding model? YES.

Embedding model generates vectors for entities for RAG and consumer export. Without embeddings static JSON, with embeddings LearningHub students query "Newton's law" via vector similarity, PROFESSOR-J answers offline. Supports local free All-MiniLM 384 fast, BGE Large SOTA 1024 best for RAG, frontier API OpenAI text-embedding-3-large 3072 best quality, NVIDIA NV-Embed SOTA 4096 free via NIM, model selector like DeepSeek harness (local + frontier models).

### Do we need RAG system in STEMMA? YES.

STEMMA is knowledge foundation, RAG is how consumers like LearningHub, PROFESSOR-J use it. Without RAG static JSON, with RAG queryable knowledge with citations. Flow: question → embedding → vector search top_k → context definitions + connections + sources → LLM frontier selector → answer with citations. API /v2/rag/search GET + /v2/rag/query POST, webapp RAG playground.

### Do we need export mechanism via api schema link/api? YES.

Export mechanism via file (knowledge.json deterministic content-hash, embeddings.jsonl, vector_store/ FAISS, consumers/<consumer>/knowledge.<consumer>.json filtered), API (adapter v0.2.0 endpoints /v2/entities, /v2/embeddings, /v2/rag/search, /v2/rag/query POST, /v2/export?consumer=..., /openapi.yaml OpenAPI 3.0.3), SDK (Python), for LearningHub (canonical physics/chem/bio/math, OpenAI embeddings, GPT-4o RAG), PROFESSOR-J (reviewed all 8 domains mediocre, BGE Large offline SOTA, FAISS, DeepSeek R1 free RAG).

## Status: live foundation in early curation

<!-- status-truth:start -->
## Status: live foundation in early curation

Machine-checkable live counts — `scripts/status_truth.py` (CI) fails if this
block drifts from canonical content (audit F2: status honesty is a gate):

- Entities: **1** — human-reviewed/canonical: **0**, draft: **1**
- Connections (first-class assertions): **0** — review-canonical: **0** (0.0%), unreviewed: **0**
- Canonical source records: **3**
<!-- status-truth:end -->







Canonicality is a *reviewed* property, not a folder: consumers should filter
by review status (`docs/CONSUMERS.md`). Architecture baseline **3.0.0**
(ADR-0029). Now comprehensive all-STEM mediocre with 8 domains, embeddings, RAG, consumer export.

## Repository layout — comprehensive all-STEM

```text
STEMMA/
├── content/<domain>/  canonical entities (Markdown + YAML frontmatter) — 8 domains physics, chemistry, biology, earth-science, astronomy, computer-science, engineering, mathematics, 12 entity types, mediocre 400-800 total
├── connections/      canonical relationship assertions (one YAML object per claim)
├── sources/          canonical citation records
├── schema/           JSON Schema contracts, relation/agent/extension registries, vocabularies, template-registry v2.0.0 comprehensive all-STEM 8 domains 97 subdomains 12 entity types, embedding-registry v1.0.0 12 models, consumer-registry v1.0.0 4 consumers, api.yaml OpenAPI 3.0.3
├── adapters/python/  first-party read-only Python consumer adapter v0.2.0 (SDK, CLI, local JSON API with embeddings + RAG + consumer export + OpenAPI)
├── scripts/          the validation gate, review workflow, ingestion, derived-artifact builders, embedding generator embed.py, RAG system rag.py, consumer export export_consumers.py, evolvable templates, HITL check
├── webapp/           stdlib ingestion/review UI + RAG playground (upload → extract → deterministic draft no LLM scales OR AI draft frontier → human review HITL → staged proposal, plus RAG playground embedding model selector + LLM selector + vector search + RAG query with citations, plus consumer export)
├── exports/          DERIVED artifacts (regenerable; never the source of truth) — knowledge.json v2.1.0 deterministic content-hash, embeddings.jsonl, vector_store/ FAISS meta.json + vectors.npy + ids.json, consumers/<consumer>/knowledge.<consumer>.json filtered, openapi.yaml
├── tests/            invariant test suite (layered)
├── explorer/         stemma — reference 3-D graph explorer (a consumer; reads only the export) — clean 3D small nodes thin lines legend manual zoom centered with domain filter for 8 domains
└── docs/             the authoritative documentation set — ARCHITECTURE comprehensive all-STEM mediocre + embeddings + RAG + consumer export, CONSUMERS with LearningHub PROFESSOR-J, EMBEDDINGS with model selector like DeepSeek harness (local + frontier models), RAG with retrieval + generation + citations, API with OpenAPI, etc.
```

## Quick start — comprehensive all-STEM with embeddings, RAG, consumer export

```bash
pip install pyyaml jsonschema        # gate dependencies
python3 scripts/verify_all.py        # full verification chain (what CI runs) — validate + physics_core_profile_check + physics_governing_check + hitl_check + evolvable_template + embed + rag + export_consumers + status_truth
python3 scripts/validate.py          # validate canonical data + regenerate the export
python3 scripts/embed.py --model sentence-transformers/all-MiniLM-L6-v2 --output exports/embeddings.jsonl  # generate embeddings (fake deterministic if torch not installed)
python3 scripts/rag.py --search "metre" --top-k 2  # vector search
python3 scripts/rag.py --question "What is metre?" --top-k 2 --model deepseek/deepseek-r1:free --consumer general  # RAG query with citations
python3 scripts/export_consumers.py --consumer general --format json  # consumer export
```

Exit code `0` = valid. To explore visually: `npm --prefix explorer run dev`.
For document ingestion/review + RAG playground: `python3 webapp/server.py --port 8081`
(see [`docs/WEBAPP.md`](docs/WEBAPP.md) + [`docs/RAG.md`](docs/RAG.md) + [`docs/EMBEDDINGS.md`](docs/EMBEDDINGS.md) + [`docs/API.md`](docs/API.md)). The webapp's Draft seam is a
provider abstraction (`webapp/providers.py`): the default **Antigravity**
provider uses the official Antigravity SDK or `agy` CLI on the webapp host with
your local Google AI Pro session (no Gemini API key); `gemini_api`, `vertex_ai`,
and `openai_compatible` are separate entitlements (ADR-0038). Without
poppler-utils, install the pure-Python PDF fallback for text PDFs:
`pip install pypdf`. For embeddings, pip install sentence-transformers torch for local models, or set API key for frontier OpenAI/Cohere/Gemini/NVIDIA.

## Get the content out — file, API, SDK, RAG, consumer export

```bash
# File-based
cat exports/knowledge.json | python3 -c "import json; print(json.load(open('exports/knowledge.json'))['content_hash'])"
cat exports/embeddings.jsonl | head -n 1
ls exports/vector_store/  # meta.json + vectors.npy + ids.json
ls exports/consumers/general/  # knowledge.general.json

# API — adapter v0.2.0 with embeddings + RAG + consumer export + OpenAPI
PYTHONPATH=adapters/python python3 -m stemma_adapter serve exports/knowledge.json --port 8080
curl http://127.0.0.1:8080/v2/stats
curl "http://127.0.0.1:8080/v2/search?q=force&domain=physics"
curl "http://127.0.0.1:8080/v2/embeddings?model=BAAI/bge-large-en-v1.5&limit=5"
curl "http://127.0.0.1:8080/v2/rag/search?q=Newton%20second%20law&top_k=5"
curl -X POST http://127.0.0.1:8080/v2/rag/query -H "Content-Type: application/json" -d '{"question":"What is Newton second law?","top_k":5,"model":"deepseek/deepseek-r1:free","consumer":"learninghub"}'
curl "http://127.0.0.1:8080/v2/export?consumer=learninghub&format=json"
curl http://127.0.0.1:8080/openapi.yaml

# SDK
PYTHONPATH=adapters/python python3 -c "from stemma_adapter import Stemma; s=Stemma.from_file('exports/knowledge.json'); print(s.stats)"
python3 scripts/rag.py --question "What is Newton's second law?" --top-k 5 --model deepseek/deepseek-r1:free --consumer learninghub

# Webapp RAG playground
python3 webapp/server.py --port 8081
# Open http://localhost:8081 — new RAG Playground section with embedding model selector like DeepSeek harness (local + frontier models) + LLM selector + domain filter + consumer selector + Search + Query buttons + citations
```

## Documentation — comprehensive all-STEM

Start with [`docs/README.md`](docs/README.md). Key entry points:
[VISION](docs/VISION.md) · [ARCHITECTURE](docs/ARCHITECTURE.md) ·
[DOMAIN-MODEL](docs/DOMAIN-MODEL.md) · [GOVERNANCE](docs/GOVERNANCE.md) ·
[CONSUMERS](docs/CONSUMERS.md) · [EMBEDDINGS](docs/EMBEDDINGS.md) · [RAG](docs/RAG.md) · [API](docs/API.md) · [GUIDELINE-EMBEDDER-RAG](docs/GUIDELINE-EMBEDDER-RAG.md) · [CONTRIBUTING](docs/CONTRIBUTING.md) ·
[ROADMAP](docs/ROADMAP.md).

## Ground rules — comprehensive all-STEM with HITL + embeddings + RAG + consumer export

1. Canonical knowledge lives only in `content/`, `connections/`, `sources/`;
   everything derived is regenerable (knowledge.json, embeddings.jsonl, vector_store/, consumers/).
2. No curriculum, grade, course, country, or product appears in canonical
   data (machine-checked).
3. AI-drafted content stays `draft` until a named human reviews it — HITL enforced, audit trail candidate_edited by human:*, writer human:*, markdown explicit edit before canonical, hitl_check.py.
4. Stable IDs (`stemma:…`) are never reused or reassigned; corrected claims
   are superseded, never edited in place.
5. The gate decides: if `verify_all.py` fails, nothing ships — includes validate + physics_core_profile_check + physics_governing_check + hitl_check + evolvable_template + embed + rag + export_consumers + status_truth.
6. Deterministic, content-hash stamped, no wall clock, versioned exports v2.1.0 + embeddings content_hash + vector_store content_hash, deterministic same content + model → same embeddings.
7. Embeddings — YES needed for RAG and consumer export, local free + frontier API, model selector like DeepSeek harness (local + frontier models).
8. RAG — YES needed in STEMMA as knowledge foundation, retrieval + generation + citations, for LearningHub, PROFESSOR-J.
9. Consumer export — YES needed via file, API, SDK, OpenAPI schema, for LearningHub, PROFESSOR-J, general, explorer.

## License

- **Knowledge content** (`content/`, `connections/`, `sources/`, `docs/`):
  **Creative Commons Attribution 4.0** — see [`LICENSE`](LICENSE).
- **Code** (`scripts/`, `schema/`, `tests/`, `explorer/`, `adapters/`): **MIT** — see
  [`LICENSE-CODE`](LICENSE-CODE).

Rationale: ADR-0001. Now comprehensive all-STEM mediocre, 8 domains, embeddings, RAG, consumer export for LearningHub, PROFESSOR-J.


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
