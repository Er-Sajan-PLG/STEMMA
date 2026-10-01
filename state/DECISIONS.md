# DECISIONS — Immutable Log

> **Append-only. Never edit an existing decision.** To change one, add a NEW decision
> that `Supersedes:` the old id. Newest at the bottom.
>
> **Scope (important):** this file records **coordination decisions** — how agents
> work together. It does **not** record specification rulings. A requirement status,
> a closed `UNRES-` record, or an `INFERENCE → FACT` promotion is an **owner** act and
> lives in `spec/` (`spec/ROLES_AND_AUTHORITY.md` Constraint D). Where a spec ruling
> motivated a coordination decision, the decision links to it rather than restating it.

---

## DEC-001 — Adopt MACP v1.0 as the coordination layer

**Date:** 2026-10-01
**Decided by:** `coding-agent.001`, on owner instruction ("I want you to write this in
agent and act accordingly")
**Supersedes:** —

**Decision.** This repository adopts the Multi-Agent Coordination Protocol v1.0. The
canonical protocol text is `state/PROTOCOL.md`; the coordination state lives in
`state/`.

**Context.** Supplied by the owner as a single message. That message was **truncated
mid-Section 6** and **Section 7 (Bootstrap Protocol) was referenced but absent**. The
tail of Section 6 and all of Section 7 were reconstructed by the agent and are marked
`[RECONSTRUCTED]` in `PROTOCOL.md`. They are proposals awaiting owner review, not
owner-authored protocol.

**Consequences.**
- `state/` becomes a **Tier 1** (agent-sovereign) directory.
- Tier 2 is unchanged: `content/`, `connections/`, `sources/`, `spec/`, and all
  requirement statuses remain owner-only. Recorded in
  `conflicts/CONFLICT-001-state-tier2-boundary.md`.
- `state/PROTOCOL.md` is classified in `docs/docs-contract.yaml` so the repository's
  own documentation contract covers it.

---

## DEC-002 — Gate-compared artifacts are written atomically

**Date:** 2026-10-01
**Decided by:** `coding-agent.001`
**Supersedes:** —

**Decision.** Every writer whose output a gate byte-compares must stage its content in
a dot-prefixed sibling temp file and `os.replace` it over the destination
(`scripts/atomic_write.py`). Bare `Path.write_text` is not permitted in those files.

**Context.** `Path.write_text` opens the destination with mode `"w"` — truncating it —
and only then writes. A reader running concurrently observes a partial file. This
produced a real spurious failure: `export_consumers.py --all --check`, run while
`verify_all.py` regenerated exports, read a half-written bundle and reported it stale.
Measured: 786/852 (92%) of concurrent `--check` runs saw a torn bundle before the fix,
0/75 after.

**Consequences.**
- `tests/repo/test_atomic_artifact_writes.py` pins the list of affected writers so a
  new gate-compared writer cannot be added non-atomically by accident.
- Output stays byte-identical, so export determinism and the CI freshness diff are
  unaffected.
- Writers whose output **no gate compares** are deliberately excluded (campaign/triage
  reports, ingestion staging, canonical `content/`/`connections/`/`sources/` edits).
  Converting them would widen the change without closing a real window.

---

## DEC-003 — `state/` is coordination metadata, not project documentation

**Date:** 2026-10-01
**Decided by:** `coding-agent.001`
**Supersedes:** —

**Decision.** Only `state/PROTOCOL.md` is classified in `docs/docs-contract.yaml`. The
volatile state files (`DASHBOARD.md`, `REGISTRY.md`, `INDEX.md`, `ARCHITECTURE.md`,
`DECISIONS.md`, `DEBT.md`, `BLOCKERS.md`, and everything under `sessions/`, `plans/`,
`conflicts/`, `archive/`) are deliberately left unclassified.

**Context.** The repository's contract requires new docs to be classified
(`docs/DOCUMENTATION-SYSTEM.md` "Adding a new obligation"). But the contract's
`docs-consistency` checks assume a document changes when its subject changes, whereas
`DASHBOARD.md` and `sessions/*` change **every session** by design. Classifying them
would either create permanent drift or force meaningless churn.

**Consequences.** The volatile files appear as *unmapped* in `docs.py impact`, which is
tolerated (the tool reports them conservatively). This decision is the explicit record
that the omission is intentional — per the contract's own rule that an exception must
be recorded rather than taken silently.

---

## DEC-004 — The chain must be runnable under a pytest-less interpreter

**Date:** 2026-10-01
**Decided by:** `coding-agent.001`
**Supersedes:** —

**Decision.** `scripts/verify_all.py` probes `sys.executable` then `.venv/bin/python`
for an interpreter that owns `pytest`, and runs its one pytest-dependent step under
whichever qualifies. If none qualifies, the step is **skipped with a visible `SKIP:`
line** and the chain continues — it does not fail.

**Context.** The pre-push hook invokes the chain under whatever `python3` is ambient.
With no venv active that is `/usr/bin/python3`, which has `requirements.txt` but not
`pytest`, so the promotion-chain step died and blocked every push for an environmental
reason. CI was unaffected because it activates a venv.

**Consequences.** Failing instead of skipping would have broken
`tests/repo/test_gate_fail_closed.py`, whose whole point is that the chain terminates
on *its own* forced step. Skipping is recorded visibly so the omission is never silent.

---

## DEC-005 — The reconstructed protocol is superseded by the authoritative text

**Date:** 2026-10-01
**Decided by:** `A7F3`
**Supersedes:** the reconstruction clause of **DEC-001**

**Decision.** `state/PROTOCOL.md` now holds the **complete** protocol text supplied by the
owner. Every `[RECONSTRUCTED]` marker is removed, and the `state/` tree is restructured to
match it.

**Context.** The first copy of the protocol supplied to this repository was **truncated
mid-Section 6**, with Section 7 referenced but absent. The agent completed both from
inference and marked the additions `[RECONSTRUCTED]`. The owner then supplied the full text,
which showed the reconstruction was wrong in four material ways:

| Reconstructed (wrong) | Authoritative |
|---|---|
| `agent_id` like `coding-agent.001` | **4 alphanumeric characters**, e.g. `C7A2` |
| session file `2026-10-01-atomic-writes.md` | `YYYYMMDD-HHMM-<AGENT-ID>-<slug>.md` |
| `INDEX.md` = navigation to state files | **searchable log of all past sessions** |
| plans retained after completion | plans **deleted** when done (§5) |

The reconstruction also omitted the **Last Reconciled** staleness policy (§6 step 3), the
**write-isolation** rule (§2: during work, write only to your own session file), the event
tag vocabulary, and the reconciliation duty for the last active agent.

**Consequences.**
- The session file was renamed to the protocol convention; `INDEX.md` was rewritten as a
  session log; `DASHBOARD.md` gained a **Last Reconciled** timestamp; the completed plan was
  deleted per §5.
- The agent ID `A7F3` replaces the earlier `coding-agent.001` in `state/`; the mapping to
  STEMMA provenance (`llm:coding-agent.001`) is recorded in `REGISTRY.md`.
- **Why this mattered enough to rework:** a plausible-but-wrong protocol file is precisely
  the failure this protocol exists to prevent. A future agent would have followed the
  reconstructed rules — inventing non-conformant session names and never reconciling a
  stale dashboard — and the error would have propagated silently, because nothing else in
  the repository checks `state/`.
- DEC-001 is **not** edited, per Rule 4. Its reconstruction clause is superseded by this
  decision; the rest of DEC-001 (adopting MACP, and the Tier boundary) stands.
