# STEMMA — Metadata Specification

**Status:** Authoritative (baseline 3.0.0). Governs the meaning, ownership,
and lifecycle of every non-knowledge field on canonical objects.
**Related:** `docs/SCHEMA-SPECIFICATION.md` (shape), `docs/DOMAIN-MODEL.md`
§5, ADR-0015/0016/0017/0018/0023.

---

## 1. Taxonomy: what counts as what

| Category | Definition | Examples | Rule |
|---|---|---|---|
| **Data** | The knowledge itself | `definition`, `examples`, `equation` display form | Canonical; the reason the object exists |
| **Relationships** | Claims linking entities | `source/relation/target` triples | Canonical, but ONLY in connections/ |
| **Metadata** | Facts *about the record* | `provenance`, `review`, `version`, `updated_at` | Canonical; governed semantics below |
| **Provenance** | Origin of the record/claim | `asserted_by`, `generated_by`, `method`, `evidence[]` | Agent-anchored; agents resolve in the registry |
| **Derived information** | Computable from canonical data | `claim_signature`, `content_hash`, inverse edges, PageRank | NEVER canonical; always regenerable |
| **Presentation** | How a consumer shows data | colors, ordering, UI copy | Consumer-owned; absent here |
| **Configuration** | How the system runs | `schema/VERSION.yaml`, CI, registries | Repo-owned, not knowledge |
| **Implementation detail** | How code does it | script internals | Never leaks into data or contract |

A field never serves two categories. When a need seems to straddle two, that
is a schema decision → ADR.

## 2. The provenance object

On **entities** (`provenance`): `ai_drafted` (required, boolean),
`source_kind` (controlled: human-authored | textbook | academic-or-research |
institutional | standards-or-specification | ai-assisted-draft | other),
`source` (citation string or null), `reviewer` (agent id or null; required
before `human_reviewed`/`canonical`), `reviewed_at`.

On **connections** (`provenance`): `asserted_by` (agent), `generated_by`
(agent), `method` (authoring | curation | migration | inference), `reviewed_by[]`
(human agents), `review_history[]` (from/to/reviewer/at/reason).

Rules:

1. **Every agent id resolves** in `schema/agent-registry.yaml` (gate-enforced;
   the entry lands in the same PR as first use).
2. **`unknown:` agents are legacy-only** — honest attribution for migrated
   records whose author is unrecoverable. Forbidden on new assertions.
3. **AI assistance is provenance, not authority**: `ai_drafted: true` or an
   `llm:` agent records how content came to be; it never advances review state.
4. **Record origin ≠ scientific origin**: the `historical` block records who
   first stated the claim and when (`stated_by` + `year` required if present;
   optional `where`/`context`/`note`/`timeline`); truth-conservative —
   contested or independent origins are documented, never flattened.
5. **Provenance is append-friendly, edit-hostile**: review history grows;
   existing entries are never rewritten.

## 3. Review and status metadata

Entity `status` and connection `assertion.review.status` are the authority
tracks (states and transitions: DOMAIN-MODEL §6; workflow:
`docs/CURATION-PROTOCOL.md`). Metadata rules:

- A transition without a named human reviewer is invalid (state machine
  enforced).
- Every transition records `at` (ISO-8601 UTC) and `reason`.
- `rejected` is auditable, never deleted.
- Review status is *per assertion*, never per entity batch: reviewing an
  entity does not bless its edges.

## 4. Context metadata (applicability of a claim)

`context` on a connection scopes the claim:

| Field | Vocabulary | Notes |
|---|---|---|
| `domain` / `subdomain` | `schema/vocabularies/{domains,subdomains}.yaml` | Canonical tokens (e.g. `mathematics`, not ad-hoc variants). |
| `regime[]` | `schema/vocabularies/regimes.yaml` | Physical regimes the claim holds in (`classical`, `quantum`, …). Empty = regime-independent *as far as reviewed*. Never stamped speculatively. |
| `scale` | same file | Characteristic scale (`macroscopic`, `atomic`, …). |
| `assumptions[]` / `qualifiers[]` | free strings / qualifier objects | Explicit limits; qualifiers participate in claim identity. |

## 5. Confidence metadata

`assertion.confidence` (number) + `confidence_basis` (string): optional and
paired — one without the other is a gate warning (ADR-0013). Confidence
annotates uncertainty; it never substitutes for review.

## 6. Temporal metadata

- `created_at` / `updated_at`: ISO-8601 or `null` when genuinely unknown.
  **File mtime is never a source** (tested).
- Review timestamps live in `review_history`, single source of truth.
- Derived artifacts carry `content_hash` (`sha256:…`), never `generated_at`
  wall clocks — determinism is a contract (ADR-0022).

## 7. Rights and licensing metadata

- Repository-level: content CC BY 4.0 (`LICENSE`), code MIT
  (`LICENSE-CODE`) — ADR-0001.
- Per-object `rights` blocks exist for overrides/attribution records
  (e.g. a quoted definition with incompatible terms); the validator checks
  shape, governance reviews substance.

## 8. Identity & cross-reference metadata

- `aliases`: historical IDs (valid, resolvable-or-historical, never own id).
- `deprecated_by` / `lifecycle.replaced_by`: succession pointers; must
  resolve.
- `external_ids`: scheme → value(s). Known schemes are format-checked
  (`wd: Q\d+`, `doi`, `orcid`, `isbn`, `qudt`, `ucum`, `cas`); unknown schemes
  allowed (open registry) with a scheme-name pattern. Cross-references point
  outward only — STEMMA never imports external identity.

## 9. Extension metadata

`extensions.*` on any object kind must be **registered** in
`schema/extension-registry.yaml` (name, applies_to, value_type, enum,
description, registered_by, registered_at, status proposed→adopted).
Unregistered keys fail the gate. An extension dimension exists because a
current need required it — not speculative. Registered dimensions today:
`dimensions` (ISQ dimension vector for quantities), `domain_scope`,
`symbol_set` — semantics in the registry itself.

## 10. Metadata the system deliberately does not have

- Grades, levels, audiences, difficulty (curriculum/pedagogy — consumer side).
- Popularity, embeddings, retrieval scores (derived — consumer side).
- Product/feature flags (out of scope entirely).
- Auto-generated summaries in canonical data (derived — belong in views).

## 11. Field audit rule

Every canonical metadata concept must have: a defined purpose, an owner
(governance), a validation rule, and a lifecycle. Fields failing this test are
removed rather than accumulated. The metadata-history ADRs (0016/0017/0018)
and the MIGRATIONS log record how the current set came to be.
