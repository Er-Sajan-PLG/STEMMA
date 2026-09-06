# Entity review — Batch 01

28 entities · reviewer: `human:reviewer.physics-001` · seed pass: True

Use a human reviewer, then run:

```bash
python3 scripts/review_entity.py review <id> --reviewer human:reviewer.physics-001
python3 scripts/review_entity.py canonicalize <id> --reviewer human:reviewer.physics-001
```

Decision field in the YAML is informational (the CLI is the authority).

| # | Entity | Domain | Type | Status | Score |
|---|--------|--------|------|--------|-------|
| 1 | `stemma:phys.mass` | physics | quantity | draft | 0.046018 |
| 2 | `stemma:phys.force` | physics | concept | draft | 0.043022 |
| 3 | `stemma:phys.energy` | physics | quantity | draft | 0.033185 |
| 4 | `stemma:chem.matter` | chemistry | concept | draft | 0.031373 |
| 5 | `stemma:phys.electric-charge` | physics | quantity | draft | 0.030842 |
| 6 | `stemma:chem.compound` | chemistry | concept | draft | 0.029586 |
| 7 | `stemma:chem.atom` | chemistry | concept | draft | 0.028516 |
| 8 | `stemma:phys.wave` | physics | concept | draft | 0.028512 |
| 9 | `stemma:math.rational-number` | mathematics | concept | draft | 0.028373 |
| 10 | `stemma:chem.chemical-reaction` | chemistry | concept | draft | 0.02821 |
| 11 | `stemma:bio.cell` | biology | concept | draft | 0.026802 |
| 12 | `stemma:math.integer` | mathematics | concept | draft | 0.025081 |
| 13 | `stemma:math.fraction` | mathematics | concept | draft | 0.021009 |
| 14 | `stemma:chem.element` | chemistry | concept | draft | 0.020657 |
| 15 | `stemma:math.algebraic-expression` | mathematics | concept | draft | 0.019823 |
| 16 | `stemma:math.function` | mathematics | concept | draft | 0.018046 |
| 17 | `stemma:bio.dna` | biology | concept | draft | 0.017902 |
| 18 | `stemma:earth.earth-system` | earth-space | concept | draft | 0.013335 |
| 19 | `stemma:bio.ecosystem` | biology | concept | draft | 0.012706 |
| 20 | `stemma:earth.atmosphere` | earth-space | concept | draft | 0.012697 |
| 21 | `stemma:bio.photosynthesis` | biology | concept | draft | 0.012052 |
| 22 | `stemma:bio.gene` | biology | concept | draft | 0.010909 |
| 23 | `stemma:earth.plate-tectonics` | earth-space | concept | draft | 0.004812 |
| 24 | `stemma:practice.scientific-observation` | scientific-practice | concept | draft | 0.004808 |
| 25 | `stemma:earth.greenhouse-effect` | earth-space | concept | draft | 0.00467 |
| 26 | `stemma:earth.rock-cycle` | earth-space | concept | draft | 0.00467 |
| 27 | `stemma:eng.engineering-design-process` | engineering | concept | draft | 0.00167 |
| 28 | `stemma:epist.observation-vs-inference` | scientific-practice | concept | draft | 0.00167 |