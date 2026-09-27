# ADR-0053: Organization / Domain / IRI Base (R5)

Status: Decided — amended 2026-09-22 (Amendment 0001: (a) publisher + canonical identity architecture REAFFIRMED and binding; (b) w3id/resolution choice UNDER REVIEW, deferred to R6 — see amendment below)
Date: 2026-09-22 (original ruling); Amended: 2026-09-22 (Amendment 0001)
Decided by: Sajan (sole owner — recorded as written instruction from the authority human; this ADR documents the owner's decision, it does not create it)
Baseline: ADR-0044
Related: docs/ARCHITECTURE-V2.md Part 10 Phase 5 (Organization/IRI Gate), docs/ROADMAP.md R5, spec/OPEN_QUESTIONS.md UNRES-STEMMA-CORE-001 (closed by this ADR), ADR-0027 (namespace decision, archived old-design)

## Context

Canonical IDs are stable URN-style identifiers — `stemma:phys.metre`, `stemma:src.*` — machine-enforced by schema patterns (concept.schema.json) and immutable by curation rule (check_id_immutability; IDs are never reused or reassigned). These are NOT published IRIs: nothing under `stemma:` dereferences today.

ARCHITECTURE-V2 assumes canonical IDs never change and that the semantic-web surface (knowledge.jsonld, SKOS, BFO-2020, schema.org, QUDT/UCUM/Wikidata anchors) is a DERIVED projection over those stable IDs (R6). The open questions were organizational, not technical: who publishes, under which domain, and whether canonical IDs themselves should migrate to HTTP IRIs. ROADMAP marked this R5 as an explicit HUMAN DECISION; everything touching published IRIs waited on it. Recovery pilot recorded it as UNRES-STEMMA-CORE-001 (blocking for publication scope; not blocking the R4 content acceptance test).

## Decision

**(a) Owning organization — Individual: Sajan.** Sajan is the publisher of record for STEMMA's published IRIs and the project identity. A formal organization (foundation, company, collective) MAY be adopted later; doing so is a new named decision recorded as a new ADR, not an amendment of this one. Publisher-of-record appears as such in R6 projections/release bundles.

**(b) Publication domain — w3id.org.** Published STEMMA IRIs resolve under a w3id.org persistent-identifier namespace (proposed base IRI slug: `https://w3id.org/stemma/`). Rationale: free, community-operated for permanence, redirect targets changeable at any time, no domain procurement, consistent with the foundation's stability requirements. Consequence/next action: the w3id slug MUST be claimed by filing the redirect-definition PR on the w3id.org repository (external human action by the owner; perform no later than R6, earlier is safer). Until claimed, the slug is unreserved.

**(c) IRI base form — staged: canonical stays `stemma:` URN; HTTP mapping is defined at R6.** Canonical IDs never change (immutability is a load-bearing property: consumers join on them; the curation gate enforces it). The HTTP IRIs chosen here exist ONLY as DERIVED projections with explicit recorded mappings (jsonld context / mapping file), defined by the R6 projection publication ADR under the domain in (b). No canonical migration, no schema pattern change, no consumer breakage. Relations/entities project per ARCHITECTURE-V2's pluggable mapping rules (QUDT/UCUM/Wikidata anchors; verified-IRI-before-publication rule).

## Consequences

- R4 (content acceptance test, ADR-0052) proceeds unchanged — it never required IRIs.
- R6 scope concrete: projection publication includes the w3id-namespace mapping file + context, defined in the R6 ADR; publication blocked only on R6 work itself, not on open identity questions.
- No schema, validator, export, or consumer code changes are implied by this ADR; nothing about `stemma:` IDs changes.
- UNRES-STEMMA-CORE-001 is CLOSED (decided).
- Risk recorded: w3id slug squatting before the owner files the namespace PR — mitigated by filing early; if lost, redirect under an alternate slug via new small ADR.
- Authority note: sub-decisions (a)–(c) were made by the sole owner in direct instruction (2026-09-22); the executor's role was presentation of options with evidence and mechanical recording.


---

## Amendment 0001 — 2026-09-22 (owner ruling, recorded)

**Context.** After this ADR was filed, the owner ordered a slow-research
evaluation before final commitment: docs/PERSISTENT-IDENTIFIER-BRIEF.md
(Phases 1-10, current-source research, no decision recorded in the brief).

**Ruling (Sajan, 2026-09-22), recorded mechanically by the executor:**

1. **REAFFIRMED — valid and binding.**
   - (a) Publisher of record: individual Sajan (a formal org later = new ADR).
   - The canonical identity architecture: immutable `stemma:` URN identifiers,
     machine-enforced by schema patterns and the curation id-immutability rule;
     canonical Markdown/YAML carries no host, domain, or resolver knowledge;
     resolution is exclusively a derived projection-layer concern.

2. **UNDER REVIEW / DEFERRED — not binding.** Sub-decision (b) (w3id.org as
   the resolution base) and the associated projection-mapping choice are NOT
   decided. Per the brief (Phase 8): this choice is reversible while the
   repository is pre-publication — no resolvable stemma URI exists yet, so
   the published-string stickiness locked on nothing. Decision stage: **R6
   projection publication**, the repository-defined stage where a resolvable
   base first becomes actually required. At R6 the owner rules: reaffirm,
   re-amend, or supersede this ADR.

3. **Explicitly not executed.** No w3id slug was registered or claimed; no
   canonical identifiers were changed; no resolution infrastructure was or
   will be implemented absent this decision. The optional w3id slug claim
   remains a separate, non-blocking consideration for the owner.

4. UNRES-STEMMA-CORE-001 is updated accordingly: canonical-identity portion
   resolved; published-PID/resolution portion open (non-blocking until R6).

**Historical note.** The Decision text above this divider is the unchanged
record of the 2026-09-22 ruling; it is historical, not silently rewritten.
The related research brief cross-references this amendment (its §0.3
disposition note).
