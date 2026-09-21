# Epistemic Summary — v0.2

Deterministic report over all `connections/*.yaml` (explicit fields only).

- Total connection records (canonical objects): **27**
- Canonical scientific assertions (`review.status == canonical`): **0**
- Proposed: 0, Asserted: 27, Inferred: 0
- Review: unreviewed 27, reviewed-only 0, canonical 0 (total reviewed including canonical: 0)
- Status: active 27, deprecated 0, rejected 0
- Origin: migrated 0, human-authored 27, llm-authored 0
- With confidence: 27, without: 0
- Human reviewed_by present: 0

> Canonical object (file exists in `connections/`) != canonical scientific assertion.
> Canonical is terminal reviewed state (reviewed-only 0, canonical 15). `review.status==canonical` implies reviewed.
> A migrated connection is a canonical object with `review.status=unreviewed` until human review.

## By assertion type
{'asserted': 27}

## By review
{'unreviewed': 27}

## By origin
{'human-authored': 27}

## By method
{'manual': 27}

Machine-readable: `reports/epistemic-summary.json`
