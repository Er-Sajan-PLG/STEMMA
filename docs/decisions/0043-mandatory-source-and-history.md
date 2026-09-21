# DECISION 0043 — Mandatory Source + Dual Verification + History for Physics-Core

- **Date:** 2026-09-21
- **Status:** PROPOSED — companion to ADR-0040/0041/0042, implements user requirement "every entity source, link, writer etc embedded"
- **Related:** ADR-0015 (evidence provenance), ADR-0018 (historical attribution), ADR-0017 (extension registry), SCHEMA-SPECIFICATION.md, CURATION-PROTOCOL.md, PHYSICS-FIRST-IMPLEMENTATION-PLAN.md
- **Author:** arena/01a0c072-stemma

## Context

User requirement after physics-first plan:

1. **Every entity source, link, writer embedded** so every claim, every entity has a source along with other info for double/triple check/verify and change later.
2. **History (previous and progression)** for laws: who proposed, timeline etc. Might not follow minimal viable schema now, but needed.
3. **Get rid of current design, every pieces, from docs to code/implementation and completely start new, but started small.** Chosen scope: nuke_content_only — delete all entities/connections/sources/exports, keep engine (schemas + validator), rewrite docs to physics-first minimal with mandatory source.

Current schema already has:
- `provenance.source_kind`, `provenance.source` (optional string)
- `sources/*.yaml` canonical records with citation, authors, year, url, isbn
- `connections.evidence[]` with `source_ref`, `locator`, `description`
- `historical` block with `stated_by`, `year`, `where`, `timeline[]`

But they are optional, not mandatory. For physics-core, we need them mandatory for verification.

User selected:
- Wipe scope: nuke_content_only
- Source requirement: both — embedded + canonical source record (dual verification)
- History requirement: optional for draft, mandatory for canonical promotion

## Decision

### 1. Dual Source Verification (Both)

Every physics entity (draft or canonical) MUST have:

**A. Embedded provenance in entity frontmatter (quick check):**
```yaml
provenance:
  ai_drafted: bool
  source_kind: textbook | academic-or-research | standards-or-specification | institutional | other
  source: "Full citation string with page"
  writer: "human:curator.001"  # NEW: who wrote this entity file
  original_author: "Halliday, Resnick, Walker"  # NEW: who originally stated the science
  link: "https://..."  # NEW: URL/DOI to source
  retrieved_at: "2026-09-21"  # NEW: when source was accessed
```

**B. Canonical source record in `sources/` (authoritative):**
- File `sources/src.<slug>.yaml` with id `stemma:src.<slug>`, type, citation, authors[], year, publisher, url/doi/isbn
- Entity must reference it via `source_refs: [stemma:src.xxx]` (NEW field) OR via `evidence` in connections
- For entity itself, we add `source_refs` array (NEW) that lists canonical source IDs that support this entity definition

This gives double verification:
- Embedded = fast human check without leaving file
- Canonical record = single source of truth, versioned, with full bibliographic data
- Later triple check: compare embedded vs canonical vs external link

### 2. Connection Evidence Mandatory

Every connection MUST have >=1 evidence with:
- `type`: textbook | standard | academic-paper | etc.
- `source_ref`: stemma:src.xxx (must resolve)
- `locator`: "Ch 5, Eq 5-1, p112" (exact page/section)
- `locator_struct`: optional structured {page, section, equation}
- `description`: why this source supports claim
- `stance`: supports

No empty evidence allowed for physics-core (even for draft). This is stricter than generic rule (which allows empty for draft).

### 3. History Optional for Draft, Mandatory for Canonical

**For `type: law`, `model`, `equation`, `experiment`:**
- Draft status: `historical` optional but encouraged
- human_reviewed/canonical status: `historical` MANDATORY with:
  ```yaml
  historical:
    stated_by: "Isaac Newton"
    year: 1687
    where: "Philosophiæ Naturalis Principia Mathematica"
    timeline:
      - year: 1687
        event: "First stated"
        by: "Isaac Newton"
      - year: 1916
        event: "Generalized by Einstein"
        by: "Albert Einstein"
  ```

**For `type: quantity`, `unit`, `concept`:**
- Historical optional always, but if present must have stated_by + year

**Rationale:** Keeps minimal viable schema for draft (can ship quickly), but ensures canonical promotion requires full audit trail for double/triple verification and future change.

### 4. Schema Changes (v2.0 Breaking)

**concept.schema.json v2.0:**
- Add `source_refs: string[]` pattern `^stemma:src\.` — at least 1 required for physics domain, optional for other domains until they adopt physics pattern
- Add to `provenance`: `writer` (string, agent id), `original_author` (string), `link` (string uri), `retrieved_at` (date)
- Make `provenance.source_kind` and `provenance.source` required for physics domain (via profile check, not JSON schema required to avoid breaking other domains)
- Add `historical` as required for law/model/equation when status=human_reviewed/canonical (enforced via profile check)

**connection.schema.json:** No change — evidence already supports source_ref, but make evidence array minItems 1 for physics domain via profile check.

**source.schema.json:** No change — already has authors, url, doi, isbn, year, publisher. Ensure every source has at least url OR doi OR isbn for verifiability.

**extension-registry:** No new extensions — use schema fields, not extensions, for source tracking (source tracking is core, not extension).

### 5. Implementation as Profile Check (v0.1 No Break)

For v0.1 (now), do NOT bump schema_version. Enforce via `physics_core_profile_check.py`:

- Entity checks:
  - `provenance.source_kind` != null
  - `provenance.source` != null and length >10
  - `provenance.writer` != null (new field, check via raw YAML)
  - `provenance.link` != null and is URL
  - `source_refs` array exists and >=1 and each resolves to file in sources/
  - If type in [law, model, equation] and status in [human_reviewed, canonical]: historical must exist with stated_by, year
- Connection checks:
  - evidence array >=1
  - each evidence has source_ref that resolves
  - locator != null
  - stance != null

This allows us to start small with new design without breaking JSON schema yet. Schema bump to 2.0 happens after pilot proves value.

### 6. Wipe and Rebuild

- Delete all existing content (done: 0 entities now)
- Keep schemas, validator, docs, but rewrite docs to reflect mandatory source + history
- Create new templates:
  - `scripts/templates/physics_entity_template.md`
  - `scripts/templates/physics_source_template.yaml`
  - `scripts/templates/physics_connection_template.yaml`
- Seed 3 sources + 3 pilot entities with new dual verification to prove pattern
- Validate, export, status_truth

## Alternatives Considered

- **Embedded only (no canonical sources/):** Rejected — loses single source of truth, duplicates citation data, no versioning of source records.
- **Canonical only (no embedded):** Rejected — requires jumping files for quick check, loses writer/retrieved_at info that is entity-specific.
- **Both mandatory for draft:** Considered but rejected for minimal viability — draft can have embedded only, canonical needs both. User selected "both" for all, so we enforce both even for draft for simplicity.
- **Separate history file per entity:** Rejected — history is part of entity identity for laws, should live in same file as `historical` block, not separate file.
- **Full nuke (delete schemas/docs):** Rejected per user choice nuke_content_only — keep engine, rewrite docs. Full nuke loses ADR history and validator which are valuable.

## Consequences

- Positive: Every claim verifiable via link + canonical record + embedded provenance; triple check possible; history gives progression; future change easy (update source, compare).
- Negative: Higher authoring cost — every entity needs source record + embedded fields. Mitigated by templates and small scope (70 entities).
- Neutral: No immediate schema break — profile check enforces, schema bump later.

## Implementation

See `docs/PHYSICS-MINIMAL-DESIGN-V2.md` for new minimal design from scratch.

## Open Questions

- Should `writer` be agent id (human:curator.001) or free string? Proposal: agent id that resolves in agent-registry.yaml for audit trail.
- Should `link` allow DOI, URL, ISBN? Proposal: URL or DOI, validated as uri.
- Should `source_refs` be required for all entity types or only law/quantity? Proposal: all types for physics.

## Status History

- 2026-09-21: PROPOSED after user clarification
