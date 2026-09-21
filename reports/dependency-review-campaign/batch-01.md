# E6.1 Dependency-edge review — Batch 01

27 edges · reviewer: `human:reviewer.physics-001` · relations: mathematically_requires, logically_requires

Decision vocabulary: **accept** (→ reviewed), **canonical** (→ reviewed → canonical, evidence required),
**reject** (reason required), **defer**. Fill `decision:` in the companion YAML, then run:

```bash
python3 scripts/apply_review_decisions.py reports/dependency-review-campaign/batch-01.yaml --reviewer human:reviewer.physics-001
```

| # | Connection | Assertion | Types | Domain/range | Text support | Evidence | Score |
|---|-----------|-----------|-------|--------------|--------------|----------|-------|
| 1 | `stemma:conn.000004` | **Newton's Second Law** mathematically requires **Time** | law→quantity | ok | name 'Time' | 1 item(s) | 0.166322 |
| 2 | `stemma:conn.000005` | **Newton's Second Law** mathematically requires **Velocity** | law→quantity | ok | none found (check definition/derivation manually) | 1 item(s) | 0.160956 |
| 3 | `stemma:conn.000003` | **Newton's Second Law** mathematically requires **Length** | law→quantity | ok | none found (check definition/derivation manually) | 1 item(s) | 0.144215 |
| 4 | `stemma:conn.000001` | **Newton's Second Law** mathematically requires **Mass** | law→quantity | ok | name 'Mass'; symbol 'm' in equation | 2 item(s) | 0.136916 |
| 5 | `stemma:conn.000019` | **Velocity** mathematically requires **Time** | quantity→quantity | ok | name 'Time' | 1 item(s) | 0.12963 |
| 6 | `stemma:conn.000027` | **Power** mathematically requires **Time** | quantity→quantity | ok | none found (check definition/derivation manually) | 1 item(s) | 0.118197 |
| 7 | `stemma:conn.000021` | **Acceleration** mathematically requires **Time** | quantity→quantity | ok | name 'Time' | 1 item(s) | 0.117003 |
| 8 | `stemma:conn.000002` | **Newton's Second Law** mathematically requires **Force** | law→quantity | ok | name 'Force'; symbol 'F' in equation | 1 item(s) | 0.114809 |
| 9 | `stemma:conn.000009` | **Conservation of Energy** mathematically requires **Work** | law→quantity | ok | none found (check definition/derivation manually) | 1 item(s) | 0.114069 |
| 10 | `stemma:conn.000023` | **Kinetic Energy** mathematically requires **Velocity** | quantity→quantity | ok | name 'Velocity' | 1 item(s) | 0.112831 |
| 11 | `stemma:conn.000017` | **Momentum** mathematically requires **Velocity** | quantity→quantity | ok | name 'Velocity' | 1 item(s) | 0.111637 |
| 12 | `stemma:conn.000020` | **Acceleration** mathematically requires **Velocity** | quantity→quantity | ok | name 'Velocity' | 1 item(s) | 0.111637 |
| 13 | `stemma:conn.000018` | **Velocity** mathematically requires **Length** | quantity→quantity | ok | none found (check definition/derivation manually) | 1 item(s) | 0.107523 |
| 14 | `stemma:conn.000025` | **Work** mathematically requires **Length** | quantity→quantity | ok | none found (check definition/derivation manually) | 1 item(s) | 0.100636 |
| 15 | `stemma:conn.000008` | **Conservation of Energy** mathematically requires **Kinetic Energy** | law→quantity | ok | none found (check definition/derivation manually) | 1 item(s) | 0.089523 |
| 16 | `stemma:conn.000010` | **Conservation of Energy** mathematically requires **Power** | law→quantity | ok | none found (check definition/derivation manually) | 1 item(s) | 0.089523 |
| 17 | `stemma:conn.000015` | **Conservation of Energy** mathematically requires **joule** | law→unit | ok | none found (check definition/derivation manually) | 1 item(s) | 0.089523 |
| 18 | `stemma:conn.000022` | **Kinetic Energy** mathematically requires **Mass** | quantity→quantity | ok | name 'Mass' | 1 item(s) | 0.088791 |
| 19 | `stemma:conn.000006` | **Newton's Second Law** mathematically requires **Acceleration** | law→quantity | ok | name 'Acceleration'; symbol 'a' in equation | 1 item(s) | 0.088329 |
| 20 | `stemma:conn.000007` | **Newton's Second Law** mathematically requires **Momentum** | law→quantity | ok | name 'Momentum' | 1 item(s) | 0.088329 |
| 21 | `stemma:conn.000011` | **Newton's Second Law** mathematically requires **kilogram** | law→unit | ok | none found (check definition/derivation manually) | 1 item(s) | 0.088329 |
| 22 | `stemma:conn.000012` | **Newton's Second Law** mathematically requires **metre** | law→unit | ok | symbol 'm' in equation | 1 item(s) | 0.088329 |
| 23 | `stemma:conn.000013` | **Newton's Second Law** mathematically requires **second** | law→unit | ok | none found (check definition/derivation manually) | 1 item(s) | 0.088329 |
| 24 | `stemma:conn.000014` | **Newton's Second Law** mathematically requires **newton** | law→unit | ok | none found (check definition/derivation manually) | 1 item(s) | 0.088329 |
| 25 | `stemma:conn.000016` | **Momentum** mathematically requires **Mass** | quantity→quantity | ok | name 'Mass' | 1 item(s) | 0.087597 |
| 26 | `stemma:conn.000024` | **Work** mathematically requires **Force** | quantity→quantity | ok | name 'Force' | 1 item(s) | 0.07123 |
| 27 | `stemma:conn.000026` | **Power** mathematically requires **Work** | quantity→quantity | ok | name 'Work' | 1 item(s) | 0.065944 |

## Reviewer notes

- A schema-valid edge is not a scientifically accepted prerequisite (protocol §1).
- `mathematically_requires`: the target appears in the source's defining equation/derivation.
- `logically_requires`: the source cannot be defined/understood without the target concept.
- If the true relation is weaker, **reject** with reason `should be related_to` (do not silently relabel; a new connection is authored instead).
- Migrated origin (`asserted_by: unknown:legacy-relationship`) is preserved on acceptance (protocol §6).
