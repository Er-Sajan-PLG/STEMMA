# ADR-0048: New Relations equivalent_to and misconception_of

Status: Decided
Date: 2026-09-21
Baseline: ADR-0044
Related: docs/ARCHITECTURE-V2.md Part 3.4, schema/relation-registry.yaml

## Context

Relation registry has 55 relations in 13 families 12 adopted 43 reserved. Reserved may not enter canonical without ADR adopting them. Need relations for formulation equivalence and misconception linking for governing laws dual-role architecture.

## Decision

Adopt two relations in Phase 1d:

**equivalent_to** (currently reserved) — adopted for formulation equivalence, e.g., different formulations of same law.

- Domain: law
- Range: law
- Symmetric: true
- Transitive: true
- Inverse: null (symmetric)
- Description: Two formulations are equivalent under specified regime/context

**misconception_of** (new) — adopted for linking misconception entities to subjects.

- Domain: misconception
- Range: enumerated entity types from concept.schema enum NOT "any" — must be specific type that can be misconceived, e.g., concept, law, process
- Symmetric: false
- Inverse: null
- Transitive: false
- Description: Misconception entity is misconception about subject entity

Example:
```yaml
id: stemma:conn.000001
source: stemma:misconception.photosynthesis-soil
relation: misconception_of
target: stemma:concept.photosynthesis
evidence: [{source_id: src.misconception-study-2023, text_span: "42% students think photosynthesis needs soil"}]
value:
  amount: "42.0"
  unit: "1"
  lowerBound: "38.0"
  upperBound: "46.0"
```

Domain misconception range enumerated types from concept.schema enum NOT "any" explicitly declare symmetric false inverse null transitive false.

Update validator domain/range checks.

Cycle scoping: Gate cycle detection check_relationship_cycles applies to ALL transitive non-symmetric relations no blanket exemptions. Derivation cycles derived_from mathematically_requires logically_requires are genuine logical contradictions must be caught. If reproduced false positive appears scoped cycle_policy:warn escape hatch may be added for that specific relation via ADR not preemptively on empty corpus.

## Consequences

Easier: expressing coexisting formulations of laws with regime-qualified validity equivalent_to, expressing misconception prevalence as first-class evidence-bearing value-claims.

Harder: misconception as Entity vs Claim distinction requires understanding, range enumeration may be restrictive.

Hard to undo: once relations exist removing requires migrating all connections using them.

## Verification

- equivalent_to with domain not law → error
- misconception_of with range outside enumerated types → error
- Missing symmetry declaration → error
- Cycle detection still rejects structural hierarchy cycles and dependency cycles no exemptions

## Related

- ADR-0044 Part 3.4, Part 3.8 governing laws dual-role
- docs/ARCHITECTURE-V2.md Part 3.4, 3.8
- schema/relation-registry.yaml
