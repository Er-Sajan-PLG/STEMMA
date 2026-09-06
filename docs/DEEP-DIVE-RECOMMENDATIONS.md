# STEMMA — Deep-Dive Recommendations (whole-repository review)

**Status:** Review artifact — no canonical data/schema/exports changed.
**Date:** 2026-09-06
**Companion to:** `docs/SOTA-REVIEW.md` (findings + decided threads),
`docs/ARCHITECTURE.md` (authoritative implemented system).
**Evidence base:** full `verify_all.py` green (23 steps), corpus-level inspection
of all 224 entities / 654 connections / 3 sources, schema/registry/validator
reading, and the ADR history.

---

## 0. The one-sentence recommendation

> **STEMMA's architecture is already the right shape. Stop building substrate;
> start turning the existing validated graph into actual reviewed, machine-usable
> science. Do that by (1) closing the five decided contract/validator gaps, then
> (2) spending the bulk of energy on review activation and the math layer — the
> two things that make the corpus trustworthy and useful.**

Everything in this document is an *additive*, gate-backed, file-based change.
No graph DB, no RDF/OWL, no microservices, no API server, no vector store.

---

## 1. Confirmed strengths (do not touch)

- Three canonical object kinds + reified connection assertions.
- Relation registry with family / inverse / transitivity / domain-range /
  adopted-vs-reserved; inverse coherence checks.
- Deterministic gate (`validate → export contract check → write`).
- Git-history identity + connection-triple immutability guards.
- Human-only review state machine + campaign worksheets.
- First-party read-only adapter + consumer-owned explorer.
- Repository independence + curriculum-neutrality gates.
- Content hashes / claim signatures / no wall-clock determinism.

---

## 2. Decided items — what to build and how (implementation guidance)

These are recorded in `docs/SOTA-REVIEW.md` §0.1/§0.2. Recommended build order
and design specifics:

| # | Item | Build this | Contract effect | Gate/test |
|---|---|---|---|---|
| 1 | **Relation registry + vocab in export** | Add optional `relation_registry`, `relation_registry_version`, `vocabularies` to `knowledge.json` | export 2.1.0 (additive); schema unchanged | export schema + adapter fail-closed + introspect API — **done (ADR-0032)** |
| 2 | **Rejected lifecycle** | Add `rejected` to `assertion.review.status`; keep `assertion.status` for record retirement; reject requires reason (`ERROR`); `all` excludes rejected; reopen command | schema 1.0.0 → 1.1.0; export stays 2.1.0 (list only, no shape change) | validator + `graph_policy` + review tools + adapter — **done (ADR-0031)** |
| 3 | **Machine-readable validator** | `results[]` with `severity`, plus `errors[]/warnings[]/info[]` + counts; `--json`; fold `integrity_anomalies.py` advisory | report contract only | report tests + `verify_all` step — **done (ADR-0033)** |
| 4 | **Domain identity** | `schema/id-domain-map.yaml`; hard ERROR on id-prefix/domain/path/vocabulary mismatch; relocate `our-environment` | vocabulary contract; content path fix | validator + repo test — **done (ADR-0034)** |
| 5 | **Ingest/proposal** | schema-valid `source` candidate; no `relationships`; remove `validate.REL_TYPES`; fail closed without Draft seam; gate before staging | ingest contract only | `test_ingest.py` negative cases — **done (ADR-0035)** |

**Recommended sequencing:** 1 → 2 → 3 → 4 → 5 (approved order). Do **1** first
because it is pure additive export value and makes the adapter boundary real;
**2** second because it is a correctness bug in the authoring path; **3** is the
harness that makes 4/5 testable in a clean way; **4/5** then slot in with the
new report.

---

## 3. Remaining threads (deep dive + recommendation)

### R1 — Canonical vs pedagogy boundary

**Evidence.** `learning_objectives` on 218/224 entities, `common_misconceptions`
220/224, `real_world_applications` 220/224, `key_experiments` 220/224. The
generality test only checks for grade/curriculum/country scoping **claims**, not
for instructional-shaped fields.

**Assessment.** `common_misconceptions`, `real_world_applications`,
and `key_experiments` are defensible as *knowledge-layer contextual facts*
(a false belief, an application, an experiment). `learning_objectives` is the
one that is genuinely pedagogical: "what a learner should be able to do" is a
teaching intent, not a scientific fact.

**Recommendation.**
- **Now:** keep the fields, but amend `DOMAIN-MODEL`/`SCHEMA-SPECIFICATION` with
  a strict boundary rule — these fields may describe scientific facts,
  applications, misconceptions, and experiments, but must never contain
  instructional sequencing, grade/level, or "should be able to".
- **Near-term (after export 2.1 lands):** add an ADR to **remove
  `learning_objectives` from the canonical entity** (schema major 2.0 and export
  major 3.0 when the corpus is ready). Consumers derive learning objectives from
  relationships and context. This is a deliberate breaking change best done
  while all 224 entities are still `draft`.
- **Do not:** convert all four to extension fields now (noisy, low value), or
  delete `common_misconceptions` (it is knowledge).

### R2 — Evidence / source integrity

**Evidence.** 599/654 connections have empty `evidence`; only 3 source records;
49 evidence items carry a `source_ref`; all 50 canonical connections do have
evidence (tooling currently enforces this at canonicalization, not the gate).

**Assessment.** This is the largest *honesty* gap. A canonical claim with no
evidence is unsupported by construction. The fix belongs in both the gate and
the curation pipeline.

**Recommendation.**
- **Validator ERROR:** `review.status == canonical` requires ≥1 evidence item
  **or** an explicit axiomatic marker
  (`evidence: [{type: other, description: "axiomatic"}]`) with a documented
  reason. This closes the "direct edit can mark canonical without evidence" hole.
- **Validator WARNING (not error):** any **active** connection with empty
  evidence — surfaces the 599 for review without blocking draft ingestion.
- **New derived report** `reports/academic-sources.json`: the set of
  `provenance.source` strings on entities (44 distinct) that have no
  `sources/*.yaml` record, plus evidence `source_ref` gaps. Not a gate failure;
  it drives backfill.
- **Roadmap:** backfill source records from those 44 strings.

### R3 — Math / measurement layer

**Evidence.** 54 quantities, 11 laws, 2 equation entities, **1 unit entity**;
104 entities carry an `equation` string, 89 a `symbol`, 57 a `unit`; the only
`dimensions`/`symbol_set` extension use is on `phys.newtons-second-law` (a law —
the wrong type). ADR-0024 is already a strong, detailed proposal.

**Assessment.** This is the highest *scientific value* gap, and ADR-0024 is the
right design. It is also the biggest work item. It should not be rushed into the
same pass as the contract fixes.

**Recommendation.**
- **Decide ADR-0024 as `decided`** with these three adjustments:
  - Use `math.equations[]` as a list (SUVAT needs four equations); keep the
    first as canonical and the rest as variants.
  - Allow half-integer exponents (empirical `√` laws).
  - Use `math.*` for machine truth and keep `equation`/`symbol`/`unit` strings as
    **derived display** during transition; add `unit_ref` inside `math`.
- **Implement in 3 phases**, each gate-backed:
  1. **Schema + validator** (`math`, `dimensions` on `quantity`/`unit`, `unit_ref`,
     symbol bindings, small LaTeX subset). This is ~300 lines + tests.
  2. **Pilot backfill** mechanics (20 quantities, 5 laws, ~12 SI units) to prove
     the validator and the dimensional check.
  3. **Expand** to electricity/magnetism, thermodynamics, chemistry quantities.
- **Do not** import QUDT/UCUM as canonical; they stay `external_ids`.

### R4 — Relation vocabulary genericity

**Evidence.** `related_to` = 371/654 (56.7%); **0 canonical** `related_to`; 61 of
314 `related_to` pairs *also* have a specific relation (redundant); the registry
already reserves `causes`, `contributes_to`, `explains`, `measures`, `quantifies`,
`expressed_in`, `equivalent_to`, etc.

**Assessment.** This is not an architecture defect — `related_to` is the honest
fallback — but it caps reasoning value. Reclassifying is curation, not tooling.

**Recommendation.**
- Add a **derived** `reports/relation-triage.json` (not a gate) that groups:
  - `related_to` edges on dependency-family pairs (likely should be
    `requires`/`mathematically_requires`),
  - `related_to` edges where the pair already has a specific relation,
  - `related_to` edges on measurables (`quantity`↔`unit`, `quantity`↔`quantity`).
- Add a **WARNING** (not error) when `related_to` is the *only* edge between two
  entities and there is a reserved relation whose domain/range fits. This
  surfaces candidate reclassification without blocking.
- **Do not** bulk-relabel anything; humans review the triage and supersede.

### R5 — Domain / taxonomy governance

**Evidence.** `content/earth-space/...` contains one `phys:`/`physics` entity
(`our-environment.md`); `scientific-practice` has two id prefixes (`epist`,
`practice`); `domains.yaml`/`subdomains.yaml` are not versioned; connection
`context.subdomain` is checked, entity `subdomain` is not a field.

**Assessment.** Domains are a contract surface for consumers, but they are
currently an unversioned, unvalidated file.

**Recommendation.**
- Add `version` to `domains.yaml`/`subdomains.yaml`/`regimes.yaml` (or a single
  `vocabulary_version` in `schema/VERSION.yaml`) and require an ADR to add a
  domain/subdomain/regime.
- Add optional `subdomain` to the entity schema (validated against vocabulary),
  and export it (already planned in the `vocabularies` sidecar). This gives
  consumers a structured taxonomy without relying on paths.
- Extend the T3 domain-identity `ERROR` check to bind `path<->subdomain`
  vocabulary too.
- Keep `epist`/`practice` as legacy (decided); future unification is an ADR.

### R6 — Review activation (the actual bottleneck)

**Evidence.** 0/224 entities human-reviewed; 0 connections in `reviewed`-only;
604/654 connections unreviewed; 50 canonical; 4 campaign batches for dependency
edges only.

**Assessment.** The gate is excellent, but the *product* is a validated graph of
mostly unverified science. The single most valuable non-infrastructure work is
review activation.

**Recommendation.**
- **Extend review tooling to entities.** There is a state machine for connection
  `review.status`, but only entity `status` (`draft → machine_validated →
  human_reviewed → canonical`) with no `review.py` command and no human-generated
  transition history. Add `scripts/review_entity.py` (or `review.py entity ...`)
  using the existing `provenance.reviewer`/`reviewed_at` fields.
- **Add an entity review campaign** analogous to
  `dependency_review_campaign.py`, prioritizing by centrality/domain coverage
  (start with the 5–10 seed concepts per domain).
- **Publish a review-coverage report** per domain/entity type in
  `reports/curation-status.json`.
- **Do not** auto-canonicalize entities; keep the human-only rule.

### R7 — Publication / release

**Evidence.** No release tags, no signed artifacts, no IRI decision
(ADR-0029 open), `VERSION` 3.0.0.

**Assessment.** Consumers can pin the repo, but "open-source friendly" really
wants a published contract + releases. This is deliberately deferred in the
roadmap (R6), and much of it is gated on the IRI decision.

**Recommendation.**
- **Now:** add a `scripts/release_check.py` that verifies `verify_all.py` green,
  `git diff --exit-code -- exports reports`, single-sourced versions, MIGRATIONS
  current, `VERSION` bumped, and prints a conventional-changelog summary.
- **Delay:** signed git tags, GitHub releases, published IRIs, JSON-LD
  projection — until the domain/IRI human decision (ADR-0029 open item).

### R8 — Dead / stale artifacts

**Evidence.** `content_trust_audit.py` references `review-queue-v0.2.json`,
`integrity-anomalies-v0.2.json`, `knowledge.compat-0.1.json`; `epistemic_summary.py`
and `curation_status.py` print hardcoded "397"/"15"/"382"/"v0.2" in generated
prose; `docs/SOURCES.md` hardcodes 149/40 counts; `export.schema.json` title says
v1.0.

**Assessment.** Mostly harmless, but they mislead readers and agents.

**Recommendation.**
- **Delete** `scripts/content_trust_audit.py` (not in the chain, dead).
- **Remove hardcoded prose counts** from `epistemic_summary.py` and
  `curation_status.py`; compute them or drop the editorial note.
- **Update `docs/SOURCES.md`** to say the counts are live-derived or to point at
  the generated report; add a docs-consistency test that the file doesn't
  hardcode stale numbers.
- Fix `export.schema.json` title.

---

## 4. Cross-cutting items the original brief under-specified (and recommendations)

| Gap | Recommendation | Effort |
|---|---|---|
| Currently-accepted vs historical truth | Keep `validity` + `lifecycle`; for theory evolution use `supersedes`/`approximates` relations and document that an old claim stays true in its regime. Don't add a new temporal graph now. | low |
| Knowledge-kind taxonomy | Don't add an enum. `assertion.type` + relation family + evidence type already convey definitional/empirical/theoretical/model. Document it. | low |
| Two provenance layers | Already covered by `historical` (scientific origin) vs `provenance` (record origin). Add a test that `historical` never carries record fields. | low |
| Disagreement / competing claims | Keep `contradicts`/`inconsistent_with`/`competes_with` reserved; a later `preferred/normal/deprecated` statement-rank can be added as an ADR if real cases appear. | medium, deferred |
| Contribution licensing / attribution | Keep CC BY 4.0 / MIT; add a "contributor attribution" note to `CONTRIBUTING.md` (who authored, when, source). No schema change. | low |
| Consumer-contract evolution policy | Already largely covered by `content_hash` + major pinning; add a short `docs/CONSUMERS.md` statement that `content_hash` changes with content, contract majors change only on breaking shape change. | low |
| "No canonicalization without evidence" | R2 gate `ERROR`. | low |
| Human review co-product | R6. | medium |

---

## 5. Prioritized build roadmap

### Phase A — contract/validator hardening (highest value, lowest risk)
1. T1 relation registry + vocabularies in export (export 2.1.0). ✅ done (ADR-0032)
2. Rejected lifecycle (schema 1.1.0, authoring correctness). ✅ done (ADR-0031)
3. Machine-readable validator report + `--json`. ✅ done (ADR-0033)
4. T3 domain identity (`id-domain-map.yaml`, fix `our-environment`). ✅ done (ADR-0034)
5. T4 ingest correctness (fail-closed, schema-valid proposals). ✅ done (ADR-0035)

### Phase B — trust and review activation (the product)
6. Human-in-the-loop ingestion/review webapp (upload → extract → LLM Draft → review → staged proposal; canonical untouched). ✅ done (ADR-0036)
7. R2 evidence gate + source backfill report. ✅ done (ADR-0037)
8. R6 entity review tooling + entity review campaign + coverage report. ✅ done (ADR-0037)
9. R4 relation-triage report + advisory warning (derived, not gating). ✅ done (ADR-0037)

### Phase C — scientific substance
10. R3 ADR-0024 decision + math schema/validator + mechanics pilot.
11. R5 taxonomy versioning + entity `subdomain` (rides with T1 vocabularies).

### Phase D — hygiene (small, parallel)
12. R8 dead/stale cleanup.
13. R7 release-check script.
14. Documentation + ADRs + the requested **agent skills / AGENTS.md contract** +
    **end-to-end vertical proof**.

---

## 6. What to deliberately NOT do

- Do **not** introduce a graph/vector DB, hosted API, microservices, or
  recommendation system.
- Do **not** move to RDF/OWL as canonical store.
- Do **not** bulk-relabel `related_to`.
- Do **not** auto-canonicalize entities or connections.
- Do **not** import QUDT/UCUM or another unit ontology as canonical truth.
- Do **not** remove stable IDs or change already-migrated identity.

---

## 7. Acceptance criteria for the deep dive

When the recommendations land:

- `python3 scripts/verify_all.py` stays green using the **same** chain.
- `git diff --exit-code -- exports reports` is clean after regeneration.
- Every contract change bumps `schema/VERSION.yaml` and adds an ADR +
  `MIGRATIONS.md` entry.
- There is at least one **negative test** per new gate rule.
- A new agent can read `AGENTS.md` + `docs/DEEP-DIVE-RECOMMENDATIONS.md` +
  `docs/SOTA-REVIEW.md` and implement a new canonical concept or gate rule
  without the original architect present.
