# DECISIONS — pilot decision records + relationship to project ADRs

Two distinct decision layers exist in this repository (do not conflate, §0.2):

1. **Project/system ADRs** — the historical, authoritative record of STEMMA's
   own architecture decisions: `docs/decisions/` (0040–0052, beginning series;
   0001–0039 archived). These are evidence for recovery (CLAIM/FACT class:
   they record that a decision was made, with stated rationale), e.g.:
   - ADR-0042 minimal relation set (basis of REQ-STEMMA-SCH-003 framing)
   - ADR-0045 value-slot, ADR-0046 warrant axis, ADR-0048 new relations
   - ADR-0049 delegated authority, ADR-0050 contract 2.2.0, ADR-0051 hygiene
2. **Pilot recovery ADRs** (this directory) — decisions made *by the recovery
   process itself*:
   - `ADR-STEMMA-SPEC-001-slice-selection.md`

Rules: historical rationale is never invented; where a historical decision's
reasoning is not recorded, the correct entry is `RATIONALE-UNKNOWN` (none
needed so far — the beginning-series ADRs carry rationale). Recovered
architectural facts (domains, layers) live in AS_BUILT/SPECIFICATION, not here.
New pilot-scope ADRs use `ADR-STEMMA-<DOMAIN>-NNN`.
