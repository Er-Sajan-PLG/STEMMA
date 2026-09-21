# DECISION 0035 — Ingest/proposal correctness (fail-closed Draft seam)

- **Date:** 2026-09-06
- **Status:** decided & implemented
- **Related:** ADR-0015 (evidence), ADR-0020 (connections-only truth),
  ADR-0028 (contract v2.0), ADR-0030 (consumer adapter),
  `docs/SOTA-REVIEW.md` §0.2 (T4), `docs/INGESTION.md`.

## Context

The ingest path emitted schema-non-conforming candidates. `source` was built
with `type: source`, extraction-only fields (`kind`, `format`, `pages`,
`ocr_used`, `extracted_text_preview`), and a `provenance` block not allowed by
`source.schema.json`, and lacked the required `citation`. The deterministic
fallback draft invented an entity with `domain: general`, `relationships: []`,
and a placeholder ID — all schema-invalid. The pipeline also referenced a
`validate.REL_TYPES` attribute that never existed, so any relationship-shaped
path crashed.

## Decision

- **Fail closed without a real Draft seam.** `ingest_to_proposals.py` refuses
  to stage a non-schema-valid placeholder; a runner must supply
  `--draft module:function`. The Source object is the only thing a deterministic
  path can stage without a seam.
- **Extraction metadata lives in a `CurationRequest` sidecar**
  (`request.extraction`: kind/format/pages/is_scanned/ocr_used/preview/
  source_name). Canonical `sources/*` records never carry extraction-only fields.
- **Gate before staging.** `stage()` only returns a dossier (and a caller may
  write it) when the curation pipeline's deterministic gates pass. A failing
  candidate raises `ProposalGateError`; it is never silently written under
  `proposals/`.
- **`build_source_candidate()` produces a schema-valid source object**
  (`id`, `type` ∈ source enum, required `citation`, optional `title`). No
  `relationships: []` on entity drafts; the dead `validate.REL_TYPES` reference
  is removed and replaced by an explicit entity-side relationship gate
  (entities carry no relationships, ADR-0020/0028).

## Alternatives considered

- **Keep placeholder fallback but make it schema-valid.** Rejected: it still
  stages garbage that a human must triage; fail-closed is cheaper and honest.
- **Remove ingestion until fixed.** Rejected: the seam is useful once wired; we
  only refuse the unwired path.
- **Carry extraction metadata on the source.** Rejected: canonical source
  records have a strict schema; extraction audit data belongs on the request.

## Consequences

- `scripts/ingest.py` schema-valid source + sidecar; `scripts/ingest_to_proposals.py`
  fail-closed + gate-before-stage; `scripts/curation_pipeline.py`
  `_check_relations` rewrite; lazy Pillow import (image-only dependency);
  `tests/curation/test_ingest.py`, `test_ingest_to_proposals.py`,
  `test_curation_pipeline.py`; docs/INGESTION example fixed; ADR.
- No canonical content or export contract changes.
