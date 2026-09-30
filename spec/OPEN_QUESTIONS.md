# OPEN QUESTIONS — UNRES records

`UNRES-` records are maintained in this file (protocol §11).
Do not silently close: `RESOLVED` requires the designated authority or an
authoritative external source. Machine copy: `spec/machine-readable/` conflicts
+ these records are mirrored in `requirements.yaml`-adjacent tooling only as IDs.

---

## UNRES-STEMMA-CORE-001 — Organization / IRI base for published IRIs — **RESOLVED (published-PID portion closed 2026-10-01)**

- **Question:** Which owning organization, domain, and IRI base will STEMMA use for published IRIs?
- **Resolved portion (binding, by Sajan):** publisher of record = individual Sajan; canonical identity = immutable `stemma:` URN identifiers (machine-enforced; resolution never enters canonical files). (ADR-0053 + Amendment 0001, 2026-09-22)
- **OPEN portion:** published-PID domain and resolution architecture (w3id.org was proposed, then deliberately re-evaluated via slow research: docs/PERSISTENT-IDENTIFIER-BRIEF.md). **Deferred to the R6 projection-publication stage**, per Amendment 0001 — the research establishes this is safely deferrable while pre-publication (nothing embeds resolvable stemma URIs yet).
- **CLOSED (published-PID portion, 2026-10-01):** owner ruled at R6 as Amendment 0001 directed — **`stemma-urn-only`**: STEMMA publishes under its own `stemma:` URNs with no external resolution base for now (`docs/decisions/r6-identifier-base.md`, `decided_by human:curator.001`). Reason: corpus/review maturity not yet sufficient for a public PID promise (single curator + AI; AI-assisted verification a planned next step). w3id remains the recorded *intended* base, to be adopted when that record's §6 conditions are met (one-line `@context` change, no canonical or consumer change). `publication_gate.py` flipped BLOCKED → OPEN. No owner infrastructure action required meanwhile.
- **Noted consequence:** FAIR F1/A1 resolvability is deliberately not satisfied for now; recorded openly, not hidden.
- **Status trail:** OPEN → CLOSED (ADR-0053, quick ruling 2026-09-22) → RE-OPENED/DEFERRED (Amendment 0001, same date, owner-directed slow research) → CLOSED at R6 as *decided to defer* (2026-10-01, stemma-urn-only; see r6-identifier-base.md).
- **Blocking?** NO — non-blocking; never blocked R4; decision recorded at R6 as scheduled.
- **Explicit non-actions:** no namespace claimed (w3id or otherwise) — claiming later as squatting insurance is a recorded *option*, not a decision; no canonical identifier changes; no resolution infrastructure.
- **Owner / Authority required:** Sajan / HUMAN_DECISION.
- **Status:** RESOLVED (published-PID portion — decided to defer with bounded upgrade conditions) · **Next action:** none required now; revisit when the §6 conditions in r6-identifier-base.md are met.

## UNRES-STEMMA-SCH-001 — Validation is graph/object-scoped; dataset-scoped validation is the 2026 frontier

- **Question:** Should STEMMA add a *dataset-scoped*, declaratively self-contained validation layer for the export (validating `entities[]` + `connections[]` + sidecars together), rather than only the current per-object JSON Schema checks and registry coherence?
- **Why unresolved:** STEMMA validates each canonical object against its schema in the gate (REQ-STEMMA-SCH-001) plus registry coherence (REQ-STEMMA-SCH-003), and guarantees the export by generator + freshness gate (REQ-STEMMA-EXP-001/-003). The 2026 validation frontier has moved to dataset scope: SHACL-DS (Chiem Dao & Debruyne, ESWC 2026) exists precisely because graph-scoped SHACL "loses track of where triples come from," and the W3C SHACL-UCR work treats dataset validation as an open requirement. STEMMA's export is effectively a dataset.
- **Known facts:** No dataset-level declarative constraint layer exists today; correctness of the export relies on the generator being correct plus the freshness diff. This is believed adequate now but is the part of the spec most likely to feel dated.
- **Impact:** Low now; grows with consumer count and export complexity. A consumer reasoning over cross-entity constraints (inverse mirrors, domain/range across the projected edges) can only trust producer behavior, not a declared contract.
- **Blocking?** NO — explicitly ruled non-blocking by owner 2026-10-01; **no requirement added at this time** (SOTA-COMPARISON-2026-10-01 F4).
- **Owner / Authority required:** Sajan (SOLE_OWNER) / HUMAN_DECISION.
- **Status:** OPEN (noted, not actioned) · **Next action:** revisit when the export gains a second real consumer or when SHACL-DS-style tooling matures enough to adopt without new infrastructure.

## UNRES-STEMMA-HITL-001 — HITL audit evidence is not repository-resident

- **Question:** Should the HITL audit trail (`workflow/audit/`, proving human edits before canonical) be committed (possibly redacted) so canonical trust can be verified from the repo alone?
- **Why unresolved:** Today the gate passes by reading git-ignored local files (EVID-STEMMA-HITL-001, EVID-STEMMA-CORE-004). A fresh clone cannot verify HITL for `metre`.
- **Known facts:** Gate reads the trail; corpus declares `writer: human:curator.001` (EVID-STEMMA-HITL-002).
- **Impact:** Trust asymmetry between the operator's machine and any other clone; weakens "HITL enforced" claim portability.
- **Blocking?** NO (behavior consistent), but HIGH integrity relevance.
- **Owner / Authority required:** Sajan (SOLE_OWNER) / REPOSITORY_LOCAL.
- **Status:** OPEN · **Next action:** decide committed-audit vs provenance-summary pattern; ADR.

## UNRES-STEMMA-EXP-001 — Empty `learninghub` consumer export in all-draft corpus

- **Question:** Is an empty `learninghub` export (0 entities, because review_policy=canonical and corpus is all-draft) the intended consumer-facing behavior during early curation, including messaging toward consumers?
- **Why unresolved:** Docs assert it is "correct per review_policy" (EVID-STEMMA-EXP-007, CLAIM/LOW) — not owner-confirmed.
- **Impact:** Consumers subscribing now receive an empty canonical product; could surprise integrators.
- **Blocking?** NO. · **Owner / Authority required:** Sajan / REPOSITORY_LOCAL.
- **Status:** OPEN · **Next action:** confirm intent; if intended, document policy in CONSUMERS.md as authoritative once approved.

## UNRES-STEMMA-INTEG-001 — Cross-repo consumer interface ownership unassigned

- **Question:** Who owns the consumer-side contract for LearningHub and PROFESSOR-J (schema evolution, compatibility expectations, change coordination)?
- **Why unresolved:** Consumers are named in registry/docs (EVID-STEMMA-INTEG-002) but no counterpart owner exists; STEMMA side is Sajan.
- **Impact:** Breaking-change coordination has no counterparty; contract discipline may be one-sided fiction.
- **Blocking?** NO for pilot; YES before real consumer integration.
- **Authority required:** CROSS_REPOSITORY / HUMAN_DECISION.
- **Status:** OPEN · **Next action:** assign owner per consumer or mark consumers "prospective".

## UNRES-STEMMA-RAG-001 — Deterministic-fake embeddings as shipped reference

- **Question:** Is the deterministic hash-based embedding fallback (labeled with a real model name + `type: faiss` in meta.json) acceptable as the shipped reference implementation behavior, or must CI require a real model for the reference path?
- **Why unresolved:** Behavior exists (EVID-STEMMA-EXP-004/-005); acceptability is a product/spec decision; mislabeled type recorded as CONFLICT-STEMMA-EXP-001.
- **Blocking?** NO. · **Owner / Authority required:** Sajan / REPOSITORY_LOCAL.
- **Status:** OPEN · **Next action:** decide policy; either document as sanctioned demo behavior or gate on real model presence.

## UNRES-STEMMA-OPS-001 — Rights review for textbook-derived extraction

- **Question:** What is the licensing position for definition text extracted from commercial textbooks (HRW, Campbell, CLRS, Atkins, Carroll) during ingestion, and what evidence may be retained/committed (e.g., verbatim excerpts in HITL trail)?
- **Why unresolved:** XC-3 sweep: PDFs intentionally stay out of git; retention rules for excerpts/metadata undecided.
- **Impact:** Legal/compliance boundary for R4 content growth and for UNRES-STEMMA-HITL-001's committed-audit option.
- **Blocking?** YES for committing any audit material containing textbook excerpts.
- **Owner / Authority required:** Sajan (+ external legal if needed) / HUMAN_DECISION.
- **Status:** OPEN · **Next action:** owner policy (e.g., standards-text-first sources, excerpt-free audit metadata).

## UNRES-STEMMA-CORE-002 — Generality guard misses prefixed scoping keys

- **Question:** Should `test_generality.py`'s `SCOPING_FIELDS` pattern drop its `^…$` anchors so it also rejects prefixed/suffixed scoping keys (`grade_level`, `grade_band`, `curriculum_scope`, `target_grade`)?
- **Why raised:** During verification of REQ-STEMMA-CORE-004 (2026-10-01, EVID-STEMMA-CORE-006/007). The guard was `^…$`-anchored and so matched only exact key names. A mutation probe injecting `grade_level: 10` into `metre.md` frontmatter was **not** rejected by the guard.
- **Impact:** **Defence-in-depth only, not an open hole.** `concept.schema.json` declares `additionalProperties: false`, so `validate.py` still rejected an unregistered scoping key (exit 1, observed). The `extensions` seam (ADR-0017) is likewise registry-gated. No violation could ship — the guard was simply not the layer that catches prefixed keys. Left unfixed, the guard's stated invariant over-claimed relative to its implementation.
- **Blocking?** NO. · **Owner / Authority required:** Sajan / SOLE_OWNER.
- **Status:** ✅ **CLOSED (2026-10-01) — owner chose option (c): widen, then mutation-test.** Implemented the same day.
  - `SCOPING_FIELDS` (the anchored regex) was replaced by a **token-based matcher**: `_scoping_tokens` splits an identifier on separators/camelCase/digits; `_joined_token_forms` restores contiguous n-grams so multi-word names (`key_stage`, `learning_objectives`) match in either spelling; `_is_scoping_field` matches **whole tokens**, never substrings, so `upgrade_notes`/`multigrade` stay legitimate. `level` is special-cased: only an education-qualified level (`edu_level`, `grade_level`) is a scoping claim — `trophic_level`, `energy_level`, `sea_level` are not.
  - The guard now catches **28** formerly-missed variants.
  - Three new tests: `test_scoping_field_guard_catches_prefixed_variants`, `test_scoping_field_guard_does_not_overreach` (negative control), and `test_widened_guard_is_enforced_end_to_end`.
  - **Non-vacuity proven by mutation:** reverting the matcher to the anchored form turns exactly those tests red (2 failed, 6 passed); restoring gives 8 passed (EVID-STEMMA-CORE-010).
  - **REQ-STEMMA-CORE-004 re-verified: FAILED → VERIFIED.**

## UNRES-STEMMA-GATE-001 — The all-green merge gate is not a required status check

- **Question:** Should `Full Test Suite (pytest)` and `All Checks Green — Nothing Bad Gets Merged` be added to the repository's required status checks on `main`, so that a red suite actually blocks a merge?
- **Why raised:** During verification of REQ-STEMMA-GATE-003 (2026-10-01, EVID-STEMMA-GATE-016/017). Both **named** acceptance criteria PASS — `ci.yml` defines the `test-suite` job running `python3 -m pytest tests/ -q`, and `all-green` both lists it in `needs` *and* asserts its result `== success` → `exit 1`; live run `36316235760` shows both green.
- **Impact:** **The merge-gating clause is unenforced.** The requirement's statement is that the all-green gate SHALL **require** the suite's success. The live repository configuration (branch protection *and* active ruleset `22215824`) requires only `Validate Knowledge Base`, `Security scan`, `Verify Governance Docs`, `Branching Strategy`, `Conventional Commits (commitlint)`. Neither the pytest job nor `all-green` is required — **a PR with a failing test suite, or a failing all-green, can still be merged.**
- **Why it hid until now:** branch protection is a **repository setting, not in-repo config**. Inspecting only `.github/workflows/ci.yml` yields a false PASS, because every job is correctly defined and correctly wired. This is exactly why the criterion names the *merge gate* rather than the *job*.
- **Blocking?** YES (blocks GATE-003). · **Owner / Authority required:** Sajan / SOLE_OWNER.
- **Status:** OPEN · **Next action:** owner adds both contexts to the required status checks for `main` in repository settings, then `REQ-STEMMA-GATE-003` is re-verified by inspecting the required-check list. Adding `all-green` alone is sufficient once it is the single aggregate gate (it already asserts every other job's result); adding the pytest job too keeps the failing cause legible. The executor did **not** change branch protection — that is a governance act, not a code change.
