# MIGRATIONS — schema & content change log

**Plan v2 E5.5.** Every schema, contract, or bulk-canonical change appends an entry here.
The rule: **a migration says what old data does** — old data must still validate against the
schema it was written for, or the entry names the script that rewrote it.

Append at the top. Never edit a landed entry except to correct a factual error (note the
correction inline).

Template:

```
## YYYY-MM-DD — <short title>
- **Tag:** ADR-00NN / plan v2 E#.# · **Kind:** additive | breaking | bulk-canonical rewrite
- **Changed:** <file/field/contract>
- **Old data:** <validates against the old schema unchanged | rewritten by scripts/<x>.py>
- **Consumer impact:** <none | repoint to … | upgrade adapter to export_version …>
```

---

## 2026-09-07 — Provider abstraction: official Antigravity local agent + separate entitlements (ADR-0038)
- **Tag:** ADR-0038 · **Kind:** webapp tooling (no canonical data change)
- **Changed:** new `webapp/providers.py` registry; first-class providers
  `antigravity` (official Antigravity SDK → official CLI `agy`, no API key),
  `gemini_api` (former `google`), `vertex_ai`, `openai_compatible` (former
  `openai`/community harness). `webapp/core.py` delegates chat/probe/models/
  login to the registry. `save_llm_config` accepts and canonicalizes aliases
  (`google`→`gemini_api`, `openai`→`openai_compatible`) and persists optional
  `project`/`location`/`transport`/`effort`/`agent`. UI exposes the four
  providers, Load models, Sign in to Antigravity, and Vertex/transport fields.
- **Old data:** existing `workflow/config/llm.json` with `provider: google` or
  `provider: openai` still reads correctly (aliases are canonicalized at read
  time); no canonical schema/export change.
- **Consumer impact:** API consumers get canonical provider ids instead of
  aliases. Antigravity now requires the official local SDK/CLI on the machine
  running the webapp; it fails closed (no placeholder candidates) otherwise.
  The webapp server default port is now `8081` (previous `8080`) so it does not
  collide with common local harness ports such as DeepSeek/Antigravity on
  `3080`; pass `--port` explicitly to use another.

---

## 2026-09-06 — Phase B trust/review activation (ADR-0037)
- **Tag:** ADR-0037 · **Kind:** gate + tooling + derived reports (no canonical data change)
- **Changed:** `validate.py` — canonical assertions require ≥1 evidence item or an explicit
  axiomatic marker (`ERROR`); active empty-evidence and `related_to`-only reclassifiable
  edges become advisory `WARNING`s (report remains gate-ERROR-free). New `review_entity.py`
  (human entity review transitions), `entity_review_campaign.py`, `academic_sources.py`,
  `relation_triage.py`. `curation_status.*` now include entity review coverage. Child
  subprocesses in the chain/tests now use `sys.executable` so a venv runner is consistent.
- **Old data:** no canonical file changes; schema/export versions unchanged (1.1.0/2.1.0).
- **Consumer impact:** the tracked `reports/validation-report.json` now carries advisory
  warnings (`WARNING` count >0, `ERROR`=0); consumers reading `results[]` should handle
  warnings. Exports are byte-identical except for regeneration (no content change).

---

## 2026-09-06 — Rejected lifecycle: `assertion.review.status=rejected` (ADR-0031)
- **Tag:** ADR-0031 · **Kind:** additive (schema minor, no canonical rewrite)
- **Changed:** `schema/connection.schema.json` `assertion.review.status` enum gains
  `rejected`; `schema/VERSION.yaml` `schema_version` `1.0.0 → 1.1.0`; validator adds a hard
  `ERROR` if a rejected assertion has no written reason; `all` policy (and adapter default)
  now excludes rejected; `review.py`/`apply_review_decisions.py` keep the record `active` and
  record rejection in `review_history`; reopen `rejected → unreviewed/proposed` is
  human-only + reason-required. Export shape is unchanged (stays 2.1.0).
- **Old data:** no canonical files change. Existing 4 `assertion.status: deprecated`
  connections are materialized-inverse repairs, not rejections — unchanged. Old 1.0.0 files
  still validate against old schema; new `1.1.0` is a superset enum.
- **Consumer impact:** additive enum value. Consumers reading `all` should now treat it as
  active-and-not-rejected; rejected claims are only in `knowledge.rejected.json`. Regenerate
  exports with `python3 scripts/validate.py`.

---

## 2026-09-06 — Domain identity gate + `our-environment` path relocation (ADR-0034)
- **Tag:** ADR-0034 · **Kind:** new gate + single-file path relocation (ID unchanged)
- **Changed:** new `schema/id-domain-map.yaml` maps id-prefix → domain + content
  directory; validator hard-errors on id-prefix/domain/path/vocabulary mismatch;
  `content/earth-space/atmosphere-climate/our-environment.md` moved to
  `content/physics/thermal-physics/our-environment.md` (its `stemma:phys.our-environment`
  ID and `domain: physics` were already correct; only the path was wrong).
- **Old data:** old schema/export unchanged (gate + file move only). The moved file's
  `id` and `domain` are unchanged, so references (connections, aliases, evidence) are
  unaffected.
- **Consumer impact:** none (no contract/ID change; the entity is still exported under
  `stemma:phys.our-environment`). Regenerate with `python3 scripts/validate.py`.

---

## 2026-09-06 — Ingestion/review webapp (ADR-0036)
- **Tag:** ADR-0036 · **Kind:** tooling/consumer (no canonical data change)
- **Changed:** new `webapp/` stdlib web UI (upload → extract → LLM Draft → human review →
  stage proposal); `workflow/` git-ignored workspace (uploads, extracted text, candidates,
  staged proposals, LLM config, audit log); `scripts/ingest.py` adds direct text-file
  extraction (`.txt/.md/.csv/.json/.yaml/.xml/.html`) alongside PDF/image; any other file
  type is retained and reported `unsupported`; `docs/WEBAPP.md` + ADR-0036; webapp core tests
  added to the verify chain.
- **Old data:** no canonical data changed. The webapp consumes existing canonical
  content read-only and never writes it.
- **Consumer impact:** none for canonical consumers. A curator uses
  `python3 webapp/server.py` to review uploads/proposals.

---

## 2026-09-06 — Ingest/proposal correctness: schema-valid source + fail-closed Draft seam (ADR-0035)
- **Tag:** ADR-0035 · **Kind:** tooling/pipeline correctness (no canonical data change)
- **Changed:** `scripts/ingest.py` builds a `source.schema.json`-conforming Source
  candidate (`id`/`type: other`/`citation`/`title`) and pushes extraction metadata into a
  `CurationRequest.extraction` sidecar (no extraction-only fields on canonical source);
  `scripts/ingest_to_proposals.py` now **requires** `--draft module:function` (fails closed
  without a real seam) and refuses to stage a dossier whose deterministic curation gates
  failed; `scripts/curation_pipeline.py` removes the dead `validate.REL_TYPES` reference and
  rejects any `relationships` field on an entity draft (ADR-0020/0028). `ingest.py` lazily
  imports Pillow so text-PDF extraction does not require an image dependency at import time.
- **Old data:** no canonical files changed. Old placeholder proposals are invalid and should
  not be staged; the CLI now refuses them.
- **Consumer impact:** ingest/proposal runners must supply a real Draft seam. Source
  candidates previously carried extraction-only fields; consumers should read them from the
  `extraction` sidecar. Regenerate nothing; this is a tooling path.

---

## 2026-09-06 — Machine-readable validation report + `--json` (ADR-0033)
- **Tag:** ADR-0033 · **Kind:** tooling/report contract (no canonical data change)
- **Changed:** `reports/validation-report.json` now has `results[]` with
  `severity/rule/focus/message`, `errors[]/warnings[]/info[]`, `severity_counts`,
  and version/`content_hash` identity; `scripts/validate.py --json` emits that
  report as the only stdout content (exit 0/1 retained); warnings are no longer
  stderr-only; `scripts/integrity_anomalies.py` gains `--json` and `--strict`
  and stays advisory in `verify_all.py`.
- **Old data:** the old SHACL-ish `resultSeverity/focusNode/resultMessage`
  members are superseded by the new members. Consumers of the report should
  read `results[]`/`errors[]`; the old keys are not carried forward.
- **Consumer impact:** CI/agents can consume the structured result directly.
  Regenerate with `python3 scripts/validate.py --json`.

---

## 2026-09-06 — Relation registry + controlled vocabularies in the export (ADR-0032)
- **Tag:** ADR-0032 · **Kind:** additive (contract minor bump)
- **Changed:** `exports/knowledge.json` gains optional top-level `relation_registry_version`,
  `relation_registry` (relation name → family/inverse/transitive/symmetric/domain/range/status)
  and `vocabularies`; `export_version` `2.0.0 → 2.1.0`. `schema/export.schema.json` updated;
  `adapters/python/` bootstraps `relations()` / `relation(name)` / `vocabularies` and fails
  closed on an unknown relation name when the registry is present.
- **Old data:** canonical YAML unchanged. A `2.0.x` export (no sidecar) still validates and
  loads with the previous literal-name behavior.
- **Consumer impact:** additive. Readers that ignore unknown members are unaffected; consumers
  that want registry semantics now get them from the artifact alone. Regenerate with
  `python3 scripts/validate.py`.

---

## 2026-09-04 — Refoundation: `stemma:` namespace, colon-free filenames, contract v2.0.0 (ADR-0027/0028)
- **Tag:** ADR-0027 / ADR-0028 · **Kind:** breaking (bulk canonical rewrite)
- **Changed:** every canonical ID `lhs:`→`stemma:` (881 objects; identity fields untouched);
  `connections/lhs:conn.NNNNNN.yaml`→`connections/conn.NNNNNN.yaml`; `sources/lhs:src.*`→`sources/src.*`;
  entity-side generated `relationships[]` projection **removed** (entities carry no relationship data);
  schemas → 1.0.0; export contract → 2.0.0; relation registry → 1.0.0 (4 duplicate reserved relations pruned);
  legacy `knowledge.compat-0.1.json` retired; curriculum-body provenance citations normalized; one law's
  type-inconsistent `dimensions` extension removed.
- **Old data:** rewritten in place by a one-time governed migration; validated green post-migration
  (`scripts/verify_all.py`). Git history is the audit trail; the immutability guard reconciles the old
  prefix through one documented alias rule.
- **Consumer impact:** adapters must use `stemma:` IDs and read the graph from `connections[]`
  (see `docs/CONSUMERS.md`). No compatibility artifact ships with 2.0.0.

## 2026-09-04 — Derived `claim_signature` in the export + duplicate-claim gate
- **Tag:** ADR-0026 · plan v2 E4.3 · **Kind:** additive (derived) + new gate
- **Changed:** `exports/knowledge.json` `connections[].claim_signature` (derived
  `sha256(source|relation|target|polarity|sorted qualifiers)`); validator rule
  `check_duplicate_claims` (two **active** connections with one signature = error);
  `schema/export.schema.json` documents the field.
- **Old data:** canonical YAML unchanged (the signature is never stored); exports written
  before this change still validate — the field is optional, not required.
- **Consumer impact:** none (additive). Regenerate exports with `python3 scripts/validate.py`.

## 2026-09-04 — Connection-triple immutability guard
- **Tag:** ADR-0026 · plan v2 E4.5 · **Kind:** new gate (no data change)
- **Changed:** `scripts/check_id_immutability.py` now reconstructs `connections/` history from
  git and rejects (a) an edited `(source, relation, target)` triple and (b) a connection deleted
  without `superseded`/`deprecated` or `lifecycle.replaced_by`.
- **Old data:** unchanged; the audited 654 connections have no historical triple edits, so the
  guard starts green. Requires `fetch-depth: 0` (CI already fetches full history).
- **Consumer impact:** none. Future corrections must supersede + re-assert under a new id.

## 2026-09-04 — Explorer decoupled from the validator (E7.4)
- **Tag:** plan v2 E7.4 · **Kind:** tooling
- **Changed:** `scripts/validate.py` no longer writes `explorer/public/exports/knowledge.json`;
  that path is git-ignored and synced by `explorer/scripts/sync-export.mjs` (`predev`/`prebuild`).
- **Old data:** no canonical data touched; the tracked copy was removed from the index.
- **Consumer impact:** explorer devs must run `npm run dev`/`npm run build` (or
  `node explorer/scripts/sync-export.mjs`) to refresh their local export copy.

## 2026-09-04 — Export contract **v1.0**
- **Tag:** ADR-0023 · plan v2 E1.5 (gate G-A) · **Kind:** breaking for consumers, additive in shape
- **Changed:** `export_version` `0.1` → `1.0`; `connections[]` and `sources[]` become **required**
  members enforced by `schema/export.schema.json` before the file is written (ADR-0022 ordering:
  validate → write). Repository `VERSION` 1.1.0 → 2.0.0.
- **Old data:** canonical data unchanged; the previous entities-only view is still emitted as
  `exports/knowledge.compat-0.1.json` while `legacy_export_version: '0.1'` exists in
  `schema/VERSION.yaml`. Deleting that key removes the artifact (test-enforced).
- **Consumer impact:** pin `SUPPORTED_EXPORT_VERSION = '1.0'` and read `connections[]`, or
  repoint to the compat file during the co-release window (`docs/EXPORT-VERSION-MIGRATION-Q3.md`).

## 2026-09-04 — `external_ids` format checks + agent registry
- **Tag:** ADR-0023 · plan v2 E4.1/E4.2 · **Kind:** additive + new gate
- **Changed:** known `external_ids` schemes (`wd`, `orcid`, `doi`, `isbn`, `qudt`, `ucum`, `cas`)
  are format-checked; every `human:`/`process:`/`llm:`/`unknown:` agent id in provenance must
  resolve in `schema/agent-registry.yaml`.
- **Old data:** 41 mechanics entities were seeded with verified Wikidata QIDs; all previously
  used agent ids were registered. No object was renamed.
- **Consumer impact:** none (validation-only).

## 2026-09-03 — Single version source + deterministic exports
- **Tag:** ADR-0022 · plan v2 E5.1/E5.2 · **Kind:** tooling / derived-artifact change
- **Changed:** `schema/VERSION.yaml` is the only place version constants live; `generated_at`
  (wall clock) replaced by `content_hash: sha256:…` in the export and in
  `reports/validation-report.json`. CI gates freshness with
  `git diff --exit-code -- exports …`.
- **Old data:** canonical data unchanged; exports regenerated once. Consumers reading
  `generated_at` must read `content_hash`.
- **Consumer impact:** a consumer that assumed "the export changes every run" can now cache by
  `content_hash`.

## 2026-09-03 — Registry integrity + controlled vocabularies
- **Tag:** ADR-0021 · plan v2 E2.1–E2.7, E6.2 · **Kind:** additive schema + gate + bulk-canonical repair
- **Changed:** entity types gain `phenomenon`, `model`, `experiment`; `regime` removed from
  relation ranges; inverse coherence, mirrored domain/range and known-type checks enforced;
  `context.domain/subdomain/regime/scale` validated against `schema/vocabularies/`; cycle
  detection on transitive relations; 37 unused relations marked `reserved`; migrated
  connections' fabricated `regime: ["classical"]` regenerated honestly (E6.2).
- **Old data:** repaired in place by `scripts/repair_registry.py`,
  `scripts/repair_connection_context.py`, `scripts/repair_materialized_inverses.py`,
  `scripts/sync_relationships.py` — see commits `19639a8`, `e7761f7`. Old (pre-repair) content
  would **fail** the current gate by design; the repairs are the migration.
- **Consumer impact:** `context.regime` may now be empty (`[]`) where knowledge is
  regime-independent — do not assume a non-empty regime.

## 2026-09-03 — Connections-only relationship truth
- **Tag:** ADR-0020 · plan v2 E1.1–E1.4 · **Kind:** new gate; inline block demoted to a projection
- **Changed:** `connections/` is the single canonical relationship source; an entity's
  `relationships[]` block is a **generated projection** (`scripts/sync_relationships.py`) and
  drift is a validator error.
- **Old data:** the 641 inline relationships were migrated 1:1 to connection files earlier
  (ADR-0011); the 6 connections-only pairs were projected back into entities by the first
  `sync_relationships.py` run.
- **Consumer impact:** new readers must use `connections[]`; `entities[].relationships` is
  deprecated and removed in contract **v2.0** (plan v2 E1.7).

## 2026-09-02 — Rename to STEMMA and freeze
- **Tag:** ADR-0019 · **Kind:** naming / governance (no data change)
- **Changed:** foundation renamed LearningHubSTEM → STEMMA; `lhs:` id namespace frozen (never
  reused, never reassigned); schema/export contracts frozen pending an explicit decision.
- **Old data:** all `lhs:` ids unchanged by the rename (`docs/HISTORY-RENAME.md`).
- **Consumer impact:** display name only.

## 2026-08-30 — First-class connections + urgent metadata v0.2
- **Tag:** ADR-0011, ADR-0016 · **Kind:** additive schema + bulk-canonical migration
- **Changed:** relationship triples became first-class `connections/` objects with an
  `assertion` block (`status`, `type`, `review`, `polarity`, `confidence`, `confidence_basis`),
  `context`, `evidence`, `lifecycle`, `created_at`/`updated_at`, `rights`, `external_ids`.
- **Old data:** 641 inline relationships were migrated 1:1 into `connections/lhs:conn.NNNNNN.yaml`
  by `scripts/migrate_relationships.py`; prose `source` strings became `sources/` stubs.
- **Consumer impact:** assertions carry `assertion.review.status` — trust is now readable per edge.
