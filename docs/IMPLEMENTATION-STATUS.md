# STEMMA — Implementation Status

**Status:** Authoritative evidence-based ledger (baseline 3.0.0, 2026-09-04).
Claims here are backed by the verification chain, not by older documents.

---

## 1. Implemented and verified (chain-green)

| Capability | Evidence |
|---|---|
| Canonical corpus: 224 entities, 654 first-class connections, 3 source records | `status_truth.py` (README block, CI-checked) |
| Four JSON Schema contracts (entity, connection, source, export) v1.0.0 | `schema/`, validated by gate |
| Relation registry v1.0.0: 55 relations, 12 adopted, coherence-checked | `schema/relation-registry.yaml` |
| Controlled vocabularies (domains/subdomains/regimes+scales), gate-enforced | `schema/vocabularies/` |
| Domain identity: `id-domain-map.yaml`, hard id-prefix/domain/path/vocabulary gate; relocated `our-environment` keeping ID | `schema/id-domain-map.yaml`, `validate.py`, `tests/registry/test_domain_identity.py` |
| Gate: schema, identity, references, registry, vocabularies, epistemics, cycles, duplicate claims, legacy-namespace guard, filename↔ID | `scripts/validate.py` |
| Deterministic export, contract-validated before write, content-hash stamped | `validate.py`, `tests/versioning/` |
| Machine-readable validator report (severity results, warnings, counts, versions) + `--json`; advisory integrity anomalies | `validate.py`, `integrity_anomalies.py`, `tests/versioning/test_validation_report.py` |
| Export-embedded relation registry + controlled vocabularies (contract 2.1.0); adapter introspection + fail-closed on unknown relation | `schema/export.schema.json`, `validate.py`, `adapters/python/`, `tests/versioning/`, `adapters/python/tests/test_adapter.py` |
| Review-policy export views + extended graph view (derived inverses/closure) | `export_review_aware.py`, `graph_analysis.py` |
| Git-history ID + assertion-triple immutability guards (namespace-alias aware) | `check_id_immutability.py` |
| Review state machine + campaign worksheets for human review | `review.py`, `curation_state.py`, `apply_review_decisions.py`, `dependency_review_campaign.py` |
| Rejected lifecycle (schema 1.1.0): `review.status=rejected`, reason-required gate, `all` excludes rejected, human-only reopen | `schema/connection.schema.json`, `validate.py`, `graph_policy.py`, `review.py`, `apply_review_decisions.py`, adapter |
| Ingestion pipeline (PDF/image/OCR → staged proposals; schema-valid source + extraction sidecar; fail-closed Draft seam; gate-before-stage) | `ingest.py`, `ingest_to_proposals.py`, `curation_pipeline.py`, `tests/curation/test_ingest*.py` |
| Ingestion/review webapp (stdlib UI, any-file upload, best-effort extraction, LLM Draft seam, human-only staging, audit trail) | `webapp/`, `docs/WEBAPP.md`, `tests/webapp/test_webapp_core.py` |
| Draft provider abstraction: official Antigravity local agent (SDK→CLI, no Gemini key), separate Gemini API / Vertex AI / OpenAI-compatible entitlements, canonical ids, fail-closed local availability | `webapp/providers.py`, `webapp/core.py`, `tests/webapp/test_webapp_core.py`, ADR-0038 |
| Phase B activation: canonical-evidence gate + R2 source backfill report; entity human review tooling + campaign + coverage; R4 relation-triage report + advisory warnings | `validate.py`, `academic_sources.py`, `relation_triage.py`, `review_entity.py`, `entity_review_campaign.py`, `curation_status.py`, `tests/curation/test_phase_b_integrity.py` |
| Extension registry + agent registry (gate-resolved) | `schema/*-registry.yaml` |
| 3-D explorer reading only the export, trust-annotated, contract-pinned | `explorer/` (`npm run verify`) |
| First-party read-only Python adapter (SDK, CLI, local JSON API), export-major pinned and policy-mirroring | `adapters/python/`, `adapters/python/tests/test_adapter.py` |
| Layered test suite + CI chain + freshness + gitleaks | `tests/`, `.github/workflows/ci.yml` |
| Ecosystem-independence and docs-consistency gates | `tests/repo/` |

## 2. Partially implemented (honest gaps)

| Area | State | Gap |
|---|---|---|
| Human review coverage | 50/654 assertions canonical (7.6%); 34/188 dependency edges reviewed; **0/224 entities human-reviewed** (tooling + worksheet generator now exist, decisions are human work) | Review is the bottleneck by design; `review_entity.py` + `entity_review_campaign.py` make it actionable |
| Source records | 3 records vs 44 unresolved entity source strings; 0 unresolved evidence refs (`reports/academic-sources.json`) | Backfill is curation work, now with a deterministic driver report |
| Math layer | Display strings only (`equation`/`symbol`/`unit`); 1 `unit` entity; no symbol→quantity bindings | ADR-0024 proposed — awaits human gate G-C |
| External IDs | Mechanics domain seeded with verified Wikidata QIDs | Other domains unseeded |
| Multilingual | Identity principle decided (ADR-0009) | No localized content (by design until needed) |
| Publication | Export file + git history | No tags/releases/IRIs yet (roadmap R6; needs the IRI decision) |

## 3. Known debt (tracked, non-blocking)

- 604 unreviewed assertions carry `asserted_by: unknown:legacy-relationship`
  (honest migration provenance) — resolves naturally as review proceeds.
- `equation`/`symbol`/`unit` display strings will be superseded by the math
  layer when ADR-0024 is decided.
- Explorer ships as a reference consumer; its accessibility polish is not
  production-grade.

## 4. Removed with the refoundation (for the record)

Inline entity `relationships[]` projection (dual-truth eliminated — ADR-0028);
legacy co-release export artifact; one-shot migration/repair scripts;
process-audit reports and superseded plans (history remains in git and ADRs).

## 5. Verification command

```bash
python3 scripts/verify_all.py     # the same chain CI runs
```
