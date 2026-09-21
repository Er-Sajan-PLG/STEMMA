# GOVERNANCE (COMPREHENSIVE ALL-STEM, MEDIOCRE COVERAGE, HITL, EVOLVABLE, FRONTIER, EMBEDDINGS, RAG, CONSUMER EXPORT)

**Status:** Beginning clean, no legacy. 1 entity (metre) via PDF primary ingestion with HITL, deterministic scales, evolvable templates, model selector like DeepSeek harness (local + frontier models). Old 74 entities archived to archive/beginning-74-entities/. Workflow has 2 PDFs, 7 candidates, 3 HITL edits. Will grow via primary PDF ingestion.

## Invariants (Beginning, HITL, Evolvable, Frontier)

- No legacy data — this is beginning clean, 1 entity via HITL, old 74 archived, will grow via primary PDF ingestion
- PDF ingestion PRIMARY, direct LLM addition SECONDARY, both require HITL before canonical — no entity without human explicitly editing markdown file
- Every physics entity governed by law from physics-governing-registry.yaml, deterministic placement, no LLM reasoning for placement
- Every entity has standard scientific definition with exact SI (e.g., metre = light path 1/299,792,458 s, c=299,792,458 m/s exact, agreed per BIPM 2019) + reference triple verification (link bipm.org + source_refs + external_ids)
- Every entity dual verification: embedded provenance (writer human:*, link, retrieved_at, source_kind, source with exact) + canonical source record in sources/ with url/doi/isbn
- Every connection evidence mandatory with source_ref+locator+description
- No related_to, only 8 relations (mathematically_requires, derived_from, appears_in_law, applies_to, generalizes, special_case_of, part_of, approximates)
- History mandatory for law/model/equation when human_reviewed/canonical with timeline
- Deterministic scales: template-registry.yaml regex + exact SI constants c,h,ΔνCs,e,k,N_A,K_cd, no LLM, no cost, no hallucination, scales to 1000s PDFs, any domain
- Evolvable: add new domain (chemistry, biology, math) via `python3 scripts/evolvable_template.py --evolve --new-domain chemistry` without code change, templates in YAML
- LLM fallback only when PDF missing exact SI definition — then frontier model (DeepSeek R1/V3 free, Claude 3.5 Sonnet/Opus, GPT-4o/o1, Gemini 2.5 Pro/2.0 Flash free, Llama 3.3 70B free) or custom model via OpenRouter/NVIDIA NIM/OpenAI-compatible, selector like DeepSeek harness (search, categories Frontier/Reasoning/Free/Custom, 25 models, custom input), even LLM requires HITL human edit before canonical
- HITL enforcement: workflow/audit/audit.jsonl must contain candidate_edited by human:* after AI draft, writer must be human:*, markdown file explicit edit, hitl_check.py fails if bypassed, review_entity.py enforces human reviewer
- Markdown explicit: AI shows data in markdown preview (textarea + rendered + checklist), human explicitly edits markdown file for easy verification (plain text diffable)
- Deterministic, content-hash stamped, no wall clock, versioned exports v2.2.0, single source VERSION.yaml

## Scope

NOW: physics core measurement-units + mechanics beginning clean, 1 entity metre via HITL, 7 candidates (length,mass,time,second,kilogram,area) ready for human edit, governed by Newton + conservation + SI + dimensional-analysis, minimal v2 with HITL + evolvable templates + frontier selector, deterministic scales
LATER: other physics subdomains (electricity-magnetism, thermal-physics), then chemistry (general, organic, inorganic), biology, math — via evolvable template-registry.yaml without code change
OUT: all STEM at once without HITL, curriculum, grade, pedagogy, LLM placement without human edit, bypassing hitl_check

## Session protocol (HITL, Evolvable, Frontier)

1. Read INGESTION-PRIMARY.md (PDF primary + HITL) + AGENT.md (deterministic protocol with HITL + evolvable + frontier) + PHYSICS-GOVERNING-LAWS.md + physics-governing-registry.yaml + template-registry.yaml (evolvable)
2. Choose ingestion mode: deterministic (no LLM, scales, recommended) OR AI draft with frontier/custom model when PDF missing exact SI (choose model via Settings → Model Selection window like DeepSeek harness)
3. Upload PDF via webapp or `python3 scripts/pdf_ingest_primary.py --pdf path/to.pdf` or deterministic `python3 scripts/evolvable_template.py --pdf-extract workflow/extraction/*.txt`
4. Extract deterministic (poppler/tesseract) → markdown preview in workflow/candidates/<doc_id>/<slug>.md (deterministic templates regex + exact SI constants OR AI draft with frontier model)
5. HITL: Human explicitly edits markdown file in webapp textarea (fix definition with Exact:, governed_by, source_refs, writer human:*, link) → Save human edit → audit logs candidate_edited by human
6. Stage for human review → workflow/proposals/<slug>.md
7. Validate: validate.py + physics_core_profile_check.py + physics_governing_check.py + hitl_check.py + evolvable_template.py check + status_truth.py --write + verify_all.py — all must pass, no legacy
8. Review: review_entity.py accept <slug> --reviewer human:curator.001 → human_reviewed
9. Canonicalize: review_entity.py canonicalize <slug> --reviewer human:curator.001 → content/physics/<subdomain>/<slug>.md + connections with evidence
10. Commit with message explaining HITL + exact SI + frontier model if used

No legacy, this is beginning clean with HITL, deterministic scales, evolvable templates, model selector like DeepSeek harness (local + frontier models).


## Embeddings + RAG + Consumer Export Invariants (NEW 2026-09-21 — Comprehensive All-STEM Mediocre)

**Do we need embedding model? YES.** Embedding model generates vectors for entities for RAG and consumer export. Without embeddings, STEMMA is static JSON. With embeddings, LearningHub students can query "Newton's law" via vector similarity, PROFESSOR-J can answer offline.

- Embedding models: 11 models in schema/embedding-registry.yaml v1.0.0 — local free All-MiniLM 384 fast, MPNet 768 quality, BGE Large SOTA 1024 best for RAG, E5 Large 1024 retrieval, BGE Small 384 fast + frontier API OpenAI text-embedding-3-large 3072 best quality, text-embedding-3-small 1536 fast, Cohere embed-v3 1024, Gemini text-embedding-004 768 free tier, NVIDIA nv-embed-v1 SOTA 4096 free via NIM — model selector like DeepSeek harness (local + frontier models) with search, categories Frontier/Free/Local/SOTA, custom input
- Deterministic: same knowledge.json content_hash + model id → same embeddings, content_hash versioned, batch_size 32, normalize true, chunking entity strategy max_tokens 512 overlap 50, stored in exports/embeddings.jsonl + exports/vector_store/ FAISS meta.json + vectors.npy + ids.json, derived artifacts regenerable
- Consumer-specific: LearningHub prefers OpenAI text-embedding-3-large 3072 high quality, PROFESSOR-J prefers BGE Large SOTA 1024 offline, general prefers All-MiniLM fast local
- Generation: python3 scripts/embed.py --model BAAI/bge-large-en-v1.5 --output exports/embeddings.jsonl --vector-store exports/vector_store/

**Do we need RAG system in STEMMA? YES.** STEMMA is knowledge foundation, RAG is how consumers like LearningHub, PROFESSOR-J use it. Without RAG static JSON, with RAG queryable knowledge with citations.

- Components: ingestion PDF → deterministic extraction via template-registry v2.0.0 → entity markdown → embedding via embedding-registry → vector_store FAISS/Chroma/Qdrant local path exports/vector_store/ versioned with content_hash → retriever similarity search over entity definitions + connections → generator LLM model selector like DeepSeek harness (local + frontier models: DeepSeek R1 free 671B reasoning, Claude 3.5 Sonnet frontier, GPT-4o frontier multimodal, Gemini 2.5 Pro frontier, Llama 3.3 70B free, custom via OpenRouter/NVIDIA NIM) → answer with citations source_refs + link
- Flow: question → embedding via embedding model → vector search top_k cosine similarity → context with definitions + connections + sources → LLM prompt with context + question → answer with citations
- API: /v2/rag/search GET + /v2/rag/query POST via adapter server v0.2.0 and webapp server, webapp RAG playground with embedding model selector and LLM model selector like DeepSeek harness (local + frontier models)
- Consumer-specific: LearningHub top_k 5 GPT-4o, PROFESSOR-J top_k 10 DeepSeek R1 free fallback Claude 3.5 Sonnet/GPT-4o/Gemini 2.5 Pro

**Consumer export — YES needed.** Export mechanism via file (exports/knowledge.json deterministic content-hash v2.2.0, embeddings.jsonl, vector_store/ FAISS, consumers/<consumer>/knowledge.<consumer>.json filtered by domains/review_policy/entity_types), API (adapter server v0.2.0 with endpoints /v2/stats, /v2/entities?domain=..., /v2/connections, /v2/search?q=..., /v2/embeddings?model=..., /v2/rag/search?q=...&top_k=..., POST /v2/rag/query, /v2/export?consumer=..., /openapi.yaml OpenAPI 3.0.3), SDK (Python pip install ./adapters/python — Stemma.from_file + StemmaRAG), for LearningHub (canonical physics/chem/bio/math, OpenAI embeddings, GPT-4o RAG), PROFESSOR-J (reviewed all 8 domains mediocre, BGE Large offline SOTA, FAISS, DeepSeek R1 free RAG), general, explorer.

## Comprehensive All-STEM Domains (8 domains, 97 subdomains)

- physics: mechanics, measurement-units, electricity-magnetism, thermal-physics, waves-optics, atomic-nuclear, quantum, relativity, fluid-mechanics, thermodynamics, optics, condensed-matter (12)
- chemistry: general, organic, inorganic, physical, analytical, biochemistry, polymer, electrochemistry, quantum-chemistry, materials-chemistry, environmental-chemistry (11)
- biology: general, molecular, cell-biology, genetics, evolution, ecology, physiology, microbiology, neuroscience, anatomy, botany, zoology, immunology, developmental (14)
- earth-science: geology, meteorology, oceanography, environmental, geography, climatology, seismology, hydrology, atmospheric, mineralogy (10)
- astronomy: astrophysics, cosmology, planetary, stellar, galactic, observational, astrobiology, celestial-mechanics (8)
- computer-science: algorithms, data-structures, programming-languages, software-engineering, artificial-intelligence, machine-learning, databases, networks, cybersecurity, operating-systems, theory, computer-architecture, graphics, compilers, distributed-systems (15)
- engineering: mechanical, electrical, civil, chemical, aerospace, biomedical, industrial, environmental, materials, software, nuclear, automotive, robotics (13)
- mathematics: algebra, geometry, calculus, statistics, probability, number-theory, discrete, linear-algebra, differential-equations, topology, analysis, logic, combinatorics, optimization (14)

Total 97 subdomains, mediocre coverage means 50-100 entities per domain = 400-800 total, with deterministic templates v2.0.0 that scale, embeddings, RAG, consumer export.

## Comprehensive Template v2.0.0

- 12 entity types: concept, quantity, unit, constant, law, principle, theorem, equation, process, structure, algorithm, material
- Extraction rules: Length, Mass, Time, Area, Volume, Element, Mole, Cell, DNA, Photosynthesis, Algorithm, Sorting, Machine Learning, Derivative, Integral, Theorem, Earthquake, Black Hole, Stress, etc. — regex patterns, domain-specific, generic fallback
- Standard definition sources: SI Brochure 9th ed. (BIPM 2019) with constants c,h,ΔνCs,e,k,N_A,K_cd, NIST, IUPAC Gold Book, CRC Handbook, HRW 12th, Campbell Biology 12th, CLRS 4th, Atkins Physical Chemistry, Carroll Astrophysics
- LLM fallback: when PDF missing exact definition, prompt template with entity context, requires HITL
- Embedding config: 8 models with chunking entity strategy, vector_store FAISS, content_hash versioning


## Explicit Separation — Canonical vs Derived vs Consumer (NEW 2026-09-21 — Answers user's question)

**User question:** "Now about RAG system and embedding, STEMMA in itself doesn't need them!? But again STEMMA alone existence is useless if we can't use it, so building RAG pipeline is inevitable here!?"

**Answer: YES, exactly right — canonical never contains embeddings/RAG, derived + consumer inevitably needs them:**

### Canonical (STEMMA itself) — NO embeddings/RAG

- Paths: content/, connections/, sources/, schema/ (except registries that define models, not vectors)
- Contains only Markdown+YAML with exact definitions, dual verification, governed_by, history, 8 relations, evidence
- Does NOT contain embeddings, vectors, .npy, embeddings.jsonl, vector_store/, FAISS indexes — NEVER
- Why: embeddings are model-specific, non-deterministic (different models give different vectors), not time-invariant, would pollute canonical with floats, make content/ non-human-reviewable, violate "no embeddings, database as source of truth" for canonical
- Validation: validate.py NEVER checks embeddings, only canonical schema, identity, references, mandatory fields — deterministic, no LLM, no embeddings
- Previously "Not on roadmap: embeddings, database as source of truth" meant canonical, not derived — correct, canonical never has embeddings

### Derived (exports/) — YES embeddings here but as derived, regenerable, deterministic, content-hash

- Paths: exports/knowledge.json v2.2.0 content-hash, embeddings.jsonl, vector_store/ FAISS meta.json + vectors.npy + ids.json, consumers/<consumer>/knowledge.<consumer>.json, openapi.yaml, reports/
- Contains YES embeddings, vectors, FAISS, but as derived artifacts, not canonical, regenerable via embed.py
- Deterministic: same knowledge.json content_hash + model id → same embeddings, content_hash versioned, e.g., content_hash = sha256(text + model_id + knowledge.json content_hash)[:16], meta.json content_hash same as knowledge.json, created_at deterministic no wall clock
- Regenerable: delete exports/ → regenerate via validate.py + embed.py --model BAAI/bge-large-en-v1.5
- Validation: verify_all.py checks embeddings existence as INFO, not FAIL — prints OK if exists, INFO "run embed.py" if missing, doesn't fail gate. Gate decides canonical validity, not derived completeness.

### Consumer + RAG Pipeline (scripts/, adapters/, webapp/) — YES RAG here but as consumer mechanism, inevitable for usability

- Paths: scripts/embed.py (local free All-MiniLM/BGE Large + frontier OpenAI Large/NVIDIA NV-Embed, model selector like DeepSeek harness (local + frontier models)), scripts/rag.py (vector search + context + LLM generation with model selector like DeepSeek harness (local + frontier models) + citations), scripts/export_consumers.py, adapters/python/ v0.2.0 (SDK + CLI + API /v2/embeddings, /v2/rag/search, POST /v2/rag/query, /v2/export, /openapi.yaml), webapp/ (ingestion/review UI + RAG playground), schema/embedding-registry.yaml v1.0.0 11 models, consumer-registry.yaml v1.0.0 4 consumers, api.yaml OpenAPI 3.0.3
- Contains YES RAG pipeline, but as consumer mechanism, not canonical. Without RAG, STEMMA is static JSON, useless for student queries. With RAG, queryable knowledge with citations.
- Flow: question → embedding → vector search top_k → context definitions + connections + sources → LLM → answer with citations
- Why inevitable: STEMMA alone existence is useless if we can't use it, so building RAG pipeline is inevitable here — LearningHub needs to answer "What is Newton's second law?" with citations, PROFESSOR-J needs to answer "Explain photosynthesis" across 8 domains mediocre, offline SOTA BGE Large + FAISS + DeepSeek R1 free. Without RAG, consumers build own RAG from scratch, duplicating work, inconsistent. Therefore RAG inevitable, but as consumer layer, not canonical.
- Validation: rag.py checks are INFO in verify_all.py, not FAIL — RAG is consumer mechanism, optional for canonical validity, but recommended for usability

### Invariants for separation (NEW)

1. Canonical never contains embeddings, vectors, or RAG artifacts — no .npy, embeddings.jsonl, vector_store/ in content/, connections/, sources/, schema/ (except registries that define embedding models, not vectors)
2. Embeddings and vector stores live only in exports/ as derived artifacts — regenerable via embed.py, versioned via content_hash + model id, deterministic, no wall clock
3. RAG lives only in scripts/ and adapters/ and webapp/ as consumer mechanism — not in canonical, optional for canonical validity, but inevitable for usability
4. Gate validate.py never checks embeddings — only canonical
5. verify_all.py checks embeddings existence as INFO, not FAIL — prints OK if exists, INFO "run embed.py" if missing, doesn't fail gate
6. Previously "Not on roadmap: embeddings, database as source of truth" meant canonical, not derived — now embeddings ARE in derived + consumer layers, which IS on roadmap (R1 comprehensive all-STEM mediocre + embeddings + RAG + consumer export)

### Answers

- Does STEMMA itself need embeddings/RAG? NO — canonical valid without embeddings, without RAG, only Markdown+YAML
- Is STEMMA alone useless if we can't use it? YES — static JSON alone not queryable via natural language, no semantic search
- Is building RAG pipeline inevitable here? YES — as derived + consumer layer, inevitable for usability, but cleanly separated from canonical, optional for canonical validity, deterministic, versioned, with model selector like DeepSeek harness (local + frontier models)


## Can Embedding and RAG Be Out of STEMMA? YES — As Connection Layer, Not Containing Whole STEMMA (NEW 2026-09-21)

**User question:** "Can i actually have embedding and RAG out of STEMMA!? How do they connect then?? Embedding and RAG doesn't contain the whole STEMMA right!? its just a connection layer!?"

**Answer: YES, exactly right — embedding and RAG can be out of STEMMA, they're just connection layer, not containing whole STEMMA, they connect via exports/knowledge.json + API + SDK + content_hash.**

- **STEMMA itself (whole STEMMA):** content/<domain>/**/*.md (Markdown+YAML with exact definitions, dual verification, governed_by, history), connections/*.yaml (8 relations, evidence), sources/*.yaml (url/doi/isbn + writer human:*), schema/ — NO embeddings, NO vectors, NO RAG — pure knowledge foundation, whole STEMMA is here, e.g., metre defined as light path 1/299,792,458 s Exact c=299,792,458 m/s Agreed per BIPM 2019 + writer human:curator.001 + link + source_refs + wd
- **Embedding (connection layer, NOT whole STEMMA):** Does NOT contain whole STEMMA — contains vectors DERIVED from STEMMA definitions, e.g., metre chunk "Metre (stemma:phys.metre) Domain: physics/measurement-units Definition: The metre..." → embedding model All-MiniLM 384 dim or BGE Large 1024 SOTA or OpenAI Large 3072 → vector [0.12, -0.34, ...] 384/1024/3072 floats — semantic fingerprint for similarity search, stored in exports/embeddings.jsonl as {entity_id, model, dimensions, vector, content, content_hash} — regenerable from knowledge.json + model id, deterministic same content_hash + model → same vector — NOT whole STEMMA, just derived vectors
- **Vector store (connection layer, NOT whole STEMMA):** Does NOT contain whole STEMMA — contains FAISS index of vectors + ids.json + meta.json with model, dimensions, content_hash, entity_count — e.g., vectors.npy shape (1, 384), ids.json ["stemma:phys.metre"] — just index for fast cosine similarity, NOT whole STEMMA, just connection layer for retrieval
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


