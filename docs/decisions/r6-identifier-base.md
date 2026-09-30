---
decision: stemma-urn-only
decided_by: human:curator.001
decided_at: 2026-10-01
rationale: >
  Owner ruling at the R6 stage, per ADR-0053 Amendment 0001. STEMMA stays on its own
  `stemma:` URN identifiers with NO external publication base for now. Decisive reason
  (owner): the corpus and the review process are not yet at the maturity that a public
  persistent-identifier namespace implies. STEMMA is currently a single curator working
  with AI assistance; extending to AI-assisted verification is an explicit next step, so
  committing publicly now would promise strangers a durability and review depth that do
  not yet exist. The brief establishes (Phase 8 §6, Phase 10 §4) that this choice is
  cheaply reversible while pre-publication — nothing external embeds a resolvable stemma
  URI yet, so no published-string stickiness has engaged. Deferring costs nothing
  structurally and preserves total freedom of base choice later.
  Explicitly NOT a rejection of w3id: w3id remains the recorded intended base once the
  content/schema/canonicalisation pipeline is proven (see §6 upgrade path). `stemma:` URNs
  are already globally unique by construction (scheme prefix + STEMMA's registry
  discipline) and scale to millions of entities for all internal and consumer-side use
  (joins, lookups, graph traversal, exports, RAG). The only capability deferred is
  EXTERNAL web dereference from the bare string — not identity, not scale, not validity.
title: R6 Identifier Base — Published Entity IRI Scheme
status: Decided
date: 2026-10-01
decides: ADR-0053 sub-decision (b) — deferred by ADR-0053 Amendment 0001 to R6
decided_by_authority: Sajan (SOLE_OWNER) — owner ruling, recorded mechanically
supersedes_in_part: an earlier same-day draft of this record that selected w3id (superseded before commit)
related:
  - docs/decisions/0053-organization-domain-iri-base.md (Amendment 0001 — deferral)
  - docs/IDENTIFIER-POLICY.md (semantic half of persistence — host-independent)
  - docs/PERSISTENT-IDENTIFIER-BRIEF.md (research evidence; no decision recorded therein)
  - docs/ROADMAP.md R6 (Projection Publication)
  - spec/OPEN_QUESTIONS.md UNRES-STEMMA-CORE-001
  - scripts/publication_gate.py (mechanical enforcement of this record's existence)
---

# R6 Identifier Base — decision record

## 0. What this record is

ADR-0053 recorded three sub-decisions; Amendment 0001 **reaffirmed** (a) publisher of
record and the canonical identity architecture as binding, and **deferred** (b) the
resolution/IRI base to R6 pending owner-directed slow research. This is that deferred
decision, recorded where R6 needs it. It does not rewrite ADR-0053; it settles its open
clause.

`scripts/publication_gate.py` blocks publication (exit 1) until this file exists with a
valid `decision` value from the candidate set and a `decided_by` beginning `human:`.
Recording `stemma-urn-only` is a full, valid decision: it satisfies the gate while
deliberately declining an external base.

## 1. The question

Under which resolvable string-and-host pair do STEMMA entities first become visible to
machines that are not STEMMA — or, alternately, is external publication itself premature?

## 2. Decision

**STEMMA publishes under its own `stemma:` URN identifiers only. No external resolution
base is adopted at this time.**

- **Identity is unchanged and unchanged-able.** Canonical IDs remain immutable `stemma:`
  URNs (`stemma:phys.metre`), machine-enforced by schema patterns and the
  id-immutability rule. This is ADR-0053(a), binding.
- **No namespace is claimed.** No w3id PR, no own domain, no ARK NAAN, no resolution
  infrastructure. Nothing is published that implies a commitment STEMMA cannot yet keep.
- **The projection continues to carry URNs.** `exports/knowledge.jsonld` keeps
  `"stemma": "stemma:"` in its `@context`. URNs are legitimate IRIs in RDF, so the
  JSON-LD, SKOS, and vocabulary mappings remain valid and complete.
- **The deferral is deliberate and bounded** — it ends when §6's conditions are met, not
  on a date.

### 2.1 Why this, rather than an immediate base

| Consideration | Assessment |
|---|---|
| Corpus maturity | 9 entities, 7 canonical. Real content at 10²–10³ scale is the plan (R7/R8). |
| Review depth | Single curator + AI assistance today. AI-assisted verification is a planned *next* step, not an established practice. |
| What a public PID promises | An operational commitment to keep resolving, indefinitely, for strangers' stored strings. |
| Consequence of promising early | If the project stalls or the base is wrong, other people's data breaks — and (brief Phase 7 S4/S7) an early own-domain choice is the one *unrecoverable* variant. |
| Consequence of deferring | Zero. Brief Phase 8 §6 / Phase 10 §4: reversible while pre-publication, because nothing external stores a resolvable stemma URI yet. |

The asymmetry is the whole argument: deferring costs nothing now, and premature
publication is the one move that can create irreversible external breakage.

### 2.2 What this decision does NOT cost

Explicitly recorded so the trade-off is honest, not self-flattering:

- **Not global uniqueness.** `stemma:` URNs are unique by construction — the scheme
  prefix is STEMMA's registered namespace in its own registry, and IDs are
  machine-enforced and immutable.
- **Not scale.** Nothing in the URN design constrains entity count. Joins, lookups,
  graph traversal, exports, consumer bundles, and RAG all operate on URN strings and
  scale to **millions of entities**. The thousands/millions-of-entities use case is
  fully served *today*.
- **Not validity.** URNs are valid IRIs; `knowledge.jsonld` is valid RDF with URN
  subjects.
- **Not internal machine use.** Any consumer reading the export resolves URNs trivially
  — it is a lookup in their own imported graph, not a network fetch.

**The only deferred capability is external dereferencing**: an outsider holding only the
bare string `stemma:phys.metre` cannot fetch STEMMA's data about it over the web, nor can
an auto-dereferencing Linked-Data crawler discover the entity without a manual import.
That is an *opportunity* cost (citation, discovery, external embedding), not a
correctness or capacity cost.

## 3. Consequence: FAIR standing, recorded honestly

Per the brief (Phase 9), FAIR **F1** as interpreted by GO FAIR requires identifiers that
are globally unique **and persistent and resolvable** ("GUPRI"); **A1** requires
retrievability by identifier over an open protocol. `stemma:` URNs satisfy the uniqueness
and persistence-by-policy halves, **not** the resolvability half.

This is an accepted, recorded consequence of the decision, to be revisited at §6. It is
not a defect being hidden: it is the reason §6 exists.

## 4. Consequences

- **R6 publication gate: OPEN.** The gate accepts this record (`stemma-urn-only`,
  `human:*`). Recording the decision — rather than leaving it unrecorded — is what
  unblocks mechanically.
- **Canonical layer untouched.** No ID migration, no schema change, no export change, no
  consumer breakage.
- **R6's projection increments remain valid as-is.** The JSON-LD projection, SHACL
  contract, deterministic bundles, and signing mechanics were all built
  **PID-agnostic** deliberately. They do not need to change because the base is deferred
  — they will need exactly one `@context` line changed when a base is adopted.
- **Release-level identification (DOI) is NOT decided here.** Still an open,
  orthogonal lane: adopting a DOI per release via Zenodo requires no entity-base
  decision and can be done at any release event. If citation-grade handles are wanted
  before the entity base is chosen, this is the lane to use — it is independent.
- **UNRES-STEMMA-CORE-001:** the published-PID portion is RESOLVED as *decided to
  defer*, with the upgrade conditions in §6 making the deferral bounded rather than
  open-ended.

## 5. Obligations this decision still incurs

Declining an external base does not remove the semantic obligations — it makes them the
*only* thing guaranteeing persistence. `docs/IDENTIFIER-POLICY.md` (owner-ratified
2026-10-01) records them and is binding now, precisely because there is no infrastructure
to fall back on: never-delete/never-reuse, deprecation ≠ removal, merge, split, and
meaning-authority rules.

**Additional precondition recorded for §6:** before any external base is adopted, the
`docs/IDENTIFIER-POLICY.md` guarantees must be *demonstrably exercised* at least once
(a real deprecation or merge in the corpus), so the upgrade rests on tested practice
rather than untested policy text.

## 6. Upgrade path — the conditions and the mechanics

**This decision is explicitly an upgradeable state, not a permanent choice.**

### 6.1 Conditions for adopting an external base (owner-set, all must hold)

1. **Corpus at meaningful scale** — the canonical corpus demonstrates the schema and
   the canonicalisation pipeline at a scale where the design is proven, not assumed.
2. **Review process is real** — review is no longer solely one curator plus AI drafts.
   Either additional human reviewers exist, or AI-assisted verification is an
   established, documented, and accepted practice in `docs/CURATION-PROTOCOL.md` with
   its limits recorded honestly.
3. **The identifier policy is exercised** — at least one real deprecation or merge has
   happened and resolved cleanly (see §5 precondition).
4. **The candidate base is re-verified at that time** — per the R5 brief protocol,
   because identifier infrastructure drifts (the purl.org lesson).

### 6.2 The mechanics (why the upgrade is cheap)

Adopting a base later touches **one line**, because the architecture keeps identity and
resolution apart (brief §6.3):

```json
{ "@context": { "stemma": "https://<chosen-base>/stemma/" } }
```

No canonical ID changes. No consumer migration for existing consumers (they join on
`stemma:` strings, which never change). No schema change. Old exports remain valid; new
exports expand to HTTP IRIs.

### 6.3 The recorded intended base

**w3id.org remains the intended base** when §6.1 is satisfied, for the reasons the
2026-09-22 research established: free, community-consortium-operated, rules in a public
forkable git repo (matching STEMMA's community-governance direction), and namespace
transfer individual → org by a PR rather than a legal instrument.

**The owner's other longer-term intent is also preserved:** a STEMMA-owned domain held by
a future org is a legitimate end-state (the OBO Foundry pattern, and OBO is already an
anchor in STEMMA's architecture via BFO IRIs). If taken, the sequence is
w3id → org-owned domain by one redirect rule, with no published-string change.

**One time-sensitive caution, recorded for later:** w3id namespaces are first-come. The
`stemma` slug was free on 2026-09-22 and re-checked 2026-10-01. If the §6.1 conditions
are far off, the owner may later consider claiming the namespace *purely as squatting
insurance* — claiming is not committing, and an unused namespace can be re-pointed or
removed. This is recorded as an option, not a recommendation, and is not part of this
decision.

## 7. Explicitly not decided / not executed

- Any external resolution base (deferred per §6).
- DOI-per-release (independent lane; adoptable at any time).
- N2T compact-identifier registration for `stemma:` (additive lane).
- No namespace claimed; no resolution infrastructure; no canonical ID changes.

## 8. Amendment procedure

- **Adopting an external base** — an amendment to this record (changing `decision:` and
  §2), plus the §6.2 one-line mapping. It does not invalidate anything already published,
  because `stemma:` strings are the stable join key and never change.
- **Change of publisher of record** (individual → org) — a new ADR, per ADR-0053's own
  rule, not an amendment here.
- **A change of switchboard** after a base exists (w3id → ARK → own domain) — an
  amendment plus a redirect-rule change, per §6.2.
