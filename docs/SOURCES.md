# SOURCES — Where STEMMA content comes from

**Status:** consumer-visible source & attribution inventory
**Date:** 2026-09-01
**Related:** `docs/METADATA-SPECIFICATION.md` (provenance semantics),
  `docs/decisions/0018-historical-attribution.md` (who + when), `schema/source.schema.json`.

> Every canonical entity in `content/` records its **provenance** — where the entity's
> content was sourced — in its YAML frontmatter (`provenance.source`, `provenance.source_kind`).
> This document makes that attribution visible in one place: the source classes in use, the
> key source works cited, and (for historically significant statements) **who first stated
> the claim and when** (the `historical` field, ADR-0018).

---

## 1. What "source" means here

Two distinct attributions are recorded (see ADR-0018 for the distinction):

| Field | Answers | Semantics |
|-------|---------|-----------|
| `provenance.source_kind` + `provenance.source` | *"Where did this entity's record come from?"* | **Record source** — the standard/textbook/citation the content was drawn from. |
| `historical.stated_by` + `historical.year` (+`timeline`) | *"Who FIRST stated this scientific claim, and when?"* | **Scientific origin** — the person and publication that established the idea. |

Both are **canonical, knowledge-layer metadata** on the entity. Neither is curriculum or
pedagogy; neither implies a grade.

---

## 2. Source classes in use (provenance.source_kind)

Measured across all 149 entities with an explicit source citation (224 total entities;
entities without a named source default to `ai-assisted-draft` / `other`).

| Source class | Entities | Meaning |
|--------------|----------|---------|
| `standards-or-specification` | 104 | Drawn from a curriculum standard, framework, or specification (e.g. NCTM, IUPAC, NGSS). |
| `textbook` | 36 | Drawn from a named textbook (e.g. Halliday & Resnick, Atkins, Campbell). |
| `academic-or-research` | 7 | Drawn from a research paper or primary study (e.g. Cavendish 1798, Lindeman). |
| `institutional` | 2 | Drawn from an institution's authoritative reference (USGS, NSF, WHO-style bodies). |

**Directive (operational):** authors prefer *standards or primary-treatise* citations over
unverifiable web sources. Every `historical` attribution must be conservative — do not
fabricate a "first" origin when a discovery was independent or contested; record
uncertainty in `historical.note`.

---

## 3. Key source works cited

The most-frequently cited provenance sources across content:

| Source | Kind | Domain(s) |
|--------|------|-----------|
| IUPAC Compendium of Chemical Terminology (incl. Gold Book) | standards | chemistry |
| Atkins' Physical Chemistry | textbook | chemistry |
| Halliday, Resnick & Walker — Fundamentals of Physics | textbook | physics |
| Campbell Biology | textbook | biology |
| NCTM Principles and Standards / ICSE / Common Core | standards | mathematics |
| International Union of Biological Sciences (+ UNESCO framework) | standards | biology |
| Guyton and Hall — Textbook of Medical Physiology | textbook | biology (physiology) |
| NOAA / WMO Atmospheric Science Standards | standards | earth-space |
| NASA Earth / IAU Astronomy Education frameworks | standards | earth-space |
| OECD PISA / NGSS (epistemic knowledge, science practices) | standards | scientific-practice |
| Charles Darwin — The Origin of Species (1859) | academic | biology (evolution) |
| Cavendish, H. — Experiments to determine the density of the Earth (1798) | academic | physics |

Canonical source records live in `sources/*.yaml` (schema: `schema/source.schema.json`) — the
structured bibliographic objects referenced (via `evidence[].source_ref`) by the connection layer.

---

## 4. Historical attribution — who stated it, and when

Per ADR-0018, historically significant laws and discoveries carry a `historical` block with
`stated_by`, `year`, optional `where`, and an optional `timeline[]`. **40 entities** currently
carry one. The full set (id → year, stated_by):

| Canonical ID | Year | Stated by |
|--------------|------|-----------|

**Mathematics**
| `stemma:math.pythagorean-theorem` | c.−530 | Pythagoras (traditionally attributed); known to earlier Babylonians |
| `stemma:math.quadratic-equation` | c.−2000 | Babylonian mathematics (earliest known) |
| `stemma:math.fundamental-theorem-of-calculus` | 1666 | Isaac Newton & Gottfried Leibniz (independent) |
| `stemma:math.logarithmic-function` | 1614 | John Napier (with Henry Briggs) |
| `stemma:math.exponential-function` | 1748 | Leonhard Euler (formalized eˣ) |
| `stemma:math.complex-number` | 1545 | Gerolamo Cardano (first use); Wessel, Argand, Gauss (geometry) |
| `stemma:math.probability` | 1654 | Blaise Pascal & Pierre de Fermat |
| `stemma:math.standard-deviation` | 1893 | Karl Pearson |
| `stemma:math.matrix` | 1858 | Arthur Cayley |

**Physics**
| `stemma:phys.newtons-first-law` / `second-law` / `third-law` / `law-of-gravitation` | 1687 | Isaac Newton (Principia) |
| `stemma:phys.work-energy-theorem` | 1687 | Derived from Newton's laws (foundation) |
| `stemma:phys.conservation-of-energy` | 1847 | Hermann von Helmholtz (consolidation); earlier empirical work by Joule, Mayer |
| `stemma:phys.coulombs-law` | 1785 | Charles-Augustin de Coulomb |
| `stemma:phys.ohms-law` | 1827 | Georg Simon Ohm |
| `stemma:phys.photoelectric-effect` | 1905 | Einstein (explanation); Hertz (observation, 1887) |
| `stemma:phys.bohr-model` | 1913 | Niels Bohr |
| `stemma:phys.nuclear-fission` | 1938 | Hahn & Strassmann (experiment); Meitner & Frisch (explanation) |

**Chemistry**
| `stemma:chem.periodic-table` | 1869 | Dmitri Mendeleev (with Lothar Meyer independently) |
| `stemma:chem.acid` | 1923 | Brønsted & Lowry (model); Arrhenius earlier (1884) |
| `stemma:chem.le-chateliers-principle` | 1884 | Henri-Louis Le Chatelier |
| `stemma:chem.alkane` | 1830 | Recognition of the paraffin (alkane) series |
| `stemma:chem.alkene` | 1860 | Recognition of the ethylene class (Erlenmeyer) |
| `stemma:chem.electrochemical-cell` | 1800 | Alessandro Volta |
| `stemma:chem.electrolysis` | 1834 | Michael Faraday (laws of electrolysis) |
| `stemma:chem.enthalpy` | 1909 | Heike Kamerlingh Onnes (coined "enthalpy") |
| `stemma:chem.entropy` | 1865 | Rudolf Clausius |
| `stemma:chem.gibbs-free-energy` | 1876 | Josiah Willard Gibbs |

**Biology**
| `stemma:bio.cell` | 1665 | Robert Hooke (discovery); Schleiden & Schwann (cell theory, 1839) |
| `stemma:bio.nucleus` | 1831 | Robert Brown |
| `stemma:bio.natural-selection` | 1859 | Charles Darwin (with A. R. Wallace independently, 1858) |
| `stemma:bio.gene` | 1909 | Wilhelm Johannsen (coined "gene") |
| `stemma:bio.chromosome` | 1888 | Heinrich Waldeyer (named); T. H. Morgan (inheritance link) |
| `stemma:bio.meiosis` | 1876 | Hertwig & van Beneden (description); Farmer & Moore (term) |
| `stemma:bio.dna` | 1953 | James Watson & Francis Crick (double helix) |
| `stemma:bio.ecosystem` | 1935 | Arthur Tansley |
| `stemma:bio.cellular-respiration` | 1937 | Hans Krebs (citric-acid cycle) |
| `stemma:bio.photosynthesis` | 1779 | Cumulative (Priestley, Ingenhousz, van Niel) |

> Every row reflects a `historical` block actually present on the entity. Attribution is
> **truth-conservative**: contested or multiple/independent origins are recorded with a `note`,
> never falsely ascribed. The check
> `tests/metadata/test_historical_attribution.py` enforces that all 11 law entities carry
> who+when. If an entity has no documented single origin, the field is absent rather than
> fabricated.

---

## 5. Why this lives outside `content/`

The **canonical** source/attribution data lives **on the entities** (`content/*.md`) — that is
the source of truth. This document is a **derived, consumer-visible inventory** that people
can read without parsing every file. It is regenerable/updatable when content changes and is
**not** authoritative on its own — the entity frontmatter and `schema/` are authoritative.

---

## 6. Relevant files

- `schema/concept.schema.json` — entity schema incl. `provenance` and `historical`.
- `schema/source.schema.json` — canonical source-object schema.
- `scripts/validate.py` — validates `provenance`, `extensions`, and `historical`.
- `tests/metadata/test_historical_attribution.py` — enforces who+when on historic laws.