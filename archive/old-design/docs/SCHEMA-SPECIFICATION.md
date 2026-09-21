# STEMMA — Schema Specification

**Status:** Authoritative for `schema_version` 1.2.0 (ADR-0027/0028/0031 + ADR-0043 dual verification).
**Contracts:** `schema/concept.schema.json`, `schema/connection.schema.json`,
`schema/source.schema.json`, `schema/export.schema.json` (JSON Schema
draft 2020-12). This document explains the model; the schemas plus
`scripts/validate.py` are the enforcement.
**Current focus:** Physics-first minimal v2 with mandatory source + history (ADR-0040/0041/0042/0043) — see `docs/PHYSICS-MINIMAL-DESIGN-V2.md`.

---

## 1. Design rules

1. **One envelope schema per object kind.** Entity types share one envelope;
   type-specific semantics live in the domain model and relation registry, not
   in per-type schemas. This keeps the schema surface small and evolution
   cheap.
2. **Strict where identity or integrity is at stake** (id patterns, required
   fields, `additionalProperties: false` on metadata objects), **open where
   growth is expected** (`extensions`, `external_ids` unknown schemes).
3. **Optional means optional with a null contract**: absent or `null`, never a
   placeholder or fabricated value.
4. **Versioned as a unit.** `schema_version` covers all four schemas and lives
   in one place (`schema/VERSION.yaml`); version literals in code are
   forbidden.
5. **Breaking vs additive.** Adding an optional property or enum value is
   additive. Changing/removing a field, narrowing a type, or changing ID
   grammar is breaking: major bump + ADR + `docs/MIGRATIONS.md` entry
   describing what old data does.

## 2. Identity and file grammar

| Object | ID pattern | File rule | Example |
|---|---|---|---|
| Entity | `^stemma:[a-z][a-z0-9-]*\.[a-z0-9][a-z0-9-]*$` | `content/<domain>/<subdomain>/<slug>.md`; filename = final ID segment; id-prefix → domain/directory mapping = `schema/id-domain-map.yaml` (ADR-0034) | `stemma:phys.force` → `content/physics/mechanics/force.md` |
| Connection | `^stemma:conn\.[0-9]{6}$` | `connections/<id-minus-namespace>.yaml` (colon-free) | `stemma:conn.000001` → `connections/conn.000001.yaml` |
| Source | `^stemma:src\.[a-z0-9][a-z0-9-]*$` | `sources/<id-minus-namespace>.yaml` | `stemma:src.cavendish-1798` → `sources/src.cavendish-1798.yaml` |

Rules enforced by the gate:

- IDs globally unique; never reused; filename↔ID consistency checked.
- Entity YAML frontmatter is parsed **strictly** — duplicate YAML keys are a
  hard error (silent last-wins is a data hazard).
- The retired pre-refoundation namespace may never reappear in canonical
  files (migration-completeness guard; see `docs/MIGRATIONS.md`).
- Connection IDs are sequential and opaque; they encode no semantics.

## 3. Entity envelope (concept.schema.json) — v1.2.0 Physics-First Minimal

Required: `id`, `type`, `name`, `domain`, `status`, `definition`, `provenance`.

| Field | Type | Purpose | v2 Mandatory? |
|---|---|---|---|
| `id` / `type` / `name` / `domain` / `status` | — | Identity and lifecycle (see DOMAIN-MODEL §2–3, §6). | Yes |
| `subdomain` | string \| null | Subdomain e.g. mechanics, per vocabularies/subdomains.yaml (ADR-0034, ADR-0040) | Yes for physics |
| `definition` | string | Curriculum-agnostic definition. The core knowledge payload. | Yes |
| `symbol` / `equation` / `unit` | string \| null | Display forms (ADR-0010), machine truth via ADR-0024 later | Optional but needed for physics |
| `source_refs` | id[] | Canonical source records `stemma:src.xxx` — dual verification with embedded provenance (ADR-0043). At least 1 required for physics-core. | **Yes for physics** |
| `provenance` | object | Record origin + dual verification (see below) | Yes, with new subfields |
| `provenance.source_kind` | enum | textbook / academic-or-research / standards-or-specification / etc. | **Yes** |
| `provenance.source` | string | Embedded citation with page — quick check | **Yes** |
| `provenance.writer` | string | Agent id who wrote file e.g. human:curator.001 — audit trail (ADR-0043) | **Yes** |
| `provenance.original_author` | string | Who originally stated science (distinct from writer) | **Yes** |
| `provenance.link` | string | URL/DOI to source for triple-check | **Yes** |
| `provenance.retrieved_at` | string | ISO date when link accessed | **Yes** |
| `historical` | object | Scientific first-attribution + timeline — optional for draft, **mandatory for law/model/equation when human_reviewed/canonical** (ADR-0043) | Conditional |
| `external_ids` | map | Wikidata, QUDT, UCUM etc. | Optional |
| `aliases` / `deprecated_by` / `examples` / `version` / `updated_at` / `rights` / `extensions` | — | Bookkeeping | Optional |
| `common_misconceptions` / `learning_objectives` / `real_world_applications` / `key_experiments` | — | Pedagogical — **forbidden for physics-core** per ADR-0041 | No |

**Explicitly absent:** any relationship array (ADR-0028), and any scoping
field (grade, curriculum, course, country, product) — structurally excluded
and tested.

Minimal valid entity v2 (physics-first with dual verification):

```markdown
---
id: stemma:phys.example
type: quantity
name: Example Quantity
domain: physics
subdomain: mechanics
status: draft
definition: >-
  A curriculum-agnostic definition with source.
symbol: m
unit: kilogram (kg)
provenance:
  ai_drafted: false
  source_kind: textbook
  source: >-
    Halliday Resnick Walker 12th ed. Ch 5, p112: definition
  writer: human:curator.001
  original_author: Halliday, Resnick, Walker
  link: https://www.wiley.com/...
  retrieved_at: "2026-09-21"
source_refs:
  - stemma:src.halliday-resnick-walker-12th
external_ids:
  wd: Q11423
---

## Notes

Triple-checkable: embedded source vs canonical record vs external link.
```

## 4. Connection envelope (connection.schema.json)

Required: `id`, `type: connection`, `source`, `relation`, `target`,
`assertion`, `provenance`.

| Block | Contents | Notes |
|---|---|---|
| `source` / `relation` / `target` | The claim triple | Immutable for the life of the ID (guard-enforced from git history). |
| `assertion` | `status` (active/superseded/…), `type` (proposed/asserted/inferred), `review.status`, `confidence` (+`confidence_basis`), `polarity` | Epistemic state of the claim. |
| `context` | `domain`, `subdomain`, `regime[]`, `scale`, `assumptions[]`, `qualifiers[]` | Applicability of the claim; vocabularies in `schema/vocabularies/`. |
| `evidence[]` | typed citation (`source_ref` → `sources/`, locator, description) + `stance` | What supports/refutes the claim. |
| `provenance` | `asserted_by`, `generated_by`, `method`, `reviewed_by[]`, `review_history[]` | Full agent-anchored origin + review trail. |
| `inference` | rule/path when `assertion.type: inferred` | Mutually exclusive with asserted provenance (ADR-0014). |
| `lifecycle` | `replaced_by` | Supersession pointer to the correcting connection. |
| `created_at` / `updated_at` | ISO-8601 \| null | `null` when genuinely unknown — never file mtime. |
| `validity` / `rights` / `extensions` | optional | Scoped semantics; see METADATA-SPECIFICATION. |

Semantics (claim identity/signatures, duplicate rules, supersession) are in
`docs/RELATIONSHIP-SPECIFICATION.md`.

## 5. Source envelope (source.schema.json)

Required: `id`, `type` (`textbook` | `academic-paper` | `standard` |
`institutional` | `other`), `citation`.

Optional bibliographic fields (`title`, `authors`, `year`, `doi`, `url`,
`isbn`, `journal`, `volume`, `edition`, `language`, `source_role`,
`accessed_at`, `license`, `locator_authority`, `rights`, `extensions`).
Unknown metadata is `null`, never guessed. Sources are *records*, not a
bibliography project: they exist so evidence has something to point at.

## 6. Export contract (export.schema.json)

`exports/knowledge.json` is the consumer contract (v2.1.0, ADR-0032):

- Required members: `export_version`, `schema_version`, `content_hash`,
  `entity_count`, `connection_count`, `source_count`, `entities[]`,
  `connections[]`, `sources[]`.
- Optional semantic sidecar: `relation_registry_version`
  (`schema/VERSION.yaml`), `relation_registry` (relation name →
  family/inverse/transitive/symmetric/domain/range/status), and
  `vocabularies` (`domains`/`subdomains`/`regimes`/`scales`). A present
  `relation_registry` is authoritative: consumers must fail closed on a
  connection relation that is not declared.
- `entities[]` carry **no** relationship data; the graph is `connections[]`
  only.
- `connections[]` carry the derived `claim_signature`.
- Deterministic: content-hash stamped, no wall clock; byte-identical
  regeneration is CI-enforced.
- The producer validates the payload against the contract **before writing** —
  a violating export cannot ship.

Review-policy views (`knowledge.{all,reviewed,canonical,trusted,proposed,rejected}.json`)
and the derived-graph view (`knowledge.extended.json`) inherit versions from
`schema/VERSION.yaml`.

## 7. Evolution and compatibility

- Additive change → patch/minor bump; no migration needed.
- Breaking change → major bump + ADR + MIGRATIONS entry naming the rewrite (if
  any) and consumer impact.
- Compatibility promise to consumers is expressed through `export_version`
  only: consumers pin the contract, not the content. Content growth is never a
  breaking change.
- Every landed migration is listed in `docs/MIGRATIONS.md` (append-only).

## 8. Open items requiring human decision

| Item | Status |
|---|---|
| Public IRI base for schema `$id`s (currently the reserved `stemma.example` placeholder) and for published IDs | **Unresolved — human decision** (blocker: domain/organization ownership; recorded in ADR-0029) |
| Math layer (machine-parseable equations, dimensions, unit entities) | Proposed in ADR-0024, awaiting human gate |
