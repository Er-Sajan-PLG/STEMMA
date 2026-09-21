# DECISION 0011 — Connection as first-class canonical assertion

- **Date:** 2026-08-30
- **Status:** decided (Phase A — awaiting human approval for activation)
- **Related:** specification §2, §5, §11; decisions 0002, 0005

## Context

v0.1 stores relationships inline inside entities (`entity.relationships[]`). This ties the lifecycle of an assertion to one endpoint entity, makes qualified metadata (confidence, evidence, provenance, context, inference) impossible to express cleanly, and conflates the assertion with the thing it describes. External evidence (Biolink Association model, PROV-O qualified relations, RDF 1.2 triple terms) treats the proposition as an object distinct from its subject/object.

124 entities exist; 205/368 relationships are generic `related_to` — weak signal. The goal is a scientific connection system that can explain *why* two topics are connected, *under what conditions*, *based on what evidence*, and *whether asserted or inferred*.

## Decision

**Connection is a first-class canonical object** with its own file and lifecycle, independent of either endpoint entity.

Canonical model becomes:

```
Entity        — describes things (concept, quantity, law, phenomenon, model, ...)
Connection    — describes claims about things (source · relation · target + qualifiers)
Source        — describes citation objects
Evidence      — supports a connection
Agent/Method  — describes who/how a connection was produced
```

File layout:

```
content/        — entities (one Markdown+YAML per entity, no connections)
connections/    — one YAML per connection, id = lhs:conn.NNNNNN
sources/        — one YAML per shared citation, id = lhs:src.<slug>
schema/         — concept.schema.json + connection.schema.json + source.schema.json + relation-registry.yaml
```

Entity does **not** contain the connection. Entity's `relationships[]` is retained during v0.2 as a **compatibility projection** regenerated from canonical `connections/` (not a second truth).

ID rule: `lhs:conn.NNNNNN` sequential, opaque, 6-digit zero-padded, immutable, never reused after deletion. Later scale may move to UUIDv7 without semantic change (RFC 9562 opaque principle).

## Alternatives considered

- Inline `connections:` array inside entity frontmatter — rejected: reintroduces endpoint coupling; prevents multiple qualified assertions between same pair with different contexts
- Keep `relationships[]` only and add metadata fields — rejected: turns entity file into assertion container; cannot cleanly model `A causes B under X` vs `A causes B under Y`
- Embed source metadata inside each connection — rejected: duplication at 1000+ connections

## Reason

An assertion can have multiple variants between the same pair (`causes`, `contributes_to`, `analogous_to`, `limited_by`) with different contexts, evidence, confidence, and review states. It can be deprecated/rejected without editing either entity. This matches qualified-assertion practice.

## Consequences

- New canonical types: `connections/`, `sources/`; new schemas; validator expansion
- `schema_version` -> 0.2 (additive); `export_version` stays 0.1 during v0.2
- Legacy `relationships[]` = derived compatibility; single source of truth is `connections/`
- Migration must be idempotent and must not fabricate epistemic metadata
