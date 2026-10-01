# SESSION: 20261001-1123-A7F3-race-fix-bootstrap

**Agent:** `A7F3`
**Model:** DeepSeek-V4.1-Flash  <!-- backfilled 2026-10-02; the field was introduced by Amendment 2 -->
**Session ID:** `20261001-1123-A7F3-race-fix-bootstrap`
**Started:** 2026-10-01T11:23Z
**Status:** COMPLETED
**Branch:** `docs/owner-rulings-unverified`
**Base commit:** `08cecb3`  <!-- A6 schema, backfilled 2026-10-01 -->
**Task:** (1) fix the export read/write race; (2) adopt MACP and bootstrap `state/`.
**Files owned:** `state/**`, `scripts/atomic_write.py`, `tests/repo/test_atomic_artifact_writes.py`, `tests/repo/test_state_tree.py`, `AGENTS.md`, `docs/docs-contract.yaml`

> Append-only. Do not edit earlier entries. Add new entries at the end.
>
> **Agent-ID note.** `A7F3` is this agent's MACP identifier. The same agent appears as
> `llm:coding-agent.001` in STEMMA canonical provenance (`provenance.writer`). Keep the two
> aligned so a session can be traced to the records it touched.

---

## [START] 2026-10-01T11:23Z — work unit 1: the export race

**Intended work.** Fix a known read/write race: a spurious failure in
`tests/repo/test_export_consumers.py::test_every_registry_consumer_has_a_fresh_committed_bundle`
observed when the pytest suite ran concurrently with `scripts/verify_all.py`.

## [DISCOVERY] The failure is a torn read, not a logic error

The failing assertion was the `export_consumers.py --all --check` subprocess returning
non-zero. `--check` regenerates each bundle in memory and compares it to the file on disk,
so any read that does not return a **complete document** is indistinguishable from a
genuinely stale bundle.

Root cause: `Path.write_text` opens the destination with mode `"w"` — truncating it — and
only then writes. Between those two moments the file is empty or a prefix of the new
content. Six such write sites existed across five exporters.

## [DECISION] Stage-and-rename, applied only where a gate compares bytes

New `scripts/atomic_write.py`: write to a dot-prefixed sibling temp file, `flush`, `fsync`,
then `os.replace` over the destination. `os.replace` is atomic, so a reader sees either the
previous complete file or the new one.

Applied to the **nine** sites whose output a gate byte-compares. Deliberately **not**
applied to the ~50 other `write_text` sites (campaign/triage reports, ingestion staging,
canonical `content/`/`connections/`/`sources/` edits): no gate compares them and nothing
reads them concurrently with a regeneration, so converting them would widen the change
without closing a window. Recorded as DEC-002.

## [PROGRESS] Verification

- `tests/repo/test_atomic_artifact_writes.py` — 11 tests, including a **negative control**
  that reproduces the truncate-then-write window and asserts a reader really does observe a
  non-document, so the atomicity assertions cannot pass vacuously.
- **Sabotage-proven:** making `_atomic_replace` non-atomic → 4 red; reverting one exporter to
  bare `write_text` → structural guard red; restore → 11 passed.
- **Byte-parity:** all 34 `exports/`+`reports/` artifacts unchanged after regeneration.
- **End-to-end through the real CLI**, window widened to make the overlap deterministic:
  786/852 (92%) concurrent `--check` runs saw a torn bundle before; **0/75** after.

Committed `08cecb3`, pushed.

---

## [PIVOT] Work unit 2 — adopting MACP, and a correction

The owner supplied the MACP protocol and directed that it be adopted and acted on.

## [DISCREPANCY] The first copy of the protocol was truncated

The initial copy arrived **truncated mid-Section 6**, with **Section 7 (Bootstrap Protocol)
referenced but absent**. I reconstructed both and marked them `[RECONSTRUCTED]`.

The owner then supplied the **complete** text. The reconstruction was wrong in four
material ways:

| I assumed | Actual protocol |
|---|---|
| agent_id like `coding-agent.001` | **4 alphanumeric characters**, e.g. `C7A2` |
| session file `2026-10-01-atomic-writes.md` | `YYYYMMDD-HHMM-<AGENT-ID>-<slug>.md` |
| `INDEX.md` = navigation to state files | **Searchable log of all past sessions** |
| plans kept after completion | plans **deleted** when done |

Rather than leave a plausible-but-wrong protocol in the repo — the exact failure this
protocol exists to prevent — the state tree was **restructured** to the authoritative text
and the reconstruction removed. Recorded as DEC-005.

## [DISCOVERY] Section 7 requires a full repository audit

Performed below; this is the audit the bootstrap protocol mandates.

### Audit — languages and frameworks

| Language | Tracked files | Role |
|---|---|---|
| Markdown | 292 | canonical entities, docs, spec |
| YAML | 191 | connections, sources, registries, schemas, workflows |
| Python | 148 | pipeline + gates + tests |
| JSON | 58 | JSON Schema, derived exports |
| TypeScript | 17 | explorer consumer |
| Turtle / JSON-LD | 8 | semantic exports |
| `.mjs` | 3 | explorer verifiers (esbuild-bundled) |

### Audit — entry points and build system

- **Build:** `Makefile` (targets: `verify`, `validate`, `strong-verify`, `quick-verify`,
  `docs`, `docs-sync`, `docs-impact`, `docs-coverage`, `security`, `deterministic`,
  `no-wall-clock`, `id-immutability`, `ci-local`, `all`). No `pyproject.toml`/`setup.py`;
  the repo is scripts + a `Makefile`, not an installable package.
- **Primary entry points:** `scripts/verify_all.py` (the authoritative chain),
  `scripts/validate.py` (validate + write base export), `scripts/docs.py` (docs contract),
  `scripts/verify_strong.py`.
- **Consumer entry points:** `explorer/` (Vite/TS), `webapp/` (Python server),
  `adapters/python/` (SDK).

### Audit — test framework

- **pytest** (`requirements-dev.txt`: `pytest>=9.1.1,<10.0`), 356 tests currently.
- Two styles coexist: pytest suites under `tests/**`, and **self-hosting scripts** with a
  `__main__` runner (`tests/repo/test_gate_fail_closed.py`, `tests/repo/test_state_tree.py`)
  so they run under an interpreter without pytest.
- Suites: `tests/repo/`, `tests/registry/`, `tests/versioning/`, `tests/curation/`,
  `tests/webapp/`, `tests/provenance/`, `tests/metadata/`.
- **Important:** `tests/repo/test_promotion_chain.py` is pytest-only (uses fixtures), so the
  chain routes it to an interpreter that owns pytest and skips it visibly if none does.

### Audit — documentation

- `README.md` (status block is GENERATED), `AGENTS.md` (operating instructions),
  `PROGRESS.md` (work tracker), `SPECIFICATION_PROCESS_REVIEW.md`.
- `docs/` — 63 tracked files, governed by `docs/docs-contract.yaml`; `docs.py check` gates
  contract integrity, link resolution, generated freshness, and four named checks.
- `spec/` — the Specification Recovery Protocol artefacts (requirements, evidence, `UNRES`,
  conflicts, interfaces) plus a machine-readable registry set.
- **Rule:** new docs must be classified in the docs contract
  (`docs/DOCUMENTATION-SYSTEM.md` "Adding a new obligation").

### Audit — CI/CD

`.github/workflows/`: `ci.yml` (11 jobs incl. `test-suite`, `all-green`), `release.yml`
(draft final releases, owner-signed), `codeql.yml`, `pages.yml`, `branching-strategy.yml`,
`workflow-lint.yml`.

Seven **required** status checks on `main`: Validate Knowledge Base · Security scan · Verify
Governance Docs · Branching Strategy · Conventional Commits (commitlint) · All Checks Green
— Nothing Bad Gets Merged · Full Test Suite (pytest).

### Audit — directory structure

| Dir | Tracked | Purpose |
|---|---|---|
| `archive/` | 360 | superseded corpora and old designs — never canonical |
| `docs/` | 63 | living documentation set (contract-gated) |
| `scripts/` | 52 | pipeline and gates |
| `tests/` | 45 | pytest suites + self-hosting runners |
| `spec/` | 35 | Specification Recovery Protocol artefacts |
| `explorer/` | 29 | consumer: graph viewer + grounded chat |
| `adapters/` | 24 | consumer: Python SDK |
| `exports/` | 23 | **derived** artifacts (regenerable, byte-identical) |
| `reports/` | 21 | **derived** reports |
| `schema/` | 20 | JSON Schema + registries + `VERSION.yaml` |
| `content/` | 17 | **canonical** entities |
| `release/` | 15 | legacy release bundles |
| `webapp/` | 8 | consumer: ingestion UI |
| `examples/` | 6 | usage examples |
| `sources/` | 4 | **canonical** citations |
| `connections/` | 3 | **canonical** assertions |
| `state/` | — | MACP coordination state (this directory) |

`n8n/`, `proposals/`, `workflow/` exist on disk but hold no tracked files (`workflow/` and
`proposals/` are git-ignored working areas by design).

### Audit — conventions

- **Commits:** Conventional Commits, enforced by commitlint. Allowed types: `feat, fix,
  docs, style, refactor, perf, test, build, ci, chore, revert, merge`. Subject case and
  line lengths are disabled; **type is strictly enforced**.
- **Hooks:** `.pre-commit-config.yaml` plus a repo `pre-push` hook running the chain, strong
  verification, an exports/reports freshness diff, and `docs.py sync`/`check`.
- **Determinism:** no wall-clock, no randomness in export generation; exports regenerate
  byte-identically.
- **Docs loop:** `docs.py impact → sync → check` must be closed before a task is complete.

### Audit — current health

- Working tree clean except this session's own changes.
- `pytest` 356 passed · `verify_all.py` 42 OK / 0 FAIL · `verify_strong.py --quick` exit 0 ·
  `docs.py check` PASS · recovery validator PASS (9/9).
- Requirements: 24 VERIFIED / 1 UNVERIFIED of 25. `UNRES`: 9 CLOSED / 1 DEFERRED / 1 OPEN.
- **No failing tests, no active blockers other than the owner merge of PR #66.**

### Audit — dependencies

- Runtime: `pyyaml>=6.0.3,<7.0`, `jsonschema>=4.26.0,<5.0` (`requirements.txt`).
- Dev: `pytest>=9.1.1,<10.0` (`requirements-dev.txt`).
- Node: `explorer/package.json` (Vite/TS).
- **Environment inconsistency found:** `numpy` is present for `/usr/bin/python3` but absent
  from `.venv`, and `scripts/embed.py` selects its vector-store type from numpy
  availability. Recorded as DEBT-004.

## [DEBT] Found during the audit

- **DEBT-001** — `PROGRESS.md`'s "Current State" block is stale (says metre is `draft` with
  0 connections and 24 requirements PROPOSED; actually metre is canonical with 2 connections
  and 24 VERIFIED).
- **DEBT-002** — the retired repo path `Er-Sajan-PLG/STEMMA` still appears in live,
  user-facing docs (`docs/API.md:92`, `adapters/python/README.md:52`).
- **DEBT-003** — residual publish-*order* window between the base export and the bundles
  derived from it (an ordering property; `os.replace` cannot fix it).
- **DEBT-004** — `.venv` and `/usr/bin/python3` disagree about `numpy`.
- **DEBT-005** — one unreproduced `content_hash` mismatch during a full-suite run.

## [PROGRESS] Structure created

Per Section 7 step 2: `DASHBOARD.md`, `REGISTRY.md`, `INDEX.md`, `ARCHITECTURE.md`,
`DECISIONS.md`, `DEBT.md`, `BLOCKERS.md`, and `sessions/`, `plans/`, `conflicts/`,
`archive/` — populated from the audit above rather than from assumption.

## [DECISION] Boundary with the repository's own governance

MACP Tier 1 grants agents sovereignty over `state/`; STEMMA's Constraint D reserves
requirement rulings to the owner. These compose once scoped — `state/DECISIONS.md` holds
*coordination* decisions, `spec/` holds *specification* rulings — but the boundary is
written down explicitly in `conflicts/CONFLICT-001-state-tier2-boundary.md` and DEC-001/
DEC-003 so a later agent cannot mistake `state/` for a second source of truth.

## [PROGRESS] Guards added

`tests/repo/test_state_tree.py` enforces the protocol's own completion criteria: required
structure, no placeholder text, every relative link resolves, every REGISTRY session id has
a session file, and **DASHBOARD's counts equal the live registries**. Sabotage-proven: a
wrong requirement count, a wrong `UNRES` count, and a broken `INDEX.md` link each turn the
relevant test red; restore returns green.

---

## [START] 2026-10-01T11:23Z — work unit 2 continues: conformance rework

## [DISCREPANCY] Conformance gaps corrected

Restructured to the authoritative protocol:

| Was | Now |
|---|---|
| `sessions/2026-10-01-atomic-writes.md` | `sessions/20261001-1123-A7F3-race-fix-bootstrap.md` (this file) |
| agent_id `coding-agent.001` | agent_id `A7F3` (4 alphanumeric chars) |
| `INDEX.md` as navigation | `INDEX.md` as a **searchable session log** |
| `plans/atomic-write-race.md` retained | plan deleted when complete (protocol §5) |
| no reconciliation timestamp | `DASHBOARD.md` carries **Last Reconciled** |
| `PROTOCOL.md` with `[RECONSTRUCTED]` text | authoritative full text, no reconstruction |

## [BLOCKER] One owner action required

PR #66 needs the owner to merge it. All checks green, no conflicts. Recorded as BLK-001 —
an executor may prepare and verify a change but may not land it on the owner's authority.

## [PROGRESS] Guards rewritten to the authoritative conventions

`tests/repo/test_state_tree.py` was **rewritten**, not patched: the first version encoded
this agent's own assumptions (date-only session filename, `coding-agent.001`-style ids,
`INDEX.md` as navigation). It now enforces the specification — session filename pattern,
4-alphanumeric agent ids, plan filename pattern, a parseable **Last Reconciled** stamp, an
`INDEX.md` row per session, no placeholder markers, link resolution, and dashboard↔registry
drift. 11 checks.

Its placeholder rule was also fixed: the original flagged the *word* "placeholder", so the
protocol text that defines the rule failed the rule. It now flags only line-initial markers
(`TODO`/`TBD`/`FIXME`/`XXX`) plus `lorem ipsum` and `<PLACEHOLDER>` — a marker, not a mention.

**Sabotage-proven**, six ways, each turning the relevant check red and restoring green:

| Sabotage | Caught by |
|---|---|
| session file renamed out of the convention | `test_session_filenames_follow_the_protocol_convention` (+ INDEX coverage) |
| `Last Reconciled` made unparseable | `test_dashboard_has_a_parseable_last_reconciled_timestamp` |
| session removed from `INDEX.md` | `test_every_session_file_has_an_index_row` |
| agent id `coding-agent.001` | `test_registry_agent_ids_are_four_alphanumeric_characters` |
| plan renamed `my-plan.md` | `test_plan_filenames_follow_the_protocol_convention` |
| dashboard counts drifted | `test_dashboard_requirement_counts_match_the_registry` |

## [BUG FOUND] Sabotage harness damaged the tree; repaired

The first sabotage driver used `os.rename` across a device boundary (`/home` → `/tmp`),
which raised `OSError: Invalid cross-device link` mid-run and left the session file renamed
to `atomic-writes-session.md`. Repaired by renaming it back; content was intact and the
guard returned 11/11. The driver was rewritten to keep all renames inside the repository and
to restore by original filename.

**Lesson for future sessions:** a sabotage harness mutates real files, so its own failure
handling matters more than its assertions. Restore by explicit original path, and never
`rename` across devices — use a same-directory rename or `shutil.move`.

## [END] 2026-10-01 — session closed

**Delivered.**

1. **Export read/write race fixed** — `scripts/atomic_write.py` (stage + `os.replace`),
   applied to the nine gate-compared write sites. 92% torn reads before, 0% after; 34/34
   artifacts byte-identical; 11 tests with a negative control; sabotage-proven. Committed
   `08cecb3`, pushed.
2. **MACP adopted and `state/` bootstrapped** from a full §7 repository audit, then
   **restructured** to the authoritative protocol after the first copy proved truncated.

**Final gate state:** `pytest` 356 passed · `verify_all.py` 42 OK / 0 FAIL ·
`verify_strong.py --quick` exit 0 · `docs.py check` PASS · recovery validator PASS (9/9,
88 evidence, 25 requirements) · state tree **11/11**.

**Ended clean:** DASHBOARD reconciled with a Last Reconciled stamp; REGISTRY row released
(`status: ended`, `files_owned` cleared); INDEX entry added; plan **deleted** (complete, per
§5); all state committed.

**Handoff.** The only owner action outstanding is merging PR #66 (BLK-001). The open
`UNRES-STEMMA-CORE-003` and `REQ-STEMMA-OPS-002` both wait on a release, not on an agent.

---

## [BUG FOUND] 2026-10-01 — the `content_hash` intermittent, root-caused and fixed

The owner directed that the protocol apply from this point, mid-work. Continuing under it.

**Symptom.** `test_versioning_policy.py::test_content_hash_covers_exactly_the_canonical_sources`
failed twice across roughly twenty full-suite runs, never in isolation.

**Diagnosis path.** I first tested the obvious hypotheses and **disproved them**: the suite
does not leave a stale export (checked before/after a full run — fresh both times), no stray
process was writing, and 8 consecutive runs passed. Then I stopped theorising and looked at
the actual diff of the dirty artifact, which showed `exports/knowledge.json` had reverted to
the **fabricated** values `cleared_at: 09:00:00` / `clearance_evidence: "conn.000156
satisfied the obligation"` — values I had fixed in `54262d7`. Grepping for those strings
found them in exactly two places: an old release bundle, and **`tests/repo/test_promotion_chain.py`'s
hardcoded fixture literal**.

**Root cause.** `test_promotion_chain.py` mutates the **real** canonical records and runs
`scripts/validate.py`, which regenerates the **real** `exports/knowledge.json` and
`reports/validation-report.json` from the mutated state. Its `restore_records` fixture
restored only the canonical records — never the derived artifacts. Three further tests in
the module ran `validate.py` with **no fixture at all**, so they leaked too; one left the
report recording `conforms: false` with 2 ERRORs.

**Why it hid.** The failure appears on the run *after* one that left the export stale,
because that test reads the export at import time. Whether the export ended stale depended on
which test last ran `validate.py` — hence ~1-in-10, never reproducible in isolation.

**Fix.** `restore_records` now snapshots and restores the derived artifacts alongside the
canonical records, plus a **module-scoped autouse** fixture covering the whole module (so
fixture-less tests and skipped restores are caught too).

**Verified.** Five consecutive full runs: 360 passed, `git status` clean for `exports/` and
`reports/`. Sabotage-proven: emptying `_DERIVED_ARTIFACTS` makes both artifacts dirty again;
restoring returns them clean.

**Correction.** DEBT-005 was first written as an unexplained one-off with a concurrent-writer
hypothesis, and the *earlier* appearance of the same fabricated values (commit `2624321`) was
attributed to a `git stash` mishap during a bisect. **That attribution was wrong** — the test
introduced them, and the stash was incidental. DEBT-005 now records the real cause.

**Lesson.** A test that mutates real canonical files and invokes the real validator mutates
the *derived* artifacts too, and must restore all of them. Restoring the inputs but not the
outputs leaves a stale artifact that the next run reads. And when a hash assertion fails
intermittently, look for a test that *writes* the artifact before suspecting a concurrent
process.
