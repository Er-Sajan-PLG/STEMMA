# STEMMA — SOTA Comparison (as of 2026-10-01)

**Purpose.** Before the owner approves the 22 requirements in the recovery pilot,
compare STEMMA's specification against the current state of the art: what major
repositories and software actually do, what the large platforms practice, and what
the 2025–2026 research literature says. Output: a requirement-level list of anything
**missing**, **wrong**, or **needing change**.

**Method.** Targeted searches restricted to the last 1–6 months (so everything here is
2026 material, not 2025). Each finding is mapped to a concrete STEMMA requirement or
document. Where STEMMA already matches SOTA, that is stated so the owner knows the
approval is not being asked for in the dark.

**Bottom line.** STEMMA's core architecture is **ahead of, or at parity with, published
practice** on the hard problems (canonical/derived separation, deterministic exports,
fail-closed gates, value-slot modelling, evidence classes). The gaps that genuinely
matter for approval are **not** in the knowledge model — they are in the **governance and
provenance-of-people layer**: how a single-maintainer, AI-heavy project survives, and how
the AI-assistance is recorded. Five findings need a change or a new requirement; three are
confirmations; two are open risks to accept knowingly.

---

## 1. Sources consulted (all 2026 unless noted)

| # | Source | Date | Why it matters here |
|---|--------|------|---------------------|
| S1 | Wikipedia RfC banning LLM-generated article content (passed 44–2) | 2026-03-20 | Hardest existing precedent for an AI-content ban in a community knowledge base |
| S2 | *The Lancet* correspondence, Topaz et al. (Columbia), audit of ~2.5M PubMed records | 2026-05-07 | Quantifies the fabricated-citation problem AI assistance creates |
| S3 | OBO Foundry Newsletter #10 — Principle 3 strengthened (PURLs MUST resolve term-centrically); Principle 8 requires `rdfs:isDefinedBy` provenance on re-identifying adopted terms; Standardization Guidelines incl. "Release Considerations" | 2026-04-13 | Closest governance peer to STEMMA's identifier + provenance policy |
| S4 | Chiem Dao & Debruyne, *From RDF Graph Validation to RDF Dataset Validation with SHACL-DS*, ESWC | 2026-05 | The validation-model frontier: SHACL is graph-scoped; datasets need more |
| S5 | Mohammadi (TNO/Sage), KG metadata specification + SHACL validation framework | 2026 | Shows no single vocabulary suffices; required elements must be SHACL-enforceable |
| S6 | Kim, *Comprehensive Editorial Protocols for Detecting AI-Generated Manuscripts*, Zenodo 10.5281/zenodo.19447994 (synthesises Elsevier/Nature/Springer/Wiley/Science/JAMA + COPE/ICMJE/WAME) | 2026-04-07 | The consensus statement on AI-content accountability and provenance metadata |
| S7 | Bus-factor / truck-factor body of work (Avelino et al. 133 projects; xz-utils CVE-2024-3094 post-mortems; Eghbal) surfaced through 2026 commentary | 2026 | The single-maintainer risk, measured and named |
| S8 | Zenodo DOI versioning: Concept DOI vs version-specific DOI; *Practical Primer on Software Citation* (arXiv:2609.28622) | 2026-09 | Confirms STEMMA's release-DOI plan |
| S9 | W3C SHACL Use Cases & Requirements (updated) | 2026-09 | Confirms dataset-level validation is an open, active concern |

---

## 2. How STEMMA compares — by theme

### 2.1 Canonical / derived separation — **STEMMA is at or ahead of SOTA**

Nothing in the 2026 literature shows a widely-adopted repository that formally separates
canonical (human-reviewed, immutable-ID) from derived (regenerable, deterministic) layers
with a fail-closed gate between them as cleanly as STEMMA's `REQ-STEMMA-CORE-001`,
`REQ-STEMMA-EXP-001`, and `REQ-STEMMA-EXP-003`. The OBO Foundry (S3) has a release process
but treats the ontology artefact itself as the thing; STEMMA's "canonical is not the
artefact, the export is" split is more explicit.

**Verdict:** approve as-is. This is a differentiator, not a gap.

### 2.2 Determinism and reproducibility — **parity with SOTA**

`REQ-STEMMA-EXP-001` (byte-identical regeneration, content-hash stamped, no wall clock)
matches the reproducible-builds.org definition and is stronger than what most public KGs
enforce. OBO's new "Release Considerations" (S3) gestures at release standards but does not
mandate byte-determinism. SHACL-DS (S4) is about *validating* datasets, not reproducing
them.

**Verdict:** approve as-is.

### 2.3 Validation model — **one forward-looking gap (Finding F4, below)**

STEMMA validates with JSON Schema inside the gate (`REQ-STEMMA-SCH-001`). The 2026
validation frontier has moved to **dataset-scoped, declaratively self-contained constraints**
— SHACL-DS (S4) and the SHACL-UCR work (S9) both exist precisely because graph-scoped
validation "collapses dataset structure or hides knowledge in code." STEMMA's export *is*
effectively a dataset (entities + connections + sidecars). This is not wrong today, but it
is the one place where the spec will feel dated within a year.

**Verdict:** approve, but record it. See Finding F4.

### 2.4 Identifier and deprecation policy — **STEMMA is ahead; one phrase to align**

STEMMA's `IDENTIFIER-POLICY.md` (never-delete, never-reuse, deprecate ≠ remove, merge, split,
meaning authority) is *more complete* than OBO Foundry's published position: S3 explicitly
shows the OBO Foundry has **no deprecation / obsoletion / tombstoning policy** — its
newsletter does not even mention those words. STEMMA already has all four in writing.

Where OBO is *ahead* is enforcement wording: OBO Principle 3 was **strengthened in 2026** to
say the PURL **after redirection MUST resolve** to the artefact, and term PURLs **MUST
resolve term-centrically**. STEMMA's equivalent obligations (§6 of `IDENTIFIER-POLICY.md`)
are currently marked *"Status: not yet active"* because the base is deferred (`stemma-urn-only`).

That is the correct sequencing given the R6 decision — but the *policy text* should say so
in the same phrase OBO uses, so that when the base is adopted, the upgrade is a one-line
activation and not a rewrite. See Finding F1.

### 2.5 Provenance and evidence — **STEMMA is ahead in structure, behind in one axis**

STEMMA's three evidence classes (FACT / CLAIM / INFERENCE) plus `validation_status`
(SUPPORTED / PARTIALLY_SUPPORTED / NEEDS_AUTHORITY) and PROV-O alignment is a genuinely
mature model. The 2026 literature (S5) confirms the field still lacks a single sufficient
vocabulary, and that the practical answer is a *community-agreed required set* enforced by
validation. STEMMA has that.

The gap is what gets recorded **about the people and the AI**, not about the claim. OBO
Principle 8 (S3) now *requires* `rdfs:isDefinedBy` provenance whenever a term is adopted
from another ontology under a new identifier — STEMMA's merge/remap path keeps a `history`
entry but does not require an explicit "this came from that" provenance triple in the
export. See Finding F3.

### 2.6 Human-in-the-loop — **STEMMA is ahead of peers, and the 2026 consensus now backs it**

This is the most important alignment. STEMMA's `REQ-STEMMA-HITL-001` / `-002` (AI drafts
stay draft until a named human reviews; no object becomes canonical without an explicit
human markdown edit; `writer: human:*` required; `hitl_check` fails closed) is now **exactly
what the 2026 consensus demands**:

- S1: Wikipedia banned LLM-generated content outright, with only two carve-outs —
  AI-assisted *copyediting of human-written text*, and first-pass translation *followed by
  full human review*. STEMMA's model (human authors the final text; AI assists) is the
  copyediting carve-out, generalised.
- S6: the publisher-consensus protocol requires that AI assistance never substitutes for
  author accountability, and that provenance of AI involvement be recorded.
- S2: the fabricated-citation finding is the empirical justification for STEMMA's
  "AI for verification/re-verification, human approves" position.

**STEMMA's HITL design is validated by the 2026 literature.** The user's stated
human-directed-AI-assisted model is the defensible mainstream position, not a shortcut.

### 2.7 Maintainer concentration — **the biggest unaddressed risk (Finding F2)**

Every 2026 source on project survival (S7) converges: a project with a bus factor of 1 is
structurally fragile, and the failure is silent until it triggers. STEMMA today is
**documented as effectively single-maintainer** (owner `Sajan`, `approver: null` everywhere,
contributors not to be accepted for some time per the user's HITL instruction). The spec
records the *content* governance thoroughly but does not record the **succession /
continuity risk** as a first-class, tracked item.

The xz-utils precedent (S7) is the sharp lesson: single-maintainer concentration is the
*precondition* that makes a trust-based takeover viable. For STEMMA the equivalent exposure
is not a supply-chain backdoor but **loss of the one person who can approve** — which
freezes the entire canonical layer, because the gate is fail-closed and `approver` is null.

**Verdict:** this must be recorded before approval. See Finding F2 — the highest-priority
finding in this report.

### 2.8 Release citation — **STEMMA's plan matches SOTA**

`ADR-0054`'s DOI-per-release plan (concept DOI + version DOIs) is exactly the Zenodo model
(S8) and matches the software-citation primer (arXiv:2609.28622, 2026-09). No change needed.

---

## 3. Findings — what is missing, wrong, or needs change

Findings are ordered by priority. Each states: what SOTA does, what STEMMA does, the delta,
and the proposed action. **None of these block approval of the 22 requirements**; they are
additions or clarifications the owner should rule on alongside.

### F2 (HIGH) — Continuity / succession risk is not recorded ⚠️ *highest priority* — **RESOLVED 2026-10-01**

- **SOTA:** bus-factor is treated as a *first-class, tracked risk*, mitigated by documented
  release process, distributed credentials, and a successor path (S7).
- **STEMMA:** `spec/ROLES_AND_AUTHORITY.md` names the sole owner; every requirement has
  `approver: null`; contributors deferred. The risk that this constitutes is nowhere recorded.
- **Delta:** no requirement or doc states what happens if the sole approver is unavailable —
  yet the fail-closed gate means canonical progress stops entirely.
- **Action taken (owner-approved):** **REQ-STEMMA-OPS-003 "Continuity of approval authority"**
  added (requirement set now 23), backed by new evidence `EVID-STEMMA-OPS-005`; a
  "Continuity of approval authority" section added to `docs/GOVERNANCE.md` recording the
  procedure, the successor path, the explicitly-accepted and dated single-maintainer risk,
  and the exit condition (second approver registered, or contributor intake opens).

### F1 (MEDIUM) — Published-IRI obligation wording should mirror OBO's "MUST resolve"

- **SOTA:** OBO Principle 3 (strengthened 2026) — PURL *after redirection* MUST resolve to
  the artefact; term PURLs MUST resolve term-centrically (S3).
- **STEMMA:** `IDENTIFIER-POLICY.md` §6 states the obligations but marks the section
  "Status: not yet active" without the redirection/term-centric phrasing.
- **Delta:** when the base is later adopted, the policy will need rewording, not just
  activation. Aligning the phrase now makes the upgrade a one-line switch.
- **Proposed action:** edit `IDENTIFIER-POLICY.md` §6 to adopt the OBO phrasing verbatim as
  the *activation condition* text, keeping the "not yet active" status.

### F3 (MEDIUM) — Adoption/merge provenance is not required to be explicit in the export

- **SOTA:** OBO Principle 8 (2026) requires `rdfs:isDefinedBy` provenance when a term is
  adopted into another ontology under a new identifier (S3); S5 shows provenance triples are
  a *required* metadata element, not optional.
- **STEMMA:** merge/split recorded in the object's `history`; export carries relation-registry
  and vocabulary sidecars (`REQ-STEMMA-EXP-002`) but no required "adopted-from" provenance edge.
- **Delta:** a consumer cannot reconstruct, from the export alone, that entity X is the
  re-identified form of an external entity.
- **Proposed action:** extend `REQ-STEMMA-EXP-002` acceptance criteria to require an
  adopted-from provenance field on merged/remapped entities, or add a dedicated relation.
  Owner's call whether this is a requirement change or a future ADR.

### F4 (MEDIUM) — Validation remains graph-scoped; dataset-scoped validity is the 2026 frontier

- **SOTA:** SHACL-DS (S4) and SHACL-UCR (S9): graph-scoped validation is inadequate for
  datasets because you "lose track of where triples come from."
- **STEMMA:** JSON Schema validation per object (`REQ-STEMMA-SCH-001`) + registry coherence
  (`REQ-STEMMA-SCH-003`), but no *dataset-level* declarative constraint layer.
- **Delta:** STEMMA validates objects and the gate, but not the export *as a dataset* in a
  declarative, self-contained way. Today this is covered by generator guarantee + freshness
  gate; longer-term it is the dated part of the spec.
- **Proposed action:** record as a forward-looking note in `spec/OPEN_QUESTIONS.md`
  (dataset-scope validation) — **do not** add a requirement now. Approve as-is.

### F5 (LOW) — "Contributors not accepted" is a policy that needs a date and an exit

- **SOTA:** the 2026 consensus is that AI involvement must be *recorded*, not hidden (S1, S6).
  STEMMA's deferral of contributors is a legitimate choice but must be explicit and reversible.
- **STEMMA:** user has ruled contributors are not accepted "for some time"; not yet written.
- **Delta:** an undocumented freeze reads as a closed project, which contradicts the
  "by the community, for the community" goal stated for R6.
- **Proposed action:** in `CONTRIBUTING.md`, state the freeze, its reason (content not yet at
  external-review quality), and the review trigger that lifts it. This is exactly the R6
  upgrade-condition logic, reapplied to contributors.

---

## 4. Confirmations (no change needed — recorded so approval is informed)

| STEMMA position | 2026 evidence it is correct |
|---|---|
| AI drafts stay draft; human approves (`HITL-001/002`) | S1 two carve-outs; S6 publisher consensus; S2 empirical justification |
| AI used for *verification/re-verification*, human for *approval* | S2 explicitly recommends automated reference verification pre-review, with human accountability retained |
| Canonical/derived separation; no embeddings in canonical (`CORE-001/003`) | No 2026 peer does it better; S5 shows consumers must introspect semantics independently |
| Deterministic, hash-stamped exports (`EXP-001`) | Matches reproducible-builds definition; no 2026 peer is stronger |
| Fail-closed gate (`GATE-001`); status honesty (`GATE-002`) | S1/S2 show why machine-checkable honesty matters |
| DOI-per-release via concept DOI (`ADR-0054`) | S8 Zenodo model; arXiv:2609.28622 |
| Deprecation ≠ deletion, never reuse IDs (`IDENTIFIER-POLICY`) | S3 shows OBO has *no* such policy — STEMMA is ahead |

---

## 5. Recommended actions before approval

1. **Record F2 (continuity)** — new requirement `REQ-STEMMA-OPS-003` + `GOVERNANCE.md` section.
   *Do this before approving*, because it changes the requirement set from 22 to 23.
2. **F1** — one-paragraph wording edit to `IDENTIFIER-POLICY.md` §6 (no status change).
3. **F3** — owner ruling: extend `EXP-002` acceptance criteria, or defer to a future ADR.
4. **F5** — wording in `CONTRIBUTING.md` (ties into the pending HITL documentation work).
5. **F4** — additive entry in `spec/OPEN_QUESTIONS.md`; no requirement change.

Everything else: the requirements stand on their own against 2026 practice. Nothing in
this comparison found the architecture *wrong*; the corrections are about **recording the
human and continuity layer as carefully as the knowledge layer**.

---

## 5b. Owner rulings (2026-10-01)

All five findings were ruled on by the owner on 2026-10-01:

| Finding | Owner ruling | Effect |
|---|---|---|
| **F2** (HIGH) continuity | **Record as the 23rd requirement** | `REQ-STEMMA-OPS-003` added + `GOVERNANCE.md` section; evidence `EVID-STEMMA-OPS-005` |
| **F1** (MED) IRI wording | **Align wording now** | `IDENTIFIER-POLICY.md` §6 reworded to the OBO "MUST resolve after redirection" form, status still not-yet-active |
| **F3** (MED) adoption provenance | **Extend it** | `REQ-STEMMA-EXP-002` acceptance criteria extended to require adopted-from provenance |
| **F4** (MED) dataset validation | **Note it; add no requirements now** | `spec/OPEN_QUESTIONS.md` entry only |
| **F5** (LOW) contributor freeze | **State it until the owner decides** | `CONTRIBUTING.md` states the freeze is in force until the owner decides otherwise |

A sixth item was raised by the owner at the same time and is tracked separately: the
**explorer** (3D force-graph app, `explorer/`) must be preserved and working, and must gain
an **AI chat** that answers by exporting from STEMMA (see §7).

---

## 6. Note on the A3 / OPS-002 inference

`REQ-STEMMA-OPS-002` rests on `EVID-STEMMA-OPS-004` (an INFERENCE) and carries
`validation_status: NEEDS_AUTHORITY`. The user has ruled: **the inference must be
human-reviewed and approved before it converts to FACT; no machine may approve it.** This
SOTA scan supports that rule — S6 requires recorded human accountability for exactly this
kind of derived assertion, and S2 shows unsupervised machine promotion of unverifiable
claims is the central risk of the current period. The mechanism for "human approves the
inference → it becomes FACT" should be documented as part of the HITL work, so the rule is
enforced by the gate rather than by convention.

---

## 7. Explorer + AI chat (owner-raised, 2026-10-01)

**Status of the explorer:** intact and working — it was never removed. `explorer/` is a
tracked Vite/TypeScript app (26 tracked files) using `3d-force-graph` + `three`; its
projection verifier passes (`node scripts/verify-graph-projection.mjs` → OK), the export
sync works, and it is wired into CI (`explorer-build` job, required by the all-green gate).
Its `dist/` build is from 2026-09-07 and should be regenerated when next built.

**Owner requirement:** the explorer must be preserved and kept working, and must gain an
**AI chat** through which people can ask questions and receive answers exported from STEMMA.
This doubles as a **consumer conformance test** — it exercises the export the way a real
consumer would, which is exactly the kind of behavioural evidence the spec's consumer
requirements (EXP-002/-004, INTEG) currently lack.

This is recorded as **REQ-STEMMA-INTEG-001**, and the boundary is settled by
**ADR-0055** (`docs/decisions/0055-explorer-product-layer-boundary.md`): the explorer and
its chat are the **product layer built on the core**, not part of it — one-way dependency
(the core never references the explorer), presentation is not canonical, the chat is a
consumer (derived-only, grounded, own model selection), and RAG stays the consumer's job
including ours. The explorer is covered as a consumer: `schema/consumer-registry.yaml`
declares `stemma-explorer`, so preserving it is consistent with existing consumer governance.

*Report compiled 2026-10-01. All sources retrieved within the last 6 months as of that date.*
