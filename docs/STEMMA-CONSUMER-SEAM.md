# STEMMA ↔ LearningHub — Consumer Seam (Phase 2)

> **Consumer proof, not a platform.** STEMMA publishes a versioned export. LearningHub
> consumes it through one adapter. One direction. Nothing else.

## The pipeline

```
STEMMA canonical files  (content/*.md — YAML frontmatter)
        │  python3 scripts/validate.py
        ▼
  exports/knowledge.json         (DERIVED — regenerable, never edited by hand)
        │  import (build/test/dev time)
        ▼
  apps/shell/src/lib/lhs-adapter.ts   (LearningHub consumer boundary)
        │
        ▼
  apps/shell/src/lib/lhs-demo.ts  →  index.html #lhs-demo
```

## Export contract

- **File:** `STEMMA/exports/knowledge.json`, contract **`export_version: 0.1`**,
  schema **`schema_version: 0.1`**.
- **Shape:** top-level `export_version`, `schema_version`, `generated_at`, `source`,
  `entity_count`, and `entities[]`. Each entity carries `id`, `type`, `name`, `domain`,
  `status`, `definition`, optional `symbol` / `unit` / `equation` / `common_misconceptions`,
  `provenance`, `relationships[]`.
- **Versioning:** a consumer may state "I consume export contract version X". Breaking changes to
  the shape bump `export_version`. Content edits are a content release and do **not** bump the
  contract. (Specification §10, decision 0008.)
- **Validation:** the validator rejects dangling relationship targets and enforces the entity and
  relationship vocabularies before the export is written. A consumer never needs to handle a
  dangling target in practice — but the adapter throws rather than silently skipping if one
  appears (defense in depth).

## Adapter location and API

- **`apps/shell/src/lib/lhs-adapter.ts`** — the only file that imports across the seam.
- **`apps/shell/src/lib/lhs-types.ts`** — LHS types, kept separate from LearningHub models.
- API: `loadKnowledge()` (validates the contract version and indexes entities),
  `getEntity(id)`, `getRelatedEntities(id)`.
- **Version enforcement:** `loadKnowledge()` rejects any `export_version !== "0.1"` with
  `LhsUnsupportedVersionError` (message includes found and supported versions). Lookups fail with
  `LhsEntityNotFoundError` / `LhsDanglingReferenceError` — never silently.

## Ownership

| Concern | Owner |
|---------|-------|
| What things mean (`definition`, `equation`, `symbol`, `unit`, relationships) | **STEMMA** (`content/`) |
| Common false beliefs (knowledge layer) | **STEMMA** (`common_misconceptions`) |
| Worked examples, questions, explanations, sequence | **LearningHub** (`apps/shell/src/lib/lhs-demo.ts`) |
| The adapter and LHS types | **LearningHub** (consumer) |
| The export file | **derived** — owned by the validator, regenerated from `content/` |

## Canonical vs derived vs pedagogical

- **Canonical:** `STEMMA/content/*.md`. Source of truth. Never generated.
- **Derived:** `STEMMA/exports/knowledge.json`. Regenerable from canonical; never
  authoritative and never hand-edited.
- **Pedagogical:** anything that teaches (worked examples, questions, ordering). Lives in the
  consumer. The boundary is kept legible in the demo UI: sections labeled
  *KNOWLEDGE — imported from STEMMA* vs *LEARNING — authored by LearningHub*.

## How to regenerate the export

```bash
cd STEMMA && python3 scripts/validate.py
```

Exit `0` writes a fresh `exports/knowledge.json`; exit `1` prints validation errors and writes
nothing. Regeneration is reflected by the consumer automatically (the adapter imports the file;
re-run tests/build to pick it up).

## How to run the demo and tests

```bash
# Consumer unit tests (includes the LHS adapter + demo slices)
pnpm --filter @learninghub/shell test

# Type-check the consumer
pnpm --filter @learninghub/shell typecheck

# Lint that covers the new files
pnpm lint:state && pnpm lint:dom && pnpm lint:arch && pnpm lint:circular

# View the demo
pnpm --filter @learninghub/shell dev        # http://localhost:5173/#lhs-demo
```

## Deferred for Phase 3

- Full MVP activation of STEMMA (content authoring, review workflow, multilingual).
- Additional consumer adapters (JARVIS, STEM-GAME, future products) — this seam is the template.
- A second vertical slice (more laws, quantities, equations) in the LearningHub UI.
- Real export piping (published artifact / package) instead of a direct file import.
- Schema/export version bumping policy when a second contract version exists.
- License files for both repos (human decision pending).
