# PHYSICS GOVERNING LAWS — Guiding Point and Verification Tool

**Status:** Authoritative for physics domain (ADR-0040/0043). This is the deterministic governing point that decides what goes where, without relying on LLM reasoning.
**Related:** `schema/physics-governing-registry.yaml` (machine-readable), `docs/DOMAIN-MODEL.md` §8, `scripts/physics_governing_check.py`, `AGENTS.md` entity addition protocol.

> **Principle:** Every physics entity must be governed by at least one law of physics. The entity does not exist in isolation — it exists because a law requires it, defines it, or constrains it. This document is the verification tool: if you cannot name the governing law, the entity does not belong.

---

## 1. Why Governing Laws, Not LLM Reasoning

LLMs hallucinate and vary by model/version. Different models will place `entropy` in mechanics vs thermal-physics inconsistently. To avoid inconsistency over time, we use deterministic governing laws as ground truth:

- **What goes where:** Subdomain is decided by which governing law requires the entity. `mass` → mechanics because Newton's Second Law governs it. `charge` → electricity-magnetism because Maxwell governs it.
- **Verification:** Every entity must list `governed_by: [stemma:phys.xxx]` in its frontmatter or via connection `governed_by` / `applies_to` / `mathematically_requires`. If missing, profile check fails.
- **Embedded:** Governing laws are embedded in `schema/physics-governing-registry.yaml` and in this doc, not in model weights. Same in 2026 or 2030.

---

## 2. The Governing Laws (Physics)

### 2.1 Universal Conservation Laws (Govern All Domains)

| ID | Law | Governs | Equation | Domain |
|---|---|---|---|---|
| `stemma:phys.conservation-energy` | Conservation of Energy | energy, work, heat, kinetic-energy, potential-energy | ΔE=0 isolated | all |
| `stemma:phys.conservation-momentum` | Conservation of Momentum | momentum, impulse | Σp=const | mechanics |
| `stemma:phys.conservation-angular-momentum` | Conservation Angular Momentum | angular-momentum, torque | ΣL=const | mechanics |
| `stemma:phys.conservation-charge` | Conservation of Charge | charge, current | ΣQ=const | electricity-magnetism |
| `stemma:phys.conservation-mass-energy` | Mass-Energy Equivalence (relativistic limit) | mass, energy | E=mc² | atomic-nuclear |

**Verification rule:** Any quantity that appears in conservation law must have dimensions consistent with that law. Energy always [M L² T⁻²].

### 2.2 Classical Mechanics (Governs `mechanics` subdomain)

| ID | Law | Governs | Equation | Regime |
|---|---|---|---|---|
| `stemma:phys.newtons-first-law` | Newton's First Law (Inertia) | inertia, reference-frame, force, mass | F_net=0 → a=0 | classical, inertial |
| `stemma:phys.newtons-second-law` | Newton's Second Law | force, mass, acceleration, momentum | F_net = m·a = dp/dt | classical, non-relativistic |
| `stemma:phys.newtons-third-law` | Newton's Third Law | force, interaction | F_AB = -F_BA | classical |
| `stemma:phys.newtons-law-gravitation` | Newton's Law of Gravitation | gravitational-force, mass, distance | F = G·m1·m2/r² | classical, weak-field |
| `stemma:phys.work-energy-theorem` | Work-Energy Theorem | work, kinetic-energy, energy | W = ΔK | classical |
| `stemma:phys.impulse-momentum-theorem` | Impulse-Momentum Theorem | impulse, momentum, force, time | J = Δp | classical |

**What goes in `mechanics`:**
- Quantities: mass, length, time, velocity, acceleration, force, momentum, angular-momentum, energy, kinetic-energy, potential-energy, work, power, impulse, torque, pressure, density, frequency
- Units: kilogram, metre, second, newton, joule, watt, pascal, hertz, metre-per-second, metre-per-second-squared
- Concepts: inertia, reference-frame, system, point-mass, rigid-body
- Models: point-mass, ideal-spring, free-fall

**Verification rule:** Any mechanics quantity must have dimensions that can be expressed as combination of M, L, T only (no I, Θ). If it has I (current), it belongs in EM, not mechanics.

### 2.3 Electromagnetism (Governs `electricity-magnetism` subdomain)

| ID | Law | Governs | Equation | Regime |
|---|---|---|---|---|
| `stemma:phys.coulombs-law` | Coulomb's Law | charge, electric-force, distance | F = k·q1·q2/r² | electrostatic |
| `stemma:phys.gauss-law-electric` | Gauss's Law (Electric) | electric-field, charge, flux | ∮E·dA = Q/ε₀ | classical |
| `stemma:phys.gauss-law-magnetic` | Gauss's Law (Magnetic) | magnetic-field, flux | ∮B·dA = 0 | classical |
| `stemma:phys.faraday-law` | Faraday's Law | electric-field, magnetic-field, time | ∮E·dl = -dΦ_B/dt | classical |
| `stemma:phys.ampere-maxwell-law` | Ampère-Maxwell Law | magnetic-field, current, electric-field | ∮B·dl = μ₀(I + ε₀dΦ_E/dt) | classical |
| `stemma:phys.lorentz-force-law` | Lorentz Force Law | force, charge, electric-field, magnetic-field, velocity | F = q(E + v×B) | classical |
| `stemma:phys.ohms-law` | Ohm's Law | voltage, current, resistance | V = I·R | linear materials |

**What goes in `electricity-magnetism`:**
- Quantities: charge, current, voltage, resistance, capacitance, electric-field, magnetic-field, electric-flux, magnetic-flux
- Units: coulomb, ampere, volt, ohm, farad, tesla, weber
- Concepts: field, electric-charge, electric-current
- Models: point-charge, ideal-conductor

**Verification rule:** Any EM quantity must have dimension involving I (electric current) or be derived from I. If dimensions are only M,L,T, it belongs in mechanics.

### 2.4 Thermodynamics (Governs `thermal-physics` subdomain)

| ID | Law | Governs | Equation | Regime |
|---|---|---|---|---|
| `stemma:phys.zeroth-law-thermodynamics` | Zeroth Law | temperature, thermal-equilibrium | If A~B and B~C then A~C | equilibrium |
| `stemma:phys.first-law-thermodynamics` | First Law | internal-energy, heat, work, energy | ΔU = Q - W | all |
| `stemma:phys.second-law-thermodynamics` | Second Law | entropy, heat, temperature | ΔS ≥ 0 isolated | all |
| `stemma:phys.ideal-gas-law` | Ideal Gas Law | pressure, volume, temperature, amount, ideal-gas | PV = nRT | ideal gas, classical |
| `stemma:phys.kinetic-theory` | Kinetic Theory | pressure, temperature, kinetic-energy, mass | PV = (1/3)Nm<v²> | ideal gas |

**What goes in `thermal-physics`:**
- Quantities: temperature, heat, internal-energy, entropy, pressure (shared with mechanics but governed by thermo here), volume
- Units: kelvin, joule (shared), pascal (shared)
- Concepts: thermal-equilibrium, ideal-gas, thermodynamic-system
- Models: ideal-gas

**Verification rule:** Thermo quantities involve Θ (temperature) or N (amount) or are energy with thermal context.

### 2.5 Measurement & Units (Governs `measurement-units` subdomain)

| ID | Law | Governs | Equation |
|---|---|---|---|
| `stemma:phys.si-definitions` | SI Base Definitions | all base units | 7 base units defined by constants |
| `stemma:phys.dimensional-analysis` | Dimensional Homogeneity Principle | all quantities | Both sides of equation must have same dimensions |

**What goes in `measurement-units`:**
- All unit entities: kilogram, metre, second, ampere, kelvin, mole, candela, newton, joule, watt, pascal, coulomb, volt, ohm, farad, tesla, hertz, etc.
- No quantities, only units (type=unit)

**Verification rule:** Every unit must have dimensions map {L,M,T,I,Θ,N,J} and must match dimension of quantity it measures. Every quantity's unit must have same dimensions.

---

## 3. Governing Mapping — What Goes Where (Deterministic)

```
Subdomain → Governing Laws → Allowed Quantity Dimensions → Example Entities

mechanics → [newtons-first, second, third, gravitation, work-energy, impulse-momentum, conservation-momentum, conservation-energy]
          → Dimensions: M, L, T, M L T⁻², M L² T⁻², etc. (no I, no Θ)
          → Entities: mass, length, time, velocity, acceleration, force, momentum, energy, work, power

electricity-magnetism → [coulomb, gauss E, gauss B, faraday, ampere-maxwell, lorentz, conservation-charge]
                      → Dimensions: must include I or Q (charge) = I T
                      → Entities: charge, current, voltage, electric-field, magnetic-field

thermal-physics → [zeroth, first, second, ideal-gas, kinetic-theory]
                → Dimensions: must include Θ or N or be energy in thermal context
                → Entities: temperature, heat, entropy, internal-energy

measurement-units → [si-definitions, dimensional-analysis]
                  → All units, dimensions must match quantity
```

**Decision procedure for new entity (no LLM):**
1. What law defines or requires this entity? Find in table above.
2. Law's subdomain = entity's subdomain.
3. Law's dimensions = entity's dimensions must be compatible.
4. If no law in table governs it, entity does NOT belong in physics-core v0.1 (defer).

Example: `velocity` → defined as rate of change of length, required by Newton's Second Law (needs acceleration which needs velocity) → governing law = newtons-second-law → subdomain = mechanics → dimensions L T⁻¹ → valid.

Example: `entropy` → governed by second-law → subdomain thermal-physics → dimensions L² M T⁻² Θ⁻¹? Actually J/K → M L² T⁻² Θ⁻¹ → valid.

---

## 4. Embedded Governing Laws — Where Laws Live

Laws are embedded in three places (triple redundancy for verification):

**A. This document** — human-readable table above, guiding point.

**B. Machine-readable registry** — `schema/physics-governing-registry.yaml`:
```yaml
governing_laws:
  - id: stemma:phys.newtons-second-law
    subdomain: mechanics
    governs_quantities: [mass, force, acceleration, momentum]
    dimensions: {M: 1, L: 1, T: -2} for force, etc.
    regime: [classical, non-relativistic, inertial]
    equation: "F_net = m*a"
```

**C. As entities themselves** — each governing law is also a canonical entity in `content/physics/...` with full provenance + historical timeline (e.g., `content/physics/mechanics/newtons-second-law.md`). So law entity both IS the law and GOVERNS other entities.

**D. In entity frontmatter** — each entity lists `governed_by`:
```yaml
governed_by:
  - stemma:phys.newtons-second-law
  - stemma:phys.conservation-energy
```
Or via connection: `entity --governed_by--> law` or `law --applies_to--> entity` or `law --mathematically_requires--> quantity`.

This way, verification does not rely on LLM reasoning — it checks `governed_by` against registry.

---

## 5. Verification Tool — Deterministic Checks (No LLM)

`scripts/physics_governing_check.py` implements:

1. **Subdomain check:** Entity's subdomain must match subdomain of its governing law(s) from registry.
2. **Dimension check:** Entity's dimensions (if present) must be compatible with governing law's allowed dimensions.
3. **Governing law existence:** Every physics entity must have at least one `governed_by` entry that resolves to a law in registry.
4. **Law entity check:** Every governing law id in registry must have a corresponding entity file in `content/physics/` with type=law and historical timeline.
5. **Circular check:** No law governs itself.

This is deterministic, no model reasoning, same result in 2026 or 2030.

---

## 6. How to Use as Guiding Point

When adding new entity:
1. Open this doc, find which law governs it.
2. If not in table, propose new law via ADR — don't invent subdomain.
3. Set entity's `subdomain` = law's subdomain.
4. Set `governed_by` = law id.
5. Ensure dimensions compatible.
6. Add connection `law --mathematically_requires--> quantity` or `quantity --governed_by--> law`.

This ensures time of addition doesn't matter — same governing laws produce same placement.

---

**End of Governing Laws**
