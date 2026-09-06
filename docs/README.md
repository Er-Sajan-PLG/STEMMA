# STEMMA — Documentation

The authoritative documentation set for the STEMMA knowledge foundation.
One subject, one document; contradictions are bugs.

## Reading order (new engineer)

1. **[VISION.md](VISION.md)** — what STEMMA is, what problem it solves, its principles and non-goals.
2. **[ARCHITECTURE.md](ARCHITECTURE.md)** — the system: layers, components, invariants, boundaries.
3. **[DOMAIN-MODEL.md](DOMAIN-MODEL.md)** — entities, connections, sources; identity and lifecycle.
4. **[GOVERNANCE.md](GOVERNANCE.md)** — invariants, decision process, human-review gates.
5. **[CONTRIBUTING.md](CONTRIBUTING.md)** — how to change things safely.

## Reference set (by subject)

| Subject | Document |
|---|---|
| Vision & principles | [VISION.md](VISION.md) |
| System architecture | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Domain model | [DOMAIN-MODEL.md](DOMAIN-MODEL.md) |
| Schema contracts & evolution | [SCHEMA-SPECIFICATION.md](SCHEMA-SPECIFICATION.md) |
| Metadata semantics | [METADATA-SPECIFICATION.md](METADATA-SPECIFICATION.md) |
| Relationship/assertion semantics | [RELATIONSHIP-SPECIFICATION.md](RELATIONSHIP-SPECIFICATION.md) |
| Pipelines (authoring → … → consumption) | [PIPELINES.md](PIPELINES.md) |
| Implementation status (evidence-based) | [IMPLEMENTATION-STATUS.md](IMPLEMENTATION-STATUS.md) |
| Roadmap | [ROADMAP.md](ROADMAP.md) |
| Testing strategy | [TESTING.md](TESTING.md) |
| Standards & interoperability | [STANDARDS.md](STANDARDS.md) |
| Governance & human gates | [GOVERNANCE.md](GOVERNANCE.md) |
| Security, integrity, provenance | [SECURITY-INTEGRITY-PROVENANCE.md](SECURITY-INTEGRITY-PROVENANCE.md) |
| Consumers & integration | [CONSUMERS.md](CONSUMERS.md) |
| Versioning policy | [VERSIONING.md](VERSIONING.md) |
| Migration log (append-only) | [MIGRATIONS.md](MIGRATIONS.md) |
| Curation & review protocol | [CURATION-PROTOCOL.md](CURATION-PROTOCOL.md) |
| Ingestion pipeline | [INGESTION.md](INGESTION.md) |
| Sources & attribution inventory | [SOURCES.md](SOURCES.md) |
| Glossary | [GLOSSARY.md](GLOSSARY.md) |
| Critical review & decision records | [SOTA-REVIEW.md](SOTA-REVIEW.md) |
| Deep-dive recommendations & implementation guide | [DEEP-DIVE-RECOMMENDATIONS.md](DEEP-DIVE-RECOMMENDATIONS.md) |
| Decision records (ADRs) | [decisions/](decisions/) |
| Contributor guide | [CONTRIBUTING.md](CONTRIBUTING.md) |

## Historical documents

ADR records (`docs/decisions/`) are the permanent decision history and remain
authoritative for their subjects. All pre-refoundation plans, audits, and
vision documents were retired on 2026-09-04 (ADR-0027); git history and
`MIGRATIONS.md` preserve the record.

## Ground rule

Documents describe the system; they do not replace it. Canonical truth is
`content/` + `connections/` + `sources/`, and the gate
(`scripts/verify_all.py`) decides — a doc that contradicts the gate is wrong.
