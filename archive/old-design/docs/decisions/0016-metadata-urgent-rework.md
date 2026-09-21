# DECISION 0016 — Urgent metadata rework v0.2 (additive)

- **Date:** 2026-08-30
- **Status:** decided
- **Related:** ADR-011..015, docs/metadata/METADATA-AUDIT-v0.2.md

## Context
Metadata audit (M1-M26) identified 11 urgent dimensions before public release (polarity, timestamps, source bibliographic, evidence type/stance, locator, qualifiers, lifecycle, claim signature, rights, entity version).

## Decision
Add **additive optional** urgent fields (keep `schema_version 0.2`, `export_version 0.1`):
- Connection: `assertion.polarity` (default positive), `created_at/updated_at`, `validity{valid_from,valid_until}`, `lifecycle{reason,replaced_by}`, `context.qualifiers[]`, `evidence{stance, locator_struct}`, `rights`
- Source: `title, authors[], year, publisher, journal, volume, doi, url, isbn, edition, language, source_role, rights`
- Entity: `updated_at, version, external_ids, rights`
- Derived: `integrity.claim_signature` (hash source|relation|target|polarity) and `content_hash` as derived, not canonical

## Reason
Public trust requires polarity, temporal validity, source identity, evidence direction, and license; all additions preserve backward compat and determinism.

## Consequences
- Migration `scripts/migrate_metadata_urgent.py` adds defaults (polarity positive, timestamps from file mtime, stance supports, qualifiers [], validity null) idempotently, no fabrication.
- Validator enforces new enums/ranges, allows missing for old.
- No breaking export change.
