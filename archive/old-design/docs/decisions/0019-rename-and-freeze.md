# DECISION 0019 — Rename foundation to STEMMA; freeze the `lhs:` identity & schema/export contracts

- **Date:** 2026-09-02
- **Status:** decided (implemented with this PR)
- **Related:** ADR-0003 (rename ≠ ID change), ADR-0007 (export contract), ADR-0008 (versioning),
  `docs/STEMMA-SPECIFICATION.md`, `docs/STEMMA-CONSUMER-SEAM.md`

## Context

The workspace distinguishes a canonical STEM knowledge **foundation** from the application/ecosystem
and intelligence layers. The foundation was historically branded **LearningHubSTEM**, which conflated
the foundation identity with the "LearningHub STEM" product lineage. To make the foundation a
general-purpose, open-source-ready canonical source, it is renamed to **STEMMA**. The consuming
product repository is independently renamed **STEM-TUITION → LearningHub** (recorded separately).

Crucially, the rename must **not** change identity or contract semantics. `lhs:` identifiers, the
schema, and the export contract have already been relied upon by adapters (`lhs-adapter`), and
were frozen by prior decisions (esp. ADR-0003).

## Decision

1. The canonical knowledge foundation repository is renamed **LearningHubSTEM → STEMMA**.
   Its GitHub identity becomes `Er-Sajan-PLG/STEMMA`.
2. The `lhs:` identity namespace remains **immutable**: entity, connection, and source IDs
   (`lhs:<domain>.<slug>`, `lhs:conn.*`, `lhs:src.*`) are permanent and never reused or reassigned.
3. The **schema contract** (`schema/concept.schema.json`, `schema/connection.schema.json`,
   `schema/source.schema.json`, including current `schema_version`) remains **frozen**.
4. The **export contract** (`exports/knowledge.json`, `export_version`, `schema_version`) remains
   **frozen**. The export remains a DERIVED artifact, regenerated only by `scripts/validate.py`.
5. Adapter protocol naming is **unchanged**: `lhs_adapter.py` / `lhs-adapter.ts`,
   `LhsEntity`, `LhsRelationship` describe the protocol/contract, not the old repo brand.
6. The rename does **not** alter any knowledge semantics, topic relations, provenance, or content.
7. Any future identity change (namespace migration, ID reassignment, contract break) requires a
   **separate architectural decision record**.

## Consequences

- **Positive:** STEMMA is an independently-usable canonical foundation; consumers (LearningHub,
  PROFESSOR-J, future products) depend on a stable contract. Historical docs may retain the old
  name only when explicitly describing history.
- **Negative:** previous external references to the `LearningHubSTEM` repo/name must be updated to
  `STEMMA`. GitHub auto-redirects the old URL.
- **Risk:** accidental `lhs:`/schema/export mutation during re-branding. Mitigated by a monotonic
  ID-immutability check (Scope B), the review gate (Scope C), and repeated validation.