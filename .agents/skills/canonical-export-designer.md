# Canonical Export Designer Skill

**Purpose**: Teach an agent how to design deterministic exports, manage export contracts, version exports, create projections/subsets, and build consumer adapters.

**When to Use**: When creating new export formats, modifying the export pipeline, adding subset exports, or designing consumer integration patterns.

**Mental Model**: Exports are derived artifacts - never the source of truth. They must be deterministic, reproducible, versioned, and explicit about information loss.

---

## Export Architecture

```
Canonical Source (content/, connections/, sources/)
        ↓
Validator/Exporter (scripts/validate.py)
        ↓
Versioned Export (exports/knowledge.json)  ← PRIMARY CONTRACT
        ↓
Subset Exports (exports/knowledge.*.json)  ← SPECIALIZED VIEWS
        ↓
Consumer Adapter (consumer-owned)
        ↓
Consumer Application Model
```

---

## Export Contract (Primary)

**File**: `exports/knowledge.json`
**Version**: `export_version` (breaking shape changes)
**Schema Version**: `schema_version` (entity/relationship schema changes)
**Kernel Version**: `kernel_version` (content releases)

**Required Top-Level Fields**:
```json
{
  "export_version": "0.2",
  "schema_version": "0.3",
  "kernel_version": "1.0.0",
  "content_hash": "sha256...",
  "generated_at": "ISO timestamp",
  "source": "content/",
  "entity_count": 224,
  "connection_count": 654,
  "source_count": 3,
  "entities": [...],
  "connections": [...],
  "sources": [...]
}
```

**Entity Representation**: Mirrors canonical frontmatter exactly (minus `_file` internal field)
**Connection Representation**: Full connection objects from `connections/`
**Source Representation**: Full source objects from `sources/`

---

## Versioning Model

| Track | Identifier | Changes On | Consumer Impact |
|-------|-----------|------------|-----------------|
| Schema | `schema_version` | Entity fields, enums, constraints | May need adapter update |
| Export | `export_version` | Export shape, top-level fields | MUST update adapter |
| Content | `kernel_version` | Entities added/updated/deprecated | No adapter change needed |

**Rule**: Content releases (new entities, fixed typos) → `kernel_version` only. Export contract stable.

---

## Subset Exports (via `scripts/export_subsets.py`)

| Export | Policy | Use Case |
|--------|--------|----------|
| `domain-{domain}` | Entities in one domain | Subject-specific consumers |
| `type-{type}` | Entities of one type | Type-specific processing |
| `status-{status}` | Entities with status | Review workflow consumers |
| `entities-only` | No connections | Lightweight lookup |
| `connections-only` | Minimal entities + all connections | Graph traversal |
| `ai-rag` | Entities with embedded adjacency | RAG/vector indexing |
| `educational` | Only canonical/reviewed | Learning applications |

**Creating New Subsets**:
1. Add filter function in `scripts/export_subsets.py`
2. Call from `main()`
3. Follow naming: `knowledge.{policy}.json`
4. Include `policy` field in output
5. Document information loss explicitly

---

## Determinism Requirements

1. **Sorted output**: Entities by ID, connections by ID
2. **Stable timestamps**: `generated_at` only metadata, not in content hash
3. **Content hash**: SHA256 of all canonical files (content + connections + sources)
4. **No randomness**: No UUID generation, no system time in content
5. **Reproducible**: Same canonical files → identical export

---

## Consumer Adapter Pattern

The adapter is the **ONLY** file that imports across the seam.

**Required Adapter Responsibilities**:
1. Validate `export_version` before any lookup (throw on mismatch)
2. Index entities by ID for O(1) lookup
3. Resolve relationships (throw on dangling, never silently skip)
4. Map canonical → consumer application model
5. Handle ID namespace compatibility (`lhs:` ↔ `stemma:`)

**Example Adapter Interface**:
```typescript
loadKnowledge(): { metadata, entityCount }
getEntity(id): Entity
getRelatedEntities(id): RelatedEntity[]
getAllEntities(): Entity[]
```

**Adapter MUST NOT**:
- Modify canonical data
- Infer missing relationships
- Add curriculum/pedagogical metadata to canonical objects
- Cache across export versions without validation

---

## Information Loss Documentation

Every subset export must document what is lost:

| Export | Loses |
|--------|-------|
| `entities-only` | All relationships |
| `domain-physics` | Cross-domain connections |
| `ai-rag` | Full connection provenance, evidence, context |
| `educational` | Draft/unreviewed content |

**Rule**: Consumer must know what they're not getting.

---

## Testing Exports

```bash
# Regenerate all exports
python3 scripts/validate.py
python3 scripts/export_subsets.py

# Verify determinism
python3 scripts/validate.py
diff exports/knowledge.json exports/knowledge.json.bak  # should be identical

# Test adapter with new export
cd /path/to/consumer && pnpm test
```

---

## Validation Checklist for Export Changes

- [ ] `export_version` bumped for breaking shape changes
- [ ] `schema_version` bumped for schema changes
- [ ] `kernel_version` bumped for content releases
- [ ] Content hash matches canonical files
- [ ] All subset exports regenerate
- [ ] Adapter validates export version
- [ ] Adapter handles new fields gracefully
- [ ] No silent data loss in subsets (documented)
- [ ] Export validates against schema
- [ ] Determinism verified (run twice, compare)

---

## Escalation Conditions
- Export contract change needed → Requires ADR, human approval
- Consumer breaks on export update → Check version enforcement in adapter
- New subset needed frequently → Add to `export_subsets.py`, not one-off scripts
- Large export performance issues → Consider streaming/incremental (documented, not built yet)