# STEMMA Knowledge Acquisition Architecture

**Version:** 1.0  
**Status:** Implemented  
**Related:** `docs/PROVENANCE.md`, `docs/SOURCE-POLICY.md`, `docs/INGESTION.md`, `docs/EVIDENCE-MODEL.md`, `docs/CANONICAL-ADMISSION.md`, `docs/STEMMA-SPECIFICATION.md`

---

## Overview

This document specifies the knowledge acquisition and canonicalization system for STEMMA — the pipeline by which STEMMA discovers, acquires, evaluates, extracts, normalizes, verifies, and admits knowledge into the canonical system.

**Core Principle:** The acquisition system feeds STEMMA. It does NOT know about LearningHubSTEM, STEM-TUITION, JARVIS, or any consumer product. The flow remains:

```
Sources → Evidence → Canonical STEMMA → Exports → Consumer Adapters → Products
```

---

## Architecture Layers

### 1. Source & Ingestion Layer
```
Humans / Contributors
Papers / PDFs / Books
Web Sources
Datasets
OER / Documentation
```
→ Source Registration → Document Ingestion → Structured Evidence Extraction

### 2. Evidence Layer
```
Source Metadata
Document Structure (sections, paragraphs, equations, tables, figures)
Extracted Text with Locators
Evidence Items with Stance
Provenance Chain
```

### 3. Candidate Knowledge Layer
```
Claim Extraction
Entity Identification
Relationship Identification
Terminology Normalization
Identifier Resolution
Duplicate Detection
Cross-Source Reconciliation
Candidate Canonical Objects
```

### 4. Validation & Review
```
Deterministic Gates (schema, identity, relations, provenance, resolution, conditions)
Semantic Review (intent, fidelity, contradiction detection)
Human Governance Gate (canonicalization = human action)
```

### 5. Canonical Admission
```
Canonical STEMMA Knowledge
  ├── entities/ (content/)
  ├── connections/ (connections/)
  └── sources/ (sources/)
```

---

## Three Distinct Layers (Never Collapsed)

| Layer | Purpose | Example |
|-------|---------|---------|
| **SOURCE** | What somebody published | "Halliday & Resnick, 12th ed., p. 123, Eq. 4.2" |
| **EVIDENCE** | Specific claim/passage from source | "Claim: Force = mass × acceleration" (located at page 123, §4.2) |
| **CANONICAL KNOWLEDGE** | STEMMA's normalized representation | Entity `lhs:phys.newtons-second-law` with `equation: F = m·a` and provenance linking to evidence |

---

## Source Registry

Every external source entering STEMMA has a source record (`sources/lhs:src.<slug>.yaml`).

### Source Record Schema (v0.3)
```yaml
id: lhs:src.<slug>
type: source
title: Full title
authors: [list of authors]
contributors: [list of contributors]
publisher: Publisher name
publication_date: ISO date
version: edition/version string
edition: edition number
doi: DOI identifier
isbn: ISBN identifier
url: Canonical URL
source_type: textbook|academic-paper|standard|institutional|web|dataset|oer|other
language: ISO language code
source_role: primary|secondary|aggregator|retrieval
accessed_at: ISO datetime
canonical_source_url: Stable canonical URL
archive_url: Wayback/Internet Archive URL
checksum: SHA256 of source content
license: SPDX license identifier
copyright_status: copyrighted|public-domain|cc0|cc-by|cc-by-sa|unknown
lifecycle: active|superseded|withdrawn|unavailable|retracted
supersedes: [lhs:src.old-id]
superseded_by: [lhs:src.new-id]
notes: Additional context
```

### Source Lifecycle States
- **active** — Current, usable source
- **superseded** — Replaced by newer version
- **withdrawn** — Source withdrawn by publisher
- **unavailable** — Source no longer accessible
- **retracted** — Source formally retracted

---

## Evidence Model

Evidence items link canonical claims to specific locations in sources.

### Evidence Record Schema
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
    description: Human-readable description of the evidence
    extraction_method: pdftotext|tesseract|manual|llm-extraction
    extraction_confidence: 0.0-1.0
```

### Evidence Stance
- **supports** — Evidence affirms the claim
- **weakly_supports** — Evidence partially supports
- **contradicts** — Evidence opposes the claim
- **qualifies** — Evidence adds conditions/limitations

---

## Document Ingestion Pipeline

### Supported Formats
| Format | Text Extraction | OCR | Structure Preservation |
|--------|----------------|-----|------------------------|
| Native PDF | pdftotext | — | Headings, paragraphs |
| Scanned PDF | — | pdftoppm + tesseract | Page-level |
| Images (PNG/JPG/TIFF) | — | tesseract | Page-level |
| HTML/Web | Readability extraction | — | DOM structure |

### Extraction Process
1. **Detect document type** (PDF, image, scanned PDF)
2. **Extract text** (pdftotext for native, OCR for scanned)
3. **Preserve structure** (page boundaries, headings where detectable)
4. **Build Source candidate** with metadata
5. **Build CurationRequest** with extracted text
6. **Stage proposal** under `proposals/` for review

### Extraction Metadata
```yaml
extraction:
  kind: pdf|image
  pages: 10
  is_scanned: true
  ocr_used: true
  char_count: 45231
  extraction_method: pdftoppm+tesseract
  extraction_timestamp: ISO datetime
  extraction_tool_versions:
    pdftotext: "23.08.0"
    tesseract: "5.3.0"
```

---

## Candidate Knowledge Layer

The candidate layer holds proposed canonical objects that have passed deterministic gates but await human review.

### Candidate Structure
```yaml
candidate:
  kind: entity|connection|source
  intent: "what should be true canonically"
  data: { ... proposed canonical object ... }
  source_ref: lhs:src.<slug>
  evidence: [evidence items]
  gates: [gate results]
  extraction_metadata: { ... }
  status: proposed|reviewed|rejected|held
```

### Candidate Progression
```
Proposed → Deterministic Gates → Semantic Review → Human Review → Canonical
                 ↓                    ↓                  ↓
             (auto)              (LLM/human)         (human only)
```

---

## Source Trust / Evidence Quality Model

Do NOT reduce to a single confidence score. Use multidimensional assessment:

### Source Authority Dimensions
| Dimension | Scale | Example |
|-----------|-------|---------|
| Institutional authority | 0-1 | NIST=1.0, personal blog=0.2 |
| Peer review status | 0-1 | Peer-reviewed=1.0, preprint=0.5 |
| Methodological strength | 0-1 | RCT=1.0, observational=0.6 |
| Recency | 0-1 | <2 years=1.0, >20 years=0.3 |
| Consensus alignment | 0-1 | Widely accepted=1.0, controversial=0.3 |
| Reproducibility | 0-1 | Replicated=1.0, single study=0.4 |
| Independence | 0-1 | Independent=1.0, industry-funded=0.5 |
| Domain relevance | 0-1 | Exact domain=1.0, tangential=0.4 |

### Separate Confidence Types
| Type | Meaning |
|------|---------|
| Extraction confidence | How well we extracted the text (OCR quality) |
| Interpretation confidence | How well we understood the claim |
| Canonicalization confidence | How well the candidate maps to canonical |
| Epistemic status | Scientific consensus on the underlying claim |

**Critical:** AI extraction confidence ≠ Scientific truth confidence.

---

## Entity Resolution / Deduplication

STEMMA encounters synonyms, abbreviations, alternate notations, historical names.

### Resolution Categories
```yaml
resolution:
  - candidate_match: "possible same entity, needs review"
  - confirmed_match: "same entity, merge or alias"
  - possible_duplicate: "likely same, different IDs"
  - historical_alias: "historical name for existing entity"
  - synonym: "different label, same concept"
  - notation_variant: "different notation (F=ma vs F=dp/dt)"
```

### Resolution Process
1. **Candidate generation** — Find potential matches by name, symbol, aliases
2. **Evidence comparison** — Compare definitions, relationships, provenance
3. **Human review** — Domain expert confirms/rejects
4. **Action** — Merge (deprecate one), alias (add to aliases), or keep separate

---

## Contradiction & Model Pluralism

STEMMA represents scientific evolution, not just current consensus.

### Supported Relationships for Contradiction
| Relation | Use Case |
|----------|----------|
| `contradicts` | Direct logical contradiction |
| `inconsistent_with` | Mathematical inconsistency |
| `competes_with` | Rival theories |
| `limited_by` | Domain/conditions of validity |
| `supersedes` | Newer model replaces older |
| `approximates` | Idealized approximation |
| `idealizes` | Simplifying assumptions |

### Example: Newtonian Mechanics
```
lhs:phys.newtonian-mechanics
  ↓ limited_by → lhs:phys.relativistic-domain
  ↓ approximates → lhs:phys.general-relativity
  ↓ supersedes → lhs:phys.aristotelian-physics
```

---

## Retrieval & Indexing Strategy

**Index ≠ Canonical Truth.** Indexes are derived artifacts.

### Index Types
| Index | Purpose | Update |
|-------|---------|--------|
| Lexical (BM25) | Keyword search | On export |
| Structural | Section/entity navigation | On export |
| Semantic (embeddings) | Similarity search | On export |
| Citation graph | Source→evidence→canonical | On export |

### Retrieval Requirements
- Return **evidence with locators**, not just chunk IDs
- Preserve **why** a passage was retrieved
- Support retrieval by: concept, entity ID, source, author, date, domain, relationship, citation

---

## Source Update & Drift Detection

### Source Lifecycle Monitoring
```
Source v1 → Detection → Source v2 → Diff → Re-ingest affected evidence
                                              ↓
                                    Identify affected canonical objects
                                              ↓
                                    Human review → Update/Supersede
```

### Dependency Graph
```
Source → Evidence → Candidate → Canonical Entity/Connection
```
When source changes, traverse backward to find impacted canonical objects.

### Update Strategies
| Change Type | Action |
|-------------|--------|
| Minor correction | Update evidence, flag canonical objects for review |
| Major revision | Re-ingest, create new evidence, supersede old |
| Retraction | Mark source retracted, review dependent canonical objects |
| URL broken | Mark source unavailable, preserve canonical with historical note |

---

## Retraction / Withdrawal Handling

Explicit support for:
- Retracted papers
- Corrected papers (corrigenda)
- Superseded standards
- Withdrawn sources
- License changes
- Dataset revisions

### Handling Policy
- **Never silently delete** canonical objects
- Preserve historical state with `status: deprecated/superseded`
- Add `retraction_notice` to evidence
- Flag dependent canonical objects for review
- Maintain audit trail in evidence ledger

---

## Evidence Ledger / Audit Trail

Persistent audit structure forming a lineage graph:

```
SOURCE-123
  ↓
EVIDENCE-981
  ↓
CANDIDATE-442
  ↓
REVIEW-77
  ↓
ENTITY-phys:0042
```

### Ledger Entry Schema
```yaml
ledger_entry:
  id: lhs:ledger.<uuid>
  type: source_registered|evidence_extracted|candidate_created|review_completed|canonical_admitted|superseded|retracted
  timestamp: ISO datetime
  actor: human:reviewer.x|llm:model|process:pipeline
  source_ref: lhs:src.<slug>
  evidence_ref: [lhs:evidence.<id>]
  candidate_ref: lhs:cand.<id>
  canonical_ref: lhs:phys.<slug>
  details: { ... }
  prior_state: { ... }
  new_state: { ... }
```

---

## Rights & Attribution

### License Categories
| Category | Policy |
|----------|--------|
| CC0 / Public Domain | Full text extraction allowed |
| CC BY / CC BY-SA | Extract with attribution, no redistribution of full text |
| Open Access (other) | Extract per license terms |
| Copyrighted (fair use) | Metadata + small snippets + citations only |
| All Rights Reserved | Metadata + citations only, no extraction |

### Attribution Requirements
Every canonical object derived from a source must preserve:
- Original authorship
- Source citation
- License metadata
- Retrieval date
- Archive URL where available

---

## AI Role in Acquisition

### AI MAY Assist With
- Source discovery & classification
- Document structure extraction
- OCR cleanup
- Entity/relationship candidate extraction
- Terminology normalization
- Deduplication suggestions
- Claim decomposition
- Citation matching
- Cross-source comparison
- Contradiction detection
- Draft canonical objects (enter candidate layer)

### AI MUST NOT
- Auto-canonicalize without human review
- Fabricate evidence or sources
- Replace human judgment on scientific truth
- Override deterministic validation gates
- Redistribute copyrighted material beyond fair use

### AI Output Path
```
AI Candidate → Evidence Attachment → Schema Validation → Semantic Validation → Provenance Verification → Human Approval → Canonical
```

---

## Canonical Admission Gates

### Mandatory Gates (All Must Pass)
| Gate | Type | Description |
|------|------|-------------|
| Schema | Deterministic | Valid against JSON Schema |
| Identity | Deterministic | ID format, uniqueness, slug match |
| Relations | Deterministic | Whitelist, no dangling targets |
| Provenance | Deterministic | Required fields, reviewer for canonical |
| Resolution | Deterministic | Source/target resolve |
| Conditions | Deterministic | Context present for relation types |

### Judgment Gates
| Gate | Type | Description |
|------|------|-------------|
| Intent | Semantic | Claim matches extracted evidence |
| Fidelity | Semantic | No hallucination, accurate extraction |
| Consistency | Semantic | No contradiction with existing canonical |
| Epistemic Status | Semantic | Appropriate confidence/uncertainty |

### Stronger Gates For
- Controversial claims
- High-impact claims
- Cross-domain relationships
- New terminology
- Retracted/superseded source material

---

## End-to-End Acquisition Proof (Implemented)

### Physics Example: Newton's Second Law from Halliday & Resnick
```
1. Source Registration
   → lhs:src.halliday-resnick (textbook, ISBN, DOI, license)

2. Document Ingestion
   → PDF extracted via pdftotext (native PDF, 45 pages relevant section)
   → Structure: pages, sections, equations detected

3. Evidence Extraction
   → Locator: p. 123, §4.2, Eq. 4.2
   → Text: "The net force on a body equals the rate of change of its momentum..."
   → Evidence item: type=textbook, stance=supports, source_ref=lhs:src.halliday-resnick

4. Candidate Generation
   → Entity: lhs:phys.newtons-second-law (law type)
   → Relationships: applies_to lhs:phys.force, lhs:phys.mass, lhs:phys.acceleration
   → Provenance: ai_drafted=false, source=halliday-resnick, evidence linked

5. Validation
   → All deterministic gates PASS
   → Semantic review: intent matches evidence, no contradiction

6. Human Review
   → Reviewer: human:reviewer.physics-001
   → Action: canonicalize

7. Canonical Admission
   → Entity written to content/physics/mechanics/newtons-second-law.md
   → Connections written to connections/
   → Export regenerated deterministically
```

---

## Implementation Status

### ✅ Implemented
| Component | Location |
|-----------|----------|
| Source Registry | `sources/`, `schema/source.schema.json` |
| Document Ingestion | `scripts/ingest.py` (pdftotext, tesseract OCR) |
| Evidence Extraction | `scripts/ingest.py` → `make_ingest_request` |
| Candidate Layer | `scripts/ingest_to_proposals.py` → `proposals/` |
| Curation Pipeline | `scripts/curation_pipeline.py` (9-stage) |
| Deterministic Gates | `scripts/curation_pipeline.py` (schema, identity, relations, provenance, resolution, conditions, intent) |
| Semantic Review Seam | LLM callback injection |
| Human Review Gate | `scripts/review.py` (accept, canonicalize, reject) |
| Source Lifecycle | `lifecycle` field in source schema |
| Evidence Model | `evidence` array in connections with stance, locator |
| Provenance Chain | `provenance` in entities, connections, sources |
| Export & Subsets | `scripts/export_subsets.py` |
| Agent Skills | `.agents/skills/` (5 skills) |

### 🔄 Extensible / Deferred
| Component | Status | Notes |
|-----------|--------|-------|
| PDF Structure Preservation | Basic | Full section/equation/table extraction deferred |
| Semantic Embeddings Index | Deferred | Derived artifact, not canonical |
| Web Search Integration | Deferred | Discovery only, not truth |
| Entity Resolution Automation | Manual | Candidate matches only |
| Source Drift Detection | Schema only | Automated monitoring deferred |
| Retraction Automation | Manual | Review workflow exists |
| License Metadata | Partial | SPDX identifiers in source schema |

---

## Agent Skills for Acquisition

### Source Discovery Skill
Teaches: finding appropriate sources for a domain/topic

### Source & Rights Assessment Skill
Teaches: source classification, license metadata, reuse constraints, provenance requirements

### Scientific Document Ingestion Skill
Teaches: PDF extraction, structure preservation, evidence segmentation, equation/table handling, OCR limitations

### Evidence-to-Canonical Skill
Teaches: claim extraction, entity extraction, relationship extraction, normalization, evidence attachment, candidate generation

### Canonical Evidence Reviewer Skill
Teaches: evidence sufficiency, contradiction handling, provenance review, epistemic status, canonical admission

### Source Update / Drift Skill
Teaches: detecting source changes, re-ingestion, impact analysis, supersession/retraction handling

---

## Vertical Proofs (Required)

### Physics: Newton's Second Law
- Source: Halliday & Resnick 12th ed. (textbook)
- Evidence: p. 123, Eq. 4.2, §4.2
- Result: Canonical entity + connections admitted

### Chemistry: Gibbs Free Energy
- Source: Atkins Physical Chemistry (textbook)
- Evidence: Ch. 4, Eq. 4.8, Table 4.1
- Result: Canonical entity + connections admitted

### Biology: DNA Structure
- Source: Watson & Crick 1953 (paper, open access)
- Evidence: Figure 1, "double helix" claim
- Result: Canonical entity + connections admitted

### Mathematics: Fundamental Theorem of Calculus
- Source: MIT OpenCourseWare (OER, CC BY-NC-SA)
- Evidence: Lecture 18, Theorem statement
- Result: Canonical entity + connections admitted

---

## Non-Goals (Explicitly NOT Built)

| Not Built | Reason |
|-----------|--------|
| Graph database | Derived artifact, not canonical |
| Vector database | Derived artifact, not canonical |
| Autonomous web crawler | Discovery ≠ truth; human-curated sources |
| LLM-as-truth | AI output enters candidate layer only |
| Full-text copyrighted redistribution | License compliance |
| Automatic canonicalization | Human governance gate required |
| Real-time source monitoring | Batch/deferred by design |
| Multilingual extraction | Deferred (language-independent IDs first) |

---

## Documentation Index

| Document | Purpose |
|----------|---------|
| `docs/KNOWLEDGE-ACQUISITION.md` | This architecture document |
| `docs/PROVENANCE.md` | Provenance model & evidence chain |
| `docs/SOURCE-POLICY.md` | Source classification, rights, lifecycle |
| `docs/INGESTION.md` | Document ingestion pipeline |
| `docs/EVIDENCE-MODEL.md` | Evidence schema, stance, locators |
| `docs/CANONICAL-ADMISSION.md` | Admission gates, review process |
| `docs/STEMMA-SPECIFICATION.md` | Canonical format, IDs, validation, export |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-09-06 | Initial acquisition architecture with full implementation |