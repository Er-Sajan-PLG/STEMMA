# STEMMA Source Policy

**Version:** 1.0  
**Status:** Implemented  
**Related:** `docs/KNOWLEDGE-ACQUISITION.md`, `docs/PROVENANCE.md`, `docs/EVIDENCE-MODEL.md`, `docs/INGESTION.md`

---

## Overview

This document defines how STEMMA classifies, evaluates, and handles sources. It governs what sources may enter the system, how they are licensed, and how attribution is preserved.

---

## Source Classification

Every source entering STEMMA must be classified by `source_type`:

| Type | Description | Examples |
|------|-------------|----------|
| `textbook` | Educational textbooks with established authority | Halliday & Resnick, Atkins Physical Chemistry |
| `academic-paper` | Peer-reviewed research papers | Nature, Science, PRX, arXiv preprints |
| `standard` | Official standards & specifications | IUPAC, SI Brochure, IEEE standards |
| `institutional` | Government/NGO authoritative publications | NIST, NASA, WHO, UNESCO |
| `web` | Authoritative websites | Wolfram MathWorld, NIST Chemistry WebBook |
| `dataset` | Structured datasets | NIST Atomic Spectra Database, PDB |
| `oer` | Open Educational Resources | MIT OpenCourseWare, Khan Academy |
| `other` | Other sources not fitting above | Expert communications, internal docs |

---

## License & Rights Policy

### Open Licenses (Permissive Extraction)

| License | Extraction Policy | Redistribution |
|---------|-------------------|----------------|
| CC0 | Full text extraction allowed | Full text redistribution allowed |
| CC BY 4.0 | Full text extraction allowed | With attribution |
| CC BY-SA 4.0 | Full text extraction allowed | With attribution, share-alike |
| Public Domain | Full text extraction allowed | Full text redistribution allowed |
| MIT / BSD (code/docs) | Full text extraction allowed | With attribution |

**Policy:** For openly licensed sources, STEMMA may extract and store full relevant passages as evidence.

### Restricted Licenses (Limited Extraction)

| License / Status | Extraction Policy | Redistribution |
|------------------|-------------------|----------------|
| CC BY-NC / CC BY-NC-SA | Extraction for internal evidence only | No redistribution of extracted text |
| Copyrighted (fair use) | Metadata + short snippets (≤90 chars) + citations only | No redistribution |
| All Rights Reserved | Metadata + citations only | No redistribution |
| Elsevier / Springer / Wiley (standard academic) | Metadata + citations + fair-use snippets | No redistribution |
| arXiv (standard license) | Metadata + abstract + citations | Abstract redistribution per arXiv policy |

**Policy:** For restricted sources, STEMMA stores only:
- Full source metadata (citation, DOI, etc.)
- Evidence locators (page, section, equation)
- Short evidence snippets under fair use
- Link to canonical source URL

### Unknown / Unclear License

**Default:** Treat as restricted. Store metadata + citations only. Flag for manual review.

---

## Attribution Requirements

Every canonical object derived from a source MUST preserve attribution:

### Required Attribution Fields
```yaml
source_ref: lhs:src.<slug>        # In evidence items
provenance.source: "Citation"     # In entity provenance
provenance.reviewer: "..."        # In entity/connection provenance
```

### Citation Format
STEMMA exports include full citation in `sources/` array and inline in provenance.

### Archive URLs
Where available, `archive_url` (Wayback Machine, Internet Archive) should be recorded for link rot protection.

---

## Source Lifecycle Management

### Lifecycle States
| State | Meaning | Canonical Impact |
|-------|---------|------------------|
| `active` | Current, authoritative source | Normal use |
| `superseded` | Newer version exists | Flag dependent canonical for review |
| `withdrawn` | Source withdrawn by publisher | Flag dependent canonical for review |
| `unavailable` | Source no longer accessible | Preserve canonical with historical note |
| `retracted` | Formally retracted | **Immediate flag** for dependent canonical review |

### Supersession Chain
```yaml
source:
  id: lhs:src.halliday-resnick-12
  lifecycle: active
  supersedes: [lhs:src.halliday-resnick-11]
```

When a source is superseded:
1. New source registered with `supersedes` link
2. Old source marked `superseded`
3. Dependent canonical objects flagged for review
4. Evidence migrated to new source where content unchanged

### Retraction Handling
When a source is retracted:
1. Source marked `retracted`
2. `retraction_notice` added to source record
3. All dependent evidence flagged
4. All dependent canonical objects queued for review
5. Canonical objects may be:
   - Updated (if other evidence supports)
   - Deprecated (if claim was solely based on retracted source)
   - Qualified (add `limited_by` relationship)

---

## Source Quality Assessment

### Authority Dimensions (for trust model)
```yaml
source_quality:
  institutional_authority: 0.0-1.0    # NIST=1.0, personal blog=0.2
  peer_review_status: 0.0-1.0         # Peer-reviewed=1.0, preprint=0.5
  methodological_strength: 0.0-1.0    # RCT=1.0, observational=0.6
  recency: 0.0-1.0                    # <2 years=1.0, >20 years=0.3
  consensus_alignment: 0.0-1.0        # Widely accepted=1.0, controversial=0.3
  reproducibility: 0.0-1.0            # Replicated=1.0, single study=0.4
  independence: 0.0-1.0               # Independent=1.0, industry-funded=0.5
  domain_relevance: 0.0-1.0           # Exact domain=1.0, tangential=0.4
```

**Note:** These are engineering policy metrics, not legal determinations.

---

## Source Deduplication

Sources are deduplicated by:
1. **DOI** (primary for papers)
2. **ISBN** (primary for books)
3. **Canonical URL** (for web sources)
4. **Title + Authors + Year** (fallback)

### Deduplication Process
1. Compute dedup key from identifiers
2. Check existing `sources/` for match
3. If match: reuse existing source ID, update metadata if newer
4. If no match: create new source record

---

## Source Registration Workflow

```
Human/AI proposes source
    ↓
Validate identifiers (DOI, ISBN, URL)
    ↓
Check deduplication
    ↓
Classify source_type
    ↓
Assess license / rights
    ↓
Create source record (sources/lhs:src.<slug>.yaml)
    ↓
Validate against source.schema.json
    ↓
Register in source registry
```

---

## Rights Metadata in Exports

All source rights metadata is included in exports:

```json
{
  "sources": [
    {
      "id": "lhs:src.halliday-resnick",
      "citation": "Halliday, Resnick, Walker — Fundamentals of Physics, 12th ed., Wiley",
      "doi": "10.1002/9781119773512",
      "license": "CC BY 4.0",
      "copyright_status": "copyrighted",
      "accessed_at": "2026-08-15T10:00:00Z"
    }
  ]
}
```

Consumers MUST respect source license terms when using exported knowledge.

---

## Takedown / Removal Policy

### Source Withdrawal Request
If a rights holder requests removal:
1. Verify request authenticity
2. Mark source `withdrawn` or `unavailable`
3. Remove full-text evidence snippets from exports
4. Preserve canonical knowledge with historical attribution
5. Update exports

### Legal Compliance
- STEMMA complies with DMCA and applicable copyright law
- Fair use snippets retained per legal guidance
- Canonical knowledge (normalized abstractions) preserved
- Attribution maintained even after source removal

---

## Prohibited Sources

The following are NOT admitted as authoritative sources:
- Known predatory journals (Beall's list, etc.)
- Sources with fabricated/false credentials
- AI-generated content without human verification
- Sources violating export control / sanctions
- Content from blocked/embargoed entities

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-09-06 | Initial source policy |