# STEMMA Evidence Model

**Version:** 1.0  
**Status:** Implemented  
**Related:** `docs/KNOWLEDGE-ACQUISITION.md`, `docs/PROVENANCE.md`, `docs/SOURCE-POLICY.md`, `schema/connection.schema.json`

---

## Overview

Evidence links canonical assertions to specific locations in sources. Every canonical claim should have an explainable path to evidence.

---

## Evidence Record Schema

```yaml
evidence:
  - type: definition|axiom|mathematical_derivation|empirical_measurement|experiment|observation|simulation|review|textbook|standard|dataset|expert_assessment|derivation|other
    stance: supports|weakly_supports|contradicts|qualifies
    source_ref: lhs:src.<slug>
    locator:
      page: "123"
      section: "4.2"
      equation: "Eq. 4.2"
      figure: "Fig. 4.3"
      table: "Table 4.1"
      dataset: "dataset-name"
      code: "code-reference"
    description: "Human-readable description of the evidence"
    extraction_method: pdftotext|tesseract|manual|llm-extraction
    extraction_confidence: 0.0-1.0
```

### Required Fields
| Field | Description |
|-------|-------------|
| `type` | Evidence type from controlled vocabulary |
| `stance` | Relationship of evidence to claim |
| `source_ref` | Must resolve to a source in `sources/` |
| `description` | Human-readable description |

### Optional Fields
| Field | Description |
|-------|-------------|
| `locator` | Structured location within source |
| `extraction_method` | How evidence was extracted |
| `extraction_confidence` | Quality of extraction (0.0-1.0) |

---

## Evidence Types (Controlled Vocabulary)

| Type | Use Case |
|------|----------|
| `definition` | Authoritative definition |
| `axiom` | Foundational assumption |
| `mathematical_derivation` | Mathematical proof/derivation |
| `empirical_measurement` | Experimental data |
| `experiment` | Controlled experiment description |
| `observation` | Empirical observation |
| `simulation` | Computational simulation result |
| `review` | Review article / meta-analysis |
| `textbook` | Textbook statement |
| `standard` | Official standard/specification |
| `dataset` | Structured dataset |
| `expert_assessment` | Expert opinion |
| `derivation` | Logical derivation |
| `other` | Other evidence type |

---

## Evidence Stance

| Stance | Meaning |
|--------|---------|
| `supports` | Evidence affirms the claim |
| `weakly_supports` | Evidence partially supports |
| `contradicts` | Evidence opposes the claim |
| `qualifies` | Evidence adds conditions/limitations |

**Default:** `supports` (but explicit is preferred)

---

## Locator Structure

```yaml
locator:
  page: "123"                    # Page number
  section: "4.2"                 # Section/chapter
  equation: "Eq. 4.2"            # Equation number
  figure: "Fig. 4.3"             # Figure number
  table: "Table 4.1"             # Table number
  dataset: "dataset-name"        # Dataset identifier
  code: "code-reference"         # Code repository/path
```

All fields optional but at least one should be present for traceability.

---

## Evidence in Connections

```yaml
connection:
  id: lhs:conn.000001
  source: lhs:phys.newtons-second-law
  relation: applies_to
  target: lhs:phys.force
  evidence:
    - type: textbook
      stance: supports
      source_ref: lhs:src.halliday-resnick
      locator:
        page: "123"
        section: "4.2"
        equation: "Eq. 4.2"
      description: "Textbook statement of Newton's second law as F=ma"
      extraction_method: pdftotext
      extraction_confidence: 0.98
```

---

## Evidence Extraction Methods

| Method | Description |
|--------|-------------|
| `pdftotext` | Native PDF text extraction (poppler) |
| `tesseract` | OCR via tesseract |
| `manual` | Human-extracted |
| `llm-extraction` | LLM-assisted extraction |
| `pdfplumber` | Advanced PDF extraction (future) |
| `marker-pdf` | Marker PDF extraction (future) |

---

## Evidence Quality Metrics

### Extraction Confidence (0.0-1.0)
| Score | Meaning |
|-------|---------|
| 0.9-1.0 | High confidence, clear extraction |
| 0.7-0.9 | Good, minor ambiguities |
| 0.5-0.7 | Moderate, some uncertainty |
| 0.3-0.5 | Low, significant ambiguity |
| 0.0-0.3 | Very low, unreliable |

### Evidence Completeness
| Level | Criteria |
|-------|----------|
| Complete | Full claim + locator + source metadata |
| Partial | Claim + source, missing precise locator |
| Minimal | Citation only, no extractable passage |

---

## Evidence Chain

Evidence forms a chain from canonical back to source:

```
Canonical Connection
    ↓
evidence[0] (type: textbook, stance: supports, source_ref: lhs:src.halliday-resnick)
    ↓
Source: lhs:src.halliday-resnick
    ↓
citation: "Halliday, Resnick, Walker — Fundamentals of Physics, 12th ed., Wiley"
doi: "10.1002/9781119773512"
```

---

## Evidence Validation Rules

### Deterministic (validate.py)
1. Evidence `type` from controlled vocabulary
2. Evidence `stance` from controlled vocabulary
3. `source_ref` must resolve to existing source
4. `locator` fields are strings (if present)

### Semantic (curation_pipeline.py)
1. Canonical connections SHOULD have ≥1 evidence item
2. `canonical` status → requires evidence (per family rules)
3. Contradicting evidence should be noted, not suppressed
4. Evidence stance should match canonical relationship polarity

---

## Evidence in Exports

### Primary Export
Full evidence array included in connections.

### Subset Exports
- `connections-only.json` — Full evidence
- `ai-rag.json` — Evidence summarized in entity adjacency
- `educational.json` — Only supporting evidence for canonical connections

---

## AI Evidence Extraction

When AI assists with evidence extraction:

```yaml
evidence:
  - type: textbook
    stance: supports
    source_ref: lhs:src.halliday-resnick
    locator:
      page: "123"
      equation: "Eq. 4.2"
    description: "Textbook statement of F=ma"
    extraction_method: llm-extraction
    extraction_confidence: 0.92
    # AI provenance tracked separately
    provenance:
      asserted_by: {type: llm, id: llm:gpt-4o}
      method: {type: llm_inference, model: gpt-4o, prompt_version: extraction-v1.2}
```

**Rule:** AI-extracted evidence enters as candidate; human verification required before canonical admission.

---

## Contradictory Evidence

STEMMA preserves contradictory evidence rather than suppressing it:

```yaml
evidence:
  - type: textbook
    stance: supports
    source_ref: lhs:src.textbook-a
    ...
  - type: academic-paper
    stance: contradicts
    source_ref: lhs:src.paper-b
    ...
  - type: academic-paper
    stance: qualifies
    source_ref: lhs:src.paper-c
    description: "Valid only under classical conditions"
    ...
```

The canonical relationship's polarity and confidence should reflect the evidence balance.

---

## Evidence Retention Policy

| Evidence Type | Retention |
|---------------|-----------|
| Supporting evidence | Permanent |
| Contradicting evidence | Permanent |
| Qualifying evidence | Permanent |
| Low-confidence evidence | Retained but flagged |
| Superseded source evidence | Retained with source lifecycle note |

**Never delete evidence** — it forms the audit trail.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-09-06 | Initial evidence model documentation |