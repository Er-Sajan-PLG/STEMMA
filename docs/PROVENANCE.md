# STEMMA Provenance Model

**Version:** 1.0  
**Status:** Implemented  
**Related:** `docs/KNOWLEDGE-ACQUISITION.md`, `docs/EVIDENCE-MODEL.md`, `docs/SOURCE-POLICY.md`, `docs/CANONICAL-ADMISSION.md`

---

## Overview

Provenance in STEMMA answers: **"Where did this fact come from?"** with traceability from canonical knowledge back to source evidence.

---

## Three-Layer Provenance Architecture

```
CANONICAL KNOWLEDGE
    │
    ├── entity.provenance          (record source: where text came from)
    ├── connection.provenance      (assertion source: who made the claim)
    └── source record              (canonical source citation)
         │
         ▼
EVIDENCE
    │
    ├── connection.evidence[]      (specific supporting passages)
    │     ├── stance
    │     ├── source_ref
    │     └── locator (page, section, equation, figure, table)
    │
    ▼
SOURCE REGISTRY
    │
    └── sources/lhs:src.<slug>.yaml (full bibliographic metadata)
```

---

## Provenance on Entities

```yaml
provenance:
  ai_drafted: true|false           # REQUIRED: was AI involved in drafting?
  source_kind:                     # Where the entity TEXT came from
    - human-authored
    - textbook
    - academic-or-research
    - institutional
    - standards-or-specification
    - ai-assisted-draft
    - other
  source: "Citation or reference"  # Human-readable citation
  reviewer: "human:reviewer.name"  # REQUIRED for human_reviewed/canonical
  reviewed_at: "ISO datetime"      # REQUIRED for human_reviewed/canonical
```

---

## Provenance on Connections (First-Class Assertions)

```yaml
provenance:
  asserted_by:                     # Who made this assertion
    type: human|llm|process|unknown
    id: "human:reviewer.name"
  generated_by:                    # What process produced the connection object
    type: process|human|llm
    id: "process:migration.relationships-v0.2"
  method:                          # How the assertion was derived
    type: manual|llm_inference|rule_inference|migration
    model: "model-name-if-llm"
    prompt_version: "prompt-version"
  reviewed_by:                     # Who reviewed this assertion
    - type: human|llm
      id: "human:reviewer.name"
  review_history:                  # Audit trail of status changes
    - from: "unreviewed"
      to: "reviewed"
      reviewer: "human:reviewer.name"
      at: "ISO datetime"
      reason: "reason text"
  rights:                          # Optional rights info
    license: "CC BY 4.0"
    attribution: "Attribution text"
    rights_holder: "holder name"
```

---

## Provenance on Sources

```yaml
id: lhs:src.<slug>
type: textbook|academic-paper|standard|institutional|web|dataset|oer|other
citation: "Full bibliographic citation"
title: "Title"
authors: ["Author 1", "Author 2"]
year: 2023
publication_date: "2023-01-15"
publisher: "Wiley"
journal: "Journal Name"
volume: "12"
doi: "10.1234/abcde"
url: "https://doi.org/..."
isbn: "978-1234567890"
edition: "12th"
language: "en"
source_role: primary|secondary|aggregator|retrieval
accessed_at: "2026-01-15T10:30:00Z"
canonical_source_url: "https://stable.url"
archive_url: "https://web.archive.org/..."
checksum: "sha256:..."
license: "CC BY 4.0"
copyright_status: copyrighted|public-domain|cc0|cc-by|cc-by-sa|unknown
lifecycle: active|superseded|withdrawn|unavailable|retracted
supersedes: ["lhs:src.old-id"]
superseded_by: ["lhs:src.new-id"]
notes: "Additional context"
```

---

## Historical Attribution (Separate from Provenance)

Records **who first stated the scientific claim and when** (scientific origin), distinct from **where the entity text came from** (record source).

```yaml
historical:
  stated_by: "Isaac Newton"          # REQUIRED when present
  year: 1687                         # REQUIRED when present (CE, negative for BCE)
  where: "Philosophiæ Naturalis Principia Mathematica"
  context: "Classical mechanics"
  note: "F=ma is constant-mass special case; general form is F=dp/dt"
  timeline:
    - year: 1687
      by: "Isaac Newton"
      event: "Second law stated in Principia"
    - year: 1750
      by: "Leonhard Euler"
      event: "Analytic formulation F=ma"
```

---

## Evidence Provenance

Evidence links canonical assertions to specific source locations.

```yaml
evidence:
  - type: textbook
    stance: supports
    source_ref: lhs:src.halliday-resnick
    locator:
      page: "123"
      section: "4.2"
      equation: "Eq. 4.2"
      figure: "Fig. 4.3"
      table: "Table 4.1"
    description: "Textbook statement of Newton's second law as F=ma"
    extraction_method: pdftotext
    extraction_confidence: 0.98
```

### Evidence Stance
- **supports** — Evidence affirms the claim
- **weakly_supports** — Evidence partially supports
- **contradicts** — Evidence opposes the claim
- **qualifies** — Evidence adds conditions/limitations

---

## AI Provenance Tracking

When AI assists, provenance must distinguish:

```yaml
provenance:
  ai_drafted: true
  source_kind: "ai-assisted-draft"
  # ... connection provenance ...
    method:
      type: "llm_inference"
      model: "gpt-4o"
      prompt_version: "extraction-v1.2"
    asserted_by:
      type: "llm"
      id: "llm:gpt-4o"
    generated_by:
      type: "llm"
      id: "llm:gpt-4o"
```

**Key invariant:** AI output enters as `draft`/`proposed` — never auto-canonicalizes.

---

## Provenance Chain Example

```
Entity: lhs:phys.newtons-second-law
  └── provenance.ai_drafted: false
  └── provenance.source: "Halliday, Resnick & Walker, 12th ed."
  └── provenance.reviewer: "human:reviewer.physics-001"
  └── provenance.reviewed_at: "2026-08-30T18:21:03Z"

Connection: lhs:conn.000001 (newtons-second-law applies_to force)
  └── provenance.asserted_by: {type: human, id: human:reviewer.physics-001}
  └── provenance.method: {type: manual}
  └── provenance.review_history:
        - from: unreviewed → reviewed (human:reviewer.physics-001)
        - from: reviewed → canonical (human:reviewer.physics-001)
  └── evidence:
        - type: textbook
          stance: supports
          source_ref: lhs:src.halliday-resnick
          locator: {page: "123", section: "4.2", equation: "Eq. 4.2"}
          description: "Textbook statement of F=ma"

Source: lhs:src.halliday-resnick
  └── citation: "Halliday, Resnick, Walker — Fundamentals of Physics, 12th ed., Wiley"
  └── doi: "10.1002/9781119773512"
  └── license: "CC BY 4.0" (for extracted snippets)
```

---

## Provenance Validation Rules

### Deterministic Gates (validate.py)
1. Entity `provenance.ai_drafted` must be boolean
2. Entity `provenance.source_kind` must be from controlled vocabulary
3. Entity `human_reviewed`/`canonical` → requires `provenance.reviewer`
4. Connection `provenance.asserted_by`, `generated_by`, `method` required
5. Connection `evidence[].source_ref` must resolve to source
6. Source `id` format: `lhs:src.<slug>`
6. Historical `stated_by` + `year` required when present

### Semantic Gates (curation_pipeline.py)
- Intent gate: Claim matches extracted evidence
- Fidelity gate: No hallucination, accurate extraction
- Consistency gate: No contradiction with existing canonical

---

## Provenance in Exports

Primary export (`exports/knowledge.json`) includes full provenance:

```json
{
  "entities": [
    {
      "id": "lhs:phys.newtons-second-law",
      "provenance": {
        "ai_drafted": false,
        "source_kind": "textbook",
        "source": "Halliday, Resnick & Walker, 12th ed.",
        "reviewer": "human:reviewer.physics-001",
        "reviewed_at": "2026-08-30T18:21:03+00:00"
      },
      "historical": {...}
    }
  ],
  "connections": [
    {
      "id": "lhs:conn.000001",
      "provenance": {
        "asserted_by": {"type": "human", "id": "human:reviewer.physics-001"},
        "generated_by": {"type": "human", "id": "human:curator.001"},
        "method": {"type": "manual"},
        "review_history": [...]
      },
      "evidence": [...]
    }
  ],
  "sources": [
    {
      "id": "lhs:src.halliday-resnick",
      "citation": "Halliday, Resnick, Walker — Fundamentals of Physics, 12th ed., Wiley",
      "doi": "10.1002/9781119773512",
      "license": "CC BY 4.0"
    }
  ]
}
```

---

## Provenance Integrity Rules

1. **Never overwrite** `asserted_by` — preserves original authorship
2. **Never auto-promote** AI drafts — human review required for `canonical`
3. **Preserve review history** — full audit trail in `review_history`
4. **Link evidence to sources** — every evidence item has resolvable `source_ref`
6. **Track origin through migrations** — `method: migration` preserves legacy origin
7. **Separate record source from scientific origin** — `provenance` ≠ `historical`

---

## Export Contracts

### Primary Export
All provenance fields included.

### Subset Exports
- `entities-only.json` — Entity provenance only
- `connections-only.json` — Connection provenance + evidence
- `ai-rag.json` — Provenance embedded in entities for RAG
- `educational.json` — Only canonical/reviewed provenance

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-09-06 | Initial provenance model documentation |