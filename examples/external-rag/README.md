# External RAG — Out of STEMMA — Connection Layer, Not Containing Whole STEMMA

This example shows how embedding and RAG can be **out of STEMMA**, as connection layer, not containing whole STEMMA, connecting via exports/knowledge.json + API + SDK + content_hash.

**User question:** "Can i actually have embedding and RAG out of STEMMA!? How do they connect then?? Embedding and RAG doesn't contain the whole STEMMA right!? its just a connection layer!?"

**Answer: YES — exactly right.**

## STEMMA itself (whole STEMMA) — NO embeddings/RAG

- STEMMA canonical: `content/`, `connections/`, `sources/`, `schema/` — Markdown+YAML with exact definitions, dual verification, governed_by, history, 8 relations, evidence — NO embeddings, NO vectors, NO RAG — pure knowledge foundation
- Whole STEMMA is here: e.g., metre defined as light path 1/299,792,458 s Exact c=299,792,458 m/s Agreed per BIPM 2019 + writer human:curator.001 + link + source_refs + wd

## Embedding and RAG out of STEMMA — connection layer, NOT whole STEMMA

- **Embedding:** Does NOT contain whole STEMMA — contains vectors DERIVED from STEMMA definitions, e.g., metre chunk → All-MiniLM 384 dim → vector [0.12, -0.34, ...] — semantic fingerprint for similarity search, stored in embeddings.jsonl as {entity_id, model, dimensions, vector, content, content_hash} — regenerable, deterministic, NOT whole STEMMA
- **Vector store:** Does NOT contain whole STEMMA — FAISS index of vectors + ids.json + meta.json — just index for fast cosine similarity, NOT whole STEMMA, just connection layer
- **RAG:** Does NOT contain whole STEMMA — retrieval logic + generation logic — grounded in STEMMA but doesn't contain whole STEMMA, only references entity IDs as context, whole STEMMA remains in STEMMA repo

## How connect? 3 ways — file, API, SDK — via content_hash

### Option A: File-based — simplest, deterministic

```bash
# STEMMA exports knowledge.json
# In this external RAG (out of STEMMA):
cp ../exports/knowledge.json ./data/knowledge.json
python3 embed.py --input ./data/knowledge.json --model BAAI/bge-large-en-v1.5 --output ./data/embeddings.jsonl --vector-store ./data/vector_store/
python3 rag.py --question "What is Newton's second law?" --top-k 5 --model deepseek/deepseek-r1:free --vector-store ./data/vector_store/
```

Connection via content_hash: if knowledge.json content_hash changed (new entities via HITL), recompute embeddings — deterministic same content_hash + model → same embeddings — does NOT contain whole STEMMA, only vectors + index + retrieval logic

### Option B: API-based — for LearningHub, PROFESSOR-J production

```python
import requests
# Get entities from STEMMA API (out of STEMMA)
resp = requests.get("http://stemma-api:8080/v2/entities?domain=physics&status=canonical&limit=1000")
entities = resp.json()
content_hash = requests.get("http://stemma-api:8080/v2/stats").json()["content_hash"]
# Generate embeddings externally (out of STEMMA)
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("BAAI/bge-large-en-v1.5")
texts = [f"{e['name']} ({e['id']}) Domain: {e['domain']} Definition: {e['definition']}" for e in entities]
vectors = model.encode(texts, normalize_embeddings=True)
# Build FAISS externally (out of STEMMA)
import faiss, numpy as np
index = faiss.IndexFlatIP(1024)
index.add(np.array(vectors, dtype='float32'))
# RAG query externally (out of STEMMA)
query = "What is Newton's second law?"
query_vec = model.encode([query], normalize_embeddings=True)
scores, ids = index.search(np.array(query_vec, dtype='float32'), k=5)
retrieved = [entities[i] for i in ids[0]]
context = "\n".join([f"{e['name']} ({e['id']}): {e['definition'][:200]} Source: {e['provenance']['link']}" for e in retrieved])
# Call LLM externally with citations
```

Connection via API + content_hash, does NOT contain whole STEMMA, just connection layer

### Option C: SDK-based — Python adapter

```python
from stemma_adapter import Stemma
from external_rag import StemmaRAG  # external RAG, out of STEMMA

stemma = Stemma.from_file("../exports/knowledge.json")  # or from_api
rag = StemmaRAG.from_stemma(stemma, embedding_model="BAAI/bge-large-en-v1.5", vector_store_path="./data/vector_store/")
answer = rag.query("What is Newton's second law?", top_k=5, model="deepseek/deepseek-r1:free", consumer="learninghub")
print(answer['answer'])  # with citations
```

Connection via SDK + content_hash, does NOT contain whole STEMMA, just connection layer

## Current implementation — optional derived inside STEMMA for convenience, but can be out

- Currently: scripts/embed.py, rag.py, export_consumers.py, exports/embeddings.jsonl, vector_store/, adapters/python/ v0.2.0, webapp RAG playground — inside STEMMA repo, but as derived + consumer layer, not canonical, optional, INFO not FAIL in verify_all.py — convenient for demo
- Can be out: YES, move to separate repo STEMMA-RAG or to LearningHub/PROFESSOR-J, keep STEMMA core pure with only content/, connections/, sources/, schema/, validate.py — cleaner separation

## Recommendation

- Keep canonical pure: content/, connections/, sources/, schema/ — NO embeddings, NO RAG, validate.py NEVER checks embeddings — whole STEMMA
- Keep derived optional inside for convenience: exports/knowledge.json, embeddings.jsonl, vector_store/, INFO not FAIL
- For production LearningHub, PROFESSOR-J: have embedding and RAG out of STEMMA as separate service that consumes STEMMA via file/API/SDK + content_hash, generates embeddings externally, builds vector store externally, serves RAG with citations — embedding/RAG doesn't contain whole STEMMA, just connection layer, whole STEMMA remains in STEMMA repo

Therefore: YES, you can have embedding and RAG out of STEMMA, they connect via exports/knowledge.json + API + SDK + content_hash, they don't contain whole STEMMA, they're just connection layer.
