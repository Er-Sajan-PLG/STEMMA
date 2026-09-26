#!/usr/bin/env python3
"""HTTP-level regression tests for webapp/server.py security + routing fixes.

Spins the real stdlib server on an ephemeral 127.0.0.1 port against a temporary
workflow directory (never the repo's workflow/). Covers:

- semantic endpoints no longer crash with UnboundLocalError (stray local
  ``import json`` in _dispatch_post shadowed the module for the whole handler);
- POST /api/semantic/extract is routed to its handler (was swallowed by the
  /api/documents/{id}/extract route and returned 404);
- claims_file is confined to the workflow directory (C3: arbitrary JSON read);
- doc_id / path ids are single safe segments (no traversal).

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


def main() -> int:
    tests = [test_semantic_extract_is_routed_not_404, test_semantic_endpoints_do_not_crash,
             test_claims_file_confined_to_workflow, test_doc_ids_are_safe_segments]
    for fn in tests:
        with tempfile.TemporaryDirectory() as d:
            fn(pathlib.Path(d))
    print("ALL WEBAPP SERVER SECURITY TESTS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
