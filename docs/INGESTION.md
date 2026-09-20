# STEMMA Document Ingestion Pipeline

**Version:** 1.0  
**Status:** Implemented (basic) / Extensible  
**Related:** `docs/KNOWLEDGE-ACQUISITION.md`, `scripts/ingest.py`, `scripts/ingest_to_proposals.py`

---

## Overview

The ingestion pipeline transforms arbitrary documents (PDFs, images, scanned documents) into structured evidence and source candidates for the curation pipeline.

**Key Principle:** Ingestion NEVER writes to canonical directories (`content/`, `connections/`, `sources/`). It produces CurationRequests staged under `proposals/` for human review.

---

## Supported Document Types

| Format | Extension | Text Extraction | OCR | Structure Preserved |
|--------|-----------|-----------------|-----|---------------------|
| Native PDF | `.pdf` | pdftotext (poppler) | — | Page boundaries, layout |
| Scanned PDF | `.pdf` | — | pdftoppm + tesseract | Page images |
| Images | `.png`, `.jpg`, `.jpeg`, `.tif`, `.tiff`, `.bmp`, `.webp` | — | tesseract | Single page |

---

## Ingestion Flow

```
Document (PDF/Image)
    ↓
detect_kind() → "pdf" | "image"
    ↓
extract()
    ├── PDF: pdftotext (native) OR pdftoppm + tesseract (scanned)
    └── Image: tesseract (with preprocessing)
    ↓
Extraction Result:
    kind, text, pages, is_scanned, ocr_used, source_name
    ↓
build_source_candidate() → Source record (lhs:src.<slug>)
    ↓
to_curation_request() → CurationRequest for curation pipeline
    ↓
curation_pipeline.run_pipeline() → PublicationDecision
    ↓
Stage dossier under proposals/
```

---

## Extraction Details

### PDF Extraction (`extract_pdf`)

1. **Page count** via `pdfinfo`
2. **Scanned detection** via `pdftotext` - if < 20 chars extracted, treat as scanned
3. **Native PDF** → `pdftotext -layout` preserves reading order
4. **Scanned PDF** → `pdftoppm -r 200 -png` → tesseract per page (max 500 pages)

### Image Extraction (`extract_image`)

1. **Open with PIL** → grayscale conversion
2. **Upscale** if min dimension < 800px (improves OCR)
3. **Tesseract** with English language model

### Tool Requirements

| Tool | Purpose | Package (Debian/Ubuntu) |
|------|---------|-------------------------|
| `pdftotext` | Native PDF text extraction | `poppler-utils` |
| `pdfinfo` | PDF metadata (page count) | `poppler-utils` |
| `pdftoppm` | PDF page rendering for OCR | `poppler-utils` |
| `tesseract` | OCR engine | `tesseract-ocr` |
| `tesseract-eng` | English language data | `tesseract-ocr-eng` |
| `Pillow` | Image preprocessing | `python3-pil` |

---

## Extraction Output

```python
@dataclass
class Extraction:
    kind: str              # "pdf" | "image"
    text: str              # Full extracted text
    pages: int             # Number of pages
    is_scanned: bool       # True if OCR was used
    ocr_used: bool         # True if tesseract was invoked
    source_name: str       # Original filename
```

---

## Source Candidate Construction

```python
def build_source_candidate(ext: Extraction, *, source_id: str | None = None) -> dict:
    _id = source_id or "lhs:src.ingest-%08x" % (abs(hash((ext.source_name, ext.pages))) & 0xFFFFFFF)
    return {
        "id": _id,
        "type": "source",
        "title": ext.source_name,
        "kind": "ingested-document",
        "format": ext.kind,
        "pages": ext.pages,
        "ocr_used": ext.ocr_used,
        "extracted_text_preview": ext.text[:2000],
        "provenance": {
            "ai_drafted": False,
            "source_kind": "other",
            "reviewer": None,
            "reviewed_at": None,
        },
    }
```

---

## Curation Request

```python
def make_ingest_request(ext: Extraction) -> dict:
    source = build_source_candidate(ext)
    return {
        "kind": "source",
        "intent": f"ingest document '{ext.source_name}' and propose canonical entities/connections from its content",
        "data": {**source, "_extracted_text": ext.text},
        "extracted_text": ext.text,
    }
```

---

## Curation Pipeline Integration

The ingestion output feeds `curation_pipeline.run_pipeline()`:

```python
decision = curation_pipeline.run_pipeline(
    request,
    draft_callback=draft or _default_draft,
    semantic_review_callback=lambda gate, artifact, bp: GateResult(gate, "pass", []),
)
```

### Default Draft (No LLM)
Produces a Source proposal + placeholder entity clearly marked for human completion.

### LLM Draft (Optional)
Supply `--draft module:function` for AI-assisted extraction.

---

## Proposal Staging

Dossier written to `proposals/<source-slug>.proposal.yaml`:

```yaml
schema_version: "0.1"
created_at: "2026-09-06T12:00:00+00:00"
input_file: "path/to/doc.pdf"
extraction:
  kind: pdf
  pages: 45
  is_scanned: false
  ocr_used: false
  char_count: 123456
source_candidate:
  id: lhs:src.ingest-abc12345
  type: source
  title: "doc.pdf"
  kind: ingested-document
  format: pdf
  pages: 45
  ocr_used: false
proposal:
  decision: request_review
  publishable: true
  gates:
    - gate: schema
      verdict: pass
      findings: []
    - gate: identity
      verdict: pass
      findings: []
    ...
  artifact: { ... proposed canonical object ... }
  reason: "all gates pass; human Governance Gate must canonicalize"
status: proposed
```

**Critical:** Proposals are NEVER canonical. Human must approve via `scripts/review.py`.

---

## CLI Usage

```bash
# Basic ingestion
python3 scripts/ingest.py path/to/document.pdf

# With JSON output
python3 scripts/ingest.py path/to/document.pdf --json

# Full pipeline to proposals
python3 scripts/ingest_to_proposals.py --path path/to/document.pdf

# With LLM draft seam
python3 scripts/ingest_to_proposals.py --path doc.pdf --draft mymodule:my_draft_fn

# Output proposal as JSON
python3 scripts/ingest_to_proposals.py --path doc.pdf --json
```

---

## Quality Considerations

### OCR Quality Factors
- **Resolution:** 200 DPI minimum for `pdftoppm`
- **Language:** English only (configurable via `-l` flag)
- **Preprocessing:** Grayscale + upscale for small images
- **Page limit:** 500 pages max per document (configurable)

### Extraction Fidelity
- Native PDF: High fidelity (text layer preserved)
- Scanned PDF: Depends on scan quality, OCR engine
- Images: Depends on resolution, contrast, font

### Known Limitations
- Multi-column layouts may have reading order issues
- Equations render as garbled text (no MathML/MathJAX extraction)
- Tables lose structure (become linear text)
- Figures/captions not extracted
- Non-English text requires language pack installation

---

## Extending the Pipeline

### Adding New Formats
1. Add extension to `_IMAGE_EXTS` or new detector
2. Implement `extract_<format>` function
3. Update `extract()` dispatcher
4. Add tool checks

### Improving Structure Preservation
Future work: Integrate `pdfplumber`, `pymupdf`, or `marker-pdf` for:
- Heading detection
- Section boundaries
- Table extraction (as CSV/Markdown)
- Equation detection (LaTeX/MathML)
- Figure/caption association

### Adding Language Support
```bash
# Install language packs
apt-get install tesseract-ocr-fra tesseract-ocr-deu tesseract-ocr-spa
```
Then pass `-l eng+fra` to tesseract.

---

## Testing Ingestion

```bash
# Test with a native PDF
python3 scripts/ingest.py test_native.pdf --json

# Test with scanned PDF
python3 scripts/ingest.py test_scanned.pdf --json

# Test with image
python3 scripts/ingest.py test_image.png --json

# Full pipeline test
python3 scripts/ingest_to_proposals.py --path test.pdf --json
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-09-06 | Initial ingestion documentation |