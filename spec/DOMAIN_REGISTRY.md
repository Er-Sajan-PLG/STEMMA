# DOMAIN REGISTRY — Controlled vocabulary for recovery artifact IDs

Established **before** permanent IDs (§7). Project code: `STEMMA`.
Canonical machine copy: `spec/machine-readable/domain_registry.yaml`.

| Domain | Meaning | Example artifact kinds covered |
|---|---|---|
| CORE | Canonical corpus: entities, connections, sources, identity, history | identity stability, canonical locations, object kinds |
| GATE | Deterministic validation gate + CI chain | verify_all, CI jobs, invariant tests, freshness checks |
| EXP | Export contract + derived artifacts | knowledge.json 2.2.0, embeddings.jsonl, vector_store, consumer exports, determinism |
| SCH | JSON Schemas + registries (contract data) | concept/connection/source schemas, relation/template/embedding/consumer/agent registries, VERSION.yaml |
| HITL | Human-in-the-loop review | hitl_check, review workflow, writer human:*, audit trail |
| SEC | Security, integrity, secrets, provenance | gitleaks, no-secrets checks, immutability guards |
| OPS | Build/dev/CI operations and repo hygiene | dependencies, pre-commit, branching, commit conventions |
| INTEG | Consumers, adapters, cross-repo interfaces | adapter SDK/API, consumer registry, examples/external-rag |
| RAG | Derived RAG/embedding reference implementation | embed.py, rag.py, export_consumers.py |
| SPEC | This recovery program itself (pilot management) | slice selection, validator, baseline, process review |

Rules (from protocol §7): IDs carry domain but **never hierarchy**; hierarchy
uses explicit `parent:` fields. New domains require recording justification
here before first use.
