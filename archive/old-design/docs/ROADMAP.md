# STEMMA — Roadmap

**Status:** Authoritative forward plan (baseline 3.0.0 + physics-first amendment ADR-0040/0041/0042, 2026-09-21).
Rebuilt from the current architecture and measured repo state; historical plans are retired.
Each phase requires explicit activation in governance (a phase listed here is
*planned*, not authorized by existing).

**Evidence for "done" claims:** `docs/IMPLEMENTATION-STATUS.md`.
**Current focus:** `docs/PHYSICS-FIRST-IMPLEMENTATION-PLAN.md` — depth-first physics core.

---

## R1 — Physics-Core v0.1 (NOW — depth-first vertical slice)

*Prove the engine works with highest-consensus science before breadth.*

This is ADR-0040 physics-first strategy. The repo is at 0 entities after refoundation — ideal for depth-first.

- **Scope:** Physics only: `mechanics`, `electricity-magnetism`, `thermal-physics` + `measurement-units` for units. ~70 entities (28 quantities, 20 units, 15 laws, 5 equations, 7 concepts/models), ~150 connections, 5 canonical sources (Halliday Resnick Walker 12th, Griffiths EM 4th, Schroeder Thermal, NIST SI Brochure, CODATA 2022).
- **Schema profile:** Minimal per ADR-0041 — required + `symbol`/`equation`/`unit` + `external_ids`/`historical`/`examples`. Forbidden for physics/: `learning_objectives`, `real_world_applications`, `key_experiments`, `common_misconceptions` (policy enforced by `physics_core_profile_check.py`).
- **Relation minimal set:** 7 adopted only per ADR-0042 — `mathematically_requires`, `derived_from`, `appears_in_law`, `applies_to`, `generalizes`/`special_case_of`, `part_of`, `approximates`. Zero `related_to` in physics/. Canonical direction rule: law -> quantity via `mathematically_requires`.
- **Evidence:** Every connection >=1 evidence with `source_ref` + locator (textbook page/section). No empty evidence.
- **Review:** 1 domain expert, campaign via `dependency_review_campaign.py --domain physics`. Worksheet prioritizes base quantities (mass, length, time) -> derived -> laws.

**Exit:**
- `verify_all.py` exit 0
- `exports/knowledge.json` v2.1.0 has 70 physics entities, 150 connections, 5 sources, embedded relation_registry
- `physics_core_profile_check.py` passes
- Explorer shows connected DAG, not isolated dots
- Adapter: `search?q=force&domain=physics` returns closure (force requires mass, acceleration)
- 100% entities human_reviewed, 100% connections canonical

## R2 — Math & Semantics Layer for Physics (NOW, gated by ADR-0024 decision)

*Physics without machine math is prose. Activate ADR-0024 partially.*

- Decide ADR-0024 with 3 adjustments from DEEP-DIVE R3: allow `math.equations[]` list (SUVAT), half-integer exponents, `unit_ref` field name.
- Implement validator: small LaTeX subset parser (~300 lines) + dimensional type-check: both sides of `=` same dimension vector.
- Backfill mechanics pilot: 20 quantities + 5 laws + 12 units with `math: {latex, symbol_bindings}`, `dimensions: {L,M,T,...}`, `unit_ref: stemma:unit.xxx`
- Retire display strings `equation`/`symbol`/`unit` to derived status (regenerated from math + units)
- Promote extension-registry `dimensions` string to deprecated

**Exit:** Dimensional errors are CI failures for physics core; 20 quantities dimensionally checked; `math_render` derived in export.

## R3 — Review activation (generic, after physics-core proves pattern)

*The architecture exists to make human-governed knowledge possible; review is the product.*

- Apply physics-core pattern to next domains: chemistry foundations, then biology, etc.
- Reviewer identity policy (ORCID-backed recommended) — human gate.
- Grow source records to cover citations actually used.

**Exit:** reviewed fraction >50% of active assertions; ≥1 domain fully reviewed (physics will be first).

## R4 — Schema & identity hardening (completing the foundation)

## R3 — Schema & identity hardening (completing the foundation)

- Resolve the public IRI / schema `$id` base decision — **human gate
  (ADR-0029 open item)**.
- Formalize alias/deprecation discovery tooling for consumers (e.g.
  `resolve(id)` across aliases).
- Statement-rank-style preferred/normal/deprecated claim semantics if
  competing-claim cases emerge (Wikidata pattern).

## R4 — Interoperability projections

- JSON-LD 1.1 context + graph projection; SKOS mapping for
  hierarchical/associative relations.
- SHACL shapes for the RDF projection (validate-with-standard-tools story).
- Optional nanopublication-style signed bundles for canonical releases.

## R5 — Developer & consumer ecosystem

- **Shipped:** first-party read-only Python adapter (`adapters/python/`) with
  SDK, CLI, and local JSON API.
- Adapter `1.0` promotion and any PyPI publication remain explicit human
  release decisions.
- `docs/CONSUMERS.md` expansion with adapter examples in > 1 language.
- CLI packaging of the gate (`pipx`-able) so consumers validate without
  cloning the repo.
- Example curriculum-mapping consumer (owned outside canonical data) as a
  reference for the mapping pattern.

## R6 — Publication & release discipline

- Signed git tags + GitHub releases per content snapshot; changelog from
  conventional commits.
- Published artifacts + integrity manifest (hashes over exports).
- Content-release cadence policy (independent of contract versions).

## R7 — Production hardening

- Scale review tooling (bulk review UX, diff-based review queues).
- Corpus growth program (domain-by-domain, review-first).
- Observability of corpus health (drift, staleness, coverage dashboards from
  existing reports).

## R8 — Advanced capabilities (gated, ordered by need)

- Multilingual content model (identity is already language-independent).
- Inference layer activation (derived claims from registry rules, clearly
  marked `inferred`).
- Retrieval/RAG support artifacts (derived, versioned, never canonical).

---

## Explicitly not on the roadmap

Hosting/APIs/auth/payments, product features, curriculum authoring, a
general-purpose ontology, canonical embeddings, any database as source of
truth. These are permanent boundaries (VISION non-goals), not deferred work.

## Sequencing rationale

R1 precedes everything: unreviewed content weakens every downstream promise.
R2 is the largest scientific-value gap. R3 must land before R4/R6 (stable
IRIs make projections and releases durable). R5 can proceed in parallel from
R3. R7/R8 follow real demand, not speculation.
