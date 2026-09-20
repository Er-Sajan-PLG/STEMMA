# DECISION 0020 — Extended Canonical Entity Model (v0.3)

- **Date:** 2026-09-06
- **Status:** decided
- **Related:** specification §4, schema/concept.schema.json, ADR-0004, ADR-0010

## Context

The v0.2 entity model defined 10 types: concept, quantity, unit, law, equation, misconception, phenomenon, model, experiment, regime. However, the specification (§4) only documented 6 core types. This inconsistency created confusion about which types were "official" vs "experimental."

Additionally, several scientifically important entity types were missing entirely:
- `observation` — empirical observations (distinct from experiments)
- `measurement` — quantified observations with units
- `classification` — taxonomic/classification schemes
- `definition` — formal definitions (distinct from concepts)
- `claim` — scientific claims with evidence/provenance

The existing `phenomenon`, `model`, `experiment`, `regime` types were in schema but not properly specified.

## Decision

**Extend the canonical entity model to 15 types with clear categorization:**

### Core Types (Always Available)
1. `concept` — General idea/notion
2. `quantity` — Measurable property
3. `unit` — Standard of measurement
4. `law` — Principle/rule
5. `equation` — Mathematical relation
6. `misconception` — Common false belief

### Extended Types (For Richer Modeling)
7. `phenomenon` — Observable occurrence
8. `model` — Simplified representation of reality
9. `experiment` — Controlled investigation
10. `regime` — Domain of applicability (conditions, scale)
11. `observation` — Empirical observation
12. `measurement` — Quantified observation with units
13. `classification` — Taxonomic scheme
14. `definition` — Formal definition
15. `claim` — Scientific assertion with evidence

**Schema version bumped to 0.3** (additive - no breaking changes to existing entities).

All types share the same required fields and frontmatter structure. Extended types are not mandatory but available when needed for precise knowledge modeling.

## Alternatives Considered

- **Keep 10 types only**: Rejected — missing types force overloading existing types (e.g., using `concept` for `observation`)
- **Separate schemas per type**: Rejected — adds complexity, single schema with type enum is simpler
- **Make all 15 core**: Rejected — many domains don't need all types; 6 core is sufficient for MVP

## Consequences

- Existing 224 entities unchanged (all use core types)
- New entities can use extended types for precision
- Validator updated to accept all 15 types
- Export includes all types
- Consumer adapters handle unknown types gracefully (pass through)
- Specification §4 updated to document all 15 types

## Status

**decided** — implemented in schema/concept.schema.json v0.3 and validator.