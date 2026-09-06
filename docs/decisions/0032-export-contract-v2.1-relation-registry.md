# DECISION 0032 — Export contract v2.1: relation registry + controlled vocabularies

- **Date:** 2026-09-06
- **Status:** decided & implemented
- **Related:** ADR-0021 (registry integrity), ADR-0022 (single version source),
  ADR-0023 (export contract), ADR-0028 (contract v2.0), ADR-0030 (consumer
  adapter), `docs/SOTA-REVIEW.md` §0.2 (T1 decision).

## Context

The export is the consumer contract, but it only publishes literal relation
names. Consumers cannot introspect relation families, inverses, transitivity,
domain/range, adopted-vs-reserved status, or the controlled vocabularies without
cloning the producer repository. ADR-0030 recorded this as a documented gap.

## Decision

The export gains an **additive, optional** relation-registry and vocabulary
sidecar:

- `relation_registry_version` (semver, mirrors `schema/relation-registry.yaml`).
- `relation_registry` — mapping of relation name → `{family, inverse,
  transitive, symmetric, domain, range, status}`.
- `vocabularies` — `{domains, subdomains, regimes, scales}` from
  `schema/vocabularies/`.

`export_version` moves **2.0.0 → 2.1.0** (additive minor bump). Old `2.0.x`
readers ignore the new members; `schema_version` and canonical object schemas
are unchanged.

## Consumer semantics

- If `relation_registry` is present, a consumer adapter **fails closed**: a
  connection whose `relation` is unknown rejects the export.
- If absent (an older `2.0.x` export), the adapter keeps its previous
  literal-name behavior (no relation introspection, no fail-closed relation
  check).
- The first-party Python adapter exposes `relations()`, `relation(name)`, and
  the `vocabularies` sidecar so downstream consumers can answer semantic
  questions without the producer repo.

## Alternatives considered

- **Require the member (contract 3.0).** Rejected: an unnecessary breaking
  change while no consumer depends on it.
- **Separate sidecar file.** Rejected: one contract file is simpler and keeps
  the artifact self-describing.
- **Keep as gap.** Rejected: it is the principal adaptor-boundary weakness.

## Consequences

- `schema/export.schema.json` gains optional members; `scripts/validate.py`
  emits them; the adapter introspects and validates them.
- `docs/CONSUMERS.md` documented version becomes `2.1.0`.
- Regression tests ensure determinism and old-`2.0.x` compatibility.
