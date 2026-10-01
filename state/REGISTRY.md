# REGISTRY — Active Agents and File Ownership

> Per MACP Section 0. Register before working; release `files_owned` at session end.
> **A row here is a live claim.** When a session ends, set `status: ended` and clear
> `files_owned` — do not delete the row.

---

## Active Agents

| agent_id | session_id | started_at | task | files_owned | status |
|---|---|---|---|---|---|
| `A7F3` | `20261001-1123-A7F3-race-fix-bootstrap` | 2026-10-01T11:23Z | Fix the export read/write race; adopt MACP and bootstrap `state/` | — | **ended** |

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

## Stale-row policy

A row with `status: active` and no session activity for a long period is **stale, not
authoritative**. Before assuming an agent holds a file, check that its session file has
recent entries. If a row is stale, mark it `abandoned` and record the fact in `DEBT.md`
rather than silently deleting it — the row is part of the audit trail.
