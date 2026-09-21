# DECISION 0009 — Multilingual principle

- **Date:** 2026-08-12
- **Status:** decided (documented); policy approval pending in the human-decision list
- **Related:** specification §12

## Context

LearningHubSTEM is global in intent. Multilingual content must not fragment conceptual identity.

## Alternatives considered

- Per-language entities — rejected: fragments identity
- Full multilingual implementation now — rejected: premature
- Language-independent identity + documented principle ← **chosen**

## Decision

**Concept identity is language-independent.** `lhs:phys.force` has representations English
"Force", Nepali "बल", Hindi "बल" — but one identity. Multilingual content is a future phase.

Open questions (LATER): canonical language (if any), translation provenance, human vs AI
translation, translation review, locale-specific terminology.

## Reason

Language is presentation of a concept, not the concept itself — consistent with the
Knowledge ≠ Curriculum ≠ Pedagogy ≠ Product boundary.

## Consequences

- No multilingual content in v0.1; languages never create new IDs.
- When implemented, translations are derived/attached representations, not new entities.

## Status

**decided (documented).** Multilingual policy approval is human item 8.
