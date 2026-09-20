# Scientific Document Ingestion Skill

**Purpose:** Teaches an agent how to ingest scientific documents (PDFs, images, scanned docs) and extract structured evidence for STEMMA.

**When to Use:** When processing a new document for knowledge acquisition.

**Mental Model:** Ingestion is the extraction layer — it produces evidence and source candidates, NEVER canonical knowledge directly.

---

## Required Inputs
- Document file (PDF, PNG, JPG, TIFF)
- Optional: LLM draft seam module

---

## Workflow

### 1. Prerequisites
```bash
# System tools required
apt-get install poppler-utils tesseract-ocr tesseract-ocr-eng python3-pil
```

### 2. Document Ingestion
```bash
# Basic extraction (JSON output)
python3 scripts/ingest.py document.pdf --json

# Full pipeline to proposals
python3 scripts/ingest_to_proposals.py --path document.pdf

# With LLM draft seam
python3 scripts/ingest_to_proposals.py --path document.pdf --draft mymodule:my_draft_fn
```

### 3. Extraction Process
```
Document → detect_kind() → extract() → Extraction(kind, text, pages, is_scanned, ocr_used)
```

| Format | Text Extraction | OCR | Notes |
|--------|-----------------|-----|-------|
| Native PDF | pdftotext -layout | — | High fidelity |
| Scanned PDF | — | pdftoppm + tesseract | Page images |
| Images | — | tesseract | Preprocessed (grayscale + upscale) |

### 4. Source Candidate Creation
```python
build_source_candidate(ext) → {
    "id": "lhs:src.ingest-<hash>",
    "type": "source",
    "title": filename,
    "kind": "ingested-document",
    "format": "pdf|image",
    "pages": N,
    "ocr_used": bool,
    "extracted_text_preview": text[:2000],
    "provenance": {"ai_drafted": False, "source_kind": "other"}
}
```

### 5. Curation Request
```python
make_ingest_request(ext) → CurationRequest(
    kind="source|entity|connection",
    intent="ingest document and propose canonical objects",
    data={source_candidate, "_extracted_text": full_text},
    source_ref=source_id
)
```

### 6. Curation Pipeline
```python
curation_pipeline.run_pipeline(
    request,
    draft_callback=draft or _default_draft,
    semantic_review_callback=lambda gate, artifact, bp: GateResult(gate, "pass", [])
) → PublicationDecision
```

### 7. Proposal Staging
Output: `proposals/<source-slug>.proposal.yaml` with:
- Extraction metadata
- Source candidate
- Proposal (decision, gates, artifact)
- Status: "proposed" (NEVER canonical)

---

## Quality Considerations

| Factor | Recommendation |
|--------|----------------|
| OCR Resolution | 200 DPI minimum |
| Language | English default; install language packs for others |
| Page Limit | 500 pages max per document |
| Multi-column | Reading order issues possible |
| Equations | Render as garbled text (no MathML extraction yet) |
| Tables | Lose structure (linear text) |
| Figures | Not extracted |

---

## Anti-Patterns
| Don't | Do |
|-------|----|
| Write directly to canonical directories | Always stage under `proposals/` |
| Skip OCR quality check | Verify extracted text makes sense |
| Auto-canonicalize | Human review mandatory |
| Ignore license | Assess rights before extraction |

---

## Extending the Pipeline
1. Add format: extend `detect_kind()` + `extract_<format>()`
2. Better structure: integrate `pdfplumber`, `marker-pdf`
3. Language support: install tesseract language packs, pass `-l eng+fra`

---

## Escalation Conditions
- OCR fails completely → Manual transcription needed
- Copyrighted document with no fair-use path → Legal review
- Extraction garbage → Try different tool/settings
- Non-English document → Install language pack