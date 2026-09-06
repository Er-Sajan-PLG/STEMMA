"""Tests for the STEMMA ingestion system (scripts/ingest.py).

Verifies deterministic extraction from text PDFs, scanned PDFs, and images; that it
never writes to canonical directories; and that it produces a well-formed Source
candidate for the curation pipeline (a human Governance Gate must approve later).

This repo runs tests as plain python3 scripts (no pytest); a __main__ driver is
provided at the bottom.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "scripts"))

import ingest  # noqa: E402


class SkipTest(Exception):
    """Raised to skip a test when a required system tool is unavailable."""


def _require(tool: str, reason: str) -> None:
    if not ingest._have(tool):
        raise SkipTest(f"{tool} unavailable: {reason}")


def _have(tool: str) -> bool:
    return ingest._have(tool)


def test_detect_kind():
    from pathlib import Path

    assert ingest.detect_kind(Path("doc.pdf")) == "pdf"
    assert ingest.detect_kind(Path("img.PNG")) == "image"
    assert ingest.detect_kind(Path("scan.tiff")) == "image"
    try:
        ingest.detect_kind(Path("notes.txt"))
        raise AssertionError("expected unsupported-type error")
    except ingest.IngestionError:
        pass


def test_extract_text_from_text_pdf(tmp_path: pathlib.Path):
    _require("pdftotext", "text-PDF extraction")
    _require("ps2pdf", "building a text PDF fixture")
    ps = tmp_path / "t.ps"
    ps.write_text(
        "%!PS\n/Courier findfont 12 scalefont setfont\n"
        "72 720 moveto (Mass is a quantity of matter.) show\nshowpage\n"
    )
    subprocess.run(["ps2pdf", str(ps), str(tmp_path / "t.pdf")], check=False)
    pdf = tmp_path / "t.pdf"
    if not pdf.exists():
        raise SkipTest("ps2pdf produced no PDF")
    ex = ingest.extract(pdf)
    assert ex.kind == "pdf"
    assert ex.is_scanned is False
    assert "quantity of matter" in ex.text


def test_extract_from_image(tmp_path: pathlib.Path):
    _require("tesseract", "image OCR")
    try:
        from PIL import Image, ImageDraw
    except ImportError as exc:
        raise SkipTest(f"Pillow unavailable: {exc}") from exc

    img = Image.new("L", (800, 80), 255)
    ImageDraw.Draw(img).text((10, 10), "F = m a", fill=0)
    p = tmp_path / "img.png"
    img.save(p)
    ex = ingest.extract(p)
    assert ex.kind == "image"
    assert ex.ocr_used is True
    # OCR may be imperfect but should capture the equation characters loosely.
    assert "F" in ex.text


def test_extract_scanned_pdf(tmp_path: pathlib.Path):
    """An image-only PDF should be detected as scanned and OCR'd."""
    _require("tesseract", "scanned-PDF OCR")
    _require("pdftoppm", "rendering scanned-PDF pages")
    try:
        from PIL import Image, ImageDraw
    except ImportError as exc:
        raise SkipTest(f"Pillow unavailable: {exc}") from exc

    img = Image.new("L", (900, 120), 255)
    ImageDraw.Draw(img).text((10, 10), "combustion of methane CH4 CO2", fill=0)
    pdf = tmp_path / "scan.pdf"
    img.save(pdf)  # Pillow writes an image-only PDF
    ex = ingest.extract(pdf)
    assert ex.kind == "pdf"
    assert ex.is_scanned is True
    assert ex.ocr_used is True
    assert len(ex.text.strip()) > 0


def test_source_candidate_shape():
    ex = ingest.Extraction(kind="pdf", text="some knowledge", pages=2, source_name="doc.pdf")
    src = ingest.build_source_candidate(ex, source_id="stemma:src.ingest-test")
    assert src["id"] == "stemma:src.ingest-test"
    assert src["type"] == "other"
    assert src["citation"].startswith("Ingested document:")
    assert src["title"] == "doc.pdf"
    # The extracted text / extraction metadata is carried on the request sidecar,
    # NOT stuffed into the canonical-shaped Source object.
    assert "text" not in src
    assert "kind" not in src
    assert "format" not in src
    assert "pages" not in src
    assert "ocr_used" not in src
    assert "extracted_text_preview" not in src
    assert "provenance" not in src


def test_source_candidate_conforms_to_schema():
    import json
    from jsonschema import Draft202012Validator

    schema = json.loads((pathlib.Path(__file__).resolve().parents[2] / "schema" / "source.schema.json").read_text())
    ex = ingest.Extraction(kind="pdf", text="some knowledge", pages=2, source_name="doc.pdf")
    src = ingest.build_source_candidate(ex, source_id="stemma:src.ingest-test")
    Draft202012Validator(schema).validate(src)
    # A required-member break must fail the schema (regression guard).
    broken = dict(src)
    broken.pop("citation")
    assert list(Draft202012Validator(schema).iter_errors(broken))
    print("PASS: source candidate conforms to source.schema.json")


def test_extraction_sidecar_keeps_metadata_out_of_source():
    ex = ingest.Extraction(kind="pdf", text="full text body", pages=1, source_name="a.pdf")
    sidecar = ingest.build_extraction_sidecar(ex)
    assert sidecar["kind"] == "pdf"
    assert sidecar["format"] == "pdf"
    assert sidecar["pages"] == 1
    assert "preview" in sidecar
    src = ingest.build_source_candidate(ex, source_id="stemma:src.ingest-test")
    assert src["id"] == "stemma:src.ingest-test"
    print("PASS: extraction metadata isolated from canonical source")


def test_make_ingest_request():
    ex = ingest.Extraction(kind="pdf", text="full text body", pages=1, source_name="a.pdf")
    req = ingest.make_ingest_request(ex)
    assert req["kind"] == "source"
    assert "extracted_text" in req
    assert req["extracted_text"] == "full text body"
    assert req["data"]["id"].startswith("stemma:src.")
    assert "kind" not in req["data"]
    assert "extraction" in req
    assert req["extraction"]["pages"] == 1


def test_ingest_never_writes_canonical(tmp_path: pathlib.Path):
    """The ingestion layer must not write to content/, connections/, or sources/."""
    try:
        from PIL import Image, ImageDraw
    except ImportError as exc:
        raise SkipTest(f"Pillow unavailable: {exc}") from exc

    img = Image.new("L", (400, 60), 255)
    ImageDraw.Draw(img).text((10, 10), "test", fill=0)
    p = tmp_path / "i.png"
    img.save(p)

    root = pathlib.Path(__file__).resolve().parents[2]
    dirs = [root / "content", root / "connections", root / "sources"]
    before = {str(c): len(list(c.rglob("*"))) for c in dirs}
    ex = ingest.extract(p)
    _ = ingest.build_source_candidate(ex)
    after = {str(c): len(list(c.rglob("*"))) for c in dirs}
    assert before == after, "ingestion must not modify canonical directories"


def test_to_curation_request_defaults_to_entity():
    ex = ingest.Extraction(kind="pdf", text="content", pages=1, source_name="doc.pdf")
    from ingest import to_curation_request

    req = to_curation_request(ex)
    assert req.kind == "entity"
    assert req.source_ref and req.source_ref.startswith("stemma:src.")
    assert "_extracted_text" in req.data
    assert req.data["_extracted_text"] == "content"
    # ADR-0028/0035: entity drafts carry no relationships.
    assert "relationships" not in req.data
    # ADR-0035: extraction metadata is in the sidecar, not the entity blueprint.
    assert req.extraction is not None
    assert req.extraction["pages"] == 1
    assert "extracted_text_preview" not in req.data


def test_to_curation_request_connection_kind():
    from ingest import to_curation_request

    ex = ingest.Extraction(kind="pdf", text="a relates to b", pages=1, source_name="doc.pdf")
    req = to_curation_request(ex, kind="connection")
    assert req.kind == "connection"
    assert req.data["type"] == "connection"


if __name__ == "__main__":
    import tempfile

    passed = skipped = 0
    with tempfile.TemporaryDirectory() as _tmp:
        _tmp_p = pathlib.Path(_tmp)
        fns = [
            test_detect_kind,
            (test_extract_text_from_text_pdf, _tmp_p),
            (test_extract_from_image, _tmp_p),
            (test_extract_scanned_pdf, _tmp_p),
            test_source_candidate_shape,
            test_source_candidate_conforms_to_schema,
            test_extraction_sidecar_keeps_metadata_out_of_source,
            test_make_ingest_request,
            (test_ingest_never_writes_canonical, _tmp_p),
            test_to_curation_request_defaults_to_entity,
            test_to_curation_request_connection_kind,
        ]
        for entry in fns:
            fn, *args = entry if isinstance(entry, tuple) else (entry,)
            try:
                fn(*args)
                passed += 1
                print(f"PASS {fn.__name__}")
            except SkipTest as e:
                skipped += 1
                print(f"SKIP {fn.__name__}: {e}")
    print(f"INGEST TESTS: {passed} pass, {skipped} skipped")
    if skipped:
        print("(some tests skipped: required system tool not available)")