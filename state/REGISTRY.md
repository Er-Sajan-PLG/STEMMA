# REGISTRY — Active Agents and File Ownership

> Per MACP Section 0. Register before working; release `files_owned` at session end.
> **A row here is a live claim.** When a session ends, set `status: COMPLETED` and clear
> `files_owned` — do not delete the row.

---

## Active Agents

| agent_id | session_id | started_at | task | files_owned | status |
|---|---|---|---|---|---|
| `A7F3` | `20261001-1123-A7F3-race-fix-bootstrap` | 2026-10-01T11:23Z | Fix the export read/write race; adopt MACP and bootstrap `state/` | — | **COMPLETED** |
| `A7F3` | `20261001-1153-A7F3-debt-cleanup` | 2026-10-01T11:53Z | Close the two unblocked documentation debt items (DEBT-001, DEBT-002) | — | **COMPLETED** |
| `A7F3` | `20261001-1434-A7F3-shadow-tree` | 2026-10-01T14:34Z | Shadow-tree fix (DEBT-007), six debt items, BLK-004 cleared, MACP v1.2 adopted | — | **COMPLETED** |
| `A7F3` | `20261001-1215-A7F3-cold-start-handoff` | 2026-10-01T12:15Z | Verify a cold clone can continue from `state/`, fix the cold-start gaps, sweep the chain for sibling silent-skip paths, incorporate MACP Amendment 1, and correct the FAISS mislabel | — | **COMPLETED** |
| `A7F3` | `20261001-2339-A7F3-protocol-startup` | 2026-10-01T23:39Z | Startup sequence (steps 1-10); then, on owner instruction, design and implement the MACP gate set and make session-state sync a blocking pre-push gate | — | **COMPLETED** |

No agent is currently active. `files_owned` is empty for every row, so any file is free to
claim.

> The session above is closed at the **owner's** instruction (DEC-007, N4). It is the most
> recent session, so `scripts/macp_sync_gate.py` still verifies its record against git —
> closing a session does not put it beyond the sync check.

---

## Agent ID Convention

MACP requires **4 alphanumeric characters**. Existing IDs:

| id | Notes |
|---|---|
| `A7F3` | This agent. Corresponds to **`llm:coding-agent.001`** in STEMMA canonical provenance (`content/**` frontmatter `provenance.writer` / `provenance.reviewer`). |

Keep the MACP id and the STEMMA provenance id aligned, so a `state/` session can be traced
to the canonical records it touched. When you register, add your own row here mapping your
4-character id to your provenance identity if you have one.

## Humans

| id | Meaning |
|---|---|
| `human:curator.001` | The owner (Sajan). The only Tier-2 authority — see `PROTOCOL.md`. SOLE_OWNER for every requirement (`spec/ROLES_AND_AUTHORITY.md`). |
| `human:<name>` | Any other registered human. Required for the `independent_validator` promotion stage. |

## Ownership Rules

0. **`files_owned` syntax: comma-separated `fnmatch` globs.** `state/**`,
   `scripts/macp_*.py`, `tests/repo/test_state_tree.py`. **Shell brace expansion is NOT
   supported** — `scripts/{a,b}.py` is split on the comma into the literals
   `scripts/{a` and `b}.py`, neither of which matches anything, so the claim silently
   covers nothing. Found by doing it: the ownership guard rejected it immediately, which
   is the guard working, but the failure reads as "under-declared" rather than "bad
   syntax". Prefer a real glob over an enumeration — a glob cannot go stale as files are
   added.
1. **One writer per file at a time.** If a file you need is owned by another active agent,
   raise a conflict rather than editing it (protocol §4).
2. **`state/` is Tier 1** — agents own it and may write it without human approval.
3. **Tier 2 is not yours.** `content/`, `connections/`, `sources/`, `spec/`, and any
   requirement status require the owner. See
   `conflicts/CONFLICT-001-state-tier2-boundary.md`.
4. **During work, write only to your own session file.** `DASHBOARD.md`, `REGISTRY.md`, and
   `INDEX.md` are updated at registration and at shutdown — not while working (protocol §2,
   "Write Isolation During Work").

## Session closure is an OWNER decision

**Do not mark a session `ended` on your own initiative.** The owner (`human:curator.001`)
declared this explicitly on 2026-10-01: *"the session is not completed until i say so."*

`A7F3` had been closing a session at the end of every work unit — running the §Shutdown
sequence, setting `status: COMPLETED`, clearing `files_owned`, and writing "session closed" into
the log. That is wrong here. A work unit finishing is **not** the same as the session ending.

Rules:

1. Finish a work unit by **logging it** and updating `DASHBOARD.md` — that part is always
   right.
2. **Leave `status: IN-PROGRESS` and `files_owned` populated** until the owner says the session is
   over.
3. Do **not** write `[END] — session closed` into the log. Use a neutral end-of-unit marker
   instead (e.g. `[PROGRESS] work unit complete`) and keep appending.
4. Only on the owner's word: run §Shutdown in full — set `status: COMPLETED`, clear
   `files_owned`, add the `INDEX.md` row if not already added, and mark the log closed.

Recorded as `DEC-007`. This is an owner override of MACP §Shutdown step 4, which the protocol
permits ("unless the user explicitly overrides it").

## Stale-row policy

A row with `status: IN-PROGRESS` and no session activity for a long period is **stale, not
authoritative**. Before assuming an agent holds a file, check that its session file has
recent entries. If a row is stale, mark it `abandoned` and record the fact in `DEBT.md`
rather than silently deleting it — the row is part of the audit trail.
