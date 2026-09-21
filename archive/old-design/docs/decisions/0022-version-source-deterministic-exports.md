# DECISION 0022 — Single version source and deterministic derived exports

- **Date:** 2026-09-03
- **Status:** decided (implemented with this change; owner-directed activation of plan v2)
- **Related:** ADR-0008 (three-track versioning), ADR-0019 (contract freeze),
  `docs/ARCHITECTURE-AUDIT-v1.0.md` (findings F5, F8),
  `docs/STEMMA-IMPLEMENTATION-PLAN-v2.md` (E5.1, E5.2)

## Context

The audit measured four disagreeing version signals: `validate.py` hardcoded
`schema_version`/`export_version` = `"0.1"` while the schemas self-describe v0.2, the
`VERSION` file said `1.0.0`, and no git tags existed. Worse, exports were stamped with
wall-clock `generated_at`, so every validator run dirtied the tracked artifacts — a tracked
derived artifact that can never be `git diff --exit-code`-clean is a process defect, and
freshness was unverifiable.

## Decision

1. **`schema/VERSION.yaml` is the single authoritative version source**
   (`schema_version`, `export_version`, `relation_registry_version`). Every exporter reads
   it; version literals in exporters are forbidden and test-enforced.
   - `schema_version` aligns to `"0.2"` (matching the schemas' own self-description; the
     `"0.1"` literal was stale drift).
   - `export_version` remains `"0.1"` — **the consumer contract does not change** (ADR-0019
     freeze; a contract bump is gate G-A with consumer co-release).
2. **Exports stamp a deterministic `content_hash`** (SHA-256 over `content/`, `connections/`,
   `sources/` file bytes + paths) instead of `generated_at`. Regeneration is byte-identical.
   The derived view exports (`knowledge.*.json`) inherit versions and the content hash.
3. **CI enforces freshness**: after the verification chain, `git diff --exit-code -- exports
   explorer/public/exports` — a stale export fails the build instead of silently shipping.
4. Repository `VERSION` bumps 1.0.0 → 1.1.0 per `docs/VERSIONING.md` (additive schema +
   content change; minor bump). Tagged releases remain gate E5.3 (not activated here).

## Alternatives considered

- Keep wall-clock timestamps — rejected: destroys reproducibility and freshness checking.
- Drop `generated_at` from the export shape without replacement — rejected: consumers may
  want to know *which* content they ingested; the hash answers that better than a clock.
- Bump `export_version` to v1.x now — rejected: requires coordinated consumer adapter
  co-release (gate G-A, plan v2 E1.5).

## Consequences

- "Which content did I consume?" = `content_hash` — reproducible and diffable.
- Stale or hand-edited derived artifacts fail CI.
- Export diffs contain only real content changes.
