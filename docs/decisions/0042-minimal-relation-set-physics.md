# DECISION 0042 — Minimal Relation Set for Physics Foundation

- **Date:** 2026-09-21
- **Status:** PROPOSED — companion to ADR-0040/0041
- **Related:** ADR-0005 (relationship vocabulary), ADR-0012 (relation vocabulary + registry), ADR-0020 (connections-only truth), ADR-0028 (single relationship source contract v2), RELATIONSHIP-SPECIFICATION.md §2, relation-registry.yaml v1.0.0 (55 relations, 12 adopted), DEEP-DIVE-RECOMMENDATIONS.md R4 (relation vocabulary genericity)
- **Author:** arena/01a0c072-stemma

## Context (R4 - Relation Vocabulary Genericity)

Pre-refoundation:
- `related_to` = 371/654 (56.7%) — honest fallback but caps reasoning value
- 0 canonical `related_to`
- 61 pairs had both `related_to` + specific relation (redundant)
- Registry already reserves precise relations: `causes`, `contributes_to`, `explains`, `measures`, `quantifies`, `expressed_in`, `equivalent_to`

User proposal: "reduce relations (hopefully none)" — zero relations would make STEMMA a glossary, not a knowledge graph. It would violate:

- VISION: "concepts, quantities, laws, models, and the relationships between them"
- ARCHITECTURE §4: Entity↔connection boundary — entities carry no relationship data, connections only. Zero connections = zero relationships.
- DOMAIN-MODEL §4: Assertion model is heart of domain
- Consumer value: adapter search + closure, explorer DAG, prerequisite reasoning all require edges

The engine's hardest checks (domain/range, cycles over dependency family, inverse coherence, duplicate claim signatures) are only exercised with connections.

Goal: Minimal but sufficient set that covers physics modeling without `related_to`.

## Decision

### Physics-Core v0.1 May Use ONLY These 7 Adopted Relations (8 counting inverse pair)

| Relation | Family | Inverse (derived) | Transitive | Domain → Range (physics use) | Physics Example |
|---|---|---|---|---|---|
| `mathematically_requires` | dependency | `mathematically_required_by` (reserved) | true | law/equation/concept → quantity/concept | `newtons-second-law` mathematically_requires `mass` |
| `derived_from` | derivation | `is_basis_of` (reserved) | true | law/equation/concept → law/concept | `kinetic-energy` derived_from `energy`, `F=ma` equation derived_from `newtons-second-law` |
| `appears_in_law` | derivation | - | false | quantity/concept → law | `force` appears_in_law `newtons-second-law` (choose canonical direction: we will use law->quantity via mathematically_requires as primary, appears_in_law as secondary if needed, but not both for same pair) |
| `applies_to` | derivation | `governed_by` (reserved) | false | law → concept/quantity/phenomenon/model | `newtons-second-law` applies_to `point-mass` |
| `generalizes` | hierarchical | `special_case_of` | true | concept/law/model → concept/law/model | `energy` generalizes `kinetic-energy` |
| `special_case_of` | hierarchical | `generalizes` | true | concept/law/model → concept/law/model | `kinetic-energy` special_case_of `energy` |
| `part_of` | structural | `has_part` (reserved) | true | concept/phenomenon/model/quantity → same | `kinetic-energy` part_of `mechanical-energy` (or system composition) |
| `approximates` | model | `approximated_by` (reserved) | false | model/equation/law → phenomenon/model | `ideal-gas` approximates `real-gas-behavior`, `ideal-gas-law` approximates `real-gas` |

**Counting:** `generalizes` + `special_case_of` are inverse pair but both adopted, so 7 distinct names if counting `generalizes` as one family, 8 if counting both directions. We list 7 families.

**Banned for physics-core:**
- `related_to` — WARNING becomes ERROR via `physics_core_profile_check.py`. Rationale: forces precise modeling; if you can't name relation, you don't understand claim.
- All `reserved` relations (requires, causes, explains, etc.) — not allowed until ADR promotion. Physics can be modeled with adopted set.
- `bridges`, `analogous_to` — cross-domain/analogy not needed for foundation.

### Enforcement

- `scripts/physics_core_profile_check.py`: Scans `connections/*.yaml` where source or target domain=physics (via id prefix `stemma:phys.` or context.domain). If relation not in minimal set, ERROR.
- `tests/curation/test_physics_core_profile.py`: Asserts same.
- CI: `python scripts/physics_core_profile_check.py --profile physics-core` — advisory now, required for physics-core PRs.

### Modeling Patterns for Physics

**Quantity:**
```
quantity: mass
  appears_in_law -> newtons-second-law (or law mathematically_requires quantity, pick one direction to avoid duplicate signatures)
```

Canonical direction rule for physics-core to avoid duplicate claim signatures:
- For dependency: use `law --mathematically_requires--> quantity` as canonical, NOT quantity --appears_in_law-- law for same pair. Choose one.
- For hierarchy: use `specific --special_case_of--> general` as canonical (more natural reading: kinetic is special case of energy). `generalizes` is derived inverse.
- For structural: `part --part_of--> whole`

**Law:**
```
law: newtons-second-law
  mathematically_requires -> mass, acceleration, force
  applies_to -> point-mass, inertial-reference-frame
```

**Model:**
```
model: ideal-gas
  approximates -> real-gas-behavior
  part_of -> thermodynamic-system
```

## Alternatives Considered

- **Zero relations:** Rejected — destroys graph value, fails to test engine, violates VISION/ARCHITECTURE, produces disconnected explorer, adapter useless. Glossary is not knowledge foundation.
- **All 12 adopted relations:** Rejected — too permissive, includes `bridges`, `analogous_to`, `related_to`, `logically_requires` which are not needed for foundation and invite vague modeling.
- **Custom physics relations (e.g., `has_dimension`, `has_unit`):** Rejected — `has_unit` already exists as reserved but `expressed_in`/`has_unit` family is measurement, not needed if unit is field on quantity. Dimensions will be schema field via ADR-0024, not relation. Keep registry stable.
- **Use `requires` generic instead of `mathematically_requires`:** Rejected — `requires` is reserved, `mathematically_requires` is adopted and precise for physics (mathematical dependency vs logical).
- **Allow `related_to` as fallback:** Rejected for physics-core — R4 shows it's abused. For physics foundation, if you can't name precise relation, claim is not ready for canonical.

## Consequences

- Positive: Forces precise, reviewable claims; 150 connections become meaningful; cycle detection (dependency DAG) exercised; claim signatures deduplicate; explorer shows real prerequisite graph; adapter can do closure queries.
- Negative: Slightly higher authoring effort — must choose precise relation. Mitigated by 7-relation cheat sheet and examples in RELATIONSHIP-SPECIFICATION.md §2.1.1.
- Neutral: No registry change — all 7 already adopted. No schema bump. Policy enforcement only.

## Implementation

- Update RELATIONSHIP-SPECIFICATION.md §2.1.1 with minimal set table + physics examples
- Update CURATION-PROTOCOL.md §3.1 with physics evidence standards per family
- Create `scripts/physics_core_profile_check.py`
- Create `tests/curation/test_physics_core_profile.py`
- Add to CONTRIBUTING.md: "Physics-core: use only minimal set"

## Open Questions

- Should `appears_in_law` be kept or should we canonicalize only `mathematically_requires` direction? Proposal: keep both allowed but forbid duplicate pair with both relations (would be redundant). The check should warn if same source/target pair has both `mathematically_requires` and `appears_in_law` (same semantics opposite direction).
- Should `approximates` be required to have `context.regime` and `assumptions`? Yes per CURATION-PROTOCOL model family — ideal gas requires `classical`, `low-pressure`, etc.

## Status History

- 2026-09-21: PROPOSED
