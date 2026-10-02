# SESSION: 20261002-0130-A7F3-start-time-enforcement

**Agent:** `A7F3`
**Model:** WorkBuddy AI agent runtime (model identifier not exposed to the agent)
**Protocol:** `v1.2`
**Session ID:** `20261002-0130-A7F3-start-time-enforcement`
**Started:** 2026-10-02T01:30Z
**Status:** IN-PROGRESS
**Branch:** `feat/macp-start-time-enforcement`
**Base commit:** `e9c3e2d`
**Task:** P1 — move MACP enforcement from publish time to start time: a STEP 8 verification receipt that gates registration, gated `macp_log.py`, a receipt requirement in the sync gate, and REGISTRATION promoted to step 1 of `state/STARTUP.md`. P2 (G6, G8) if scope allows.
**Files owned:** `state/**`, `scripts/startup_receipt.py`, `scripts/macp_log.py`, `scripts/macp_sync_gate.py`, `tests/repo/test_state_tree.py`, `tests/repo/test_atomic_artifact_writes.py`

> Append-only. Do not edit earlier entries. Add new entries at the end.

---

## [START] — 2026-10-02T01:30Z

Owner instruction, verbatim: *"you didnot follow the protocal that mean the work done in
previsous session didnot work. time to make the protocal work"*, plus a scoped brief.

**The failure being fixed.** The MACP gates shipped in PR #83 are enforced at **publish**
time (pre-push hook + the `macp-gates` CI job). Nothing runs at **start** time. A session
skipped STEP 8, reported numbers it had not measured, and never registered — and **no gate
fired, because it never pushed.** The gates work; they are in the wrong place.

That previous session is this agent's, one message earlier in this conversation. Recorded
plainly: recon was done, but three of STEP 8's five checks were run *inside*
`gate_status.py --check` rather than by the agent, `gh pr checks` was substituted with
`gh run list`, the requirement/UNRES counts were repeated from `DASHBOARD.md` without
opening `verification.yaml`, and STEP 9 (registration) was judged not applicable because
the agent had decided a question was not a work unit. The escape hatch is the *gap between
starting and pushing*: an agent can read, claim, and report indefinitely without ever
touching an enforced surface.

**Owner scope, verbatim constraints:**
- P1 (required): start-time enforcement — verification receipt + gated registration.
- P2 (if scope allows): G6 and G8. DEC-010 deferred them pending "observed failures"; that
  condition is now met, so the deferral is lifted. **P1 first** — P2 would NOT have
  prevented the failure above.
- Do NOT touch BLK-005 or BLK-006 (owner decisions).
- Do NOT edit anything under `spec/`, `content/`, `connections/` or `sources/` — Tier 2.
- Ask before doing anything outside this scope.

**Ordering note.** The brief says read `state/STARTUP.md` and `state/DASHBOARD.md` before
anything else, and P1 item 4 moves REGISTRATION to step 1. So recon ran first (git status,
fetch, branch list, stash, log — all clean, `main` = `e9c3e2d`), then this registration,
then the rest of the sequence. Registering after recon but before any edit is the closest
honest reading of both instructions.

## [PROGRESS] — 2026-10-02T01:30Z

Registered. Session file created and REGISTRY row added with `Status: IN-PROGRESS` and a
real `files_owned` declaration (not a bare global, which G7 forbids). Branch
`feat/macp-start-time-enforcement` cut from `e9c3e2d`; `state` is a valid *commit* type but
not a valid *branch* prefix, so `feat/` is used.

## Receipt location — decision to be recorded

The receipt must be readable by three consumers: `macp_log.py` (local), the
`test_state_tree.py` guard (local + CI), and `macp_sync_gate.py` (pre-push). So it must be
**committed**, not gitignored.

## [PROGRESS] — 2026-10-02T01:42Z

P1 built. scripts/startup_receipt.py runs the five STEP 8 checks as separate subprocesses and writes state/verification.json (single file keyed by session id, so PROTOCOL section 2 is not amended). macp_log.py now refuses without a current receipt, test_state_tree.py gains test_every_live_session_has_a_current_step8_receipt (19 checks), macp_sync_gate.py gains check 7, and STARTUP.md moves REGISTRATION to step 1 with the rest renumbered. Negative controls run: no receipt, stale receipt and environment-blocked all refuse; genuine receipt passes. The ownership guard fired twice on under-declared files_owned, which is the guard doing its job.

**Files touched so far (auto-recorded from git):** `scripts/macp_log.py`, `scripts/macp_sync_gate.py`, `scripts/startup_receipt.py`, `state/ARCHITECTURE.md`, `state/INDEX.md`, `state/REGISTRY.md`, `state/STARTUP.md`, `state/sessions/20261002-0130-A7F3-start-time-enforcement.md`, `state/verification.json`, `tests/repo/test_atomic_artifact_writes.py`, `tests/repo/test_state_tree.py`


## [PROGRESS] — 2026-10-02T01:49Z

P2 done. G6 mechanises four rows of the real P4 ownership table in state/PROTOCOL.md as completeness rules (protocol/AGENTS.md to state/DECISIONS.md; docs/decisions to state/DECISIONS.md; .github/workflows to state/ARCHITECTURE.md; spec/ to state/BLOCKERS.md or state/DEBT.md — the Tier-2 boundary row, which was undetectable before). G8 adds a Protocol: header field validated against the version AGENTS.md declares; historical sessions are validated only if they declare one, because Rule 4 forbids editing them. Both ship with in-test negative controls. Recorded as DEC-011 and DEC-012 in state/DECISIONS.md. state/STARTUP.md, state/ARCHITECTURE.md and state/DASHBOARD.md updated; the documented state-tree count is now 21/21.

**Files touched so far (auto-recorded from git):** `scripts/macp_log.py`, `scripts/macp_sync_gate.py`, `scripts/startup_receipt.py`, `state/ARCHITECTURE.md`, `state/DASHBOARD.md`, `state/DECISIONS.md`, `state/INDEX.md`, `state/REGISTRY.md`, `state/STARTUP.md`, `state/sessions/20261002-0130-A7F3-start-time-enforcement.md`, `state/verification.json`, `tests/repo/test_atomic_artifact_writes.py`, `tests/repo/test_state_tree.py`

