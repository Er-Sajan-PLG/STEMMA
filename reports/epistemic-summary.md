# Epistemic Summary — v0.2

Deterministic report over all `connections/*.yaml` (explicit fields only).

- Total connection records (canonical objects): **654**
- Canonical scientific assertions (`review.status == canonical`): **50**
- Proposed: 653, Asserted: 1, Inferred: 0
- Review: unreviewed 604, reviewed-only 0, canonical 50 (total reviewed including canonical: 50)
- Status: active 650, deprecated 4, rejected 0
- Origin: migrated 641, human-authored 13, llm-authored 0
- With confidence: 1, without: 653
- Human reviewed_by present: 50

> Canonical object (file exists in `connections/`) != canonical scientific assertion.
> Canonical is terminal reviewed state (reviewed-only 0, canonical 15). `review.status==canonical` implies reviewed.
> A migrated connection is a canonical object with `review.status=unreviewed` until human review.

## By assertion type
{'proposed': 653, 'asserted': 1}

## By review
{'canonical': 50, 'unreviewed': 604}

## By origin
{'migrated': 641, 'human-authored': 13}

## By method
{'migration': 641, 'manual': 13}

Machine-readable: `reports/epistemic-summary.json`
