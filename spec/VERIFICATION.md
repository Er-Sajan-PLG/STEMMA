# VERIFICATION — CORE-GATE-EXPORT slice

Protocol §18. **Rule enforced:** a requirement may not be `VERIFIED` before it
is `APPROVED` (§9.1). **All 25 requirements were APPROVED on 2026-10-01**
(owner: Sajan / `human:curator.001`; see spec/BASELINE.md). The §9.1 blocking
condition is therefore **cleared** and verification executions are underway.

**Current position (2026-10-01): 24 VERIFIED · 0 FAILED · 1 UNVERIFIED.**

The three findings raised earlier in this drive (CORE-004, EXP-002 criterion 4,
GATE-003) were all repaired and re-verified. A **fourth** finding — HITL
enforcement — was raised, routed to the owner as `UNRES-STEMMA-HITL-002`, and
**ruled on by the owner on 2026-10-01**; it is now closed and its two
requirements are repaired and re-verified. The finding was the more serious of
the classes of work, because it was not a gap inside a guard: it was a gap
between a requirement ("AI-drafted content stays draft until a named human
reviews it") and a corpus where six of nine canonical entities declared an
**LLM** writer.

The owner's ruling had three parts, all executed in this push: **(1) scope** —
HITL covers *all* data (`content/` and every entity type), not only
`connections/`; the chain now runs `hitl_check.py --all` instead of the vacuous
`--check-workflow` over a git-ignored, empty directory. **(2) corpus** — the six
LLM-written canonical entities were demoted to `draft` and their unsupported
human-review claims (`provenance.reviewer`/`reviewed_at`) removed; the corpus is
now **1 canonical** (`metre`, human-written *and* human-reviewed) / **8 clean
drafts**. The canonical-but-LLM-asserted connection `conn.000157` — which cited
two now-draft endpoints — was demoted to `unreviewed`. **(3) enforcement** — the
validator now validates what it claims: `validate.py` gained a content-layer
human-writer+reviewer rule (`check_entity_agents`) and canonical-endpoint
coupling for connections (a review-status connection may only cite canonical
entities). Every new gate is **mutation-proven non-vacuous** — each defect the
ruling targets turns a gate red, and restoring turns it green.

The round-2 finding was that the test-suite and `all-green` jobs ran and passed,
but neither was a *required* status check on `main` — so the merge-gating clause
of REQ-STEMMA-GATE-003 was not enforced. Changing branch protection is a
repository setting and a governance act, not a code change, so it was routed to
the owner as `UNRES-STEMMA-GATE-001`. The owner added both checks; re-inspection
of the **effective** rules (`repos/…/rules/branches/main`, not the legacy
`branches/main/protection` endpoint, which does not reflect ruleset-based rules)
confirms all 7 required checks, `strict_required_status_checks_policy: true`, and
**byte-exact** context-string matches against the live CI job names. Closed and
re-verified as `EVID-STEMMA-GATE-018`.

The FAIL→PASS history for all findings is retained deliberately, because a
verification exercise that only ever reports PASS is not measuring anything.
The HITL rows below are kept as they were found (FAILED, with the exact
evidence) and carry a repair note, rather than being silently rewritten.

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
| REQ-STEMMA-GATE-003 | INSPECTION | ✅ **VERIFIED** (2026-10-01, after repair) | EVID-GATE-016 — both named criteria PASS (test-suite runs `pytest tests/ -q`; `all-green` needs it and asserts its result). EVID-GATE-017 — the defect: neither was a required status check. **EVID-GATE-018** — the fix: 7 required checks now include `Full Test Suite (pytest)` and `All Checks Green — Nothing Bad Gets Merged`; `strict=true`; context strings byte-match live CI job names | ✅ done — FAILED → VERIFIED (UNRES-GATE-001 closed) |
| REQ-STEMMA-GATE-004 | UNIT_TEST | **VERIFIED** (2026-10-01) | EVID-GATE-014 — orphan doc probe caught (`does not list: [ORPHAN-PROBE.md]`) | ✅ done |
| REQ-STEMMA-GATE-005 | UNIT_TEST | **VERIFIED** (2026-10-01) | EVID-GATE-015 — injected retired-ecosystem token caught at file:line | ✅ done |
| REQ-STEMMA-EXP-001 | UNIT_TEST + SYSTEM_TEST(CI) | **VERIFIED** (2026-10-01) | EVID-EXP-010 — byte-identical across 3 runs; `sha256:*` stamped; no wall clock | ✅ done |

| REQ-STEMMA-EXP-002 | UNIT_TEST | ✅ **VERIFIED** (2026-10-01, after implementation) | EVID-EXP-009 (the gap) → **EVID-EXP-011/012/013**. `adopted_from` declared in both schemas, enforced by `check_adopted_from`, projected into the export; malformed variants rejected; export byte-identical (additive) | ✅ done — FAILED → VERIFIED (ADR-0056) |
| REQ-STEMMA-EXP-003 | INTEGRATION_TEST | ✅ **VERIFIED** (2026-10-01) | EVID-EXP-014 (ci.yml:32-34 gate is present, wired after the chain, repeated at :283/:301 and release.yml:69); EVID-EXP-015 (negative control: appended entity **and** edited existing entity → exit 1); EVID-EXP-016 (positive control: `validate.py` regeneration restored the diff to 0) | ✅ done — non-vacuous **and** a true freshness gate, not a tautology |
| REQ-STEMMA-EXP-004 | INTEGRATION_TEST | ✅ **VERIFIED** (2026-10-01) | EVID-EXP-017 (`--review-policy all` → **9** entities incl. all 8 drafts; `canonical` → **1**, `{canonical}` only — filter is non-vacuous; the whole corpus is now exercised since the demotion widened the draft set from 2 to 8); EVID-EXP-006 (the old 0-entity observation) | ✅ done — AC2 confirmed by the owner (canonical-only consumer contract is intended); `UNRES-STEMMA-EXP-001` closed |
| REQ-STEMMA-HITL-001 | INTEGRATION_TEST | ✅ **VERIFIED** (2026-10-01, owner-ruled repair) | EVID-HITL-003/004 (the finding: chain step vacuous, 6/9 canonical entities LLM-written) → **EVID-HITL-006** (chain now runs `--all`; 6 entities demoted; corpus 1 canonical/8 draft) → **EVID-HITL-007** (mutation proof: draft→canonical with LLM writer, and metre's writer→llm, each turn `validate.py` AND `hitl_check --all` red; restore → green) → **EVID-HITL-008** (content-layer writer+reviewer rule added) | ✅ done — FAILED → VERIFIED (UNRES-HITL-002 closed by owner ruling) |
| REQ-STEMMA-HITL-002 | INTEGRATION_TEST | ✅ **VERIFIED** (2026-10-01, owner-ruled repair) | EVID-HITL-005 (the finding) → **EVID-HITL-006/007/008**. The per-entity human-review requirement is now status-aware (only review-status entities are gated; drafts exempt; staging always writer-gated) and exercised over all data in CI; 15 negative-control tests pass (unregistered/retired/institutional/machine writers, cross-entity edits, substring slugs, fail-closed unreadable registry) | ✅ done — FAILED → VERIFIED; residual UNRES-HITL-001 is evidence *portability*, not behavior |
| REQ-STEMMA-HITL-003 | INTEGRATION_TEST | ✅ **VERIFIED** (2026-10-01, owner directive + two same-day amendments) | **EVID-HITL-009** (adoption: staged chain + debt enforcement wired into `validate.py`/`review_entity.py`, both schemas extended, chain exit 0) → **EVID-HITL-010** (mutation proof, 8 cases: incomplete waived chain, same-day stages, board stage while waived, empty history, outstanding debt full-block on an entity, the same on a *connection*, connection debt, and deletion of the enforcement registry — each exit 1; restore → exit 0) → **EVID-HITL-011** (board waiver `ENF-003.board_waiver` + pilot-scale full debt block `ENF-002.pilot_scale_block`, both read from the registry at run time; 18 tests pass; retiring the waiver turns the gate red) | ✅ done — non-vacuous; chain shape and debt mode are data-driven and fail closed |
| REQ-STEMMA-SEC-001 | STATIC_ANALYSIS | **VERIFIED** (2026-10-01) | EVID-SEC-003 — canonical secret-free; gitleaks wired (ci.yml:55) + pre-commit hook | ✅ done |
| REQ-STEMMA-SEC-002 | INSPECTION | ✅ **VERIFIED** (2026-10-01) | EVID-SEC-004 (all **6245** history objects scanned for 6 key shapes → zero matches; negative control proves the scan fires on a plant); EVID-SEC-005 (`.env.example` template with empty values, `.env` git-ignored, runtime loader at `providers.py:43-51`, gitleaks in CI) | ✅ done — AC1 non-vacuously clean; AC2 boundary enforced (re-review at second pilot is hygiene, not an unmet criterion) |
| REQ-STEMMA-OPS-001 | MEASUREMENT | **VERIFIED** (2026-10-01) | EVID-OPS-006 (clean clone, exit 0, 4.00 s, 21 steps); EVID-OPS-007 (controlled: bare venv 1/2 → +requirements.txt 0) | ✅ done |
| REQ-STEMMA-OPS-002 | INSPECTION | UNVERIFIED | EVID-OPS-008 — all single-source mechanisms exist and are gate-enforced; owner ruled a documented per-release audit as the instrument, trend starts at `v3.0.0` | **not yet measurable**: criterion is a trend *across releases*; the audit is now recorded at `v3.0.0` (one point, not a series) — deliberately stays UNVERIFIED until a second release completes the pair |
| REQ-STEMMA-OPS-003 | INSPECTION | **VERIFIED** (2026-10-01) | EVID-OPS-009 — procedure + successor path + dated accepted risk + exit condition documented | ✅ done |
| REQ-STEMMA-INTEG-001 | INTEGRATION_TEST | ✅ **VERIFIED** (2026-10-01) | EVID-INTEG-005 (`verify-graph-projection.mjs` exit 0, 10 PASS, non-vacuous); EVID-INTEG-007 (explorer-build is an all-green dependency); EVID-INTEG-006 (zero `content/`/`.md` references; sole input `exports/knowledge.json`); EVID-INTEG-008 (AC3: `verify-grounded-chat.mjs` 35 PASS, refusal + fabricated-citation sabotages each fail the run) | ✅ done — AC3 grounded chat implemented and gated in CI; citations are subset-of-export and an off-corpus question is refused |

**No `FAILED` record remains** — all three findings (two from round 1, one from
round 2) were ruled on, fixed, and re-verified (see below).

## The round-2 finding — GATE-003, the merge gate that does not gate

**REQ-STEMMA-GATE-003 — CI runs the full test suite, and the merge gate requires
its success.** *Raised.* Both named acceptance criteria **PASS**:
`ci.yml:262-284` defines the `test-suite` job running `python3 -m pytest tests/ -q`,
and `all-green` (`:328-345`) lists `test-suite` in `needs` *and* asserts
`needs.test-suite.result == 'success' → exit 1`. Live run `36316235760` shows
both jobs green.

**What failed was the third clause**: the requirement says the all-green gate
"SHALL **require** its success". The live repository configuration — checked via
the GitHub API, not the workflow file — then required only:

> `Validate Knowledge Base` · `Security scan` · `Verify Governance Docs` ·
> `Branching Strategy` · `Conventional Commits (commitlint)`

Neither `Full Test Suite (pytest)` nor `All Checks Green` was among them. **A
pull request with a red test suite, or a red all-green, could still be merged.**

This was invisible to workflow inspection by construction: branch protection is a
repository setting, not a file in the repo. That is precisely why the criterion
names the *merge gate* rather than the *job* — and why inspecting only `ci.yml`
would have produced a false PASS. Routed as **UNRES-STEMMA-GATE-001**; the fix
(adding both contexts to the required checks) is a repository-settings action, not
a code change, and was reserved to the owner.

*Repaired and re-verified.* The owner added both contexts. Re-inspection of the
**effective** rules — `repos/…/rules/branches/main`, the authoritative endpoint;
the legacy `branches/main/protection` endpoint does **not** reflect ruleset-based
rules and would have shown a stale five-check list — now returns **7** required
checks including both:

> `Full Test Suite (pytest)` · `All Checks Green — Nothing Bad Gets Merged`

with `strict_required_status_checks_policy: true`, and each required context
string **byte-exactly** matches the CI job name reported by run `36316235760`
(including the em-dash in `All Checks Green — Nothing Bad Gets Merged`; a
near-miss would have silently failed to bind). Recorded as `EVID-STEMMA-GATE-018`.
The underlying failure path was already fail-closed (`verify_all.py` exits
non-zero and terminates the chain), so the repair closes the *gating* gap without
touching the detection logic.

Repository ruleset inventory at fix time: `main` (id `22215824`,
`enforcement: active`, scoped to `refs/heads/main`) is the only active ruleset and
carries all 7 checks; `BRANCHES` (id `22216058`, `enforcement: disabled`, scoped
to `~ALL`) is inert. One nuance recorded but not treated as a finding: the
required-checks rule sets `do_not_enforce_on_create: true`, which only exempts
the branch's initial creation and does not weaken normal PR merges.

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

**All three earlier `FAILED` records are now `VERIFIED`** (two from round 1, one
from round 2), and **REQ-STEMMA-EXP-003** plus **REQ-STEMMA-SEC-002** were
verified in the same push. But the same push raised **two new `FAILED` records**
— HITL-001 and HITL-002 — described immediately below.

The 3 remaining `UNVERIFIED` are **not all equal**, and the matrix now records
their acceptance-criteria status individually rather than lumping them as
"execution owed":

- **EXP-004** — AC2 was confirmed by the owner (canonical-only consumer contract
  is intended); `UNRES-STEMMA-EXP-001` closed, requirement **VERIFIED**.
- **INTEG-001** — AC1, AC2 and AC4 all **PASS** for the graph viewer, and AC3 is
  now **implemented and verified**: the grounded chat exists, cites real export
  ids, and refuses when ungrounded (EVID-INTEG-008). Requirement **VERIFIED**.
- **OPS-002** — the only one still blocked purely on a precondition: its
  criterion is a trend *across releases*. The owner ruled a documented
  per-release audit as the instrument; the first data point (`v3.0.0`) is
  recorded, and a second release is needed to complete the pair.

Stating it this way matters: "UNVERIFIED" hides the difference between *we have
not looked yet* and *we looked, and it is not built*. Both of those were true of
this drive at different times — and the third case is *we looked, and the
evidence needs a second release to exist*.

### REQ-STEMMA-EXP-003 — derived-artifact freshness, verified by execution

The criterion names a CI step (`git diff --exit-code -- exports reports`), so the
tempting move is to *read* `ci.yml` and call it verified. That would test the
file, not the gate. Instead the step was **executed as an integration test**
against the real artifacts (EVID-EXP-014/015/016):

- **Negative control — the gate can go red.** Appending a new entity to
  `exports/knowledge.json` → exit 1. Editing an *existing* entity's field
  (`stemma:phys.force`) → exit 1. Both a "missing regeneration" and a "stale
  regeneration" are caught.
- **Positive control — the gate is not a tautology.** After mutating the
  artifact, `python3 scripts/validate.py` (the canonical generator) regenerated
  it; the diff returned to **0** with a clean tree. This matters: without it, a
  gate that merely compares the artifact to its own committed copy would look
  identical and pass forever. Regeneration restoring the file byte-for-byte is
  what makes a green diff *mean* the derived artifacts match their sources.

The same gate is repeated at `ci.yml:283` (tests must not mutate derived
artifacts) and `:301`, and in `release.yml:69` at tag time.

## The HITL finding — a gate that passes because it has nothing to look at

**REQ-STEMMA-HITL-001 — human review before canonical.** *Raised, FAILED.* The
chain does include the step: `scripts/verify_all.py:31` runs
`hitl_check.py --check-workflow` as step 8. But executing that exact invocation
produces:

```
Candidates: 0 markdown files
Proposals: 0 markdown files
Human edits (HITL): 0
OK: no workflow candidates or proposals yet — nothing to check      # exit 0
```

`workflow/` is git-ignored (`.gitignore:10`) and `git ls-files workflow/` returns
**zero** tracked files. So AC1 is **present but vacuous**: the gate audits a
directory that is empty on every fresh clone, and asserts nothing about the nine
entities in `content/`.

Then AC2 — "every canonical entity carries a human writer" — is checked against
the derived export:

| entity | status | `provenance.writer` |
|---|---|---|
| conservation-energy · force · length · mass · newtons-second-law · time | **canonical** | `llm:coding-agent.001` |
| metre | canonical | `human:curator.001` |
| kilogram · second | draft | `llm:coding-agent.001` |

**Six of nine canonical entities declare an LLM writer**, directly contradicting
the requirement's statement. `hitl_check.py --all` independently returns exit 1
with `9/9 entities fail HITL`. Nothing in the chain surfaces this, because no gate
applies the rule to `content/`: `validate.py`'s human-reviewer check
(`check_connection_agents`) is scoped to `connections/` only.

This is the mirror image of the GATE-003 defect and worth stating plainly. There,
a real gate was not wired into the merge gate. Here, the check is present and
correct but **scoped to an empty directory**, so a green result carries no
information. A check that cannot fail is not a weaker check — it is a different
thing wearing the same name.

**REQ-STEMMA-HITL-002 — explicit human markdown edit mandatory.** *Raised,
FAILED.* AC1 is properly implemented in the checker (`hitl_check.py:12,56-60,139`
requires a `candidate_edited` event attributed to a registered human). The live
trail, however, contains six events — `config_saved` ×2, `document_uploaded`,
`extraction_started`, `extraction_complete`, `candidates_generated` — and **zero
`candidate_edited` events**. The check is correct but never exercised, for the
same scoping reason.

Both were routed as **`UNRES-STEMMA-HITL-002`** (owner ruling required; the
remediation touches provenance, which the executor will not rewrite unilaterally)
and are entangled with the pre-existing **`UNRES-STEMMA-HITL-001`** (the audit
trail is git-ignored, so HITL evidence is not repository-portable — a fresh clone
cannot verify any of it).

### Resolution — the owner's ruling (2026-10-01)

The owner ruled on all three questions, and the executor carried out the ruling:

1. **Scope = all data.** The owner's words: *"HITL scope is all data, not only
   connection, its content and everything all entity."* The chain now runs
   `hitl_check.py --all`, which audits `content/` (every entity type) **and**
   `connections/`. The vacuous `--check-workflow` step is gone.
2. **Demote the six.** *"demote 6 llm written canonical entities."* Done:
   `conservation-energy`, `force`, `length`, `mass`, `newtons-second-law`, `time`
   → `draft`. Their unsupported `provenance.reviewer`/`reviewed_at` claims were
   removed too — you cannot demote to draft while leaving a false human-review
   assertion in the metadata. The corpus is now **1 canonical / 8 drafts**.
3. **Validate everything.** *"validator validates the work given it is to
   validate … they must validate everything."* `validate.py` now enforces a
   content-layer human-writer+reviewer rule (the analog of
   `check_connection_agents`) and canonical-endpoint coupling for connections.

Executing the ruling exposed a fourth, latent defect: the connection-endpoint
check **said** "does not resolve to a canonical entity" but only tested ID
membership (EVID-HITL-008). With the coupling enforced, the canonical connection
`conn.000157` — LLM-asserted, citing two now-draft endpoints — could no longer
stand, and was demoted to `unreviewed`. That is the invariant working as
documented for the first time.

| entity / connection | before | after |
|---|---|---|
| conservation-energy · force · length · mass · newtons-second-law · time | canonical (`writer=llm:i`) | **draft** (review claim removed) |
| metre | canonical (human) | canonical (human) — unchanged |
| kilogram · second | draft | draft — unchanged |
| conn.000157 (force → mass) | canonical review | **unreviewed** (endpoints now draft) |
| conn.000156 (metre value) | canonical review | canonical review — unchanged |

## NFR metrics (§18)

Performance/reliability requirements: **none in this slice** → no metric/threshold
records exist. Explicitly NOT_APPLICABLE rather than invented.
(Gate runtime anecdote ~3–8 s locally is observation, not a requirement. The
clean-clone measurement recorded 4.00 s over 21 steps — still an observation.)

## Gate 6 checklist (§31)

- [x] every applicable requirement has a verification method (no permanent NOT_YET_DETERMINED)
- [x] verification status recorded (21 VERIFIED · 0 FAILED · 3 UNVERIFIED as of 2026-10-01)
- [x] unverified explicitly marked
- [x] objective evidence referenced for as-built observations
- [x] VERIFIED records carry an execution date, named evidence, and a recorded result
- [x] FAILED records carry the specific unmet criterion and a routed open question
- [x] no round-1 FAILED record is left unrepaired: both were ruled on, fixed, and re-verified
- [x] round-2 FAILED (GATE-003) was repaired by the owner and re-verified: 7 required checks, byte-exact context match (UNRES-GATE-001 closed)
- [x] round-3 FAILED (HITL-001, HITL-002) repaired after the owner's ruling on UNRES-STEMMA-HITL-002 (scope = all data, 6 demoted, validator validates everything); both re-verified with mutation controls
- [x] no FAILED record remains outstanding in this slice

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
| 2026-10-01 | REQ-STEMMA-GATE-003 | INSPECTION | PASS (**re-verified after owner repair**) | EVID-GATE-018 |
| 2026-10-01 | REQ-STEMMA-EXP-003 | INTEGRATION_TEST | PASS (**executed: mutation + regeneration controls**) | EVID-EXP-014, EVID-EXP-015, EVID-EXP-016 |
| 2026-10-01 | REQ-STEMMA-HITL-001 | INTEGRATION_TEST | **FAIL** (AC1 vacuous, AC2 violated 6/9) | EVID-HITL-003, EVID-HITL-004 |
| 2026-10-01 | REQ-STEMMA-HITL-002 | INTEGRATION_TEST | **FAIL** (check correct, zero `candidate_edited` events) | EVID-HITL-005 |
| 2026-10-01 | REQ-STEMMA-SEC-002 | INSPECTION | PASS (**6245 objects scanned, zero keys; non-vacuous via plant**) | EVID-SEC-004, EVID-SEC-005 |
| 2026-10-01 | REQ-STEMMA-EXP-004 | INTEGRATION_TEST | PASS (**owner confirmed AC2; UNRES-EXP-001 closed**) | EVID-EXP-017 |
| 2026-10-01 | REQ-STEMMA-HITL-001 | INTEGRATION_TEST | PASS (**re-verified after owner-ruled repair**) | EVID-HITL-006, EVID-HITL-007, EVID-HITL-008 |
| 2026-10-01 | REQ-STEMMA-HITL-002 | INTEGRATION_TEST | PASS (**re-verified after owner-ruled repair**) | EVID-HITL-006, EVID-HITL-007, EVID-HITL-008 |
| 2026-10-01 | REQ-STEMMA-INTEG-001 | INTEGRATION_TEST | **PASS** (AC3 chat implemented; 35 checks, 2 sabotages caught) | EVID-INTEG-005, EVID-INTEG-006, EVID-INTEG-007, EVID-INTEG-008 |
| 2026-10-01 | REQ-STEMMA-OPS-003 | INSPECTION | PASS | EVID-OPS-009 |

## Method notes (recorded, not hidden)

- **Mutation discipline.** Every PASS above that validates a *guard* was paired
  with a negative control: inject the violation and confirm the guard fails. A
  green run is only informative if the check can go red (EVID-GATE-012).
- **GATE-001 scope.** The negative-path execution proves the chain's own failure
  semantics — exit propagation, step naming, termination. It does **not** prove
  that each of the 17 real steps fails correctly under its own failure modes.
- **OPS-002 is deliberately left UNVERIFIED.** Every single-source mechanism
  exists (EVID-OPS-008), and the owner ruled that a documented per-release audit
  is the measurement instrument with `v3.0.0` as its first data point, but the
  criterion is a *trend across releases*. Marking it VERIFIED would be claiming
  a trend from one observation. (`REQ-STEMMA-EXP-004` and `REQ-STEMMA-INTEG-001`,
  the other two UNVERIFIED requirements, were both resolved this round — see the
  owner rulings in `spec/UNVERIFIED-DECISIONS.md`.)
