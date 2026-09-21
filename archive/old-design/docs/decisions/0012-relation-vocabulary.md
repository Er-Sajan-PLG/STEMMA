# DECISION 0012 — Relation vocabulary and authoritative registry

- **Date:** 2026-08-30
- **Status:** decided (Phase A)
- **Related:** specification §5, decisions 0005, 0011

## Context

v0.1 has 10 core relations; 8 are used, `related_to` dominates (205/368). The flat enum hides semantics: inference rules (transitive, symmetric, inverse), families, and domain/range constraints are implicit. Plan adds cross-domain bridges, analogies, model approximation, measurement, causal and explanatory relations.

Proposed `is_a: transitive true` was too broad; `extends/supersedes/isomorphic_to` were incorrectly transitive. Bridge validation `domain != domain` was too narrow.

## Decision

**Relation registry is the single source of truth.** File: `schema/relation-registry.yaml`.

- Enum of legal `relation` names lives in the registry, not only in `concept.schema.json`
- Each relation declares: `family`, `inverse`/`symmetric`, `transitive`, `domain`/`range`
- Validator enforces family membership and domain/range compatibility; rejects illegal inference
- Guardrails for v0.2: `is_a` = class/subclass semantics only; defer `instance_of`; `extends/supersedes/isomorphic_to` are **non-transitive**; causal `causes/contributes_to/results_in/influences` **non-transitive**

Families (v0.2 initial set, 11 families + 1 associative + 1 derivation):

```
structural:       is_a, part_of, has_part, contains, composed_of
hierarchical:     generalizes, special_case_of, broader_than, narrower_than
dependency:       requires, prerequisite_of, mathematically_requires, logically_requires, depends_on
causal:           causes, contributes_to, results_in, influences, prevents
explanatory:      explains, accounts_for, predicted_by, supported_by, evidenced_by
model:            approximates, idealizes, extends, supersedes
conflict:         contradicts, inconsistent_with, competes_with, limited_by
measurement:      measures, measured_by, quantifies, expressed_in, has_unit
engineering:      enables, used_in, applied_to, implemented_by
analogy:          analogous_to, isomorphic_to, corresponds_to
cross_domain:     bridges, maps_to, manifestation_of, shared_mechanism_with
associative:      related_to
derivation:       derived_from, appears_in_law, applies_to
```

`related_to` remains as symmetric `associative` fallback for genuinely unspecified association (not a garbage bin; review queue to reclassify).

## Alternatives considered

- Flat enum in `concept.schema.json` only — rejected: no place for inference semantics
- Ontology import (SKOS, Biolink) as canonical vocabulary — rejected: LHS stays lightweight Markdown+YAML; borrows principles not stack
- Symmetric/inverse materialized in canonical — rejected: keep canonical assertions only; derived graph computes closure (SKOS pattern: direct `broader` vs transitive closure separated)

## Reason

Every inference rule needs testable justification (OWL property characteristics have formal semantics). Transitivity/symmetry cannot be intuitive flags. Registry + validator makes semantics explicit and prevents contradictions.

## Consequences

- `derived` edges (inverse, transitive closure) are **derived graph intelligence**, never canonical
- Bridge validation is scope-aware: `domain != domain OR subdomain != subdomain` for `bridges`
- Dependency-cycle detection applies only to `dependency` family + selected transitive relations (`prerequisite_of`, `requires`, etc.), not to `analogous_to` chains
