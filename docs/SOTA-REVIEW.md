# STEMMA — Critical SOTA Review & Canonical-Knowledge Gap Analysis

**Status:** Review artifact (not an architecture authority). Companion to
`docs/ARCHITECTURE.md` (which remains authoritative for the implemented system).
**Date:** 2026-09-06
**Method:** repository audit + full `scripts/verify_all.py` (23 steps, green) +
data-level inspection of `content/`, `connections/`, `sources/`, `exports/`,
`adapters/`, and `tests/`.
**Scope:** evaluate STEMMA as a canonical STEM knowledge infrastructure from
first principles; identify what is missing from the re-architecture brief
itself; propose smallest-justified improvements before any implementation.

---

## 0. Executive summary

> The full per-thread recommendations live in
> [`docs/DEEP-DIVE-RECOMMENDATIONS.md`](DEEP-DIVE-RECOMMENDATIONS.md).
> This file records findings, decided design threads, and the gap analysis.

STEMMA is already a surprisingly strong canonical knowledge infrastructure.
It is *not* a generic/derived knowledge dump, nor a naive JSON schema over
science text. It implements the core principles the brief asks for:

- three canonical object kinds (entity / connection / source);
- first-class, reified relationship assertions with provenance, review state,
  evidence, context, and lifecycle;
- a governed relation registry with domain/range, inverse coherence, and
  transitivity;
- a deterministic gate whose order is `validate → write export`, with the
  export validated against its own contract **before** publication;
- git-history identity and connection-triple immutability guards;
- review-stage separation (`unreviewed → reviewed → canonical`, human-only
  transitions);
- a first-party read-only consumer adapter and a consumer-owned explorer;
- an architecture that deliberately excludes graph DBs, microservices, and
  heavyweight ontology stacks.

The biggest problems are therefore **not**: "add a graph database", "adopt
RDF/OWL", or "build an API". The biggest problems are:

1. **The `rejected` lifecycle state is not representable in the schema.**
   `docs/CURATION-PROTOCOL.md` and `docs/GLOSSARY.md` state that rejected
   assertions are auditable and retained. But
   `schema/connection.schema.json` only allows
   `assertion.status ∈ {active,deprecated,superseded}` and
   `assertion.review.status ∈ {unreviewed,reviewed,canonical}`. The review
   tooling (`scripts/review.py`, `scripts/apply_review_decisions.py`) therefore
   either produces schema-invalid YAML or encodes "rejection" as
   `assertion.status: deprecated` — which conflates *rejected as scientifically
   wrong* with *retired/renumbered*. A reviewer cannot legally and readably
   record "this claim is wrong and here is why".

2. **The relation registry is not in the export.**
   `docs/CONSUMERS.md` and ADR-0030 explicitly document this as a known gap:
   consumers cannot discover relation families, inverses, transitivity, or
   domain/range from the published contract alone. They must clone the
   producer repo or hard-code relation semantics. This weakens the adaptor
   boundary, which is one of the brief's central requirements.

3. **The validator is not truly machine-readable at the warning/info level.**
   `validate.py` accumulates `errors` and a separate `warnings` list, prints
   warnings to stderr, but writes only `errors` (all labelled `Violation`) into
   `reports/validation-report.json`. `integrity_anomalies.py` *does* produce an
   `ERROR/WARNING/INFO` report but is not part of `verify_all.py` and never
   fails even on `ERROR`. There is no single, deterministic,
   machine-readable severity-annotated result for CI or agent consumption.

4. **The schema does not validate the entity's domain identity.** Entity
   `domain` is a free string; the id prefix (`stemma:phys.*`) and the on-disk
   path (`content/physics/...`) are not cross-checked against
   `schema/vocabularies/domains.yaml` or a declared domain-code mapping. The
   corpus currently contains a real mismatch: `content/earth-space/.../
   our-environment.md` has id `stemma:phys.our-environment` and `domain:
   physics` (its identity, path, and vocabulary disagree). Nothing in the gate
   catches this.

5. **The "knowledge vs consumer" boundary is contaminated in the entity
   schema.** `learning_objectives`, `common_misconceptions`, and arguably
   `real_world_applications` are consumer/pedagogy-shaped fields living in
   canonical data. The bridge (1) and the architecture claim "no curriculum,
   grade, course or product", but "learning objectives" are by definition
   instructional intent. This is the clearest place where product logic has
   leaked into the canonical layer.

6. **The mathematical layer is display-string-only.** `equation`,
   `symbol`, `unit` are strings, there is exactly one `unit` entity in the
   corpus, and there is no symbol→quantity binding, no dimensional vector, no
   machine-checkable equation structure. ADR-0024 (the math layer) is proposed
   but open. This is the single largest subject-matter gap for "WHOLE STEM" and
   affects quantities, laws, derived relations, and dimensional consistency.

7. **Evidence and source records are largely unbacked.**  599/654 connections
   carry empty `evidence[]`; only 3 canonical source records exist while 44
   distinct citation strings appear on entities. The validator permits
   canonical assertions with no evidence (review tooling checks it manually),
   and there is no gate that the provenance `source` strings on entities should
   eventually resolve to `sources/*.yaml`.

8. **Stale/hand-written analytic text drifts.** `scripts/epistemic_summary.py`
   and `scripts/curation_status.py` embed prose like "All 397 are canonical
   objects; 15 canonical assertions" / "canonical objects (397)" that do not
   match the real corpus (654 connections, 50 canonical). `docs/SOURCES.md`
   hard-codes counts ("149 entities", "40 entities carry one") which are also
   not gate-checked. These are a documentation/report accuracy hazard.

9. **The ingest path emits non-schema-conforming candidates.** `ingest.py`
   `build_source_candidate()` returns `type: source` with `kind/format/pages/
   extracted_text_preview` — it does not conform to `source.schema.json`
   (required `citation`; `type` must be `textbook|academic-paper|standard|
   institutional|other`). The default entity draft in `ingest_to_proposals.py`
   still emits `relationships: []`, which ADR-0028 makes a schema violation. The
   curation pipeline compares against a `validate.REL_TYPES` attribute that does
   not exist on `validate.py`, so any non-empty `relationships` path crashes.

10. **The relation vocabulary is over-generic in corpus practice.**
    `related_to` is 371/654 connections (57%). It is a legitimate associative
    catch-all, but its dominance hides that most corpus edges are semantically
    weak. The registry already reserves stronger relations
    (`causes`, `contributes_to`, `explains`, `measures`, `quantifies`,
    `expressed_in`, `equivalent_to`, ...) that are unused. This is a content
    curation problem, not an architecture problem, but it is the main reason
    the graph is not yet a *reasoning*-grade knowledge graph.

11. **The domain vocabulary has an unmanaged code-vs-name split.** IDs use
    short codes (`phys`, `chem`, `bio`, `math`, `earth`, `eng`, `epist`,
    `practice`); the `domain` field and path use full words (`physics`,
    `chemistry`, `biology`, `mathematics`, `earth-space`, `engineering`,
    `scientific-practice`). There is no single source of truth mapping
    `phys ↔ physics`, and `scientific-practice` currently has two id prefixes
    (`epist` and `practice`) for the same domain.

12. **`content_trust_audit.py` and `docs/INGESTION.md` are stale.** The
    trust-audit script is not in the verify chain and references artifact names
    that no longer exist (`knowledge.compat-0.1.json`, `review-queue-v0.2.json`,
    `integrity-anomalies-v0.2.json`). The ingestion doc's library example still
    shows `relationships: []`.

---

## 0.1 Decided design: the `rejected` lifecycle state (2026-09-06)

The review was asked to decide how scientific rejection is represented. The
decisions are recorded here as the implementation contract for Tier-1 item 1:

- **Rejection lives in `assertion.review.status`** (`unreviewed / reviewed /
  canonical / rejected`). A rejected record remains an active canonical object
  (`assertion.status: active`); `deprecated`/`superseded` stay reserved for
  structural retirement (dedup, merge, replaced), not scientific rejection.
  **Implemented 2026-09-06 (ADR-0031, schema 1.1.0).**
- **A rejection must carry a written reason.** The gate raises a hard `ERROR`
  when `assertion.review.status == rejected` but neither `lifecycle.reason`
  nor the most recent `provenance.review_history[]` entry supplies a reason.
- **The default `all` consumer view excludes rejected claims.** Rejected
  assertions surface only in `exports/knowledge.rejected.json`; `all` becomes
  "active and not rejected". Consumers who want the full audit set read the
  rejected view.
- **Reopen is explicit and human-only:** `rejected → unreviewed/proposed`
  via a new review command that records a human reviewer + reason; direct
  `rejected → reviewed/canonical` remains forbidden.
- **No existing canonical content needs editing.** The four
  `assertion.status: deprecated` connections are materialized-inverse repairs,
  not rejections; they stay deprecated.

## 0.2 Open decision threads (decision grid)

### Decided: T1 — Relation registry in export (2026-09-06)

Decisions recorded during the review refinement phase and **implemented on
2026-09-06 (ADR-0032, contract 2.1.0)**:

1. **Additive optional top-level sidecar.** `exports/knowledge.json` gains
   `relation_registry_version` and `relation_registry`; both are optional so
   `2.0.x` consumers keep working.
2. **Include controlled vocabularies in the same bump.** Add
   `vocabularies` (`domains`, `subdomains`, `regimes`, `scales`) alongside the
   relation registry.
3. **`export_version` minor bump `2.0.0 → 2.1.0`.** `schema_version` stays
   `1.x`; canonical object schemas are unchanged.
4. **Adapter fails closed when the registry is present.** If a published export
   carries `relation_registry`, the adapter rejects any connection whose
   `relation` is not a registered relation. If the field is absent (old `2.0.x`
   export), the adapter keeps its current literal-name behavior but cannot
   introspect semantics.
5. **Adapter surface gains relation introspection:** `relations()`,
   `relation(name)` (family, inverse, transitive, symmetric, domain, range,
   status), plus a fail-closed `validate`/`load` path.
6. Tests: byte-identical regeneration with the new members; adapter discovers
   `mathematically_required_by` as the inverse of `mathematically_requires`;
   adapter rejects an unknown relation; old `2.0.x`-shaped export without the
   registry still loads.

**Consequences implemented:** `schema/export.schema.json` (optional members),
`scripts/validate.py` (emit registry + vocabularies), the first-party adapter
(`loader.py` fail-closed + `client.py`/`server.py`/`cli.py` introspection),
`docs/CONSUMERS.md`, `docs/VERSIONING.md`, `docs/MIGRATIONS.md`, ADR-0032
(export contract 2.1.0), `tests/versioning/`, `adapters/python/tests/`.
`scripts/graph_analysis.py` and derived-policy views were NOT changed — they
inherit the sidecar from the export they read, and the exported artifacts are
regenerated byte-identically sidecar-inclusive.

### Decided: T2 — Machine-readable validator (2026-09-06)

Decisions recorded during the review refinement phase and **implemented on
2026-09-06 (ADR-0033)**:

1. **Report shape: both.** `reports/validation-report.json` keeps a single
   `results[]` array with a per-item `severity` (`ERROR`/`WARNING`/`INFO`,
   `rule`, `focus`, `message`), **and** adds convenience arrays `errors[]`,
   `warnings[]`, `info[]` plus `severity_counts`.
2. **Fold `integrity_anomalies.py` into `verify_all.py` as advisory.** It gains
   exit-code and report integration, but its `ERROR`s remain non-fatal
   (structural/analytical anomalies are surfaced, not gate-blocking), except
   where a rule is explicitly promoted to a validator error.
3. **Add `--json` to `scripts/validate.py`** so CI and agents can consume the
   structured result without parsing stdout (exit `0`/`1` retained).
4. Existing `validate.py` warnings (e.g. confidence-without-basis) become
   first-class `warnings[]` entries rather than stderr-only.

**Consequences implemented:** `scripts/validate.py` (report writer + `--json` +
warning collection), `scripts/integrity_anomalies.py` (advisory `--json`/`--strict`),
`scripts/verify_all.py` (advisory step + report-format test),
`tests/versioning/test_validation_report.py`, `docs/TESTING.md`, ADR-0033.

### Decided: T3 — Domain identity enforcement (2026-09-06)

Decisions recorded during the review refinement phase and **implemented on
2026-09-06 (ADR-0034)**:

1. **New `schema/id-domain-map.yaml`** is the single source of truth for
   `id-prefix → canonical domain name` (one index file, all prefixes).
2. **Both `epist` and `practice` map to `scientific-practice`** for now, with
   `practice`/`epist` marked legacy; a later migration to one prefix requires an
   ADR + alias migration (identity change), not this change.
3. **Hard `ERROR` gate.** Any of these is a validator failure:
   - id prefix not in `id-domain-map.yaml`;
   - prefix→domain != entity `domain`;
   - entity file path directory != mapped domain;
   - entity `domain` not in `schema/vocabularies/domains.yaml`.
4. **Fix `stemma:phys.our-environment` by relocating the file** (keep the
   immutable ID; adjust path + domain metadata to match), not by changing the
   ID. The current file is at `content/earth-space/.../our-environment.md` with
   `domain: physics`; it must move to a `physics`-tree subdomain (e.g.
   `content/physics/...`) and retain `stemma:phys.our-environment`.

**Consequences implemented:** `schema/id-domain-map.yaml`; `scripts/validate.py`
(`check_entity_domain_identity` + map coherence); relocated `our-environment.md`;
`schema/vocabularies/domains.yaml` unchanged (map is the one place codes meet
names); `docs/MIGRATIONS.md`; `tests/registry/test_domain_identity.py`; ADR-0034.

### Decided: T4 — Ingest/proposal correctness (2026-09-06)

Decisions recorded during the review refinement phase and **implemented on
2026-09-06 (ADR-0035)**:

1. **Fail closed when no real Draft seam is wired.** `ingest_to_proposals.py`
   refuses to stage a non-schema-valid placeholder; it errors and tells the
   caller to provide `--draft module:function` (or remove the CLI).
2. **Extraction metadata stays in the `CurationRequest` sidecar** (`kind`,
   `format`, `pages`, `ocr_used`, `preview`). Canonical `sources/*` records do
   not carry extraction-only fields.
3. **Gate before staging.** The staged proposal must pass the curation-pipeline
   deterministic gates before it is written under `proposals/`. The human
   Governance Gate later decides review status only.
4. `build_source_candidate()` must produce a schema-valid source object
   (`type` + required `citation`); no `relationships: []` on entity drafts; the
   dead `validate.REL_TYPES` reference is removed/replaced by registry-aware
   checks (entities carry no relationships per ADR-0028).

**Consequences implemented:** `scripts/ingest.py` (schema-valid source candidate +
`build_extraction_sidecar` + lazy PIL import), `scripts/ingest_to_proposals.py`
(fail-closed `DraftSeamError` + gate-before-stage `ProposalGateError`),
`scripts/curation_pipeline.py` (removed `validate.REL_TYPES`; entity-side
`relationships` rejected), `docs/INGESTION.md` (removed `relationships: []`
example; `--draft` documented required), `tests/curation/test_ingest.py`,
`test_ingest_to_proposals.py`, `test_curation_pipeline.py` (now in the chain),
ADR-0035 (ingest/proposal contract).

### Open threads

Recorded so the review can be continued by any agent without re-deriving the
options. Statuses stay `open` until a decision is made; once decided, the
choice moves into `0.1`-style headings or a new ADR.

| Thread | Problem | Recommended option | Option A | Option B | Option C | Decision |
|---|---|---|---|---|---|---|
| T1 Relation registry in export | Consumers cannot introspect relation semantics from the contract | **Decided (2026-09-06): additive optional top-level `relation_registry` + `relation_registry_version` + `vocabularies`; export → 2.1.0; adapter fails closed on unknown relation when registry present** | Additive optional sidecar (back-compatible) | Required member (breaking-ish) | Keep out (leave as documented gap) | **decided** |
| T2 Machine-readable validator | No single ERROR/WARNING/INFO report; `integrity_anomalies.py` outside chain | **Decided (2026-09-06): `results[]` with severity + convenience `errors[]/warnings[]/info[]`; add `--json`; wire anomalies in advisory** | Fold anomalies into the gate and fail on ERROR | Keep separate; only unify format | Leave CLI-only | **decided** |
| T3 Domain identity enforcement | id-prefix / `domain` field / path / vocabulary can disagree silently | **Decided (2026-09-06): new `schema/id-domain-map.yaml`; hard ERROR on id-prefix/domain/path/vocabulary mismatch; fix `our-environment` by relocating the file** | New id-domain-map + cross-check (recommended) | Only validate `domain` field against `domains.yaml` | Only validate path prefix | **decided** |
| T4 Ingest/proposal correctness | Ingest path emits schema-invalid source/entity candidates and relies on absent `validate.REL_TYPES` | **Decided (2026-09-06): fail closed without a real Draft seam; extraction metadata in CurationRequest sidecar; gate before staging; schema-valid source candidate** | Fail closed when no seam | Keep placeholder fallback but make it schema-valid | Remove ingestion layer until fixed | **decided** |

### T1 detail: relation registry in export

**Why this matters.** The export is the only consumer contract. Today a consumer
can read `connections[]` and see literal relation names, but cannot answer:

- Is `mathematically_requires` in the `dependency` family? Is it transitive?
- What is the legal inverse of `derived_from`?
- Are `part_of` source/target types valid for `concept`/`phenomenon`?
- Which relations are `adopted` vs `reserved`?

Without this, every consumer either hard-codes producer-side semantics or clones
the repo — exactly what the adaptor boundary is meant to prevent.

**Design options:**

1. **Additive optional top-level object (recommended).**
   `exports/knowledge.json` gains:
   ```json
   "relation_registry_version": "1.0.0",
   "relation_registry": {
     "part_of": {
       "family": "structural",
       "inverse": "has_part",
       "transitive": true,
       "symmetric": false,
       "domain": ["concept","phenomenon","model","quantity"],
       "range": ["concept","phenomenon","model","quantity"],
       "status": "adopted"
     },
     "...": { "...": "..." }
   },
   "vocabularies": { "domains": [...], "subdomains": {...}, "regimes": [...], "scales": [...] }
   ```
   - Backward compatible: old `2.x` readers ignore unknown members.
   - `export_version` minor bump `2.0.0 → 2.1.0` (additive).
   - `schema_version` unchanged (canonical object schemas don't change).
   - Adapter: when present, validate every connection's `relation` against the
     registry; expose `relations()` / `relation(name)` / families; if absent,
     fall back to current literal-name behavior (still contract-valid for 2.0.x
     exports).
   - Tests: byte-identical regeneration; adapter can discover `mathematically_required_by`
     as the inverse of `mathematically_requires`; adapter rejects a connection
     using an unknown relation; docs say old readers ignore the new members.

2. **Required member.** Stronger contract, but every consumer must reject
   2.0.x exports or accept a major contract bump (`3.0`). Not worth it until a
   real consumer depends on the field.

3. **Keep as gap.** Costs the adaptor boundary the brief is asking for; not
   recommended.

**Sub-decision: include vocabularies now or later?** `domains`/`subdomains`/
`regimes`/`scales` are equally producer-side today. Adding them in the same
additive bump is cheap and makes the contract self-describing. Recommended:
include them now.

**Open sub-questions for T1:**
- Make the registry **optional** (back-compatible) or **required** in the export?
- Include **vocabularies** in the same additive bump, or relations only?
- Should the adapter **fail closed** on an unknown relation when the registry is
  present (recommended), or warn only?

## 1. What STEMMA claims → what it actually is

| Layer | What the docs claim | What I verified |
|---|---|---|
| Vision | independent, open, curriculum-neutral, product-independent STEM foundation | Yes, strongly reinforced by governance and repo-independence tests. |
| Schema | three object kinds, minimal envelope, governed extension, JSON Schema 2020-12 | Yes, plus strict duplicate-YAML rejection, function-as-gate semantics. |
| Relationships | first-class assertions with evidence/context/provenance; relation registry | Yes, plus derives claim signatures and enforces triple immutability from git. |
| Validator | schema + identity + references + registry + vocabularies + epistemics + cycles + duplicate claims | Yes for errors; **not** a single severity-aware machine-readable result including warnings/info; no entity-domain/value identity check. |
| Exporter | deterministic, content-hash stamped, contract-validated before write | Yes. Also embeds derived `claim_signature` and review-policy views. |
| Consumer contract | `connections[]` only, pin export major, no producer dependency | Yes, and a first-party read-only adapter implements it. Gap: no relation registry in the export. |
| Lifecycle | rejected stays auditable | **No** — rejected is not a legal schema value; tooling currently emulates it with `deprecated`. |
| Domain coverage | concept, quantity, unit, law, equation, misconception, phenomenon, model, experiment | Nine types, but only 1 `unit`, 2 `equation`, 11 `law`, 0 `misconception`, and the math layer is display-only. |

---

## 2. Findings by severity

### CRITICAL

- **C1. `rejected` claim lifecycle is unrepresentable.** `curation_state.py`
  permits `rejected` transitions, `review.py` writes `review.status: rejected`,
  `apply_review_decisions.py` writes `lifecycle: {reason:..., replaced_by:null}`
  and `assertion.status: deprecated`. But `connection.schema.json` forbids
  `rejected` in `review.status` and forbids `rejected` in `assertion.status`.
  Result: a reviewer can create a file that fails the gate, or is forced to use
  "deprecated" for "wrong". This breaks the auditability the brief demands.

- **C2. Relation semantics are not published to consumers.** The
  relation-registry is canonical/producer-side only. Without it a consumer
  cannot distinguish `mathematically_requires` from `related_to`, cannot
  discover legal inverses, cannot reject unknown relations, cannot evaluate
  `domain/range`, and cannot reason about transitivity. This is the largest
  adaptor-boundary failure.

- **C3. Entity identity lacks a domain-code / path / vocabulary cross-check.**
  `stemma:<code>.<slug>`, the `domain` field, and the `content/<domain>/...`
  path can all disagree silently. One live entity already disagrees
  (`stemma:phys.our-environment` under `earth-space/`). Consumers and
  validation cannot trust the taxonomy.

### HIGH

- **H1. Machine-readable validation lacks severity semantics.** No unified
  `ERROR/WARNING/INFO` result contract; warnings/info are not in
  `reports/validation-report.json`; `integrity_anomalies.py` (which has the
  severity model) is outside the gate and never fails on ERROR.

- **H2. The export omits a relation/version/registry sidecar needed by the
  adapter.** The "known gap" is real and documented; it is not an
  over-engineering problem to close it via an additive export field.

- **H3. Canonical schema carries pedagogy-shaped entity fields**
  (`learning_objectives`, `common_misconceptions`). The docs rationalise them
  as "knowledge-layer", but they are consumer-teaching constructs. They belong
  in consumer adapters/derived views, or must be explicitly justified and
  gated as non-pedagogical.

- **H4. Evidence/source integrity is weak.** 92% of connections have no
  evidence; only 3 source records; no gate requires the provenance source
  strings to be resolvable to source records; `canonical` evidence is enforced
  only by tooling, not by the validator.

- **H5. Math/measurement layer is not data.** Display strings cannot support
  dimensional analysis, unit conversion, equation parsing, symbol
  disambiguation, or machine-checkable "this law applies here".

### MEDIUM

- **M1. Over-generic `related_to` dominates** the corpus (57%); stronger
  reserved relations are unused. Not architectural, but it caps scientific
  utility and review value.
- **M2. Ingest path produces non-valid source/entity candidates** and crashes
  on `validate.REL_TYPES` if a `relationships` list is non-empty.
- **M3. Domain-code ↔ vocabulary-name mapping is undocumented and
  un-versioned**; `scientific-practice` has two id prefixes.
- **M4. Stale hard-coded prose in generated reports and hand-written source
  inventory** causes documentation/report drift.
- **M5. The verify chain is monolithic and uses the real corpus as the only
  fixture.** It is good for integration, but there are few isolated /
  throwaway fixtures for new gate rules.
- **M6. No end-to-end vertical proof (canonical → validate → export →
  adapter → consumer model)** with negative cases exists as a single test.
- **M7. Release/publication mechanics (signed tags, IRI, hosted contract) are
  not implemented** (roadmap R6), which matters for "open-source friendly"
  and consumers pinning a contract rather than a git commit.

### LOW

- **L1. `content_trust_audit.py` is dead/stale and should be removed or wired.**
- **L2. `export.schema.json` title says v1.0 but description says v2.0.**
- **L3. Explorer "accessibility polish is not production-grade"** (documented).
- **L4. `source.schema.json` has no `provenance`/`ai_drafted` field, so the
  ingestion source candidate cannot be schema-valid even after a type fix.**

---

## 3. What is deliberately NOT worth changing

- **No graph DB / vector DB / microservices / hosted API.** Not needed.
- **No RDF/OWL as canonical store.** Not needed; the projection story in
  `docs/STANDARDS.md` is sensible.
- **No LLM inside the canonical core.** Ingestion uses a *seam*; review remains
  human. Keep it.
- **No per-type schema explosion.** One envelope per object kind is right.
- **No curriculum/grade/course tags.** The independence test is a strength.
- **No change to stable IDs.** `stemma:phys.force` etc. are the contract.

---

## 4. Comparison against modern approaches

| Approach | What would STEMMA gain | Complexity | Verdict |
|---|---|---|---|
| JSON Schema + deterministic build | validation, contracts, reproducible artifacts | low | **already adopted** |
| Reified statements / claim identity (Wikidata / RDF-star style) | one claim = one identity, evidence+qualifiers, duplicate detection | low | **already adopted** (`claim_signature`, connections) |
| Controlled relation registry | semantics, domain/range, inverse, legal names | low | **already adopted** |
| Typed graph / knowledge-graph projection | graph querying + visualisation | low-moderate | already exists as derived `knowledge.extended.json` |
| PROV-O-style provenance | agent/activity/review separation | medium | conceptually aligned; not needed as canonical RDF |
| SHACL | external validation of an RDF projection | medium | roadmap R4; not needed for authoring gate |
| Content-addressed / versioned datasets | reproducibility, integrity | low | **already adopted** (`content_hash`) |
| Data contracts | explicit consumer boundary | low | **already adopted** (`export.schema.json`) |
| Ontology / OWL reasoning | entailment, classification | high | rejected; human disagreement + review semantics are the requirement |
| Graph database | faster graph queries at scale | high | delayed until real need |
| Vector/embedding index | RAG retrieval | high | derived-only, never canonical |
| Public IRI + JSON-LD release | web-scale interop | medium-high | step 2, after domain/org decision (open human gate) |

---

## 5. Things the re-architecture brief itself under-specifies

The user asked me to state what the prompt is missing. These are the things a
senior knowledge-systems architect would add to the brief:

1. **The distinction between "currently accepted" and "historically true".**
   STEM is full of superseded theories. The brief lists `supersedes` and
   temporal validity but does not ask for a science-evolution model: when did a
   claim hold, when was it replaced, is the old claim still true *in its
   regime*? STEMMA currently has no way to say this without a host of
   `validity` dates on every connection.

2. **A knowledge-kind taxonomy.** Definitional/axiomatic, empirical,
   theoretical, model-based, derived, historical — these have different
   evidence standards and different trust semantics. The brief's `Entity /
   Claim / Evidence / Source` list stops short of this; `assertion.type`
   (`proposed/asserted/inferred`) does not capture it.

3. **The two provenance layers.** Record provenance (who wrote the file, which
   process migrated it) must stay separate from scientific provenance (who
   first stated/measured it). The repo already has `historical`; the brief
   treats provenance as one concept and could accidentally conflate them.

4. **Quantities, units, dimensions, and equations as first-class machine
   structures.** The brief mentions quantities/units but not the *calculus*
   around them: symbol binding, dimensional consistency, unit equivalence,
   equation parsing, scope of a law, unit-system policy. This is the most
   scientifically consequential under-specified part.

5. **How the taxonomy (domains/subdomains) is governed and versioned.**
   The brief assumes a hierarchy but not who may add `earth-space` or
   `scientific-practice`, or when adding a subdomain is a contract change.

6. **The human review bottleneck is the real product.** The brief treats
   "build a validator" as the focus, but 604/654 assertions are unreviewed and
   0/224 entities are human-reviewed. Without a review/scaling/diff-review
   design, the system is a beautifully validated graph of unverified science.
   The brief should name "review activation" as co-equal to schema integrity.

7. **What "canonical" means for disagreement and competing evidence.** You
   can have two humans disagree. The brief says `contradicts` but not how to
   represent ranked/preferred/normal, how consumers resolve conflicting
   canonical assertions, or how disputes are reopened.

8. **Licensing / attribution provenance of content contributions.** CC BY 4.0
   requires share-alike attribution, but there is no per-contribution
   attribution schema or contribution-openness expectation. Open-source
   governance also needs maintainer roles, contribution CLA, and Code of
   Conduct, none of which are architecture but all of which are needed for a
   durable open project.

9. **Consumer-contract evolution policy in practice.** How does a consumer
   distinguish "same fact, new review" (content hash changes) from "will my
   queries still work"? `content_hash` and contract majors help, but there is
   no written policy for backfill/supersession affecting a consumer's cached
   curriculum.

10. **A "no canonicalization without evidence" gate.** The brief wants
    provenance integrity; the repo currently only checks it in the review
    path, not in the gate.

---

## 6. Proposed target architecture (smallest justified version)

Keep the current files-first, git-based, contract-on-file architecture. Do
**not** introduce a database or ontology stack. Move the canonical content
model into an **explicit "canonical truth → validated representation →
deterministic export → consumer adaptor"** pipeline with a strictly additive
contract surface.

```
    content/  connections/  sources/       (canonical, in git)
        │         │            │
        ▼         ▼            ▼
   [ gate: validate + severities + registry + identity + lifecycle ]
        │
        ▼
   exports/knowledge.json        (contract; now includes relation registry + versions)
        │
        ▼
   consumer adaptor (validates contract; can introspect relations)
        │
        ▼
   consumer domain model (curriculum, UI, pedagogy, RAG, etc.)
```

Concrete target changes (if the review is approved):

1. **Add `rejected` as a legal lifecycle state** in
   `connection.schema.json` (`assertion.status` and/or
   `assertion.review.status`), align `curation_state.py`, `review.py`,
   `apply_review_decisions.py`, `CURATION-PROTOCOL`, validator enums + tests.
   This is an additive schema change → ADR + version bump + migration note.

2. **Embed the relation registry + versions in the export.** Add
   `relation_registry` and an explicit `versions` object to
   `exports/knowledge.json` (additive; export version 2.1.0). Validate via
   export schema; make adapter introspect families/inverses/transitivity.
   This closes the documented ADR-0030 gap.

3. **Make validation output severity-aware and machine-readable.**
   `reports/validation-report.json` gains `errors[]`, `warnings[]`, `info[]`
   with deterministic severities. Add `--json`/structured output to the gate so
   CI and agents consume one artifact. Wire `integrity_anomalies.py` into the
   chain (or fold it in) and make `ERROR` non-blocking only where documented.

4. **Cross-check entity domain identity.** Validate the id prefix against a
   new `schema/id-domain-map.yaml` (or the existing domains vocabulary with a
   code map), the `domain` field against `domains.yaml`, and the on-disk path
   against the declared domain. Fix the `phys.our-environment` mismatch. This
   is a self-contained validator + vocabulary addition.

5. **Clarify (and where justified remove) pedagogy-shaped canonical fields.**
   The safe first step is to stop treating `learning_objectives` /
   `common_misconceptions` as canonical truth: keep them as *governed
   extensions* or move them to consumer-side derived views. This requires an
   ADR because it changes the entity schema contract, even if additive.

6. **Fix the ingest/proposal path to be schema-valid.** `build_source_candidate`
   must produce a source with a valid `type` and `citation`; entity drafts must
   not contain `relationships`; remove/replace the `validate.REL_TYPES`
   reference. Add a negative test that the ingest path never writes canonical.

7. **Add a vertical end-to-end proof.** A test that creates a tiny canonical
   entity + connection, validates it, builds a deterministic export, reads it
   through the adapter, projects it into a minimal consumer "lesson/prerequisite"
   model, and verifies negative cases (unknown relation, dangling ID, invalid
   review transition, non-deterministic export).

8. **Add environment-local agent skills + AGENTS.md contract.** Create
   `.agents/skills/` (or `docs/agent-skills/`) with the five practical
   skills requested, plus a concise `AGENTS.md` "how to work on STEMMA"
   contract. Keep them tied to the real gate commands and invariants.

9. **Prune stale/dead artifacts and fix drift.** Remove/repair
   `content_trust_audit.py`, fix hard-coded report/count prose, fix
   `docs/INGESTION.md` example, fix `export.schema.json` title, and make
   `docs/SOURCES.md` reflect (or link to) live generated counts.

10. **Write the durable ADRs** for any of the above that touch contracts,
    lifecycle/identity, or export versioning (at minimum: lifecycle rejected
    state, relation-registry-in-export, validation report severity, entity
    domain identity, and canonical-vs-pedagogy boundary).

---

## 7. Explicitly out of scope for this iteration (to avoid over-engineering)

- RDF/OWL/JSON-LD canonical store.
- Graph/vector databases, hosted API, auth, microservices.
- Internal AI agents in canonical code.
- Recommendation/curriculum/pedagogy generation.
- Multilingual content (identity is already language-independent).
- Full `related_to` → specific-relation corpus migration (huge curation task;
  the registry and review campaign already enable it).

---

## 8. Verification plan

Every implementation step must be enforced by the existing chain mindset:

1. Add/modify the gate rule **and** a deterministic test that fails when the
   rule is violated.
2. Update `docs/IMPLEMENTATION-STATUS.md`, `docs/MIGRATIONS.md`, and the
   relevant specification.
3. Run `python3 scripts/verify_all.py` (green) and `git diff --exit-code
   -- exports reports`.
4. For export/contract change, bump `schema/VERSION.yaml`, update
   `docs/CONSUMERS.md`, and update `adapters/python/tests/test_adapter.py`.

---

## 9. Recommendation

The architecture is sound and close to the conceptual target. The highest-value
next work is **not** a rewrite:

> close the lifecycle-state and relation-registry gaps, make validation
> machine-readable and severity-aware, harden entity domain identity, fix the
> broken ingest/proposal path, and add the reusable agent skills + a vertical
> end-to-end proof.

All of that is additive and governable, and it will make STEMMA safe for an
independent consumer and a future agent to extend without the original
architect present.
