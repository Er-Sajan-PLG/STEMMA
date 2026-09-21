# DECISION 0013 — Confidence and qualification semantics

- **Date:** 2026-08-30
- **Status:** decided (Phase A)
- **Related:** decisions 0011, 0012

## Context

Proposed `confidence` + `weight` conflated distinct dimensions (prerequisite strength vs evidential support vs centrality). `weight` had no operational definition. Migration proposed fabricating `confidence: 0.9, strength: 1.0` for all migrated edges — manufacturing certainty.

Biolink defines confidence as belief in the assertion itself, distinct from effect size/p-value; strength-style dimensions require separate operational definitions.

## Decision

**v0.2 keeps `confidence` only; generic `strength` is deferred.**

```yaml
assertion:
  confidence: 0.0..1.0  # optional, null if unknown
  confidence_basis: expert_review | experimental | theoretical | derived | null
```

- `confidence` = how confident we are that the assertion itself is correct, within its stated context/regime
- No global `strength` field until each relation family gets an operational definition (e.g., `prerequisite_strength` for dependency, `causal_strength` for causal — future ADRs)
- Context/qualifiers carry validity, not a number:
  ```yaml
  context:
    regime: [classical, nonrelativistic]  # multi-valued, controlled
    scale: macroscopic
    assumptions: [low_velocity, weak_gravity]
  ```

Migration never fabricates: `confidence: null`, `assertion.type: proposed`, `review.status: unreviewed`, `method: migration`.

## Alternatives considered

- Keep `strength: 0..1` globally — rejected: semantics differ per family, would produce meaningless numbers
- Fabricate defaults for migrated — rejected: turns uncertainty into fake precision
- Omit confidence entirely — rejected: epistemic uncertainty is central to scientific KG trust

## Reason

A high-confidence weak prerequisite (e.g., “Newtonian approximates relativity at low v” — confidence 0.99, but only within regime) must be distinguishable. Numbers without operational meaning erode trust.

## Consequences

- Template: `confidence` omitted or null for migrated connections; reviewed connections carry explicit basis
- Validator warns if `confidence` set without `confidence_basis` and vice versa
