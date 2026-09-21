# DECISION 0010 — Entity metadata extension (equation · symbol · unit · common_misconceptions)

- **Date:** 2026-08-12
- **Status:** decided (documented); implemented as Phase 2 scope
- **Related:** specification §2 (template), §4 (entity model); decision 0004

## Context

Phase 2 is the first consumer proof: a product must render an entity's statement, equation,
symbol and unit **from the export** without interpreting free prose. The Phase 1 template (§2)
carried only `definition` and `examples`, so this metadata had no machine-readable home. The
alternative — authoring separate Equation / Unit / Misconception entities for the seed — was
rejected as over-modeling for a five-entity proof set (those types stay available for growth).

## Alternatives considered

- Separate `equation` / `unit` / `misconception` entities for every fact (rejected: over-modeling;
  entity types remain fixed by decision 0004)
- Prose-only representation (rejected: the consumer would have to parse free text)
- Optional scalar metadata fields on the canonical entity ← **chosen**

## Decision

Extend the canonical entity with **optional** knowledge-layer fields:

| Field | Type | Meaning | Notes |
|-------|------|---------|-------|
| `equation` | string | canonical mathematical form using defined symbols | e.g. `F = m·a`; not a separate Equation entity |
| `symbol` | string | symbol(s) for the quantity/law | e.g. `F`, `m`, `a`, `p` |
| `unit` | string | SI unit of the quantity | e.g. `newton (N)`, `kilogram (kg)` |
| `common_misconceptions` | array of strings | common false beliefs learners hold | knowledge-layer; distinct from pedagogical relationships (§7) |

Rules:

- All four fields are **optional**; `additionalProperties: false` is preserved on the schema.
- They carry **knowledge, not curriculum and not pedagogy**. `common_misconceptions` records the
  false belief itself; how to teach against it belongs to consumers (§7).
- `equation` is a *display form* of an existing relationship; it does **not** create a new
  entity type, a new relationship, or a second canonical authoring source.
- No new relationship vocabulary and no new entity types are introduced (freeze rule respected).

## Reason

The consumer must be able to render `name · statement · equation · related entities` verbatim
from `knowledge.json`. Scalar metadata is the smallest contract that makes that possible without
changing the entity vocabulary.

## Consequences

- Schema `concept.schema.json` gains four optional properties; the export shape is otherwise
  unchanged.
- `schema_version` / `export_version` stay `0.1`: this is the first versioned consumer contract;
  no earlier consumer exists to break.
- Seed entities are enriched in Phase 2; enrichment is a content change (not a contract change).

## Status

**decided (documented).** Implemented under Phase 2 scope.
