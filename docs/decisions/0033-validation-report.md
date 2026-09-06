# DECISION 0033 — Machine-readable validation report (ADR-0033)

- **Date:** 2026-09-06
- **Status:** decided & implemented
- **Related:** ADR-0022 (determinism), ADR-0023 (contract gate),
  `docs/SOTA-REVIEW.md` §0.2 (T2), `docs/TESTING.md`.

## Context

The validator's human stdout was the only machine-readable channel for
failures. CI and agents had to reparse prose; warnings were stderr-only;
`integrity_anomalies.py` was a report in the chain but had no structured
emission or exit-code policy.

## Decision

- **`reports/validation-report.json` gains a flat, deterministic, machine
  shape:** `results[]` (each `{severity, rule, focus, message}`),
  convenience `errors[]` / `warnings[]` / `info[]`, `severity_counts`
  (`{ERROR, WARNING, INFO}`), plus `schema_version`, `export_version`,
  `relation_registry_version`, `kernel_version`, `content_hash`, and
  `valid` / `ok` / `conforms`.
- **`scripts/validate.py --json` emits the same report to stdout** as the
  only stdout content (human status goes to stderr); exit `0`/`1` retained.
- **Existing warnings become first-class `warnings[]`**, not stderr-only.
- **`integrity_anomalies.py` is advisory in the verify chain.** It always
  writes its report and returns `0` by default; `--json` emits structured
  output, `--strict` opts into `ERROR` gating (not used by the default chain).

## Alternatives considered

- **Keep prose-only.** Rejected: CI/agent automation needs a stable contract.
- **Scrape stdout in CI.** Rejected: brittle.
- **Make anomalies gate-breaking.** Rejected: structural/analytical
  anomalies are surfaced for review; only explicit validator errors gate.

## Consequences

- `scripts/validate.py` report writer + `--json`; `scripts/integrity_anomalies.py`
  `--json`/`--strict`; `scripts/verify_all.py` runs the report test and keeps
  anomalies advisory; `tests/versioning/test_validation_report.py` enforces the
  shape; docs updated.
- The report's `content_hash`/versions tie it to the exact snapshot it
  validated, so a report is never ambiguous about which export it describes.
