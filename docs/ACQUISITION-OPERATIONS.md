# STEMMA Acquisition Operations Guide

**Supplemental to AGENTS.md** — Detailed knowledge acquisition operations for AI agents and humans.

---

## How Knowledge Enters STEMMA

### 1. Source Registration
```bash
# Register a new source
python3 scripts/register_source.py \
    --type textbook \
    --title "Fundamentals of Physics" \
    --authors "Halliday, Resnick, Walker" \
    --year 2021 \
    --doi "10.1002/9781119773512" \
    --license "CC BY 4.0" \
    --publisher "Wiley"
```

### 2. Document Ingestion
```bash
# Extract text from PDF/image (JSON output)
python3 scripts/ingest.py textbook_chapter.pdf --json

# Full pipeline: ingestion → proposals
python3 scripts/ingest_to_proposals.py --path textbook_chapter.pdf

# With LLM draft seam (optional)
python3 scripts/ingest_to_proposals.py --path doc.pdf --draft mymodule:my_draft_fn
```

### 3. Proposal Review
```bash
# List all proposals
ls proposals/

# Review a specific proposal
cat proposals/lhs_src_halliday-resnick.proposal.yaml
```

### 4. Human Governance Gate
```bash
# Review a connection
python3 scripts/review.py show lhs:conn.000123

# Accept for review
python3 scripts/review.py accept lhs:conn.000123 --reviewer human:reviewer.physics-001

# Canonicalize (make canonical)
python3 scripts/review.py canonicalize lhs:conn.000123 --reviewer human:reviewer.physics-001

# Reject
python3 scripts/review.py reject lhs:conn.000123 --reviewer human:reviewer.physics-001 --reason "Insufficient evidence"
```

### 5. Canonical Admission (Automatic)
```bash
# Validation + export regeneration (happens automatically after canonicalize)
python3 scripts/validate.py
```

---

## What Counts as Evidence

| Evidence Type | Example | Required Locator |
|---------------|---------|------------------|
| Textbook statement | Halliday & Resnick p.123, Eq.4.2 | page, section, equation |
| Experimental result | Cavendish 1798, Figure 3 | figure, table |
| Mathematical derivation | Euler 1750, §12 | section, equation |
| Standard specification | SI Brochure 9th ed., §2.1 | section |

**Every evidence item must have:**
- `type` (from controlled vocabulary)
- `stance` (supports/weakly_supports/contradicts/qualifies)
- `source_ref` (lhs:src.xxx)
- `locator` (page/section/equation/figure/table)
- `description` (human-readable)

---

## How Sources Are Registered

Every source gets a record in `sources/lhs:src.<slug>.yaml`:

```yaml
id: lhs:src.halliday-resnick
type: textbook
citation: "Halliday, Resnick, Walker — Fundamentals of Physics, 12th ed., Wiley"
title: "Fundamentals of Physics"
authors: ["Halliday", "Resnick", "Walker"]
year: 2021
publisher: "Wiley"
doi: "10.1002/9781119773512"
isbn: "978-1119773512"
edition: "12th"
language: "en"
source_type: textbook
license: "CC BY 4.0"
copyright_status: copyrighted
accessed_at: "2026-09-06T12:00:00Z"
canonical_source_url: "https://doi.org/10.1002/9781119773512"
archive_url: "https://web.archive.org/web/2026/https://doi.org/10.1002/9781119773512"
checksum: "sha256:..."
lifecycle: active
```

---

## How Provenance Works

**Three-layer provenance chain:**

```
Canonical Entity/Connection
    ↓ provenance (who, when, how)
Evidence Item
    ↓ source_ref
Source Record (lhs:src.xxx)
    ↓ citation, DOI, license
```

- **Entities** carry `provenance` (ai_drafted, source_kind, source, reviewer, reviewed_at)
- **Connections** carry `provenance` (asserted_by, generated_by, method, review_history) + `evidence[]`
- **Sources** carry full bibliographic metadata + license + lifecycle

---

## What AI May Do

- ✅ Source discovery & classification
- ✅ Document structure extraction
- ✅ OCR cleanup
- ✅ Entity/relationship candidate extraction
- ✅ Terminology normalization
- ✅ Deduplication suggestions
- ✅ Claim decomposition
- ✅ Citation matching
- ✅ Cross-source comparison
- ✅ Contradiction detection
- ✅ Draft canonical objects (enter candidate layer)

---

## What AI May NOT Do

- ❌ Auto-canonicalize without human review
- ❌ Fabricate evidence or sources
- ❌ Replace human judgment on scientific truth
- ❌ Override deterministic validation gates
- ❌ Redistribute copyrighted material beyond fair use

---

## How Copyrighted Material Is Handled

| License | Extraction | Export |
|---------|------------|--------|
| CC0 / CC BY | Full text | With attribution |
| CC BY-NC | Internal only | No redistribution |
| Copyrighted (fair use) | Metadata + snippets (≤90 chars) | Citations only |
| All Rights Reserved | Metadata + citations | Citations only |

---

## How Human Review Works

```bash
# Review a connection
python3 scripts/review.py show lhs:conn.000123

# Canonicalize (make canonical)
python3 scripts/review.py canonicalize lhs:conn.000123 --reviewer human:reviewer.physics-001
```

**Canonicalization requires:**
1. All deterministic gates pass
2. Semantic review gates pass
3. Evidence exists (per family rules)
4. Named human reviewer (`human:reviewer.<name>`)
5. Reason provided
6. `review_history` entry created

---

## How Source Changes Propagate

```bash
# Detect drift
python3 scripts/detect_drift.py

# Handle retraction
python3 scripts/handle_retraction.py --action retract --source lhs:src.xxx --reason "Retracted by publisher" --apply

# Handle correction
python3 scripts/handle_retraction.py --action correct --source lhs:src.xxx --reason "Corrigendum published" --apply

# Handle supersession
python3 scripts/handle_retraction.py --action supersede --source lhs:src.old --new-source lhs:src.new --reason "New edition published" --apply
```

---

## Acquisition Agent Skills

| Skill | Purpose |
|-------|---------|
| `source-discovery.md` | Find appropriate sources |
| `source-rights-assessment.md` | Assess licenses & rights |
| `scientific-document-ingestion.md` | Ingest PDFs/images |
| `evidence-to-canonical.md` | Convert evidence to candidates |
| `canonical-evidence-reviewer.md` | Review evidence for admission |
| `source-update-drift.md` | Monitor source changes |

---

## Quick Start Acquisition

```bash
# 1. Check current state
python3 scripts/validate.py

# 2. Register a new source
python3 scripts/register_source.py --type textbook --title "..." --doi "..." --license "CC BY 4.0"

# 3. Ingest a document
python3 scripts/ingest_to_proposals.py --path chapter.pdf

# 4. Review proposals
ls proposals/

# 5. Canonicalize after review
python3 scripts/review.py canonicalize lhs:conn.XXXXX --reviewer human:reviewer.xxx

# 6. Verify
python3 scripts/validate.py
```