# DASHBOARD — STEMMA

> **Current state only.** What IS, not what happened. History lives in `sessions/`.

**Last Reconciled:** 2026-10-01T23:39Z
**Reconciled by:** `A7F3`
**Protocol:** MACP **v1.2** (`state/PROTOCOL.md`; startup sequence in `state/STARTUP.md`)

> **An agent is active** — `A7F3`, session `20261001-2339-A7F3-protocol-startup` (started
> 2026-10-01T23:39Z). It owns `state/**`, the MACP gate scripts, their tests, and `ci.yml`.
> It ran the startup sequence, then designed and implemented the MACP gate set
> (`DEC-010`) and the session↔state sync gate. The previous session
> (`20261001-1434-A7F3-shadow-tree`) is `COMPLETED` and its files are released.

> **Staleness policy (protocol §6 step 3):** `< 24 h` → trustworthy · `24–48 h` → verify key
> claims before relying on them · `> 48 h` → **STALE**, you must reconcile before working.

---

## Repository

| | |
|---|---|
| Repo | `STEMORG2026/STEMMA` (`Er-Sajan-PLG/STEMMA` is a pure redirect) |
| Branch | `main` (everything merged) |
| Version | `VERSION` = **3.0.0** · schema `1.3.0` · export `2.2.0` · relation registry `1.0.0` |
| Owner | Sajan (`human:curator.001`, `SOLE_OWNER`) |

> `HEAD` is deliberately **not** stated here. It lives in the generated Gate Status block below,
> read from `git rev-parse` at generation time. It used to be hand-written, and on 2026-10-01 it
> was found **11 commits stale** — nothing re-derived it, and no guard covered it.

## Gate Status — GENERATED

> **This block is generated, not written.** `python3 scripts/gate_status.py` runs the gates and
> rewrites it; CI fails if it is stale. Do not hand-edit the rows — they are overwritten.

<!-- BEGIN GENERATED: gate-status — do not edit by hand; regenerate with `python3 scripts/gate_status.py` -->
**Measured:** 2026-10-02T00:18Z · **HEAD:** `6244ba0`

| Gate | Result |
|---|---|
| `pytest tests/ -q` | **367 passed** |
| `scripts/verify_all.py` | **42 OK / 0 FAIL** (exit 0) |
| `scripts/docs.py check` | **PASS** |
| `spec/machine-readable/validate_recovery.py` | **PASS** — 9/9 checks |
| `scripts/verify_strong.py --quick` | exit 0 |
| `tests/repo/test_state_tree.py` | **PASS — 18/18** |
<!-- END GENERATED: gate-status -->



> Gate results are **measurements, not standing truths** — the stamp inside the block is when
> they were last run, and the test count changes with almost every commit. The
> `test_state_tree.py` guard cross-checks this file's *registry-derived* counts
> (requirements, `UNRES`) automatically; the pytest count has no derivable source, so it is
> stamped instead. Do not read a stale-looking count as drift without re-running.

> Running the suite leaves the working tree **clean** — `exports/` and `reports/` included.
> That is now guaranteed rather than incidental: `test_promotion_chain.py` mutates real
> canonical records, so it snapshots and restores the derived artifacts it causes to be
> regenerated (DEBT-005).

> Both `verify_all.py` and `pytest` are green under **both** `/usr/bin/python3` and
> `.venv/bin/python`. The chain routes its one pytest-dependent step to whichever
> interpreter owns pytest, and skips it with a visible line if none does.

## Verification State

| Metric | Value |
|---|---|
| Requirements | **24 VERIFIED · 0 FAILED · 1 UNVERIFIED** of 25 |
| Unverified | `REQ-STEMMA-OPS-002` — **parked to release time** by owner ruling |
| Evidence records | **88** |
| Interfaces | 2 · Decision records 1 · Conflicts 2 |
| `UNRES` records | **9 CLOSED · 1 DEFERRED · 1 OPEN** of 11 |
| — open | `UNRES-STEMMA-CORE-003` — **deliberately left OPEN** by owner directive |
| — deferred | `UNRES-STEMMA-SCH-001` (`revisit_trigger` recorded) |
| Corpus | **1 canonical** (`stemma:phys.metre`, human-written + human-reviewed) / **8 drafts** |

## Open Work

| Item | State |
|---|---|
| **PR #66** — *Execute owner rulings on the 7 open UNRES records + unstick the pre-push gate* | **MERGED** |
| **PR #67** — *Complete #66: the squash merge captured an earlier snapshot* | **MERGED** |
| Publication gate | **OPEN** — `docs/decisions/r6-identifier-base.md` = `stemma-urn-only`; w3id deferred, not rejected |

> **Handoff note.** `main` now carries everything — `state/`, the MACP section in `AGENTS.md`,
> the protocol (v1.1), the atomic-write helper, the gate repairs and the FAISS correction. A
> cold clone of `main` can continue from `state/` alone; the two setup steps are in
> `state/ARCHITECTURE.md` → "Cold start" (venv + `install_hooks.py`), and without them the gate
> silently skips and pushes are ungated.
>
> **What was nearly lost:** #66 was squash-merged and the squash captured an earlier snapshot
> than the branch tip — five commits, including the 78-place FAISS correction, never landed.
> Detected during shutdown by comparing `main`'s tree to the branch, recovered via #67. Nothing
> reported it: not CI, not the merge.

## Blocked — owner action

`BLOCKERS.md` holds **2 open** items, both requiring the owner. Neither is technical:

- **BLK-005** — `spec/CONFLICTS.md` claims a docs sync that had not happened (Tier 2).
- **BLK-006** — `tmp/fix-release-exports` proposes a **4.0.0** release while `main` is `3.0.0`.

## Next Actions

1. **Owner:** decide the Tier-2 record — BLK-005. (BLK-004 was cleared: its three `spec/` repo-name references are historical provenance tied to baseline commit `fb66dd9`, not stale values.)
2. **Owner:** decide `tmp/fix-release-exports` (BLK-006). It is the only unmerged branch; cutting
   a release is not cleanup, so it was left alone.
3. **Then:** `UNRES-STEMMA-CORE-003` and `REQ-STEMMA-OPS-002` both resolve at **release time**.
4. **Candidate work with no blocker:** `DEBT.md` holds **2 open** (003, 004) and **10 resolved**. DEBT-003 is an accepted residual (an ordering property; atomicity
   cannot fix it). DEBT-004 is **not a defect** — nothing in-repo reads the vector-store files.
5. **Queued, not orphaned:** `state/plans/agent-A7F3-gate-design.md` stays **ACTIVE**. It holds
   the gate design, of which G1–G5 and G7 are implemented (`DEC-010`); **G6** (P4's ownership
   table as a completeness check) and **G8** (protocol-version drift) are deferred to a future
   session. The plan is deliberately kept rather than deleted — `PROTOCOL.md` §5 says plans are
   deleted when *done*, and this one has live scope left.
6. **Known environment hazard:** the sandbox injects a `sitecustomize.py` shim enforcing a
   per-turn delete budget, which fails closed by raising `SystemExit(1)`. It makes the full
   pytest suite unreliable when a turn has already done other work (365/367 passed standalone;
   2–6 failures inside a longer turn). `gate_status.py` classifies this as
   **environment-blocked** rather than red. **CI has no such shim.** Re-run a red pytest row
   before believing it.

> **Corpus — checked 2026-10-01, so the next agent need not redo it.** Every entity under
> `content/` passes `schema/concept.schema.json` with **0 errors**. The non-canonical drafts are
> therefore **structurally ready**: nothing about their front matter blocks promotion. Their only
> blocker is **HITL review**, and that is not delegable — `scripts/review_entity.py` refuses any
> actor that is not an active `human:` in `schema/agent-registry.yaml`, and ADR-0057 requires
> consecutive promotion stages on separate days. `review_entity.py list` already emits exactly the
> fields a reviewer needs, so no extra report is warranted.
>
> Counts are deliberately not restated here — the generated README status block owns them
> (REQ-STEMMA-OPS-002).

## Environment Facts (re-verified by inspection 2026-10-01, not assumed)

| | |
|---|---|
| Filesystem | `/home/sajan/Projects` is a **persistent** ext4 volume on physical NVMe (not overlayfs, not a container) |
| Owner signing key | GPG `4705983D407DEB9C` (rsa4096, no expiry) in `~/.gnupg`, backed up in Bitwarden + `~/stemma-key-backup/` |
| Python | system `3.14.7`; `.venv` present and owns `pytest` |
| `numpy` | present in `/usr/bin/python3`, **absent** in `.venv` — relevant to the `embed.py` store-type path |
