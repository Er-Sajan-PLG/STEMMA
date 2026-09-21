# EVIDENCE REGISTER — CORE-GATE-EXPORT slice

Protocol §5–6. Classes: `FACT` (demonstrably present), `CLAIM` (asserted by a
source, not verified), `INFERENCE` (analyst's conclusion from evidence).
Canonical machine copy: `spec/machine-readable/evidence.yaml`.
All observations made at baseline commit `fb66dd9` on 2026-09-22 unless noted.

## GATE

| ID | Class | Conf | Locator | Observation |
|---|---|---|---|---|
| EVID-STEMMA-GATE-001 | FACT | HIGH | cmd `python3 scripts/verify_all.py` → exit 0 | Full gate chain passes: validate, status_truth, physics checks, hitl, graph_analysis, export_review_aware, registry/domain/versioning tests, semantic pipeline checks |
| EVID-STEMMA-GATE-002 | FACT | HIGH | cmd: run verify_all with interpreter lacking pyyaml → printed `FAIL: .../validate.py`, **exit 1** | Gate fails closed: a failing step stops the chain with non-zero exit |
| EVID-STEMMA-GATE-003 | FACT | HIGH | cmd `python3 scripts/validate.py` → stdout | `OK: 1 entities valid; export written to exports/knowledge.json` + `reports/validation-report.json` written |
| EVID-STEMMA-GATE-004 | FACT | MEDIUM | cmd validate.py without deps → exit 2, `error: PyYAML is required`; requirements.txt @ 6f90c32 | Dependencies now declared (ROADMAP R0 item closed) |
| EVID-STEMMA-GATE-005 | FACT | HIGH | `.github/workflows/ci.yml:238-253` (test-suite job), `:262` (all-green needs) | CI runs full pytest and the all-green gate requires it |
| EVID-STEMMA-GATE-006 | FACT | HIGH | cmd `python3 scripts/status_truth.py` → stdout | `OK: README status block matches live counts (1 entities, 0 connections, 0 canonical assertions)` — status honesty is gated |
| EVID-STEMMA-GATE-007 | FACT | HIGH | cmd `python3 tests/repo/test_docs_consistency.py` → exit 0 | ADR-0029 invariant live: required docs exist, docs/README.md indexes exactly the existing docs, no living doc links a retired doc, VERSION keys present |
| EVID-STEMMA-GATE-008 | FACT | HIGH | cmd `python3 tests/repo/test_independence.py` → exit 0 | ADR-0027/0051 invariant live: no retired-doc refs, no ecosystem-controller refs, no retired ID namespace outside history |
| EVID-STEMMA-GATE-009 | FACT | HIGH | cmd output 2026-09-22 @ef9a315: `16 failed, 163 passed` while `main` CI was green | Full-suite failures were previously invisible to CI (test-suite job did not exist) |
| EVID-STEMMA-GATE-010 | FACT | MEDIUM | `scripts/verify_all.py:48-54` | Derived-layer checks (embeddings/RAG/consumer) are INFO, not FAIL, by design comment `# Don't fail, just info` |

## CORE

| ID | Class | Conf | Locator | Observation |
|---|---|---|---|---|
| EVID-STEMMA-CORE-001 | FACT | HIGH | `content/physics/measurement-units/metre.md:1-40`; `ls connections/` (empty); `ls sources/` (3 files) | Corpus: 1 entity (metre, `status: draft`, `writer: human:curator.001`), 0 connections, 3 source records |
| EVID-STEMMA-CORE-002 | FACT | MEDIUM | cmd `grep -rn "src.halliday\|src.newton" content/ connections/` → empty | 2 of 3 source records are unreferenced by any canonical content |
| EVID-STEMMA-CORE-003 | FACT | HIGH | `schema/concept.schema.json:19`, `:115`, `:5` | Entity IDs must match `^stemma:…`, source IDs `^stemma:src.…`; schema self-describes "ADR-0027" namespace |
| EVID-STEMMA-CORE-004 | FACT | HIGH | `metre.md:7` (`status: draft`); `.gitignore:10` (`workflow/`); gate output `OK: HITL workflow has human edits` | The only entity is draft; the HITL audit trail proving human edit lives in the git-ignored `workflow/` directory — not reproducible from the repository alone |
| EVID-STEMMA-CORE-005 | CLAIM | MEDIUM | `docs/ROADMAP.md` (R4 section); `docs/decisions/0052-content-acceptance-test.md` | Intent: next milestone seeds 3–5 entities, 2–3 connections proving both authority tiers — not yet implemented |

## SCH

| ID | Class | Conf | Locator | Observation |
|---|---|---|---|---|
| EVID-STEMMA-SCH-001 | FACT | HIGH | `schema/VERSION.yaml` (schema_version 1.2.0, export_version 2.2.0, relation_registry_version 1.0.0) | Single version source of truth |
| EVID-STEMMA-SCH-002 | FACT | HIGH | cmd: registry parse → 15 `status: adopted`; `scripts/physics_core_profile_check.py:7`, `:138-139` | Registry adopts 15 relations incl. `related_to`; physics-core profile restricts to 8 and forbids `related_to` — the two statements are scope-compatible, not contradictory |
| EVID-STEMMA-SCH-003 | FACT | MEDIUM | `tests/registry/test_registry_coherence.py:19-37`, `:73-83`; registry entries w/ `inverse: null` | Coherence rules: named inverses must be mutual; symmetric ⇒ no inverse; non-symmetric MAY carry null inverse; adopted w/ named inverse ⇒ must exist |
| EVID-STEMMA-SCH-004 | FACT | HIGH | `schema/api.yaml:4` (`version: 2.2.0`) | OpenAPI document version tracks the export contract |

## EXP

| ID | Class | Conf | Locator | Observation |
|---|---|---|---|---|
| EVID-STEMMA-EXP-001 | FACT | HIGH | cmd: json.load(exports/knowledge.json) | `export_version: 2.2.0`, `content_hash: sha256:2c007fc6e235b0ac…`, 1 entity / 0 connections / 3 sources |
| EVID-STEMMA-EXP-002 | FACT | HIGH | CI `no-wall-clock` job; `tests/versioning/test_deterministic_export.py` via cmd pytest exit 0 | Export regenerates byte-identically; no wall clock; content_hash stamped |
| EVID-STEMMA-EXP-003 | FACT | HIGH | gate output lines `OK: all -> … knowledge.all.json` … `rejected`; `ls exports/` | Seven review-aware variant exports are derived from the same corpus deterministically |
| EVID-STEMMA-EXP-004 | FACT | HIGH | `exports/vector_store/meta.json` (`"type": "faiss"`); `scripts/embed.py:227`, `:241-244` (`# Fallback: write vectors.json` … "numpy not available") | meta.json declares `type: faiss` even when the store is the deterministic JSON fallback (`vectors.json` + `meta.json` + `ids.json`) — label/behavior divergence |
| EVID-STEMMA-EXP-005 | FACT | MEDIUM | head of `exports/embeddings.jsonl`; `docs/TESTING.md` embedding section | 1 embedding record (all-MiniLM-L6-v2, 384-dim) produced by deterministic hash-based fallback when torch/sentence-transformers absent |
| EVID-STEMMA-EXP-006 | FACT | MEDIUM | `exports/consumers/learninghub/knowledge.learninghub.json`; gate output | learninghub consumer export contains 0 entities (review_policy `canonical`; corpus is all-draft). general export contains the draft entity |

## HITL / SEC / OPS / INTEG

| ID | Class | Conf | Locator | Observation |
|---|---|---|---|---|
| EVID-STEMMA-HITL-001 | FACT | MEDIUM | gate output `OK: HITL workflow has human edits` | hitl_check reads the git-ignored workflow audit trail and passes |
| EVID-STEMMA-HITL-002 | FACT | HIGH | `metre.md` frontmatter (`ai_drafted: false`, `writer: human:curator.001`) | The entity is human-written by declaration in its own metadata |
| EVID-STEMMA-SEC-001 | FACT | HIGH | `.github/workflows/ci.yml:52-53` + no-secrets grep step | Secret scanning (gitleaks) + canonical no-secrets grep in CI |
| EVID-STEMMA-SEC-002 | FACT | MEDIUM | CI verify-knowledge-base step "Check no embeddings in canonical content" | Canonical layer scanned for forbidden vector material |
| EVID-STEMMA-OPS-001 | FACT | HIGH | cmd `python3 -m pytest tests/ -q` → `133 passed` @fb66dd9 | Full suite green after hygiene commits |
| EVID-STEMMA-OPS-002 | FACT | MEDIUM | `.pre-commit-config.yaml` (`verify-all` hook, `always_run: true`) | Pre-commit runs the entire gate chain on every commit |
| EVID-STEMMA-OPS-003 | FACT | HIGH | `git log fb66dd9^..fb66dd9 --oneline`; `git diff main --shortstat` (104 files, +578/−5545) | 2026-09-22 hygiene sweep (owner-authorized): archived old design, removed duplicates, fixed drift — pre-pilot remediation context |
| EVID-STEMMA-INTEG-001 | FACT | MEDIUM | cmd `grep -rn StemmaRAG adapters/ --include="*.py"` → 0 hits; 9 doc lines in GOVERNANCE/CONSUMERS/GUIDELINE | `StemmaRAG` is referenced in docs but does not exist in the adapter package |
| EVID-STEMMA-INTEG-002 | CLAIM | MEDIUM | `schema/consumer-registry.yaml` | Four consumers declared (learninghub, professor-j, stemma-explorer, general) with review_policy/domain preferences — declared intent |
| EVID-STEMMA-INTEG-003 | CLAIM | MEDIUM | `docs/CONSUMERS.md`, `docs/GOVERNANCE.md` consumer sections | Intended usage patterns (models, top_k, review policies) are documentation claims, unverified against any running consumer |
| EVID-STEMMA-EXP-007 | CLAIM | LOW | `docs/CONSUMERS.md` (learninghub 0-entities "correct per review_policy") | The empty learninghub export is asserted intended; not owner-confirmed |
| EVID-STEMMA-OPS-004 | INFERENCE | MEDIUM | `git diff main --stat` (12→11 model fix, contract-version edits in >10 files, 2026-09-22) | Hardcoding counts/versions in many prose locations is the demonstrated drift mechanism; machine-owned single sources (status_truth, VERSION.yaml) are the working countermeasure |

## Excluded (§5.3)

`archive/` (immutable history), `explorer/node_modules`/build outputs (vendor/generated), `.git` internals, git-ignored `workflow/` contents (inspected only via `hitl_check` gate, not committed — see UNRES-STEMMA-HITL-001).
