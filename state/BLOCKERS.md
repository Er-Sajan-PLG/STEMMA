# BLOCKERS — Things Preventing Progress

> Record blockers **immediately**. A blocker is something that stops work and that the
> agent cannot clear by itself. If an agent *can* clear it, it is not a blocker — it is
> a task.
>
> **Current count: 3 actionable · 2 parked · 0 technical.**

---

## BLK-001 — PR #66 requires the owner to merge

**Raised:** 2026-10-01 by `A7F3`
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

## BLK-004 — Three stale repo-name references in `spec/` need an owner edit

**Raised:** 2026-10-01 by `A7F3`
**Status:** **OPEN — awaiting owner**
**Blocking:** nothing (inert metadata), but it is a wrong value in Tier-2 files

**What is needed.** Three files under `spec/` still carry the retired repo name
`Er-Sajan-PLG/STEMMA`:

| Location | Content |
|---|---|
| `spec/ROLES_AND_AUTHORITY.md:4` | `Repository: Er-Sajan-PLG/STEMMA @ fb66dd9 (arena/01a0c5b1-stemma)` |
| `spec/PILOT_CHARTER.md:6` | `\| Repository \| Er-Sajan-PLG/STEMMA (\`/home/user/STEMMA\`) \|` |
| `spec/machine-readable/authority.yaml:2` | `repository: Er-Sajan-PLG/STEMMA` |

**Why an agent cannot clear it.** `spec/` is **Tier 2** — owner-only under Constraint D.
The executor may identify the defect and record it, but must not edit a specification file on
its own authority. This is the boundary working as intended, not a gap.

**Impact: low.** Verified that no gate reads these values — `validate_recovery.py` does not
inspect the `repository` field, and nothing else loads `authority.yaml`. So this is a
correctness/clarity issue in Tier-2 records, not a broken command. (Contrast DEBT-002, where
the same stale name in `docs/` **did** break `gh attestation verify`.)

**Nuance for the owner.** `spec/ROLES_AND_AUTHORITY.md:4` cites the repo *and a commit*
(`@ fb66dd9`) as the provenance of the authority model. If that line is a historical record
of where the model was established, it may be **correct as written** and should be left alone
— in which case only `PILOT_CHARTER.md` and `authority.yaml` need a decision. The agent is
not positioned to judge that; it is a Tier-2 call.

---

## BLK-005 — `spec/CONFLICTS.md` claims a docs sync that did not happen

**Raised:** 2026-10-01 by `A7F3`
**Status:** **OPEN — awaiting owner**
**Blocking:** nothing functional, but a Tier-2 record is inaccurate

**What is needed.** `spec/CONFLICTS.md`, CONFLICT-STEMMA-EXP-001 resolution 1, states that
"the living docs that repeated the claim were synced". A sweep found **78 occurrences across 19
files** still asserting STEMMA's own store is FAISS. The docs have since been fixed (DEBT-008),
so the sentence is now true — but it was false when written, and the record should say so rather
than read as though the sync happened at the time.

**Why an agent cannot clear it.** `spec/` is **Tier 2** — owner-only under Constraint D. The
executor may identify the inaccuracy and record it, but must not edit a specification record on
its own authority.

**Suggested minimal edit (owner's call):** note that the docs sync was completed 2026-10-01 in
the same session as DEBT-008, and that the original claim was written from a partial sweep.
Whether to record the overstatement at all is the owner's judgement.

**Not urgent:** the underlying defect is fixed; this is about the record being honest.

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
