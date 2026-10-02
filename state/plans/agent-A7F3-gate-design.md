# PLAN: MACP gate design — where the protocol needs a gate

**Owner:** `A7F3`
**Status:** ACTIVE — **first slice (G1, G2, G3, G4+G5, G7) implemented 2026-10-02**; G6 and G8 deferred
**Created:** 2026-10-01T23:53Z
**Session:** `20261001-2339-A7F3-protocol-startup`

## Implementation status

| | Gate | State |
|---|---|---|
| **G1** | Repair the dead ownership guard | **DONE** — fired twice unprompted, catching real under-declarations |
| **G2** | Generate the DASHBOARD Gate Status table | **DONE** — `scripts/gate_status.py`, `--check` in CI |
| **G3** | Derive the DASHBOARD `HEAD` line | **DONE** — in the same generated block |
| **G4** | Verification artifact required for registration | **DONE, re-designed** — see below |
| **G5** | CI re-runs and compares | **DONE** — `gate_status.py --check` in the new `macp-gates` job |
| **G7** | Forbid the trivial `files_owned` | **DONE** |
| **G6** | P4's ownership table as a completeness check | **DEFERRED** (P7 sequencing) |
| **G8** | Protocol-version drift | **DEFERRED** (P7 sequencing) |

**G4 was re-designed during implementation, and the change is an improvement.** The plan
proposed a new `state/verification/<session-id>.json`. That would have added a directory to
`PROTOCOL.md` §2's structure — a protocol amendment for no benefit. It also would have
violated the plan's own rule 3: a JSON file is still a claim the agent can hand-write.

Instead, `scripts/gate_status.py` writes its block **only when every gate is green**, so a
fresh stamp is a by-product of having run the gates and passed. The startup gate then checks
the cheap decisive property: every live session must have started at or before that stamp.
No new artifact, no §2 change, and the agent cannot assert the evidence — only produce it.

The binding was also changed from *stamp ≥ session `Base commit`* to *stamp ≥ session
`Started`*: `Base commit` is fixed at session start, so once the session commits, `HEAD` no
longer equals it and the check would fail spuriously for a session doing the right thing.

One thing that did **not** survive contact: the startup check could not live in
`test_state_tree.py` or in `gate_status.py`'s own gate list. Both deadlock — the artifact it
checks is produced by the run that would have to pass first. It lives in its own script.

## Goal

Make it impossible for an agent to *silently* skip the parts of the protocol that are currently
enforced by discipline alone. The owner's ask: a gate that forces the protocol to be followed
completely at startup, plus gates on the important steps — verification above all.

This plan is a **design**, not an implementation. Nothing here is built yet.

## Scope

**In:** state-layer gates — startup completeness, verification evidence, state-file accuracy,
P4's ownership table, protocol-version drift.

**Out (deliberately):** anything requiring correctness judgement; anything that needs new prose
in a session file; blocking pre-commit hooks; the canonical/specification layer (Tier 2).

## The four rules a gate here must satisfy

Derived from the protocol's own text, not invented. They are the design constraints; violating
any one produces the failure the protocol already predicts.

1. **Gate completeness, never correctness.** P7: correctness is not mechanically decidable.
   Ask "did you do X", never "was X right".
2. **Warn locally, block in CI.** P7: a blocking pre-commit hook trains agents to `--no-verify`
   reflexively, or to write minimal records that satisfy the hook — *"both worse than no hook."*
3. **Never gate on a sentence the agent must write.** This is the corollary that matters most.
   Any gate of the form "the session file must say you verified" is satisfiable by typing the
   sentence. A gate must be satisfied by **an artifact that already exists, or that the gate
   itself generates** — never by new prose.
4. **Prefer generating a value to asserting it.** Where a value is machine-derivable, generate
   it. A generated value cannot be forgotten and cannot be stale. The repository already works
   this way: `scripts/status_truth.py` owns the README counts, `scripts/review_manifest.py` owns
   the review manifest.

Corollary: **fail closed on a missing artifact, not on a wrong claim.** Missing is a reliable
signal; wrong is not detectable.

---

## Proposed gates, ranked by value per unit of effort

### Tier 1 — repairs and generated artifacts (safe now; add no new discipline)

**G1 — Repair the dead ownership guard.** *(highest value in this list)*
`tests/repo/test_state_tree.py:401` selects rows with `status.lower() == "active"`, but `DEC-009`
migrated the vocabulary to `IN-PROGRESS`. The guard is unreachable — proven both ways this
session. One-token fix. Then add a **non-vacuity assertion** so it cannot silently die again:
assert the vocabulary the guard matches is the vocabulary `REGISTRY.md` actually uses.
*Home:* `test_state_tree.py`. *Effort:* minutes. *Replaces a broken gate rather than adding one.*

**G2 — Generate the DASHBOARD Gate Status table.**
Add `scripts/gate_status.py` that runs the table's commands and writes the block, in the
`status_truth.py` style, plus a CI freshness diff. The table then *cannot* be stale or false —
the failure class disappears instead of being policed. Today it is the most-read unverified
artifact in the repository: six command results that nothing re-runs.
*Home:* `scripts/gate_status.py` + `test_state_tree.py` freshness check.

**G3 — Derive the DASHBOARD `HEAD` line** from `git rev-parse` inside the same generated block.
Kills the stale-`HEAD` class, which was found live this session (11 commits stale).

### Tier 2 — the startup gate

**G4 — A verification artifact required for registration.**
`scripts/startup_check.py` runs the STEP 8 commands and writes
`state/verification/<session-id>.json` = `{base_commit, ran_at, {command: exit_code, digest}}`.
New check: **every `IN-PROGRESS` session must have a matching artifact whose `base_commit`
equals the header's `Base commit` and whose `ran_at` is at or after `Started`.** A missing
artifact means step 8 was skipped → fail.

This is the startup gate the owner asked for, and it satisfies rule 3: the artifact is produced
by *running* the commands, not by asserting that they were run.

**G5 — CI re-runs the cheap gates and byte-compares** against the recorded artifact. This is what
makes G4 un-fakeable: hand-writing the JSON is caught, because CI's real output will not match.
Use only the fast gates (`verify_all.py`, `docs.py check`, `validate_recovery.py`,
`verify_strong.py --quick`); the pytest job stays separate and unchanged.

### Tier 3 — mechanise P4's ownership table

Every row of the settled ownership table is checkable as a *completeness* condition — "file X
changed ⇒ file Y also changed in the same session". The table is currently pure prose that
nothing reads.

**G6 — Implement P4 as a completeness check.** The highest-value rows:

| Trigger (changed) | Must also have changed |
|---|---|
| `state/PROTOCOL.md` or `AGENTS.md` | a new `DEC-` in `state/DECISIONS.md` |
| a new `docs/decisions/*.md` | a row in `state/DECISIONS.md` |
| **any `spec/` file** | a `BLK-` or `DEBT-` entry |

The third row is the sharpest: `spec/` is Tier 2, owner-only under Constraint D. An agent editing
`spec/` without raising a blocker is a **boundary breach**, and the diff makes it mechanically
detectable today.

**G7 — Forbid the trivial `files_owned`.** The repaired G1 guard is satisfiable by declaring
`files_owned: **`. Require either a non-global pattern or an explicit justification. Otherwise
the ownership guard can always be passed by widening the claim until it is meaningless.

**G8 — Protocol-version drift.** Add `Protocol: v1.2` to the session header schema; CI asserts it
equals the version declared in `PROTOCOL.md`. This closes a gap the protocol itself lists as
unaddressed ("protocol version drift — no rule covers that").

### Deliberately NOT gated

- **Scope discipline (N3).** "Did you fix an unrelated bug" is not decidable from a diff.
- Whether a `[BUG FOUND]` entry was *worth* writing — not decidable, and a gate would reward noise.
- Anything requiring new prose in a session file (rule 3).
- **Local push-blocking.** Warn only; block in CI (rule 2).
- Tier 2 content: `spec/`, `content/`, `connections/`, `sources/`.

---

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| **Compliant-looking rot** — gates satisfied by minimal records | Rules 3–4: gate on generated artifacts, never on prose. G7 removes the trivial escape. |
| **False confidence** — passing gates read as "the work is correct" | State plainly in each gate's docstring that it checks completeness, not correctness (repo style). |
| **`--no-verify` reflex** | Local hooks warn only; blocking lives in required CI checks. |
| **Sequencing** — P7 defers machine-checked drift until **20+ sessions**; this repository has **5** | Tier 1 is *repair plus generation*, not new discipline, so it does not need the 20-session evidence base. Tiers 2–3 are new gates and are the owner's call; the protocol explicitly permits an owner override. |
| **CI cost** | G5 re-runs only the fast gates; the suite stays in its own job. |
| **Gate fatigue** — too many gates, agents route around them | Eight proposed, five recommended now (G1–G4, G7). G5–G6, G8 can follow once these are proven. |

## Rollback

Every gate is independent and revertible in isolation. G1 is a one-token revert. G2–G3 revert by
deleting the generated block and its freshness check. G4–G5 revert by deleting
`scripts/startup_check.py`, `state/verification/` and the corresponding check. No gate mutates
canonical data, so rollback never touches Tier 2.

## Success criteria

1. No gate is satisfiable by writing prose.
2. A session that skips STEP 8 **fails** instead of passing silently.
3. `DASHBOARD.md` cannot contain a stale gate result or a stale `HEAD`.
4. The ownership guard fires — verified by sabotage, both directions.
5. An agent editing `spec/` without a blocker record is caught mechanically.
6. Each gate ships with a demonstrated failing case, in the style of
   `tests/repo/test_gate_fail_closed.py`.

## Recommended first slice

**G1 + G2 + G3 + G4 + G7** — the four repairs/generators plus the startup gate. They close every
failure actually observed on 2026-10-01, add no new discipline, and are individually revertible.
G5, G6 and G8 should wait until these have run for a while, so they encode observed failures
rather than guesses — which is P7's own sequencing argument, applied rather than overruled.

## Current state

Design complete, nothing implemented. The session is open and awaiting authorisation; no
implementation work has begun (N3).
