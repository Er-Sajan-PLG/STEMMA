#!/usr/bin/env python3
"""STEMMA (`stemma:` namespace) knowledge ingestion — extract text from PDFs, images, and scanned docs.

This is the **extraction layer** of the canonical-knowledge pipeline. It turns an
arbitrary document (PDF of any size, PNG/JPG/TIFF image, scanned PDF) into
*extracted text* plus a *canonical Source candidate*, which then feeds the curation
pipeline (scripts/curation_pipeline.py) for the LLM/generative Draft stage.

Design rules (aligns with the canonical-knowledge north star):
  - Deterministic where possible: text extraction uses poppler (pdftotext) + tesseract
    OCR; no LLM is used to *extract* — that part must be exact and auditable.
  - AI stays downstream of canonical truth: this module NEVER writes to content/,
    connections/, or sources/ itself, and it NEVER auto-canonicalizes. It emits a
    CurationRequest (a candidate) that a human Governance Gate must approve.
  - General-purpose: no hardcoded subject, curriculum, language, or content type.
    Extraction works for any text/OCR-able document.
  - Source preservation: every extraction produces a Source candidate carrying the
    file's identity/location so provenance is never lost.

Tooling (system, no fragile Python deps):
  - poppler-utils: pdftotext (text PDFs), pdftoppm (render pages of scanned PDFs)
  - tesseract + Pillow: OCR for images and scanned pages
These are checked at runtime; a clear error is raised if unavailable.
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Image formats we can OCR directly.
_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}

# Text-based formats that can be read directly without extraction tooling.
_TEXT_EXTS = {".txt", ".md", ".csv", ".json", ".yaml", ".yml", ".xml", ".html", ".htm"}

# A conservative per-page OCR cap to bound memory for arbitrarily large scanned PDFs.
_MAX_OCR_PAGES = 500


class IngestionError(Exception):
    """Raised when a document cannot be ingested."""


@dataclass
class Extraction:
    """Result of extracting text from one document."""
    kind: str                       # "pdf" | "image"
    text: str
    pages: int = 0
    is_scanned: bool = False
    ocr_used: bool = False
    source_name: str = ""


def _have(tool: str) -> bool:
    return shutil.which(tool) is not None


def _check_tools(need_ocr: bool = False) -> None:
    if not _have("pdftotext") and not _have("pdfinfo"):
        raise IngestionError("poppler-utils not installed (pdftotext/pdfinfo required for PDFs)")
    if need_ocr and not _have("tesseract"):
        raise IngestionError("tesseract not installed (required for scanned PDFs / images)")


def detect_kind(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".pdf":
        return "pdf"
    if ext in _IMAGE_EXTS:
        return "image"
    if ext in _TEXT_EXTS:
        return "text"
    raise IngestionError(f"unsupported document type: {ext!r} (supported: .pdf, {', '.join(sorted(_IMAGE_EXTS))}, {', '.join(sorted(_TEXT_EXTS))})")


# --------------------------------------------------------------------------- #
# PDF extraction
# --------------------------------------------------------------------------- #

def _pdf_is_scanned(path: Path) -> bool:
    """Heuristic: a PDF is scanned if pdftotext yields no meaningful text."""
    text = _pdftotext(path)
    return len(text.strip()) < 20


def _pdftotext(path: Path) -> str:
    if not _have("pdftotext"):
        return ""
    try:
        r = subprocess.run(
            ["pdftotext", "-q", "-layout", str(path), "-"],
            capture_output=True, text=True, timeout=300,
        )
        return r.stdout or ""
    except (subprocess.SubprocessError, OSError):
        return ""


def _ocr_pdf(path: Path, max_pages: int = _MAX_OCR_PAGES) -> str:
    """Render PDF pages to images (pdftoppm) and OCR them (tesseract)."""
    if not (_have("pdftoppm") and _have("tesseract")):
        raise IngestionError("pdftoppm + tesseract required to OCR a scanned PDF")
    with tempfile.TemporaryDirectory() as tmp:
        tmpd = Path(tmp)
        try:
            r = subprocess.run(
                ["pdftoppm", "-r", "200", "-png", str(path), str(tmpd / "page")],
                capture_output=True, timeout=600,
            )
        except (subprocess.SubprocessError, OSError) as exc:
            raise IngestionError(f"pdftoppm failed: {exc}") from exc
        if r.returncode != 0:
            raise IngestionError("pdftoppm could not render PDF pages")
        pages = sorted(tmpd.glob("page-*.png"))
        if not pages:
            return ""
        # Bound work for huge documents (OCR the first N pages).
        chosen = pages[:max_pages]
        parts = [_tesseract_image(p) for p in chosen]
        return "\n\n".join(parts)


def extract_pdf(path: Path, *, ocr_max_pages: int = _MAX_OCR_PAGES) -> Extraction:
    _check_tools()
    try:
        page_count = int(
            subprocess.run(["pdfinfo", str(path)], capture_output=True, text=True)
            .stdout.split("Pages:")[1].split("\n")[0].strip()
        )
    except (IndexError, ValueError, subprocess.SubprocessError):
        page_count = 0

    is_scanned = _pdf_is_scanned(path)
    if is_scanned and _have("pdftoppm"):
        ocr_used = True
        text = _ocr_pdf(path, ocr_max_pages)
    else:
        ocr_used = False
        text = _pdftotext(path)

    return Extraction(
        kind="pdf", text=text, pages=page_count,
        is_scanned=is_scanned, ocr_used=ocr_used, source_name=path.name,
    )


# --------------------------------------------------------------------------- #
# Image extraction
# --------------------------------------------------------------------------- #

def _tesseract_image(img: Any) -> str:
    if not _have("tesseract"):
        raise IngestionError("tesseract not installed (required for image OCR)")
    try:
        from PIL import Image  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise IngestionError("Pillow not installed (required for image OCR)") from exc
    if isinstance(img, Image.Image):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=True) as tf:
            img.save(tf.name)
            return _tesseract_path(Path(tf.name))
    return _tesseract_path(img)


def _tesseract_path(path: Path) -> str:
    try:
        r = subprocess.run(
            ["tesseract", str(path), "stdout", "-l", "eng"],
            capture_output=True, text=True, timeout=300,
        )
        return r.stdout or ""
    except (subprocess.SubprocessError, OSError):
        return ""


def extract_image(path: Path) -> Extraction:
    _check_tools(need_ocr=True)
    try:
        from PIL import Image  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise IngestionError("Pillow not installed (required for image OCR)") from exc
    try:
        with Image.open(path) as img:
            # Normalize to improve OCR: grayscale + modest upscale for tiny images.
            if img.mode not in ("L", "1"):
                img = img.convert("L")
            if min(img.size) < 800:
                scale = max(1.0, 800 / min(img.size))
                img = img.resize((int(img.size[0] * scale), int(img.size[1] * scale)))
            text = _tesseract_image(img)
    except OSError as exc:
        raise IngestionError(f"cannot open image {path}: {exc}") from exc
    return Extraction(kind="image", text=text, is_scanned=True, ocr_used=True, source_name=path.name)


# --------------------------------------------------------------------------- #
# Text file extraction
# --------------------------------------------------------------------------- #

def extract_text_file(path: Path) -> Extraction:
    """Read a text-based document's contents directly (no OCR/extraction tooling).

    CSV/JSON are `kind: text`; the extracted text is a plaintext rendering of the
    content so a Draft seam can propose entities/connections from it.
    """
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise IngestionError(f"cannot read text file {path}: {exc}") from exc
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        # Best-effort: a single-byte fallback so Latin-1/locale text still
        # extracts without crashing; the request records it as ocr_used=False.
        text = raw.decode("latin-1")
    return Extraction(
        kind="text", text=text, pages=0, is_scanned=False,
        ocr_used=False, source_name=path.name,
    )


# --------------------------------------------------------------------------- #
# Unified entry point + candidate construction
# --------------------------------------------------------------------------- #

def extract(path: Path, *, ocr_max_pages: int = _MAX_OCR_PAGES) -> Extraction:
    """Extract text from a PDF/image/scanned/text document. General-purpose entry point."""
    if not path.exists() or not path.is_file():
        raise IngestionError(f"not a file: {path}")
    kind = detect_kind(path)
    if kind == "pdf":
        return extract_pdf(path, ocr_max_pages=ocr_max_pages)
    if kind == "text":
        return extract_text_file(path)
    return extract_image(path)


def build_source_candidate(ext: Extraction, *, source_id: str | None = None) -> dict[str, Any]:
    """Build a schema-conforming canonical Source candidate from an Extraction.

    ADR-0035: the source object is a cite/location record (`id`, `type`,
    `citation`, optional `title`) — it conforms to `source.schema.json` and does
    NOT carry extraction-only fields. Those live in the CurationRequest sidecar,
    so a human Governance Gate sees a canonical-shaped source and the extraction
    metadata stays separate.
    """
    _id = source_id or "stemma:src.ingest-%08x" % (abs(hash((ext.source_name, ext.pages))) & 0xFFFFFFF)
    return {
        "id": _id,
        "type": "other",
        "citation": f"Ingested document: {ext.source_name}",
        "title": ext.source_name,
    }


def build_extraction_sidecar(ext: Extraction) -> dict[str, Any]:
    """Extraction metadata for the CurationRequest sidecar (ADR-0035).

    These are not canonical-source fields; they describe how the text was
    obtained so a reviewer can audit OCR/format/pages without the source record
    carrying extraction-only data.
    """
    return {
        "kind": ext.kind,
        "format": ext.kind,
        "pages": ext.pages,
        "is_scanned": ext.is_scanned,
        "ocr_used": ext.ocr_used,
        "preview": ext.text[:2000],
        "source_name": ext.source_name,
    }


def make_ingest_request(ext: Extraction) -> dict[str, Any]:
    """Build the payload (a CurationRequest 'source' + extraction sidecar) a runner
    feeds to the curation pipeline's Draft stage for entity/connection generation."""
    source = build_source_candidate(ext)
    return {
        "kind": "source",
        "intent": f"ingest document '{ext.source_name}' and propose canonical entities/connections from its content",
        "data": source,
        "extraction": build_extraction_sidecar(ext),
        "extracted_text": ext.text,
    }


def to_curation_request(ext: Extraction, *, kind: str = "entity",
                        source_anchor: str | None = None) -> "Any":
    """Return a scripts/curation_pipeline.CurationRequest from an extraction.

    This is the typed hand-off: extract() → CurationRequest → run_pipeline(). The
    extracted text rides on request.data['_extracted_text'] (draft input only) and
    the extraction metadata rides on request.extraction (ADR-0035 sidecar). The
    ingested Source id is on request.source_ref, so the Draft seam (an LLM)
    proposes canonical entities/connections anchored to that source. The Human
    Governance Gate still approves anything that enters canonical; ingestion
    itself never writes.

    ``kind`` is the *target* object kind the Draft should produce (default 'entity';
    use 'connection' when extracting couplet relationships). The Source candidate
    itself is produced by build_source_candidate and is a separate provenance object,
    not the thing that gets gated as an entity.
    """
    import curation_pipeline

    source = build_source_candidate(ext)
    return curation_pipeline.CurationRequest(
        kind=kind,
        intent=f"ingest document '{ext.source_name}' and propose canonical {kind}s from its content",
        data={**_empty_object(kind), "_extracted_text": ext.text},
        source_ref=source_anchor or source["id"],
        extraction=build_extraction_sidecar(ext),
    )


def _empty_object(kind: str) -> dict[str, Any]:
    """A minimal shape the seam will fill in — enough to pass identity/type checks."""
    if kind == "connection":
        return {
            "id": "stemma:conn.000000", "type": "connection",
            "source": "stemma:unknown", "relation": "related_to", "target": "stemma:unknown",
            "assertion": {"status": "active", "type": "proposed", "review": {"status": "unreviewed"}},
            "context": {}, "provenance": {},
        }
    if kind == "source":
        return {"id": "stemma:src.<slug>", "type": "source"}
    return {
        "id": "stemma:<domain>.<slug>", "type": "concept", "name": "", "domain": "general",
        "status": "draft", "definition": "", "provenance": {"ai_drafted": True},
    }


if __name__ == "__main__":
    import argparse
    import sys

    p = argparse.ArgumentParser(description="STEMMA knowledge ingestion (extract text from docs).")
    p.add_argument("path", help="PDF or image file to ingest")
    p.add_argument("--json", action="store_true", help="emit extraction + source candidate as JSON")
    args = p.parse_args()

    try:
        ex = extract(Path(args.path))
    except IngestionError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        import json
        payload = {
            "kind": ex.kind,
            "pages": ex.pages,
            "is_scanned": ex.is_scanned,
            "ocr_used": ex.ocr_used,
            "char_count": len(ex.text),
            "source_candidate": build_source_candidate(ex),
            "text_preview": ex.text[:500],
        }
        print(json.dumps(payload, indent=2))
    else:
        print(f"ingested {args.path} ({ex.kind}, {ex.pages} pages, {'scanned/OCR' if ex.ocr_used else 'text'}):")
        print(f"  extracted {len(ex.text)} chars")
        print("  preview:", ex.text[:200].replace("\n", " "))
    sys.exit(0)