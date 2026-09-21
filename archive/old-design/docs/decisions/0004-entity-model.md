# DECISION 0004 — Entity model

- **Date:** 2026-08-12
- **Status:** decided (documented); vocabulary approval pending in the human-decision list
- **Related:** specification §4

## Context

The knowledge layer needs a minimal, unambiguous set of entity types — enough for real STEM
knowledge, not a grand ontology.

## Alternatives considered

- A single generic "node" type (rejected: loses meaning)
- A large typed hierarchy (rejected: premature)
- Six fixed types ← **chosen**

## Decision

Six entity types, fixed for v0.1: **Concept, Quantity, Unit, Law, Equation, Misconception.**

Per-type documentation (purpose, what it does/does not represent, required/optional fields,
relationship participation, deprecation, type-change rule) lives in the specification §4. Key
rules: a Law is the canonical source of `applies_to` and target of `appears_in_law`; an Equation
is not a Law; a Misconception is a false belief, not the correct concept; type changes are not
permitted (a different type is a new entity).

## Reason

Six types cover the seed and foreseeable growth without forcing premature modeling choices.

## Consequences

- Adding a seventh type requires a governance decision (freeze rule).
- Unit, Equation, Misconception are defined now but not present in the seed.

## Status

**decided (documented).** Entity vocabulary approval is human item 6.
