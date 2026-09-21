# PHYSICS MINIMAL DESIGN V2 — From Scratch, Small, With Full Provenance

**Date:** 2026-09-21
**Status:** PROPOSED — redesign from scratch, nuke_content_only scope
**Related:** ADR-0040/0041/0042/0043, PHYSICS-FIRST-IMPLEMENTATION-PLAN.md, VISION.md, DOMAIN-MODEL.md
**Goal:** Get rid of old content, keep engine, rebuild minimal physics foundation where every entity/claim has source, link, writer for double/triple verification + history timeline for laws.

---

## 1. Why Nuke Content Only (Not Full Nuke)

User selected `nuke_content_only`:
- Delete `content/**`, `connections/*`, `sources/*`, `exports/*` → 0 entities (done)
- Keep `schema/`, `scripts/validate.py`, `docs/` → engine stays, no need to rebuild validator
- Rewrite docs to reflect new mandatory source + history rules

This preserves:
- JSON Schemas (4 files) + registries (relation, agent, extension)
- Gate (validate.py) + history guards + review state machine
- ADRs (history of decisions)
- Explorer + adapter (consumers)

But content restarts small with new design.

---

## 2. New Minimal Entity Schema (Physics-First)

### 2.1 Required Fields (All Entities)

```yaml
id: stemma:phys.<slug>          # stable, never reused
type: quantity | unit | law | equation | concept | model | phenomenon
name: "Human readable"
domain: physics
subdomain: mechanics | electricity-magnetism | thermal-physics | measurement-units
status: draft | human_reviewed | canonical
definition: "Curriculum-agnostic, verifiable definition, 1-3 sentences"
```

### 2.2 Mandatory Provenance + Dual Source Verification (NEW)

```yaml
provenance:
  ai_drafted: false              # bool, required
  source_kind: textbook | academic-or-research | standards-or-specification | institutional
  source: "Halliday Resnick Walker 12th ed. Ch 5, p112: 'Mass is...'"  # embedded citation
  writer: human:curator.001      # NEW: who wrote this file (agent id)
  original_author: "Halliday, Resnick, Walker"  # NEW: who originally stated science
  link: "https://www.wiley.com/en-us/Fundamentals+of+Physics%2C+12th+Edition-p-9781119801128"  # NEW: URL/DOI
  retrieved_at: "2026-09-21"     # NEW: when source accessed
  reviewer: null                 # for draft
  reviewed_at: null

source_refs:                     # NEW: canonical source records, dual verification
  - stemma:src.halliday-resnick-walker-12th
  - stemma:src.nist-si-brochure-9th

symbol: m                        # optional but needed for physics
unit: kilogram (kg)              # display string until ADR-0024
external_ids:
  wd: Q11423
  qudt: quantitykind-Mass
```

**Dual verification:**
- Embedded `provenance.source` + `link` + `writer` = quick check without leaving file
- Canonical `sources/src.xxx.yaml` + `source_refs` = authoritative bibliographic record, versioned, with authors[], year, publisher, url/doi/isbn
- Later triple check: compare embedded vs canonical vs external link; if mismatch, flag for review

**Validation rule (profile check):**
- `source_kind`, `source`, `writer`, `link`, `retrieved_at` must be present and non-empty
- `source_refs` array >=1 and each id must have file in `sources/`
- Each source file must have url OR doi OR isbn

### 2.3 History — Optional for Draft, Mandatory for Canonical (Law/Model/Equation)

```yaml
# For quantity, unit, concept: optional
# For law, model, equation, experiment: optional for draft, MANDATORY for human_reviewed/canonical

historical:
  stated_by: "Isaac Newton"
  year: 1687
  where: "Philosophiæ Naturalis Principia Mathematica"
  context: "Classical mechanics, inertial frames"
  timeline:
    - year: 1687
      event: "First stated as Lex II"
      by: "Isaac Newton"
    - year: 1749
      event: "Reformulated as F=ma by Euler"
      by: "Leonhard Euler"
    - year: 1916
      event: "Limited to non-relativistic regime by GR"
      by: "Albert Einstein"
```

**Why optional for draft?** Minimal viable schema — can ship draft quickly without full history research, but canonical promotion requires full audit trail for verification and future change.

**Enforcement:**
- If `type in [law, model, equation, experiment]` and `status in [human_reviewed, canonical]` and `historical` missing → ERROR

### 2.4 What is NOT in Minimal Schema (Still Forbidden)

Per ADR-0041:
- `learning_objectives`, `real_world_applications`, `key_experiments`, `common_misconceptions` — forbidden for physics core (pedagogy, consumer side)
- `examples` — allowed max 1, knowledge-layer only

---

## 3. New Minimal Connection Schema (Every Claim Has Source)

```yaml
id: stemma:conn.000001
type: connection
source: stemma:phys.newtons-second-law
relation: mathematically_requires  # only from minimal set ADR-0042
target: stemma:phys.mass

assertion:
  status: active
  type: asserted
  review:
    status: unreviewed
  confidence: 1.0
  confidence_basis: expert_review

context:
  domain: physics
  subdomain: mechanics
  regime: [classical]
  assumptions: [non-relativistic, constant-mass]

evidence:  # MANDATORY >=1 for physics-core, even for draft
  - type: textbook
    stance: supports
    source_ref: stemma:src.halliday-resnick-walker-12th  # must resolve
    locator: "Ch 5, Eq 5-1, p112"
    locator_struct:
      page: "112"
      section: "5-2"
      equation: "5-1"
    description: "HRW defines F_net = m*a, showing law requires mass"

provenance:
  asserted_by: {type: human, id: human:curator.001}
  generated_by: {type: human, id: human:curator.001}
  method: {type: manual}
  writer: human:curator.001  # NEW: who wrote this claim
  link: "https://..."  # NEW: link to discussion or source
```

**Mandatory for physics-core:**
- evidence array >=1
- each evidence has source_ref that resolves to sources/
- locator present (page/section)
- description present (why source supports claim)

---

## 4. New Minimal Source Schema (Canonical Record)

```yaml
id: stemma:src.halliday-resnick-walker-12th
type: textbook
citation: "Halliday, D., Resnick, R., & Walker, J. (2021). Fundamentals of Physics (12th ed.). Wiley."
title: "Fundamentals of Physics"
authors: ["David Halliday", "Robert Resnick", "Jearl Walker"]
year: 2021
publisher: Wiley
edition: 12th
isbn: "978-1119801128"
url: "https://www.wiley.com/..."
language: en
source_role: primary
writer: human:curator.001  # NEW: who created this source record
retrieved_at: "2026-09-21"
```

Every source must have url OR doi OR isbn for verifiability.

---

## 5. File Structure (Small Start)

```
content/
  physics/
    mechanics/
      mass.md (new design)
      force.md
      newtons-second-law.md (with historical)
    measurement-units/
      kilogram.md
      newton.md
    .gitkeep

connections/
  conn.000001.yaml (new design with mandatory evidence)
  .gitkeep

sources/
  src.halliday-resnick-walker-12th.yaml (new design)
  src.nist-si-brochure-9th.yaml
  .gitkeep

scripts/
  physics_core_profile_check.py (updated to enforce new rules)
  templates/
    physics_entity_template.md
    physics_source_template.yaml
    physics_connection_template.yaml

docs/
  PHYSICS-MINIMAL-DESIGN-V2.md (this file)
  PHYSICS-FIRST-IMPLEMENTATION-PLAN.md (old plan, now superseded by V2)
  VISION.md (updated with depth-first + dual verification)
  DOMAIN-MODEL.md (updated with mandatory source + history)
  etc.
```

---

## 6. Validation Flow (New)

```
content/physics/**/*.md (new design with source_refs + provenance.writer/link)
  + sources/*.yaml (canonical)
  + connections/*.yaml (mandatory evidence)
  ↓
scripts/validate.py (existing gate: schema, identity, references, registry, cycles)
  ↓
scripts/physics_core_profile_check.py (NEW rules):
  - entity has source_kind, source, writer, link, retrieved_at, source_refs>=1
  - source_refs resolve
  - law/model/equation human_reviewed/canonical has historical
  - connection evidence>=1 with source_ref, locator, description
  ↓
exports/knowledge.json (deterministic, with relation_registry)
  ↓
status_truth.py (counts)
```

---

## 7. Example Entity (New Design)

See `content/physics/mechanics/mass.md` after rebuild — will have:

- id, type, name, domain, status, definition
- symbol, unit
- provenance with writer, original_author, link, retrieved_at, source_kind, source
- source_refs array
- historical optional (for quantity)
- external_ids

Example law with history mandatory for canonical:

`content/physics/mechanics/newtons-second-law.md` will have historical with timeline Newton 1687 → Euler 1749 → Einstein 1916.

---

## 8. Why This is Still Minimal

- 7 required fields + provenance (6 subfields) + source_refs (1 array) + optional historical = ~15 fields total
- Old schema had 15+ optional pedagogical fields (learning_objectives etc.) — we removed those, so net smaller
- Dual verification adds 4 new provenance subfields (writer, original_author, link, retrieved_at) + source_refs — but these are core for verification, not bloat
- History is optional for draft, so draft entities can be created quickly

Minimal != no provenance. Minimal = no pedagogy, but full source audit trail.

---

## 9. Migration from Old Design

- Old content already nuked (0 entities)
- Old docs updated: VISION, ROADMAP, ARCHITECTURE, DOMAIN-MODEL, IMPLEMENTATION-STATUS
- Old ADRs preserved: 0001-0039 remain, 0040-0043 are new physics-first
- Schemas: No breaking change yet — new fields enforced via profile check, not JSON schema required. Schema v2.0 will make them required after pilot.

---

## 10. Acceptance Criteria for V2 Minimal

- 0 entities → 3 pilot entities with new design (mass, force, newtons-second-law) each with writer, link, source_refs, and law has historical
- 3 sources with url/isbn
- 2 connections with mandatory evidence (source_ref, locator, description)
- `validate.py` passes
- `physics_core_profile_check.py` passes (no warnings)
- `status_truth.py` shows 3 entities, 2 connections, 3 sources
- Every claim triple-checkable: embedded source vs canonical record vs external link

---

**End of V2 Minimal Design**
