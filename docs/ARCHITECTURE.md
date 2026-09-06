# STEMMA — System Architecture

**Status:** Authoritative (baseline 3.0.0, ADR-0029).
**Related:** `docs/VISION.md` (why), `docs/SCHEMA-SPECIFICATION.md`,
`docs/RELATIONSHIP-SPECIFICATION.md`, `docs/METADATA-SPECIFICATION.md`,
`docs/PIPELINES.md` (how data flows), `docs/TESTING.md` (how it is enforced).

---

## 1. The system in one picture

```
                        ┌─────────────────────────────────────────────────┐
                        │  CANONICAL LAYER (source of truth, in git)      │
                        │                                                 │
                        │  content/**.md        entities (MD + YAML)      │
                        │  connections/*.yaml   first-class assertions    │
                        │  sources/*.yaml       citation records          │
                        └───────────────┬─────────────────────────────────┘
                                        │
                        ┌───────────────▼─────────────────────────────────┐
                        │  GATE (deterministic, zero-trust)               │
                        │  scripts/validate.py                             │
                        │  · schema conformance (JSON Schema 2020-12)     │
                        │  · identity, references, registry coherence     │
                        │  · epistemic rules (review, confidence, cycles) │
                        │  · duplicate-claim detection (claim signatures) │
                        │  · export validated against its own contract    │
                        └───────────────┬─────────────────────────────────┘
                                        │  (only if the gate passes)
                        ┌───────────────▼─────────────────────────────────┐
                        │  DERIVED LAYER (regenerable, never authoritative)│
                        │  exports/knowledge.json          the contract    │
                        │  exports/knowledge.{policy}.json review views    │
                        │  exports/knowledge.extended.json inverses+closure│
                        │  reports/*                       operational     │
                        └───────────────┬─────────────────────────────────┘
                                        │
              ┌─────────────────────────┼──────────────────────────┐
              ▼                         ▼                          ▼
      first-party tools         external consumers          future derived
      explorer/ (graph viz,     curricula, apps, AI          indexes, embeddings,
      reads ONLY the export)    systems (via the export)     RDF/JSON-LD projections
```

Dependency direction is always **downward**: consumers depend on the export;
the export depends on canonical data; nothing depends upward. The canonical
layer depends on nothing.

## 2. Components

| Component | Path | Role | Layer |
|---|---|---|---|
| Entity corpus | `content/<domain>/<subdomain>/<slug>.md` | Canonical knowledge nodes; YAML frontmatter + prose. | canonical |
| Assertion corpus | `connections/conn.NNNNNN.yaml` | Canonical relationship assertions (one object per claim). | canonical |
| Source records | `sources/src.<slug>.yaml` | Canonical citation records referenced by evidence. | canonical |
| Schemas | `schema/*.schema.json` | Machine contracts for each canonical object kind + the export. | contract |
| Registries | `schema/relation-registry.yaml`, `schema/agent-registry.yaml`, `schema/extension-registry.yaml`, `schema/vocabularies/` | Governed controlled vocabularies. | contract |
| Version source | `schema/VERSION.yaml` | Single source for schema/export/registry versions. | contract |
| Gate | `scripts/validate.py` | Validation + deterministic export generation. | gate |
| History guards | `scripts/check_id_immutability.py` | Identity & assertion-triple immutability from git history. | gate |
| Review state machine | `scripts/review.py`, `scripts/curation_state.py`, `scripts/apply_review_decisions.py` | Human review workflow for assertions. | workflow |
| Ingestion | `scripts/ingest.py`, `scripts/ingest_to_proposals.py`, `scripts/curation_pipeline.py` | Document → review-ready proposal (never canonical directly). | workflow |
| Analysis | `scripts/graph_analysis.py`, `scripts/epistemic_summary.py`, `scripts/integrity_anomalies.py`, `scripts/curation_status.py`, `scripts/dependency_review_campaign.py` | Derived reporting on corpus state. | derived |
| Explorer | `explorer/` | First-party 3-D graph visualizer; a *consumer* that reads only the published export. | consumer |
| Python adapter | `adapters/python/` | First-party read-only consumer adapter: Python SDK, CLI, and local JSON API over the export. | consumer |
| Test suite | `tests/` | Layered invariant tests (see `docs/TESTING.md`). | gate |
| CI | `.github/workflows/ci.yml` | Runs the full verification chain + freshness + security scans. | gate |

## 3. Layer invariants (what the architecture guarantees)

1. **Canonicality is a location, not an opinion.** Only
   `content/`+`connections/`+`sources/` are canonical; anything regenerable is
   derived; a derived artifact can never become authoritative.
2. **No unvalidated state.** The export is written only after every check
   passes — including validation *of the export against its own contract*.
3. **No silent identity churn.** IDs are immutable (guard: git-history
   identity reconstruction); assertion triples are immutable (correction =
   supersession + new ID).
4. **No duplicate claims.** Two active assertions with the same claim
   signature fail the gate.
5. **No hidden authority.** Every agent in provenance resolves in the agent
   registry; review status transitions are recorded with reviewer and reason.
6. **No curriculum coupling.** The generality invariant is tested; scoping
   metadata (grade/course/country/product) is structurally absent.
7. **No ecosystem coupling.** The repository-independence invariant is tested:
   canonical data, schemas, code, and core docs contain no reference to any
   private project ecosystem.
8. **Determinism.** Derived artifacts carry a content hash, never a wall
   clock; regeneration is byte-identical (tested; CI enforces freshness via
   `git diff --exit-code`).

## 4. Boundaries and dependency rules

- **Entity ↔ connection boundary.** Entities carry *no* relationship data.
   All relationships live in `connections/` as first-class objects (ADR-0020,
   executed fully in contract v2.0 / ADR-0028). This is the single-relationship-
   source invariant; the explorer and export enforce it structurally.
- **Data ↔ metadata boundary.** Knowledge fields (definition, equation
  display forms) are distinct from provenance/review metadata; metadata never
  edits silently (see `docs/METADATA-SPECIFICATION.md`).
- **Gate ↔ consumer boundary.** The validator never writes into consumer
   trees (the explorer syncs its own copy). The gate's only output channel is
   `exports/` and `reports/`.
- **Canonical ↔ derived boundary.** Derived generators may read canonical
   data; they never write it.

## 5. Extension mechanisms

| Mechanism | Purpose | Governance |
|---|---|---|
| `schema/extension-registry.yaml` | Additive metadata dimensions on entities/connections/sources | Registered with purpose + owner; validated by the gate |
| `schema/relation-registry.yaml` `reserved` status | Pre-defined relations not yet in canonical use | Require an ADR before first canonical use |
| `schema/agent-registry.yaml` | New provenance agents (human/process/llm) | Same PR as first use |
| External-ID schemes (`external_ids`) | Cross-reference Wikidata, DOI, ORCID, QUDT, UCUM… | Known schemes format-checked; unknown schemes allowed |
| Export views (`exports/knowledge.<policy>.json`) | Review-policy filtered views of the same assertions | Policy semantics in `scripts/graph_policy.py` |

Anything not extendable through these mechanisms requires an ADR, because it
changes the contract surface.

## 6. What is deliberately NOT in the architecture

- No database, service, API gateway, or cloud dependency — the contract is a
  validated file.
- No RDF/OWL stack in the canonical layer. The assertion model is
  *forward-compatible* with RDF-star-style reification and maps to SKOS/Biolink
  patterns in derived projections (`docs/STANDARDS.md` records the decisions).
- No embeddings or model outputs in canonical data — always derived,
  model-versioned, and outside the contract.
- No schema sprawl: one envelope schema per object kind; type semantics live
  in the domain model and registry, not in per-type schemas.

## 7. Architectural decisions

Foundational decisions are recorded as ADRs in `docs/decisions/` and are the
authority for everything described here. The current baseline is fixed by
ADR-0027 (ecosystem decoupling + `stemma:` namespace), ADR-0028 (contract v2.0:
connections-only relationship truth), and ADR-0029 (refoundation baseline).
