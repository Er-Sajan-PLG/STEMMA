# DECISION 0029 — Refoundation baseline and architectural freeze

- **Date:** 2026-09-04
- **Status:** decided (baseline recorded); **freeze active**.
- **Related:** ADR-0027, ADR-0028, all specifications under `docs/`

## Context

The 2026-09 refoundation (ADR-0027/0028) re-established STEMMA as an
independent open-source project: new authoritative documentation set,
`stemma:` namespace, single relationship source, contract v2.0.0, cleaned
repository. To prevent the historical pattern — competing documents
describing slightly different systems, experimental content silently becoming
architecture — a single baseline must be declared authoritative.

## Decision

**Baseline 3.0.0** is the architectural freeze point. Exactly one
authoritative definition exists for each subject:

| Subject | Authority |
|---|---|
| Vision, scope, non-goals | `docs/VISION.md` |
| System architecture, invariants | `docs/ARCHITECTURE.md` |
| Domain model, identity, lifecycle | `docs/DOMAIN-MODEL.md` |
| Schema philosophy & contracts | `docs/SCHEMA-SPECIFICATION.md` |
| Metadata philosophy | `docs/METADATA-SPECIFICATION.md` |
| Relationship model | `docs/RELATIONSHIP-SPECIFICATION.md` + `schema/relation-registry.yaml` |
| Pipelines | `docs/PIPELINES.md` |
| Testing strategy | `docs/TESTING.md` + `scripts/verify_all.py` |
| Standards & interop | `docs/STANDARDS.md` |
| Governance, human gates | `docs/GOVERNANCE.md` |
| Security/integrity/provenance | `docs/SECURITY-INTEGRITY-PROVENANCE.md` |
| Consumer contract | `schema/export.schema.json` + `docs/CONSUMERS.md` |
| Roadmap | `docs/ROADMAP.md` |
| Versioning | `docs/VERSIONING.md` + `schema/VERSION.yaml` |
| Decision history | `docs/decisions/` |

Freeze means: changes to any of the above require a documented decision
(ADR) rather than drift. Minor editorial improvements remain unrestricted.

## Open items requiring human decisions (standing register)

| # | Item | Where recorded |
|---|---|---|
| 1 | Public IRI base for IDs and schema `$id`s (placeholder `stemma.example` in use) | `docs/STANDARDS.md` §4 |
| 2 | Math layer (equations/dimensions/units as data) | ADR-0024 (proposed) |
| 3 | Reviewer identity policy (ORCID-backed or pseudonymous) | ROADMAP R1 |
| 4 | Ratification of ADR-0027's three flagged choices | ADR-0027 §Human review |

## Consequences

- Future work is evaluated against this baseline; a document that contradicts
  the gate or the schemas is a bug (docs-consistency test enforces the set).
- The old accumulation pattern (new plan superseding old plan, both kept) is
  retired: plans live in one ROADMAP, decisions in ADRs, status in
  IMPLEMENTATION-STATUS.
