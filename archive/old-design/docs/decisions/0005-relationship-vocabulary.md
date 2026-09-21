# DECISION 0005 — Relationship vocabulary

- **Date:** 2026-08-12
- **Status:** decided (documented); vocabulary approval pending in the human-decision list
- **Related:** specification §5

## Context

Relationships must be unambiguous. `requires(A, B)` and `related(A, B)` have very different
semantics and must not blur.

## Alternatives considered

- The earlier vision's loose set (`requires`, `teaches`, `extends`, `applied_in`, `related`, …)
  — rejected: `teaches` is ambiguous; `extends` overlaps `derived_from`/`generalizes`
- A large fixed list — rejected
- A curated core whitelist ← **chosen**

## Decision

**Core knowledge (canonical, v0.1):**

```text
logically_requires  mathematically_requires  part_of  derived_from
special_case_of     generalizes  equivalent_to  applies_to
appears_in_law      related_to
```

Each has documented meaning, direction, symmetry, inverse, transitivity, allowed entity types,
examples, and non-examples (specification §5.1). Pedagogical (`commonly_taught_before`,
`commonly_misunderstood_as`, `scaffolds`) and curriculum (`mapped_to_curriculum`,
`included_in_unit`, `assessed_by`) relationships are **not** canonical in v0.1. `teaches` is never
a core relationship.

Semantic enforcement (validator): `applies_to` source is a `law`; `appears_in_law` target is a
`law`.

## Reason

A small, precisely-defined whitelist keeps the canonical model unambiguous and testable while
leaving pedagogy and curriculum to their own layers.

## Consequences

- Adding/removing/redefining a core relationship is a governance event (freeze rule).
- Loose terms from the vision are mapped to the whitelist (e.g. `requires` → `logically_requires`
  / `mathematically_requires`).

## Status

**decided (documented).** Relationship vocabulary approval is human item 7.
