# DECISION 0041 — Minimal Entity Profile and Deprecation of Pedagogical Fields

- **Date:** 2026-09-21
- **Status:** PROPOSED — awaiting human activation, companion to ADR-0040
- **Related:** ADR-0004 (entity-model), ADR-0010 (entity-metadata-extension), ADR-0017 (adaptive extensions), SCHEMA-SPECIFICATION.md §3, DOMAIN-MODEL.md §2, DEEP-DIVE-RECOMMENDATIONS.md R1 (canonical vs pedagogy boundary), VISION.md Principle 1 (knowledge not curriculum)
- **Author:** arena/01a0c072-stemma

## Context (R1 - Canonical vs Pedagogy)

Pre-refoundation corpus had on 224 entities:
- `learning_objectives` on 218/224 (97%)
- `common_misconceptions` 220/224
- `real_world_applications` 220/224
- `key_experiments` 220/224

Generality test only checks for grade/curriculum/country scoping claims, not instructional-shaped fields. DEEP-DIVE R1 assessment:

- `common_misconceptions`, `real_world_applications`, `key_experiments` are defensible as knowledge-layer but bloat for minimal proof.
- `learning_objectives` is genuinely pedagogical: "what a learner should be able to do" is teaching intent, not scientific fact. Belongs to consumer (curriculum mapping), not canonical.

For physics core, definition + symbol + equation + unit is the whole value. Extra arrays are LLM slop that increases review load without machine value.

Current `concept.schema.json` allows all fields optional (except required 7). So we can enforce minimal profile via policy/test without breaking schema.

## Decision

### 1. Define Minimal Profile for Physics-Core v0.1

**Required (gate already):**
`id, type, name, domain, status, definition, provenance`

**Allowed for physics-core:**
- `symbol` (quantity/law)
- `equation` (law/equation, display string until ADR-0024)
- `unit` (quantity, display string until ADR-0024)
- `examples` (max 1, knowledge-layer illustration)
- `external_ids` (wd, qudt, ucum, doi)
- `historical` (stated_by, year)
- `aliases` (if needed for migration)
- `version`, `updated_at` (bookkeeping)

**Explicitly FORBIDDEN for physics-core v0.1 (absent, not null):**
- `learning_objectives`
- `real_world_applications`
- `key_experiments`
- `common_misconceptions`

Enforcement: `scripts/physics_core_profile_check.py` + `tests/curation/test_physics_core_profile.py` — WARNING now, ERROR for physics-core PRs.

### 2. Formal Deprecation Path (Schema v2.0 Breaking)

- **v0.1 (this ADR, no break):** Documentation only in SCHEMA-SPECIFICATION.md §3.1 "Minimal Profile vs Full Envelope". No JSON Schema change.
- **v2.0 (future, breaking, needs human gate):** Remove `learning_objectives` from `concept.schema.json` entirely. Keep `real_world_applications`, `key_experiments`, `common_misconceptions` but mark as deprecated in description, to be moved to extensions or removed after consumer impact analysis. Bump `schema/VERSION.yaml`: schema_version 1.1.0 → 2.0.0, export_version 2.1.0 → 3.0.0. Document in MIGRATIONS.md.

Rationale: Breaking change best done while corpus is 0 entities (now) or small (70), not after 500.

### 3. Future Canonical Fields (ADR-0024)

Minimal profile will gain after ADR-0024 decision:
- `math: {equation: {latex, form}, symbol_bindings: [{symbol, quantity, role}], variants}`
- `dimensions: {L,M,T,I,Θ,N,J}` map (promoted from extension string)
- `unit_ref: stemma:unit.xxx` (ID reference, not display string)
- `constant: bool` for physical constants

Existing `equation`/`symbol`/`unit` strings become derived display regenerated from `math` + unit entities.

## Alternatives Considered

- **Keep all fields:** Rejected — bloat, review burden, pedagogical leakage violates VISION Principle 1.
- **Convert all four to extension-registry:** Rejected — noisy, low value; extensions are for additive knowledge-layer dimensions, not for pedagogical fields. Better to remove.
- **Immediate schema breaking removal now:** Rejected — while ideal (corpus is 0), we need physics-core to prove value first; immediate break would require major bump before any content, confusing. Use policy enforcement first, schema break second.
- **Keep `common_misconceptions` as knowledge:** Considered — it IS knowledge-layer (false belief). But for physics minimal, we defer; misconceptions can be modeled as `misconception` entities with `contradicts` relation later, not as string array on quantity.

## Consequences

- Positive: Physics entities become 30% smaller, review focuses on definition + symbol + equation + unit correctness. Aligns with "small core, governed extension" principle. Reduces LLM slop.
- Negative: Consumers relying on `learning_objectives` from old export will break at v2.0 — but old corpus was 0 canonical entities human-reviewed, so impact is minimal. Mitigated by consumer notification in CONSUMERS.md.
- Neutral: No immediate schema break; validation still passes if someone adds banned fields outside physics/ (other domains LATER may still use them until v2.0).

## Implementation

- Update SCHEMA-SPECIFICATION.md §3.1 with minimal profile table
- Update DOMAIN-MODEL.md §2.1 with physics entity profile
- Create `scripts/physics_core_profile_check.py`
- Create `tests/curation/test_physics_core_profile.py`
- Add CI step advisory
- Update CONTRIBUTING.md checklist: "For physics/, use minimal profile"

## Open Questions for Human Gate

- Should `real_world_applications` and `key_experiments` be kept as optional knowledge-layer for physics? This ADR says no for v0.1, but could allow 1 each. Decision needed.
- Should `examples` be allowed? Yes, max 1, to illustrate concept without pedagogy.

## Status History

- 2026-09-21: PROPOSED
