# ADR-0056: `adopted_from` — Explicit Adoption Provenance in the Export Contract

Status: Decided — 2026-10-01
Date: 2026-10-01
Decided by: Sajan (sole owner), ruling on REQ-STEMMA-EXP-002 acceptance criterion 4
(human ruling: "widen + mutation-test and implement adopted_from").
Relates to: ADR-0032 (introspection sidecars), ADR-0044 (integrated foundation v2),
ADR-0049 (delegated authority v2), ADR-0050 (contract 2.2.0), ADR-0016 (external_ids),
ADR-0018 (`historical` attribution), REQ-STEMMA-EXP-002, UNRES-STEMMA-CORE-002
Amended by: nothing yet.

## Context

REQ-STEMMA-EXP-002 (revision 2) requires, in criterion 4:

> every entity with a merge/adoption history entry exposes an adopted-from provenance field
> (external identifier + relation) in the export

Verification of EXP-002 on 2026-10-01 returned **FAILED on criterion 4 of 4** (criteria 1–3
PASSED). The finding was blunt: *no `adopted_from` field exists in `concept.schema.json` or
`export.schema.json`, and there is no merge/adoption history mechanism.* The criterion was
unimplementable as written.

The gap is real and not merely nominal. STEMMA already records two neighbouring things, and
neither is adoption provenance:

| Field | Records | Does NOT record |
|---|---|---|
| `external_ids` | which external thing this entity **is** (identity anchor, e.g. `wd: Q11573`) | that an adoption *happened*, from what, or how strongly the terms match |
| `provenance` | where the **content** came from (source, writer, reviewer) | anything about identity or re-identification |
| `historical` | who **first stated** the science, and when | adoption between identifier systems |

So an entity could carry `external_ids: {wd: Q11573}` and be indistinguishable from an entity
that was *adopted wholesale* from Wikidata under a new STEMMA identifier. The act of adoption —
the thing OBO Foundry Principle 8 demands be declared — was invisible.

Why this matters beyond bookkeeping: the strengthened 2026 OBO requirement (OBO Foundry
Newsletter #10, 2026-04-13; `EVID-STEMMA-EXP-008`) treats provenance as **required, not
optional**, metadata for adopted terms, enforced via the OBO Dashboard. STEMMA's
`IDENTIFIER-POLICY` already treats identity as first-class; leaving adoption implicit left a
hole in exactly the layer consumers must be able to trust.

Two courses were open: **implement the field**, or **defer it to a later ADR and weaken
criterion 4**. The owner chose to implement. This ADR records that decision and its shape.

## Decision

### 1. Add an optional `adopted_from` object to canonical entities

Declared in `schema/concept.schema.json` (closed object; `additionalProperties: false`):

| Key | Required | Meaning |
|---|---|---|
| `external_id` | **yes** | the origin identifier, `scheme:value` (e.g. `wd:Q11402`, `obo:UO_0000008`) or a bare `stemma:` entity id for intra-STEMA adoption |
| `relation` | **yes** | how the adopted term relates to its origin (closed enum, below) |
| `source_external_ids` | no | extra anchors of the origin (e.g. its DOI/ORCID), for provenance depth |
| `note` | no | human-readable adoption rationale or known divergence |
| `adopted_at` | no | ISO date the adoption was recorded |
| `authority` | no | `internal` \| `delegated` (ADR-0049) — who ratified the adoption |

`relation` is a **closed** enum, SKOS-shaped plus two STEMMA-specific cases:

- `exact_match`, `close_match`, `broad_match`, `narrow_match` — SKOS mapping properties;
- `reidentification` — same entity, new identifier (nothing semantically new was learned);
- `merge` — two or more prior entities were unified into this one.

### 2. Project it into the export

Declared in `schema/export.schema.json` under `entities[].adopted_from`, same closed shape.
Criterion 4 is an **export** criterion: a field enforced only in the canonical schema but never
projected would satisfy the letter of the canonical contract while failing consumers. Both
schemas must declare it, and a test asserts exactly that.

### 3. Enforce it in the validator, not by convention

`scripts/validate.py` gains `check_adopted_from()`, mirroring `check_historical()` (ADR-0018):

- rejects a non-object, a missing/empty `external_id`, a `relation` outside the enum;
- rejects non-string `note`/`adopted_at`, an `authority` outside `internal|delegated`;
- rejects **unknown keys** via a closed `ADOPTED_FROM_KEYS` set — defence in depth, so the
  reason is legible and the check survives a caller that validates without the schema pass.

**Absence is legal and is the majority case.** An absent `adopted_from` means "no adoption to
report", never "unknown, fill it in". A guard that demanded the field everywhere would force
fabricated provenance — the same reasoning ADR-0018 applies to `historical`.

### 4. Mutation-tested, not merely declared

`tests/metadata/test_adoption_provenance.py` carries positive shape checks, a
schema-declaration check for **both** schemas, negative cases feeding nine malformed variants
through the real `check_adopted_from`, a negative control asserting valid records are *not*
rejected, and an absence-is-legal check. Injecting `relation: sort_of_ish` or dropping
`external_id` into a real entity is rejected by `validate.py` with exit 1 and a named error.

## Consequences

**Easier.** A consumer can now ask "was this term adopted, from where, and how strongly
matched?" without cloning the producer — the same goal ADR-0032 set for the relation registry.
Consumers that ignore the field read the export exactly as before; the change is **additive**,
so `export_version` does **not** bump (stays `2.2.0`). This is what "evolve additively within
a major version" (EXP-002's own statement) is supposed to look like.

**Harder.** There is now one more optional block to keep coherent, and the closed `relation`
enum needs an ADR amendment to extend — deliberately, since a silent widening of adoption
semantics is precisely the kind of change that should not be additive-by-default.

**Hard to undo.** Once consumers branch on `adopted_from`, removing it is a breaking change.
Mitigated by it being optional and closed.

**Explicitly NOT decided here.** No mechanism is added to *derive* adoption from a merge
history; the record is authored, not inferred. Auto-derivation from identifier churn would need
its own ADR, and doing it silently would manufacture provenance — the failure mode this whole
line of work exists to prevent.

## Verification

- `adopted_from` present in `concept.schema.json` and `export.schema.json`, both closed
  (`additionalProperties: false`) — asserted by `test_schema_declares_adopted_from`.
- Valid record on a real entity survives `scripts/validate.py` (exit 0) and appears in
  `exports/knowledge.json` — demonstrated 2026-10-01.
- Malformed records (missing `external_id`, illegal `relation`, unknown key, bad `authority`,
  non-string `note`, wrong type) each rejected with a named error
  (`test_validator_rejects_malformed_adopted_from`).
- Valid records and the absent case are **not** rejected — the negative control.
- Export contract unchanged for existing consumers: `exports/knowledge.json` byte-identical
  before and after the schema addition.

## Related

- ADR-0018 — `historical` attribution (the shape this field mirrors)
- ADR-0016 — `external_ids` (identity anchoring, distinct from adoption provenance)
- ADR-0049 — delegated authority (`authority` key)
- ADR-0050 — contract 2.2.0 (the additive-evolution precedent)
- REQ-STEMMA-EXP-002 criterion 4 — the requirement this satisfies
- `EVID-STEMMA-EXP-008` — OBO Foundry Principle 8 (external precedent)
