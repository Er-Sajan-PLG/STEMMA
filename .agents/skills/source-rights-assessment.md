# Source & Rights Assessment Skill

**Purpose:** Teaches an agent how to assess sources for STEMMA inclusion, including classification, license compatibility, reuse constraints, and provenance requirements.

**When to Use:** Every time a new source is considered for STEMMA acquisition.

**Mental Model:** Sources have metadata, licenses, and lifecycle states. Assessment ensures legal compliance and trustworthiness.

---

## Required Inputs
- Source candidate (raw metadata, URL, file)
- Domain context

---

## Workflow

### 1. Source Classification
Classify by `source_type`:
| Type | Criteria |
|------|----------|
| `textbook` | Published educational textbook, ISBN |
| `academic-paper` | Peer-reviewed, DOI, journal |
| `standard` | Official standard body (IUPAC, ISO, NIST) |
| `institutional` | Government/NGO publication |
| `web` | Authoritative website, stable URL |
| `dataset` | Structured data with schema |
| `oer` | Open educational resource, open license |
| `other` | Fallback |

### 2. License Assessment
| License Category | Extraction Policy | Export Policy |
|------------------|-------------------|---------------|
| CC0 / Public Domain | Full text | Full text |
| CC BY 4.0 | Full text | With attribution |
| CC BY-SA 4.0 | Full text | With attribution, share-alike |
| CC BY-NC | Internal evidence only | No redistribution |
| Copyrighted (fair use) | Metadata + snippets (≤90 chars) | Citations only |
| All Rights Reserved | Metadata + citations | Citations only |
| Unknown | Treat as restricted | Citations only |

**Rule:** When in doubt, treat as restricted.

### 3. Rights Metadata Collection
Collect for every source:
```yaml
license: "CC BY 4.0"  # SPDX identifier
copyright_status: copyrighted|public-domain|cc0|cc-by|cc-by-sa|unknown
accessed_at: "2026-09-06T12:00:00Z"
canonical_source_url: "https://doi.org/..."
archive_url: "https://web.archive.org/..."
checksum: "sha256:..."
```

### 4. Lifecycle Assessment
| State | Meaning | Action |
|-------|---------|--------|
| `active` | Current, usable | Normal use |
| `superseded` | Newer version exists | Flag dependents for review |
| `withdrawn` | Publisher withdrew | Flag dependents |
| `unavailable` | Link broken | Preserve with note |
| `retracted` | Formal retraction | **Immediate review** of dependents |

---

## Anti-Patterns
| Don't | Do |
|-------|----|
| Assume public = free to reuse | Check license explicitly |
| Ignore NC/ND clauses | Respect non-commercial/no-derivatives |
| Redistribute copyrighted full text | Store only metadata + fair-use snippets |
| Skip archive URL | Always capture Wayback/Internet Archive link |

---

## Escalation Conditions
- License unclear → Flag for legal review
- No open alternative for essential content → Budget/access decision
- Source retracted → Immediate dependent review via `scripts/handle_retraction.py`
- License change detected → Re-assess all extracted evidence