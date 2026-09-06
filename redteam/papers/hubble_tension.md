# Red Team Test Paper 1: Contradictory Findings in Dark Energy

**Title:** Tension in the Hubble Constant: Contradictory Evidence from CMB and Local Measurements  
**Authors:** A. Riess et al. (SH0ES), N. Aghanim et al. (Planck)  
**Journal:** Nature Astronomy (simulated)  
**Year:** 2023  
**DOI:** 10.1038/s41550-023-01890-x  
**License:** CC BY 4.0 (simulated open access)  

---

## Abstract

We report a persistent 5.3σ tension between the Hubble constant measured from the cosmic microwave background (CMB) under ΛCDM and direct local measurements using the distance ladder. The Planck 2018 CMB data yields H₀ = 67.4 ± 0.5 km/s/Mpc, while the SH0ES Cepheid-supernova distance ladder gives H₀ = 73.04 ± 1.04 km/s/Mpc. This discrepancy cannot be explained by known systematics in either measurement. We present evidence both supporting and challenging the reality of this tension, and discuss implications for cosmology.

---

## 1. Introduction

The Hubble constant H₀ is the proportionality constant in Hubble's law: v = H₀d, where v is recession velocity and d is proper distance. Its value determines the age, size, and expansion history of the universe. Two independent precision measurements now disagree at the 5.3σ level:

**Planck CMB (ΛCDM):** H₀ = 67.4 ± 0.5 km/s/Mpc [Aghanim et al. 2018]  
**SH0ES Distance Ladder:** H₀ = 73.04 ± 1.04 km/s/Mpc [Riess et al. 2022]

This tension is widely considered the most significant crisis in modern cosmology.

---

## 2. Evidence Supporting the Tension

### 2.1 CMB Measurement (Planck)

The Planck satellite measured CMB temperature and polarization anisotropies with unprecedented precision. Under the standard ΛCDM model with 6 parameters:

| Parameter | Value | Description |
|-----------|-------|-------------|
| H₀ | 67.4 ± 0.5 km/s/Mpc | Hubble constant |
| Ωₘ | 0.315 ± 0.007 | Matter density |
| Ω_Λ | 0.685 ± 0.007 | Dark energy density |
| σ₈ | 0.811 ± 0.006 | Fluctuation amplitude |

**Equation 1:** The CMB power spectrum constrains the angular scale of the sound horizon:
$$\theta_* = \frac{r_s(z_*)}{D_A(z_*)}$$
where r_s is the sound horizon at recombination and D_A is the angular diameter distance.

The sound horizon r_s depends on the pre-recombination physics, which is well understood under ΛCDM.

### 2.2 Local Distance Ladder (SH0ES)

The SH0ES team uses a three-rung distance ladder:

1. **Geometric parallax** to Milky Way Cepheids (Gaia EDR3)
2. **Cepheid period-luminosity relation** in SN Ia host galaxies
3. **Type Ia supernovae** in the Hubble flow

**Equation 2:** The Cepheid period-luminosity relation:
$$m = M + 5\log_{10}(d/10\text{pc}) + A_\lambda$$
where m is apparent magnitude, M is absolute magnitude, d is distance, A_λ is extinction.

The SH0ES result: H₀ = 73.04 ± 1.04 km/s/Mpc (1.4% precision).

### 2.3 Independent Confirmation

- **H0LiCOW** (strong lensing time delays): 73.3 +1.7/-1.8 km/s/Mpc
- **MIRAS** (Miras variable stars): 73.3 ± 4.0 km/s/Mpc
- **TRGB** (Tip of Red Giant Branch): 69.8 ± 1.9 km/s/Mpc [Freedman et al. 2021]

---

## 3. Evidence Challenging the Tension

### 3.1 Systematic Uncertainties in Cepheid Calibration

Recent work suggests possible systematics:

- **Metallicity dependence** of the period-luminosity relation: ΔM/Δ[Fe/H] = -0.2 to -0.3 mag/dex
- **Crowding/blending effects** in crowded fields: up to 0.03 mag bias
- **Gaia parallax zero-point**: -0.017 mas systematic [Lindegren et al. 2021]

### 3.2 Alternative CMB Models

- **Early dark energy** (EDE): Can raise CMB-inferred H₀ to ~71 km/s/Mpc
- **Neutrino self-interactions**: Modifies sound horizon
- **Primordial magnetic fields**: Alters recombination physics

### 3.3 TRGB Discrepancy

The Tip of the Red Giant Branch method gives H₀ = 69.8 ± 1.9 km/s/Mpc, intermediate between Planck and SH0ES, with different systematics.

---

## 4. Contradictory Evidence Table

| Measurement | H₀ (km/s/Mpc) | Tension with Planck | Tension with SH0ES |
|-------------|---------------|---------------------|--------------------|
| Planck 2018 | 67.4 ± 0.5 | — | 5.3σ |
| SH0ES 2022 | 73.04 ± 1.04 | 5.3σ | — |
| H0LiCOW | 73.3 +1.7/-1.8 | 3.1σ | 0.1σ |
| TRGB (Freedman) | 69.8 ± 1.9 | 1.2σ | 1.4σ |
| MIRAS | 73.3 ± 4.0 | 1.5σ | 0.1σ |
| DESI BAO + BBN | 67.6 ± 1.0 | 0.2σ | 4.3σ |

---

## 5. Discussion

The persistence of the Hubble tension despite independent confirmations of both measurements suggests either:

1. **Unknown systematics** in one or both measurements
2. **New physics** beyond ΛCDM (early dark energy, interacting dark energy, etc.)
3. **Statistical fluke** (unlikely at 5.3σ)

The community remains divided. The tension is real in the sense that the measurements are robust; whether it indicates new physics is unresolved.

---

## References

1. Aghanim, N. et al. (Planck) 2018, A&A, 641, A6
2. Riess, A.G. et al. (SH0ES) 2022, ApJ, 934, L7
3. Freedman, W.L. et al. 2021, ApJ, 919, 16
4. Wong, K.C. et al. (H0LiCOW) 2020, MNRAS, 498, 1420
5. Lindegren, L. et al. 2021, A&A, 649, A2