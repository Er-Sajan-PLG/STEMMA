# DECISION 0034 — Domain identity enforcement (id-domain-map)

- **Date:** 2026-09-06
- **Status:** decided & implemented
- **Related:** ADR-0003 (identity), ADR-0021 (vocabularies), ADR-0027
  (`stemma:` namespace), `docs/SOTA-REVIEW.md` §0.2 (T3).

## Context

The immutable `stemma:<prefix>.<slug>` ID, the scalar `domain` field, and the
`content/<directory>/` path are three representations of one identity. Before
this change they could disagree silently (one real case:
`content/earth-space/.../our-environment.md` with id `stemma:phys.our-environment`,
domain `physics`). Consumers can't trust a domain lookup if the ID, field, or
path disagree.

## Decision

- **New `schema/id-domain-map.yaml`** is the single source of truth for
  `id-prefix → canonical domain + content directory`.
- **Both `epist` and `practice` map to `scientific-practice`** for now, with
  `legacy: true`; a later migration to one prefix is an identity change
  requiring an ADR + alias migration, not this change.
- **Hard `ERROR` gate** (before export, `scripts/validate.py`):
  - id prefix not in the map;
  - prefix→domain != entity `domain`;
  - entity file path directory != map `directory`;
  - entity `domain` not in `schema/vocabularies/domains.yaml`.
- **The map itself is coherence-checked**: domain must be in the domains
  vocabulary and directory must exist under `content/`.
- **`stemma:phys.our-environment` is relocated** from
  `content/earth-space/atmosphere-climate/` to
  `content/physics/thermal-physics/` (its ID and domain are already `phys` /
  `physics`; only the path was wrong). The immutable ID is never changed; a
  file move is not an identity change.

## Alternatives considered

- **Only validate `domain` against `domains.yaml`.** Rejected: the ID/path
  disagreement stays invisible.
- **Only validate the path prefix.** Rejected: the domain field can still lie.
- **Change the ID to `earth.our-environment`.** Rejected: `stemma:` IDs are
  immutable; identity errors must be fixed by relocating/adjusting metadata,
  never by reassigning an ID.

## Consequences

- `schema/id-domain-map.yaml` (new), `scripts/validate.py` checks,
  `content/` relocation, `tests/registry/test_domain_identity.py`,
  `scripts/verify_all.py` step, docs/MIGRATIONS + ADR.
- Schema/export versions unchanged (gate + content-path change only). No
  canonical object shape changed, no consumer contract change.
