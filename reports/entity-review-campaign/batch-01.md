# Entity review — Batch 01

5 entities · reviewer: `human:reviewer.physics-001` · seed pass: True

Use a human reviewer, then run:

```bash
python3 scripts/review_entity.py review <id> --reviewer human:reviewer.physics-001
python3 scripts/review_entity.py canonicalize <id> --reviewer human:reviewer.physics-001
```

Decision field in the YAML is informational (the CLI is the authority).

| # | Entity | Domain | Type | Status | Score |
|---|--------|--------|------|--------|-------|
| 1 | `stemma:phys.time` | physics | quantity | draft | 0.031498 |
| 2 | `stemma:phys.length` | physics | quantity | draft | 0.028391 |
| 3 | `stemma:phys.velocity` | physics | quantity | draft | 0.028132 |
| 4 | `stemma:phys.mass` | physics | quantity | draft | 0.021092 |
| 5 | `stemma:phys.newtons-second-law` | physics | law | draft | 0.019824 |