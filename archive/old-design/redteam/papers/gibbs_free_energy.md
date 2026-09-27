# Red Team Test Paper 2: Gibbs Free Energy - Cross-Disciplinary Notation & Uncertainty

**Title:** Thermodynamic Consistency of Gibbs Free Energy Definitions Across Physics, Chemistry, and Biology  
**Authors:** Cross-Disciplinary Working Group  
**Journal:** Journal of Chemical Physics (simulated)  
**Year:** 2023  
**DOI:** 10.1063/5.0123456  
**License:** CC BY 4.0  

---

## Abstract

The Gibbs free energy G = H - TS is a cornerstone of thermodynamics, yet its definition, notation, and interpretation differ significantly across physics, chemistry, and biology. We systematically compare definitions, identify sources of confusion, and propose a unified notation framework. Critical issues include: sign conventions for work, standard state definitions, activity vs. concentration, and the treatment of non-ideal systems.

---

## 1. Introduction

The Gibbs free energy determines spontaneity (ΔG < 0) and equilibrium (ΔG = 0). Yet its mathematical expression varies:

| Discipline | Standard Definition | Work Convention |
|------------|--------------------|-----------------|
| Physics (Thermodynamics) | G = U + pV - TS | Work done BY system is positive |
| Chemistry | G = H - TS | Work done ON system is positive (IUPAC) |
| Biology | G = G° + RT ln Q | Often uses concentration not activity |

These differences lead to sign errors, factor-of-RT errors, and miscommunication.

---

## 2. Mathematical Definitions

### 2.1 Fundamental Relation

**Equation 1 (Universal):**
$$G = U + pV - TS = H - TS$$

where U = internal energy, p = pressure, V = volume, T = temperature, S = entropy, H = U + pV = enthalpy.

### 2.2 Differential Form

**Equation 2 (Universal):**
$$dG = Vdp - SdT + \sum_i \mu_i dn_i$$

where μ_i = chemical potential of species i, n_i = amount of substance.

### 2.3 Chemical Potential

**Equation 3 (Physics/Chemistry standard):**
$$\mu_i = \mu_i^\circ + RT \ln a_i$$

where a_i = activity, μ_i° = standard chemical potential.

**Equation 3b (Biology - often uses concentration):**
$$\mu_i = \mu_i^\circ + RT \ln \left(\frac{c_i}{c^\circ}\right) \quad \text{(approximation)}$$

---

## 3. Cross-Disciplinary Conflicts

### 3.1 Work Sign Convention

| Convention | Physics (Clausius) | Chemistry (IUPAC) | Difference |
|------------|-------------------|-------------------|------------|
| Work done BY system | W > 0 | W < 0 | Sign flip |
| dU = δQ + δW | dU = δQ - δW | — | Sign flip |

**Impact:** In chemistry, dG = Vdp - SdT (work done ON system). In physics, often written with opposite sign for work terms.

### 3.2 Standard State Definitions

| Species | Chemistry (IUPAC) | Biology | Physics |
|---------|------------------|---------|---------|
| Solute | 1 mol/L (ideal) | 1 M | 1 mol/kg |
| Gas | 1 bar | 1 atm | 1 bar |
| Pure solid/liquid | Pure substance at 1 bar | Pure substance | Unit activity |
| Water (solvent) | Pure liquid at 1 bar | 55.5 M | Pure liquid |

**Equation 4 (Standard Gibbs energy of reaction):**
$$\Delta_r G^\circ = -RT \ln K$$

where K = equilibrium constant (activities). **CRITICAL:** K is dimensionless (activities), but biology often uses K_c with concentrations.

### 3.3 Activity vs Concentration

**Equation 5:**
$$a_i = \gamma_i \frac{c_i}{c^\circ}$$

where γ_i = activity coefficient, c_i = concentration, c° = standard concentration (1 M).

**Biology often assumes:** γ_i ≈ 1, a_i ≈ c_i/c° → introduces errors in non-ideal solutions (e.g., cellular cytoplasm).

### 3.4 Non-Ideal Systems

**Equation 6 (Debye-Hückel limiting law):**
$$\log_{10} \gamma_\pm = -A |z_+ z_-| \sqrt{I}$$

where I = ionic strength, A ≈ 0.509 (water, 25°C).

In biology, intracellular I ≈ 0.15-0.2 M → γ ≈ 0.75 for monovalent ions. **Neglecting this introduces ~0.7 kJ/mol error per ion.**

---

## 4. Uncertainty Quantification

### 4.1 Standard Gibbs Energies of Formation

| Species | Δ_f G° (kJ/mol) | Uncertainty | Source |
|---------|-----------------|-------------|--------|
| H₂O(l) | -237.13 | ±0.04 | NIST |
| ATP⁴⁻(aq) | -2761.9 | ±3.5 | Alberty 2003 |
| ADP³⁻(aq) | -1896.2 | ±3.0 | Alberty 2003 |
| H⁺(aq) | 0 (by definition) | — | Convention |
| Mg²⁺(aq) | -454.8 | ±0.5 | NIST |

**Critical:** ATP hydrolysis ΔG°' = -30.5 kJ/mol is often cited, but **this is at pH 7, [Mg²⁺] = 1 mM, I = 0.25 M**, not standard state.

**Equation 7 (Transformed Gibbs energy at specified pH, pMg):**
$$\Delta_r G'^\circ = \Delta_r G^\circ + RT \ln \left( \frac{[\text{H}^+]^n [\text{Mg}^{2+}]^m}{K_{\text{bind}}} \right)$$

### 4.2 Propagation of Uncertainty

For ATP hydrolysis: ATP⁴⁻ + H₂O → ADP³⁻ + HPO₄²⁻ + H⁺

| Component | ΔG° (kJ/mol) | Uncertainty |
|-----------|--------------|-------------|
| ATP⁴⁻ | -2761.9 | ±3.5 |
| ADP³⁻ | -1896.2 | ±3.0 |
| HPO₄²⁻ | -1088.3 | ±0.5 |
| H₂O | -237.1 | ±0.04 |
| **Sum** | **-30.5** | **±4.6** |

**The uncertainty (±4.6 kJ/mol) is 15% of the value.** Most textbooks cite -30.5 without uncertainty.

---

## 5. Cross-Disciplinary Entity Resolution

### 5.1 Same Concept, Different Names/Symbols

| Physics | Chemistry | Biology | Unified ID |
|---------|-----------|---------|------------|
| Gibbs free energy G | Gibbs energy G | Gibbs free energy ΔG | lhs:thermo.gibbs-free-energy |
| Chemical potential μ | Chemical potential μ | Chemical potential μ | lhs:thermo.chemical-potential |
| Activity a | Activity a | Concentration c (approx) | lhs:thermo.activity |
| Standard state (1 bar) | Standard state (1 bar, 1 M) | pH 7, 1 M, 37°C | lhs:thermo.standard-state |

### 5.2 Equation Notation Variants

| Form | Physics | Chemistry | Biology |
|------|---------|-----------|---------|
| ΔG = -RT ln K | ✓ | ✓ | Sometimes K_c |
| ΔG = ΔG° + RT ln Q | ✓ | ✓ | ✓ (often c not a) |
| ΔG = ΔH - TΔS | ✓ | ✓ | ✓ |

---

## 6. Contradictory Claims

### Claim 1: "ATP hydrolysis yields -30.5 kJ/mol"
- **Status:** CONTEXT-DEPENDENT
- **Evidence A:** Alberty (2003) ΔG°' = -30.5 kJ/mol at pH 7, [Mg²⁺]=1mM, I=0.25M
- **Evidence B:** NIST Δ_f G°(ATP⁴⁻) = -2761.9 ± 3.5 kJ/mol → ΔG° = -20.5 kJ/mol (different standard state)
- **Resolution:** Must specify standard state (pH, pMg, I, T)

### Claim 2: "ΔG = -RT ln K"
- **Status:** TRUE for dimensionless K (activities)
- **Evidence A:** IUPAC Gold Book - K is dimensionless
- **Evidence B:** Biology textbooks use K_c (concentrations) → dimensioned
- **Resolution:** K vs K_c distinction is critical

---

## 7. Historical Evolution

| Year | Development | Discipline |
|------|-------------|------------|
| 1873 | Gibbs "On the Equilibrium of Heterogeneous Substances" | Physics |
| 1923 | Lewis & Randall "Thermodynamics" | Chemistry |
| 1930s | Onsager reciprocal relations | Physics |
| 1960s | Alberty - biochemical thermodynamics | Biology |
| 1994 | IUPAC "Quantities, Units and Symbols" | Chemistry |
| 2019 | IUPAC "Green Book" 3rd ed. | Chemistry |

---

## 8. Recommendations

1. **Always specify standard state:** pH, pMg, I, T, P
2. **Use activities, not concentrations** (or state approximation)
3. **Report uncertainties** for all ΔG values
4. **Adopt unified notation:** G for Gibbs energy, μ for chemical potential
5. **Distinguish K (activities) from K_c (concentrations)**

---

## Equations Summary

| Eq | Expression | Domain |
|----|------------|--------|
| 1 | G = H - TS | Universal |
| 2 | dG = Vdp - SdT + Σμ_i dn_i | Universal |
| 3 | μ_i = μ_i° + RT ln a_i | Phys/Chem |
| 3b | μ_i = μ_i° + RT ln(c_i/c°) | Bio (approx) |
| 4 | Δ_r G° = -RT ln K | Universal |
| 5 | a_i = γ_i c_i/c° | Universal |
| 6 | log γ = -A|z+z-|√I | Electrochem |
| 7 | Δ_r G'° = Δ_r G° + RT ln([H⁺]ⁿ[Mg²⁺]ᵐ/K) | Biochem |

---

## References

1. Gibbs, J.W. 1873. "On the Equilibrium of Heterogeneous Substances"
2. Alberty, R.A. 2003. "Biochemical Thermodynamics"
3. IUPAC. 2019. "Green Book" 3rd ed.
4. NIST Standard Reference Database 69
5. Nelson, Cox, Lehninger "Principles of Biochemistry"