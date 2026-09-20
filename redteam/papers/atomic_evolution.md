# Red Team Test Paper 3: Historical Evolution with Competing Models - Atomic Structure

**Title:** From Dalton to Quantum Mechanics: The Evolution of Atomic Theory and Competing Models  
**Authors:** History of Science Working Group  
**Journal:** Physics in Perspective (simulated)  
**Year:** 2023  
**DOI:** 10.1007/s00016-023-00345-6  
**License:** CC BY 4.0  

---

## Abstract

Atomic theory has undergone radical transformations from Dalton's indivisible atoms to quantum mechanical orbitals. Each model was considered "canonical" in its time, then superseded. We trace this evolution, highlighting where competing models coexisted, how evidence accumulated, and how the community resolved (or failed to resolve) disagreements. Key transitions: indivisible → plum pudding → nuclear → Bohr → quantum mechanical → quantum field theory.

---

## 1. Timeline of Atomic Models

| Period | Model | Key Proponents | Key Evidence | Status |
|--------|-------|----------------|--------------|--------|
| 1803-1897 | **Dalton's Indivisible Atoms** | Dalton | Law of multiple proportions | Superseded |
| 1897-1909 | **Plum Pudding** | Thomson | Cathode rays (electrons) | Superseded |
| 1909-1913 | **Rutherford Nuclear** | Rutherford, Geiger, Marsden | Gold foil scattering | Superseded |
| 1913-1925 | **Bohr Model** | Bohr | Hydrogen spectrum | Superseded |
| 1925-1930 | **Quantum Mechanics** | Heisenberg, Schrödinger, Dirac | Matrix/wave mechanics | Current (non-rel) |
| 1930-present | **QFT/QED** | Dirac, Feynman, Schwinger | Lamb shift, g-2 | Current (rel) |

---

## 2. Competing Models During Transitions

### 2.1 Thomson vs. Kelvin (1897-1904)

**Thomson's Plum Pudding:** Electrons embedded in positive sphere  
**Kelvin's Vortex Atoms:** Atoms as knotted vortices in ether

**Evidence for Thomson:** Cathode ray deflection (e/m measurement)  
**Evidence for Kelvin:** Stability, periodicity explained by knot topology  
**Resolution:** Thomson's model won due to quantitative e/m; Kelvin's lacked predictive power

### 2.2 Rutherford vs. Thomson (1909-1913)

**Rutherford's Nuclear Model:** Tiny dense nucleus, electrons orbiting  
**Thomson's Modified Plum Pudding:** Multiple rings of electrons

**Key Experiment:** Geiger-Marsden gold foil scattering (1909)

**Equation 1 (Rutherford scattering cross-section):**
$$\frac{d\sigma}{d\Omega} = \left(\frac{Z_1 Z_2 e^2}{16\pi\epsilon_0 E}\right)^2 \frac{1}{\sin^4(\theta/2)}$$

**Observation:** ~1 in 8000 α-particles scattered at >90° → impossible for plum pudding

### 2.3 Bohr vs. Classical Mechanics (1913-1925)

**Bohr Model:** Quantized angular momentum L = nħ, discrete orbits  
**Classical Expectation:** Orbiting electrons should radiate and spiral in

**Equation 2 (Bohr energy levels):**
$$E_n = -\frac{m e^4}{8\epsilon_0^2 h^2 n^2} = -\frac{13.6 \text{ eV}}{n^2}$$

**Conflict:** Bohr model worked for H but failed for He, violated uncertainty principle

**Competing Model:** Bohr-Sommerfeld (elliptical orbits, azimuthal quantum number)

---

## 3. Evidence Evolution

### 3.1 Spectral Lines

| Model | Explains H Spectrum? | Explains He Spectrum? | Fine Structure? | Zeeman Effect? |
|-------|---------------------|----------------------|-----------------|----------------|
| Dalton | ✗ | ✗ | ✗ | ✗ |
| Plum Pudding | ✗ | ✗ | ✗ | ✗ |
| Rutherford | ✗ | ✗ | ✗ | ✗ |
| Bohr | ✓ | ✗ | ✗ | Partial |
| Bohr-Sommerfeld | ✓ | Partial | ✓ | ✓ |
| QM (Schrödinger) | ✓ | ✓ | ✓ | ✓ |
| QED | ✓ | ✓ | ✓ | ✓ (anomalous g-factor) |

### 3.2 Key Experiments That Killed Models

| Experiment | Year | Killed Model | Surviving Model |
|------------|------|--------------|-----------------|
| Cathode rays (e/m) | 1897 | Dalton indivisible | Plum pudding |
| Gold foil scattering | 1909 | Plum pudding | Nuclear |
| Stark effect | 1913 | Simple Bohr | Bohr-Sommerfeld |
| Compton scattering | 1923 | Classical waves | Photon/QM |
| Davisson-Germer | 1927 | Classical particles | Wave mechanics |
| Lamb shift | 1947 | Non-rel QM | QED |

---

## 4. Unresolved Disagreements During Transitions

### 4.1 Wave-Particle Duality (1923-1927)

**Debate:** Is light/electron wave or particle?

| View | Proponents | Evidence |
|------|------------|----------|
| Wave | Schrödinger, de Broglie | Davisson-Germer, interference |
| Particle | Einstein, Compton | Photoelectric, Compton |
| **Synthesis (1927):** Complementarity (Bohr) - both, but not simultaneously |

### 4.2 Matrix vs Wave Mechanics (1925-1926)

**Heisenberg-Born-Jordan:** Matrix mechanics (non-commutative algebra)  
**Schrödinger:** Wave equation (differential equations)

**Equation 3 (Heisenberg uncertainty):**
$$\Delta x \Delta p \geq \frac{\hbar}{2}$$

**Equation 4 (Schrödinger equation):**
$$i\hbar \frac{\partial \psi}{\partial t} = \left(-\frac{\hbar^2}{2m}\nabla^2 + V\right)\psi$$

**Resolution (1926):** Schrödinger proved equivalence; Dirac unified with transformation theory

---

## 5. Canonical Entities and Their Evolution

### 5.1 Entity Lineage

```
lhs:chem.atom (Dalton, 1803)
    ↓ supersedes
lhs:chem.atom.plum-pudding (Thomson, 1897)
    ↓ supersedes
lhs:chem.atom.nuclear (Rutherford, 1911)
    ↓ supersedes
lhs:chem.atom.bohr (Bohr, 1913)
    ↓ supersedes
lhs:chem.atom.quantum-mechanical (Schrödinger, 1926)
    ↓ supersedes
lhs:chem.atom.qft (Dirac/Feynman, 1930+)
```

### 5.2 Relationships That Change

| Relationship | Dalton | Thomson | Rutherford | Bohr | QM |
|--------------|--------|---------|------------|------|-----|
| atom → electron | N/A | part_of | part_of | part_of | part_of |
| electron → atom | N/A | part_of | part_of | part_of | part_of |
| atom → nucleus | N/A | N/A | part_of | part_of | part_of |
| nucleus → proton | N/A | N/A | N/A | N/A | part_of |
| nucleus → neutron | N/A | N/A | N/A | N/A | part_of (1932) |

---

## 6. Uncertainty and Disagreement in Current Model

### 6.1 Interpretational Disagreements (QM)

| Interpretation | Proponents | Key Difference |
|----------------|------------|----------------|
| Copenhagen | Bohr, Heisenberg | Wavefunction collapse |
| Many-Worlds | Everett, Deutsch | No collapse, all outcomes realized |
| Bohmian | Bohm, Bell | Hidden variables, particles have trajectories |
| QBism | Fuchs, Schack | Quantum states are beliefs |

**Status:** All make identical predictions; no experiment distinguishes them.

### 6.2 Beyond Standard Model (QFT)

| Problem | Competing Solutions |
|---------|-------------------|
| Hierarchy | Supersymmetry, composite Higgs, extra dimensions |
| Dark Matter | WIMPs, axions, sterile neutrinos, primordial BHs |
| Neutrino Mass | Seesaw mechanism, Dirac vs Majorana |

**Status:** No consensus; all untested at accessible energies.

---

## 7. Contradictory Evidence Cases

### Case 1: Neutron Discovery (1932)

**Before 1932:** Nucleus = protons + electrons (to explain charge/mass ratio)  
**Contradiction:** Electron in nucleus violates uncertainty principle (ΔxΔp too small)  
**Resolution:** Chadwick discovers neutron → nucleus = protons + neutrons

### Case 2: Parity Violation (1956-1957)

**Before 1957:** Parity conservation assumed universal  
**Lee-Yang proposal:** Weak force violates parity  
**Wu experiment (1957):** Co-60 beta decay shows asymmetry  
**Result:** Parity violated in weak interaction; Nobel 1957

### Case 3: CP Violation (1964)

**Before 1964:** CP symmetry assumed  
**Cronin-Fitch experiment:** K⁰ → 2π decay violates CP  
**Result:** CP violated; Kobayashi-Maskawa 3-generation model (1973)

---

## 8. Current Open Questions

| Question | Competing Views | Evidence Needed |
|----------|----------------|-----------------|
| QM Interpretation | Copenhagen vs Many-Worlds vs Bohm | Experimental test of macroscopicity |
| Dark Matter | WIMPs vs Axions vs Primordial BHs | Direct detection, structure formation |
| Neutrino Mass | Dirac vs Majorana | Neutrinoless double beta decay |
| Proton Decay | GUTs predict, SM forbids | Hyper-Kamiokande, DUNE |
| Quantum Gravity | String Theory vs LQG vs Asymptotic Safety | Planck-scale physics |

---

## 9. Lessons for Canonical Knowledge Systems

1. **Models have lifecycles:** Every "canonical" model was once contested
2. **Supersession ≠ deletion:** Old models preserved with `supersedes`/`superseded_by`
3. **Evidence is cumulative:** Each model explained more evidence than predecessor
4. **Disagreement is productive:** Competing models drive better experiments
4. **Uncertainty is structural:** Not all disagreement resolves (QM interpretations)
5. **Cross-disciplinary notation:** Different fields used different math for same physics

---

## References

1. Dalton, J. 1803. "New System of Chemical Philosophy"
2. Thomson, J.J. 1897. "Cathode Rays"
3. Rutherford, E. 1911. "Scattering of α and β Particles"
4. Bohr, N. 1913. "On the Constitution of Atoms and Molecules"
5. Heisenberg, W. 1925. "Quantum-Theoretical Re-interpretation"
6. Schrödinger, E. 1926. "Quantization as Eigenvalue Problem"
7. Dirac, P.A.M. 1930. "Principles of Quantum Mechanics"
8. Feynman, R.P. 1948. "Space-Time Approach to QED"