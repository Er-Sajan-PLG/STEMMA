# PHYSICS-FIRST MINIMAL CANONICALIZATION — Implementation Plan

**Date:** 2026-09-21 (Kathmandu)
**Status:** PROPOSED — awaiting human activation
**Branch:** arena/01a0c072-stemma
**Related:** VISION.md, ROADMAP.md, DOMAIN-MODEL.md, SCHEMA-SPECIFICATION.md, RELATIONSHIP-SPECIFICATION.md, ADR-0024, ADR-0029, DEEP-DIVE-RECOMMENDATIONS.md R1/R3/R4

---

## 0. Executive Summary

All-STEM canonicalization fails not because the engine is impossible, but because **human review doesn't scale**. The engine (`validate.py` + 4 schemas + registry) is domain-agnostic and already green. The bottleneck is curation: 224 entities / 654 connections previously had 604 unreviewed, 599 without evidence, 371 lazy `related_to`.

**Proposal:** Reduce domain to **physics**, reduce schema usage to **minimal profile**, reduce relations to **7 adopted relations (not zero)**, and ship **foundation + governing laws + half major entities (~70 entities, ~150 connections)** as a vertical proof that the canonicalizing engine *does* work.

This document is the change-plan for every doc, roadmap, ADR, and schema artifact.

---

## 1. Thesis / Antithesis / Synthesis

| User Proposal | Verdict | Reason |
|---|---|---|
| Reduce domain to physics | **AGREE STRONGLY** | Physics has highest consensus, mathematized, curriculum-neutral. Aligns with VISION non-goal: "Depth over breadth". |
| Reduce schema properties | **AGREE with nuance** | `learning_objectives`, `real_world_applications`, `key_experiments`, `common_misconceptions` are bloat flagged in R1. For physics core, only use required + `symbol`/`equation`/`unit` + `external_ids`/`historical`. No schema break needed - just don't populate. Formal deprecation via ADR-0041 later. |
| Reduce relations to none | **DISAGREE - kill this** | Zero relations = glossary, not knowledge graph. Violates value proposition (ADR-0020 connections-only truth). Newton's law meaningless without `mathematically_requires` mass/acceleration. Minimal set = 7 adopted relations, not 0. |
| Foundation + governing laws + half major entities | **AGREE** | Define half as: mechanics + EM + thermo foundations. ~70 entities is reviewable in <2 weeks with 1 domain expert. |

**Synthesis:** Physics-core v0.1 = 70 entities, 150 connections, 7 relations, minimal profile, with ADR-0024 math layer partially activated.

---

## 2. Physics Core Taxonomy (What "half" means)

### 2.1 Subdomain Slicing
Use existing `schema/vocabularies/subdomains.yaml` physics entries, but activate only 3 for v0.1:

- `mechanics` (priority 1)
- `electricity-magnetism` (priority 2)
- `thermal-physics` (priority 3)
- DEFER: `waves-optics`, `atomic-nuclear`, `measurement-units` (units live under measurement but we will seed 20 anyway)

### 2.2 Entity Inventory v0.1 (70)

**Quantities - 28:**
- Base ISQ: length, mass, time, electric-current, thermodynamic-temperature, amount-substance, luminous-intensity (7)
- Mechanics derived: velocity, acceleration, force, momentum, angular-momentum, energy, kinetic-energy, potential-energy, work, power, pressure, density, frequency (13)
- EM derived: charge, voltage, resistance, capacitance, electric-field, magnetic-field (6)
- Thermo: heat, entropy (2)

**Units - 20:**
- SI base: metre, kilogram, second, ampere, kelvin, mole, candela
- Derived: newton, joule, watt, pascal, coulomb, volt, ohm, farad, tesla, hertz, metre-per-second, metre-per-second-squared, kilogram-per-cubic-metre

**Laws - 15:**
- Newton 1/2/3, gravitation, conservation: energy, momentum, angular-momentum, charge
- Maxwell: Gauss E, Gauss B, Faraday, Ampere-Maxwell
- Thermo: 1st law, 2nd law, ideal-gas-law

**Equations - 5:**
- `F=ma`, `KE=½mv²`, `p=mv`, `V=IR`, `PV=nRT` (as equation entities linking to laws)

**Concepts/Models/Phenomena - 7:**
- concept: inertia, field, system, reference-frame
- model: point-mass, ideal-gas
- phenomenon: free-fall

Total: 28+20+15+5+7 = 75 (buffer for 70 target)

### 2.3 Connection Inventory v0.1 (~150)

Pattern for each law:
```
law --mathematically_requires--> quantity (3-4 per law) = ~60
quantity --appears_in_law--> law (inverse pattern, derived but we store canonical direction) = we store only one direction; choose law->quantity for canonical
quantity --derived_from--> quantity (e.g., velocity derived_from length+time) = ~15
law --applies_to--> model/phenomenon = ~15
quantity --generalizes--> quantity (energy generalizes kinetic) = ~10
concept --part_of--> concept/model = ~5
model --approximates--> phenomenon = ~5
equation --derived_from--> law = ~5
```

Uses only adopted relations. Zero `related_to`.

---

## 3. Schema Minimalism

### 3.1 Minimal Profile Definition

**Required (gate-enforced):**
`id, type, name, domain, status, definition, provenance`

**Allowed for physics core:**
`symbol, equation, unit, external_ids, historical, examples (1 max)`

**Explicitly NOT used for physics core v0.1:**
`learning_objectives, real_world_applications, key_experiments, common_misconceptions` - leave absent/null. Documented as pedagogical bloat in R1. No breaking schema change yet; formal removal in ADR-0041 schema v2.0.

**Future (ADR-0024 activation):**
`math: {latex, symbol_bindings, variants}`, `dimensions: {L,M,T,I,Θ,N,J}`, `unit_ref: stemma:unit.xxx`, `constant: bool`

Rationale: Physics without symbol/equation/unit is prose. Those 3 are display strings today, machine truth tomorrow via ADR-0024.

### 3.2 Extension Registry Changes
- Retire `dimensions` string extension (proposed) - replaced by schema-level `dimensions` map per ADR-0024
- Retire `symbol_set` string - replaced by `math.symbol_bindings`
- Keep `domain_scope` but mark as not used for physics core (pure vs applied is implicit in type)

---

## 4. Relation Minimalism (Why Not Zero)

**Zero relations fails 4 invariants:**
1. ARCHITECTURE.md §4: Entity↔connection boundary - entities carry no relationships. If connections=0, no relationships exist at all.
2. RELATIONSHIP-SPECIFICATION.md §5: Graph invariants (cycles, domain/range) never exercised.
3. VISION.md: "concepts, quantities, laws, models, and the relationships between them" - relationships are in the tagline.
4. CONSUMERS.md: Adapter search + graph traversal useless with isolated nodes.

**Minimal adopted set for physics (7):**
| Relation | Family | Use in physics | Example |
|---|---|---|---|
| `mathematically_requires` | dependency | Law needs quantity | `newtons-second-law` requires `mass` |
| `derived_from` | derivation | Equation from law, quantity from quantity | `kinetic-energy` derived_from `energy` |
| `appears_in_law` | derivation | Quantity appears in law | `force` appears_in `newtons-second-law` (alternative direction to above, pick one canonical) |
| `applies_to` | derivation | Law applies to model | `newtons-second-law` applies_to `point-mass` |
| `generalizes` / `special_case_of` | hierarchical | Taxonomy | `energy` generalizes `kinetic-energy` |
| `part_of` | structural | Composition | `kinetic-energy` part_of `mechanical-energy` system |
| `approximates` | model | Model validity | `ideal-gas` approximates `real-gas-behavior` |

All are status=adopted in `relation-registry.yaml` v1.0.0, no ADR needed to use. We enforce via policy: physics-core PRs may only use these 7. `related_to` is banned for physics-core (WARNING becomes ERROR via custom check).

---

## 5. Document Changes Required - Every Doc

### 5.1 VISION.md
**Current:** "Foundational STEM knowledge: concepts, quantities, units, laws..." breadth-first.
**Change:** Add § "Depth-First Strategy" after Principles:
> VISION non-goal "Coverage of the whole of science" is operationalized as physics-first. We achieve depth in one domain (physics: mechanics, EM, thermo) before breadth across STEM. This validates the engine and review workflow with highest-consensus science.

Add to Non-goals: "Attempting all STEM at once - deferred until physics-core canonical >50%."

### 5.2 ROADMAP.md
**Current:** R1 review activation generic, R2 math layer generic.
**Change:** Rewrite R1/R2 as physics-core:

**R1 — Physics-Core Review Activation (NOW)**
- Ship 70 physics entities (mechanics+EM+thermo) with minimal profile
- 150 connections using 7-relation minimal set, zero `related_to`
- Source records: Halliday Resnick Walker 12th, Griffiths EM, etc. (5 records)
- Exit: 70 entities human_reviewed, 150 connections canonical, explorer shows connected DAG, adapter search returns physics graph.

**R2 — Math Layer Activation for Physics (NOW, partial ADR-0024)**
- Decide ADR-0024 with adjustments: allow `math.equations[]` list, half-integer exponents, `unit_ref`
- Implement validator: LaTeX subset parser + dimensional check
- Backfill mechanics 20 quantities + 5 laws + 12 units
- Exit: dimensional errors are CI failures.

Push old R1 (generic review) to R3, shift others down. Add Explicitly Not: other domains until physics-core exit.

### 5.3 ARCHITECTURE.md
**Current:** No mention of vertical slice.
**Change:** Add §2.5 "Reference Vertical Slice: physics-core":
> Architecture is validated by a physics-core vertical slice: content/physics/{mechanics,electricity-magnetism,thermal-physics}/, connections using minimal adopted set, export v2.1.0, explorer visualization. This slice proves gate, export, adapter, explorer chain with real science.

No architectural change - additive documentation.

### 5.4 DOMAIN-MODEL.md
**Current:** 9 entity types, identity model generic.
**Change:**
- Add §2.1 "Physics Entity Profile (Minimal)": required + allowed fields list as above.
- Add §2.2 "Physics Subdomain Taxonomy": mechanics, electricity-magnetism, thermal-physics as NOW; others LATER.
- Add §4.1 "Physics Modeling Patterns": 
  - Quantity pattern: definition + symbol + unit + dimensions + appears_in_law
  - Law pattern: definition + equation + mathematically_requires + applies_to
  - Unit pattern: symbol + dimensions + system SI + external_ids qudt/ucum/wd
- Add invariant: "Physics core uses only 7 adopted relations; related_to forbidden."

### 5.5 SCHEMA-SPECIFICATION.md
**Current:** Lists all optional fields as equal.
**Change:**
- Add §3.1 "Minimal Profile vs Full Envelope": minimal profile is required+symbol/equation/unit/external_ids/historical; other arrays (learning_objectives etc.) are deprecated for physics core, retained only for backward compat until schema v2.0.
- Document transition: `equation`/`symbol`/`unit` strings are derived display after ADR-0024; `math` object is canonical.
- Add open item: ADR-0041 will remove `learning_objectives` (breaking, schema major 2.0).

No schema file change in v0.1 - only documentation. Schema change in ADR-0041.

### 5.6 RELATIONSHIP-SPECIFICATION.md
**Current:** 12 adopted relations listed generically.
**Change:**
- Add §2.1.1 "Physics-Core Minimal Set": table of 7 relations with physics examples, domain/range enforcement.
- Add §6.1 "Evidence Standards for Physics-Core": 
  - structural/hierarchical: textbook definition (Halliday Resnick)
  - dependency: explicit derivation or equation
  - derivation: law text + equation
  - model: regime + assumptions required (classical, non-relativistic, etc.)
- Add rule: `related_to` in physics/ is WARNING that fails CI for physics-core PRs (custom script).

### 5.7 METADATA-SPECIFICATION.md
**Current:** Extensions dimensions as string.
**Change:**
- Mark `dimensions` string extension as deprecated, replaced by ADR-0024 `dimensions` map.
- Mark `symbol_set` as deprecated, replaced by `math.symbol_bindings`.
- Add §9.1 "Physics-Core Extension Policy": no new extensions without ADR-0040.

### 5.8 CURATION-PROTOCOL.md
**Current:** Generic evidence standards.
**Change:**
- Add §3.1 "Physics-Core Evidence Sufficiency":
  | Family | Minimum for physics canonical |
  |---|---|
  | dependency (mathematically_requires) | Textbook equation showing requirement + derivation |
  | derivation | Textbook law statement + equation |
  | hierarchical | Textbook taxonomy |
  | structural | Definition |
  | model | Stated regime (classical, ideal, etc.) + assumptions |
- Add §9 "Physics-Core Review Campaign": 70 entities prioritized by centrality: mass, length, time first, then force, energy, then laws. Worksheet generator `dependency_review_campaign.py` scoped to `domain=physics`.

### 5.9 GOVERNANCE.md
**Current:** NOW/LATER classification generic.
**Change:** Update §3 Scope discipline:
- NOW: physics-core v0.1 (mechanics, EM, thermo foundations), ADR-0024 partial activation, minimal profile
- LATER: other physics subdomains (waves-optics, atomic-nuclear), other STEM domains, multilingual
- OUT: curriculum mapping, grade tags (still forbidden)

### 5.10 IMPLEMENTATION-STATUS.md
**Current:** Claims 224 entities but actually 0 now.
**Change:** Reset to refoundation baseline + add physics-core track:
- Implemented: gate, schemas, registries, adapter, explorer (existing)
- Partially: physics-core 0/70 entities, 0/150 connections, math layer proposed
- Add new section "Physics-Core v0.1 Status": table with counts, driven by `status_truth.py` filtered to domain=physics.

### 5.11 PIPELINES.md / INGESTION.md / KNOWLEDGE-ACQUISITION.md
**Change:** Add physics ingestion pipeline:
> Source: Halliday Resnick Walker PDF -> `ingest.py` -> proposals -> human review -> canonical. No auto-canonicalization. Source records: `src.halliday-resnick-12th`, `src.griffiths-em-4th`, etc.

### 5.12 CONSUMERS.md
**Change:** Add physics-core consumer example:
```python
from stemma_adapter import Client
c = Client("exports/knowledge.json")
c.search("force", domain="physics") # returns force + its mathematically_requires closure
```

### 5.13 CONTRIBUTING.md / TESTING.md / VERSIONING.md / SECURITY... / SOURCES.md / STANDARDS.md / GLOSSARY.md
- CONTRIBUTING: Add physics-core contribution guide: minimal profile checklist.
- TESTING: Add `tests/curation/test_physics_core_profile.py` - enforces 7-relation limit + minimal fields.
- VERSIONING: Note physics-core does not bump export major; content growth is not breaking.
- SOURCES: Seed 5 physics textbooks as canonical sources.
- STANDARDS: Map physics minimal set to SKOS: generalizes=broader, special_case_of=narrower.
- GLOSSARY: Add physics-core terms: ISQ dimension, symbol binding.

### 5.14 docs/README.md
Add link to this plan as "Current Focus: Physics-First".

---

## 6. ADR Changes Required

### Existing ADRs to Amend (addendum, not rewrite)

- **ADR-0004 entity-model**: Addendum: physics-core uses subset of fields; pedagogical fields deprecated path documented in ADR-0041.
- **ADR-0010 entity-metadata-extension**: Addendum: `equation`/`symbol`/`unit` strings become derived display after ADR-0024; physics core is pilot.
- **ADR-0024 math-layer**: Move from PROPOSED to DECIDED with 3 adjustments from Deep-Dive R3: `math.equations[]` list, half-integer exponents allowed, `unit_ref` field. This is the physics enabler. Gate G-C human approval required.
- **ADR-0029 refoundation-baseline**: Addendum: baseline 3.0.0 + physics-core v0.1 as first vertical slice.

### New ADRs to Create

#### ADR-0040: Physics-First Minimal Canonicalization Strategy
- **Status:** PROPOSED
- **Context:** All-STEM breadth makes review impossible; engine works, curation doesn't scale.
- **Decision:** Depth-first: ship physics core (mechanics, EM, thermo) ~70 entities, ~150 connections, before other domains. Other domains LATER.
- **Consequences:** Roadmap R1/R2 rewritten, physics becomes reference implementation, other domains deferred, review load drops 80%.
- **Related:** VISION non-goals, ROADMAP, ADR-0029.

#### ADR-0041: Minimal Entity Profile and Deprecation of Pedagogical Fields
- **Status:** PROPOSED
- **Context:** R1 finds `learning_objectives` pedagogical, `real_world_applications` etc. bloat. 218/224 entities had them as LLM slop.
- **Decision:** Define minimal profile (required + symbol/equation/unit/external_ids/historical). Forbid `learning_objectives`, `real_world_applications`, `key_experiments`, `common_misconceptions` for physics core (absent, not null). Formal removal from schema in v2.0 (breaking) after physics-core proves value.
- **Alternatives:** Keep all fields (rejected: bloat), convert to extensions (rejected: noisy).
- **Consequences:** Schema stays additive now, breaking later; validator adds WARNING for physics/ entities using banned fields; docs updated.

#### ADR-0042: Minimal Relation Set for Physics Foundation
- **Status:** PROPOSED
- **Context:** 55 relations exist, 12 adopted, 371 `related_to` abused. Physics doesn't need all.
- **Decision:** Physics-core v0.1 may use only 7 adopted relations: `mathematically_requires`, `derived_from`, `appears_in_law`, `applies_to`, `generalizes`, `special_case_of`, `part_of`, `approximates` (7+1). `related_to` forbidden for physics core. Enforced by `test_physics_core_profile.py`.
- **Alternatives:** Zero relations (rejected: destroys graph value), all 12 adopted (rejected: too permissive), custom physics relations (rejected: registry already has them).
- **Consequences:** Forces precise modeling; proves registry sufficiency; makes review tractable.

#### ADR-0043 (optional): Physics-Core Source Policy
- **Status:** PROPOSED
- **Decision:** Canonical physics sources are 5 textbooks: Halliday Resnick Walker 12th, Griffiths EM 4th, Schroeder Thermal, etc. Each gets `sources/src.*.yaml` with full bibliographic data. All physics connections must cite one.

---

## 7. Schema / Registry / Vocabulary Changes

### schema/concept.schema.json
- **v0.1 (no break):** No change. Only documentation in SCHEMA-SPECIFICATION.md that minimal profile is recommended.
- **v2.0 (ADR-0041, breaking):** Remove `learning_objectives` from properties (or mark deprecated with description). Add `math`, `dimensions`, `unit_ref`, `constant` per ADR-0024. Bump `schema/VERSION.yaml` schema_version 1.1.0 -> 2.0.0.

### schema/extension-registry.yaml
- Mark `dimensions` and `symbol_set` as `status: deprecated` with note "replaced by ADR-0024 schema fields".
- No new extensions for physics core.

### schema/relation-registry.yaml
- No change to registry - 7 relations already adopted.
- Add comment header: "Physics-core minimal set: mathematically_requires, derived_from, appears_in_law, applies_to, generalizes, special_case_of, part_of, approximates. See ADR-0042."

### schema/vocabularies/subdomains.yaml
- No change - physics subdomains already defined. Document that v0.1 activates only 3.

### schema/id-domain-map.yaml
- No change - `phys` prefix already maps to `physics`.

### schema/VERSION.yaml
- v0.1: No bump (content growth only)
- v2.0: When ADR-0041 lands: schema_version 2.0.0, export_version 3.0.0 (breaking field removal)

---

## 8. Script / Test / CI Changes

### New scripts
- `scripts/physics_core_profile_check.py`: Validates content/physics/**/*.md uses only minimal fields + 7 relations. Used in CI as WARNING for now, ERROR for physics-core PRs.
- `scripts/seed_physics_core.py`: Generates 70 entity drafts from template + Halliday index (ai_drafted=true).

### Modified scripts
- `validate.py`: Add optional `--profile physics-core` flag that enforces ADR-0042.
- `curation_status.py`: Add filter `domain=physics` report.
- `status_truth.py`: Already supports domain counts; ensure README status block shows physics count.

### New tests
- `tests/curation/test_physics_core_profile.py`:
  - No physics entity has learning_objectives etc.
  - No physics connection uses related_to
  - Every physics law has >=2 mathematically_requires
  - Every quantity has symbol
  - No cycles in dependency edges
- `tests/registry/test_physics_minimal_relations.py`

### CI
- `.github/workflows/ci.yml`: Add step `python scripts/physics_core_profile_check.py --warn`

---

## 9. Content Seeding Plan (Implementation)

### Phase P0: Taxonomy & Templates (Day 1)
- Create `content/physics/mechanics/`, `electricity-magnetism/`, `thermal-physics/`, `measurement-units/` folders (already exist as .gitkeep)
- Create entity template `scripts/templates/physics_entity.md.j2` with minimal profile
- Create 5 source records in `sources/`:
  - `src.halliday-resnick-walker-12th`
  - `src.griffiths-intro-electrodynamics-4th`
  - `src.schroeder-thermal-physics`
  - `src.nist-si-brochure-9th`
  - `src.codata-2022`

### Phase P1: Foundation Quantities & Units (Day 2-3)
- 28 quantities + 20 units = 48 entities
- Each quantity: id `stemma:phys.<slug>`, type quantity, domain physics, subdomain mechanics/measurement-units, definition from HRW, symbol, unit string, external_ids wd+qudt, provenance ai_drafted=true, source_kind textbook
- Validate: `python3 scripts/validate.py` must pass

### Phase P2: Governing Laws & Equations (Day 4-5)
- 15 laws + 5 equations = 20 entities
- Each law: type law, equation display string, historical attribution (Newton 1687 etc.)
- Validate

### Phase P3: Connections - Minimal Graph (Day 6-8)
- 150 connections: use `connections/conn.000001.yaml` sequential
- Each: source law -> mathematically_requires -> quantity, with evidence textbook page locator, provenance human:reviewer.physics-001 (seed reviewer in agent-registry.yaml)
- Ensure no duplicate claim signatures
- Validate + check_id_immutability

### Phase P4: Review & Export (Day 9-10)
- Run `dependency_review_campaign.py --domain physics` to generate worksheet
- Human review: mark 70 entities human_reviewed, 150 connections reviewed->canonical with review_history
- `validate.py` regenerates `exports/knowledge.json` v2.1.0 with 70 entities
- Explorer: `npm --prefix explorer run dev` shows connected DAG
- Adapter test: search "force" returns closure

### Phase P5: Math Layer Activation (Day 11-15, needs ADR-0024 decision)
- Add `math.latex` + `symbol_bindings` + `dimensions` to 20 quantities + 5 laws
- Implement small LaTeX parser (300 lines) in `scripts/math_validate.py`
- Dimensional check: F=ma => [M L T^-2] = [M][L T^-2] passes
- Retire display strings to derived

---

## 10. Roadmap Rewrite (Proposed)

Replace ROADMAP.md with:

```
R1 — Physics-Core v0.1 (NOW, 2 weeks)
  70 entities, 150 connections, 7 relations, minimal profile, 5 sources
  Exit: verify_all green, explorer shows DAG, adapter search works, >50% canonical

R2 — Math Layer for Physics (NOW, 2 weeks, gated by ADR-0024 decision)
  LaTeX + bindings + dimensions + unit_ref, dimensional CI
  Exit: 20 quantities dimensionally checked

R3 — Physics-Core v0.2 (LATER, waves-optics + atomic-nuclear, +50 entities)
R4 — Second Domain (LATER, chemistry foundations, reuse pattern)
R5 — Interop & Publication (R4/R6 old)
R6 — Scale & Hardening
```

---

## 11. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Physics definitions contested (mass in relativity) | Use `context.regime: [classical]` + `assumptions: [non-relativistic, point-mass]`; note in definition that relativistic mass is separate entity |
| Zero relations temptation returns | Enforce via test_physics_core_profile.py ERROR |
| Schema minimalism loses info | Keep external_ids + historical; pedagogical fields are consumer responsibility per VISION |
| Review bottleneck still | 70 entities is 1 expert * 3 days; campaign worksheet makes it actionable |
| ADR-0024 decision stalls | Ship v0.1 with display strings, mark math as SEAM; v0.2 activates math |

---

## 12. Acceptance Criteria for Physics-Core v0.1

- `python3 scripts/verify_all.py` exit 0
- `exports/knowledge.json` has 70 physics entities, 150 connections, 5 sources, relation_registry embedded
- `python3 scripts/physics_core_profile_check.py` passes
- Explorer shows connected graph, not isolated dots
- Adapter: `curl /v2/search?q=force&domain=physics` returns force + requires mass, acceleration
- No physics entity has `learning_objectives` etc.
- No physics connection uses `related_to`
- All connections have >=1 evidence with source_ref
- Review: 100% entities human_reviewed, 100% connections canonical

---

## 13. Immediate Next Steps (for this branch)

1. Land ADR-0040, 0041, 0042 as PROPOSED in `docs/decisions/`
2. Update ROADMAP.md R1/R2 to physics-first
3. Update VISION.md with depth-first strategy paragraph
4. Update DOMAIN-MODEL.md with physics profile + modeling patterns
5. Update SCHEMA-SPECIFICATION.md with minimal profile section
6. Update RELATIONSHIP-SPECIFICATION.md with minimal set table
7. Create `scripts/physics_core_profile_check.py` + test
8. Seed 5 source records
9. Seed 10 pilot entities (mass, length, time, velocity, acceleration, force, energy, metre, second, kilogram) + 15 connections to prove chain
10. Run verify_all, commit, push to `arena/01a0c072-stemma`

---

## 14. Appendix: File Change Checklist

- [ ] docs/VISION.md - add depth-first
- [ ] docs/ROADMAP.md - rewrite R1/R2 physics-first
- [ ] docs/ARCHITECTURE.md - add §2.5 vertical slice
- [ ] docs/DOMAIN-MODEL.md - add physics profile
- [ ] docs/SCHEMA-SPECIFICATION.md - add minimal profile
- [ ] docs/RELATIONSHIP-SPECIFICATION.md - add minimal set
- [ ] docs/METADATA-SPECIFICATION.md - deprecate dimensions string
- [ ] docs/CURATION-PROTOCOL.md - add physics evidence standards + campaign
- [ ] docs/GOVERNANCE.md - NOW = physics core
- [ ] docs/IMPLEMENTATION-STATUS.md - add physics track
- [ ] docs/PIPELINES.md - add physics pipeline
- [ ] docs/CONSUMERS.md - add physics consumer example
- [ ] docs/CONTRIBUTING.md - add physics checklist
- [ ] docs/TESTING.md - add physics profile test description
- [ ] docs/SOURCES.md - list 5 physics textbooks
- [ ] docs/decisions/0040-physics-first-strategy.md - NEW
- [ ] docs/decisions/0041-minimal-entity-profile.md - NEW
- [ ] docs/decisions/0042-minimal-relation-set-physics.md - NEW
- [ ] schema/extension-registry.yaml - mark deprecated
- [ ] schema/relation-registry.yaml - add comment
- [ ] schema/VERSION.yaml - no bump yet
- [ ] scripts/physics_core_profile_check.py - NEW
- [ ] tests/curation/test_physics_core_profile.py - NEW
- [ ] content/physics/... - 70 new entities
- [ ] connections/ - 150 new connections
- [ ] sources/ - 5 new sources

---

**End of Plan**
