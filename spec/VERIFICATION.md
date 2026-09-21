# VERIFICATION — CORE-GATE-EXPORT slice

Protocol §18. **Rule enforced:** a requirement may not be `VERIFIED` before it
is `APPROVED` (§9.1). All requirements are `PROPOSED`; therefore every record
below is `UNVERIFIED` — with method identified and current-behavior evidence
cited where it exists. Current-behavior evidence is as-built observation,
not requirement verification (§18: a test's existence is not proof).

| Requirement | Method | Status | Current-behavior evidence (as-built only) | Gap to real verification |
|---|---|---|---|---|
| REQ-STEMMA-CORE-001 | INSPECTION | UNVERIFIED | EVID-GATE-003; repo layout | approval; periodic re-inspection |
| REQ-STEMMA-CORE-002 | STATIC_ANALYSIS | UNVERIFIED | check_id_immutability + test_id_immutability in suite (EVID-OPS-001) | approval |
| REQ-STEMMA-CORE-003 | STATIC_ANALYSIS | UNVERIFIED | CI grep step (EVID-SEC-002) | approval |
| REQ-STEMMA-CORE-004 | UNIT_TEST | UNVERIFIED | test_generality in suite | approval |
| REQ-STEMMA-SCH-001 | UNIT_TEST | UNVERIFIED | validate.py gate (EVID-GATE-003) | approval |
| REQ-STEMMA-SCH-002 | UNIT_TEST | UNVERIFIED | test_no_version_literals_in_exporters; docs-consistency | approval |
| REQ-STEMMA-SCH-003 | UNIT_TEST | UNVERIFIED | test_registry_coherence in gate | approval |
| REQ-STEMMA-GATE-001 | INTEGRATION_TEST | UNVERIFIED | Observed fail-closed exit 1 (EVID-GATE-002) | approval; add permanent negative-path CI test (currently manual observation) |
| REQ-STEMMA-GATE-002 | UNIT_TEST | UNVERIFIED | status_truth in gate (EVID-GATE-006) | approval |
| REQ-STEMMA-GATE-003 | INSPECTION | UNVERIFIED | ci.yml test-suite job (EVID-GATE-005) | approval; observe CI red-merge block once |
| REQ-STEMMA-GATE-004 | UNIT_TEST | UNVERIFIED | test_docs_consistency exit 0 (EVID-GATE-007) | approval |
| REQ-STEMMA-GATE-005 | UNIT_TEST | UNVERIFIED | test_independence exit 0 (EVID-GATE-008) | approval |
| REQ-STEMMA-EXP-001 | UNIT_TEST + SYSTEM_TEST(CI) | UNVERIFIED | byte-identical checks in tests + CI no-wall-clock job | approval |
| REQ-STEMMA-EXP-002 | UNIT_TEST | UNVERIFIED | test_export_publishes_relation_registry_and_vocabularies | approval |
| REQ-STEMMA-EXP-003 | INTEGRATION_TEST | UNVERIFIED | CI `git diff --exit-code -- exports reports` after regeneration | approval |
| REQ-STEMMA-EXP-004 | INTEGRATION_TEST | UNVERIFIED | export_consumers runs; learninghub 0-entity output observed | approval + UNRES-STEMMA-EXP-001 closure |
| REQ-STEMMA-HITL-001 | INTEGRATION_TEST | UNVERIFIED | hitl_check in gate (EVID-HITL-001) | approval + UNRES-STEMMA-HITL-001 (evidence locality) limits strength |
| REQ-STEMMA-HITL-002 | INTEGRATION_TEST | UNVERIFIED | same as above | same as above |
| REQ-STEMMA-SEC-001 | STATIC_ANALYSIS | UNVERIFIED | gitleaks + grep jobs (EVID-SEC-001) | approval |
| REQ-STEMMA-SEC-002 | INSPECTION | UNVERIFIED | XC-5 recorded; webapp NOT_YET_ASSESSED | approval + second pilot (webapp slice) |
| REQ-STEMMA-OPS-001 | MEASUREMENT | UNVERIFIED | clean-venv install + gate run performed during recovery | approval; repeat on tagged release |
| REQ-STEMMA-OPS-002 | INSPECTION | UNVERIFIED | drift-fix diff 2026-09-22; single-source mechanisms exist | approval; trend watch |

## NFR metrics (§18)

Performance/reliability requirements: **none approved in this slice** → no
metric/threshold records exist. Explicitly NOT_APPLICABLE rather than invented.
(Gate runtime anecdote ~3–8 s locally is observation, not a requirement.)

## Gate 6 checklist (§31)

- [x] every applicable requirement has a verification method (no permanent NOT_YET_DETERMINED)
- [x] verification status recorded (all UNVERIFIED, reason: pre-approval)
- [x] unverified explicitly marked (this whole table)
- [x] objective evidence referenced for as-built observations
