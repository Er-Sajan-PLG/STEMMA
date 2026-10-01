# STARTUP — mandatory sequence (read before any work)

> The settled MACP revision (USA `AGENTS.md`, 2026-10-02) makes the startup sequence a
> **10-step** procedure and requires it to live in its own file. This is that file.
> `state/PROTOCOL.md` §6 and Amendment 2 both point here.

Run these in order. **Do not begin work until all 10 are complete.** You are stateless;
the repository is not.

---

## STEP 1 — Git reconnaissance

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

## STEP 2 — Does `state/` exist?

- **No** → jump to the Bootstrap Protocol (`state/PROTOCOL.md` §7). You are the first agent.
- **Yes** → continue.

## STEP 3 — Read `state/DASHBOARD.md`

Gives you the picture in under a minute: current state, who is active, critical alerts,
what was recently completed.

Check the **Last Reconciled** stamp:

| Age | Action |
|---|---|
| < 24 h | Trust it, proceed |
| 24–48 h | Verify against `git log` before trusting |
| > 48 h | **STALE** — reconcile DASHBOARD.md before working |

## STEP 4 — Read `state/REGISTRY.md`

Identify who else is active and what they claim. File-ownership rules:

- Another **ACTIVE** agent owns files you need → **STOP**. Coordinate (add a note to their
  session file), choose another approach, or wait.
- Owner **INACTIVE** (> 24 h) → you may claim ownership.
- Shared files (config, CI, `AGENTS.md`) require a `[COORDINATION]` note in both session files.

## STEP 5 — Check `state/BLOCKERS.md`

Confirm your task is not blocked upstream, and does not block someone else's work.

## STEP 6 — Targeted history via `state/INDEX.md`

Search INDEX.md by keyword or file path. Read **only the 2–3 most relevant** past sessions.
Reading every session file wastes your context window.

## STEP 7 — `ARCHITECTURE.md` and `DECISIONS.md`, conditionally

- Read `ARCHITECTURE.md` only if your task touches system structure.
- Read `DECISIONS.md` only if you are about to make a design choice — someone may have
  already decided it.

## STEP 8 — VERIFY STATE AGAINST REALITY (mandatory)

**State files are claims, not facts.** Before proceeding:

- [ ] `gh pr list --head <branch> --state open` — does a PR already exist?
- [ ] `gh pr checks <pr>` — is CI green?
- [ ] `python3 scripts/verify_all.py` — does the chain pass?
- [ ] `python3 -m pytest tests/ -q` — do the tests actually pass?
- [ ] `python3 tests/repo/test_state_tree.py` — do the state invariants hold?
- [ ] **Spot-check at least one claim from DASHBOARD.md against the code.**

If any verification fails → **STOP**. Document the discrepancy in your session file, then
fix it or escalate. Do not proceed on stale state.

> This step is the reason the amendment exists. STEMMA's own history has three recorded
> instances of a *label* asserting a verification that never happened — `spec/CONFLICTS.md`
> claiming a docs sync, the DASHBOARD claiming its environment facts were "verified by
> inspection", and BLK-004 calling correct historical provenance "stale". In each case the
> label is why nobody looked.

## STEP 9 — Register yourself

Create `state/sessions/YYYYMMDD-HHMM-<AGENT-ID>-<slug>.md`, beginning with the header
schema (see `state/PROTOCOL.md` Amendment 2 — `Agent`, `Model`, `Branch`, `Started`,
`Status: IN-PROGRESS`, `Base commit`, plus STEMMA's `Session ID`, `Task`, `Files owned`).

Add yourself to `state/REGISTRY.md`: agent ID (invent 4 alphanumeric characters), model,
branch, one-line task, current UTC timestamp, files claimed.

## STEP 10 — Create a plan entry (multi-step work only)

`state/plans/agent-<ID>-<slug>.md` with: objective, scope (in/out), approach, risks and
mitigations, rollback, success criteria. Delete it when the plan completes.

---

**Only after all 10 steps may you begin actual work.**
