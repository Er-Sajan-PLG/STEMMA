# STEMMA — Vision

**Status:** Authoritative. Supersedes every earlier vision/north-star document.
**Audience:** Anyone encountering STEMMA for the first time.

---

## What STEMMA is

STEMMA is an **open, structured, reusable knowledge foundation for science,
technology, engineering, and mathematics (STEM)**. It expresses the concepts,
quantities, laws, models, and relationships that constitute established STEM
knowledge as *version-controlled, machine-readable, human-reviewable data* —
independent of any curriculum, product, institution, or application.

```
STEMMA = a governed knowledge graph of STEM fundamentals, published as data.
```

It is not a course, a textbook, an app, a tutoring system, or a database
product. It is the *substrate* such things can be built on.

## The problem

Established STEM knowledge is abundantly available to humans as prose, but
badly available to software:

- **Textbooks are unstructured.** The fact that "kinetic energy requires mass
  and velocity" is prose in a chapter, not a referenceable, checkable edge in
  a graph.
- **Curricula re-encode the same knowledge repeatedly.** Every course,
  textbook, and platform re-describes force, osmosis, and mole calculations
  from scratch. The knowledge itself is universal; its packaging is not.
- **AI systems lack a trustworthy substrate.** Language models can recite
  science but need retrieval grounding: stable identifiers, explicit
  prerequisite structure, review status, and provenance they can cite.
- **Educational tooling cannot port knowledge.** Tutoring systems, simulators,
  and games each maintain private concept lists that drift apart and cannot
  interoperate.

No widely adopted, openly licensed, curriculum-neutral, machine-readable
foundation of STEM fundamentals exists. STEMMA exists to be that foundation.

## Identity statement

| Question | Answer |
|---|---|
| **What is STEMMA?** | A governed, open corpus of canonical STEM knowledge entities and first-class relationship assertions, with validation, provenance, versioning, and a published export contract. |
| **What problem does it solve?** | It makes established STEM knowledge reusable as *data* — stable identity, explicit semantics, reviewable provenance — so any curriculum, tool, or AI system can build on the same foundation instead of re-encoding it. |
| **What is its domain?** | Foundational STEM knowledge: concepts, quantities, units, laws, equations, misconceptions, phenomena, models, experiments — and the relationships among them. |
| **Canonical source of truth?** | The canonical files in `content/`, `connections/`, and `sources/`, validated by `scripts/validate.py`. Everything else is derived and regenerable. |
| **What is outside its scope?** | Curriculum, sequencing, grades, pedagogy, assessment, user data, presentation, hosting platforms, and any application logic. All of these belong to consumers. |

## Principles

1. **Knowledge, not curriculum.** The canonical layer records what the
   knowledge *is* and how it *relates*. When or to whom it is taught is a
   consumer decision. No grade, course, syllabus, or country appears in
   canonical content.
2. **Products are external.** STEMMA has consumers, never owners. It must
   remain fully useful if every current consumer disappears.
3. **Canonical is reviewed, not assumed.** Machine validation establishes
   form; only named human review establishes authority. AI-drafted content is
   provenance information, never authority.
4. **One source of truth; everything else derived.** Indexes, graph views,
   embeddings, APIs, and visualizations are regenerable artifacts — never the
   record itself.
5. **Stable identity.** Identifiers (`stemma:<domain>.<slug>`) are never
   reused, never reassigned, and independent of filenames, products, or
   storage.
6. **Assertions are objects.** A relationship is a first-class record with its
   own identity, evidence, context, confidence, review status, and lifecycle —
   not a field on an entity.
7. **Honest data.** Unknown is recorded as unknown (`null`), never invented.
   Provenance records origin, including "unrecoverable", rather than a
   plausible fiction.
8. **Machine-readable and human-readable together.** Every canonical object is
   simultaneously diffable prose-adjacent YAML/Markdown and strictly validated
   data.
9. **Small core, governed extension.** The schema stays deliberately minimal;
   growth happens through the governed extension registry, not schema sprawl.

## Why an independent open-source project

STEM knowledge is a public good. Its structured representation should be too.
The value of the foundation compounds with every independent consumer:
curricula, tutoring tools, simulators, visualizations, research tooling, and
AI systems that would otherwise each maintain a private, drifting copy. An
open project with explicit governance, stable identifiers, and a published
contract is the only credible home for that shared substrate.

## What "durable" means here

- **Identity outlives content churn**: entities can be deprecated, split, and
  merged without breaking consumer references.
- **The contract outlives the corpus**: schema and export contracts version
  independently of content growth.
- **History is part of the design**: git is the audit log; the guards verify
  identity and assertion immutability from history, not memory.
- **The model outlives fashion**: assertions follow the reified-statement
  pattern (claim + qualifiers + evidence + provenance), which maps cleanly
  onto Wikidata-style statement models and RDF-star-style reification —
  without requiring that stack.

## Non-goals

- Being a curriculum, syllabus, or courseware standard (consumers map onto
  STEMMA; STEMMA never maps onto them).
- Hosting, serving, or authenticating anything. Publication is a file
  contract.
- A general-purpose ontology or reasoning system. STEMMA models the domain it
  needs, no more.
- Coverage of the whole of science. Depth and correctness over breadth.

---

*Architecture: `docs/ARCHITECTURE.md`. Domain model: `docs/DOMAIN-MODEL.md`.
Governance and human-review gates: `docs/GOVERNANCE.md`.*
