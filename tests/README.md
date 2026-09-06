# STEMMA — Test Suite

Layered invariant tests. Strategy and layer map: `docs/TESTING.md`.
Entry point: `python3 scripts/verify_all.py` (the chain CI runs).

Tests are plain runnable Python scripts (no framework required): each exits 0
on pass. Pure detection cores are importable for reuse.

| Directory | Layer | Highlights |
|---|---|---|
| `repo/` | Repository integrity | Ecosystem independence (ADR-0027 §6); docs consistency (ADR-0029); version single-sourcing |
| `phase-b/` | Domain invariants | Boundary (canonical vs derived), reconciliation (no orphaned references), validator idempotence, registry guardrails, provenance |
| `registry/` | Schema tests | Relation-registry coherence (inverses mirror, types exist) |
| `relationships/` *(removed)* | — | Projection-sync tests deleted with the projection itself (ADR-0028) |
| `curation/` | Workflow + identity | Review protocol, generality (curriculum-agnosticism), ingestion safety, id/triple immutability (pure-logic TDD core) |
| `metadata/` | Metadata semantics | Polarity/confidence/timestamps/evidence contracts, no-fabrication, duplicate-key rejection, extensions, historical attribution |
| `provenance/` | Provenance & contract | Agent-registry resolution, external-id formats, claim signatures, consumer-docs version currency |
| `versioning/` | Determinism/compat | Byte-identical regeneration; export conforms to contract; contract rejects malformed payloads |

Explorer end-to-end check: `npm --prefix explorer run verify` (projects from
`connections[]`, trust-annotated; rejects contract-violating exports).
