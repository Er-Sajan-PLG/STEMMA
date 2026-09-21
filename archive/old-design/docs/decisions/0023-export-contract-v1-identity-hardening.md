# DECISION 0023 — Export contract v1.0 (gate G-A) + first-class `external_ids` and agent registry

- **Date:** 2026-09-04
- **Status:** decided (implemented with this change; owner decision on gate G-A: "bump to 1.0 now")
- **Related:** ADR-0007 (export contract), ADR-0008 (versioning), ADR-0016 (metadata rework — `external_ids`),
  ADR-0019 (freeze), ADR-0020 (connections-only truth), ADR-0022 (single version source),
  `docs/EXPORT-VERSION-MIGRATION-Q3.md`, `docs/STEMMA-IMPLEMENTATION-PLAN-v2.md` (E1.5, E4.1, E4.2, gate G-A),
  `docs/ARCHITECTURE-AUDIT-v1.0.md` (F1, F2, F5, F6)

## Context

1. **Contract.** Since ADR-0011 the export has carried `connections[]` and `sources[]` as *additive*
   members under `export_version: 0.1`. Consumers could not *rely* on them, so the one live consumer
   (STEM-TUITION adapter) still reads the legacy `entities[].relationships` projection — the
   audited two-truths defect (F1) survives at the consumer boundary even after ADR-0020 fixed it in
   the repository. `EXPORT-VERSION-MIGRATION-Q3.md` deferred the bump until connections became a
   *required* part of the contract, with a governed co-release. Gate G-A asks exactly that question.
2. **Identity.** ADR-0016 named `external_ids`; ADR-0021 put the field in `concept.schema.json`;
   no entity used it and no format check existed (F6). Provenance referenced eight agent identifiers
   (`human:…`, `process:…`, `unknown:…`) that resolved to nothing — a reviewer ID was a free string (F2).

## Decision

### A. Export contract v1.0 (plan v2 E1.5; gate G-A — decided)

1. `export_version` becomes **`1.0`**. Contract shape is now **machine-defined** in
   `schema/export.schema.json` and `scripts/validate.py` validates the payload against it **before
   writing** — a producer cannot ship a payload violating the contract it advertises.
2. **Required members:** `export_version`, `schema_version`, `content_hash`, `source`,
   `entity_count`, `connection_count`, `source_count`, `entities[]`, **`connections[]`**, **`sources[]`**.
   Consumers may rely on assertion objects with `assertion.review.status` and `provenance`.
3. `entities[].relationships[]` stays in v1.x **as a deprecated generated projection** (ADR-0020).
   Its removal is **v2.0** (plan v2 E1.7) — a separate decision, after the consumer reads `connections[]`.
4. **Co-release window.** `schema/VERSION.yaml` gains `legacy_export_version: '0.1'`; while present,
   the validator also emits `exports/knowledge.compat-0.1.json` (entities-only, stamped `0.1`,
   `source` string marked COMPATIBILITY VIEW). The STEM-TUITION adapter is repointed to that file
   *or* upgraded (`SUPPORTED_EXPORT_VERSION = '1.0'`, read `connections[]`) in the same release.
   When the adapter reads `1.0`, delete the key → the artifact disappears (test-enforced).
5. Repository `VERSION` 1.1.0 → **2.0.0** (breaking contract change per `docs/VERSIONING.md`).
   Derived-view exports (`knowledge.{all,…}.json`, `knowledge.extended.json`) inherit versions from
   `schema/VERSION.yaml`; their last hardcoded fallbacks (`"0.1"`/`"0.2"`) are removed (ADR-0022).

### B. `external_ids` first-class (plan v2 E4.1)

6. `external_ids` is a mapping *scheme → value | [values]* (already in the schema). The validator now
   **format-checks known schemes**: `wd` (`Q\d+`), `orcid`, `doi`, `isbn`, `qudt`, `ucum`, `cas`;
   duplicates within a scheme are errors. Unknown schemes are allowed (open registry) but must match
   the schema's scheme-name pattern.
7. **Seed:** all 41 mechanics entities carry Wikidata QIDs, each verified against the Wikidata API
   (label + description) on 2026-09-04. Where an entity is a *specialisation* of one item, the closer
   item wins (`scalar` → Q181175 *scalar quantity*, `vector` → Q2672914 *vector quantity*). Where
   Wikidata splits a concept, both are listed (`newtons-second-law` → Q104212301 general + Q2397319
   constant-mass). Where no faithful item exists, **no ID** is recorded (`equations-of-motion`: the
   SUVAT set has no item; Q215007 is the general ODE sense) — a wrong anchor is worse than none.
8. External IDs **link and anchor**; they never import content and never become identity (ADR-0003).

### C. Agent registry (plan v2 E4.2)

9. `schema/agent-registry.yaml` lists every agent identity (`id`, `class`, `display_name`,
   `external_id`, `status`, `note`). The validator resolves **every** agent reference —
   `asserted_by`, `generated_by`, `reviewed_by[]`, `review_history[].reviewer` on connections,
   `provenance.reviewer` on entities, `registered_by` in the extension registry — and exits 1 on
   an unknown id, a class/prefix mismatch, or a non-human `review_history.reviewer`.
10. `unknown:legacy-relationship` is registered deliberately (honest attribution of the 641
    migrated assertions; CURATION-PROTOCOL §6). **Any non-migrated assertion attributed to an
    `unknown:` agent is an error** (plan v2 §4 metric).
11. Reviewer `external_id` (ORCID) stays `null` until gate G-D (E6.5) decides the identity policy.

## Alternatives considered

- Bump to `0.2` — rejected: the shape change is breaking for a consumer that pins `0.1`;
  semver says major. `1.0` also signals the first contract consumers may build on.
- Keep `0.1` and let consumers "opportunistically" read connections — rejected: that is the
  audited defect (a truth nobody is allowed to rely on).
- Remove `relationships[]` in the same bump — rejected: doubles consumer work in one release;
  E1.7 is sequenced after the adapter reads `connections[]`.
- Hardcode a list of allowed reviewer strings in the validator — rejected: governance by
  registry file (like relations/extensions), not by code constant.

## Consequences

- Consumers of `1.0` get first-class assertions with review status; the LearningHub adapter must
  co-release (either repoint to the compat view or upgrade). Until then the compat artifact keeps
  the demo working.
- "Who said this?" now always resolves; new assertions cannot hide behind `unknown:`.
- Mechanics entities are cross-linkable to Wikidata/QUDT tooling; E3.3 (unit registry) can reuse
  the same mechanism with `qudt:`/`ucum:` schemes.
- Tests: `tests/versioning/test_deterministic_export.py` (contract + co-release window),
  `tests/provenance/test_agents_external_ids.py` (registry, formats, seed, E6.1 tooling).
