# STEMMA — Testing Strategy

**Status:** Authoritative (baseline 3.0.0).
**Entry point:** `python3 scripts/verify_all.py` — the chain CI runs; exit 0
is the release gate.

---

## 1. Principles

1. Tests enforce **architectural invariants**, not implementation branches.
2. The CI chain and the local command are **the same chain** — no
   CI-only magic.
3. Pure detection cores are separated from IO (git/files) so invariants are
   unit-testable with plain dicts (TDD core in `check_id_immutability.py`).
4. Tests are dependency-light (stdlib + PyYAML + jsonschema) and runnable as
   plain scripts — no framework lock-in.

## 2. Layers and where they live

| Layer | What it enforces | Where |
|---|---|---|
| **Gate (validation)** | Everything in `docs/PIPELINES.md` §2.4 | `scripts/validate.py` |
| **Unit** | Pure cores: claim signatures, graph policy filters, immutability detection | `tests/provenance/`, `tests/curation/test_connection_immutability.py` |
| **Schema tests** | Schemas are valid JSON Schema; registry coherence (inverses mirror, types exist, no duplicate semantics) | `tests/registry/` |
| **Relationship integrity** | Triples immutable from git history; no re-assertion of edited claims; supersession rules | `tests/curation/test_connection_immutability.py`, `tests/curation/test_id_immutability.py` |
| **Metadata semantics** | Polarity/confidence/timestamp/evidence contracts; no fabricated timestamps; strict duplicate-key rejection; extension registry; historical attribution | `tests/metadata/` |
| **Pipeline tests** | Ingestion never writes canonical; curation pipeline can't canonicalize; validator idempotence on a clean tree | `tests/curation/test_ingest.py`, `test_curation_pipeline.py`, `tests/phase-b/` |
| **Phase B integrity** | Canonical-evidence gate/axiomatic marker; active-empty-evidence advisory; relation-triage advisory + report shape; academic-source report; entity review transitions (fixture root); deterministic entity campaign | `tests/curation/test_phase_b_integrity.py` |
| **Webapp core** | Git-ignored workflow; upload + text extraction; unsupported-type retention; fail-closed LLM provider; candidate validation/staging; connection endpoint resolution; provider abstraction (Antigravity local agent fail-closed, Gemini/Vertex/OpenAI-compatible adapters, `agy` command shape, model listing, sign-in guidance) | `tests/webapp/test_webapp_core.py` |
| **Domain invariants** | Curriculum-agnosticism of content (generality) with scientific-terminology awareness | `tests/curation/test_generality.py`, `tests/phase-b/test_boundary.py` |
| **Provenance tests** | Agent registry resolution; `external_ids` formats; consumer docs state the current export version | `tests/provenance/` |
| **Determinism/compatibility** | Byte-identical regeneration; export conforms to contract; contract rejects missing members | `tests/versioning/` |
| **Validator report contract** | `reports/validation-report.json` shape (`results[]`/severity/`errors[]`/`warnings[]`/`info[]`/`severity_counts`/versions/`content_hash`), `--json` emits only the report, advisory anomalies | `tests/versioning/test_validation_report.py` |
| **Repository integrity** | Ecosystem independence; docs set complete and non-contradictory (index↔files); README status truth | `tests/repo/` (new with the refoundation) |
| **Adapter integration** | The first-party Python adapter loads the real export, mirrors policy counts, resolves aliases, traverses prerequisites, exercises CLI, and serves the local JSON API | `adapters/python/tests/test_adapter.py` |
| **End-to-end (consumer)** | The explorer projects the graph from `connections[]` with trust annotation; rejects contract-violating exports | `explorer/scripts/verify-graph-projection.mjs` |

## 3. The verify chain

`scripts/verify_all.py` runs, in order: validator (+ machine-readable report)
→ status-truth → epistemic summary → advisory integrity anomalies → graph
analysis → review-aware exports → curation status → phase-b domain/boundary
tests → registry coherence → validation-report/contract + deterministic export
tests → curation tests → generality → id-immutability → provenance/agent tests
→ claim-identity → connection-immutability → campaign determinism →
git-history immutability guard → Python adapter integration tests → webapp core
tests → repository-integrity tests.

The validator report is deterministic (ADR-0033): `validate.py --json` emits
`reports/validation-report.json` to stdout as the only stdout content; exit
`0`/`1` is retained. `integrity_anomalies.py` is advisory in the chain
(`--strict` opts into ERROR gating).

Any failure stops the chain.

## 4. CI enforcement (`.github/workflows/ci.yml`)

1. **verify** — the full chain (full git history fetched for the guards),
   then `git diff --exit-code` over derived artifacts (freshness: a stale
   export fails the build).
2. **security** — gitleaks + secret-pattern scan of content.
3. **docs** — required authoritative documents exist.
4. **process** — branch naming + Conventional Commits on PRs.

## 5. Fixtures and data validation

- The canonical corpus itself is the primary fixture: most tests run against
  the real tree (integration-style by design — the corpus *is* the product).
- Pure-logic fixtures are inline (TDD cases for immutability detection,
  signatures, policies).
- The explorer verifies against the real export it will ship.

## 6. Regression strategy

- Regressions become named checks in the chain (e.g.
  `test_e1_regression.py`: reviewed-vs-canonical ambiguity can't return;
  `test_boundary.py`: canonical/derived boundary violations fail).
- Every ADR lands with the test that would have caught its violation.

## 7. Release gates

A release (tag) requires: chain green on main · derived artifacts fresh ·
versions single-sourced · MIGRATIONS current · no `proposed`-status registry
item silently promoted · human-review gates recorded as decided where the
change touched them.
