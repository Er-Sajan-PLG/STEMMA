# REGISTRY — Active Agents and File Ownership

> Per MACP Section 0. Register before working; release `files_owned` at session end.
> **A row here is a live claim.** When a session ends, set `status: ended` and clear
> `files_owned` — do not delete the row.

---

## Active Agents

| agent_id | session_id | started_at | task | files_owned | status |
|---|---|---|---|---|---|
| `A7F3` | `20261001-1123-A7F3-race-fix-bootstrap` | 2026-10-01T11:23Z | Fix the export read/write race; adopt MACP and bootstrap `state/` | — | **ended** |
| `A7F3` | `20261001-1153-A7F3-debt-cleanup` | 2026-10-01T11:53Z | Close the two unblocked documentation debt items (DEBT-001, DEBT-002) | — | **ended** |
| `A7F3` | `20261001-1215-A7F3-cold-start-handoff` | 2026-10-01T12:15Z | Verify a cold clone can continue from `state/`, fix the cold-start gaps, sweep the chain for sibling silent-skip paths, incorporate MACP Amendment 1, and correct the FAISS mislabel | `state/**`, `docs/**`, `AGENTS.md`, `webapp/**`, `examples/**`, `tests/repo/test_state_tree.py`, `tests/repo/test_promotion_chain.py`, `.github/workflows/ci.yml`, `.github/workflows/release.yml` | **active** |

No agent is currently active. `files_owned` is empty for every row, so any file is free to
claim.

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
sequence, setting `status: ended`, clearing `files_owned`, and writing "session closed" into
the log. That is wrong here. A work unit finishing is **not** the same as the session ending.

Rules:

1. Finish a work unit by **logging it** and updating `DASHBOARD.md` — that part is always
   right.
2. **Leave `status: active` and `files_owned` populated** until the owner says the session is
   over.
3. Do **not** write `[END] — session closed` into the log. Use a neutral end-of-unit marker
   instead (e.g. `[PROGRESS] work unit complete`) and keep appending.
4. Only on the owner's word: run §Shutdown in full — set `status: ended`, clear
   `files_owned`, add the `INDEX.md` row if not already added, and mark the log closed.

Recorded as `DEC-007`. This is an owner override of MACP §Shutdown step 4, which the protocol
permits ("unless the user explicitly overrides it").

## Stale-row policy

A row with `status: active` and no session activity for a long period is **stale, not
authoritative**. Before assuming an agent holds a file, check that its session file has
recent entries. If a row is stale, mark it `abandoned` and record the fact in `DEBT.md`
rather than silently deleting it — the row is part of the audit trail.
