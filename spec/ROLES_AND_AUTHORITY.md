# ROLES AND AUTHORITY — STEMMA Specification Recovery Pilot

```text
Repository:                 Er-Sajan-PLG/STEMMA @ fb66dd9 (arena/01a0c5b1-stemma)
Pilot Scope:                CORE-GATE-EXPORT vertical slice (see PILOT_CHARTER.md)
Specification Owner:        Sajan (repository owner, "Principal Architect")
Specification Authority:    Sajan (SOLE_OWNER)
Architecture Authority:     Sajan (SOLE_OWNER); advisory inputs: Arena agent, docs/decisions ADR history
Security Authority:         Sajan (SOLE_OWNER); no separate security officer exists
Cross-Repository Interface Owner: Sajan for STEMMA side; LearningHub/PROFESSOR-J sides: UNASSIGNED (UNRES-STEMMA-INTEG-001)
Baseline Approver:          Sajan (SOLE_OWNER) — PENDING first review of this baseline
Provisional Authority:      Arena agent (executor) — investigate/recover/classify/propose only; MAY NOT approve
Authority Mode:             SOLE_OWNER
AUTHORITY-UNKNOWN:          NO — authority is explicitly identified
Approval Process:           DRAFT → PROPOSED → owner review → APPROVED / REJECTED / DEFERRED
                            (§4.2). The executor self-approves NOTHING (§0.3.1: non-response is not approval).
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

## What the executor did NOT do (Constraint D)

- Did not set any requirement status above `PROPOSED`.
- Did not resolve any `CONFLICT-` or close any `UNRES-` record.
- Did not approve the baseline. `spec/BASELINE.md` records approval as PENDING.
