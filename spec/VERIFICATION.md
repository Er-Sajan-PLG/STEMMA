# VERIFICATION — CORE-GATE-EXPORT slice

Protocol §18. **Rule enforced:** a requirement may not be `VERIFIED` before it
is `APPROVED` (§9.1). **All 24 requirements were APPROVED on 2026-10-01**
(owner: Sajan / `human:curator.001`; see spec/BASELINE.md). The §9.1 blocking
condition is therefore **cleared** and verification executions are underway.

**Current position (2026-10-01): 13 VERIFIED · 2 FAILED · 9 UNVERIFIED.**

The two `FAILED` records are *findings, not accidents*: each names a real gap
between what a requirement promises and what its named mechanism does. They are
kept visible here rather than quietly downgraded to `UNVERIFIED`, because a
verification exercise that only ever reports PASS is not measuring anything.

Status legend: **VERIFIED** = executed, passed, dated, evidenced. **FAILED** =
executed and a criterion was not met (gap recorded; owner decides the remedy).
**UNVERIFIED** = no execution yet; approval permits verification, it does not
perform it. §18 note: a test's *existence* is never proof — every row below was
either executed or is honestly marked as not yet executed.

## Requirement matrix

| Requirement | Method | Status | Execution evidence | Remaining gap |
|---|---|---|---|---|
| REQ-STEMMA-CORE-001 | INSPECTION | UNVERIFIED | EVID-GATE-003; repo layout | run INSPECTION: confirm layout still holds; record date |
| REQ-STEMMA-CORE-002 | STATIC_ANALYSIS | **VERIFIED** (2026-10-01) | EVID-CORE-008 — immutability PASS (9 live/9 historical ids); controlled probe: control entity valid, all malformed ids rejected | ✅ done |
| REQ-STEMMA-CORE-003 | STATIC_ANALYSIS | **VERIFIED** (2026-10-01) | EVID-CORE-009 — canonical clean; injected vector literal detected (check discriminates) | ✅ done |
| REQ-STEMMA-CORE-004 | UNIT_TEST | **FAILED** (2026-10-01) | EVID-CORE-006 — guard is `^…$`-anchored, misses `grade_level`; EVID-CORE-007 — schema still catches it | guard coverage gap; **UNRES-CORE-002** (owner decision) |
| REQ-STEMMA-SCH-001 | UNIT_TEST | **VERIFIED** (2026-10-01) | EVID-SCH-007 — clean required-field removal → exit 1, names file + property | ✅ done |
| REQ-STEMMA-SCH-002 | UNIT_TEST | **VERIFIED** (2026-10-01) | EVID-SCH-006 — 8 passed incl. `test_no_version_literals_in_exporters` | ✅ done |
| REQ-STEMMA-SCH-003 | UNIT_TEST | **VERIFIED** (2026-10-01) | EVID-SCH-006 — 6 passed (inverses mutual/mirrored, symmetric no inverse, domain/range known types) | ✅ done |
| REQ-STEMMA-GATE-001 | INTEGRATION_TEST | **VERIFIED** (2026-10-01) | EVID-GATE-011 (4 passed); EVID-GATE-012 (mutation-checked, non-vacuous) | ✅ done — exit 1, step named, chain stops after 1 step |
| REQ-STEMMA-GATE-002 | UNIT_TEST | **VERIFIED** (2026-10-01) | EVID-GATE-013 — tamper probe 9→108 → exit 1 naming the divergence | ✅ done |
| REQ-STEMMA-GATE-003 | INSPECTION | UNVERIFIED | ci.yml test-suite job (EVID-GATE-005) | observe CI red-merge block once |
| REQ-STEMMA-GATE-004 | UNIT_TEST | **VERIFIED** (2026-10-01) | EVID-GATE-014 — orphan doc probe caught (`does not list: [ORPHAN-PROBE.md]`) | ✅ done |
| REQ-STEMMA-GATE-005 | UNIT_TEST | **VERIFIED** (2026-10-01) | EVID-GATE-015 — injected retired-ecosystem token caught at file:line | ✅ done |
| REQ-STEMMA-EXP-001 | UNIT_TEST + SYSTEM_TEST(CI) | **VERIFIED** (2026-10-01) | EVID-EXP-010 — byte-identical across 3 runs; `sha256:*` stamped; no wall clock | ✅ done |
| REQ-STEMMA-EXP-002 | UNIT_TEST | **FAILED** (2026-10-01) | EVID-EXP-009 — criteria 1–3 PASS; criterion 4 unmet (no `adopted_from` field exists in any schema) | implement adopted-from provenance; owner decision |
| REQ-STEMMA-EXP-003 | INTEGRATION_TEST | UNVERIFIED | CI `git diff --exit-code -- exports reports` after regeneration | run the named method and record the result |
| REQ-STEMMA-EXP-004 | INTEGRATION_TEST | UNVERIFIED | export_consumers runs; learninghub 0-entity output observed | UNRES-EXP-001 closed by owner; run INTEGRATION_TEST |
| REQ-STEMMA-HITL-001 | INTEGRATION_TEST | UNVERIFIED | hitl_check in gate (EVID-HITL-001) | UNRES-HITL-001 (evidence locality) limits strength; run INTEGRATION_TEST |
| REQ-STEMMA-HITL-002 | INTEGRATION_TEST | UNVERIFIED | same as above | same as above |
| REQ-STEMMA-SEC-001 | STATIC_ANALYSIS | **VERIFIED** (2026-10-01) | EVID-SEC-003 — canonical secret-free; gitleaks wired (ci.yml:55) + pre-commit hook | ✅ done |
| REQ-STEMMA-SEC-002 | INSPECTION | UNVERIFIED | XC-5 recorded; webapp NOT_YET_ASSESSED | second pilot (webapp slice); owner ruling: full redesign pending |
| REQ-STEMMA-OPS-001 | MEASUREMENT | **VERIFIED** (2026-10-01) | EVID-OPS-006 (clean clone, exit 0, 4.00 s, 21 steps); EVID-OPS-007 (controlled: bare venv 1/2 → +requirements.txt 0) | ✅ done |
| REQ-STEMMA-OPS-002 | INSPECTION | UNVERIFIED | EVID-OPS-008 — all single-source mechanisms exist and are gate-enforced | **not yet measurable**: criterion is a trend *across releases*; `git tag` is empty (one point, not a series) |
| REQ-STEMMA-OPS-003 | INSPECTION | **VERIFIED** (2026-10-01) | EVID-OPS-009 — procedure + successor path + dated accepted risk + exit condition documented | ✅ done |
| REQ-STEMMA-INTEG-001 | INTEGRATION_TEST | UNVERIFIED | explorer verify passes (EVID-INTEG-004); AI chat not yet implemented | implement grounded chat; run INTEGRATION_TEST (citations + refusal + derived-only) |

## The two FAILED findings

**REQ-STEMMA-CORE-004 — generality guard misses prefixed keys.**
`SCOPING_FIELDS` in `tests/curation/test_generality.py:33` is anchored `^…$`, so
it matches exact key names (`grade`, `curriculum`, `level`, `course_level`,
`country_scope`) but not variants (`grade_level`, `grade_band`,
`curriculum_scope`, `target_grade`). Injecting `grade_level: 10` into
`metre.md` frontmatter was **not** rejected by the guard.
*Severity: defence-in-depth only.* `concept.schema.json` declares
`additionalProperties: false`, so `validate.py` still rejected the injection
(exit 1). No violation can ship; the guard's stated invariant simply over-claims
relative to its implementation. Raised as **UNRES-STEMMA-CORE-002** for the owner
— the executor recorded the finding and did **not** self-approve a fix.

**REQ-STEMMA-EXP-002 — adopted-from provenance absent.**
Criteria 1–3 pass (`export_version` 2.2.0 == VERSION.yaml; `relation_registry`
(56 relations) + vocabularies sidecars present; jsonschema validation 0 errors).
Criterion 4 is unmet: no `adopted_from` field is defined in **either**
`concept.schema.json` or `export.schema.json`, and no merge/adoption history
mechanism exists. Entities carry `external_ids` (Wikidata QIDs), which is
*identity mapping*, not *adoption provenance*. The criterion is vacuously true
today (no entity has adoption history) but cannot be exercised — the mechanism
is simply absent. This is a real gap introduced when criterion 4 was added under
SOTA F3; it needs an owner decision on whether to implement or defer.

## NFR metrics (§18)

Performance/reliability requirements: **none in this slice** → no metric/threshold
records exist. Explicitly NOT_APPLICABLE rather than invented.
(Gate runtime anecdote ~3–8 s locally is observation, not a requirement. The
clean-clone measurement recorded 4.00 s over 21 steps — still an observation.)

## Gate 6 checklist (§31)

- [x] every applicable requirement has a verification method (no permanent NOT_YET_DETERMINED)
- [x] verification status recorded (13 VERIFIED · 2 FAILED · 9 UNVERIFIED as of 2026-10-01)
- [x] unverified explicitly marked
- [x] objective evidence referenced for as-built observations
- [x] VERIFIED records carry an execution date, named evidence, and a recorded result
- [x] FAILED records carry the specific unmet criterion and a routed open question

## Verification log

| Date | Requirement | Method | Result | Evidence |
|---|---|---|---|---|
| 2026-10-01 | REQ-STEMMA-GATE-001 | INTEGRATION_TEST | PASS | EVID-GATE-011, EVID-GATE-012 |
| 2026-10-01 | REQ-STEMMA-OPS-001 | MEASUREMENT | PASS | EVID-OPS-006, EVID-OPS-007 |
| 2026-10-01 | REQ-STEMMA-CORE-002 | STATIC_ANALYSIS | PASS | EVID-CORE-008 |
| 2026-10-01 | REQ-STEMMA-CORE-003 | STATIC_ANALYSIS | PASS | EVID-CORE-009 |
| 2026-10-01 | REQ-STEMMA-CORE-004 | UNIT_TEST | **FAIL** | EVID-CORE-006, EVID-CORE-007 |
| 2026-10-01 | REQ-STEMMA-SCH-001 | UNIT_TEST | PASS | EVID-SCH-007 |
| 2026-10-01 | REQ-STEMMA-SCH-002 | UNIT_TEST | PASS | EVID-SCH-006 |
| 2026-10-01 | REQ-STEMMA-SCH-003 | UNIT_TEST | PASS | EVID-SCH-006 |
| 2026-10-01 | REQ-STEMMA-GATE-002 | UNIT_TEST | PASS | EVID-GATE-013 |
| 2026-10-01 | REQ-STEMMA-GATE-004 | UNIT_TEST | PASS | EVID-GATE-014 |
| 2026-10-01 | REQ-STEMMA-GATE-005 | UNIT_TEST | PASS | EVID-GATE-015 |
| 2026-10-01 | REQ-STEMMA-EXP-001 | UNIT_TEST | PASS | EVID-EXP-010 |
| 2026-10-01 | REQ-STEMMA-EXP-002 | UNIT_TEST | **FAIL** | EVID-EXP-009 |
| 2026-10-01 | REQ-STEMMA-SEC-001 | STATIC_ANALYSIS | PASS | EVID-SEC-003 |
| 2026-10-01 | REQ-STEMMA-OPS-003 | INSPECTION | PASS | EVID-OPS-009 |

## Method notes (recorded, not hidden)

- **Mutation discipline.** Every PASS above that validates a *guard* was paired
  with a negative control: inject the violation and confirm the guard fails. A
  green run is only informative if the check can go red (EVID-GATE-012).
- **GATE-001 scope.** The negative-path execution proves the chain's own failure
  semantics — exit propagation, step naming, termination. It does **not** prove
  that each of the 17 real steps fails correctly under its own failure modes.
- **OPS-002 is deliberately left UNVERIFIED.** Every single-source mechanism
  exists (EVID-OPS-008), but the criterion is a *trend across releases* and no
  tagged releases exist yet. Marking it VERIFIED would be claiming a trend from
  one observation.
