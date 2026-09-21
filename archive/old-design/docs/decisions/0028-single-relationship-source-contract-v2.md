# DECISION 0028 — Single relationship source executed: contract v2.0, registry v1.0

- **Date:** 2026-09-04
- **Status:** decided & implemented (executes the endpoint already designed by
  ADR-0020 and scheduled in ADR-0023 §A.3; collected here with the refoundation).
- **Related:** ADR-0011 (connection model), ADR-0020 (connections-only truth),
  ADR-0023 (contract v1.0), ADR-0027 (namespace)

## Context

ADR-0020 made `connections/` the single relationship source but retained the
entity-side inline `relationships[]` block as a *generated compatibility
projection*, with contract v1.x still exporting it. Two consequences
persisted: dual representations in every entity file, and a standing risk of
projection drift. ADR-0023 §A.3 scheduled removal at contract 2.0. The
refoundation bump to 2.0.0 executes it. Separately, the relation registry
carried `reserved` relations duplicating adopted semantics (`broader_than`/
`narrower_than` ≡ `generalizes`/`special_case_of`; `contains` ≡ `has_part`;
`is_a` ≡ `special_case_of`), violating one-name-per-meaning.

## Decision

1. **Entities carry no relationship data at all.** The `relationships` field
   is removed from `concept.schema.json`; any relationship-shaped block on an
   entity is now a *validation error* (not merely drift). The projection
   generator (`sync_relationships.py`) and its sync test are deleted — there
   is nothing to sync.
2. **Export contract v2.0.0**: `entities[]` have no relationship member;
   `connections[]` is the graph. The explorer reads connections only and
   *rejects* exports missing them (contract-failure, not silent empty graph).
3. **Registry v1.0.0**: the four duplicate `reserved` relations are pruned.
   No adopted relation changed; canonical data is untouched (they had zero
   uses). SKOS `skos:broader/narrower` remain the interop mapping targets.
4. **Filename grammar**: connection/source filenames are the ID minus the
   namespace segment (colon-free), and filename↔ID consistency is now
   gate-checked.

## Alternatives considered

- **Keep the projection indefinitely** — rejected: it re-creates the
  two-truths failure mode ADR-0020 closed, and every consumer already had a
  contract-version pin to migrate by.
- **Prune all unused `reserved` relations** — rejected: the reserved
  vocabulary is deliberate design with defined semantics and promotion gates;
  only *duplicates* are defects.

## Consequences

- Consumers reading `entities[].relationships` must switch to `connections[]`
  (the reference explorer demonstrates the pattern).
- The schema major bump to 1.0.0 and contract 2.0.0 ride with ADR-0027's
  migration in one release.
- Entity files shrink; authoring has exactly one way to express a
  relationship.

## Human review

Executed as the scheduled endpoint of already-decided ADRs (0020, 0023);
flagged for information in the refoundation review rather than as a new
open question.
