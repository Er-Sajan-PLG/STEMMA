# STEMMA — Roadmap

**Status:** Authoritative forward plan (baseline 3.0.0). Rebuilt from the
current architecture and measured repo state; historical plans are retired.
Each phase requires explicit activation in governance (a phase listed here is
*planned*, not authorized by existing).

**Evidence for "done" claims:** `docs/IMPLEMENTATION-STATUS.md`.

---

## R1 — Review activation (the core value)

*The architecture exists to make human-governed knowledge possible; review is
the product.*

- Review the 604 unreviewed assertions via the dependency campaign cadence.
- First entity reviews (224 drafts → reviewed/canonical for seed domains).
- Reviewer identity policy (ORCID-backed recommended) — human gate.
- Grow source records to cover the citations actually used by evidence.

**Exit:** reviewed fraction > 50% of active assertions; ≥ 1 domain fully
reviewed.

## R2 — Math & semantics layer (the subject-matter gap)

- Decide ADR-0024 (LaTeX equations, symbol→quantity bindings, ISQ dimensions
  on quantities, unit entities) — **human gate G-C**.
- Backfill quantities/laws; retire display-string fields to derived status.
- Dimensional-consistency checks as gate rules.

**Exit:** machine-checkable equations on all `quantity`/`law` entities.

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
