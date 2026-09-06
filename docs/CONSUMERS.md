# STEMMA — Consumers & Integration

**Status:** Authoritative. How any external system consumes STEMMA.
**Contract:** `schema/export.schema.json` · current contract line:
`export_version: 2.1.0` (verified against `schema/VERSION.yaml` by the test
suite — a stale version here fails CI).

---

## 1. The consumption model

STEMMA publishes one thing: a **versioned, validated, deterministic JSON
export** of its canonical knowledge. Consumers read the export, adapt it to
their own needs, and own everything downstream:

```
STEMMA (canonical, gated) ──▶ exports/knowledge.json (contract v2.x)
                                      │
                                      ▼
                      consumer adapter (consumer-owned)
                                      │
                                      ▼
           curricula, apps, tutors, simulators, AI systems
```

Consumers are external by design. STEMMA records no consumer as a dependency,
and nothing in this repository may assume a particular consumer exists
(machine-checked: `tests/repo/test_independence.py`).

## 2. Reading the export

- Pin the **contract major version** (`export_version` starts with `2.`).
  Reject exports whose major version you do not support rather than guessing.
- Required members: `entities[]`, `connections[]`, `sources[]`, counts,
  `content_hash`, versions (see `docs/SCHEMA-SPECIFICATION.md` §6).
- Optional semantic sidecar (contract v2.1): `relation_registry`,
  `relation_registry_version`, `vocabularies`. When present, a consumer
  **must** fail closed on a connection whose `relation` is not declared.
- **The graph is `connections[]` only** — entities carry no relationship data
  (contract v2.0). Draw edges from connections; annotate with
  `assertion.review.status`.
- **Trust policy:** filter by review status for your use case. Ready-made
  views exist (`knowledge.canonical.json`, `knowledge.trusted.json`,
  `knowledge.reviewed.json`, `knowledge.proposed.json`); semantics in
  `scripts/graph_policy.py`. A conservative consumer uses `canonical` only.
- Deprecated/superseded objects remain exported (with successors) — never
  assume absence.
- `claim_signature` lets you deduplicate claims across views without
  recomputing hashes.

## 3. Consumer responsibilities

| Yours | STEMMA's |
|---|---|
| Curriculum mapping & sequencing | Stable IDs + explicit prerequisite relations |
| Presentation, pedagogy, assessment | Neutral knowledge data |
| Localization strategy | Language-independent identity |
| Caching & freshness | `content_hash` + deterministic regeneration |
| Filtering by trust | Per-assertion review status + policy views |

## 4. Adapter checklist

1. Validate the export against `schema/export.schema.json` on load.
2. Check `export_version` major; fail closed on mismatch.
3. Build your graph from `connections[]`; keep the review status on every
   edge; decide and document your trust policy.
4. Reference entities by ID, never by label (labels change; IDs never do).
5. Handle `deprecated`/`superseded` via successor pointers.
6. (Reference implementation: `explorer/` in this repo — a first-party
   consumer that obeys every rule above.)

## 5. First-party Python adapter

STEMMA now ships a first-party **read-only** Python adapter in
`adapters/python/`:

- standard-library only (`python>=3.10`),
- SDK (`stemma_adapter.Stemma`),
- CLI (`stemma-adapter`),
- local JSON API (`python3 -m stemma_adapter serve ...`).

This is a **consumer adapter**, not a new source of truth: it validates and
reads the export, mirrors `scripts/graph_policy.py` policy semantics, and
never writes canonical data. Adapter `0.1.x` ships in-repo; promotion to
adapter `1.0` and any PyPI publication remain human-gated release decisions.

Contract v2.1 (ADR-0032) closes the former relation-registry gap: the export
now embeds `relation_registry` + `relation_registry_version` + `vocabularies`.
The adapter surfaces these through `client.relations()`, `client.relation(name)`,
`client.vocabularies`, the CLI (`relations`, `relation`, `vocabularies`), and
the JSON API (`/v2/relations`, `/v2/relations/{name}`, `/v2/vocabularies`).
When the registry is present the adapter fails closed on an unknown relation.

## 6. Contributing corrections

Found a scientific error or a missing relationship? That is a canonical
change: propose it through contribution (`docs/CONTRIBUTING.md`) — assertions
are superseded, never edited in place. Consumer-specific needs (ordering,
grouping, presentation) never belong in canonical data.

---

*Historical note: earlier consumer-integration documents specific to a
particular external product were retired with the 2026-09 refoundation
(ADR-0027); their content is generalised here.*
