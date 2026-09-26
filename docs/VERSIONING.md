# VERSIONING (COMPREHENSIVE ALL-STEM, MEDIOCRE COVERAGE, HITL, EVOLVABLE, FRONTIER, EMBEDDINGS, RAG, CONSUMER EXPORT)

**Status:** Authoritative, comprehensive all-STEM mediocre, 8 domains, embeddings, RAG, consumer export.

## Consumer versioning and release policy (ADR-0054 Amendment 1)

Status of each rule: **D** = already decided by the owner (recorded here),
**P** = proposed, awaiting the owner's decision. Nothing marked **P** is
binding until the amendment in ADR-0054 is marked Decided.

### 1. Independent version numbers (D)

| Number | Lives in | Identifies | Changes when |
|---|---|---|---|
| **Release version** | `./VERSION`; git tag `vX.Y.Z[-rcN]`; export `kernel_version`; manifest `release_tag` | one published bundle — what consumers pin | a new final release (rules: §2) |
| **`export_version`** | `schema/VERSION.yaml`; every export file | the file format consumers parse | only when the format changes (§3) — never for content alone |
| **`schema_version`** | `schema/VERSION.yaml`; export `schema_version` | the authoring schemas under `schema/` | when concept/connection/source schemas change; producer-side, informational for consumers |
| **`content_hash`** | every export file; `manifest.json` | the canonical knowledge | automatically, whenever canonical sources change (§4) |
| `relation_registry_version` | `schema/VERSION.yaml`; export | the relation vocabulary shipped inside the export | when `schema/relation-registry.yaml` changes |
| adapter version | `adapters/python/pyproject.toml` (+ `__version__`) | the `stemma-adapter` package | its own SemVer; `adapters/python/CHANGELOG.md` |

They move independently. `export_version` stays on 2.x and is **not** aligned
with the release version 3.x. Tags must match `./VERSION` (`release.yml`).

### 2. Release version rules (P)

SemVer, judged from a consumer's point of view:

- **MAJOR** — an `export_version` major bump; removal or rename of a
  `kind: export` release asset; anything listed as breaking in §3.
- **MINOR** — an `export_version` minor bump; new content (entities,
  connections, sources) or status promotions; a new consumer export or other
  new asset.
- **PATCH** — corrections to existing content (definitions, values,
  provenance, citations) with all IDs unchanged.

Release candidates (`-rcN`) iterate on one version; each new final release
needs a new `VERSION` because tags are immutable (§7).

### 3. Breaking vs additive for the export file contract (facts; one P rule)

Additive → `export_version` **MINOR**; readers of the same major keep working:

- a new optional member on entities, connections, sources, provenance or
  evidence (open objects in `schema/export.schema.json`);
- a new optional top-level member (declared in `export.schema.json`, which is
  closed at the top level; the SDK ignores unknown top-level members);
- a new relation, provided it is in the export's embedded `relation_registry`
  (the SDK refuses only relations missing from that registry);
- a new value for an enumerated field such as `status`, `authority`, `warrant`
  or `correction_class` (the SDK does not restrict them). **(P)** Consumers
  must treat unknown values as "unknown — not canonical", never as an error.

Breaking → `export_version` **MAJOR** (the SDK refuses an unknown major —
`SUPPORTED_EXPORT_MAJOR`):

- removing or renaming a member, or changing its type, units or meaning;
- **any new member in the value slot** (`connections[].value`): it is closed
  in both `export.schema.json` and the SDK, so existing readers would reject it;
- removing an entity or connection ID, or changing what it denotes (IDs are
  immutable; retire them — §5).

Content changes are never format changes: they move `content_hash` and the
release version, not `export_version`.

### 4. `content_hash` (facts)

- `sha256` over the relative path and bytes of every file under `content/`,
  `connections/` and `sources/` (`scripts/validate.py`). Subset and consumer
  exports carry the same base `content_hash`.
- It changes **iff** those bytes change — including whitespace-only edits. It
  does **not** change for version bumps, schema or registry edits, or tooling.
- Same `content_hash` does not mean same file bytes: a new `export_version` or
  `kernel_version` over unchanged content produces a different file. To detect
  *any* change, compare the file's sha256 (`manifest.files`, `SHA256SUMS.txt`,
  `knowledge.hash.json`). Use `content_hash` to answer only "did the knowledge
  change?". Cache on `(export_version, content_hash)` or on the file sha256 —
  never on `content_hash` alone.

### 5. Deprecation (P)

- **IDs** are never deleted or reused. Retire an entity with
  `status: deprecated` plus `deprecated_by` (the SDK validates the target), and
  a connection with `lifecycle.replaced_by`.
- **Contract members and release assets**: announce in `docs/MIGRATIONS.md` and
  the release notes; keep them for at least one final MINOR release **and** 90
  days; remove only in the next MAJOR.
- **Old majors** are not published side by side. Earlier final releases stay
  downloadable (tags are immutable), and consumers pin a major through the SDK.

### 6. Where changes are recorded (P — formalises current practice)

| What | Where |
|---|---|
| every `export_version`, `schema_version` or `relation_registry_version` change, and every release-asset change, with the consumer action | `docs/MIGRATIONS.md` |
| one line per version with its ADR | comments in `schema/VERSION.yaml` |
| adapter package versions | `adapters/python/CHANGELOG.md` |
| per-release summary | GitHub Release notes (written by `release.yml`) |

`tests/repo/test_versioning_policy.py` fails if the current export, schema,
registry or adapter version has no entry here. **(P)** No root `CHANGELOG.md`:
retire release-please (`.github/workflows/release-please.yml` and its config
are still present, fail on every push to `main`, and would create a changelog
that duplicates the ones above).

### 7. Tags, release candidates and promotion

- **Tags are immutable (D)**: never moved, deleted or re-pushed. A mistake is
  fixed with a new `-rcN` or a new version. Protect `v*` tags with a
  repository tag ruleset (owner setting).
- **`vX.Y.Z-rcN` (D)**: CI publishes a GitHub pre-release with the Sigstore
  build attestation only; manifest status `PENDING-PUBLICATION`.
- **`vX.Y.Z` (D)**: requires `scripts/publication_gate.py` (the identifier-base
  decision in `docs/decisions/r6-identifier-base.md`). CI creates it as a
  **draft**; the owner signs `SHA256SUMS.txt` locally, uploads only
  `SHA256SUMS.sig`, verifies it, then publishes. The GPG key never goes into
  GitHub Actions. Commands: `docs/API.md` → "Owner signature".
- **Promotion (P)**: a final tag must point at exactly the commit of the last
  `-rcN` of that version that passed `release.yml`; any change means a new rc.
  The export files are then byte-identical to that rc (only the manifest's
  `release_tag` and status differ). Enforcing this in `release.yml` is a
  proposed follow-up, not implemented yet.

## Versions — single source VERSION.yaml (ADR-0022; ADR-0027/0028 refoundation)

- **schema_version:** 1.3.0 — v1.3.0 ADDITIVE optional provenance.drafted_by (machine origin of a human-written entity; H1); earlier: canonical JSON Schemas, concept, connection, source, v1.0.0 namespace stemma: replaces retired prefix, deprecated entity-side relationships[] removed
- **export_version:** 2.2.0 — exports/knowledge.json consumer contract, v2.0.0 entities[].relationships removed, graph is connections[] only, all IDs stemma:-namespaced, v2.1.0 ADDITIVE optional relation_registry + relation_registry_version + vocabularies sidecar so consumers can introspect relation semantics from export alone, old 2.0.x readers ignore new members, v2.2.0 ADDITIVE value-slot XOR target/value per ADR-0045 + authority internal|delegated per ADR-0049 + warrant axis definitional axiomatic model_based + correction_class per ADR-0046 (ADR-0050 contract update 2.2.0)
- **relation_registry_version:** 1.0.0 — schema/relation-registry.yaml, 8 relations only (mathematically_requires, derived_from, appears_in_law, applies_to, generalizes, special_case_of, part_of, approximates), no related_to in physics, reserved duplicates removed (broader_than/narrower_than duplicated generalizes/special_case_of, contains duplicated has_part, is_a duplicated special_case_of)
- **template-registry_version:** 2.0.0 — NEW comprehensive all-STEM, 8 domains physics/chemistry/biology/earth-science/astronomy/computer-science/engineering/mathematics, 97 subdomains, 12 entity types concept/quantity/unit/constant/law/principle/theorem/equation/process/structure/algorithm/material, extraction_rules regex for all domains, standard_definition_sources SI Brochure/NIST/IUPAC/CRC/HRW/Campbell/CLRS/Atkins/Carroll, llm_fallback prompt, embedding config with 8 models, evolvable without code change via --evolve
- **embedding-registry_version:** 1.0.0 — NEW embeddings for RAG and consumer export, 11 models local free All-MiniLM 384 fast 80MB 5x faster, MPNet 768 quality 420MB, BGE Large SOTA 1024 1.3GB best for RAG MTEB top, E5 Large 1024 retrieval, BGE Small 384 fast 133MB + frontier API OpenAI text-embedding-3-large 3072 best quality MTEB 64.6 $0.00013/1k, text-embedding-3-small 1536 fast $0.00002/1k, Ada 002 legacy, Cohere embed-v3 1024, Gemini text-embedding-004 768 free tier, NVIDIA nv-embed-v1 SOTA 4096 free via NIM MTEB top, default All-MiniLM fast local fallback BGE Small, deterministic content_hash + model id → same embeddings, chunking entity strategy max_tokens 512 overlap 50, vector_store FAISS flat cosine path exports/vector_store/ meta.json + vectors.npy + ids.json, batch_size 32 normalize true, consumer-specific LearningHub OpenAI Large 3072, PROFESSOR-J BGE Large SOTA 1024 offline, general All-MiniLM
- **consumer-registry_version:** 1.0.0 — NEW consumer export for LearningHub, PROFESSOR-J, general, explorer, each with domains, review_policy, entity_types, export_formats, embedding_model, api_access endpoints rate_limit auth api_key, rag config top_k model fallback_models, export_mechanisms file (knowledge.json deterministic content-hash, embeddings.jsonl, vector_store/ FAISS, consumers/<consumer>/knowledge.<consumer>.json filtered, openapi.yaml) + api (adapter v0.2.0 endpoints /v2/stats /v2/entities /v2/connections /v2/search /v2/embeddings /v2/rag/search /v2/rag/query POST /v2/export /openapi.yaml OpenAPI 3.0.3) + sdk (Python pip install ./adapters/python Stemma.from_file + StemmaRAG, future TypeScript), RAG flow question → embedding → vector search top_k → context definitions + connections + sources → LLM frontier selector → answer with citations
- **api_version:** 2.2.0 — NEW OpenAPI 3.0.3 schema in schema/api.yaml, endpoints /v2/stats, /v2/entities?domain=..., /v2/connections, /v2/search?q=..., /v2/embeddings?model=..., /v2/rag/search?q=...&top_k=..., POST /v2/rag/query, /v2/export?consumer=..., /openapi.yaml, for LearningHub, PROFESSOR-J, general, explorer, auth none local + api_key for LearningHub/PROFESSOR-J + bearer for frontier models via OpenRouter
- **governing_registry_version:** 1.0.0 — schema/physics-governing-registry.yaml, 23 laws, deterministic placement
- **kernel_version:** 3.0.0 — architecture baseline ADR-0029

## Deterministic, content-hash, no wall clock — now also for embeddings and vector store

- **exports/knowledge.json:** deterministic `content_hash` (no wall clock), `export_version` 2.2.0; current values are in the file itself and in each release `manifest.json` (see §4 above)
- **exports/embeddings.jsonl:** content_hash per embedding = sha256(text + model_id + knowledge.json content_hash)[:16], deterministic same content + model → same embeddings, versioned via knowledge.json content_hash + model id, 1 embeddings now
- **exports/vector_store/:** meta.json with model, dimensions, content_hash, entity_count, created_at deterministic no wall clock, version 1.0.0, type faiss, index_type flat, metric cosine, vectors.npy + ids.json, versioned via content_hash + model id, deterministic
- **exports/consumers/<consumer>/knowledge.<consumer>.json:** filtered by consumer domains/review_policy/entity_types, content_hash same as main export, deterministic, versioned

## Version literals forbidden — must read from VERSION.yaml

Every producer of derived artifacts (scripts/validate.py, export_review_aware.py, graph_analysis.py, embed.py, rag.py, export_consumers.py) MUST read version constants from schema/VERSION.yaml. Version literals in scripts forbidden.

## Scaling + Frontier + Embeddings + RAG + Consumer Export

- Deterministic scales: template-registry.yaml v2.0.0 regex + exact SI constants + authoritative sources for all 8 domains, scales to 1000s PDFs, any domain, no cost
- Evolvable: add new domain without code change via --evolve, template-registry v2.0.0
- LLM only when PDF missing exact definition: frontier DeepSeek R1/V3 free, Claude 3.5 Sonnet/Opus, GPT-4o/o1, Gemini 2.5 Pro/2.0 Flash free, Llama 3.3 70B free via OpenRouter/NVIDIA NIM, selector like DeepSeek harness
- Even LLM requires HITL: human explicitly edits markdown before canonical
- Embeddings — YES needed: For RAG and consumer export, embedding model generates vectors, deterministic same content_hash + model → same embeddings, local free All-MiniLM 384 fast + BGE Large SOTA 1024 best for RAG + frontier API OpenAI Large 3072 best quality + NVIDIA NV-Embed SOTA 4096 free via NIM, model selector like DeepSeek harness (local + frontier models), stored in embeddings.jsonl + vector_store/ FAISS
- RAG — YES needed: STEMMA is knowledge foundation, RAG is how consumers use it, without RAG static JSON, with RAG queryable knowledge with citations, flow question → embedding → vector search top_k → context definitions + connections + sources → LLM frontier selector → answer with citations, API /v2/rag/search GET + /v2/rag/query POST, webapp RAG playground
- Consumer export — YES needed: file (knowledge.json deterministic content-hash v2.2.0, embeddings.jsonl, vector_store/ FAISS, consumers/<consumer>/knowledge.<consumer>.json filtered), API (adapter v0.2.0 endpoints /v2/entities, /v2/embeddings, /v2/rag/search, /v2/rag/query POST, /v2/export?consumer=..., /openapi.yaml OpenAPI 3.0.3), SDK (Python Stemma.from_file + StemmaRAG), for LearningHub, PROFESSOR-J, general, explorer


## Explicit Separation — Canonical vs Derived vs Consumer (NEW 2026-09-21)

**Does STEMMA itself need embeddings/RAG? NO — canonical layer NO embeddings/RAG, only Markdown+YAML, versioned via schema_version 1.3.0, export_version 2.2.0, relation_registry_version 1.0.0, template-registry_version 2.0.0, governing_registry_version 1.0.0, kernel_version 3.0.0, single source VERSION.yaml, no literals, no wall clock. Is STEMMA alone useless if we can't use it? YES — static JSON alone not queryable. Is building RAG pipeline inevitable? YES — as derived + consumer layer, inevitable for usability.**

- **Canonical versioning:** schema_version 1.3.0, export_version 2.2.0, relation_registry_version 1.0.0, template-registry_version 2.0.0, governing_registry_version 1.0.0, kernel_version 3.0.0 — single source VERSION.yaml — canonical content/ + connections/ + sources/ + schema/ — NO embeddings, NO RAG — versioned, deterministic, content-hash, no wall clock
- **Derived versioning:** exports/knowledge.json content_hash sha256:2c007... deterministic no wall clock v2.2.0, embeddings.jsonl content_hash per embedding = sha256(text + model_id + knowledge.json content_hash)[:16] deterministic same content + model → same embeddings versioned via knowledge.json content_hash + model id, vector_store/ meta.json with model, dimensions, content_hash, entity_count, created_at deterministic no wall clock version 1.0.0 type faiss index_type flat metric cosine, consumers/<consumer>/knowledge.<consumer>.json filtered content_hash same as main deterministic versioned — YES embeddings here but as derived, regenerable, deterministic, versioned
- **Consumer + RAG versioning:** embedding-registry_version 1.0.0 11 models, consumer-registry_version 1.0.0 4 consumers, api_version 2.2.0 OpenAPI 3.0.3 — model selector like DeepSeek harness (local + frontier models) — RAG versioned via content_hash + model_used + embedding_model_used deterministic same question + same knowledge + same models → same retrieved + same context (LLM generation may be non-deterministic unless temperature 0) — YES RAG here but as consumer mechanism, inevitable for usability, optional for canonical validity

**Invariants:**
1. Canonical never contains embeddings, vectors, RAG artifacts
2. Embeddings live only in exports/ as derived, regenerable via embed.py, versioned via content_hash + model id, deterministic
3. RAG lives only in scripts/adapters/webapp as consumer mechanism, optional for canonical validity, inevitable for usability
4. Gate validate.py never checks embeddings, only canonical versioning
5. verify_all.py checks embeddings existence as INFO not FAIL
6. Previously "Not on roadmap: embeddings, database as source of truth" meant canonical, not derived — now embeddings ARE in derived + consumer which IS on roadmap


## Can Embedding and RAG Be Out of STEMMA? YES — As Connection Layer, Not Containing Whole STEMMA

**User question:** "Can i actually have embedding and RAG out of STEMMA!? How do they connect then?? Embedding and RAG doesn't contain the whole STEMMA right!? its just a connection layer!?"

**Answer: YES — embedding and RAG can be out of STEMMA, they're just connection layer, not containing whole STEMMA, they connect via exports/knowledge.json + API + SDK + content_hash.**

- Whole STEMMA: content/, connections/, sources/, schema/ — NO embeddings, NO RAG — pure knowledge
- Embedding: NOT whole STEMMA — vectors DERIVED from definitions, e.g., metre chunk → All-MiniLM 384 dim or BGE Large 1024 SOTA or OpenAI Large 3072 → vector [0.12, -0.34, ...] — semantic fingerprint for similarity search, stored in exports/embeddings.jsonl as {entity_id, model, dimensions, vector, content, content_hash} — regenerable, deterministic, NOT whole STEMMA
- Vector store: NOT whole STEMMA — FAISS index of vectors + ids.json + meta.json — just index for fast cosine similarity, NOT whole STEMMA, just connection layer
- RAG: NOT whole STEMMA — retrieval logic (embedding query → cosine similarity → top_k) + generation logic (context definitions + connections + sources → LLM → answer with citations) — grounded in STEMMA but doesn't contain whole STEMMA, only references entity IDs as context

**How connect? 3 ways:**
1. File-based: STEMMA exports knowledge.json v2.2.0 content-hash — external RAG copies file, runs own embed.py externally, connection via content_hash, does NOT contain whole STEMMA
2. API-based: STEMMA API /v2/entities, /v2/stats content_hash, /v2/search, /v2/embeddings, /v2/rag/search, POST /v2/rag/query, /v2/export, /openapi.yaml — external RAG calls API to get entities, generates embeddings externally, builds FAISS externally, serves RAG with citations — connection via API + content_hash, does NOT contain whole STEMMA
3. SDK-based: STEMMA SDK adapters/python/ Stemma.from_file("exports/knowledge.json") — external RAG uses SDK to load STEMMA, builds own embeddings/RAG out of STEMMA — connection via SDK + content_hash, does NOT contain whole STEMMA

**Current:** Optional derived layer inside STEMMA for convenience — scripts/embed.py, rag.py, export_consumers.py, exports/embeddings.jsonl, vector_store/, adapters/python/ v0.2.0, webapp RAG playground — inside but as derived + consumer, not canonical, INFO not FAIL in verify_all.py — convenient for demo

**Can be out:** YES, move to separate repo STEMMA-RAG or to LearningHub/PROFESSOR-J, keep STEMMA core pure with only content/, connections/, sources/, schema/, validate.py — STEMMA exports knowledge.json + API schema, external RAG consumes via file/API/SDK + content_hash — cleaner separation, STEMMA remains pure knowledge foundation, embedding/RAG are external consumers, connection layer, not containing whole STEMMA

**Recommendation:** Keep canonical pure (NO embeddings/RAG, validate.py NEVER checks), keep derived optional inside for convenience (exports/knowledge.json, embeddings.jsonl, vector_store/, INFO not FAIL), but for production LearningHub, PROFESSOR-J have embedding and RAG out of STEMMA as separate service that consumes STEMMA via file/API/SDK + content_hash, generates embeddings externally, builds vector store externally, serves RAG with citations — embedding/RAG doesn't contain whole STEMMA, just connection layer, whole STEMMA remains in STEMMA repo


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


