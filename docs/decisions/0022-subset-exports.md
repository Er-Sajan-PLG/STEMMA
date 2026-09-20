# DECISION 0022 — Deterministic Subset Export System

- **Date:** 2026-09-06
- **Status:** decided
- **Related:** scripts/export_subsets.py, ADR-0007, ADR-0011, specification §11

## Context

The v0.2 export produced only a single monolithic `exports/knowledge.json`. This forced all consumers to download/process the entire knowledge base (224 entities, 654 connections) even when they only needed a subset (e.g., only physics, only canonical entities, only entities without connections for lightweight lookup).

Different consumer needs emerged:
- LearningHub: needs canonical entities with relationships
- AI/RAG systems: need entities with embedded adjacency for vector indexing
- Search indexes: need entities-only, no connections
- Subject-specific apps: need single domain
- Mobile/offline: need minimal payloads

## Decision

**Implement a deterministic subset export system (`scripts/export_subsets.py`) generating focused exports from the primary export.**

### Standard Subset Exports
| Export | Policy | Entities | Connections | Use Case |
|--------|--------|----------|-------------|----------|
| `knowledge.domain-{domain}.json` | Domain filter | ~30-100 | Domain-internal | Subject-specific apps |
| `knowledge.type-{type}.json` | Type filter | ~1-150 | Type-internal | Type-specific processing |
| `knowledge.status-{status}.json` | Status filter | Variable | Status-filtered | Review workflows |
| `knowledge.entities-only.json` | No connections | All | 0 | Lightweight lookup |
| `knowledge.connections-only.json` | Minimal entities | Referenced | All | Graph traversal |
| `knowledge.ai-rag.json` | RAG-optimized | All | Embedded in entities | Vector indexing, RAG |
| `knowledge.educational.json` | Canonical only | Canonical | Canonical-reviewed | Learning applications |

### Export Contract
Each subset export includes:
```json
{
  "export_version": "0.2",
  "schema_version": "0.3",
  "policy": "domain:physics",
  "generated_at": "...",
  "source": "content/",
  "entity_count": 96,
  "connection_count": 291,
  "entities": [...],
  "connections": [...]
}
```

### Determinism Guarantees
- Sorted entities (by ID) and connections (by ID)
- Content hash from canonical files only
- Same canonical → identical subsets
- No system time in content

### Information Loss Documentation
Every subset explicitly documents what is lost:
- `entities-only`: All relationships
- `domain-*`: Cross-domain connections
- `ai-rag`: Full connection provenance, evidence, context qualifiers
- `educational`: Draft/unreviewed content

## Alternatives Considered

- **Consumer-side filtering**: Rejected — wastes bandwidth, duplicates logic
- **Database/API with query params**: Rejected — violates "simple now", file-based is sufficient
- **Separate export per consumer**: Rejected — unmaintainable, subset system is generic

## Consequences

- Primary export unchanged (backward compatible)
- Subset exports regenerated on every `validate.py` run
- Consumers choose appropriate subset
- New subsets added to `export_subsets.py` (not one-off scripts)
- Export version bumped to 0.2 (new entity types in schema 0.3)

## Status

**decided** — implemented in scripts/export_subsets.py.