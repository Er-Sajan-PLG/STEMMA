# DECISION 0008 — Versioning

- **Date:** 2026-08-12
- **Status:** decided (documented)
- **Related:** specification §10

## Context

Schema, export contract, and knowledge content change at different rates. Collapsing them into one
number forces consumers to re-render on every content change.

## Alternatives considered

- Single version number — rejected: conflates three independent tracks
- Full package-manager/release pipeline — rejected: premature
- Three distinct tracks ← **chosen**

## Decision

Three version tracks, never collapsed:

1. **Schema version** — version of `schema/concept.schema.json`.
2. **Export / contract version** — version of the export file contract.
3. **Content release** — the knowledge set itself (LATER; no tooling now).

Both `schema_version` and `export_version` are recorded in the export. A consumer states "I consume
export contract version X" without implying every knowledge release requires a rewrite.

## Reason

Separating tracks keeps content evolution cheap and contract evolution governed.

## Consequences

- Adding/editing/deprecating entities is a content change, not a contract change.
- Breaking schema or contract changes are governance events (freeze rule).

## Status

**decided (documented).**
