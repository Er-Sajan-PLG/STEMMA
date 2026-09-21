# DECISION 0018 — Historical scientific attribution (who + when + timeline)

- **Date:** 2026-09-01
- **Status:** decided (implemented with this PR)
- **Related:** decisions 0006 (provenance), 0010, 0017; `docs/STEMMA-SPECIFICATION.md` §8;
  `docs/SOURCES.md`; `schema/concept.schema.json`

## Context

LearningHubSTEM is a canonical STEM knowledge foundation. It carries 149 entities with
`provenance.source` citations, but **no structured record of the historical origin of a
scientific claim** — who first stated a law, principle, or discovery, and when. That is a
different question from record provenance:

- `provenance` answers *"where did this entity's content come from / who reviewed it?"* —
  the **source of the record** (textbook, standard, AI draft).
- historical attribution answers *"who first stated this scientific claim, in what work,
  and when?"* — the **scientific origin of the idea**.

Without it, a consumer cannot easily render "Newton's Second Law, stated by Isaac Newton in
*Principia* (1687)", nor can an educator distinguish a claim's origin from where this
particular phrasing was sourced. This matters for the foundation's credibility and for AI
consumers that synthesize "when and by whom was this discovered".

## Decision

Add an **optional, additive `historical` field** on canonical **entities** (not connections),
captured **on the entity that states the claim** (typically a `law`, `equation`, or a
`concept`/`quantity` that names a specific discovery). Shape:

```yaml
historical:
  stated_by: "Isaac Newton"                    # person/group who first stated it (required)
  year: 1687                                   # year of first publication/statement (required)
  where: "Philosophiæ Naturalis Principia Mathematica"   # optional working/source
  timeline:                                    # optional ordered list of milestones
    - year: 1687
      by: "Isaac Newton"
      event: "First stated the three laws of motion in Principia"
    - year: 1686
      event: "Derivation of inverse-square gravitation"
  context: "Mechanics; classical physics"      # optional domain note
  note: "Any clarifying prose, uncertainty, or attribution caveat"  # optional
```

Rules:

- `historical` is **optional** and **backward-compatible** (`schema_version` stays `0.2`,
  `export_version` stays `0.1`). Absent = no origin recorded (common for general concepts).
- `stated_by` and `year` are **required when the field is present**. `year` is an integer
  (CE; negative for BCE). `timeline[].year` is an integer, `timeline[].by` optional
  (defaults to `stated_by`), `timeline[].event` required.
- **Truth conservative:** record what is historically documented; where attribution is
  contested or approximate, say so in `note` rather than asserting a false precision.
  Do **not** fabricate a single "first" origin when a discovery was independent/multiple.
- It resides on the **canonical entity** as knowledge-layer metadata (intrinsic to the idea),
  consistent with the ADR-0010 extensions. It is **not** curriculum/pedagogy.
- `provenance` remains the record-source model; `historical` is the claim-origin model. They
  are distinct fields with distinct semantics.

## Alternatives considered

- **Reuse `provenance`**: rejected — `provenance.source`/`source_kind` already mean "where
  this entity text came from"; conflating the origin of the *record* with the origin of the
  *scientific claim* would blur auditability.
- **An extension-registry slot (ADR-0017)**: rejected for the rich structured shape
  (person + year + timeline[] + where). ADR-0017 slots are single scalar values; a
  structured historical block belongs as a first-class entity field, not squeezed into a
  scalar extension.
- **Free prose in `definition`**: rejected — not machine-readable for consumers.

## Reason

Traceability of scientific origin is core credibility for a canonical knowledge foundation
and a hard requirement for AI consumers that must answer "who/when discovered this". A
structured, conservative, optional field delivers this without a breaking schema change and
without inventing false attribution.

## Consequences

- `concept.schema.json` gains an optional `historical` object; `schema_version`/`export_version`
  unchanged (additive).
- `scripts/validate.py` gains a light `check_historical()` (present ⇒ `stated_by`+`year`;
  integer years; timeline shape). No fabricated attribution: field absent where unknown.
- `docs/SOURCES.md` lists the source-of-content inventory and, for key historic statements,
  records the historical origin `who` + `when`.
- Historic-law entities (Newton's laws, Coulomb, Ohm, conservation of energy, etc.) and key
  discoveries (photoelectric effect, Bohr model, Big Bang) gain a `historical` block.
- README and specification §8 document the new field.

## Status

**decided (implemented with this PR).**