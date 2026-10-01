# CONFLICT: CONFLICT-001-state-tier2-boundary

**Raised by:** `coding-agent.001`
**Date:** 2026-10-01
**Status:** **RESOLVED**

---

## The question

MACP declares `state/` **Tier 1 — agent sovereignty**: agents may create, update, and
resolve these files without human approval.

STEMMA declares (`spec/ROLES_AND_AUTHORITY.md` **Constraint D**) that the executor may
**not** approve/reject/defer a requirement, **not** close a `UNRES-` record, and **not**
promote an `INFERENCE` to a `FACT`.

Adopting MACP therefore risks creating a second, competing source of truth: an agent could
write a confident line into `state/DECISIONS.md` that reads like a specification ruling,
and a later agent — trusting `state/` as "the shared memory" — would act on it. The two
authority models are not obviously compatible, so this was raised rather than assumed away.

## Position A — `coding-agent.001`: the protocols compose, once scoped

MACP's tier system is about **who may write coordination state**, not about who owns the
specification. The two documents answer different questions:

- MACP answers *"how do agents coordinate?"* → `state/`
- STEMMA answers *"what is true about the knowledge base, and who may declare it?"* →
  `content/`, `connections/`, `sources/`, `spec/`

Nothing in MACP grants an agent authority over a requirement's status. Tier 1 is a
statement about `state/` files only. So there is no actual collision — but there **is** a
real risk of *accidental* collision through duplication, which the boundary below removes.

## Position B — (no second agent; raised as a design risk)

Stated for completeness, since a conflict needs both sides documented: if `state/` were
allowed to carry specification rulings, it would immediately become a rival to `spec/`.
Two registries answering the same question is precisely the failure mode this repository
already treats as a first-class defect elsewhere (see `ARCHITECTURE.md` — "canonical vs
derived"; the same reasoning applies to "canonical vs coordination").

## Resolution

**Resolved by scoping, not by precedence.** Neither protocol overrides the other; their
domains are disjoint and the boundary is written down:

| Tier | Files | Authority |
|---|---|---|
| **1 — coordination** | everything under `state/` | Agents may write freely. |
| **2 — specification** | `content/`, `connections/`, `sources/`, `spec/`, and **every requirement status** | **Owner only.** |

**Binding rules for any agent working in this repository:**

1. `state/DECISIONS.md` records **coordination** decisions. It must never restate, replace,
   or paraphrase a specification ruling.
2. A requirement status, a `UNRES-` closure, or an `INFERENCE → FACT` promotion is recorded
   **only** in `spec/`, by the owner.
3. Where a spec ruling motivates a coordination decision, `state/DECISIONS.md` **links** to
   it rather than restating it. DEC-001 is the worked example.
4. `state/` must never be cited as evidence in `spec/`. Evidence lives in
   `spec/machine-readable/evidence.yaml`.
5. If an agent believes a specification change is needed, it writes the proposal in
   `state/` **and** raises it to the owner — it does not record it as decided.

Recorded in `DECISIONS.md` as DEC-001 and DEC-003.

## Protocol note — why this file is not in `archive/`

MACP Section 4 **Phase D** says a resolved conflict moves to `state/archive/`. That step was
deliberately **not** applied here, and the deviation is recorded rather than taken
silently (per `AGENTS.md` — "Do not violate silently").

Phase D assumes a *spent* disagreement: once resolved, nothing needs to point at it. This
record is the opposite — it is a **standing boundary** that `PROTOCOL.md` and
`DECISIONS.md` both reference, and that every future agent must follow. Archiving it would
break those references and hide a rule that is still in force.

**Proposed refinement to MACP (for owner review):** Phase D should distinguish a *spent
disagreement* (archive) from a *standing boundary or invariant* (keep live, mark
`RESOLVED`). Only the former is safe to archive. This is a proposal, not a change to the
protocol text, which remains owner-authored in all supplied sections.
