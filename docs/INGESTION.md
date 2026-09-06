# STEMMA Knowledge Ingestion — from document to review-ready proposal

**Status:** Implemented. **Scope:** extract knowledge from any-size PDFs, images,
scanned docs, and text-based documents and stage *review-ready candidate* content
(source + proposed entities/connections) for the canonical knowledge graph. Nothing
becomes canonical automatically.

Related: `scripts/ingest.py`, `scripts/curation_pipeline.py`,
`scripts/ingest_to_proposals.py`, and the interactive
[Ingestion & Review webapp](WEBAPP.md) (`webapp/`).

---

## Why

STEMMA gains knowledge from documents. The ingestion layer turns an arbitrary
document into **extracted text + a canonical Source candidate**, which the curation
pipeline's Draft stage turns into proposed entities/connections. Every step is gated;
**no one can add canonical knowledge by merging** (the merge/review gate — the human
Governance Gate) is where the human decides what enters `content/` / `connections/`.

## Pipeline

```
document (PDF / image / scanned PDF)
   │  scripts/ingest.py extract()
   ▼
Extraction{kind, text, pages, is_scanned, ocr_used, source_name}
   │  scripts/ingest.py to_curation_request()
   ▼
CurationRequest(kind=entity|connection, source_ref=stemma:src.*, data[extracted_text])
   │  scripts/curation_pipeline.py run_pipeline() with a Draft seam (LLM)
   ▼
PublicationDecision{propose | request_review | hold | reject}
   │          └─ NEVER 'canonical' — the human Governance Gate decides via review.py
   ▼
scripts/ingest_to_proposals.py → proposals/<id>.proposal.yaml  (staged, gitignored)
```

## Extractors (deterministic, no fragile deps)

PDFs use poppler (`pdftotext` / `pdfinfo`) when available. If poppler is not
installed, a pure-Python `pypdf` fallback extracts text-based PDFs (scanned
PDFs still require poppler + tesseract OCR). Text-based files
(`txt/md/csv/json/yaml/xml/html`) are read directly. Unsupported types are
retained and marked `unsupported` with a reason.

Install the fallback when poppler is unavailable (`pip install pypdf`); CI/gate
runs should still install `pyyaml jsonschema` and may use either engine. A
scanned/image-only PDF without poppler reports its status but has no OCR text —
install `poppler-utils` + `tesseract` on that machine to OCR it.

| Input | Tool | Behavior |
|-------|------|----------|
| Text PDF | `pdftotext` (poppler), else `pypdf` | exact text; `is_scanned=False` |
| Scanned / image-only PDF | `pdftoppm` (render pages) + `tesseract` | OCR; `is_scanned=True`, `ocr_used=True`; bounded to first N pages for huge docs |
| Image (PNG/JPG/TIFF/BMP/WebP) | `tesseract` + Pillow | OCR after grayscale + upscale for small images |

Detection: a PDF is considered scanned if `pdftotext` yields < ~20 chars. All tooling is
checked at runtime; a clear error is raised if unavailable.

## Safety invariants

1. **Never writes canonical.** `ingest.py` and `ingest_to_proposals.py` do not write to
   `content/`, `connections/`, or `sources/`. Output lands in the gitignored `proposals/`
   staging area.
2. **Never auto-canonicalizes.** The pipeline's `DecisionAction` set is
   `{propose, request_review, hold, reject}` — it can never emit `canonical`.
   Canonicalization is always a human `scripts/review.py canonicalize ... --reviewer=...`
   action gated by `scripts/curation_state.py` (proposed→reviewed→canonical, reviewer
   required).
3. **AI stays downstream of canonical truth.** Extraction is deterministic (poppler +
   tesseract). Entity/connection *proposal* generation is an **LLM-agnostic Draft seam**
   supplied by a runner; deterministic gates (identity/schema/provenance/relations) reuse
   `scripts/validate.py`. No hardcoded subject, curriculum, or language.

## Usage

```bash
# With an LLM Draft seam (module:function) that proposes entities/connections.
# REQUIRED (ADR-0035): without --draft the runner fails closed — it never stages
# a schema-invalid placeholder.
python3 scripts/ingest_to_proposals.py --path img.png --draft mymodule:my_draft_fn
python3 scripts/ingest_to_proposals.py --path scan.pdf --draft mymodule:my_draft_fn --json

# Library use:
python3 - <<'PY'
from pathlib import Path
import sys; sys.path.insert(0,'scripts')
import ingest, curation_pipeline as cp
ex = ingest.extract(Path("doc.pdf"))
req = ingest.to_curation_request(ex, kind="entity")
def draft(bp, data, **kw):   # your LLM seam
    return {"id":"stemma:phys.draft-x","type":"concept","name":"X","domain":"physics",
            "status":"draft","definition":data["_extracted_text"][:200],
            "provenance":{"ai_drafted":True,"source":bp.source_ref}}
dec = cp.run_pipeline(req, draft_callback=draft,
                      semantic_review_callback=lambda g,a,b: cp.GateResult(g,"pass",[]))
print(dec.action)   # request_review — human must `review.py canonicalize` it
PY
```

## Interactive review (webapp)

For a visual upload → extract → draft → human-review → stage-proposal loop, run the
[Ingestion & Review webapp](WEBAPP.md):

```bash
python3 webapp/server.py --host 0.0.0.0 --port 8080
```

The webapp keeps every artifact under git-ignored `workflow/`, uses the same fail-closed
Draft seam policy (the LLM provider is configured in the UI, not committed), and never
writes to `content/`/`connections/`/`sources/`.

## Review gate

A human-review/merge-gate system so that "not anyone can update the knowledge graph by
merging" is the intended follow-up: branch/PR-based proposals + a human reviewer that
approves before canonicalization, enforced in the merge path. The webapp's staged proposals
are the input to that gate; the canonical write is still a separate human +
`scripts/review.py` + `scripts/verify_all.py` decision.