# archive/

**Purpose (MACP §2):** old sessions, compressed by month. Also the destination for resolved
conflicts (§4 Phase D).

**Nothing here is current.** If you are reading a file in this directory to answer a question
about the present, you are reading the wrong file — start at
[`../DASHBOARD.md`](../DASHBOARD.md).

## What belongs here

| Kind | Moved here when |
|---|---|
| Sessions older than 30 days | The last active agent reconciles (§Shutdown step 7). Compress by month, e.g. `2026-10/`. |
| Spent conflicts | The disagreement is resolved and nothing needs to reference it (§4 Phase D). |
| Superseded plans | `Status: ABANDONED`. Completed plans are **deleted**, not archived (§5). |
| Old dashboards | A full rewrite, not an incremental update. Keep the previous version for history. |

## What does **not** belong here

- **Standing boundaries and invariants.** A resolved rule that is still in force stays live.
  See [`../conflicts/CONFLICT-001-state-tier2-boundary.md`](../conflicts/CONFLICT-001-state-tier2-boundary.md)
  for the worked example and the reasoning.
- **Append-only logs that are still recent.** `sessions/` is never archived by editing; a
  session log is permanent history, and archiving is a move, not a rewrite.
- **Anything referenced by a live file.** Check first — a broken link from `INDEX.md` or
  `PROTOCOL.md` is worse than a crowded directory.

## Currently empty

Created by the MACP bootstrap on 2026-10-01. Empty-but-present is intentional: `archive/` is
part of the §2 structure contract, and a missing directory invites an agent to invent a
different name for it.
