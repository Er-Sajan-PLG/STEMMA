#!/usr/bin/env python3
"""HTTP-level regression tests for webapp/server.py security + routing fixes.

Spins the real stdlib server on an ephemeral 127.0.0.1 port against a temporary
workflow directory (never the repo's workflow/). Covers:

- semantic endpoints no longer crash with UnboundLocalError (stray local
  ``import json`` in _dispatch_post shadowed the module for the whole handler);
- POST /api/semantic/extract is routed to its handler (was swallowed by the
  /api/documents/{id}/extract route and returned 404);
- claims_file is confined to the workflow directory (C3: arbitrary JSON read);
- doc_id / path ids are single safe segments (no traversal);
- C2: the stored API key is never forwarded to a different base_url;
- llm.json is 0600; default bind is 127.0.0.1; no CORS; Host/Origin guard.

Plain runnable script (exit 0 on pass) and pytest-compatible.
"""
from __future__ import annotations

import json
import pathlib
import sys
import tempfile
import threading
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "webapp"))

import server as S  # noqa: E402
from core import Workflow  # noqa: E402


class _Live:
    def __init__(self, tmp: pathlib.Path):
        self.wf = Workflow(tmp / "wf")
        self.srv = S.serve(host="127.0.0.1", port=0, workflow=self.wf)
        self.port = self.srv.server_address[1]
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()

    def call(self, method: str, path: str, body=None, headers=None):
        data = json.dumps(body).encode() if body is not None else None
        hdrs = {"Content-Type": "application/json"}
        hdrs.update(headers or {})
        req = urllib.request.Request(f"http://127.0.0.1:{self.port}{path}", data=data, headers=hdrs, method=method)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.status, dict(resp.headers), json.loads(resp.read().decode() or "null")
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode()
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                payload = raw
            return exc.code, dict(exc.headers), payload

    def close(self):
        self.srv.shutdown()
        self.srv.server_close()


def _claims_file(wf: Workflow) -> pathlib.Path:
    d = wf.root / "candidates" / "abc123"
    d.mkdir(parents=True, exist_ok=True)
    f = d / "semantic_claims.json"
    f.write_text(json.dumps({"claims": [{
        "claim_id": "c1",
        "claim": {"subject": "metre", "relation": "measures", "object": "length"},
        "evidence": {"text_span": "The metre is the SI unit of length."},
        "source": {"source_id": "stemma:src.test"},
    }]}), encoding="utf-8")
    return f


def test_semantic_extract_is_routed_not_404(tmp_path: pathlib.Path):
    live = _Live(tmp_path)
    try:
        st, _, body = live.call("POST", "/api/semantic/extract", {
            "text": "The metre is the SI unit of length. c = 299792458 m/s exactly.",
            "source_id": "stemma:src.test", "model": "deterministic", "provider": "deterministic"})
        assert st == 200, (st, body)
        assert "claims" in body and "local variable" not in json.dumps(body), body
    finally:
        live.close()
    print("PASS: /api/semantic/extract reaches its handler (no 404)")


def test_semantic_endpoints_do_not_crash(tmp_path: pathlib.Path):
    live = _Live(tmp_path)
    try:
        f = _claims_file(live.wf)
        rel = str(f.relative_to(live.wf.root))
        for ep in ("/api/semantic/verify", "/api/semantic/conflicts", "/api/semantic/resolve"):
            st, _, body = live.call("POST", ep, {"claims_file": rel})
            text = json.dumps(body)
            assert st == 200, (ep, st, body)
            assert "local variable" not in text and "UnboundLocalError" not in text, (ep, body)
    finally:
        live.close()
    print("PASS: semantic verify/conflicts/resolve run without UnboundLocalError")


def test_claims_file_confined_to_workflow(tmp_path: pathlib.Path):
    live = _Live(tmp_path)
    try:
        outside = tmp_path / "secret_outside.json"
        outside.write_text(json.dumps({"claims": [{"claim_id": "LEAKED"}]}), encoding="utf-8")
        attempts = [
            str(outside),                                   # absolute outside
            "../secret_outside.json",                       # traversal (workflow-relative)
            "candidates/../../secret_outside.json",         # traversal via subdir
            "/etc/passwd",                                  # non-json system file
            "README.md",                                    # repo file, not in workflow
        ]
        for ep in ("/api/semantic/verify", "/api/semantic/conflicts",
                   "/api/semantic/resolve", "/api/semantic/proposals"):
            for bad in attempts:
                st, _, body = live.call("POST", ep, {"claims_file": bad})
                assert st == 400, (ep, bad, st, body)
                assert "LEAKED" not in json.dumps(body), (ep, bad, body)
    finally:
        live.close()
    print("PASS: claims_file outside the workflow directory is rejected (400)")


def test_doc_ids_are_safe_segments(tmp_path: pathlib.Path):
    live = _Live(tmp_path)
    try:
        st, _, _ = live.call("GET", "/api/semantic/claims?doc_id=../../etc")
        assert st == 400, st
        st, _, _ = live.call("POST", "/api/semantic/extract", {"doc_id": "../../x"})
        assert st == 400, st
        st, _, _ = live.call("GET", "/api/documents/..")
        assert st == 404, st
    finally:
        live.close()
    print("PASS: doc_id / path ids reject traversal")


def _attacker_listener():
    """A local HTTP server recording any Authorization header it receives."""
    import http.server
    got: dict = {"auth": []}

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            got["auth"].append(self.headers.get("Authorization"))
            body = b'{"data":[{"id":"attacker-model"}]}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *a):  # noqa: D401
            return

    srv = http.server.HTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, got


DUMMY_KEY = "sk-DUMMY-OWNER-KEY-123"


def test_stored_key_never_sent_to_other_endpoint(tmp_path: pathlib.Path):
    """C2: POST /api/config/models with an attacker base_url must not receive the stored key."""
    live = _Live(tmp_path)
    evil, got = _attacker_listener()
    try:
        st, _, _ = live.call("POST", "/api/config", {"provider": "openai_compatible",
                              "base_url": "https://api.example.com/v1", "api_key": DUMMY_KEY, "model": "m"})
        assert st == 200
        evil_url = f"http://127.0.0.1:{evil.server_address[1]}"
        live.call("POST", "/api/config/models", {"provider": "openai_compatible", "base_url": evil_url})
        live.call("POST", "/api/config/models", {"provider": "openai_compatible", "base_url": evil_url,
                                                 "api_key": "••••-123"})
        leaked = [a for a in got["auth"] if a and DUMMY_KEY in a]
        assert not leaked, f"stored key was sent to a different endpoint: {got['auth']}"
    finally:
        evil.shutdown()
        live.close()
    print("PASS: stored key is never forwarded to a different base_url (C2)")


def test_changing_base_url_requires_reentering_key(tmp_path: pathlib.Path):
    live = _Live(tmp_path)
    try:
        live.call("POST", "/api/config", {"provider": "openai_compatible",
                  "base_url": "https://api.example.com/v1", "api_key": DUMMY_KEY, "model": "m"})
        # same endpoint + blank key -> key preserved
        st, _, body = live.call("POST", "/api/config", {"provider": "openai_compatible",
                                 "base_url": "https://api.example.com/v1", "api_key": "", "model": "m2"})
        assert st == 200 and body["api_key"].endswith("-123"), body
        # different endpoint + blank key -> refused, key not moved
        st, _, body = live.call("POST", "/api/config", {"provider": "openai_compatible",
                                 "base_url": "http://evil.example/v1", "api_key": "", "model": "m"})
        assert st == 400, (st, body)
        stored = json.loads((live.wf.root / "config" / "llm.json").read_text())
        assert stored["base_url"] == "https://api.example.com/v1" and stored["api_key"] == DUMMY_KEY
    finally:
        live.close()
    print("PASS: changing base_url requires re-entering the key")


def test_key_file_is_owner_only(tmp_path: pathlib.Path):
    live = _Live(tmp_path)
    try:
        live.call("POST", "/api/config", {"provider": "openai_compatible",
                  "base_url": "https://api.example.com/v1", "api_key": DUMMY_KEY, "model": "m"})
        f = live.wf.root / "config" / "llm.json"
        assert (f.stat().st_mode & 0o777) == 0o600, oct(f.stat().st_mode & 0o777)
        assert (f.parent.stat().st_mode & 0o777) == 0o700, oct(f.parent.stat().st_mode & 0o777)
    finally:
        live.close()
    print("PASS: llm.json is 0600 in a 0700 directory")


def test_cross_origin_and_rebinding_blocked(tmp_path: pathlib.Path):
    live = _Live(tmp_path)
    try:
        # cross-site page trying to drive the API
        st, hdrs, _ = live.call("POST", "/api/config/models", {"provider": "openai_compatible"},
                                headers={"Origin": "https://evil.example"})
        assert st == 403, st
        assert "Access-Control-Allow-Origin" not in hdrs
        # DNS rebinding: attacker hostname resolving to 127.0.0.1
        st, _, _ = live.call("GET", "/api/config", headers={"Host": "evil.example"})
        assert st == 403, st
        # CSRF via a 'simple' text/plain form post
        st, _, _ = live.call("POST", "/api/config", {"provider": "x"}, headers={"Content-Type": "text/plain"})
        assert st == 415, st
        # same-origin UI request still works, and carries no CORS header
        st, hdrs, _ = live.call("GET", "/api/config", headers={"Origin": f"http://127.0.0.1:{live.port}"})
        assert st == 200 and "Access-Control-Allow-Origin" not in hdrs, (st, hdrs)
        # preflight is never approved
        st, hdrs, _ = live.call("OPTIONS", "/api/config")
        assert st == 405 and "Access-Control-Allow-Origin" not in hdrs
    finally:
        live.close()
    print("PASS: cross-origin, DNS-rebinding and text/plain CSRF requests are blocked; UI unaffected")


def test_allowed_hosts_env(tmp_path: pathlib.Path, monkeypatch=None):
    import os
    old = os.environ.get("STEMMA_ALLOWED_HOSTS")
    os.environ["STEMMA_ALLOWED_HOSTS"] = "mybox.tail1234.ts.net"
    live = _Live(tmp_path)
    try:
        st, _, _ = live.call("GET", "/api/config", headers={"Host": "mybox.tail1234.ts.net"})
        assert st == 200, st
    finally:
        live.close()
        if old is None:
            os.environ.pop("STEMMA_ALLOWED_HOSTS", None)
        else:
            os.environ["STEMMA_ALLOWED_HOSTS"] = old
    print("PASS: STEMMA_ALLOWED_HOSTS admits a private-network name (e.g. Tailscale)")


def test_default_bind_is_loopback():
    import inspect
    assert inspect.signature(S.serve).parameters["host"].default == "127.0.0.1"
    print("PASS: default bind address is 127.0.0.1")


def main() -> int:
    tests = [test_semantic_extract_is_routed_not_404, test_semantic_endpoints_do_not_crash,
             test_claims_file_confined_to_workflow, test_doc_ids_are_safe_segments,
             test_stored_key_never_sent_to_other_endpoint, test_changing_base_url_requires_reentering_key,
             test_key_file_is_owner_only, test_cross_origin_and_rebinding_blocked, test_allowed_hosts_env]
    for fn in tests:
        with tempfile.TemporaryDirectory() as d:
            fn(pathlib.Path(d))
    test_default_bind_is_loopback()
    print("ALL WEBAPP SERVER SECURITY TESTS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
