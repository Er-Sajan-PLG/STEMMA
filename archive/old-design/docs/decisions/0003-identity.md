# DECISION 0003 — Stable identity

- **Date:** 2026-08-12
- **Status:** decided (documented)
- **Related:** specification §3

## Context

Identifiers must survive renames, reordering, curriculum differences, and product differences.

## Alternatives considered

- Numeric/database IDs (rejected: not stable across systems)
- Path-dependent IDs (rejected: files move)
- Namespaced `lhs:<domain>.<slug>` ← **chosen**

## Decision

IDs are `lhs:<domain>.<slug>`, globally unique, stable, never reassigned, never reused,
machine- and human-readable, independent of files/curriculum/products. Rename ≠ ID change.
Split/merge/replace handled by deprecation + `deprecated_by` + `aliases` (never in-place mutation).

## Reason

Namespaced, ASCII, regex-validated IDs give uniqueness and readability without infrastructure.

**Why IDs must never change (the technical truth-protection rationale):** an `lhs:` ID is a
reference that external consumers depend on — adapters (`lhs-adapter`), caches, cross-references
in `connections/*.yaml`, `deprecated_by`/`aliases`, citations in the export contract, and any
consumer product or AI system that has already persisted an `lhs:` ID. If an ID's meaning were
reassigned (e.g. `lhs:phys.example` once meant "Classical mechanics" and later means "Quantum
mechanics"), every consumer that stored the old meaning would silently now point at a different
fact. IDs are therefore a **stable contract, not a label**: preserving identity preserves
knowledge-assignment truth; changing it quietly falsifies history. Deprecation plus
`deprecated_by` plus `aliases` are the only legitimate ways to evolve — never in-place mutation,
never reuse. See also ADR-0007 (export contract) and `docs/HISTORY-RENAME.md` (why repo names can
change but IDs and history must not).

## Consequences

- Deprecated IDs remain reserved forever; alias handling is explicit.
- Validator enforces ID format, uniqueness, and alias validity.

## Status

**decided (documented).**
