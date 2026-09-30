# IDENTIFIER POLICY — STEMMA

Status: Authoritative (owner-approved)
Owner: Sajan (SOLE_OWNER) — publisher of record per ADR-0053
Ratified: 2026-10-01
Related: ADR-0053 (+ Amendment 0001) · docs/decisions/r6-identifier-base.md ·
docs/PERSISTENT-IDENTIFIER-BRIEF.md §6.4 · docs/CURATION-PROTOCOL.md ·
docs/GOVERNANCE.md · spec/OPEN_QUESTIONS.md UNRES-STEMMA-CORE-001

## Why this document exists

The persistence of an identifier has two halves. One is **technical** — a resolver
that maps a string to a current location. The other is **semantic** — promises about
what an identifier is allowed to *mean* over time, and what happens when the thing it
names changes, splits, merges, or dies.

**STEMMA currently relies on the semantic half alone.** Per
`docs/decisions/r6-identifier-base.md` (2026-10-01), no external resolution base is
adopted; identifiers are `stemma:` URNs, globally unique and locally authoritative but
not externally dereferenceable. That makes this document more load-bearing, not less:
with no resolver to fall back on, these governance promises are the *only* thing
keeping an embedded identifier meaningful. It must exist — and be exercised — before any
external consumer embeds a STEMMA identifier, because retrofitting these promises after
the fact breaks other people's data.

The technical half can be added later at the cost of one mapping line (§6). The
semantic half cannot be retrofitted at any cost.

Scope: this policy governs **canonical entity identifiers** (`stemma:<ns>.<slug>`),
**source identifiers** (`stemma:src.*`), **connection identifiers** (`conn.NNNNNN`),
and — once published — the **published IRIs** projected from them. It does not govern
release-artifact identifiers (see §7).

---

## 1. Immutability — never delete, never reuse

**The rule.** A canonical identifier, once minted, is permanent. It is never deleted,
never reassigned, and never repurposed to name a different thing.

**Rationale.** Identifiers are the join key of the entire system. Consumers store them
in their own databases forever; a reused identifier silently corrupts every join made
against it, and the corruption is undetectable from the consumer's side.

**Enforcement.** Machine-enforced today: `check_id_immutability.py` plus
`test_id_immutability` fail the gate if an ID disappears or changes meaning.
Corrected claims are **superseded, never edited in place** (ADR-0043 lineage).

**Published IRIs.** This rule applies with equal force to the HTTP form once a
resolution base is adopted. A published IRI is a promise made to strangers; the
promise is not retractable. Until then it applies unchanged to the `stemma:` URN,
which is already embedded in consumer imports and exports.

---

## 2. Deprecation ≠ removal

**The rule.** An entity that is no longer current keeps its identifier. It is marked
`status: deprecated` and, where a successor exists, carries `superseded_by: <id>`.

**What must remain true.** The identifier continues to resolve (technically) and
continues to identify the same historical concept (semantically). Importers honor the
deprecation flag; they are not expected to drop the entry.

**Forbidden.** Silently removing a deprecated entity, or reusing its identifier for
something current. Deprecation is a *state*, not a deletion.

---

## 3. Merge

**The rule.** When two entities are found to be the same thing, one is absorbed:
the surviving identifier keeps the merged semantics; the absorbed identifier is
**retained** and marked `merged_into: <surviving-id>`.

**Resolution behavior.** A request for the absorbed identifier resolves with a
deprecation/redirect notice pointing at the survivor. Tooling that walks the graph
should follow `merged_into`.

**Forbidden.** Deleting the absorbed identifier, or repurposing it. Other datasets
hold it; a deletion is a silent dangling reference.

---

## 4. Split

**The rule.** When one entity is found to conflate two distinct things, the original
identifier **keeps the historical union semantics** and is marked `split:` pointing at
the new, narrower identifiers.

**Why the original is not narrowed.** Consumers holding the original ID were promised
"the thing this ID named." After a split, that promise is only kept by the original
retaining the broader historical meaning; silently narrowing it changes what an
existing consumer's data refers to.

**Forbidden.** Reusing the original identifier for one of the narrower concepts.

---

## 5. Meaning authority

**The rule.** The canonical layer plus the human review chain
(`docs/CURATION-PROTOCOL.md` review states, `scripts/review.py`, `hitl_check.py`) is
the **only** authority that may define, redefine, or mint an identifier's meaning.

**Explicit non-authorities.** AI extraction, ingestion pipelines, templating, and any
automated process may produce **proposals**; they may never mint an identifier or
alter an existing identifier's meaning. Machine drafts are recorded as
`ai_drafted: true` with the machine as `drafted_by`; a named human becomes `writer`
on review (HITL fails closed without a registered `human:*`).

**Rationale.** Semantic stability is the half of persistence no resolver can provide.
If an automated process could redefine an ID, the immutable string would be a stable
name for an unstable thing — the worst of both.

---

## 6. Published-IRI obligations

**Status: not yet active.** Per `docs/decisions/r6-identifier-base.md` (2026-10-01),
STEMMA publishes under its own `stemma:` URNs only, with **no external resolution base**.
The obligations below therefore do not bind yet — they activate on the day an external
base is adopted. They are recorded now because they are the price of that upgrade, and
because they must be *demonstrably exercised* before the upgrade is taken (§5
precondition in the R6 record).

Once an identifier is published as an HTTP IRI, STEMMA accepts these operational duties,
independent of the resolution base:

1. **Keep resolution working — the MUST, stated in the standard's own words.** A published
   IRI **MUST resolve after redirection** to the artefact it names, and a published
   *entity* IRI **MUST resolve to a term-centric page for that entity** (not to a bulk
   file, not to a list, not to a search result). This wording follows the OBO Foundry's
   Principle 3 as strengthened in 2026 (OBO Foundry Newsletter #10, 2026-04-13) — the
   closest governance peer to STEMMA — so that adopting the base later is a switch, not a
   redefinition. Broken targets are STEMMA's responsibility, not the resolver's.
2. **Keep maintainer authority current and non-singular.** Do not let resolution
   authority rest on one person's account. At least one maintainer other than the
   owner must be able to edit redirect rules, so that succession (individual → org) is
   a routine edit rather than a recovery operation. (Consistent with
   `REQ-STEMMA-OPS-003`, continuity of approval authority.)
3. **Never embed a STEMMA-owned address in a published string.** Published IRIs must
   route through an institution-backed resolution switchboard, never directly through
   a domain STEMMA must own forever. This is what keeps the base swappable.
4. **Change the mapping, not the string.** Moving the content host is a redirect-rule
   change. Rebranding the published string itself is the one irreversible act; it
   requires a new ADR and is avoided by design.
5. **Record authority changes.** A change of publisher of record (individual → org →
   consortium) is a new ADR; a change of resolution base is an amendment to the R6
   identifier-base record. Neither silently rewrites history.

---

## 7. Out of scope — release-artifact identifiers

Release snapshots (exports, JSON-LD dumps, signed bundles) are a **different
identifier class** from entities. They are content-addressed today
(`R6-bundle-<payload_hash12>`, `content_hash` fields) and may additionally receive
DOI/Handle identifiers via a repository (e.g. Zenodo) in a separate, orthogonal
decision.

The distinction is deliberate and matches established practice: no serious project
stuffs per-term concept identifiers into DOI-style registration objects, and nobody
expects a dataset DOI to be a dereferenceable vocabulary term. **Entity identifiers and
release identifiers are two systems held together by metadata** — do not conflate
them, and do not mint a registration-object identifier per entity.

---

## 8. Summary of promises to embedders

Anyone may embed a STEMMA identifier and rely on all of the following:

- The identifier will never name a different thing than it names today.
- The identifier will never be deleted or reused.
- A deprecated, merged, or split identifier remains present and self-describing
  (currently by inspection of the canonical layer; by dereference once §6 activates, at
  which point a published IRI **MUST resolve after redirection** to the entity's own
  term-centric page — §6.1).
- The meaning of an identifier changes only through the documented human review chain.
- The identifier is globally unique — no two STEMMA entities may share a `stemma:` string.
- The string shape is stable permanently; the address behind it (if any is ever adopted)
  may move without notice.

**Scope of the promise today.** All of the above hold now, and hold at millions of
entities. One thing is explicitly *not* promised yet: that a machine holding only the bare
string `stemma:phys.metre`, with no prior import of STEMMA data, can fetch something over
the web. That is the single capability deferred by
`docs/decisions/r6-identifier-base.md`, and it is additive — adopting it later breaks
nothing that exists today.

These promises are the product. A resolver is merely one way to deliver them, and STEMMA
has deliberately not bought one yet. Until it does, the promises are enforced by the
canonical gate and the human review chain — which is why §1–§5 are machine-checked rather
than advisory.
