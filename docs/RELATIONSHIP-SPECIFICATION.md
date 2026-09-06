# STEMMA — Relationship Specification

**Status:** Authoritative (registry v1.0.0). The semantics of every edge in
the knowledge graph.
**Contracts:** `schema/relation-registry.yaml` (the registry),
`schema/connection.schema.json` (the envelope),
`scripts/validate.py` (domain/range, cycles, coherence),
`scripts/check_id_immutability.py` (triple immutability).

---

## 1. Model

Relationships are **first-class assertion objects** (connections/), never
fields on entities. One file = one claim = one identity:

- **Record identity:** `stemma:conn.NNNNNN` (opaque, sequential, immutable).
- **Claim identity (derived):**
  `claim_signature = sha256(source | relation | target | polarity | sorted qualifiers)`
  — the identity of the *proposition*. Never hand-authored; emitted in the
  export so consumers can deduplicate without recomputing (ADR-0026).

## 2. Relation registry

`schema/relation-registry.yaml` is the single authority for relation
semantics. Each relation defines:

| Property | Meaning |
|---|---|
| `family` | Semantic family: structural, hierarchical, dependency, causal, explanatory, model, analogy, measurement, cross_domain, associative/derivation. |
| `inverse` | The mirror relation (must exist and mirror back — coherence-checked). Inverse edges are **derived only**, never stored twice. |
| `transitive` | Whether transitive closure is semantically legal (illegal transitivity is gate-checked on cycles). |
| `domain` / `range` | Allowed entity types for source/target (gate-checked). |
| `status` | `adopted` (in canonical use) or `reserved` (defined, zero uses; **requires an ADR before first canonical use**). |

Registry integrity rules (validator-enforced): membership, family,
inverse-mirroring, domain/range referencing only defined entity types, no
duplicates of adopted semantics.

### 2.1 Adopted relations (12)

`part_of`, `generalizes`, `special_case_of`, `requires-family dependency edges`
(`logically_requires`, `mathematically_requires`), `derived_from`,
`appears_in_law`, `applies_to`, `related_to`, `bridges`, `analogous_to`,
`approximates`.

### 2.2 Reserved relations

Defined for future use with full semantics, zero canonical uses. Pruned in
v1.0.0: `broader_than`/`narrower_than` (≡ `generalizes`/`special_case_of`;
SKOS `skos:broader/narrower` are the mapping targets), `contains` (≡
`has_part`), `is_a` (≡ `special_case_of` for taxonomy). One name per meaning —
duplicated relation semantics are a defect, not a feature.

## 3. Claim lifecycle and immutability

1. **The triple is immutable.** `(source, relation, target)` under an ID never
   changes. Correcting a claim = supersede (`assertion.status: superseded` +
   `lifecycle.replaced_by`) + assert the corrected claim under a **new** ID.
2. **Evidence/review/confidence/context may change freely** — only the claim
   itself is frozen.
3. **Removal requires retirement.** A connection that vanishes without
   supersession/deprecation fails the git-history guard (consumers may hold
   its ID).
4. **No duplicate active claims.** Two active connections with one claim
   signature fail the gate. Competing claims (disagreement) are modeled as
   separate assertions with distinct qualifiers/polarity, resolved by review —
   not by overwriting.

## 4. Structural semantics

- **Directionality**: `source –relation→ target` reads as an English sentence
  ("kinetic energy *mathematically_requires* mass"). Inverses are derived at
  projection time (`graph_analysis.py` materializes them marked `derived`).
- **Cardinality**: unbounded by design (many claims are legitimately many-to-
  many); uniqueness is at claim level (signature), not pair level.
- **Polarity**: `positive`/`negative` (optional; distinct from the `contradicts`
  relation — a negative claim still asserts a relationship, `contradicts`
  asserts a conflict between claims).
- **Context scopes the claim**: domain/subdomain/regime/scale/assumptions/
  qualifiers (see METADATA-SPECIFICATION §4). A claim outside its stated
  regime is a reviewer question, not silently true.

## 5. Graph invariants (gate-enforced)

1. Every `source`/`target` resolves to a live entity (no dangling edges).
2. Domain/range conformance to the registry.
3. **No cycles** over dependency-family relations (`requires`,
   `mathematically_requires`, `logically_requires`, `part_of`,
   `generalizes`/`special_case_of`) — knowledge prerequisites must be a DAG.
4. No illegal transitivity (e.g. `extends`/`supersedes` chains).
5. Inverse coherence in the registry (mutual + mirrored).
6. `bridges`/`shared_mechanism_with` only across domains/subdomains (cross-
   domain is their point).

## 6. Evidence standards (review-time)

Minimum evidence per family before `canonical` (full table:
`docs/CURATION-PROTOCOL.md`): structural → authoritative conceptual source;
dependency → explicit derivation/prerequisite documentation; causal →
experimental literature (a textbook alone is insufficient for strong `causes`);
model (`approximates`/`idealizes`) → stated validity regime + assumptions;
analogy → explicit correspondence mapping; cross-domain → mechanism citation.

Axiomatic/definitional claims (e.g. `part_of` nucleus→cell) may carry
`evidence: [{type: other, description: "axiomatic structural definition"}]`.

## 7. Extending the vocabulary

1. Check the registry: an adopted/reserved relation may already express it.
2. If genuinely new: propose an ADR (family, inverse, transitivity,
   domain/range, evidence standard, why existing relations are insufficient).
3. Landing = registry entry + validator support + tests, in one PR.
4. Using a `reserved` relation canonically = its promotion ADR (registry
   status flips to `adopted`).

Relations are never added "just in case": the registry grows by decision, not
by drift.
