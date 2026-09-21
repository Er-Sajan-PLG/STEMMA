# DECISION 0024 — STEM math layer: canonical LaTeX, symbol bindings, dimensions, unit references

- **Date:** 2026-09-04 (draft)
- **Status:** **PROPOSED — awaiting gate G-C (human approval).** Nothing in this record is
  enforced or backfilled until the status changes to `decided`; per plan v2 §1 the ADR then lands
  **together with** its validator rule and tests (E3.1 → E3.4).
- **Related:** ADR-0010 (equation/symbol/unit display fields), ADR-0016/0021 (`external_ids`),
  ADR-0017 (extension registry — current `dimensions`/`symbol_set` extensions), ADR-0023
  (`external_ids` first-class; `qudt:`/`ucum:` schemes), `docs/ARCHITECTURE-AUDIT-v1.0.md` (F4),
  `docs/STEMMA-IMPLEMENTATION-PLAN-v2.md` (E3.1–E3.6, gate G-C)

## Context (audit F4 — the subject-matter gap)

STEMMA is a *STEM* foundation, yet its mathematics is opaque to machines:

- `equation`, `symbol`, `unit` are free display strings (`"KE = ½·m·v²"`, `"KE or K"`,
  `"joule (J)"`). Nothing can parse, type-check, render, or cross-reference them.
- Dimensions exist on **one** entity — and on a *law* (`phys.newtons-second-law`,
  `extensions.dimensions: "M L T^-2"`), which is a type error: laws relate quantities; only
  quantities have dimensions.
- No symbol→quantity binding: the `m` in `KE = ½·m·v²` is not linked to `lhs:phys.mass`, so the
  graph cannot say *why* kinetic energy `mathematically_requires` mass (the E6.1 campaign has to
  rediscover this by reading text).
- There is exactly **one** `unit` entity in 224; `phys.acceleration` says
  `unit: metre per second squared (m/s²)` as prose.
- Consumers (tutoring UIs, AI agents) therefore re-derive or hallucinate the math.

Inventory today: 54 `quantity`, 11 `law`, 2 `equation`, 1 `unit` entities; 98
`mathematically_requires` edges.

## Decision (proposed)

### 1. Entity-level `math` object (canonical, optional, additive)

```yaml
math:
  equation:
    latex: "K = \\tfrac{1}{2} m v^{2}"          # canonical form; ONE per entity (variants → derived)
    form: definition | law | derived | identity   # what kind of statement this is
  symbol_bindings:                               # every free symbol in `latex` MUST be bound
    - {symbol: "K", quantity: lhs:phys.kinetic-energy, role: subject}
    - {symbol: "m", quantity: lhs:phys.mass}
    - {symbol: "v", quantity: lhs:phys.velocity}
  variants:                                      # optional non-canonical but common forms
    - {latex: "KE = \\tfrac{1}{2} m v^{2}", note: "school notation"}
```

- Allowed on `quantity`, `law`, `equation`, `model`. `symbol_bindings[].quantity` must resolve to a
  `quantity` entity (or a documented `constant:` — see §5).
- `role: subject` marks the quantity being defined (exactly one for `form: definition`).
- Symbols bound in `math.symbol_bindings` are the **machine truth**; the existing string fields
  `equation`, `symbol`, `unit` become **derived display** (regenerated from `math` + unit entities
  by a script, or kept as human-readable hints while the backfill is partial — the validator
  warns on mismatch, never errors, during the transition).

### 2. Dimensions on quantities (promoted from extension to schema)

```yaml
dimensions: {L: 2, M: 1, T: -2}       # ISQ base vector; omitted keys = 0; dimensionless = {}
```

- Keys restricted to the seven ISQ base dimensions **`L M T I Θ N J`** (length, mass, time,
  electric current, thermodynamic temperature, amount of substance, luminous intensity); integer or
  half-integer exponents. Allowed **only** on `type: quantity`. The
  `extensions.dimensions` string dimension is retired after backfill; the one existing use on a
  *law* is removed (fix of the F4 type error) and re-expressed as bindings on its quantities.
- Angle and solid angle are dimensionless (`{}`) per SI; a `kind:` string (e.g. `plane-angle`,
  `energy`, `torque`) disambiguates same-dimension quantities without inventing base dimensions.

### 3. Units become entities; `unit` becomes a reference

```yaml
# content/physics/units/metre-per-second-squared.md
id: lhs:unit.metre-per-second-squared
type: unit
name: metre per second squared
symbol: "m/s²"                        # display (string ok on unit entities)
dimensions: {L: 1, T: -2}
system: SI
external_ids: {qudt: M-PER-SEC2, ucum: "m/s2", wd: Q1051665}
```

- Quantities reference units by ID: `unit: lhs:unit.metre-per-second-squared` (new field name
  `unit_ref` during transition; `unit` string retained as derived display until E3.5).
- Unit definitions carry a `conversion:` block to their coherent SI unit (`{base: lhs:unit…,
  factor: 1000, offset: 0}`) — enough for dimensional reduction, not a full unit system (OUT).
- QUDT/UCUM codes go in `external_ids` (the ADR-0023 mechanism); STEMMA does not import either
  ontology.

### 4. Validator rules (land with `decided`; plan v2 E3.4)

| Rule | Severity |
|------|----------|
| Every free symbol in `math.equation.latex` has exactly one binding; every binding's symbol occurs in the LaTeX | error |
| `symbol_bindings[].quantity` resolves to a `quantity` entity (or registered constant) | error |
| `dimensions` only on `quantity`/`unit`; keys ⊆ `L M T I Θ N J`; exponents numeric | error |
| **Dimensional type-check**: for `form: definition|law|identity`, both sides of `=` reduce to the same dimension vector under the bindings' `dimensions` (supports `+ - * / ^ \frac \sqrt \tfrac \cdot`, numeric literals, bound symbols, bound constants; `\sin \cos \exp \ln` require dimensionless arguments) | error when all symbols are bound; **warning** while any binding lacks `dimensions` (partial backfill degrades gracefully) |
| `unit_ref` resolves to a `unit` entity whose `dimensions` equal the quantity's `dimensions` | error |
| `mathematically_requires` connection whose source has bindings: target must appear among the bound quantities (or a warning "edge not grounded in math") | warning (feeds E6.1) |

Parsing scope is a **deliberately small LaTeX subset** (the one above). Anything else (integrals,
tensors, differential operators) is stored, rendered, but **not type-checked** — flagged
`math.check: skipped` in derived output. CAS-level semantics remain deferred (plan v2 §5).

### 5. Constants

Physical constants (`G`, `c`, `k_B`, `e`, `h`) are `quantity` entities with `constant: true`,
`value`, `uncertainty`, `unit_ref`, and `external_ids: {codata: …, wd: …}` — bindings reference them
like any quantity. No separate constant registry.

### 6. Derived rendering (E3.5; not part of this gate's validator scope)

`exports/knowledge.json` gains, per entity with `math`, derived `math_render: {mathml: …,
plain: …}` produced by a build step. Never canonical; regenerable.

### 7. Backfill order (E3.2 / E3.3 — after `decided`)

1. Mechanics: 20 quantities + 5 laws + `equations-of-motion`; ~12 SI units created.
2. Electricity & magnetism, thermodynamics, waves.
3. Chemistry quantities (molarity, rate) and the math domain's `equation` entities.
Each backfill batch is `ai_drafted: true` until reviewed (E6.4 cadence); the validator only
promotes warnings to errors for entities whose bindings are complete.

## Alternatives considered

- **MathML as the canonical form** — rejected: verbose, hard to author/review by hand, and still
  needs bindings; MathML is a derived rendering (E3.5).
- **OpenMath / Content MathML** — deferred: semantically ideal, authoring cost too high for a
  hand-curated repo; the small LaTeX subset + bindings captures the same content for our checks.
- **Full unit ontology import (QUDT)** — rejected (plan v2 §1/§5): STEMMA stays independently
  authoritative; QUDT/UCUM are anchors via `external_ids`.
- **Keep dimensions as a string extension (`"M L T^-2"`)** — rejected: unparsable without a
  grammar, and the one use is on the wrong entity type.
- **Symbol bindings on connections instead of entities** — rejected: the binding is a property of
  the equation, not of a dependency edge; edges can be *derived* from bindings (the reverse is
  impossible).

## Consequences

- The graph gains a mechanical explanation for dependency edges (a binding *is* a
  `mathematically_requires` justification), which shrinks E6.1 review effort over time.
- Dimensional errors in content become CI failures instead of reader-caught mistakes.
- Consumers can render math faithfully and AI agents can ground symbol semantics.
- Cost: schema additions (`math`, `dimensions`, `unit_ref`, `constant`, unit-entity fields), a
  small LaTeX parser (~300 lines, no dependencies), the unit-entity backfill, and an
  `extension-registry.yaml` retirement of `dimensions`/`symbol_set`.
- Open questions for the gate (G-C):
  1. Field name during transition: `unit_ref` (this draft) vs overloading `unit` with an ID pattern.
  2. Half-integer exponents (needed for e.g. `√(L)` in some empirical laws) — allow or reject?
  3. Whether `equation` entities (`equations-of-motion`) may carry **multiple** canonical equations
     (`math.equations[]`) — this draft says one canonical + variants; SUVAT is four independent
     statements and argues for a list.
