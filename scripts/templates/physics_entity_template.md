---
id: stemma:phys.<slug>
type: quantity  # quantity | unit | law | equation | concept | model | phenomenon
name: "<Human Name>"
domain: physics
subdomain: mechanics  # mechanics | electricity-magnetism | thermal-physics | measurement-units
status: draft
definition: "<Curriculum-agnostic definition, 1-3 sentences, verifiable>"

# Physics display (optional but needed)
symbol: "<symbol>"
unit: "<unit display>"

# Dual verification - MANDATORY for physics-core v2 (ADR-0043)
provenance:
  ai_drafted: false
  source_kind: textbook  # textbook | academic-or-research | standards-or-specification | institutional | other
  source: "<Full citation string with page, e.g., Halliday Resnick Walker 12th ed. Ch 5, p112>"
  writer: human:curator.001  # who wrote this file (agent id)
  original_author: "<Who originally stated science, e.g., Halliday, Resnick, Walker>"
  link: "https://..."  # URL or DOI to source
  retrieved_at: "2026-09-21"
  reviewer: null
  reviewed_at: null

source_refs:  # canonical source records, dual verification
  - stemma:src.halliday-resnick-walker-12th

# Optional for draft, MANDATORY for human_reviewed/canonical if type law/model/equation
historical:
  stated_by: "<Who>"
  year: 1687
  where: "<Work>"
  timeline:
    - year: 1687
      event: "First stated"
      by: "<Who>"

external_ids:
  wd: Q...
  qudt: quantitykind-...
---

## Notes

Optional prose, but keep minimal.
