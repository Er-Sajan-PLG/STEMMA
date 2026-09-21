# DECISION 0001 — Licensing

- **Date:** 2026-08-12 (drafted); **decided 2026-09-02**
- **Status:** decided (2026-09-02)
- **Related:** specification §15

## Context

"Open" needs legal grounding. Two tracks were considered: knowledge/content and
code/tooling. This decision was documented as a human call and marked **PENDING** until the
owner approved.

## Alternatives considered

| Track | Candidate | Implication |
|-------|-----------|-------------|
| Knowledge/content | **CC BY 4.0** | attribution required; reusable/remixable/commercial with credit; interoperable; attribution preserved |
| Knowledge/content | **CC0** | public-domain dedication; maximal openness; attribution not required; irrevocable |
| Code/tooling | **MIT** | permissive, minimal, widely understood; no patent grant |
| Code/tooling | **Apache-2.0** | permissive + explicit patent grant + contribution terms |

## Decision

Decided 2026-09-02 (owner approval):

- Knowledge/content → **CC BY 4.0** (preserves attribution for an open knowledge foundation while
  enabling reuse). Ship as `LICENSE`.
- Code/tooling → **MIT** (simplest fit for the small validator/scripts; Apache-2.0 if external
  contributors or patent clarity become important). Ship as `LICENSE-CODE`.

## Reason

CC BY 4.0 balances the "anyone can build on it" goal with durable attribution, which supports the
foundation's provenance principle. MIT keeps tooling friction low.

## Consequences

- `LICENSE` (CC BY 4.0) and `LICENSE-CODE` (MIT) are the authoritative license files.
- The license scope matches the README and specification §15: content
  (`content/`, `connections/`, `sources/`, `docs/`) is CC BY 4.0; code
  (`scripts/`, `schema/`, tests) is MIT.

## Status

**decided 2026-09-02** (items 1 and 2 of the human-decision list).
