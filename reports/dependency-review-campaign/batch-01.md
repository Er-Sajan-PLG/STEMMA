# E6.1 Dependency-edge review — Batch 01

1 edges · reviewer: `human:reviewer.physics-001` · relations: mathematically_requires, logically_requires

Decision vocabulary: **accept** (→ reviewed), **canonical** (→ reviewed → canonical, evidence required),
**reject** (reason required), **defer**. Fill `decision:` in the companion YAML, then run:

```bash
python3 scripts/apply_review_decisions.py reports/dependency-review-campaign/batch-01.yaml --reviewer human:reviewer.physics-001
```

| # | Connection | Assertion | Types | Domain/range | Text support | Evidence | Score |
|---|-----------|-----------|-------|--------------|--------------|----------|-------|
| 1 | `stemma:conn.000157` | **Force** mathematically requires **Mass** | quantity→quantity | ok | name 'Mass' | 2 item(s) | 0.081072 |

## Reviewer notes

- A schema-valid edge is not a scientifically accepted prerequisite (protocol §1).
- `mathematically_requires`: the target appears in the source's defining equation/derivation.
- `logically_requires`: the source cannot be defined/understood without the target concept.
- If the true relation is weaker, **reject** with reason `should be related_to` (do not silently relabel; a new connection is authored instead).
- Migrated origin (`asserted_by: unknown:legacy-relationship`) is preserved on acceptance (protocol §6).
