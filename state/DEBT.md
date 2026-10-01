# DEBT — Known Problems and Accumulated Debt

> Record debt **immediately** when found, not when it becomes urgent. An entry here
> is a claim about the current repository, so it carries a location and a way to
> confirm it. Newest at the bottom.

---

## DEBT-001 — `PROGRESS.md` "Current State" block was stale (RESOLVED)

**Found:** 2026-10-01 by `A7F3` · **Resolved:** 2026-10-01 by `A7F3` (session `20261001-1153-A7F3-debt-cleanup`)
**Severity was:** medium — it is a status document, so a wrong status is actively misleading

**What was wrong.** The block, headed *"Current State (verified 2026-09-22)"*, stated
*"1 entity (metre, `draft`), 0 connections"* (metre is now **canonical** with **2**
connections) and *"24 requirements **PROPOSED** awaiting owner approval"* (now **24
VERIFIED / 1 UNVERIFIED**).

**Why it mattered.** The file's own preamble *and* its "Ground rules for this file" section
both say it tracks *work, not corpus counts*, and that counts live in the README status-truth
block. The docs contract says the same (`note: "work tracker; counts owned by status_truth"`).
The block was violating the file's own rule.

**Fix — structural, not a refresh.** The block now holds **no machine-owned values**; it is a
table pointing at each single source (`state/DASHBOARD.md`, the README status block,
`spec/machine-readable/verification.yaml`, `spec/CONFLICTS.md`, `docs/ARCHITECTURE-V2.md`,
`.github/workflows/ci.yml`). Refreshing the numbers would only have reset the drift clock.

**Verified:** `docs.py check` PASS (PROGRESS.md is link-scoped, so its new links are
resolved), `verify_all.py` 42 OK / 0 FAIL, `pytest` 360 passed.

---

## DEBT-002 — Retired repo path in live docs broke attestation verification (RESOLVED)

**Found:** 2026-10-01 by `A7F3` · **Resolved:** 2026-10-01 by `A7F3` (session `20261001-1153-A7F3-debt-cleanup`)
**Severity was:** **higher than first recorded** — see the correction below

**Correction to the original entry.** This was first written as *"low–medium — commands still
work via GitHub redirect"*. **That was wrong, and it was wrong in the dangerous direction.**
Verified empirically against the real release:

```
gh release download v3.0.0 -R STEMORG2026/STEMMA -p manifest.json
gh attestation verify manifest.json --repo STEMORG2026/STEMMA   # exit 0  ✅
gh attestation verify manifest.json --repo Er-Sajan-PLG/STEMMA  # exit 1  ❌
                                                                # "Error: verifying with issuer sigstore.dev"
```

The redirect covers git and API operations but **not** attestation verification. The
documented command was **broken**, and a reader following it would see a verification failure
and could reasonably conclude the release was untrustworthy. That is a security-relevant
documentation defect.

**Scope was also understated.** A sweep found **six** live files, not the two originally
listed. Four were in `docs/API.md` and are the *same broken procedure* — including
`expected_repository="Er-Sajan-PLG/STEMMA"`, a security parameter that fails closed (the right
direction, but it still breaks a documented safety check).

**Fixed** (8 occurrences across 4 files): `docs/API.md` (4), `schema/api.yaml` (1),
`README.md` (1), `explorer/src/services/feedback.ts` (1). Verified first that nothing depended
on the old values: no gate reads `authority.yaml`'s `repository` field, and no test pins the
feedback URL. Explorer re-verified after the change — `npm run verify` 10 PASS, `npm run
typecheck` clean, `verify-grounded-chat.mjs` PASS.

**Deliberately NOT fixed — three are Tier 2 (owner-only).** `spec/ROLES_AND_AUTHORITY.md:4`,
`spec/PILOT_CHARTER.md:6` and `spec/machine-readable/authority.yaml:2` still carry the old
name. `spec/` is owner-only under Constraint D, so the executor must not edit them. Raised as
**BLK-004** for the owner.

**Correctly left alone:** `.github/workflows/pages.yml:6` (a historical explanation, accurate
as written), `adapters/python/tests/**` (deliberately exercise redirect/fork/symlink handling
with arbitrary repo strings), `archive/**` (historical by definition).

**Lesson.** "It still works via redirect" is a claim to **test**, not to assume. The redirect
is real for git and the API but does not extend to attestation verification — and a broken
*verification* command is worse than a broken link, because its failure looks like a
trust problem rather than a typo.

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

---

## DEBT-006 — A generated artifact was invisible to CI (RESOLVED)

**Found:** 2026-10-01 by `A7F3` · **Resolved:** 2026-10-01 (same session)
**Severity was:** medium — a committed stale artifact could pass CI

**How it was found.** By sweeping for the *siblings* of a pattern already fixed once, rather
than treating it as a one-off: **a check that reads a state something else has already
normalised cannot detect drift in that state.** The earlier instance was
`verify_strong.check_consumer_registry`, which read a tree the chain had just regenerated.

**The defect.** `spec/machine-readable/review_manifest.json` is a committed, generated artifact
whose staleness no CI gate could detect:

1. Its in-chain guard is **vacuous**. The chain runs `review_manifest.py` (write) and then
   `review_manifest.py --check` — so the check compares the file against the version the chain
   wrote moments earlier. Verified: tampering with the committed manifest leaves the chain at
   **exit 0**, and the tampering is silently **overwritten** (0 occurrences of the marker
   afterwards).
2. CI's freshness diff was **path-filtered** to `-- exports reports`, and the manifest lives
   under `spec/`. Verified directly: with a `spec/` file modified, the filtered diff returns
   **0** (blind) while the unfiltered diff returns **1**.

So the only thing protecting it was the **local pre-push hook**, whose blanket
`git diff --exit-code` does see it. Hooks are not cloned, so a contributor without hooks — or a
commit made through the web UI — could land a stale manifest with CI green.

**Control.** `export_jsonld.py --check` was tested the same way and **does** fail correctly
(exit 1, named step), because nothing regenerates `knowledge.jsonld` before it. That contrast is
what makes the finding specific rather than a general complaint about `--check`.

**Fix — the class, not the instance.** The path filter expressed a weaker invariant than
intended. The real invariant is *"after the generators run, no tracked file is modified."* Four
sites carried the filter; all four now diff the whole tree:

| Site | Was |
|---|---|
| `ci.yml` — verify-knowledge-base, chain freshness | `-- exports reports` |
| `ci.yml` — test-suite, "tests mutated derived artifacts" | `-- exports reports` |
| `ci.yml` — adapter-verify, same | `-- exports reports` |
| `release.yml` — chain + artifacts fresh at tag | `-- exports reports` |

Broadening is **safe**, and that was verified before applying it rather than assumed: on a clean
checkout the chain, the full pytest suite, and the adapter suite each leave a blanket
`git diff --exit-code` at **exit 0** with no untracked files. So a non-empty diff now means
genuinely stale or mutated content, and it covers every generated artifact rather than a
hand-maintained list — the same fragility that made this possible.

**Verified after the fix:** with a `spec/` file modified, the old command exits 0 and the new one
exits 1. Workflow YAML still parses.

**Lesson.** A path filter on a freshness check is a hand-maintained allow-list of "places things
get written", and it silently goes stale when a new generated artifact appears elsewhere. Where
the invariant is "nothing changed", say exactly that.

---

## DEBT-007 — A test deletes a tracked file, so it is environment-sensitive (mitigated)

**Found:** 2026-10-01 by `A7F3`, when a pre-push run failed and blocked a push
**Severity:** medium — it produced a *false* regression signal and blocked delivery
**Status:** mitigated (the failure is now diagnosable; the underlying fragility remains)

**What happened.** A push was blocked by the pre-push hook:

```
FAILED tests/repo/test_promotion_chain.py::test_missing_enforcement_registry_fails_closed
1 failed, 17 passed in 3.09s
```

The test **passed 5/5 when run directly**. The hook log carried the real cause:

```
[safe-delete][SAFE_DELETE_BULK_CONFIRM_REQUIRED] {... "targets":
  [".../spec/machine-readable/enforcement_rules.yaml"] ...}
```

**Root cause.** `test_missing_enforcement_registry_fails_closed` removes the **real, tracked**
`spec/machine-readable/enforcement_rules.yaml` and restores it in `finally`. This environment
intercepts file deletion — `unlink()` is routed through a trash-move helper which emits
`[safe-delete]` messages, and **raises** when it cannot complete the move
(`SAFE_DELETE_FAIL_CLOSED`), or when a per-turn delete budget is exceeded
(`SAFE_DELETE_BULK_CONFIRM_REQUIRED`, threshold 50). When the removal is blocked, the registry
stays in place, `validate.py` then *succeeds*, and the test fails on
`assert r.returncode != 0` — a message that points at the gate rather than at the blocked
setup step.

**Why this is a real repo defect and not just an environment quirk.** Two properties are wrong
on the repository's side of the line:

1. **It mutates a tracked file to test a behaviour.** A crash or an interrupt between
   `unlink()` and the `finally` leaves the repository without a registry that every gate reads.
   That is the same class as DEBT-005, which was also a test mutating real state.
2. **A blocked setup step fails as if the *code* regressed.** Nothing distinguished "the
   fail-closed behaviour is broken" from "we could not set up the scenario".

**Mitigation applied.** The test now:
- catches an exception from `unlink()` and **skips** with the exception text, and
- verifies the file is actually gone before asserting, and **skips** with a reason if a guard
  intercepted the removal.

Verified both ways: normal path **passes**; with the directory made read-only the test
**skips** (1 skipped) instead of failing, and the registry is left byte-identical.

**Residual fragility — not fixed.** The test still touches the real tree. The clean fix is a
**shadow tree**, the pattern already used by `tests/repo/test_gate_fail_closed.py`: copy the
minimal tree into `tmp_path` and break it there, so nothing real is mutated. That requires
`validate.py` to resolve the registry path relative to the tree root it is run from, which is a
larger change than this defect justifies on its own. Recorded as the recommended follow-up.

**Lesson.** A test whose *setup* mutates tracked state cannot distinguish "the behaviour
regressed" from "the environment stopped me". Verify the setup took effect, and say which of
the two happened.

---

## DEBT-007 — A test deletes a tracked file, so it is environment-sensitive (mitigated)

**Found:** 2026-10-01 by `A7F3`, when a pre-push run failed and blocked a push
**Severity:** medium — it produced a *false* regression signal and blocked delivery
**Status:** mitigated (the failure is now diagnosable; the underlying fragility remains)

**What happened.** A push was blocked by the pre-push hook:

```
FAILED tests/repo/test_promotion_chain.py::test_missing_enforcement_registry_fails_closed
1 failed, 17 passed in 3.09s
```

The test **passed 5/5 when run directly**. The hook log carried the real cause:

```
[safe-delete][SAFE_DELETE_BULK_CONFIRM_REQUIRED] {... "targets":
  [".../spec/machine-readable/enforcement_rules.yaml"] ...}
```

**Root cause.** `test_missing_enforcement_registry_fails_closed` removes the **real, tracked**
`spec/machine-readable/enforcement_rules.yaml` and restores it in `finally`. This environment
intercepts file deletion — `unlink()` is routed through a trash-move helper which emits
`[safe-delete]` messages, and **raises** when it cannot complete the move
(`SAFE_DELETE_FAIL_CLOSED`), or when a per-turn delete budget is exceeded
(`SAFE_DELETE_BULK_CONFIRM_REQUIRED`, threshold 50). When the removal is blocked, the registry
stays in place, `validate.py` then *succeeds*, and the test fails on
`assert r.returncode != 0` — a message that points at the gate rather than at the blocked
setup step.

**Why this is a real repo defect and not just an environment quirk.** Two properties are wrong
on the repository's side of the line:

1. **It mutates a tracked file to test a behaviour.** A crash or an interrupt between
   `unlink()` and the `finally` leaves the repository without a registry that every gate reads.
   That is the same class as DEBT-005, which was also a test mutating real state.
2. **A blocked setup step fails as if the *code* regressed.** Nothing distinguished "the
   fail-closed behaviour is broken" from "we could not set up the scenario".

**Mitigation applied.** The test now:
- catches an exception from `unlink()` and **skips** with the exception text, and
- verifies the file is actually gone before asserting, and **skips** with a reason if a guard
  intercepted the removal.

Verified both ways: normal path **passes**; with the directory made read-only the test
**skips** (1 skipped) instead of failing, and the registry is left byte-identical.

**Residual fragility — not fixed.** The test still touches the real tree. The clean fix is a
**shadow tree**, the pattern already used by `tests/repo/test_gate_fail_closed.py`: copy the
minimal tree into `tmp_path` and break it there, so nothing real is mutated. That requires
`validate.py` to resolve the registry path relative to the tree root it is run from, which is a
larger change than this defect justifies on its own. Recorded as the recommended follow-up.

**Lesson.** A test whose *setup* mutates tracked state cannot distinguish "the behaviour
regressed" from "the environment stopped me". Verify the setup took effect, and say which of
the two happened.
