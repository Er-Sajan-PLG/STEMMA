#!/usr/bin/env python3
"""ADR-0035: ingest → proposal staging correctness.

The proposal path must fail closed when no real Draft seam is wired, must never
stage a schema-invalid placeholder, and must never write a dossier whose
deterministic curation gates failed. Canonical extraction metadata stays out of
the source object.
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "scripts"))

import curation_pipeline  # noqa: E402
import ingest  # noqa: E402
import ingest_to_proposals as itp  # noqa: E402


def _bp(kind: str) -> curation_pipeline.CurationBlueprint:
    return curation_pipeline.CurationBlueprint(kind=kind, target_id=None)


def test_default_draft_fails_closed_for_entity_and_connection():
    try:
        itp._default_draft(_bp("entity"), {"_extracted_text": "x"})
    except itp.DraftSeamError as exc:
        assert "--draft" in str(exc)
    else:
        raise AssertionError("entity without a real seam must refuse to draft")

    try:
        itp._default_draft(_bp("connection"), {"_extracted_text": "x"})
    except itp.DraftSeamError:
        pass
    else:
        raise AssertionError("connection without a real seam must refuse to draft")

    # Source is the one object that does not need an LLM seam.
    data = {"id": "stemma:src.x", "type": "other", "citation": "a"}
    assert itp._default_draft(_bp("source"), data) == data
    print("PASS: default draft fails closed (entity/connection), allows source")


def test_stage_fails_closed_without_draft():
    """stage() must check the seam before touching the document."""
    try:
        itp.stage(pathlib.Path("missing.pdf"))
    except itp.DraftSeamError as exc:
        assert "--draft" in str(exc)
    else:
        raise AssertionError("stage() without a real seam must fail closed")
    print("PASS: stage fails closed without a Draft seam")


def test_main_requires_draft_before_reading_file():
    rc = itp.main(["--path", "missing.pdf", "--json"])
    assert rc == 1
    print("PASS: CLI requires --draft before touching the document")


def test_stage_rejects_gate_failure():
    """If the real seam produces a candidate that fails a deterministic gate,
    stage must raise and not return a staged dossier."""
    fake_ext = ingest.Extraction(kind="pdf", text="x", pages=1, source_name="doc.pdf")
    original_extract, original_to_req = ingest.extract, ingest.to_curation_request
    try:
        ingest.extract = lambda doc, **kw: fake_ext
        ingest.to_curation_request = lambda ext, **kw: curation_pipeline.CurationRequest(
            kind="entity",
            intent="test",
            data={"id": "nope", "type": "concept", "name": "Bad", "domain": "physics",
                  "status": "draft", "definition": "x", "provenance": {}},
            source_ref="stemma:src.test",
            extraction=ingest.build_extraction_sidecar(ext),
        )

        def bad_draft(bp, data, **kw):
            return {"id": "nope", "type": "concept", "name": "Bad", "domain": "physics",
                    "status": "draft", "definition": "x", "provenance": {}}

        try:
            itp.stage(pathlib.Path("any.pdf"), draft=bad_draft)
        except itp.ProposalGateError as exc:
            assert "refusing to stage" in str(exc)
        else:
            raise AssertionError("failed candidate must not be staged")
    finally:
        ingest.extract, ingest.to_curation_request = original_extract, original_to_req
    print("PASS: gate failure before staging is refused")


def test_good_entity_draft_stage_returns_dossier():
    """A schema-valid entity produced by a real seam passes deterministic gates
    and returns a dossier carrying both a schema-valid source and the sidecar."""
    import json
    from jsonschema import Draft202012Validator

    fake_ext = ingest.Extraction(kind="pdf", text="x", pages=2, source_name="doc.pdf")
    original_extract, original_to_req = ingest.extract, ingest.to_curation_request
    try:
        ingest.extract = lambda doc, **kw: fake_ext
        ingest.to_curation_request = lambda ext, **kw: curation_pipeline.CurationRequest(
            kind="entity",
            intent="test",
            data={"id": "stemma:test.p1", "type": "concept", "name": "P", "domain": "physics",
                  "status": "draft", "definition": "def", "provenance": {"ai_drafted": True}},
            source_ref="stemma:src.test",
            extraction=ingest.build_extraction_sidecar(ext),
        )

        def good_draft(bp, data, **kw):
            return {"id": "stemma:test.p1", "type": "concept", "name": "P", "domain": "physics",
                    "status": "draft", "definition": "def", "provenance": {"ai_drafted": True}}

        dossier = itp.stage(pathlib.Path("any.pdf"), draft=good_draft)
        assert dossier["proposal"]["publishable"] is True
        assert dossier["proposal"]["decision"] == "request_review"
        # The source candidate is schema-valid.
        schema = json.loads((pathlib.Path(__file__).resolve().parents[2] / "schema" / "source.schema.json").read_text())
        Draft202012Validator(schema).validate(dossier["source_candidate"])
        # Extraction metadata is in the sidecar, not on the source candidate.
        assert dossier["extraction"]["pages"] == 2
        assert "extracted_text_preview" not in dossier["source_candidate"]
    finally:
        ingest.extract, ingest.to_curation_request = original_extract, original_to_req
    print("PASS: valid draft stages a schema-valid dossier")


def main() -> int:
    test_default_draft_fails_closed_for_entity_and_connection()
    test_stage_fails_closed_without_draft()
    test_main_requires_draft_before_reading_file()
    test_stage_rejects_gate_failure()
    test_good_entity_draft_stage_returns_dossier()
    print("ALL INGEST-TO-PROPOSALS TESTS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
