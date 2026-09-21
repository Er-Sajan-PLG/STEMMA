# DECISION 0014 — Assertion mode, review lifecycle, and inference metadata

- **Date:** 2026-08-30
- **Status:** decided (Phase A)
- **Related:** decisions 0011, 0013

## Context

Previous plan duplicated concepts: `assertion_type: inferred` and `inference.mode: inferred` — allowing contradictions. Also proposed `is_a` with `transitive: true` and `instance_of` overlapping; `extends/supersedes/isomorphic_to` incorrectly transitive.

## Decision

**Single orthogonal dimensions:**

```yaml
assertion:
  status: active | deprecated | superseded   # lifecycle
  type: asserted | inferred | proposed        # epistemic origin
  review:
    status: unreviewed | reviewed | canonical  # review gate
  confidence: 0.0..1.0  # optional
  confidence_basis: ...

inference:  # present ONLY when type: inferred
  rule: prerequisite_transitivity
  path:
    - lhs:phys.A
    - lhs:phys.B
    - lhs:phys.C
```

Rules:

- Asserted: `type: asserted`, no `inference` block
- Inferred: `type: inferred` + required `inference.rule` + `inference.path`
- Proposed: `type: proposed`, no inference unless actually inferred
- No `inference` block when `type != inferred`
- Review lifecycle is independent: `inferred` can be `canonical` after review; `asserted` can be `unreviewed`

**is_a** = class/subclass only (`quark is_a particle`). `instance_of` deferred (no LHS use case for v0.2). Remove `instance_of` from v0.2 registry.

**Transitivity corrections for v0.2 (non-transitive):** `extends`, `supersedes`, `isomorphic_to`, plus all causal `causes/contributes_to/results_in/influences/prevents` and `analogous_to`. Registry declares these explicitly false; validator rejects auto-closure on them.

## Alternatives considered

- Single `status` enum mixing lifecycle + epistemic + review — rejected: creates contradictions (`inferred` vs `unreviewed`)
- `instance_of` alongside `is_a` — rejected: overlapping semantics; LHS models abstract knowledge, not individual instances
- Make all hierarchical relations transitive — rejected: each needs justification (e.g., `supersedes` historically is not transitive)

## Reason

`inferred` != `unreviewed`; `canonical` != `asserted`. Inference provenance must be checkable (PROV-O distinguishes agents/activities/qualified derivation). Non-transitive defaults are conservative and safe.

## Consequences

- Validator enforces mutual exclusivity; rejects `assertion.type: asserted` with `inference` block and vice versa
- Migration creates `type: proposed, review: unreviewed` (not `asserted`)
