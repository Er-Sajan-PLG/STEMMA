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
    # An incomplete (no API key) provider must fail closed, independent of whether
    # a real local Antigravity agent happens to be installed on the host.
    wf.save_llm_config(provider="gemini_api", base_url="https://generativelanguage.googleapis.com/v1beta",
                       model="gemini-mock", api_key="")
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
    saved = wf.save_llm_config(provider="openai_compatible", base_url="https://api.example.com/v1", model="example-model", api_key="k1234")
    assert saved["provider"] == "openai_compatible"
    assert saved["configured"] is True
    assert saved["api_key"] == "••••1234"
    real = wf.read_llm_config()
    assert real["api_key"] == "k1234"

    # A subsequent save with the masked value must NOT overwrite the secret.
    again = wf.save_llm_config(provider="openai_compatible", base_url="https://api.example.com/v1", model="example-model", api_key=saved["api_key"])
    assert again["configured"] is True
    assert wf.read_llm_config()["api_key"] == "k1234"
    print("PASS: LLM config masks and preserves secret")


def test_provider_canonicalization(tmp_path: pathlib.Path):
    wf = _fresh_workflow(tmp_path)
    saved = wf.save_llm_config(provider="google", base_url="https://generativelanguage.googleapis.com/v1beta",
                               model="gemini-3-pro-preview", api_key="k1234")
    assert saved["provider"] == "gemini_api", "google alias must canonicalize to gemini_api"
    print("PASS: provider aliases canonicalized")


def test_gemini_config_roundtrip(tmp_path: pathlib.Path):
    wf = _fresh_workflow(tmp_path)
    saved = wf.save_llm_config(provider="gemini_api", base_url="https://generativelanguage.googleapis.com/v1beta",
                               model="gemini-3-pro-preview", api_key="k1234")
    assert saved["provider"] == "gemini_api"
    assert saved["configured"] is True
    assert saved["api_key"] == "••••1234"
    real = wf.read_llm_config()
    assert real["provider"] == "gemini_api"
    assert real["api_key"] == "k1234"
    # Switching provider must not reuse a Gemini key for OpenAI-compatible.
    again = wf.save_llm_config(provider="openai_compatible", base_url="https://api.openai.com/v1",
                               model="gpt-4o-mini", api_key=saved["api_key"])
    assert again["configured"] is False
    print("PASS: Gemini LLM config roundtrip + provider isolation")


def test_provider_registry_contract():
    import providers
    # Four distinct entitlement paths, Antigravity is official/local.
    assert set(providers.PROVIDER_IDS) == {"antigravity", "gemini_api", "vertex_ai", "openai_compatible"}
    # Aliases never leak into persistence.
    assert providers.canonical_provider("google") == "gemini_api"
    assert providers.canonical_provider("openai") == "openai_compatible"
    # Antigravity does not require an API key; Gemini API does.
    assert providers.spec("antigravity").needs_api_key is False
    assert providers.spec("gemini_api").needs_api_key is True
    print("PASS: provider registry contract")


def test_agy_headless_command(tmp_path):
    import providers
    cmd = providers.agy_command({"provider": "antigravity", "model": "gemini-3.1-pro-high",
                                 "effort": "high"}, "hello", timeout="20m")
    assert cmd[0] == "agy"
    assert cmd[1] == "-p" and cmd[2] == "hello"
    assert "--model" in cmd and cmd[cmd.index("--model") + 1] == "gemini-3.1-pro-high"
    assert "--effort" in cmd and cmd[cmd.index("--effort") + 1] == "high"
    assert "--print-timeout" in cmd and cmd[cmd.index("--print-timeout") + 1] == "20m"
    print("PASS: agy command builds official headless invocation")


def test_provider_json_parsing():
    import providers
    assert providers.json_from_content("```json\n{\"candidates\": []}\n```") == {"candidates": []}
    assert providers.json_from_content("{\"a\":1}") == {"a": 1}
    assert providers._extract_chat_text("bare text") == "bare text"
    openai = {"choices": [{"message": {"content": "{\"candidates\":[]}"}}]}
    assert providers.json_from_content(providers._extract_chat_text(openai)) == {"candidates": []}
    gemini = {"candidates": [{"content": {"parts": [{"text": "{\"candidates\":[]}"}]}}]}
    assert providers.json_from_content(providers._extract_chat_text(gemini)) == {"candidates": []}
    print("PASS: provider JSON/fence parsing")


def test_antigravity_availability_uses_local_tool(tmp_path):
    import providers
    old = providers._sdk_importable
    providers._sdk_importable = lambda: False  # type: ignore[assignment]
    try:
        # agy is not on PATH in the gate environment by default, so it should
        # fail closed with an installation message rather than silently using a
        # Gemini API key.
        av = providers.availability("antigravity", {})
        assert av["ok"] is False or av["mechanism"] in ("antigravity-sdk", "antigravity-cli")
        if not av["ok"]:
            assert "Antigravity" in av["message"]
            assert "API key" not in av["message"].lower()
    finally:
        providers._sdk_importable = old  # type: ignore[assignment]
    print("PASS: Antigravity availability fails closed without local agent")


def test_google_request_shape():
    config = {"provider": "google", "base_url": "https://generativelanguage.googleapis.com/v1beta",
              "model": "gemini-3-pro-preview", "api_key": "g1234"}
    url, body, headers = Workflow._google_request(config, "Propose candidates.")
    assert url.endswith("/models/gemini-3-pro-preview:generateContent")
    assert headers["x-goog-api-key"] == "g1234"
    assert "Authorization" not in headers
    payload = json.loads(body.decode("utf-8"))
    assert payload["contents"][0]["parts"][0]["text"] == "Propose candidates."
    assert payload["generationConfig"]["responseMimeType"] == "application/json"
    print("PASS: Google Gemini request shape")


def test_antigravity_openai_request_shape():
    config = {"provider": "antigravity", "base_url": "http://127.0.0.1:6012/v1",
              "model": "gemini-3-pro", "api_key": "local"}
    url, body, headers = Workflow._openai_request(config, "Propose candidates.")
    assert url == "http://127.0.0.1:6012/v1/chat/completions"
    assert headers["Authorization"] == "Bearer local"
    payload = json.loads(body.decode("utf-8"))
    assert "response_format" not in payload, "local harnesses must not be forced to json_object"
    assert payload["model"] == "gemini-3-pro"
    print("PASS: Antigravity/local-harness request shape")


def test_parse_openai_fenced_payload():
    payload = {"choices": [{"message": {"content": "```json\n{\"candidates\":[]}\n```"}}]}
    assert Workflow._parse_openai_payload(payload) == {"candidates": []}
    print("PASS: OpenAI-compatible fenced JSON parsing")


def test_list_provider_models_openai_shape(tmp_path):
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    class H(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            if self.path != "/v1/models":
                self.send_response(404); self.end_headers(); return
            body = json.dumps({"object": "list", "data": [
                {"id": "gemini-3-pro", "object": "model"},
                {"id": "gemini-3.1-pro-high", "object": "model"},
                {"id": "claude-opus-4-6-thinking", "object": "model"},
            ]}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        def log_message(self, *a): pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), H)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    port = server.server_address[1]
    try:
        wf = Workflow(tmp_path / "wf")
        result = wf.list_provider_models(
            provider="openai_compatible",
            base_url=f"http://127.0.0.1:{port}/v1",
            api_key="local",
        )
    finally:
        server.shutdown()
    assert result["ok"] is True
    assert result["count"] == 3
    assert "gemini-3-pro" in result["models"]
    assert "claude-opus-4-6-thinking" in result["models"]
    print("PASS: OpenAI-compatible harness model listing")


def test_list_provider_models_gemini_shape(tmp_path):
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    class H(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            body = json.dumps({"models": [{"name": "models/gemini-3-pro-preview"},
                                          {"name": "models/gemini-3-flash"}]}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        def log_message(self, *a): pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), H)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    port = server.server_address[1]
    try:
        wf = Workflow(tmp_path / "wf2")
        result = wf.list_provider_models(provider="gemini_api",
                                         base_url=f"http://127.0.0.1:{port}/v1beta",
                                         api_key="g1234")
    finally:
        server.shutdown()
    assert "gemini-3-pro-preview" in result["models"]
    assert "gemini-3-flash" in result["models"]
    print("PASS: Gemini API model listing")


def test_provider_login_antigravity_instructions(tmp_path):
    wf = Workflow(tmp_path / "wf")
    result = wf.provider_login(provider="antigravity")
    assert result["ok"] is False
    assert "Antigravity CLI" in result["message"] or "Antigravity SDK" in result["message"]
    assert "Google" in result["message"] and ("sign in" in result["message"].lower() or "credentials" in result["message"].lower())
    print("PASS: Antigravity sign-in uses local CLI/SDK, never a Google credential")


def test_provider_login_openai_harness(tmp_path):
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    class H(BaseHTTPRequestHandler):
        def do_POST(self):  # noqa: N802
            body = json.dumps({"url": "https://accounts.google.com/o/oauth2/auth?client=mock",
                               "message": "Sign in to Google AI Pro"}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        def log_message(self, *a): pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), H)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    port = server.server_address[1]
    try:
        wf = Workflow(tmp_path / "wf")
        result = wf.provider_login(provider="openai_compatible",
                                   base_url=f"http://127.0.0.1:{port}/v1",
                                   api_key="local")
    finally:
        server.shutdown()
    assert result["ok"] is True
    assert "accounts.google.com" in result["url"]
    assert "Sign in to Google AI Pro" in result["message"]
    print("PASS: OpenAI-compatible harness sign-in URL flow")


def test_provider_login_gemini_explains_key(tmp_path):
    wf = Workflow(tmp_path / "wf")
    result = wf.provider_login(provider="gemini_api", base_url="https://generativelanguage.googleapis.com/v1beta")
    assert result["ok"] is False
    assert "API key" in result["message"]
    print("PASS: Gemini provider sign-in guidance")


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
                  "model": "gemini-mock", "api_key": "g1234"}
        payload = wf._llm_chat(config, "Prompt")
        assert payload["candidates"][0]["proposal"]["id"] == "stemma:phys.mock"
        assert captured["path"].endswith("/models/gemini-mock:generateContent")
        assert captured["auth"] == "g1234"
        assert captured["body"]["generationConfig"]["responseMimeType"] == "application/json"

        # The UI's "Test provider" path uses the same adapter.
        wf.save_llm_config(provider="google", base_url=config["base_url"],
                           model="gemini-mock", api_key="g1234")
        probe = wf.test_llm_provider()
        assert probe["ok"] is True
        assert probe["provider"] == "gemini_api", "google alias canonicalizes to gemini_api"
    finally:
        server.shutdown()
        server.server_close()
    print("PASS: Gemini API adapter works against a local mock")


def test_antigravity_chat_dispatch_without_api_key(tmp_path):
    import providers
    wf = _fresh_workflow(tmp_path)
    original_transport = providers._antigravity_transport
    original_cli = providers._antigravity_cli_chat
    original_sdk = providers._antigravity_sdk_chat
    providers._antigravity_transport = lambda config: "cli"  # type: ignore[assignment]
    providers._antigravity_sdk_chat = lambda config, prompt: "should not be used"  # type: ignore[assignment]
    providers._antigravity_cli_chat = lambda config, prompt: json.dumps({  # type: ignore[assignment]
        "candidates": [{"kind": "entity", "proposal": {"id": "stemma:phys.antigravity-local"}}]
    })
    try:
        config = {"provider": "antigravity", "model": "gemini-3-pro", "api_key": ""}
        payload = wf._llm_chat(config, "Prompt")
        assert payload["candidates"][0]["proposal"]["id"] == "stemma:phys.antigravity-local"
    finally:
        providers._antigravity_transport = original_transport  # type: ignore[assignment]
        providers._antigravity_cli_chat = original_cli  # type: ignore[assignment]
        providers._antigravity_sdk_chat = original_sdk  # type: ignore[assignment]
    print("PASS: Antigravity chat dispatches via local agent without an API key")


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
        test_provider_canonicalization(tmp_path)
        test_gemini_config_roundtrip(tmp_path)
        test_antigravity_openai_request_shape()
        test_parse_openai_fenced_payload()
        test_provider_registry_contract()
        test_agy_headless_command(tmp_path)
        test_provider_json_parsing()
        test_antigravity_availability_uses_local_tool(tmp_path)
        test_list_provider_models_openai_shape(tmp_path)
        test_list_provider_models_gemini_shape(tmp_path)
        test_provider_login_antigravity_instructions(tmp_path)
        test_provider_login_openai_harness(tmp_path)
        test_provider_login_gemini_explains_key(tmp_path)
        test_google_request_shape()
        test_parse_google_payload()
        test_llm_chat_google_mock(tmp_path)
        test_antigravity_chat_dispatch_without_api_key(tmp_path)
        test_connection_requires_known_endpoints(tmp_path)
    print("ALL WEBAPP CORE TESTS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
