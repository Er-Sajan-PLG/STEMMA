# The eight `UNRES` records — owner decision sheet

Prepared: 2026-10-01 · For: Sajan (`human:curator.001`, SOLE_OWNER)
Status: **EXECUTED 2026-10-01.** The owner accepted every recommendation below and the executor carried them out. Registry now **9 CLOSED · 1 DEFERRED · 1 OPEN** of 11.

> **RULED AND EXECUTED 2026-10-01 (second pass).** Each section's `> **RULED:**` line records the outcome. Outcomes: §1 `CORE-001` → **CLOSED** (registry ratified to match the prose). §2 `HITL-001` → **CLOSED** option (c), hash-only provenance manifest. §3 `OPS-001` → **CLOSED** option (b), excerpt-free metadata only (XC-3 amendment). §4 `INTEG-001` → **CLOSED** option (a), external consumers marked `prospective`. §5 `RAG-001` → **CLOSED** option (a), fallback sanctioned + label fixed. §6 `SCH-001` → **DEFERRED**, its already-ruled state stated precisely. §7 `CORE-003` → **left OPEN by owner directive** (active research; no action).
>
> Executed under Constraint D: the owner ruled; the executor implemented and recorded. The executor did not itself approve, reject, or close any record.

This sheet exists for the same reason as `spec/UNVERIFIED-DECISIONS.md`: these
records are not waiting on verification work. Each is waiting on something only
the owner can supply — a ruling, a policy, or a designation — or is a
bookkeeping divergence the executor is not permitted to close.

Executor executed under Constraint D (`spec/ROLES_AND_AUTHORITY.md` §79–88): the
executor may *execute* work and *record* results, but may **not** approve, reject,
or defer a requirement, **close any `UNRES-` record**, or convert an `INFERENCE`
to a `FACT` without owner review. **Nothing in this sheet changes a status.**

---

## Summary — eight records, four different situations

| # | Record | Ruled | Outcome |
|---|--------|-------|---------|
| 1 | `UNRES-STEMMA-CORE-001` | (a) ratify closure | **CLOSED** — registry synced to the prose |
| 2 | `UNRES-STEMMA-HITL-001` | (c) hash-only manifest | **CLOSED** — `scripts/review_manifest.py`, gate-enforced |
| 3 | `UNRES-STEMMA-OPS-001` | (b) excerpt-free metadata | **CLOSED** — XC-3 amendment |
| 4 | `UNRES-STEMMA-INTEG-001` | (a) consumers prospective | **CLOSED** — registry v1.1.0 `maturity` field |
| 5 | `UNRES-STEMMA-RAG-001` | (a) sanction + fix label | **CLOSED** — fallback sanctioned, `type` fixed |
| 6 | `UNRES-STEMMA-SCH-001` | (b) reclassify | **DEFERRED** — already ruled "not now" |
| 7 | `UNRES-STEMMA-CORE-003` | no action | **OPEN** — owner research in progress, by directive |

Registry after: **9 CLOSED · 1 DEFERRED · 1 OPEN** of 11.

**Note on the count.** The registry holds **7** `OPEN` records and **4** `CLOSED`.
The "8" in circulation counts 7 open records plus the extra `UNRES-` identifier
tracked in the registry — `UNRES-STEMMA-CORE-001`, which is `OPEN` in the registry
while the prose already records it `RESOLVED`. That divergence is item 1 below and
is why the sheet covers eight identifiers while only seven are genuinely open.
There is no separate eighth question.

---

## 1. `UNRES-STEMMA-CORE-001` — IRI base · **DIVERGENCE, not an open question**

**Registry says:** `status: OPEN`.
**Prose says:** `## UNRES-STEMMA-CORE-001 … — **RESOLVED (published-PID portion closed 2026-10-01)**`.

The prose records a genuine, dated, owner-attributed decision:

- Publisher of record = individual Sajan; canonical identity = immutable `stemma:`
  URNs (binding, ADR-0053 + Amendment 0001).
- The published-PID portion was **deferred to R6**, then **closed at R6** as
  `stemma-urn-only` (`docs/decisions/r6-identifier-base.md`, `decided_by:
  human:curator.001`).
- `publication_gate.py` flipped **BLOCKED → OPEN**.
- Status trail: OPEN → CLOSED → RE-OPENED/DEFERRED → **CLOSED at R6**.

The **only** thing out of step is the machine registry, which was never updated
when the decision was taken. There is no live question here; there is a stale row.

**Options**

- **(a) Ratify closure — close the registry record to match the prose.** *(recommended)*
  Sets `status: CLOSED` with `disposition`, `resolution`, `closed_date:
  2026-10-01`, `closed_by: human:curator.001`, mirroring the `EXP-001` closure.
  Registry and prose agree; open count drops to 6.
- **(b) Re-open the prose question.** Reverses a recorded owner decision — only
  correct if the `stemma-urn-only` ruling is itself being withdrawn.
- **(c) Leave both as-is.** The divergence persists; the next reader cannot tell
  which document is authoritative.

> **RULED: (a) — RATIFY CLOSURE (2026-10-01). EXECUTED.** `UNRES-STEMMA-CORE-001` set to `CLOSED` with `disposition`, `resolution`, `closed_date: 2026-10-01`, `closed_by: human:curator.001`, mirroring the `EXP-001` closure. The registry had read `OPEN` only because it was never synced when the R6 ruling was taken — this was a bookkeeping divergence, not a live question. Registry and prose now agree. Open count drops to 6.

---

## 2. `UNRES-STEMMA-HITL-001` — HITL audit evidence not repository-resident · **OPEN, BLOCKING**

**Question:** Should the HITL audit trail (`workflow/audit/`, proving human edits
before canonical) be committed (possibly redacted) so canonical trust can be
verified from the repo alone?

**Why it now matters more than when it was filed.** The original framing was
"integrity-portability": the operator's machine could verify HITL, a fresh clone
could not. The 2026-10-01 verification of `REQ-STEMMA-HITL-001/002` changed its
character — `hitl_check.py --check-workflow` audits an empty, git-ignored
`workflow/` and exits 0 with *"nothing to check"* (EVID-STEMMA-HITL-003). So the
concern is no longer only portability: the record is entangled with the
**evidence form** that the HITL gate depends on.

**What has already changed.** The ruling on `UNRES-STEMMA-HITL-002` moved the
chain's invocation to `hitl_check.py --all` over `content/` + `connections/`, so
the gate no longer reads the empty directory. That closes the *behavior* half.
This record is the residue: what evidence form should exist, and where.

**Impact:** trust asymmetry between the operator's machine and any other clone;
the phrase "HITL enforced" currently means "enforced where the local trail is
present". **Blocking?** YES for `REQ-STEMMA-HITL-001`.

**Note the interaction with item 3:** committing audit material may pull
textbook excerpts into git, which is exactly what `UNRES-STEMMA-OPS-001` governs.
These two should be ruled together, not independently.

**Options**

- **(a) Commit a redacted audit trail + disclosure ADR.** Commit
  `workflow/audit/` under a redaction rule (no verbatim source excerpts, hashes
  and metadata only), so a fresh clone can verify HITL end to end. *This is the
  option that makes the trust claim portable* — and it is only safe once item 3's
  excerpt policy lands.
- **(b) Accept local-state provenance and record it explicitly.** Keep
  `workflow/` git-ignored; add an ADR stating that HITL evidence is
  operator-local by design, that the committed corpus carries the *declared*
  provenance (`writer`, `reviewer`, `reviewed_at`) as the portable record, and
  that fresh-clone verification of HITL is therefore **out of scope**. Cheap,
  honest, and narrows the trust claim rather than fixing it.
- **(c) Commit a signed provenance summary (no excerpts).** Emit a
  per-entity, hash-only review manifest (`entity id → {writer, reviewer, stage
  dates, evidence hash}`) into the repo at promotion time; never commit the raw
  trail. Middle path: portable, excerpt-free, and it satisfies item 3 by
  construction.
- **(d) Leave OPEN.** The gate is green today; the portability gap persists.

> **RULED: (c) — HASH-ONLY PROVENANCE MANIFEST (2026-10-01). EXECUTED.** `scripts/review_manifest.py` emits `spec/machine-readable/review_manifest.json`: per reviewed record, its id, kind, relpath, declared provenance, ordered `promotion_history`, and a `sha256` of the file — and no text of any kind. `verify_all.py` runs it then `--check`, so a post-review edit fails CI naming the record. 8 tests in `tests/repo/test_review_manifest.py` assert the excerpt-free property, the binding property, determinism, and that the generator reads canonical records only (sabotaging it to read `workflow/` turns 3 red). Ruled jointly with §3.

---

## 3. `UNRES-STEMMA-OPS-001` — Rights review for textbook-derived extraction · **OPEN, BLOCKING for any excerpt**

**Question:** What is the licensing position for definition text extracted from
commercial textbooks (HRW, Campbell, CLRS, Atkins, Carroll) during ingestion, and
what evidence may be retained/committed (e.g. verbatim excerpts in the HITL trail)?

**Why unresolved:** the XC-3 sweep decided PDFs stay out of git, but retention
rules for *excerpts* and *metadata* were never decided.

**Impact:** the legal/compliance boundary for R4 content growth, and for item 2's
committed-audit option. **Blocking?** YES for committing anything containing
textbook excerpts; not blocking the current corpus (which holds extracted
*definitions*, not verbatim passages).

**This is the only item on the sheet that may need a non-owner input** (legal
review). The executor cannot resolve it and should not guess.

**Options**

- **(a) Standards-first sources.** Restrict retained sources to openly-licensed
  or public-domain standards bodies and open textbooks; drop commercial
  textbook bodies from anything committed. Strongest position; may cost coverage.
- **(b) Excerpt-free metadata only.** Retain textbook *citations* (title, edition,
  chapter locator — already the pattern, e.g. `stemma:src.halliday-resnick-walker-12th`)
  and never commit verbatim passage text. Definitions are re-expressed, not copied.
  Compatible with item 2 option (c); likely the practical answer.
- **(c) Minimal-quotation + attribution policy.** Permit short verbatim excerpts
  under a documented fair-use/attribution rule, recorded as an XC amendment with
  the excerpt cap stated numerically.
- **(d) Record as accepted risk.** Owner documents that the pilot retains
  extracted definitions under an accepted-risk position, with a revisit trigger
  before any public release.

> **RULED: (b) — EXCERPT-FREE METADATA ONLY (2026-10-01). EXECUTED.** Recorded as the XC-3 amendment in `spec/EXTERNAL_CONSTRAINTS.md`: committable are citation metadata (`sources/*.yaml`) and re-expressed definitions in STEMMA's own voice; never committable are source PDFs, verbatim passages however short, and anything under `workflow/`. By reproducing nothing verbatim the project relies on no fair-use defence. Enforced structurally — `sources/*.yaml` carry no body-text field, and the §2 manifest is excerpt-free by construction. Ruled jointly with §2.

---

## 4. `UNRES-STEMMA-INTEG-001` — Cross-repo consumer interface ownership unassigned · **OPEN, non-blocking now**

**Question:** Who owns the consumer-side contract for LearningHub and PROFESSOR-J
(schema evolution, compatibility expectations, change coordination)?

**Why unresolved:** consumers are named in the registry and docs
(EVID-STEMMA-INTEG-002) but **no counterpart owner exists**; the STEMMA side is
Sajan. Breaking-change coordination therefore has no counterparty, and the
contract discipline may be one-sided fiction.

**Blocking?** NO for the pilot; **YES before real consumer integration.**

Note this is a *different* record from `REQ-STEMMA-INTEG-001` (the explorer +
grounded chat, now `VERIFIED`). Same numeric suffix, unrelated subject.

**Options**

- **(a) Mark all consumers "prospective."** Reclassify learninghub, professor-j,
  and the general consumer as prospective in `schema/consumer-registry.yaml`;
  the STEMMA side owes no compatibility promise until integration is real. Honest
  and cheap; removes a claim nobody can currently keep.
- **(b) Designate owners now.** Name a counterpart owner per consumer (even if it
  is Sajan wearing a second hat, recorded explicitly), so change coordination has
  a named endpoint.
- **(c) Defer to a post-pilot integration phase** with a recorded rationale and a
  revisit trigger (first real consumer pull), keeping the record OPEN.

> **RULED: (a) — MARK CONSUMERS PROSPECTIVE (2026-10-01). EXECUTED.** `schema/consumer-registry.yaml` v1.1.0 adds a `maturity` field (`prospective` for learninghub and professor-j; `concrete` for stemma-explorer and general) plus a `maturity_legend`. The one-sided-contract problem is removed by not claiming a contract with no counterparty. Consumer bundles regenerated and the full gate re-run to confirm export behaviour is unchanged.

---

## 5. `UNRES-STEMMA-RAG-001` — Deterministic-fake embeddings as shipped reference · **OPEN, non-blocking**

**Question:** Is the deterministic hash-based embedding fallback (labeled with a
real model name + `type: faiss` in `meta.json`) acceptable as the shipped
reference implementation behavior, or must CI require a real model for the
reference path?

**Why unresolved:** the behavior exists (EVID-STEMMA-EXP-003/004/005);
acceptability is a product/spec decision. The mislabeled `type: faiss` is
separately recorded as `CONFLICT-STEMMA-EXP-001` (still `OPEN`) — the environment
has no FAISS and stores plain `vectors.json`.

**Two distinct things are tangled here** and are worth separating when ruling:
1. **Determinism of the fallback** — is a hash-derived vector acceptable *as a
   reference behavior* when no model can be downloaded?
2. **Truthfulness of the metadata** — `meta.json` asserting `type: faiss` when the
   store is JSON. This one is arguably a defect independent of the policy call.

**Blocking?** NO. **Owner / Authority required:** Sajan / REPOSITORY_LOCAL.

**Options**

- **(a) Sanction it, and fix the label.** Declare the deterministic fallback
  sanctioned demo behavior for the pilot, **and** stop writing `type: faiss`
  unconditionally — write the actual store type. Resolves the policy question and
  the mislabel in one move. *(recommended — the label fix is correct under any
  policy)*
- **(b) Gate on a real model.** CI requires a genuine model for the reference
  path; the fallback becomes a test-only fixture. Higher fidelity, higher CI cost,
  and it conflicts with the pilot's offline constraint.
- **(c) Separate the two.** Rule the policy question (a or b) and treat the
  `type: faiss` mislabel as its own defect to fix regardless — which is what
  `CONFLICT-STEMMA-EXP-001` is already tracking.

> **RULED: (a) — SANCTION IT, AND FIX THE LABEL (2026-10-01). EXECUTED.** The hash fallback is declared sanctioned pilot behaviour: opt-in (`--placeholder`), self-labelling (`stemma:placeholder-hash`), and refused otherwise (`EmbeddingUnavailable`), so it can never be mistaken for a real embedding. The `type: faiss` mislabel was fixed independently — `scripts/embed.py` now records `numpy-flat`/`json-flat` — with a guard in `tests/repo/test_vector_store_type_truthfulness.py` and EVID-STEMMA-EXP-019.

---

## 6. `UNRES-STEMMA-SCH-001` — Dataset-scoped declarative validation · **OPEN, already ruled "not now"**

**Question:** Should the export gain a *dataset-scoped*, declaratively
self-contained validation layer (validating `entities[]` + `connections[]` +
sidecars together) beyond per-object JSON Schema?

**This one is effectively already decided.** The prose records an owner ruling on
2026-10-01: **non-blocking, and explicitly no requirement added at this time**
(SOTA-COMPARISON-2026-10-01 F4). What remains is a revisit trigger, not a
question.

**Impact:** low now; grows with consumer count. A consumer reasoning over
cross-entity constraints can currently trust producer behavior only, not a
declared contract.

**Options**

- **(a) Leave OPEN as a standing scope note.** Correct if you want it visible as a
  known frontier rather than a decided item. Revisit trigger: a second real
  consumer, or SHACL-DS-style tooling maturing.
- **(b) Reclassify `DEFERRED`.** The registry permits `DEFERRED`; the prose ruling
  ("not actioned") matches that status more precisely than `OPEN`. A deferred
  record is a *ruled* record; an open one invites re-litigation.
- **(c) Re-open as a requirement.** Add a `REQ-` for dataset-scoped validation.
  Not recommended at a 9-entity corpus with one real consumer.

> **RULED: (b) — RECLASSIFY `DEFERRED` (2026-10-01). EXECUTED.** The record was already ruled "not now" (SOTA F4); `DEFERRED` states that precisely and stops it inviting re-litigation. A `revisit_trigger` is recorded: a second real consumer, or dataset-scoped tooling maturing to adoption without new infrastructure.

---

## 7. `UNRES-STEMMA-CORE-003` — Canonical is time-relative; revalidation debt + evolving methods · **OPEN, owner-held research, NO ACTION**

**This is the record where "open" is the correct and intended state.** The owner
has ruled the parts that could be ruled, and is actively researching the rest.

**Already ruled and implemented (2026-10-01):**
- **PART 1 (debt model)** — debt lives in record frontmatter (`revalidation_debt`),
  visible to and enforced by the gate (ADR-0057, `REQ-STEMMA-HITL-003`,
  EVID-HITL-009/010). Canonical-with-debt is the chosen shape; **not**
  auto-demote-on-new-entity.
- **PART 3 (upgrade path)** — additive via the promotion chain; no demotion or
  re-creation.
- **Live instrument** — `ENF-STEMMA-HITL-002.pilot_scale_block {active:true,
  block_mode:full, relaxes_to:forward_only}`: at pilot scale the gate invalidates
  **any** reviewed record carrying outstanding debt, so the corpus size at which
  full blocking becomes a burden is **measured directly** rather than guessed.

**Still open, deliberately, with no target date — all four are owner
calculations, not executor tasks:**
- (a) the exact *should-connect* predicate (candidate generation at scale; naive
  all-pairs is *O(N²)*);
- (b) numeric PART 2 tier thresholds;
- (c) what "connection-complete" means (boolean vs coverage ratio vs graph
  invariant);
- (d) how debt clearance interacts with supersede-don't-edit — it is an
  **addition/revision**, so the schema stays flexible there.

**Owner reasoning, verbatim (2026-10-01):** *"should connect predicate is hard, i
cannot make decision now, i need to do some calculation before i make decision,
keep it open for now. also tier threshold also need some time before i make
decisions, these are real issues, connection in itself is hard question especially
when entity grows and needs completion criteria. It is one of the things i am
actively researching, keep it open as well. Debt clearing concept is just new for
now, and since connection in itself is hard to master, debt clearance is as well.
It is a revision really, addition, so schema also needs to be flexible here and it
also needs time. Every decision needs time."*

**Executor recommendation: take no action.** The record is tracked, not
scheduled, and it is explicitly *not* a prerequisite for L5 or corpus-scale
claims. The only thing the executor can do is keep it visible — and it already
is. Ruling it closed would destroy the record of open research; ruling it
`DEFERRED` could be argued, but the owner has said "keep it open."

> **RULED: NO ACTION — KEEP OPEN (2026-10-01).** The owner confirmed this is the one record where `OPEN` is the intended state. The four remaining items are owner calculations under active research; closing would destroy the record of open research and `DEFERRED` would misstate an active investigation as a shelved one. Annotated in the registry with the owner directive and an executor note that no work is scheduled.

---

## 8. What the executor can do without a ruling

Only one item has work the executor may perform **before** an owner decision,
because it requires no authority and is correct under every option:

- **§5, the `type: faiss` mislabel.** `meta.json` asserts `type: faiss` while
  `scripts/embed.py` writes plain `vectors.json` (`CONFLICT-STEMMA-EXP-001`,
  still `OPEN`). Writing the *actual* store type is correct whether the fallback
  is sanctioned (option a) or gated (option b). It is a truthfulness fix, not a
  policy choice.

Everything else waits on a ruling. **Per Constraint D the executor does not close
any `UNRES-` record, does not set `CLOSED`/`DEFERRED` on its own initiative, and
does not convert an `INFERENCE` to a `FACT`.**

---

## Decisions requested

| # | Record | Recommended option |
|---|--------|--------------------|
| 1 | `UNRES-STEMMA-CORE-001` | **(a)** ratify closure, sync registry to prose |
| 2 | `UNRES-STEMMA-HITL-001` | **(c)** hash-only provenance manifest (portable, excerpt-free) |
| 3 | `UNRES-STEMMA-OPS-001` | **(b)** excerpt-free metadata only (pair with item 2) |
| 4 | `UNRES-STEMMA-INTEG-001` | **(a)** mark consumers prospective |
| 5 | `UNRES-STEMMA-RAG-001` | **(a)** sanction fallback + fix the label |
| 6 | `UNRES-STEMMA-SCH-001` | **(b)** reclassify `DEFERRED` |
| 7 | `UNRES-STEMMA-CORE-003` | **no action** — keep open (owner research in progress) |
