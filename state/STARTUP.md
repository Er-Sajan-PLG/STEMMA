# STARTUP — mandatory sequence (read before any work)

> The settled MACP revision (USA `AGENTS.md`, 2026-10-02) makes the startup sequence a
> **10-step** procedure and requires it to live in its own file. This is that file.
> `state/PROTOCOL.md` §6 and Amendment 2 both point here.
>
> **Registration moved from step 9 to step 1.** The gates shipped in PR #83 are enforced
> at PUBLISH time, so a session that skipped verification and never pushed failed nothing.
> On 2026-10-02 that is exactly what happened: recon was done, numbers were reported that
> had not been measured, and no session was ever registered — and no gate fired.
> Registration now comes first so that reconnaissance, and everything after it, is
> attributable to a session that exists.
>
> **Divergence, recorded not fixed:** `state/PROTOCOL.md` §3 still lists a 9-step sequence
> with registration at step 9. Amending the settled revision is the owner's call, so it is
> left as written; **this file is authoritative for ordering.**

Run these in order. **Do not begin work until all 10 are complete.** You are stateless;
the repository is not.

---

## STEP 1 — REGISTER YOURSELF

Create `state/sessions/YYYYMMDD-HHMM-<AGENT-ID>-<slug>.md`, beginning with the header
schema (see `state/PROTOCOL.md` Amendment 2 — `Agent`, `Model`, `Branch`, `Started`,
`Status: IN-PROGRESS`, `Base commit`, plus STEMMA's `Session ID`, `Task`, `Files owned`).

Add yourself to `state/REGISTRY.md`: agent ID (invent 4 alphanumeric characters), model,
branch, one-line task, current UTC timestamp, files claimed.

- [ ] Session file created with a complete header (all seven fields)
- [ ] REGISTRY row added, `Status: IN-PROGRESS`, `files_owned` declared honestly
- [ ] `INDEX.md` row added — a session file with no index row fails the state-tree guard
- [ ] Timestamp read from the clock, never composed from memory

**Why first.** Every later step writes a claim into the record. Registration is what makes
those claims *somebody's*; unregistered recon is unattributable by construction.

> **`files_owned` syntax:** comma-separated `fnmatch` globs. Shell brace expansion does NOT
> work — `scripts/{a,b}.py` splits on the comma into two literals that match nothing, so
> the claim silently covers zero files. Prefer a glob to an enumeration: a glob cannot go
> stale as files are added. Rule 0 in `state/REGISTRY.md`.

## STEP 2 — Git reconnaissance

```bash
git status
git branch -vva
git log --oneline -10
git stash list
git fetch --all
```

Confirm:

- [ ] Working tree is clean (if not, document why in your session file)
- [ ] You know which branch you are on
- [ ] No unresolved merge conflicts exist
- [ ] You have the latest from remote

> **A stale remote-tracking ref looks exactly like a lost merge.** Before concluding that a
> merged PR dropped commits, run `git fetch --all` — then verify by **tree**
> (`git rev-parse origin/main^{tree}` against the branch tip), never by "the PR is merged".
> A squash merge once silently dropped five commits here (#66 → recovered in #67).

## STEP 3 — Does `state/` exist?

- **No** → jump to the Bootstrap Protocol (`state/PROTOCOL.md` §7). You are the first agent.
- **Yes** → continue.

## STEP 4 — Read `state/DASHBOARD.md`

Gives you the picture in under a minute: current state, who is active, critical alerts,
what was recently completed.

Check the **Last Reconciled** stamp:

| Age | Action |
|---|---|
| < 24 h | Trust it, proceed |
| 24–48 h | Verify against `git log` before trusting |
| > 48 h | **STALE** — reconcile DASHBOARD.md before working |

**Never repeat a number from this file without opening its source.** The requirement and
`UNRES` counts are cross-checked by a guard; the evidence count is covered by **no
guard** — measure it from `spec/machine-readable/evidence.yaml`.

## STEP 5 — Read `state/REGISTRY.md`

Identify who else is active and what they claim. File-ownership rules:

- Another **ACTIVE** agent owns files you need → **STOP**. Coordinate (add a note to their
  session file), choose another approach, or wait.
- Owner **INACTIVE** (> 24 h) → you may claim ownership.
- Shared files (config, CI, `AGENTS.md`) require a `[COORDINATION]` note in both session files.

## STEP 6 — Check `state/BLOCKERS.md`

Confirm your task is not blocked upstream, and does not block someone else's work.

## STEP 7 — Targeted history via `state/INDEX.md`

Search INDEX.md by keyword or file path. Read **only the 2–3 most relevant** past sessions.
Reading every session file wastes your context window.

## STEP 8 — `ARCHITECTURE.md` and `DECISIONS.md`, conditionally

- Read `ARCHITECTURE.md` only if your task touches system structure.
- Read `DECISIONS.md` only if you are about to make a design choice — someone may have
  already decided it.

## STEP 9 — VERIFY STATE AGAINST REALITY (mandatory)

**State files are claims, not facts.** Run the five checks and record that you ran them:

```bash
python3 scripts/startup_receipt.py
```

That runs each check as its own subprocess and writes `state/verification.json` with every
check's name, command, exit code and timestamp. It is what STEP 8 compliance is measured
against — running the checks inside some other script does not produce a receipt.

The five checks:

- [ ] `gh pr list --state open` — does a PR already exist?
- [ ] `gh run list --branch main` — is CI green? (`gh pr checks` when a PR exists)
- [ ] `python3 scripts/verify_all.py` — does the chain pass?
- [ ] `pytest tests/ -q` — do the tests actually pass?
- [ ] `python3 tests/repo/test_state_tree.py` — do the state invariants hold?
- [ ] **Spot-check at least one claim from DASHBOARD.md against its source file.**

If any verification fails → **STOP**. Document the discrepancy in your session file, then
fix it or escalate. Do not proceed on stale state.

**Without a receipt, everything downstream refuses you:** `scripts/macp_log.py` will not
append an entry, `test_state_tree.py` fails on your session, `scripts/macp_sync_gate.py`
refuses the push, and CI refuses the merge. The receipt must be **newer than your
`Started` stamp** — one written before the session began does not describe the repository
you are working in.

> **Be honest about the limit:** no tool can force you to run a command. What this does is
> make an unverified, unregistered session **fail every gate**, rather than making it
> impossible to begin.
>
> **Environment-blocked is not red.** This sandbox enforces a per-turn delete budget and
> raises `SAFE_DELETE_BULK_CONFIRM_REQUIRED`; the full suite then fails in a turn that has
> already done other work and passes in a fresh one. That is recorded as
> `environment_blocked`, which gates treat as *not green* without calling the repo red.
> Re-run as the first command of a fresh turn, and re-run a red row before believing it.

> This step is the reason the amendment exists. STEMMA's own history has recorded instances
> of a *label* asserting a verification that never happened — `spec/CONFLICTS.md` claiming a
> docs sync, the DASHBOARD claiming its environment facts were "verified by inspection",
> BLK-004 calling correct historical provenance "stale", and a session reporting five STEP 8
> results from one wrapped command it had never inspected. In each case the label is why
> nobody looked.

## STEP 10 — Create a plan entry (multi-step work only)

`state/plans/agent-<ID>-<slug>.md` with: objective, scope (in/out), approach, risks and
mitigations, rollback, success criteria. Delete it when the plan completes.

---

**Only after all 10 steps may you begin actual work.**
