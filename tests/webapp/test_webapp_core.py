#!/usr/bin/env python3
"""Webapp core tests (STEMMA ingestion/review webapp).

The webapp is a proposal-engineering tool: it must never write to content/,
connections/, or sources/. It stages schema-valid, human-reviewed proposals
under the git-ignored workflow/ dir only.
"""
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "webapp"))

from core import CandidateInvalid, ProviderNotConfigured, Workflow  # noqa: E402


def _fresh_workflow(tmp_path: pathlib.Path) -> Workflow:
    return Workflow(tmp_path / "wf")


def test_default_workflow_is_gitignored_path():
    # Default workflow lives under repo root/workflow which .gitignore excludes.
    wf = Workflow()
    assert wf.root.name == "workflow"
    assert str(wf.root).startswith(str(ROOT))
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "workflow/" in gitignore
    print("PASS: workflow dir is git-ignored")


def test_upload_and_text_extraction(tmp_path: pathlib.Path):
    wf = _fresh_workflow(tmp_path)
    doc = wf.accept_upload(original_name="laws.md", mime="text/markdown", data=b"# Laws\nForce equals mass times acceleration.\n")  # noqa: E501
    assert doc["kind"] == "text"
    assert doc["status"] == "uploaded"

    doc = wf.extract_document(doc["id"])
    assert doc["status"] == "ready"
    assert doc["extraction"]["kind"] == "text"
    assert doc["extraction"]["text_path"].endswith(f"{doc['id']}.txt")
    text = (wf.root / doc["extraction"]["text_path"]).read_text(encoding="utf-8")
    assert "Force equals mass times acceleration" in text
    assert "Force equals mass times acceleration" in doc["extraction"]["preview"]
    print("PASS: upload + text extraction")


def test_unsupported_type_is_retained_and_marked(tmp_path: pathlib.Path):
    wf = _fresh_workflow(tmp_path)
    doc = wf.accept_upload(original_name="report.xyz", mime="application/octet-stream", data=b"whatever")
    assert doc["kind"] == "other"
    doc = wf.extract_document(doc["id"])
    assert doc["status"] == "unsupported"
    assert "unsupported" in (doc.get("error") or "")
    assert (wf.root / doc["stored_path"]).exists(), "file must be retained"
    print("PASS: unsupported type retained + marked")


def test_generation_requires_provider(tmp_path: pathlib.Path):
    wf = _fresh_workflow(tmp_path)
    doc = wf.accept_upload(original_name="laws.txt", mime="text/plain", data=b"good content")
    wf.extract_document(doc["id"])
    try:
        wf.generate_candidates(doc["id"])
    except ProviderNotConfigured:
        pass
    else:
        raise AssertionError("generation must refuse without a configured LLM provider")
    print("PASS: generation fails closed until provider configured")


def test_validation_and_staging(tmp_path: pathlib.Path):
    wf = _fresh_workflow(tmp_path)
    doc = wf.accept_upload(original_name="laws.txt", mime="text/plain", data=b"good content")
    wf.extract_document(doc["id"])

    good = {"id": "stemma:phys.test-newton", "type": "concept", "name": "Newton's law",
            "domain": "physics", "status": "draft",
            "definition": "A proposed definition.",
            "provenance": {"ai_drafted": False, "source": "stemma:src.webapp-x"}}
    candidate = {"id": "cand-test", "doc_id": doc["id"], "kind": "entity",
                 "proposal": good, "findings": []}
    # Manually place the candidate for the core test.
    import uuid
    candidate["id"] = uuid.uuid4().hex[:12]
    (wf.candidates / f"{doc['id']}.json").write_text(
        json.dumps({"doc_id": doc["id"], "generated_at": "", "candidates": [candidate]}),
        encoding="utf-8")
    result = wf.stage_candidate(candidate["id"], reviewer="human:tester.001", note="test proposal")
    assert result["path"].endswith(".entity.proposal.yaml")
    # The proposal is NOT under content/connections/sources.
    assert not any(str(wf.root / result["path"]).startswith(str(ROOT / d)) for d in ("content", "connections", "sources"))
    assert (wf.root / result["path"]).exists()
    # Staged doc status reflects the human decision.
    assert wf.get_document(doc["id"])["status"] == "staged"
    print("PASS: schema-valid candidate stages into workflow/ proposal")


def test_invalid_candidate_refuses_stage(tmp_path: pathlib.Path):
    wf = _fresh_workflow(tmp_path)
    doc = wf.accept_upload(original_name="laws.txt", mime="text/plain", data=b"good content")
    wf.extract_document(doc["id"])
    bad = {"id": "not-an-id", "type": "concept", "name": "Bad", "domain": "physics",
           "status": "draft", "definition": "x", "provenance": {"ai_drafted": True}}
    candidate = {"id": "cand-bad", "doc_id": doc["id"], "kind": "entity", "proposal": bad, "findings": []}
    import uuid
    candidate["id"] = uuid.uuid4().hex[:12]
    (wf.candidates / f"{doc['id']}.json").write_text(
        json.dumps({"doc_id": doc["id"], "generated_at": "", "candidates": [candidate]}),
        encoding="utf-8")
    try:
        wf.stage_candidate(candidate["id"], reviewer="human:tester.001")
    except CandidateInvalid:
        pass
    else:
        raise AssertionError("invalid candidate must not stage")
    print("PASS: invalid candidate refuses to stage")


def test_llm_config_masks_and_preserves_secret(tmp_path: pathlib.Path):
    wf = _fresh_workflow(tmp_path)
    saved = wf.save_llm_config(base_url="https://api.example.com/v1", model="example-model", api_key="secret-key-1234")
    assert saved["configured"] is True
    assert saved["api_key"] == "••••1234"
    real = wf.read_llm_config()
    assert real["api_key"] == "secret-key-1234"

    # A subsequent save with the masked value must NOT overwrite the secret.
    again = wf.save_llm_config(base_url="https://api.example.com/v1", model="example-model", api_key=saved["api_key"])
    assert again["configured"] is True
    assert wf.read_llm_config()["api_key"] == "secret-key-1234"
    print("PASS: LLM config masks and preserves secret")


def test_connection_requires_known_endpoints(tmp_path: pathlib.Path):
    wf = _fresh_workflow(tmp_path)
    doc = wf.accept_upload(original_name="laws.txt", mime="text/plain", data=b"content")
    wf.extract_document(doc["id"])
    conn = {"id": "stemma:conn.999998", "type": "connection",
            "source": "stemma:phys.force", "relation": "requires",
            "target": "stemma:phys.unknown", "assertion": {"status": "active", "type": "proposed", "review": {"status": "unreviewed"}},
            "provenance": {"asserted_by": {"type": "human", "id": "human:tester.001"},
                           "generated_by": {"type": "human", "id": "human:tester.001"},
                           "method": {"type": "manual"}}}
    errs = wf.validate_candidate("connection", conn)
    assert any("source" in e or "target" in e or "does not resolve" in e or "unknown" in e for e in errs), errs
    print("PASS: connection proposals require known endpoints")


def main() -> int:
    import tempfile

    test_default_workflow_is_gitignored_path()
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = pathlib.Path(tmp)
        test_upload_and_text_extraction(tmp_path)
        test_unsupported_type_is_retained_and_marked(tmp_path)
        test_generation_requires_provider(tmp_path)
        test_validation_and_staging(tmp_path)
        test_invalid_candidate_refuses_stage(tmp_path)
        test_llm_config_masks_and_preserves_secret(tmp_path)
        test_connection_requires_known_endpoints(tmp_path)
    print("ALL WEBAPP CORE TESTS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
