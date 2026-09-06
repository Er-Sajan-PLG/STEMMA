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
    saved = wf.save_llm_config(provider="openai", base_url="https://api.example.com/v1", model="example-model", api_key="secret-key-1234")
    assert saved["configured"] is True
    assert saved["api_key"] == "••••1234"
    real = wf.read_llm_config()
    assert real["api_key"] == "secret-key-1234"

    # A subsequent save with the masked value must NOT overwrite the secret.
    again = wf.save_llm_config(provider="openai", base_url="https://api.example.com/v1", model="example-model", api_key=saved["api_key"])
    assert again["configured"] is True
    assert wf.read_llm_config()["api_key"] == "secret-key-1234"
    print("PASS: LLM config masks and preserves secret")


def test_google_config_roundtrip(tmp_path: pathlib.Path):
    wf = _fresh_workflow(tmp_path)
    saved = wf.save_llm_config(provider="google", base_url="https://generativelanguage.googleapis.com/v1beta",
                               model="gemini-3-pro-preview", api_key="AIza-test-key-1234")
    assert saved["provider"] == "google"
    assert saved["configured"] is True
    assert saved["api_key"] == "••••1234"
    real = wf.read_llm_config()
    assert real["provider"] == "google"
    assert real["api_key"] == "AIza-test-key-1234"
    # Switching provider must not reuse a Google key for OpenAI.
    again = wf.save_llm_config(provider="openai", base_url="https://api.openai.com/v1",
                               model="gpt-4o-mini", api_key=saved["api_key"])
    assert again["configured"] is False
    print("PASS: Google LLM config roundtrip + provider isolation")


def test_google_request_shape():
    config = {"provider": "google", "base_url": "https://generativelanguage.googleapis.com/v1beta",
              "model": "gemini-3-pro-preview", "api_key": "AIza-key"}
    url, body, headers = Workflow._google_request(config, "Propose candidates.")
    assert url.endswith("/models/gemini-3-pro-preview:generateContent")
    assert headers["x-goog-api-key"] == "AIza-key"
    assert "Authorization" not in headers
    payload = json.loads(body.decode("utf-8"))
    assert payload["contents"][0]["parts"][0]["text"] == "Propose candidates."
    assert payload["generationConfig"]["responseMimeType"] == "application/json"
    print("PASS: Google Gemini request shape")


def test_antigravity_openai_request_shape():
    config = {"provider": "antigravity", "base_url": "http://127.0.0.1:6012/v1",
              "model": "gemini-3-pro", "api_key": "any-local-key"}
    url, body, headers = Workflow._openai_request(config, "Propose candidates.")
    assert url == "http://127.0.0.1:6012/v1/chat/completions"
    assert headers["Authorization"] == "Bearer any-local-key"
    payload = json.loads(body.decode("utf-8"))
    assert "response_format" not in payload, "local harnesses must not be forced to json_object"
    assert payload["model"] == "gemini-3-pro"
    print("PASS: Antigravity/local-harness request shape")


def test_parse_openai_fenced_payload():
    payload = {"choices": [{"message": {"content": "```json\n{\"candidates\":[]}\n```"}}]}
    assert Workflow._parse_openai_payload(payload) == {"candidates": []}
    print("PASS: OpenAI-compatible fenced JSON parsing")


def test_parse_google_payload():
    raw = {"candidates": [{"content": {"parts": [{"text": "{\"candidates\":[{\"kind\":\"entity\",\"proposal\":{\"id\":\"stemma:phys.test\"}}]}"}]}}]}
    payload = Workflow._parse_google_payload(raw)
    assert payload["candidates"][0]["kind"] == "entity"
    # Fence-wrapped variant must also parse.
    fenced = {"candidates": [{"content": {"parts": [{"text": "```json\n{\"candidates\":[]}\n```"}]}}]}
    assert Workflow._parse_google_payload(fenced) == {"candidates": []}
    print("PASS: Google Gemini response parsing")


def test_llm_chat_google_mock(tmp_path: pathlib.Path):
    """End-to-end adapter test against a local Gemini-shaped HTTP mock."""
    import http.server
    import threading

    captured = {}

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_POST(self):  # noqa: N802
            length = int(self.headers.get("Content-Length") or 0)
            body = self.rfile.read(length)
            captured["path"] = self.path
            captured["auth"] = self.headers.get("x-goog-api-key")
            captured["body"] = json.loads(body.decode("utf-8"))
            encoded = json.dumps({
                "candidates": [{"content": {"parts": [{"text": json.dumps({
                    "candidates": [{"kind": "entity", "proposal": {"id": "stemma:phys.mock"}}]
                })}]}}]
            }).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        def log_message(self, *args):  # noqa: N802
            return

    wf = _fresh_workflow(tmp_path)
    server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        config = {"provider": "google", "base_url": f"http://127.0.0.1:{port}/v1beta",
                  "model": "gemini-mock", "api_key": "AIza-mock"}
        payload = wf._llm_chat(config, "Prompt")
        assert payload["candidates"][0]["proposal"]["id"] == "stemma:phys.mock"
        assert captured["path"].endswith("/models/gemini-mock:generateContent")
        assert captured["auth"] == "AIza-mock"
        assert captured["body"]["generationConfig"]["responseMimeType"] == "application/json"

        # The UI's "Test provider" path uses the same adapter.
        wf.save_llm_config(provider="google", base_url=config["base_url"],
                           model="gemini-mock", api_key="AIza-mock")
        probe = wf.test_llm_provider()
        assert probe["ok"] is True
        assert probe["provider"] == "google"
    finally:
        server.shutdown()
        server.server_close()
    print("PASS: Google Gemini adapter works against a local mock")


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
        test_google_config_roundtrip(tmp_path)
        test_antigravity_openai_request_shape()
        test_parse_openai_fenced_payload()
        test_google_request_shape()
        test_parse_google_payload()
        test_llm_chat_google_mock(tmp_path)
        test_connection_requires_known_endpoints(tmp_path)
    print("ALL WEBAPP CORE TESTS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
