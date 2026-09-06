# GLOSSARY — STEMMA

Terms used across the specification set. Authoritative definitions live in
the linked documents.

| Term | Meaning | See |
|------|---------|-----|
| **canonical** | The source of truth: `content/`, `connections/`, `sources/` only. | ARCHITECTURE §1 |
| **derived artifact** | Anything regenerable from canonical data (exports, views, reports); never authoritative. | PIPELINES §3 |
| **entity** | A canonical knowledge node (`stemma:<domain>.<slug>`). | DOMAIN-MODEL §2 |
| **connection** | A first-class assertion object: claim triple + assertion + context + evidence + provenance. | DOMAIN-MODEL §4 |
| **claim (triple)** | `(source, relation, target)` — what a connection asserts; immutable. | RELATIONSHIP-SPEC §3 |
| **claim signature** | Derived `sha256(source\|relation\|target\|polarity\|qualifiers)`; identity of the proposition. | RELATIONSHIP-SPEC §1 |
| **supersession** | Correcting a claim: retire the old connection (`superseded` + `replaced_by`), assert under a new ID. | RELATIONSHIP-SPEC §3 |
| **relation registry** | `schema/relation-registry.yaml` — semantics of every relation (family, inverse, domain/range, status). | RELATIONSHIP-SPEC §2 |
| **adopted / reserved** | Relation in canonical use / defined for future use (promotion needs an ADR). | RELATIONSHIP-SPEC §2 |
| **provenance** | Facts about the record's origin: agents, method, review history. | METADATA-SPEC §2 |
| **agent registry** | `schema/agent-registry.yaml` — every human/process/llm/unknown agent; gate-resolved. | METADATA-SPEC §2 |
| **review status** | Authority track: `unreviewed → reviewed → canonical` (+ `rejected`); human-only transitions. | DOMAIN-MODEL §6, CURATION-PROTOCOL |
| **evidence** | Typed citations supporting/refuting a claim (distinct from provenance). | METADATA-SPEC §2 |
| **source record** | A canonical citable origin in `sources/`. | DOMAIN-MODEL §1 |
| **historical attribution** | Who first stated the science and when (`historical` block); distinct from record provenance. | METADATA-SPEC §2 |
| **context** | Applicability scope of a claim: domain, subdomain, regime, scale, assumptions, qualifiers. | METADATA-SPEC §4 |
| **extension registry** | Governed additive metadata dimensions (`extensions.*`). | METADATA-SPEC §9 |
| **external IDs** | Outward cross-references (Wikidata, DOI, QUDT, …), format-checked. | METADATA-SPEC §8 |
| **export contract** | The validated, versioned consumer artifact `exports/knowledge.json` (v2.x). | CONSUMERS, SCHEMA-SPEC §6 |
| **content hash** | Deterministic `sha256:` digest over canonical inputs; freshness/integrity stamp. | VERSIONING §4 |
| **gate** | `scripts/validate.py` + the verify chain; the only path from canonical data to export. | PIPELINES §2.4 |
| **generality invariant** | No curriculum/grade/country/product semantics in canonical data. | DOMAIN-MODEL §7 |
| **independence invariant** | No coupling to any private ecosystem anywhere in the repo. | GOVERNANCE §12 |
| **freeze** | Foundational changes require an ADR — not "never change". | GOVERNANCE §3 |
| **baseline** | The declared authoritative state of all architecture documents (currently 3.0.0). | ADR-0029 |
| **adapter** | A consumer-side library, CLI, or API layer that reads the export and reshapes it for downstream use without becoming canonical truth. | CONSUMERS §5 |
| **consumer** | Any external system reading the export; owns adapters, curriculum, presentation. | CONSUMERS |
| **draft / machine_validated / human_reviewed / canonical / deprecated / superseded** | Entity lifecycle states. | DOMAIN-MODEL §6 |
