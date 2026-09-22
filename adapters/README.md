# adapters/ — consumer connection layer (reference implementation)

- `python/stemma_adapter/` — read-only SDK + optional HTTP adapter exporting the
  deterministic derived export (`exports/knowledge.json`, export_version from
  `schema/VERSION.yaml`) as `/v2/*` endpoints (see [../schema/api.yaml](../schema/api.yaml)):
  `/v2/stats`, `/v2/entities`, `/v2/entities/{id}`, `/v2/connections`, `/v2/search`,
  `/v2/neighbors/{id}`, `/v2/prerequisites/{id}`, `/v2/relations`, `/v2/embeddings`,
  `/v2/rag/search`, `/v2/rag/query` (POST), `/v2/export`.
- Contract: [../docs/API.md](../docs/API.md) and exported sidecars (relation
  registry, vocabularies) inside the export itself.
- Ships `Stemma` / `load_export`; `StemmaRAG` is specified but not yet
  implemented (see [../spec/SPECIFICATION_GAP_ANALYSIS.md](../spec/SPECIFICATION_GAP_ANALYSIS.md),
  SPECIFIED_AND_MISSING finding).
- Consumers should connect via file / API / SDK + `content_hash`, never by
  reading canonical markdown (see [../docs/GUIDELINE-EMBEDDER-RAG.md](../docs/GUIDELINE-EMBEDDER-RAG.md)).
