# DECISION 0020 — Connections-only relationship truth; inline block is a generated projection

- **Date:** 2026-09-03
- **Status:** decided (implemented with this change; owner-directed activation of plan v2)
- **Related:** ADR-0011 (declared the same intent, never mechanized), ADR-0003 (identity),
  `docs/ARCHITECTURE-AUDIT-v1.0.md` (finding F1), `docs/STEMMA-IMPLEMENTATION-PLAN-v2.md` (E1)

## Context

ADR-0011 made `connections/` the single source of truth for relationships and demoted
`entity.relationships[]` to a "compatibility projection" — but no generator, consistency gate,
or deprecation path was ever built. Measured consequence (audit F1): all 641 inline
relationships duplicated 1:1 as connection files, 13 connection pairs existed only in
connections, consumers read the legacy inline projection, and nothing detected drift. Two
truths lived in canonical files.

## Decision

1. `connections/` is the **sole** canonical relationship source. Editing relationships means
   adding/deprecating connection objects. New inline relationships that do not exist in
   `connections/` are a validation error.
2. `entity.relationships[]` is a **generated compatibility projection**:
   `relationships := [{type, target} for active connections with source == entity.id]`,
   sorted by (type, target). Generator: `scripts/sync_relationships.py` (idempotent).
3. `scripts/validate.py` recomputes the projection and **fails on any drift** with the exact
   repair command.
4. Inline relation names are governed by `schema/relation-registry.yaml` (the schema enum is
   relaxed to `string`; the gate enforces membership).
5. Removal of the inline block from `concept.schema.json` and the export is deferred to the
   contract v1.x bump (gate G-A of plan v2 E1.5) with consumer co-release.

## Alternatives considered

- Keep hand-maintained inline as a second truth — rejected: it is the audited defect.
- Delete the inline block immediately — rejected: the one live consumer adapter and the
  explorer still read it; removal is gated (G-A), not silent.

## Consequences

- The graph has exactly one truth; drift is mechanically impossible while the gate runs.
- Entity diffs for relationship changes appear only via regeneration (reviewable, deterministic).
- Consumers keep working unchanged until the coordinated contract bump.
