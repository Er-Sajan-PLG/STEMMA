# DEBT — Known Problems and Accumulated Debt

> Record debt **immediately** when found, not when it becomes urgent. An entry here
> is a claim about the current repository, so it carries a location and a way to
> confirm it. Newest at the bottom.

---

## DEBT-001 — `PROGRESS.md` "Current State" block is stale

**Found:** 2026-10-01 by `A7F3`
**Severity:** medium — it is a status document, so a wrong status is actively misleading
**Location:** `PROGRESS.md` lines 6–14

**What is wrong.** The block is headed *"Current State (verified 2026-09-22)"* and states:

- *"Canonical corpus: 1 entity (metre, `draft`), 0 connections, 3 source records"* — metre is
  now **canonical** (human-written + human-reviewed) and there are **2** connections.
- *"24 requirements **PROPOSED** awaiting owner approval; nothing self-approved"* — the
  requirements are now **24 VERIFIED / 1 UNVERIFIED**.

**Why it matters.** The file's own preamble says it tracks *work, not corpus counts, to
avoid drift* — yet the block that drifted is the corpus/verification summary. A reader
trusting it would conclude the project is at an earlier stage than it is.

**Fix.** Either re-verify and update the block, or delete the counts from it and point at
`state/DASHBOARD.md` / the README status block as the single source. The second is
preferable: it removes the drift surface rather than resetting it.

---

## DEBT-002 — Retired repo path `Er-Sajan-PLG/STEMMA` in live, user-facing docs

**Found:** 2026-10-01 by `A7F3`
**Severity:** low–medium — commands still work via GitHub redirect, but they teach the wrong path
**Locations (live, non-archive):**

| Location | Content |
|---|---|
| `docs/API.md:92` | `gh attestation verify knowledge.learninghub.json --repo Er-Sajan-PLG/STEMMA` |
| `adapters/python/README.md:52` | `Stemma.from_release("Er-Sajan-PLG/STEMMA", "v3.0.0-rc1", …)` |

**Context.** The repository is now `STEMORG2026/STEMMA`; `Er-Sajan-PLG/STEMMA` is a pure
redirect. The correct name is used elsewhere (`docs/API.md` also cites the new path in the
signing procedure), so the codebase is internally inconsistent.

**Not debt:** `adapters/python/tests/*` deliberately use the old name — they test
redirect/fork/symlink handling and arbitrary repo strings. `archive/**` is historical by
design. Do not "fix" either.

---

## DEBT-003 — Residual publish-order window between base export and derived bundles

**Found:** 2026-10-01 by `A7F3`, while fixing the torn-read race
**Severity:** low — requires a content change concurrent with a `--check` run
**Location:** conceptual; documented in `scripts/atomic_write.py` module docstring

**What it is.** DEC-002 made each *file* consistent, but the chain still publishes a *set*
over time: `exports/knowledge.json` is rewritten first, and the consumer bundles derived
from it after. A `--check` running concurrently with a **genuine content change** could
therefore see a new base against an old bundle and report it stale.

**Why it is not a torn read.** Every individual read is a complete document. This is an
ordering property, not an atomicity one, so `os.replace` cannot fix it.

**Why it is tolerable.** The chain and the pytest suite are separate CI jobs; locally,
content changes are not made concurrently with a run. Closing it properly would need
staging plus a single atomic swap of the whole `exports/` tree, which is disproportionate
to the risk.

---

## DEBT-004 — `.venv` and `/usr/bin/python3` disagree about `numpy`

**Found:** 2026-10-01 by `A7F3`
**Severity:** low, but it silently changes behaviour
**Location:** environment

**What it is.** `numpy` is installed for `/usr/bin/python3` and **absent** from `.venv`.
`scripts/embed.py` selects its vector-store type from numpy availability
(`numpy-flat` vs `json-flat`), so the same command produces a different store type
depending on which interpreter runs it.

**Why it matters.** The store type is recorded in `exports/vector_store/meta.json` and is
now guarded by `tests/repo/test_vector_store_type_truthfulness.py`, which asserts the label
matches the artifact on disk. That guard is satisfied either way, but a contributor
switching interpreters would see the artifact type change and might read it as a bug.

**Fix.** Pin the intended behaviour explicitly (either add `numpy` to `requirements.txt`
or document that the fallback is the reference path), rather than leaving it implicit in
which interpreter happens to be used.

---

## DEBT-005 — `test_promotion_chain.py` dirtied the derived artifacts (RESOLVED)

**Found:** 2026-10-01 by `A7F3`
**Status:** **RESOLVED** — fixed in `tests/repo/test_promotion_chain.py`
**Severity was:** high, though it presented as low

**Symptom.** A full `pytest tests/ -q` run intermittently reported:

```
FAILED tests/repo/test_versioning_policy.py::test_content_hash_covers_exactly_the_canonical_sources
```

The test hashes `content/`, `connections/`, `sources/` and compares against
`EXPORT["content_hash"]`, where `EXPORT` is read from `exports/knowledge.json` **at module
import time**. `git status` was clean for all three canonical directories, so the canonical
layer had not changed.

**Root cause.** `tests/repo/test_promotion_chain.py` mutates the **real** canonical records
(`metre.md`, `conn.000156.yaml`) and then runs `scripts/validate.py`, which regenerates the
**real** `exports/knowledge.json` and `reports/validation-report.json` from whatever
canonical state it finds. Its `restore_records` fixture restored only the two canonical
records — not the derived artifacts. So the export was left computed from the *mutated*
state, carrying a wrong `content_hash` and any fixture-injected field values.

Three further tests in the same module ran `validate.py` with **no** fixture at all
(`test_baseline_gate_is_green`, `test_missing_enforcement_registry_fails_closed`,
`test_board_waiver_retire_turns_chains_back_on`), so they leaked too — one of them left
`reports/validation-report.json` recording `conforms: false` with 2 ERRORs.

**Why it looked intermittent.** The failure appears on the run *after* one that left the
export stale, because the next run reads the export at collection time. Whether the export
ended stale depended on which test last invoked `validate.py` — so it reproduced roughly
once in ten runs, and never in isolation.

**Fix.** Two fixtures in `tests/repo/test_promotion_chain.py`:
`restore_records` now snapshots and restores the derived artifacts alongside the canonical
records, and a **module-scoped autouse** fixture snapshots them for the whole module so the
fixture-less tests and any skipped restore are covered too.

**Verified.** After the fix, running the module or the full suite leaves `git status` clean
for `exports/` and `reports/`; 360 passed on five consecutive full runs. Sabotage-proven:
emptying `_DERIVED_ARTIFACTS` makes both artifacts dirty again, and restoring returns them
to clean.

**Correction to an earlier record.** This was first written up as an unexplained one-off,
with a leading hypothesis about a concurrent writer, and an *earlier* occurrence of the same
fabricated values (commit `2624321`) was attributed to a `git stash` mishap during a bisect.
**That attribution was wrong.** The fabricated values `cleared_at: 2026-10-01T09:00:00+00:00`
and `clearance_evidence: "conn.000156 satisfied the obligation"` exist in exactly two places
in the repository: `test_promotion_chain.py`'s hardcoded fixture literal, and an old release
bundle. The test is what introduced them into `exports/knowledge.json` — the stash was
incidental.

**Lesson.** A test that mutates real canonical files and invokes the real validator is
mutating *derived* artifacts too, and must restore all of them. Restoring the inputs but not
the outputs leaves a stale artifact that the next run reads. When a hash-mismatch assertion
fails intermittently, look for a test that writes the artifact rather than for a concurrent
process.
