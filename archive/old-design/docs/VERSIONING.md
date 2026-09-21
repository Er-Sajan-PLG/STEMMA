# STEMMA Versioning

**Version:** 1.0.0
**Status:** Active
**Owner:** Governance
**Applies To:** This repository (canonical knowledge foundation)
**Related:** `schema/concept.schema.json`, `exports/knowledge.json`, `scripts/validate.py`,
  `docs/decisions/0008-versioning.md`

---

## 1. Purpose

Versioning in STEMMA distinguishes three separate, never-collapsed tracks (per
decision 0008), plus a release tracker for content:

- **`schema_version`** — version of `schema/concept.schema.json` (field set, enums, constraints).
- **`export_version`** — version of the `exports/knowledge.json` consumer contract (shape/semantics).
- **Content release** — new/edited/deprecated entities (any content change; does not imply a contract bump).
- **`VERSION` (this file's `**Version:**`)** — the repository's semantic release tracker used
  to keep docs fresh and coordinate cross-repo releases.

---

## 2. Source of truth

| Track | Source | Where recorded |
|-------|--------|----------------|
| Schema | `schema_version` | `exports/knowledge.json`, `schema/concept.schema.json` |
| Export contract | `export_version` | `exports/knowledge.json` |
| Content release | content changes + `VERSION` bump | git history; release semver |
| Repo release | `VERSION` file | this file's `**Version:**` |

---

## 3. Bumping rules

- **Schema / contract change (breaking):** bump `schema_version` / `export_version` by the
  documented rule (breaking → major) and record an ADR. See decision 0008.
- **Content addition / curation:** bump `VERSION` MINOR (new knowledge) or PATCH
  (correction/review), using version bumping so doc markers stay in sync.
- Additive schema/metadata extension (ADR-0017/0018): leave `schema_version`/`export_version`
  unchanged; bump `VERSION` MINOR.

The version tool keeps doc `**Version:**` markers fresh:

```bash
# bump minor
# check version markers
```

---

## 4. Derived artifacts

`exports/*.json` are **derived and regenerable** — never hand-edited. Regenerate with
`python3 scripts/validate.py`. They are validated before the export is written; a consumer
never handles a dangling reference.

---

## 5. Enforcement

- `scripts/validate.py` validates schema/status/relationships/provenance/extensions/historical.
- Pre-commit `check-doc-versions` hook verifies doc version markers match `VERSION` before merge.
- Content is curriculum/grade-agnostic (NORTHSTAR): grade semantics live only in consumer
  mapping docs.

---

*Derived from decision 0008.*