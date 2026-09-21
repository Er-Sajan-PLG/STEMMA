# DECISION 0025 — Retire the "ACTIVATE LEARNINGHUBSTEM MVP" activation phrase

- **Date:** 2026-09-04
- **Status:** decided (implemented with this change)
- **Related:** ADR-0019 (rename & freeze), `docs/HISTORY-RENAME.md`,
  `docs/STEMMA-IMPLEMENTATION-PLAN-v2.md` (E0.3, finding R2)

## Context

The rename of the repository/brand **LearningHubSTEM → STEMMA** (ADR-0019) left one
governance string behind: the MVP activation phrase `"ACTIVATE LEARNINGHUBSTEM MVP"`
survived in three governing documents (`docs/STEMMA-SPECIFICATION.md`,
`docs/STEMMA-ROADMAP.md`, `docs/GOVERNANCE.md`). The phrase is a trigger, not a label — a
human says it to activate the full MVP — and a trigger that names a retired brand is a
governance defect: someone activating the project in good faith would type the old name.

## Decision

1. The activation phrase is re-pointed to **`"ACTIVATE STEMMA MVP"`** in all three governing
   documents. The old phrase **`"ACTIVATE LEARNINGHUBSTEM MVP"`** is **retired as a trigger**
   and must not be used to activate future work.
2. This is a rename-reconciliation change only (R2 of the plan's findings register). It does
   **not** activate the MVP, and it does not change any `lhs:` ID, schema, or export contract
   (ADR-0003, ADR-0019).

## Alternatives considered

- Leave the old phrase and add a note "aka ACTIVATE STEMMA MVP" — rejected: leaves a
  dead-brand trigger as the primary string and preserves ambiguity.
- Retire the activation-phrase mechanism entirely — rejected: the phased-activation discipline
  is a governance feature (each phase requires an explicit human decision); only the brand in
  the phrase was wrong.

## Consequences

- The single active activation phrase is `"ACTIVATE STEMMA MVP"`.
- Historical records (`docs/HISTORY-RENAME.md`, dated decision records) may still quote the old
  phrase as history; that is intentional and must not be "fixed".
