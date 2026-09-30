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
