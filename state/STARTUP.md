# STARTUP — mandatory sequence (read before any work)

> The settled MACP revision (USA `AGENTS.md`, 2026-10-02) makes the startup sequence a
> **10-step** procedure and requires it to live in its own file. This is that file.
> `state/PROTOCOL.md` §6 and Amendment 2 both point here.
>
> **Registration is two-phase.** STEP 1 writes *identity only* (session file, `REGISTRY.md`
> row, `INDEX.md` row) — no repository facts are known yet, so none are written. STEP 2 runs
> git recon, then fills `Branch`, `Base commit`, and `files_owned` from what recon actually
> found. Verification (STEP 9) is **gated on phase B**: `scripts/startup_receipt.py` refuses
> to run while phase B is incomplete or does not match git.
>
> **Why split it.** Phase A needs no information, so it can go first and guarantee every
> later claim has an owner — which is why registration moved off step 9: a session that never
> registered left its work unattributable. Phase B needs reconnaissance. `Branch` and
> `Base commit` are facts about the repository that cannot be known before looking at it, and
> the sync gate derives both the changed-file set and the commit list from `Base commit`, so a
> guessed value makes guards measure the wrong repository. Measured: a session that captured
> `Base commit` before recon had to correct it after the base moved.
>
> `state/PROTOCOL.md` §3 carries the same ordering in compact form; the two files agree. This
> file is authoritative for detail.

Run these in order. **Do not begin work until all 10 are complete.** You are stateless;
the repository is not.

---

## STEP 1 — REGISTER YOURSELF (phase A: identity)

Create `state/sessions/YYYYMMDD-HHMM-<AGENT-ID>-<slug>.md`, beginning with the
**identity** header (Amendment 2 — `Agent`, `Model`, `Session ID`, `Started`,
`Status: IN-PROGRESS`). Do **not** write `Branch`, `Base commit`, or `files_owned` yet;
those come from recon in STEP 2.

Add yourself to `state/REGISTRY.md` (agent id, model, session id, started_at, task,
`Status: IN-PROGRESS`) with `files_owned` left as `—` for now. Add the `state/INDEX.md`
row.

- [ ] Session file created with the identity header (Agent, Model, Session ID, Started, Status)
- [ ] REGISTRY row added, `Status: IN-PROGRESS`, `files_owned` = `—`
- [ ] INDEX.md row added — a session file with no index row fails the state-tree guard
- [ ] Timestamp read from the clock, never composed from memory

**Why first.** Every later step writes a claim into the record. Registration is what makes
those claims *somebody's*; unregistered recon is unattributable by construction.

> **`files_owned` syntax:** comma-separated `fnmatch` globs. Shell brace expansion does NOT
> work — `scripts/{a,b}.py` splits on the comma into two literals that match nothing, so
> the claim silently covers zero files. Prefer a glob to an enumeration: a glob cannot go
> stale as files are added. Rule 0 in `state/REGISTRY.md`.

## STEP 2 — Git reconnaissance, then register context (phase B)

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

Then **complete phase B**: fill `Branch`, `Base commit`, and `files_owned` from what recon
found — in the session header *and* the `REGISTRY.md` row (the ownership guard reads
`files_owned` from there).

- [ ] Header now carries `Branch` and `Base commit`
- [ ] `REGISTRY.md` `files_owned` declares honestly what this session will touch
- [ ] The two `Branch`/`Base commit` values resolve in git (`git rev-parse <value>`)

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

## STEP 9 — VERIFY STATE AGAINST REALITY (mandatory, gated on phase B)

**State files are claims, not facts.** Run the five checks and record that you ran them:

```bash
python3 scripts/startup_receipt.py
```

The script **refuses to run until phase B is complete** — `Branch` and `Base commit` must be
present and resolve in git (filled at STEP 2 from recon). A session that skipped recon cannot
obtain a receipt; without one, nothing downstream accepts its work. Once it runs, it executes
each check as its own subprocess and writes `state/verification.json` with every check's name,
command, exit code and timestamp. That file is what STEP 8 compliance is measured against —
running the checks inside some other script does not produce a receipt.

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
