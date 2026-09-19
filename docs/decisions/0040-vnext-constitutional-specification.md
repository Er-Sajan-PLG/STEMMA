# 40. STEMMA vNext Constitutional Specification

Date: 2026-09-14

## Status

Ratified — conceptual freeze. This document is the **normative core** of the
STEMMA vNext model. It supersedes the exploratory audit and any earlier
field-level description that conflicts with it. No implementation agent may
modify canonical data, schema, or the gate in a way that contradicts these
rules; this document is the reference those changes are stress-tested against.

## 0. Authority and scope

This is a **contract**, not prose and not code. It governs:

- the canonical object model and its semantic primitives,
- the registries (relations, rules, vocabularies),
- the deterministic gate,
- ingestion and the review workflow.

Consumers (the explorer, the read-only adapter) read the derived export and are
otherwise unaffected. The canonical layer remains Git-native YAML + Markdown;
this specification changes *what the files mean*, not where they live.

---

## 1. Constitutional laws

These are non-negotiable. Everything else in this document operationalizes them.

### L1 — Claim is the sole bearer of epistemic truth

An entity, a source, a document, a definition string, an equation string, a
model output, or a relationship **does not become true merely by existing**.

Only a **Claim** can assert something as true, false, proposed, inferred,
derived, disputed, and so on. A canonical claim must carry:

```text
assertion
context
provenance
review state
```

and must be supported by at least one of:

```text
source evidence
formal derivation
explicit human authorship
```

*Entity ≠ truth. Source ≠ truth. LLM output ≠ truth. Definition string ≠ truth.
Connection ≠ truth by default.*

### L2 — Canonicalization is human-only

```text
LLM → candidate → validation → human review → canonical
```

Never:

```text
LLM → canonical
```

The human-gated ingestion and forward-only review state machine are
foundational and survive unchanged conceptually.

### L3 — AI confidence is not epistemic truth

The following are **five distinct things and are never collapsed into a single
number**:

```text
model_confidence     — an uncalibrated signal from a model
source_support       — the direction/strength of evidence for a claim
validation_status    — deterministic gate outcome (pass/fail/advisory)
review_status        — human epistemic state (unreviewed…canonical)
epistemic_status     — asserted/inferred/derived/disputed/hypothesized…
```

A model may emit `model_confidence`; it may not, by itself, change
`review_status` or `epistemic_status`.

### L4 — Deterministic science stays deterministic

No LLM is authoritative for:

```text
reference integrity
schema conformance
units
dimensions
equation structure
variable binding
dimensional consistency
controlled vocabulary
graph invariants
```

These are computed, never generated.

### L5 — Identity is immutable

An ID never changes meaning; correction is supersession + a new ID. Identity
guards are enforced from git history, not by assertion.

### L6 — Derived ≠ canonical

Exports and reports are regenerable, byte-deterministic, and never
authoritative. The canonical layer depends on nothing; everything else depends
on it.

### L7 — No curriculum/product/grade semantics in canonical data

STEMMA is a knowledge foundation, not a course, a product, or a curriculum.

### L8 — Materialization is constitutional

```text
DOCUMENT → OBSERVATION → CANDIDATE ASSERTION → ENTITY RESOLUTION
  → CLAIM → VALIDATION → REVIEW → CANONICAL KNOWLEDGE → DERIVED EXPORT
```

Never:

```text
PDF → LLM → canonical
```

---

## 2. Canonical semantic primitives

These are **semantic primitives** first; not every one is an immediate
top-level file. Their meanings are normative even before their storage is
finalized.

| Primitive | Definition | Boundary (what it is NOT) |
|---|---|---|
| **Entity** | What we are talking about; a referent. | Not truth; carries no relationships. |
| **Property** | Intrinsic canonical structure of what an entity *is*. | Not assertional; carries no evidence/review. |
| **Claim** | An assertion about something (true/false/proposed…). | The *only* bearer of epistemic truth (L1). |
| **ValueClaim** | A claim whose object is a structured value, not an entity reference. | Still a claim; still evidence-bearing. |
| **Relation** | A typed, directed, registry-controlled edge. | Not free-form; no uncontrolled generic predicate. |
| **Evidence** | A located source-observation that supports or contradicts a claim. | Not the source; not the claim. |
| **Source** | A bibliographic citation. | Not content; not a document. |
| **Document** | A material artifact (content hash, version/edition, URI). | Not a citation. |
| **Observation** | A specific located reading extracted from a document. | Not a claim; becomes evidence after interpretation. |
| **ExtractionRun** | The activity (tool, params-hash, timestamp) that produced observations. | Not provenance-by-assertion. |
| **Context** | Where/when/under what assumptions a claim applies. | Not truth; not evidence. |
| **Derivation** | A reproducible step: premises → rule → conclusion. | Not an undocumented "LLM inferred it". |
| **Provenance** | Agent / activity / generation / review trail. | Attestation; not truth. |
| **Review** | The forward-only human epistemic state machine. | Not validation; not confidence. |
| **Rule** | A registered transformation usable in a derivation. | Not free text; registry-controlled. |

---

## 3. The Property / Claim / ValueClaim boundary

The distinction is **ontological**, not procedural.

```text
PROPERTY    = part of the canonical description of what the entity is.
CLAIM       = an assertion about something that can be true or false.
VALUECLAIM  = a claim whose object is a structured value.
```

Validation and review operate **on top of** this distinction:

- The deterministic validator checks **properties** (they are structural).
- **Claims** additionally require epistemic governance: evidence, provenance,
  context, and review state.

The same semantic fact may be represented differently depending on whether we
are *defining a canonical entity* (`Quantity.dimension` = a property) or
*asserting something about an existing entity* ("Entity X has dimension L" = a
claim). The representation tracks the **speech act**, not the physics.

**Normative law:** *Properties describe canonical structure; claims carry
epistemic assertions.*

---

## 4. Quantity architecture

**QuantityKind is not Dimension.** Dimension is necessary for quantitative
typing but does not uniquely identify a quantity kind. Energy and torque share
dimension M·L²·T⁻² yet are different kinds with different meaning and
convention.

```text
QuantityKind
    └── has_dimension → Dimension

Quantity
    ├── instance_of  → QuantityKind
    └── has_dimension → Dimension

Measurement / observed value
    └── ValueClaim
```

The validator enforces:

```text
quantity.dimension == quantity.quantity_kind.dimension
```

Examples:

```text
Displacement
  → quantity_kind → stemma:qkind.displacement
  → dimension     → length (L)

Energy
  → quantity_kind → stemma:qkind.energy
  → dimension     → M L² T⁻²

Torque
  → quantity_kind → stemma:qkind.torque
  → dimension     → M L² T⁻²      # same dimension, different kind
```

A **measurement** (e.g. "displacement = 5 m, measured at t") is a ValueClaim —
a magnitude + unit + uncertainty assertion — never an entity and never a
property.

---

## 5. Claim model

A claim has two forms and exactly one rank:

1. **Relational** — `subject → predicate → object` (entity → entity).
2. **Valued** — `subject → predicate → value` (entity → structured literal:
   `magnitude + unit + uncertainty + value_type`).

Both carry: `assertion`, `context`, `evidence[]`, `provenance`, optional
`derivation`, and `validity`.

**Rank** (`preferred` / `normal` / `deprecated`) means **"reviewed preference
among competing canonical claims."** It does **not** mean "higher rank =
objectively true." Rank is a human review-time cross-claim preference, never an
LLM output, never auto-set.

**Duplicate rule:** two claims are duplicates (rejected) only when subject,
predicate, object/value, polarity, **and context** are all identical. Claims
that differ in value, context, or source are **competing**, not duplicates, and
their relationship is typed (§6).

---

## 6. Conflict semantics

Only one thing is "conflict"; the rest have their own semantics:

| Relationship | Model | A conflict? |
|---|---|---|
| True epistemic contradiction (`Claim A contradicts Claim B`) | `contradicts` (claim↔claim) | **Yes** |
| Same entity, different wording | alias / alternate label (SKOS-style `altLabel`) | No |
| Different regime | `context` (disjoint regime) | No |
| Different assumptions | `context` / model relation | No |
| Historical replacement | `supersedes` (lifecycle) | No |
| Source correction | `corrects` (evidence stance `contradicts` on the errored source) | No |
| Approximation | `approximates` (model relation) | No |
| Different model | model relation | No |

The **first-class conflict relation is exactly one: `contradicts`.** The former
`conflict` family (`contradicts`, `inconsistent_with`, `competes_with`,
`limited_by`) collapses to `contradicts`; the others are re-homed into context,
lifecycle, identity, and evidence-stance. Rank resolves the narrow `contradicts`
case at review time — and is *preference*, not *truth*.

---

## 7. Derivation (first-class, reproducible)

```yaml
derivation:
  id: stemma:derivation.0001
  premises:
    - stemma:claim.A
    - stemma:claim.B
  rule: stemma:rule.dimension-consistency
  transformation: ...
  conclusion: stemma:claim.C
  provenance: ...
```

**Fundamental invariant:**

```text
replay(rule, premises) == conclusion
```

whenever the rule is deterministic. Deterministic rules (dimensional algebra,
unit algebra, logical rules, algebraic substitution) are re-run by the
validator. Non-deterministic derivations must cite a **registered** rule and
carry `method.type` and rank; an anonymous "an LLM said so" is not a
derivation and is never auto-canonical.

This turns STEMMA from "a graph containing claims" into "a graph containing
claims **plus inspectable reasoning lineage**." The legacy `inference.path` maps
to `derivation.premises` and is deprecated.

---

## 8. Provenance and materialization

The chain L8 is backed by concrete objects:

- **Document** — `content_sha256`, version/edition, URI; bibliographic metadata
  anchors to a `Source`.
- **ExtractionRun** — `document` ref, `tool`, `params_hash`, `started_at`,
  `run_hash`.
- **Observation** — a located reading produced by an `ExtractionRun`.
- **Evidence** — points a claim at an observation/document with `locator_struct`
  and `stance`, and back-references its `ExtractionRun`.
- **Claim/entity provenance** — `asserted_by`, `generated_by`, `method`
  (model + prompt + prompt/config hash), `reviewed_by[]`, `review_history[]`.

The trace reaches the exact source version and the exact run, not merely a
citation.

---

## 9. Validation architecture

Nine independent layers, frozen:

```text
1. Structural   — JSON Schema: fields, types, enums, cardinality.
2. Referential  — every reference resolves (entity, unit, dimension, source,
                 document, run, premise, rule, successor).
3. Vocabulary   — relations, domains, subdomains, regimes, types, evidence
                 types, epistemic kinds.
4. Graph        — cycle detection, inverse coherence, duplicate detection (§5),
                 conflict typing (§6).
5. Semantic     — domain/range typing; quantity↔quantity_kind↔dimension
                 consistency (§4); requirement that a quantity carry a kind and
                 a dimension.
6. Mathematical — equation syntax, variable bindings all typed, LHS/RHS
                 well-formed.
7. Dimensional  — variable dimensions typed; equation LHS/RHS dimension vectors
                 equal; unit references dimensionally consistent.
8. Provenance   — every claim/entity has provenance; ai_drafted boolean;
                 reviewer required for canonical; agents resolve in registry;
                 model_confidence cannot set confidence-without-basis.
9. Epistemic    — forward-only review; rank monotonicity; a preferred-rank
                 value claim is unique per (subject, predicate).
```

**Hard law:** *Layers 5–7 must not require an LLM.* This is the bridge between
a document graph and a scientific knowledge system.

---

## 10. Canonical Displacement example

```yaml
entity:
  id: stemma:physics.displacement
  type: quantity
  name: Displacement

  properties:
    quantity_kind: stemma:qkind.displacement
    dimension: stemma:dimension.length
    reference_unit: stemma:unit.metre

claims:

  - id: stemma:claim.displacement.vector
    form: valued
    subject: stemma:physics.displacement
    predicate: is_vector
    value:
      value_type: boolean
      value: true

  - id: stemma:claim.displacement.position_difference
    form: relational
    subject: stemma:physics.displacement
    predicate: defined_by
    object: stemma:physics.position_difference

equation:

  id: stemma:eq.displacement.definition
  lhs: Δr
  relation: "="
  rhs:
    op: subtract
    args:
      - r_f
      - r_i

  variables:
    - symbol: Δr
      quantity: stemma:physics.displacement
    - symbol: r_f
      quantity: stemma:physics.position
    - symbol: r_i
      quantity: stemma:physics.position

context:
  assumptions:
    - same_reference_frame

provenance: ...
```

Each `claim` carries its own `evidence`, `provenance`, `review`, `context`,
and `epistemic_status`. *(Illustrative example; evidence is not source-derived.)*

---

## 11. Officially rejected (no further evolution in these directions)

```text
NO:  "unit": "newton"                        (a string is not machine-readable science)
NO:  "equation": "F = ma"                    (without a parseable representation)
NO:  "definition": "..."                     (treated as knowledge by itself)
NO:  "confidence": 0.97                      (mistaken for epistemic authority)
NO:  PDF → LLM → canonical
NO:  "knowledge graph" because an object contains a relationships[] array
```

A field *named* `dimension`, `equation`, or `unit` that contains uncontrolled
prose is not progress — it is the exact failure this specification eliminates.

---

## 12. Ratification record

| Decision | Verdict |
|---|---|
| Claim is the sole epistemic truth-bearer | **RATIFY** |
| Property / Claim / ValueClaim separation | **RATIFY** (authorization is removed as the semantic basis) |
| QuantityKind / Quantity / Measurement | **MODIFY** — QuantityKind remains distinct from Dimension |
| Narrow true-conflict relation | **RATIFY** |
| First-class reproducible Derivation | **RATIFY** |

---

## 13. Postponed / non-goals

OWL reasoning; SHACL (learn-from only); RDF/JSON-LD emission (already roadmap
R4); a formal TBox; embeddings/RAG; multilingual localization strategy.
STEMMA remains small, inspectable, deterministic, and Git-native.