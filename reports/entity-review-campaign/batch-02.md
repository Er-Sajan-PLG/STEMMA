# Entity review — Batch 02

12 entities · reviewer: `human:reviewer.physics-001` · seed pass: False

Use a human reviewer, then run:

```bash
python3 scripts/review_entity.py review <id> --reviewer human:reviewer.physics-001
python3 scripts/review_entity.py canonicalize <id> --reviewer human:reviewer.physics-001
```

Decision field in the YAML is informational (the CLI is the authority).

| # | Entity | Domain | Type | Status | Score |
|---|--------|--------|------|--------|-------|
| 1 | `stemma:phys.work` | physics | quantity | draft | 0.019245 |
| 2 | `stemma:phys.force` | physics | quantity | draft | 0.017985 |
| 3 | `stemma:phys.kinetic-energy` | physics | quantity | draft | 0.013699 |
| 4 | `stemma:phys.power` | physics | quantity | draft | 0.013699 |
| 5 | `stemma:phys.conservation-energy` | physics | law | draft | 0.012824 |
| 6 | `stemma:phys.acceleration` | physics | quantity | draft | 0.012505 |
| 7 | `stemma:phys.momentum` | physics | quantity | draft | 0.012505 |
| 8 | `stemma:phys.joule` | physics | unit | draft | 0.011699 |
| 9 | `stemma:phys.kilogram` | physics | unit | draft | 0.010505 |
| 10 | `stemma:phys.metre` | physics | unit | draft | 0.010505 |
| 11 | `stemma:phys.newton` | physics | unit | draft | 0.010505 |
| 12 | `stemma:phys.second` | physics | unit | draft | 0.010505 |