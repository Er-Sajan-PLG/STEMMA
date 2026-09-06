# STEMMA — Standards & Interoperability

**Status:** Authoritative (baseline 3.0.0). Records which standards STEMMA
adopts, which it interoperates with, where it deliberately does not use a
standard, and why.

---

## 1. Adopted (used canonically)

| Standard | Where | Why |
|---|---|---|
| **JSON Schema draft 2020-12** | `schema/*.schema.json` | Mature, tool-rich, exact fit for structural validation of YAML/JSON objects. |
| **YAML 1.1 (strictly parsed)** | All canonical files | Human-diffable authoring; duplicate-key rejection because silent last-wins is a data hazard. |
| **JSON (UTF-8, sorted keys)** | Export contract | Universal machine readability; deterministic serialization. |
| **SHA-256** | `content_hash`, `claim_signature` | Integrity + claim identity; deterministic, dependency-free. |
| **Semantic Versioning** | `schema_version`, `export_version`, release line | Compatibility reasoning must be mechanical. |
| **ISO 8601 (UTC)** | All timestamps | Unambiguous time; `null` when unknown. |
| **SI / ISQ (BIPM)** | Unit and dimension vocabulary basis | The existing standard for quantities and units; no invented unit system. |
| **Wikidata QIDs** | `external_ids.wd` | The practical stable anchor for cross-referencing public knowledge; seeded and verified for the mechanics domain. |
| **DOI, ORCID, ISBN, QUDT, UCUM, CAS** | `external_ids` known schemes | Established identifier systems, format-checked by the gate. |
| **CC BY 4.0 (content) / MIT (code)** | Licensing | Open reuse with attribution for data; permissive for tooling (ADR-0001). |
| **Conventional Commits + commitlint** | Process | Mechanical changelogs and reviewable history. |

## 2. Interoperates with (derived projections / mappings)

| Standard | Relationship | Status |
|---|---|---|
| **SKOS** (`skos:broader/narrower/related`) | Mapping target for hierarchical/associative relations in a future RDF/JSON-LD projection; internal duplicates of SKOS semantics were pruned so the mapping is 1:1 | designed-for, not yet emitted |
| **JSON-LD 1.1** | Planned publication format for the graph projection (`@context` mapping `stemma:` relations to IRIs); 1.2 tracked, not blocking | roadmap (R4) |
| **RDF-star / RDF 1.2 triple terms** | The connection model is forward-compatible: `{source, relation, target}` ≈ triple term; assertion/context/evidence/provenance ≈ reifier annotations. Kept as a *mapping*, not a canonical dependency (still a W3C draft) | designed-for |
| **SHACL** | Candidate validation vocabulary *for the RDF projection only* (so external consumers can validate STEMMA data with standard tooling); never a replacement for the authoring gate | roadmap (R4) |
| **Biolink Model association pattern** | Conceptual alignment (qualified association: subject/predicate/object + qualifiers + evidence + provided_by); relation families map to Biolink predicates in projections | designed-for |
| **PROV-O** | Conceptual alignment for provenance (agent/activity separation); a PROV mapping is derivable from the provenance blocks | designed-for |
| **schema.org `DefinedTerm`** | Candidate shape for web publication of entities | roadmap |
| **CASE / LRMI** | Curriculum packaging — explicitly **consumer-side**; STEMMA never emits curriculum structures | out of STEMMA |

## 3. Deliberately not adopted (and why)

| Technology | Decision | Reason |
|---|---|---|
| **RDF/OWL as canonical store** | Not used canonically | At this scale a triple store adds operational cost with zero correctness gain; the assertion model gives the same shape with review machinery RDF lacks. Interop preserved via projections. |
| **OWL reasoning** | Not used | STEMMA needs governed human disagreement (competing claims, review ranks), not entailment. Revisit only if classification reasoning becomes a real workload. |
| **Graph databases** | Derived index at most, never canonical | Files in git are the canonical store; the graph is a projection (`knowledge.extended.json`). |
| **Wikibase software** | Pattern adopted, software not | Statement ranks/external-ID property patterns are borrowed; the wiki+SQL editing stack contradicts file-based governance. |
| **Custom relation semantics** | Avoided | One registry with defined families/inverses; duplicates of standard semantics (e.g. SKOS broader) are pruned, not reinvented. |
| **Wall-clock timestamps in artifacts** | Forbidden | Determinism is a contract; content hashes only. |
| **Embeddings in canonical data** | Forbidden | Model-versioned, lossy, derived by definition. |

## 4. Identifier strategy

- Canonical IDs are compact, memorable, namespace-scoped strings
  (`stemma:phys.force`) — stable today, independent of any registry.
- External IDs anchor STEMMA objects to public identifier systems
  (Wikidata/DOI/QUDT/…) outward-only.
- **Open decision (human gate, ADR-0029):** the public IRI form — e.g.
  `https://<domain>/id/phys.force` — and the schema `$id` base (currently the
  reserved placeholder `stemma.example`). Blocked on choosing an
  organization/domain; until then, string IDs are the contract.
