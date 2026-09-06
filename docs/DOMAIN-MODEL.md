# STEMMA — Domain Model

**Status:** Authoritative (baseline 3.0.0).
**Related:** `docs/SCHEMA-SPECIFICATION.md` (field-level contracts),
`docs/RELATIONSHIP-SPECIFICATION.md` (assertion semantics),
`docs/METADATA-SPECIFICATION.md` (provenance/lifecycle).

---

## 1. Object kinds

The canonical layer has exactly three object kinds:

| Kind | Identity | Lives in | Represents |
|---|---|---|---|
| **Entity** | `stemma:<domain>.<slug>` | `content/**.md` | A node: something knowable (concept, quantity, law, …). |
| **Connection** | `stemma:conn.NNNNNN` | `connections/*.yaml` | An edge: one asserted relationship between two entities. |
| **Source** | `stemma:src.<slug>` | `sources/*.yaml` | A citable origin (paper, textbook, standard, dataset). |

Everything else in the system is either metadata *on* these objects or derived
*from* them.

## 2. Entity types

Nine types are defined (ADR-0004, extended by ADR-0021). Type is immutable: a
different type is a different entity (new ID).

| Type | Represents | Does not represent |
|---|---|---|
| `concept` | A general idea or category (e.g. Force). | A measurement, a law statement, a belief. |
| `quantity` | A measurable property (Mass, Acceleration). | The unit (that is `unit`), a specific measurement. |
| `unit` | A measurement standard (kilogram, m/s²). | The quantity itself. |
| `law` | A general proposition holding under stated conditions (Newton's Second Law). | A formula string (`equation`), a concept. |
| `equation` | A mathematical relation between quantities (F = m·a). | The law's prose statement, the quantities. |
| `misconception` | A common false belief learners hold. | The correct concept; pedagogy. |
| `phenomenon` | An observable occurrence (diffusion, seasons). | Its explanation (that is a `law`/`model` + relations). |
| `model` | An idealized representation (ideal gas, Bohr model). | The phenomenon it models. |
| `experiment` | A canonical experimental setup or observation. | A specific historical event (that is `historical` metadata). |

Current corpus distribution is tracked live by `scripts/status_truth.py` and
published in the README status block.

## 3. Identity model

- **Grammar:** `stemma:<domain>.<slug>`; domains are short ASCII codes
  (`phys`, `chem`, `math`, `bio`, `earth`, `eng`, `practice`); slugs are
  lowercase `[a-z0-9-]`.
- **Immutability:** an ID never changes meaning. Reassignment is detected from
  git history (`check_id_immutability.py`); renaming an entity changes `name`,
  never `id`.
- **Lifecycle events and their identity handling:**

| Event | Rule |
|---|---|
| renamed | `name` changes; ID unchanged. |
| split | New IDs for the parts; original becomes `deprecated` with `deprecated_by` (or documented ambiguity). |
| merged | Survivor keeps its ID; the other is `deprecated` → survivor. |
| replaced | New ID; old `deprecated` → new; new lists old in `aliases`. |
| deprecated | `status: deprecated`; ID reserved forever, never reused. |

- **Namespace history:** the pre-refoundation prefix was migrated to
  `stemma:` in a single governed bulk migration that changed no
  identity-defining field (ADR-0027; details and the guard's alias rule are
  recorded in `docs/MIGRATIONS.md`).

## 4. Assertion model (the heart of the domain)

A **connection** is a reified statement — the claim plus everything known
*about* the claim:

```
stemma:conn.000377
  source      → stemma:phys.newtons-second-law     (entity)
  relation    → mathematically_requires            (registry entry)
  target      → stemma:phys.force                  (entity)
  assertion   → status, type, review, confidence, polarity
  context     → domain, subdomain, regime, scale, assumptions, qualifiers
  evidence[]  → typed citations with stance (supports/refutes)
  provenance  → asserted_by, generated_by, method, reviewed_by[], review_history[]
  lifecycle   → supersession pointers (replaced_by)
```

Semantics (identity of a claim, immutability, supersession, duplicate
detection) are specified in `docs/RELATIONSHIP-SPECIFICATION.md`.

## 5. Provenance and epistemics (summary)

- **Origin** (`provenance`): who/what produced the record, by what method,
  with what machine assistance. Agents resolve in the agent registry.
  `unknown:*` agents are honest attribution for unrecoverable origin —
  allowed on migrated records only.
- **Review** (`assertion.review` + `review_history`): the human authority
  track. States: `unreviewed → reviewed → canonical` (and `rejected`).
  Transitions are forward-only with named reviewer and reason; a state machine
  (`scripts/curation_state.py`) is the only writer.
- **Confidence** (`assertion.confidence` + `confidence_basis`): optional
  uncertainty annotation; never set without its basis.
- **Historical attribution** (`historical`): who first *stated the science*
  and when — distinct from record provenance; truth-conservative when origins
  are contested or independent.

## 6. Lifecycle states

Entities: `draft → machine_validated → human_reviewed → canonical`,
plus terminal `deprecated`/`superseded` (forward-only; a released entity is
never edited in place — it is replaced).

Connections: `proposed/asserted → reviewed → canonical`, or `rejected`
(auditable, never deleted); retirement requires supersession or deprecation.

See `docs/CURATION-PROTOCOL.md` for the review workflow and evidence standards
per relation family.

## 7. Domain invariants

1. No curriculum, grade, course, country, or product semantics in canonical
   data (tested: `tests/curation/test_generality.py`).
2. No relationship data on entities — connections only (tested: validator +
   export contract v2.0).
3. Every reference resolves (entities, sources, successors, agents,
   registry entries) — no dangling pointers anywhere.
4. Review is human: no `unknown:` reviewer, no auto-canonicalization, no
   review transitions without a named human agent.
5. Unknown is `null`, never fabricated (timestamps, confidence, regime).
6. Derived data is marked derived and regenerable byte-for-byte.

## 8. Out of the domain model (consumer responsibilities)

Curriculum mapping and sequencing, pedagogical ordering, assessment,
presentation, localization *strategy* (multilingual identity is defined —
ADR-0009 — but content localization is a consumer concern), analytics, and
any product behavior. STEMMA's export gives consumers stable IDs and explicit
structure to build these on.
