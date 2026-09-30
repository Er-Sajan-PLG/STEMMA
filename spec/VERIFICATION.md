# VERIFICATION — CORE-GATE-EXPORT slice

Protocol §18. **Rule enforced:** a requirement may not be `VERIFIED` before it
is `APPROVED` (§9.1). **All 24 requirements were APPROVED on 2026-10-01**
(owner: Sajan / `human:curator.001`; see spec/BASELINE.md). The §9.1 blocking
condition is therefore **cleared** and verification executions are underway.

**Current position (2026-10-01): 16 VERIFIED · 1 FAILED · 7 UNVERIFIED.**

The one `FAILED` record is a **new finding from round 2**, not a regression: the
test-suite and `all-green` jobs run and pass, but neither is a *required* status
check on `main` — so the merge-gating clause of REQ-STEMMA-GATE-003 is not
enforced. It is routed to the owner as `UNRES-STEMMA-GATE-001` because changing
branch protection is a repository setting and a governance act, not a code
change, and the executor has no authority over it.

The two round-1 failures were repaired under owner ruling and re-verified (see
below); that FAIL→PASS history is retained deliberately, because a verification
exercise that only ever reports PASS is not measuring anything.

Status legend: **VERIFIED** = executed, passed, dated, evidenced. **FAILED** =
executed and a criterion was not met (gap recorded; owner decides the remedy).
**UNVERIFIED** = no execution yet; approval permits verification, it does not
perform it. §18 note: a test's *existence* is never proof — every row below was
either executed or is honestly marked as not yet executed.

## Requirement matrix

| Requirement | Method | Status | Execution evidence | Remaining gap |
|---|---|---|---|---|
| REQ-STEMMA-CORE-001 | INSPECTION | ✅ **VERIFIED** (2026-10-01) | EVID-CORE-011 (rogue entity outside `content/` silently ignored — `entity_count` stayed 9); EVID-CORE-012 (explorer's sole data source is `exports/knowledge.json` via one loader; regeneration leaves `exports/` byte-identical) | ✅ done — canonical locations enforced, not merely declared |
| REQ-STEMMA-CORE-002 | STATIC_ANALYSIS | **VERIFIED** (2026-10-01) | EVID-CORE-008 — immutability PASS (9 live/9 historical ids); controlled probe: control entity valid, all malformed ids rejected | ✅ done |
| REQ-STEMMA-CORE-003 | STATIC_ANALYSIS | **VERIFIED** (2026-10-01) | EVID-CORE-009 — canonical clean; injected vector literal detected (check discriminates) | ✅ done |
| REQ-STEMMA-CORE-004 | UNIT_TEST | ✅ **VERIFIED** (2026-10-01, after repair) | EVID-CORE-006/007 (the defect) → **EVID-CORE-010** (the fix). Guard widened to token-based, 28 variants caught; mutation-revert turns the new tests red | ✅ done — FAILED → VERIFIED (UNRES-CORE-002 closed) |
| REQ-STEMMA-SCH-001 | UNIT_TEST | **VERIFIED** (2026-10-01) | EVID-SCH-007 — clean required-field removal → exit 1, names file + property | ✅ done |
| REQ-STEMMA-SCH-002 | UNIT_TEST | **VERIFIED** (2026-10-01) | EVID-SCH-006 — 8 passed incl. `test_no_version_literals_in_exporters` | ✅ done |
| REQ-STEMMA-SCH-003 | UNIT_TEST | **VERIFIED** (2026-10-01) | EVID-SCH-006 — 6 passed (inverses mutual/mirrored, symmetric no inverse, domain/range known types) | ✅ done |
| REQ-STEMMA-GATE-001 | INTEGRATION_TEST | **VERIFIED** (2026-10-01) | EVID-GATE-011 (4 passed); EVID-GATE-012 (mutation-checked, non-vacuous) | ✅ done — exit 1, step named, chain stops after 1 step |
| REQ-STEMMA-GATE-002 | UNIT_TEST | **VERIFIED** (2026-10-01) | EVID-GATE-013 — tamper probe 9→108 → exit 1 naming the divergence | ✅ done |
| REQ-STEMMA-GATE-003 | INSPECTION | ⚠️ **FAILED** (2026-10-01) | EVID-GATE-016 — both named criteria PASS (test-suite runs `pytest tests/ -q`; `all-green` needs it and asserts its result). EVID-GATE-017 — **`neither` is a required status check on `main`** | **UNRES-GATE-001** (owner action: add both to required checks) |
| REQ-STEMMA-GATE-004 | UNIT_TEST | **VERIFIED** (2026-10-01) | EVID-GATE-014 — orphan doc probe caught (`does not list: [ORPHAN-PROBE.md]`) | ✅ done |
| REQ-STEMMA-GATE-005 | UNIT_TEST | **VERIFIED** (2026-10-01) | EVID-GATE-015 — injected retired-ecosystem token caught at file:line | ✅ done |
| REQ-STEMMA-EXP-001 | UNIT_TEST + SYSTEM_TEST(CI) | **VERIFIED** (2026-10-01) | EVID-EXP-010 — byte-identical across 3 runs; `sha256:*` stamped; no wall clock | ✅ done |

| REQ-STEMMA-EXP-002 | UNIT_TEST | ✅ **VERIFIED** (2026-10-01, after implementation) | EVID-EXP-009 (the gap) → **EVID-EXP-011/012/013**. `adopted_from` declared in both schemas, enforced by `check_adopted_from`, projected into the export; malformed variants rejected; export byte-identical (additive) | ✅ done — FAILED → VERIFIED (ADR-0056) |
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

**No `FAILED` record is left unrepaired** — the two round-1 failures were ruled
on, fixed, and re-verified (see below).

## The round-2 finding — GATE-003, the merge gate that does not gate

**REQ-STEMMA-GATE-003 — CI runs the full test suite, and the merge gate requires
its success.** *Raised.* Both named acceptance criteria **PASS**:
`ci.yml:262-284` defines the `test-suite` job running `python3 -m pytest tests/ -q`,
and `all-green` (`:328-345`) lists `test-suite` in `needs` *and* asserts
`needs.test-suite.result == 'success' → exit 1`. Live run `36316235760` shows
both jobs green.

**What fails is the third clause**: the requirement says the all-green gate
"SHALL **require** its success". The live repository configuration — checked via
the GitHub API, not the workflow file — requires only:

> `Validate Knowledge Base` · `Security scan` · `Verify Governance Docs` ·
> `Branching Strategy` · `Conventional Commits (commitlint)`

Neither `Full Test Suite (pytest)` nor `All Checks Green` is among them. **A pull
request with a red test suite, or a red all-green, can still be merged.**

This is invisible to workflow inspection by construction: branch protection is a
repository setting, not a file in the repo. That is precisely why the criterion
names the *merge gate* rather than the *job* — and why inspecting only `ci.yml`
would have produced a false PASS. Routed as **UNRES-STEMMA-GATE-001**; the fix
(add both contexts to the required checks) is a repository-settings action, not
a code change, and is reserved to the owner.

## The two round-1 findings — raised, routed, repaired, re-verified

Both findings below were raised in round 1 and returned **FAILED**. Neither was
quietly downgraded. The owner ruled the remedy on 2026-10-01; both were fixed and
re-verified the same day. The FAIL→PASS history is retained deliberately: it is
the evidence that the gap was closed, and it records that the executor did not
self-approve either repair (Constraint D — the *ruling* came from the owner).

**REQ-STEMMA-CORE-004 — generality guard missed prefixed keys.** *Raised.*
`SCOPING_FIELDS` in `tests/curation/test_generality.py` was anchored `^…$`, so it
matched exact key names (`grade`, `curriculum`, `level`, `course_level`,
`country_scope`) but not variants (`grade_level`, `grade_band`,
`curriculum_scope`, `target_grade`). Injecting `grade_level: 10` into `metre.md`
frontmatter was **not** rejected by the guard. *Severity: defence-in-depth only* —
`concept.schema.json` declares `additionalProperties: false`, so `validate.py`
still rejected the injection (exit 1). Raised as **UNRES-STEMMA-CORE-002**.
→ **Repaired** (owner chose *widen + mutation-test*): the anchored regex was
replaced by a token-based matcher catching 28 variants while still allowing
`upgrade_notes`/`multigrade`/`trophic_level`. Non-vacuity proved by reverting the
matcher and watching the new tests go red (EVID-CORE-010). **UNRES-CORE-002 closed.**

**REQ-STEMMA-EXP-002 — adopted-from provenance was absent.** *Raised.*
Criteria 1–3 passed; criterion 4 was unmet: no `adopted_from` field was defined in
**either** `concept.schema.json` or `export.schema.json`, and no merge/adoption
history mechanism existed. Entities carry `external_ids` (Wikidata QIDs), which is
*identity mapping*, not *adoption provenance*. The criterion was vacuously true
(no entity had adoption history) but could not be exercised.
→ **Repaired** (owner chose *implement*, not defer): see **ADR-0056**.
`adopted_from` is now a closed object in both schemas (`external_id` + closed
`relation` enum + optional `source_external_ids`/`note`/`adopted_at`/`authority`),
enforced by `check_adopted_from()` in `validate.py` (mirroring `check_historical`,
including unknown-key rejection) and projected into `entities[]`. A valid record
on a real entity survived validation and appeared in the export; malformed
variants each produced exit 1 with a named error. The change is **additive** —
`exports/knowledge.json` is byte-identical where no entity is an adoption, so
`export_version` correctly stays `2.2.0` (EVID-EXP-011/012/013).

**Both round-1 `FAILED` records are now `VERIFIED`.** The remaining 7
requirements are `UNVERIFIED` — execution owed, not defects — and the single
`FAILED` record is the round-2 GATE-003 merge-gating finding above.

## NFR metrics (§18)

Performance/reliability requirements: **none in this slice** → no metric/threshold
records exist. Explicitly NOT_APPLICABLE rather than invented.
(Gate runtime anecdote ~3–8 s locally is observation, not a requirement. The
clean-clone measurement recorded 4.00 s over 21 steps — still an observation.)

## Gate 6 checklist (§31)

- [x] every applicable requirement has a verification method (no permanent NOT_YET_DETERMINED)
- [x] verification status recorded (16 VERIFIED · 1 FAILED · 7 UNVERIFIED as of 2026-10-01)
- [x] unverified explicitly marked
- [x] objective evidence referenced for as-built observations
- [x] VERIFIED records carry an execution date, named evidence, and a recorded result
- [x] FAILED records carry the specific unmet criterion and a routed open question
- [x] no round-1 FAILED record is left unrepaired: both were ruled on, fixed, and re-verified
- [x] round-2 FAILED (GATE-003) carries its unmet clause and a routed open question (UNRES-GATE-001)

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
| 2026-10-01 | REQ-STEMMA-CORE-004 | UNIT_TEST | PASS (**re-verified after repair**) | EVID-CORE-010 |
| 2026-10-01 | REQ-STEMMA-EXP-002 | UNIT_TEST | PASS (**re-verified after implementation**) | EVID-EXP-011, EVID-EXP-012, EVID-EXP-013 |
| 2026-10-01 | REQ-STEMMA-OPS-003 | INSPECTION | PASS | EVID-OPS-009 |
| 2026-10-01 | REQ-STEMMA-CORE-001 | INSPECTION | PASS | EVID-CORE-011, EVID-CORE-012 |
| 2026-10-01 | REQ-STEMMA-GATE-003 | INSPECTION | **FAIL** (merge-gating clause) | EVID-GATE-016, EVID-GATE-017 |
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
