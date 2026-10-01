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
| `20261001-1123-A7F3-race-fix-bootstrap` | `A7F3` | 2026-10-01 | Export read/write race fixed; MACP adopted and `state/` bootstrapped from a full repository audit | `scripts/atomic_write.py`, `scripts/{validate,export_jsonld,export_subsets,export_review_aware,graph_analysis,export_consumers,status_truth,docs}.py`, `tests/repo/test_atomic_artifact_writes.py`, `tests/repo/test_state_tree.py`, `AGENTS.md`, `docs/docs-contract.yaml`, `state/**` | ended | `docs/owner-rulings-unverified` |

**Bootstrap:** no prior sessions. This log was created on 2026-10-01 by `A7F3` as part of
the Section 7 bootstrap; the single row above is the first session recorded.

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
