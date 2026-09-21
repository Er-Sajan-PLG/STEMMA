# DECISION 0021 — Registry integrity: entity types, inverse coherence, vocabulary enforcement, data repairs

- **Date:** 2026-09-03
- **Status:** decided (implemented with this change; owner-directed activation of plan v2)
- **Related:** ADR-0012 (registry), ADR-0014 (inference), ADR-0016 (urgent metadata),
  `docs/ARCHITECTURE-AUDIT-v1.0.md` (findings F3, F6, F9, F11),
  `docs/STEMMA-IMPLEMENTATION-PLAN-v2.md` (E2.1–E2.7, E6.2)

## Context

The audit measured the registry — the semantic heart of the system — as its least-validated
component: 39 inverse-coherence defects (35 relations naming inverses that do not exist;
`appears_in_law` mis-paired with `contains`; asymmetric `part_of`/`has_part` domain/range);
domain/range referencing entity types that cannot exist; `misconception` able to participate
in no relation despite the specification saying it participates via `related_to`; controlled
vocabularies enforced by no script (194 context violations measured); ADR-0014's inference
exclusivity and ADR-0016's entity fields specified but unimplemented; and migration-fabricated
`context.regime: [classical]` boilerplate on 641 connections.

## Decision

1. **Entity type enum grows by three**: `phenomenon`, `model`, `experiment` (additive; the
   registry's domain/range already referenced them; zero existing entities change type).
   Type changes on existing entities remain forbidden (ADR-0004).
2. **Registry integrity is a validator invariant** (`check_registry_coherence`): every
   `inverse` names a defined relation, is mutual, and mirrors domain/range; symmetric
   relations carry no inverse; domain/range reference known entity types only.
3. **Registry repair** (`scripts/repair_registry.py`, idempotent): undefined inverse fields
   dropped; bogus `appears_in_law ↔ contains` pairing removed; missing inverse relations for
   adopted relations ADDED (`mathematically_required_by`, `logically_required_by`,
   `is_basis_of`, `governed_by`, `approximated_by`) so derived graph projections emit only
   legal names; unused relations marked `status: reserved` (37→47 reserved, 12 adopted);
   `misconception` added to `related_to` domain/range per specification §4.6; `limited_by`
   loses the phantom `regime` type. Registry version 0.2 → 0.3.
4. **Vocabulary enforcement**: `validate.py` checks `context.domain/subdomain/regime/scale`
   against `schema/vocabularies/`; vocabularies extended to match the existing content tree
   (physiology; 4 chemistry subdomains; `microscopic` scale); `context.domain: math`
   unified to `mathematics` (142 connections).
5. **Orphaned ADR rules implemented**: inference mutual exclusivity (ADR-0014),
   confidence↔basis pairing warning (ADR-0013), `lifecycle.replaced_by` and
   `deprecated_by` resolution, entity fields `version`, `updated_at`, `external_ids`
   (namespaced, multi-valued), `rights` (ADR-0016 entity half).
6. **Honest context data (E6.2)**: migration-method connections lose the fabricated
   `regime: [classical]` (now `regime: []`); human-curated regimes are untouched.
7. **Materialized inverse duplicates deprecated** (4 connections: conn.000434, 000435,
   000554, 000555): ADR-0012 forbids storing derived inverse edges; duplicates get
   `assertion.status: deprecated` + `lifecycle.replaced_by` pointing at the survivor.
   IDs are never reused.

## Alternatives considered

- Keep phantom types out of the enum and instead constrain the registry — rejected: the
  causal/explanatory/model/measurement families are unusable without `phenomenon`/`model`,
  and the audit's R20 named exactly this drift.
- Enforce vocabularies only for new data — rejected: the violations are mechanical naming
  drift, repairable now with zero semantic loss.
- Delete materialized-inverse connections — rejected: connection IDs are immutable records;
  deprecation with `replaced_by` preserves history (ADR-0011).

## Consequences

- The registry can no longer silently diverge from the schema or itself.
- Derived graph projections emit only legal relation names.
- Epistemic context fields mean something again (empty ≠ fabricated-classical).
- Adding a relation now requires: registry entry + (if adopted) coherent inverse + tests.
