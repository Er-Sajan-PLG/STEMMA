# DECISION 0021 — Multi-Level Validation Pipeline with Severity Levels

- **Date:** 2026-09-06
- **Status:** decided
- **Related:** scripts/validate.py, ADR-0013, specification §13

## Context

The v0.2 validator was a single-pass checker that treated all failures as blocking errors. It couldn't distinguish between:
- True canonical invalidity (must block)
- Data quality issues (should warn)
- Improvement suggestions (informational)

This made it impossible to maintain a growing knowledge base where legacy content has known issues but shouldn't block new contributions.

## Decision

**Implement a 9-stage validation pipeline with three severity levels:**

### Severity Levels
| Level | Blocks Export | Use Case |
|-------|---------------|----------|
| **ERROR** | YES | Invalid canonical content (schema, dangling refs, ID conflicts) |
| **WARNING** | NO | Data quality issues (missing inverses, structural cycles) |
| **INFO** | NO | Improvement suggestions (quantity missing unit, misconception missing related_to) |

### Validation Stages
1. **Syntax & Parse** — YAML validity, duplicate keys, frontmatter structure
2. **Schema Conformance** — JSON Schema validation
3. **ID & Identity** — Format, uniqueness, filename matching, aliases
4. **Semantic Constraints** — applies_to/appears_in_law rules, type-specific checks
5. **Referential Integrity** — All targets resolve, no dangling references
6. **Provenance & Lifecycle** — Required fields, reviewer for canonical, deprecation hygiene
7. **Structural Validation** — Cycle detection (structural transitive only), inverse consistency
8. **Extension Registry** — Registered keys, applicability, enums, types
9. **Entity-Connection Consistency** — Inline relationships represented in first-class connections

### Reporting
- SHACL-style validation report (`reports/validation-report.json`)
- Machine-readable with severity per result
- Exit 0 on WARNING/INFO only; exit 1 only on ERROR

## Alternatives Considered

- **Single severity (all errors)**: Rejected — blocks legitimate growth
- **Warning-as-error flag**: Rejected — still binary, no gradation
- **Separate linter tool**: Rejected — validation must be single command for CI

## Consequences

- Legacy content (224 entities, 654 connections) now passes validation
- New content held to higher standard (WARNINGs should be addressed)
- CI can enforce ERROR-only gate while tracking WARNING/INFO trends
- Validation report enables tooling (IDE integration, dashboards)

## Status

**decided** — implemented in scripts/validate.py v0.3.