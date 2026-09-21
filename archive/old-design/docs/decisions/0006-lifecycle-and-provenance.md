# DECISION 0006 — Lifecycle and provenance

- **Date:** 2026-08-12
- **Status:** decided (documented)
- **Related:** specification §8

## Context

Content must carry an honest record of its maturity and origin. In particular,
**machine validation ≠ scientific correctness**.

## Alternatives considered

- Two states (draft/canonical) — rejected: hides the review step
- Full citation database — rejected: overbuilding

## Decision

Lifecycle: `draft → machine_validated → human_reviewed → canonical → deprecated / superseded`
(forward-only; released entities are never edited in place).

Provenance: `ai_drafted` (required) + optional `source_kind` (controlled vocabulary),
`source`, `reviewer`, `reviewed_at`. `reviewer` is required before `human_reviewed`/`canonical`.

Principle: **AI assistance is provenance information, not authority.** AI content never becomes
canonical without human review.

## Reason

Traceability without a research-citation database; a named human gate preserves authority.

## Consequences

- Validator enforces reviewer presence for reviewed/canonical states.
- Seed entities stay `status: draft`, `ai_drafted: true` until human review.

## Status

**decided (documented).**
