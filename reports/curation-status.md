# Curation Status — v0.2

- Total connections: 2 (canonical objects)
- Canonical assertions (`review.status==canonical`): 0
- Reviewed-only: 2, Canonical: 0, Unreviewed: 0 (total reviewed inc. canonical: 2)
- Proposed: 0, Inferred: 0
- Migrated: 0, Human-authored: 1, LLM: 1
- Rejected: 0, Deprecated: 0
- Semantics: `reviewed-only` vs `canonical` (terminal); canonical implies reviewed

## By relation
{'derived_from': 1, 'mathematically_requires': 1}

## By family
{'derivation': 1, 'dependency': 1}

## By domain
{'physics': 2}

## By review
{'reviewed': 2}

## By origin
{'human-authored': 1, 'llm-authored': 1}

## Top reviewed (canonical)
- stemma:conn.000156: derived_from stemma:phys.metre -> value:{'amount': '299792458', 'lowerBound': None, 'upperBound': None, 'unit': 'qudt:unit-MeterPerSecond'}
- stemma:conn.000157: mathematically_requires stemma:phys.force -> stemma:phys.mass

## Remaining highest priority
none

## Gaps
- Evidence gaps: 0 (sample [])
- Provenance gaps (no reviewed_by): 0

## Entity review coverage
- Entities: 7
- Human-reviewed/canonical entities: 7 (100.0%)
- Canonical entities: 0
- By status: {'human_reviewed': 7}
- By domain: {"physics": {"canonical": 0, "human_reviewed": 7, "total": 7}}

## Note
Schema correctness != semantic acceptance. Canonical objects (397) include 382 proposed/unreviewed.
