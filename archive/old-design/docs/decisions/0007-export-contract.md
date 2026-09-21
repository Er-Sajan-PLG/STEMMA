# DECISION 0007 — Export / consumer contract

- **Date:** 2026-08-12
- **Status:** decided (documented)
- **Related:** specification §11

## Context

Consumers must be able to consume LearningHubSTEM without depending on its internals — and
without LearningHubSTEM depending on them.

## Alternatives considered

- REST API / GraphQL / microservice — rejected: infrastructure, out of scope for Phase 1
- Direct file reads by consumers — rejected: no stable contract
- Versioned machine-readable file export ← **chosen**

## Decision

Consumption boundary:

```text
canonical content → scripts/validate.py → exports/knowledge.json → consumer adapter → consumer app
```

The export contract documents: export version + schema version, entity representation, stable IDs,
lifecycle status, relationships, provenance, handling of deprecated entities (kept, flagged,
never silently deleted), and the regeneration principle.

## Reason

A documented file/export contract is sufficient for Phase 1; it keeps the foundation independent
of consumers (e.g. STEM-TUITION) while being genuinely consumable.

## Consequences

- No API, microservice, auth, or cloud infrastructure is built to demonstrate the contract.
- Deprecated entities remain in the export for consumer migration.

## Status

**decided (documented).**
