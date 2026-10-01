# BLOCKERS — Things Preventing Progress

> Record blockers **immediately**. A blocker is something that stops work and that the
> agent cannot clear by itself. If an agent *can* clear it, it is not a blocker — it is
> a task.
>
> **Current count: 1 actionable · 2 parked · 0 technical.**

---

## BLK-001 — PR #66 requires the owner to merge

**Raised:** 2026-10-01 by `coding-agent.001`
**Status:** **OPEN — awaiting owner**
**Blocking:** landing the UNRES rulings, the pre-push gate fixes, and the atomic-write fix

**What is needed.** `PR #66` (*Execute owner rulings on the 7 open UNRES records + unstick
the pre-push gate*) is **OPEN · MERGEABLE · CLEAN · 30 checks pass · 0 fail**. It needs a
merge by the owner.

**Why an agent cannot clear it.** Merging to `main` is a Tier-2 act. `main` is protected by
required status checks and the owner is the sole approver. An executor may prepare and
verify a change but may not land it on the owner's authority
(`spec/ROLES_AND_AUTHORITY.md` Constraint D).

**Note.** The PR went through a rewrite: an earlier commit's subject was `spec: execute
owner rulings…`, and `spec` is not an accepted commit type (the allowed set includes
`docs`). It was reworded to `docs(spec): …` by replaying the six later commits onto the
reworded base and re-creating the merge — verified **tree-identical** to the pre-rewrite
tip, so only the message changed.

---

## Parked (not actionable — waiting on an external event)

### BLK-002 — `REQ-STEMMA-OPS-002` is parked to release time

**Status:** parked by owner ruling, 2026-10-01 (second pass)
**Unblocks when:** the next release lands

The requirement is a per-release audit of prose-owned machine values. A single data point
cannot show a trend, and the trend's first point is `v3.0.0`. The instrument and its first
point are complete and committed (`docs/PROSE-OWNED-VALUES-AUDIT.md`,
`scripts/audit_prose_owned_values.py`). The requirement correctly **remains `UNVERIFIED`**
until a second release completes the pair. **No work on this before the next release.**

### BLK-003 — `UNRES-STEMMA-CORE-003` awaits an owner ruling

**Status:** deliberately left **OPEN** by explicit owner directive
**Unblocks when:** the owner rules

This was the one record of the seven that the owner did **not** direct the executor to
close. Closing it would require converting an `INFERENCE` to a `FACT`, which Constraint D
forbids the executor from doing. It is recorded in
`spec/machine-readable/open_questions.yaml` with `owner_ruling_2026_10_01_second_pass` and
`executor_note_2026_10_01`. Its subject matter (debt method/tier decisions) is also
coupled to the pilot-scale debt measurement phase, so it may naturally resolve at release
time alongside BLK-002.

---

## Cleared

_(none yet)_

---

## What is *not* blocked

There are **no technical blockers**. Gates are green on all four layers, no conflicting
agent holds a needed file, and `state/conflicts/` holds one boundary question that does not
stop work. The three items above are all human-authority waits, not defects.
