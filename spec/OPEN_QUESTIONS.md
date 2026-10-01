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
- **Update (2026-10-01, verification of HITL-001/002):** this is no longer only an integrity-portability concern — it is the reason the HITL gate cannot be verified at all. `hitl_check.py --check-workflow` (the chain's own invocation) audits an empty, git-ignored `workflow/` and exits 0 with "nothing to check" (EVID-STEMMA-HITL-003). See the new **UNRES-STEMMA-HITL-002** below; the two are entangled, because resolving either without the other still leaves HITL unverifiable on a fresh clone.

## UNRES-STEMMA-HITL-002 — HITL enforcement is vacuous in CI and violated in the corpus

- **Question:** How should human review be enforced, given that the gate that is supposed to enforce it has nothing to inspect, and the corpus contradicts the requirement? Specifically: (a) should the chain run `hitl_check` in a mode covering `content/`, not only `workflow/`? (b) what happens to the 6 canonical entities that declare an **LLM** writer? (c) should the `content/` human-reviewer rule exist at the validator layer at all?
- **Why raised:** During verification of REQ-STEMMA-HITL-001/002 (2026-10-01, EVID-STEMMA-HITL-003/004/005). The chain step at `scripts/verify_all.py:31` runs `hitl_check.py --check-workflow`, which reports 0 candidates / 0 proposals / 0 human edits and exits 0 — it audits a git-ignored directory (`.gitignore:10`; `git ls-files workflow/` = 0 tracked files). **AC1 is present but vacuous.** AC2 is then **violated as stated**: 6 of 9 entities are `status=canonical` while `provenance.writer=llm:coding-agent.001` (conservation-energy, force, length, mass, newtons-second-law, time); only `stemma:phys.metre` is human-written. `hitl_check.py --all` independently returns **exit 1** with `9/9 entities fail HITL`.
- **Impact:** The requirement's central claim — "AI-drafted content SHALL remain draft until a named human reviews it" — is currently backed by **no gate that runs in CI over `content/`**. `validate.py`'s human-reviewer rule (`check_connection_agents`, rejecting a non-`human:` reviewer) applies only to `connections/`, never to `content/` entities, so nothing prevents an LLM-written entity from reaching `canonical`. REQ-STEMMA-HITL-002's `candidate_edited` requirement is correctly implemented in the checker but is never exercised, because the trail holds zero such events.
- **Relationship to the GATE-003 defect:** structurally similar but not identical. GATE-003 was a real gate not wired into the merge gate. Here the check is present *and correct* but scoped to an empty directory, so a green result carries no information — a check that cannot fail is not a weaker check, it is a different thing wearing the same name.
- **Blocking?** YES (blocks REQ-STEMMA-HITL-001 and REQ-STEMMA-HITL-002). · **Owner / Authority required:** Sajan / SOLE_OWNER.
- **Status:** ✅ **CLOSED (2026-10-01, owner ruling).** The owner ruled on all three parts, and the executor carried out the ruling:
  1. **Scope = all data.** *"HITL scope is all data, not only connection, its content and everything all entity."* The chain now runs `hitl_check.py --all` over `content/` + `connections/` (`scripts/verify_all.py` step 8); the vacuous `--check-workflow` invocation is gone. The migration-plan concern is resolved because the corpus was brought into compliance first (part 2).
  2. **Demote the six.** *"demote 6 llm written canonical entities."* The 6 entities were demoted to `draft` and their unsupported `reviewer`/`reviewed_at` claims removed. Corpus: **1 canonical / 8 drafts**. `conn.000157` (canonical, LLM-asserted, two draft endpoints) was demoted to `unreviewed`.
  3. **Validate everything.** *"validator validates the work given it is to validate … they must validate everything."* `validate.py` gained a content-layer human-writer+reviewer rule (`check_entity_agents`) and canonical-endpoint coupling for connections.
  - **Evidence:** EVID-STEMMA-HITL-006 (execution), EVID-STEMMA-HITL-007 (mutation controls — every gate provably red on the targeted defect, green on restore), EVID-STEMMA-HITL-008 (the validator endpoint defect + fix). All gates re-run green: `verify_all.py` exit 0, `docs.py check` PASS, 289 pytest tests pass. Both requirements flipped **FAILED → VERIFIED**.
  - **Residual:** **UNRES-STEMMA-HITL-001** (audit-trail portability) remains OPEN and independent — it is about the *evidence form* on a fresh clone, not about the behavior now enforced.

## UNRES-STEMMA-EXP-001 — Empty `learninghub` consumer export in all-draft corpus

- **Question:** Is an empty `learninghub` export (0 entities, because review_policy=canonical and corpus is all-draft) the intended consumer-facing behavior during early curation, including messaging toward consumers?
- **Why unresolved:** Docs assert it is "correct per review_policy" (EVID-STEMMA-EXP-007, CLAIM/LOW) — not owner-confirmed.
- **Impact:** Consumers subscribing now receive an empty canonical product; could surprise integrators.
- **Blocking?** NO. · **Owner / Authority required:** Sajan / REPOSITORY_LOCAL.
- **Status:** OPEN · **Next action:** confirm intent; if intended, document policy in CONSUMERS.md as authoritative once approved.
- **Update (2026-10-01, verification of EXP-004):** the premise has **moved**. The question was raised when the corpus was all-draft and the learninghub export was consequently empty. The corpus is now **1 canonical / 8 drafts** (after the HITL ruling demoted the 6 LLM-written entities), and the learninghub export contains that **1 canonical entity with all 8 drafts excluded** — verified by building the bundle under every policy (`all` → 9 entities incl. all drafts; `reviewed`/`trusted`/`canonical` → 1, `{canonical}` only; EVID-STEMMA-EXP-017). So this is no longer a question about an *empty* export (although a canonical-only export over a 1-entity corpus is nearly so) but about whether a **canonical-only** export is the intended consumer contract. The verification of EXP-004 AC1 does not depend on the answer; AC2 does, which is why EXP-004 stays UNVERIFIED until the owner rules.

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
- **Blocking?** YES (blocked GATE-003). · **Owner / Authority required:** Sajan / SOLE_OWNER.
- **Status:** ✅ **CLOSED (2026-10-01) — the owner added both required status checks.** Re-verified the same day (EVID-STEMMA-GATE-018).
  - **Verification method matters:** the authoritative source is the **effective rules** endpoint — `gh api repos/…/rules/branches/main` — *not* the legacy `branches/main/protection` endpoint. The legacy endpoint does **not** reflect ruleset-based rules and still returned the stale five-check list after the change; relying on it would have produced a false FAIL (or, earlier, a false PASS). This endpoint divergence is recorded as the generalisable lesson.
  - The active ruleset now requires **7** checks: the original five plus `Full Test Suite (pytest)` and `All Checks Green — Nothing Bad Gets Merged`, with `strict_required_status_checks_policy: true`.
  - Each required context string was compared **byte-for-byte** against the CI job names reported by live run `36316235760` — both match exactly, including the em-dash in `All Checks Green — Nothing Bad Gets Merged`. A near-miss would have left the check present-but-never-binding, which is the same defect wearing a green tick.
  - Ruleset inventory: `main` (id `22215824`, `active`, `refs/heads/main`) carries the checks; `BRANCHES` (id `22216058`, `disabled`, `~ALL`) is inert. Nuance recorded, not treated as a defect: `do_not_enforce_on_create: true` exempts only the branch's initial creation.
  - **REQ-STEMMA-GATE-003 re-verified: FAILED → VERIFIED.** The underlying failure path was already fail-closed (`verify_all.py` exits non-zero and terminates the chain), so this repair closed the *gating* gap without changing detection logic.

## UNRES-STEMMA-CORE-003 — Canonical is time-relative: revalidation debt + evolving validation methods

- **Question:** An entity may be legitimately canonicalized *before* the corpus is large enough for meaningful connections, but once more entities exist that *should* connect to it, it owes those connections and must be re-validated. How is this **"canonical now, revalidation owed later"** debt modelled — and how do the validation **methods** themselves evolve as the corpus grows from tens to millions/billions of entities?
- **Context (owner observation, 2026-10-01):** *"the canonicalized entity can be upgraded specially in connection because in early entity addition, there might not be enough entity to have connection information but as entity gets added to millions to billions, all entities must get updated, and they must be validated as well by the validator, that means validating towards end or when entities becomes more is more difficult and methods will evolve as well along the way."*
  The live corpus already shows the seed of the problem: `conn.000157` (force → mass) was canonical-worthy only while both endpoints were canonical; when the HITL ruling (`UNRES-STEMMA-HITL-002`) demoted the endpoints, the connection had to follow. Nothing in the protocol expressed that dependency as a *debt* — it was caught only because a validator rule happened to exist.
- **Why it matters (two directions):**
  1. **Staleness:** an early canonical entity can silently become connection-incomplete as the graph grows around it, and **no gate notices**.
  2. **Non-executability at scale:** validation methods calibrated for a 9-entity corpus (exhaustive, per-entity, whole-corpus re-run inside `verify_all`) cannot run over 10⁶–10⁹ entities at acceptable cost — so the gate that currently carries the entire trust claim **stops being executable**. A spec whose gate cannot run is not enforcing its requirement.
- **Impact:** Blocks any defensible claim that **L4 (verified) stays verified as the corpus grows** — i.e. it is a precondition for **L5 (enforced)** and for every corpus-scale claim. It does not invalidate the current L4 result at 9 entities; it says that result is *conditional on corpus size*.
- **Blocking?** YES. · **Owner / Authority required:** Sajan / SOLE_OWNER.
- **Decisions already taken in principle (owner, 2026-10-01):**
  1. **Revalidation debt, not auto-demote.** Canonical records the corpus state at approval; new relevant entities accrue explicit **"revalidation owed"** debt; the entity stays canonical but **flagged**; debt must be cleared — or explicitly owner-deferred with a recorded reason — before the next baseline. *Rejected:* auto-demote-on-new-entity (one new entity must not cascade into thousands of demotions).
  2. **Tiered methods, ADR-governed boundaries.** Validation methods tier by corpus size (exhaustive below a threshold → sampled + statistical confidence → locality/graph-consistency), and the **tier thresholds/definitions are themselves fixed by ADR** so they cannot drift silently.
  3. **Upgrade path required.** An entity canonicalized with no connections must have a defined route to *gain* connections and be re-validated **without** being demoted and re-created — an additive, supersede-don't-edit-compatible promotion of connection-completeness, with the new connections themselves HITL-reviewed.
- **Still undecided (what the owner must rule on before implementation):**
  - **Debt data model** — where debt lives: entity frontmatter, a derived index, or a review-queue record.
  - **The "should connect" predicate** — how candidate connections are generated at scale (this is the hard part; naive all-pairs is *O(N²)*).
  - **Numeric tier thresholds** — the corpus sizes at which each method tier takes over.
  - **What "connection-complete" means** — a per-entity boolean, a coverage ratio, or a graph-level invariant.
  - **Interaction with supersede-don't-edit** — a debt-clearing edit is additive, but is it a new revision?
- **Status:** OPEN · **Next action:** owner rules on the "still undecided" items. **No implementation before the ruling** — this touches the *meaning* of `canonical`, which is a governance act reserved to the owner (`spec/ROLES_AND_AUTHORITY.md`, Constraint D).
