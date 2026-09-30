# VERIFICATION — CORE-GATE-EXPORT slice

Protocol §18. **Rule enforced:** a requirement may not be `VERIFIED` before it
is `APPROVED` (§9.1). **All 24 requirements were APPROVED on 2026-10-01**
(owner: Sajan / `human:curator.001`; see spec/BASELINE.md). The §9.1 blocking
condition is therefore **cleared**: verification executions may now begin.

Every record below is still `UNVERIFIED` because **no verification execution
has been run yet** — approval permits verification, it does not perform it.
The method is identified and current-behavior evidence is cited where it exists;
that evidence is as-built observation, not requirement verification (§18: a
test's existence is not proof). The "gap to real verification" column now lists
the *execution* still owed, not an approval that is missing.

| Requirement | Method | Status | Current-behavior evidence (as-built only) | Gap to real verification |
|---|---|---|---|---|
| REQ-STEMMA-CORE-001 | INSPECTION | UNVERIFIED | EVID-GATE-003; repo layout | run INSPECTION: confirm layout still holds; record date |
| REQ-STEMMA-CORE-002 | STATIC_ANALYSIS | UNVERIFIED | check_id_immutability + test_id_immutability in suite (EVID-OPS-001) | run the named method and record the result |
| REQ-STEMMA-CORE-003 | STATIC_ANALYSIS | UNVERIFIED | CI grep step (EVID-SEC-002) | run the named method and record the result |
| REQ-STEMMA-CORE-004 | UNIT_TEST | UNVERIFIED | test_generality in suite | run the named method and record the result |
| REQ-STEMMA-SCH-001 | UNIT_TEST | UNVERIFIED | validate.py gate (EVID-GATE-003) | run the named method and record the result |
| REQ-STEMMA-SCH-002 | UNIT_TEST | UNVERIFIED | test_no_version_literals_in_exporters; docs-consistency | run the named method and record the result |
| REQ-STEMMA-SCH-003 | UNIT_TEST | UNVERIFIED | test_registry_coherence in gate | run the named method and record the result |
| REQ-STEMMA-GATE-001 | INTEGRATION_TEST | UNVERIFIED | Observed fail-closed exit 1 (EVID-GATE-002) | run permanent negative-path CI test (currently manual observation) |
| REQ-STEMMA-GATE-002 | UNIT_TEST | UNVERIFIED | status_truth in gate (EVID-GATE-006) | run the named method and record the result |
| REQ-STEMMA-GATE-003 | INSPECTION | UNVERIFIED | ci.yml test-suite job (EVID-GATE-005) | observe CI red-merge block once |
| REQ-STEMMA-GATE-004 | UNIT_TEST | UNVERIFIED | test_docs_consistency exit 0 (EVID-GATE-007) | run the named method and record the result |
| REQ-STEMMA-GATE-005 | UNIT_TEST | UNVERIFIED | test_independence exit 0 (EVID-GATE-008) | run the named method and record the result |
| REQ-STEMMA-EXP-001 | UNIT_TEST + SYSTEM_TEST(CI) | UNVERIFIED | byte-identical checks in tests + CI no-wall-clock job | run the named method and record the result |
| REQ-STEMMA-EXP-002 | UNIT_TEST | UNVERIFIED | test_export_publishes_relation_registry_and_vocabularies | run the named method and record the result |
| REQ-STEMMA-EXP-003 | INTEGRATION_TEST | UNVERIFIED | CI `git diff --exit-code -- exports reports` after regeneration | run the named method and record the result |
| REQ-STEMMA-EXP-004 | INTEGRATION_TEST | UNVERIFIED | export_consumers runs; learninghub 0-entity output observed | UNRES-STEMMA-EXP-001 now closed by owner (empty export exceptional); run INTEGRATION_TEST |
| REQ-STEMMA-HITL-001 | INTEGRATION_TEST | UNVERIFIED | hitl_check in gate (EVID-HITL-001) | UNRES-STEMMA-HITL-001 (evidence locality) limits strength; run INTEGRATION_TEST |
| REQ-STEMMA-HITL-002 | INTEGRATION_TEST | UNVERIFIED | same as above | same as above |
| REQ-STEMMA-SEC-001 | STATIC_ANALYSIS | UNVERIFIED | gitleaks + grep jobs (EVID-SEC-001) | run the named method and record the result |
| REQ-STEMMA-SEC-002 | INSPECTION | UNVERIFIED | XC-5 recorded; webapp NOT_YET_ASSESSED | second pilot (webapp slice) required; owner ruling: webapp full redesign pending |
| REQ-STEMMA-OPS-001 | MEASUREMENT | UNVERIFIED | clean-venv install + gate run performed during recovery | repeat MEASUREMENT on a tagged release |
| REQ-STEMMA-OPS-002 | INSPECTION | UNVERIFIED | drift-fix diff 2026-09-22; single-source mechanisms exist | INSPECTION trend watch across releases |
| REQ-STEMMA-OPS-003 | INSPECTION | UNVERIFIED | docs/GOVERNANCE.md continuity section added 2026-10-01 (EVID-OPS-005) | run INSPECTION: procedure + successor path documented; risk dated |
| REQ-STEMMA-INTEG-001 | INTEGRATION_TEST | UNVERIFIED | explorer verify passes (EVID-INTEG-004); AI chat not yet implemented | implement grounded chat; run INTEGRATION_TEST (citations + refusal + derived-only) |

## NFR metrics (§18)

Performance/reliability requirements: **none in this slice** → no metric/threshold
records exist. Explicitly NOT_APPLICABLE rather than invented.
(Gate runtime anecdote ~3–8 s locally is observation, not a requirement.)

## Gate 6 checklist (§31)

- [x] every applicable requirement has a verification method (no permanent NOT_YET_DETERMINED)
- [x] verification status recorded (all UNVERIFIED, reason: approved 2026-10-01 but not yet executed)
- [x] unverified explicitly marked (this whole table)
- [x] objective evidence referenced for as-built observations
