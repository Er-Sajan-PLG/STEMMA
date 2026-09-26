# API — How consumers get STEMMA data

**Status:** reconciled with the code on 2026-09-26 per
[ADR-0054](decisions/0054-consumer-access-surface.md). Where this page and the
code disagree, the code plus `schema/api.yaml` (v2.3.0) win. `schema/api.yaml`
is kept in sync with the adapter by `tests/repo/test_api_spec_matches_server.py`.

## The three access paths (in order of preference)

| Path | What it is | Status |
|---|---|---|
| **File** | `exports/knowledge.json` (+ `knowledge.*.json` review views, `knowledge.jsonld`), versioned by `content_hash` | **Primary contract.** Published read-only at <https://er-sajan-plg.github.io/STEMMA/exports/knowledge.json> |
| **SDK** | Python `stemma_adapter` (`adapters/python/`) — loads + validates an export fail-closed, graph queries, ADR-0045 valued claims | Supported |
| **HTTP `/v2/*`** | The same SDK served read-only over one export, run locally by the consumer | Optional convenience; no auth, no rate limiting, no hosted endpoint |

The webapp (`webapp/server.py`, `/api/*`) is the owner's **private curation
tool**, not a consumer API (see [WEBAPP.md](WEBAPP.md)).

## HTTP `/v2/*` — adapter server

```bash
PYTHONPATH=adapters/python python3 -m stemma_adapter serve exports/knowledge.json --port 8080   # binds 127.0.0.1
curl http://127.0.0.1:8080/v2/stats
```

Stable paths (read-only, JSON):

- /v2/stats — counts, content_hash, versions
- /v2/entities?domain=...&type=...&status=...&limit=... — list entities
- /v2/entities/{id} — one entity, e.g. `stemma:phys.metre`
- /v2/resolve/{id} — follow alias / deprecation chains → `{resolved, chain}`
- /v2/external/{scheme}/{value} — look up by external id, e.g. `/v2/external/wd/Q14038`
- /v2/connections?source=...&target=...&relation=...&policy=... — list connections
- /v2/search?q=...&domain=...&limit=... — token search
- /v2/neighbors/{id}, /v2/prerequisites/{id}?policy=... — graph queries (entity→entity edges only)
- /v2/values/{id}?relation=&policy=... — valued claims (ADR-0045 value-slot: `{amount, lowerBound, upperBound, unit}`), e.g. the metre's defining speed of light
- /v2/relations, /v2/relations/{name}, /v2/vocabularies — registries
- /openapi.yaml (alias /v2/openapi.yaml) — the OpenAPI document

Experimental paths (`x-stability: experimental` — reference/demo only; unless
`sentence-transformers` is installed they use deterministic **placeholder**
vectors, so similarity results are not meaningful):

- /v2/embeddings?model=...&id=...&domain=...&limit=...
- /v2/rag/search?q=...&top_k=...&model=...&domain=...
- POST /v2/rag/query — body `{question, top_k, model, embedding_model, domain, consumer}`
- /v2/export?consumer=...&format=...&review_policy=...

Not implemented (planned, needs a future ADR): authentication, API keys,
per-consumer rate limits, a hosted production endpoint.

## Webapp `/api/*` — private admin tool (not a consumer API)

Curation workflow (documents, semantic extraction/verification, proposals,
LLM provider config) plus a RAG playground on the same experimental
embeddings. Bound to `127.0.0.1`, no CORS, Host/Origin-checked; routes may
change without notice. See [WEBAPP.md](WEBAPP.md).

## File-based exports

- `exports/knowledge.json` — main deterministic export (content_hash)
- `exports/knowledge.{all,reviewed,canonical,trusted,proposed,rejected}.json` — review-aware views
- `exports/knowledge.jsonld` — derived semantic-web projection (ADR-0053)
- `exports/embeddings.jsonl`, `exports/vector_store/` — **not committed or published** (derived, model-specific; a consumer concern). Generate locally with `scripts/embed.py` — it refuses to write vectors without a real model; `--placeholder` writes hash vectors labelled `stemma:placeholder-hash` for pipeline tests only
- `exports/consumers/<consumer>/knowledge.<consumer>.json` — one bundle per consumer in `schema/consumer-registry.yaml` (general, learninghub, professor-j, stemma-explorer). Each is a valid export (loads with `stemma_adapter`), narrowed by domain/subdomain/type and a trust tier applied to **both** entity status and connection review (`canonical` ⊂ `trusted` ⊆ `reviewed` ⊂ `all`; `trusted` also requires LLM-asserted connections to be canonical). Deterministic; CI fails if stale (`export_consumers.py --all --check`)

Generated via `python3 scripts/validate.py` (knowledge.json + views) and the
optional `scripts/embed.py` / `scripts/export_consumers.py`.

## Releases — the published file contract

Consumers (internal products and third parties alike) pull the **same** bundle
from GitHub Releases — never from the repo. `.github/workflows/release.yml`
publishes one per tag `vX.Y.Z` / `vX.Y.Z-rcN` (`X.Y.Z` = `./VERSION`, which is
independent of `export_version`).

| Asset | Kind (`manifest.files[*].kind`) |
|---|---|
| `knowledge.json` | `export` — everything, all statuses |
| `knowledge.<consumer>.json` | `export` — pre-filtered per `schema/consumer-registry.yaml` |
| `knowledge.hash.json` | `hash-pointer` — sha256 + `content_hash` of `knowledge.json` (cheap "did it change?") |
| `connections.canonical.json` | `connections-view` — canonical connections only, **not** a full export (named `knowledge.canonical.json` in `v3.0.0-rc1`) |
| `knowledge.jsonld`, `stemma-shapes.ttl` | JSON-LD projection, SHACL shapes |
| `manifest.json`, `SHA256SUMS.txt`, `stemma-<tag>.tar.gz` | versions, `content_hash`, per-file sha256/counts, `license: CC-BY-4.0`, `generated_at` (commit time) |

Never included: embeddings / vector stores (ADR-0054) — the builder refuses them.

**Verify before use:**

```bash
sha256sum -c SHA256SUMS.txt
gh attestation verify knowledge.learninghub.json --repo Er-Sajan-PLG/STEMMA   # Sigstore build provenance
python -m stemma_adapter validate knowledge.learninghub.json
```

Without `gh` ≥ 2.49 (no `attestation` command), verify the same Sigstore
attestation with [`sigstore-python`](https://pypi.org/project/sigstore/):

```bash
d=$(sha256sum knowledge.learninghub.json | cut -d' ' -f1)
gh api repos/Er-Sajan-PLG/STEMMA/attestations/sha256:$d --jq '.attestations[0].bundle' > att.json
sigstore verify github knowledge.learninghub.json --bundle att.json \
  --repository Er-Sajan-PLG/STEMMA --ref refs/tags/<tag> --trigger push
```

Builds are reproducible: rebuilding a tag with
`SOURCE_DATE_EPOCH=$(git log -1 --format=%ct) python3 scripts/build_release_bundle.py --release-tag <tag>`
yields byte-identical assets.

**Status:** until the owner records `docs/decisions/r6-identifier-base.md`
(Amendment 0001), only pre-releases (`-rcN`) publish, marked
`PENDING-PUBLICATION`; a final tag fails at `scripts/publication_gate.py`.

**Owner signature (manual, second layer).** `-rcN` tags are **CI-attested
only** (Sigstore) and carry no owner signature. A **final** tag is never
published by CI: `release.yml` creates it as a **draft** (invisible to
consumers), and it stays unpublished until the owner has signed
`SHA256SUMS.txt` locally and attached `SHA256SUMS.sig`. The GPG key must never
be stored in GitHub Actions secrets or used by any workflow.

```bash
TAG=vX.Y.Z
gh release download "$TAG" -D "sign-$TAG" -p SHA256SUMS.txt -p manifest.json
# optional, independent: rebuild from the tag (reproducible) and diff SHA256SUMS.txt
python3 scripts/sign_release_bundle.py "sign-$TAG" --key <owner-key>
python3 scripts/sign_release_bundle.py "sign-$TAG" --verify-only
gh release upload "$TAG" "sign-$TAG/SHA256SUMS.sig"      # upload ONLY the .sig
gh release edit "$TAG" --draft=false --latest             # publish
```

The signer also annotates the *local* `manifest.json`; never re-upload it (the
published manifest is the attested one). Consumers verify with
`gpg --verify SHA256SUMS.sig SHA256SUMS.txt` against the owner's published key.
`release/` is local staging only (git-ignored); bundles are not committed.

## SDK

- **Python:** adapters/python/ pip install ./adapters/python
  ```python
  from stemma_adapter import Stemma
  stemma = Stemma.from_file("exports/knowledge.json")   # validates, fails closed
  print(stemma.stats)
  print(stemma.search("force", domain="physics"))
  print(stemma.neighbors("stemma:phys.force"))           # entity -> entity edges
  print(stemma.values("stemma:phys.metre"))              # ADR-0045 valued claims
  # CLI equivalents: python -m stemma_adapter {stats,search,neighbors,values,...} exports/knowledge.json

  # Experimental RAG via scripts/rag.py (placeholder vectors unless sentence-transformers is installed)
  import sys
  sys.path.insert(0, "scripts")
  import rag
  results = rag.vector_search("Newton second law", top_k=5)
  answer = rag.rag_query("What is Newton second law?", top_k=5, model="deepseek/deepseek-r1:free", consumer="learninghub")
  ```

- **Future TypeScript:** adapters/typescript/

## Consumer-specific API access

Defined in `schema/consumer-registry.yaml` v1.0.0. **Planned, not enforced:**
the adapter has no auth or rate limiting today (ADR-0054); these entries
describe intended consumer profiles.

- **LearningHub:** endpoints /v2/stats, /v2/entities, /v2/search, /v2/rag/query, /v2/embeddings — rate limit 1000/hour api_key — example query "What is Newton's second law?"
- **PROFESSOR-J:** endpoints /v2/stats, /v2/entities, /v2/connections, /v2/search, /v2/neighbors, /v2/prerequisites, /v2/rag/query, /v2/rag/search, /v2/embeddings, /v2/export — rate limit 10000/hour api_key — example "Explain photosynthesis and its relation to cellular respiration"
- **General:** /v2/stats, /v2/entities, /v2/search — 100/hour none
- **Explorer:** no API (reads file)

## Why API needed for LearningHub, PROFESSOR-J?

- **File-based alone insufficient:** LearningHub is web platform, needs REST API to query STEMMA without file access, with filtering by domain, embeddings, RAG, consumer-specific exports, auth, rate limiting, OpenAPI schema for client generation
- **PROFESSOR-J:** AI professor needs API for RAG queries, embeddings, vector search, with offline option (local file + FAISS) + online API (OpenRouter frontier models)
- **OpenAPI schema:** Provides machine-readable API contract for client generation, documentation, testing — e.g., LearningHub can generate TypeScript client from openapi.yaml, PROFESSOR-J can generate Python client

## Related docs

- `schema/api.yaml` — OpenAPI schema
- `schema/consumer-registry.yaml` — consumer API access
- `schema/embedding-registry.yaml` — embedding models for /v2/embeddings
- `adapters/python/stemma_adapter/server.py` v0.2.0 — adapter server with embeddings + RAG + export + OpenAPI
- `webapp/server.py` — webapp server with RAG playground
- `scripts/embed.py` — generates embeddings for API
- `scripts/rag.py` — RAG system for API
- `scripts/export_consumers.py` — consumer-specific exports for API
- `docs/CONSUMERS.md` — consumer definitions
- `docs/EMBEDDINGS.md` — embeddings
- `docs/RAG.md` — RAG


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


