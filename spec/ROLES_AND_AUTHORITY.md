# ROLES AND AUTHORITY — STEMMA Specification Recovery Pilot

```text
Repository:                 Er-Sajan-PLG/STEMMA @ fb66dd9 (arena/01a0c5b1-stemma)
Pilot Scope:                CORE-GATE-EXPORT vertical slice (see PILOT_CHARTER.md)
Specification Owner:        Sajan (repository owner, "Principal Architect")
Specification Authority:    Sajan (SOLE_OWNER)
Architecture Authority:     Sajan (SOLE_OWNER); advisory inputs: Arena agent, docs/decisions ADR history
Security Authority:         Sajan (SOLE_OWNER); no separate security officer exists
Cross-Repository Interface Owner: Sajan for STEMMA side; LearningHub/PROFESSOR-J sides: UNASSIGNED (UNRES-STEMMA-INTEG-001)
Baseline Approver:          Sajan (SOLE_OWNER) — **APPROVED 2026-10-01** (all 24 requirements + baseline)
Provisional Authority:      Arena agent (executor) — investigate/recover/classify/propose only; MAY NOT approve
Authority Mode:             SOLE_OWNER
AUTHORITY-UNKNOWN:          NO — authority is explicitly identified
Approval Process:           DRAFT → PROPOSED → owner review → APPROVED / REJECTED / DEFERRED
                            (§4.2). The executor self-approves NOTHING (§0.3.1: non-response is not approval).
                            Status 2026-10-01: all 24 slice requirements APPROVED by the owner.
Conflict Escalation Path:   executor records CONFLICT-*, classifies required authority level
                            (REPOSITORY_LOCAL / CROSS_REPOSITORY / EXTERNAL / HUMAN_DECISION),
                            owner resolves; external bodies (BIPM/IUPAC etc.) are authority
                            for domain truth, not for this specification.
```

## SOLE_OWNER limitation record (§4.1)

Independence is **absent**: a single person specifies, approves, and (via the
agent) executes. Approval is based on sole-owner authority. Limitation: no
independent reviewer catches owner blind spots; mitigations in use are the
machine gates (CI, validator, docs-consistency and independence invariants)
and this artifact set's explicit evidence/confidence classification. This
limitation is part of the baseline record, not a defect to hide.

## Interim three-role waiver — promotion chain (ADR-0057 §1a)

The promotion chain is `validator → independent_validator → board`, and each
stage must be performed by a **different human** on a **different calendar day**
(`ENF-STEMMA-HITL-001`..`004`, `spec/machine-readable/enforcement_rules.yaml`).

**Current interim state (owner directive 2026-10-01):** the owner — Sajan,
`human:curator.001` — acts as **all three roles** "for now, until I say so."
This is a deliberate, temporary deviation from the independence rule, and it is
made machine-visible rather than silently permitted:

- `schema/agent-registry.yaml` records
  `human:curator.001` with `roles: [validator, independent_validator, board]`.
- Every promotion completed under this state MUST carry a
  `provenance.promotion_history[].independence_waiver` naming
  `sanctioned_by`, `reason` and `retire_when` (ADR-0057 §1a). The gate fails if
  the actors are not distinct and the waiver is absent.
- The day-gap rule is **not** waivable. Acting as all three roles on one day is
  refused in real time by `scripts/review_entity.py` and by the gate — the owner
  has explicitly asked that this be impossible to break.
- **Retires when:** a second active human agent with a validation role is
  registered. Until then, any canonicalization is measurably *biased* — that is
  the recorded, accepted cost of the interim state.

### Board stage waived while the owner is the sole validator (ADR-0057 §1c)

Owner ruling, later on 2026-10-01: *"waive the board for now as I am the only
validator."*

The board stage presumes a **≥2-human** panel that does not exist yet. Rather than
fake a board (which the ≥2 rule would reject anyway) or leave `canonical`
unreachable, the stage is **omitted** and the omission is recorded as data:
`ENF-STEMMA-HITL-003.board_waiver {active: true,
required_stages_while_waived: [validator, independent_validator],
retire_when: a second active human agent with a validation role is registered}`.

- The **required chain is two stages** while the waiver is active; `validate.py`
  resolves it from the registry at run time. A record carrying a board stage now
  fails the gate.
- `canonical` is reachable from `independently_validated`; the CLI will not write a
  board stage while the waiver holds.
- Stage 1 and stage 2 must still be distinct humans, or carry the §1a waiver — the
  board waiver does not weaken the independence rule for the stages that remain.
- **Retires when:** a second active human with a validation role is registered.
  Retiring it restores the three-stage ≥2-human chain mechanically.

## What the executor did NOT do (Constraint D)

- Did not set any requirement status above `PROPOSED`. *(The 2026-10-01 transition to
  `APPROVED` was entered by the owner — Sajan, `human:curator.001` — not by the executor.)*
- Did not resolve any `CONFLICT-` or close any `UNRES-` record.
- Did not approve the baseline. *(The baseline approval on 2026-10-01 is the owner's.)*

The executor's constraint continues to hold after approval: it may now *execute
verification* (L3 → L4) and *record* results, but it still may not approve, reject, or
defer requirements, nor convert an INFERENCE to a FACT without owner review.
