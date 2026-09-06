# DECISION 0031 — Rejected lifecycle (schema 1.1.0)

- **Date:** 2026-09-06
- **Status:** decided & implemented
- **Related:** ADR-0011 (assertion model), ADR-0026 (claim identity),
  ADR-0028 (contract v2.0), `docs/SOTA-REVIEW.md` §0.1.

## Context

Scientific rejection had no representation. The review tooling encoded it as
`sentinel` or structurally `deprecated`, which conflates "this claim is wrong /
not accepted" with "this record was merged/retired." That is a correctness bug
in the authoring path: a rejected assertion was indistinguishable from a
retired structural record, and the audit trail lost the distinction.

## Decision

- **Rejection is a review state.** `assertion.review.status` gains `rejected`
  (`unreviewed / reviewed / canonical / rejected`). `schema_version` moves
  `1.0.0 → 1.1.0`; export stays `2.1.0` (same object shape, one enum value).
- **A rejected record remains an active canonical object**
  (`assertion.status: active`). `deprecated`/`superseded` stay reserved for
  structural retirement (dedup, merge, replaced), never for rejection.
- **A rejection must carry a written reason.** The gate is a hard `ERROR`
  when `assertion.review.status == rejected` but neither `lifecycle.reason`
  nor the most recent `provenance.review_history[]` entry for that rejection
  supplies a reason.
- **The default `all` consumer view excludes rejected claims.** `all` =
  active AND not rejected; rejected assertions surface only in
  `exports/knowledge.rejected.json` (and the adapter's `rejected_connection_count`).
- **Reopen is explicit and human-only:** `rejected → unreviewed/proposed`
  through a review command that records a human reviewer + reason; direct
  `rejected → reviewed/canonical` remains forbidden.
- **No existing canonical content needs editing.** The four
  `assertion.status: deprecated` connections are materialized-inverse repairs,
  not rejections; they stay deprecated.

## Alternatives considered

- **`assertion.status: rejected`.** Rejected because status means record
  lifecycle, not scientific judgement.
- **Only `lifecycle.reason` carries rejection.** Rejected because it is not
  machine-filterable without an extra convention.
- **Keep as gap.** Rejected because it silently corrupts the trust signal.

## Consequences

- `schema/connection.schema.json` review.status enum + `schema/VERSION.yaml`
  schema_version bump; `scripts/validate.py` hard reason gate;
  `graph_policy.py`/adapter `all` excludes rejected; `review.py` +
  `apply_review_decisions.py` reject/reopen semantics; tests + docs.
- Export content hash changes only if canonical content changes; schema/export
  version field updates as usual.
