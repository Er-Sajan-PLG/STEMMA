# INDEX — Searchable Log of All Past Sessions

> **Purpose (MACP §2):** a searchable log of past sessions. Use it for **targeted history**
> — find the 2–3 sessions relevant to your task and read only those. Do **not** read every
> session file (§6 step 6).
>
> Add a row here at shutdown (§Shutdown step 3). Rows are append-only.

---

## Session log

| Session ID | Agent | Date | Title | Files touched | Status | Branch |
|---|---|---|---|---|---|---|
| `20261001-1123-A7F3-race-fix-bootstrap` | `A7F3` | 2026-10-01 | Export read/write race fixed; MACP adopted and `state/` bootstrapped from a full repository audit | `scripts/atomic_write.py`, `scripts/{validate,export_jsonld,export_subsets,export_review_aware,graph_analysis,export_consumers,status_truth,docs}.py`, `tests/repo/test_atomic_artifact_writes.py`, `tests/repo/test_state_tree.py`, `AGENTS.md`, `docs/docs-contract.yaml`, `state/**` | COMPLETED | `docs/owner-rulings-unverified` |
| `20261001-1153-A7F3-debt-cleanup` | `A7F3` | 2026-10-01 | Closed DEBT-001 (stale `PROGRESS.md` block, fixed structurally) and DEBT-002 (retired repo name broke `gh attestation verify` — severity corrected upward); raised BLK-004 | `PROGRESS.md`, `docs/API.md`, `adapters/python/README.md`, `schema/api.yaml`, `README.md`, `explorer/src/services/feedback.ts`, `state/{DEBT,BLOCKERS,DASHBOARD,INDEX,REGISTRY}.md` | COMPLETED | `docs/owner-rulings-unverified` |
| `20261001-1434-A7F3-shadow-tree` | `A7F3` | 2026-10-01 | Eliminate real-tree mutation from `test_promotion_chain.py` via a shadow tree (DEBT-007 residual) | `tests/repo/test_promotion_chain.py`, `state/**` | COMPLETED | `main` |
| `20261001-1215-A7F3-cold-start-handoff` | `A7F3` | 2026-10-01 | Verified a cold clone can continue from `state/`; documented the cold-start setup; swept the chain for sibling silent-skip paths and fixed a CI freshness blind spot (DEBT-006) | `state/ARCHITECTURE.md`, `state/{DASHBOARD,INDEX,REGISTRY,DEBT,DECISIONS}.md`, `state/sessions/**`, `AGENTS.md`, `.github/workflows/{ci,release}.yml` | COMPLETED | `main` (merged as #66 + #67) |
| `20261001-2339-A7F3-protocol-startup` | `A7F3` | 2026-10-01 | Ran the MACP v1.2 startup sequence end to end (steps 1–10) and stopped before project work; step 8 verification found two stale DASHBOARD claims and a silently vacuous ownership guard | `state/sessions/20261001-2339-A7F3-protocol-startup.md`, `state/plans/agent-A7F3-gate-design.md`, `state/{REGISTRY,INDEX,DASHBOARD,BLOCKERS,ARCHITECTURE,DECISIONS}.md`, `tests/repo/{test_state_tree,test_atomic_artifact_writes}.py`, `scripts/{gate_status,macp_startup_gate}.py`, `.github/workflows/ci.yml` | IN-PROGRESS | `main` |

> **The row above was `IN-PROGRESS` for most of the session.** Per `DEC-007` a session stays open until the
> owner says otherwise, so this row is a *live* entry: its status and file list are updated as
> work continues and finalised only at owner-declared shutdown. An earlier revision of this
> row said `ended`, which contradicted `REGISTRY.md` and DEC-007 — a state file disagreeing
> with another state file is exactly the drift the DASHBOARD/registry guard exists to prevent,
> and the INDEX row was outside that guard's reach.

**Bootstrap:** the log was created on 2026-10-01 by `A7F3` as part of the Section 7 bootstrap.
Five sessions are recorded so far.

---

## How to search

| Looking for | Do this |
|---|---|
| Work on a specific file | `grep -rl "<path>" state/sessions/` |
| A decision's context | `grep -rn "\[DECISION\]" state/sessions/`, then read `DECISIONS.md` |
| A defect's origin | `grep -rn "\[BUG FOUND\]" state/sessions/` |
| Why a direction changed | `grep -rn "\[PIVOT\]" state/sessions/` |
| Anything that blocked someone | `grep -rn "\[BLOCKER\]" state/sessions/` |
| Debt as it was noticed | `grep -rn "\[DEBT\]" state/sessions/` |

Event tags are defined in `PROTOCOL.md` §2 ("Write Isolation During Work") and are the
reason sessions are greppable at all.

---

## Related state outside `state/`

`state/` is the *coordination* layer. Authoritative project state lives elsewhere and is
**not** duplicated here:

| Question | Authoritative location |
|---|---|
| What does a requirement's verification state say? | `spec/machine-readable/verification.yaml` |
| Which open questions exist? | `spec/machine-readable/open_questions.yaml` |
| Which conflicts between sources exist? | `spec/CONFLICTS.md` |
| What evidence supports a claim? | `spec/machine-readable/evidence.yaml` + `spec/EVIDENCE_REGISTER.md` |
| Who may approve what? | `spec/ROLES_AND_AUTHORITY.md` |
| What are the live enforcement rules? | `spec/machine-readable/enforcement_rules.yaml` |
| How does the repository itself work? | `state/ARCHITECTURE.md` |
