# DASHBOARD — STEMMA

> **Current state only.** What IS, not what happened. History lives in `sessions/`.

**Last Reconciled:** 2026-10-01T13:56Z
**Reconciled by:** `A7F3`
**Protocol:** MACP v1.0 (`state/PROTOCOL.md`)

> **An agent is currently active** — `A7F3`, session `20261001-1215-A7F3-cold-start-handoff`.
> Per DEC-007 the session stays open until the owner says otherwise, so `files_owned` may be
> populated in `REGISTRY.md` even though the last work unit finished.

> **Staleness policy (protocol §6 step 3):** `< 24 h` → trustworthy · `24–48 h` → verify key
> claims before relying on them · `> 48 h` → **STALE**, you must reconcile before working.

---

## Repository

| | |
|---|---|
| Repo | `STEMORG2026/STEMMA` (`Er-Sajan-PLG/STEMMA` is a pure redirect) |
| Branch | `docs/owner-rulings-unverified` |
| HEAD | `08cecb3` — `fix(exports): write gate-compared artifacts atomically` |
| Version | `VERSION` = **3.0.0** · schema `1.3.0` · export `2.2.0` · relation registry `1.0.0` |
| Owner | Sajan (`human:curator.001`, `SOLE_OWNER`) |

## Gate Status — ALL GREEN

| Gate | Result (measured 2026-10-01T13:44Z) |
|---|---|
| `pytest tests/ -q` | **365 passed** |
| `scripts/verify_all.py` | **42 OK / 0 FAIL** (exit 0) |
| `scripts/docs.py check` | **PASS** |
| `spec/machine-readable/validate_recovery.py` | **PASS** — 9/9 checks |
| `scripts/verify_strong.py --quick` | exit 0 |
| `tests/repo/test_state_tree.py` | **PASS — 16/16** (structure, naming, reconciliation stamp, INDEX coverage, dashboard↔registry drift, INDEX↔registry session status, session-header schema, protocol commit type, duplicate record ids, ownership coverage) |

> Gate results are **measurements, not standing truths** — the timestamp above is when they
> were last run, and the test count changes with almost every commit. The
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
| **PR #66** — *Execute owner rulings on the 7 open UNRES records + unstick the pre-push gate* | **OPEN · MERGEABLE · CLEAN · 30 checks pass · 0 fail** — awaiting owner merge (BLK-001) |
| Publication gate | **OPEN** — `docs/decisions/r6-identifier-base.md` = `stemma-urn-only`; w3id deferred, not rejected |

> **Handoff note.** A cold clone of this branch can continue from `state/` alone — verified by
> cloning it fresh and following the startup sequence. Two setup steps are needed and are
> documented in `state/ARCHITECTURE.md` → "Cold start" (venv + `install_hooks.py`); without
> them the gate is skipped and pushes are ungated, and neither failure is loud.
>
> **The one thing that blocks a *cold* start: `main` has no `state/` at all.** Everything here
> is on `docs/owner-rulings-unverified`; until BLK-001 is merged, an agent starting from `main`
> would not find the protocol, `DASHBOARD.md`, or this note.

## Nothing Is Blocked

`BLOCKERS.md` has no items requiring human action beyond the PR #66 merge. See
`BLOCKERS.md` for the one owner-action item.

## Next Actions

1. **Owner:** merge PR #66 (all checks green, no conflicts) — BLK-001.
2. **Owner:** decide the three stale repo-name references under `spec/` — BLK-004. One of
   them (`spec/ROLES_AND_AUTHORITY.md:4`) cites a commit and may be a historical record that
   is correct as written; that judgement is Tier 2.
3. **Then:** the open `UNRES-STEMMA-CORE-003` and `REQ-STEMMA-OPS-002` both resolve at
   **release time** — neither can progress before a release lands. Do not start them.
4. **Candidate work with no blocker:** `DEBT.md` now holds **2 open** (003, 004), **1 mitigated** (007) and **5 resolved** (001, 002, 005, 006, 008). DEBT-003 is a documented, accepted residual (an ordering property, not fixable by atomicity). DEBT-004 turned out **not to be a defect**: nothing in-repo reads `vectors.npy` / `vectors.json`, so the store form varying by interpreter is harmless, and the docs already describe the type as honest either way. What it did surface was DEBT-008.

## Environment Facts (verified by inspection, not assumed)

| | |
|---|---|
| Filesystem | `/home/sajan/Projects` is a **persistent** ext4 volume on physical NVMe (not overlayfs, not a container) |
| Owner signing key | GPG `4705983D407DEB9C` (rsa4096, no expiry) in `~/.gnupg`, backed up in Bitwarden + `~/stemma-key-backup/` |
| Python | system `3.14.7`; `.venv` present and owns `pytest` |
| `numpy` | present in `/usr/bin/python3`, **absent** in `.venv` — relevant to the `embed.py` store-type path |
