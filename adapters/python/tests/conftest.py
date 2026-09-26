"""Offline HTTPS fixture for the release loader (no live network).

`fixtures/v3.0.0-rc1/` holds real, public files of the STEMMA v3.0.0-rc1
GitHub release: manifest.json, SHA256SUMS.txt, three exports-or-not assets,
and the public Sigstore attestation bundle returned by
`GET /repos/Er-Sajan-PLG/STEMMA/attestations/sha256:<digest>` (signed
`bundle_url` removed). They are byte-identical to the published assets
(reproducible rebuild from the tag) — see test_fixture_matches_published_digests.
"""

from __future__ import annotations

import json
import os
import shutil
import ssl
import subprocess
import sys
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

PYTHON_ROOT = Path(__file__).resolve().parents[1]
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "v3.0.0-rc1"
REPO = "Er-Sajan-PLG/STEMMA"
TAG = "v3.0.0-rc1"
ASSETS = ("manifest.json", "SHA256SUMS.txt", "knowledge.json", "knowledge.learninghub.json",
          "knowledge.canonical.json", "knowledge.hash.json")


class ReleaseFixture:
    """In-memory release host: GitHub-style download paths, a mirror, a CDN and the attestations API."""

    def __init__(self) -> None:
        self.files = {name: (FIXTURE / name).read_bytes() for name in ASSETS}
        self.attestations = (FIXTURE / "attestations-api.json").read_bytes()
        self.requests: list[str] = []
        self.redirect: str | None = None          # None | "https" | "http"
        self.no_length_extra: dict[str, bytes] = {}  # name -> junk appended, no Content-Length
        self.fake_length: dict[str, int] = {}     # name -> lying Content-Length header
        self.tags = {TAG}                          # tags served on download paths
        self.replay_any_digest = False             # API returns the genuine bundle for any digest
        self.base = ""

    def asset_requests(self, name: str) -> list[str]:
        return [p for p in self.requests if p.rsplit("/", 1)[-1] == name]

    def attestation_digests(self) -> set[str]:
        import base64
        bundle = json.loads(self.attestations)["attestations"][0]["bundle"]
        statement = json.loads(base64.b64decode(bundle["dsseEnvelope"]["payload"]))
        return {s["digest"]["sha256"] for s in statement["subject"]}


def _handler(fx: ReleaseFixture):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args) -> None:  # keep test output clean
            pass

        def _send(self, code: int, body: bytes, name: str | None = None) -> None:
            self.send_response(code)
            if name in fx.no_length_extra:
                body = body + fx.no_length_extra[name]
            elif name in fx.fake_length:
                self.send_header("Content-Length", str(fx.fake_length[name]))
            else:
                self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802
            path = urllib.parse.urlsplit(self.path).path
            fx.requests.append(path)
            parts = path.strip("/").split("/")
            # /<owner>/<repo>/releases/download/<tag>/<name>
            if len(parts) == 6 and parts[2:4] == ["releases", "download"]:
                if f"{parts[0]}/{parts[1]}" != REPO or parts[4] not in fx.tags:
                    return self._send(404, b"not found")
                name = parts[5]
                if fx.redirect and name in fx.files:
                    scheme = fx.redirect
                    host = fx.base.split("://", 1)[1]
                    self.send_response(302)
                    self.send_header("Location", f"{scheme}://{host}/cdn/{name}?X-Amz-Signature=secret")
                    self.send_header("Content-Length", "0")
                    self.end_headers()
                    return None
                return self._serve(name)
            if len(parts) == 2 and parts[0] in ("mirror", "cdn"):
                return self._serve(parts[1])
            # /repos/<owner>/<repo>/attestations/sha256:<hex>  (any repo: attacker-controlled API)
            if len(parts) == 5 and parts[0] == "repos" and parts[3] == "attestations":
                digest = parts[4].removeprefix("sha256:")
                if fx.replay_any_digest or digest in fx.attestation_digests():
                    return self._send(200, fx.attestations)
                return self._send(404, b'{"message":"Not Found"}')
            return self._send(404, b"not found")

        def _serve(self, name: str) -> None:
            if name not in fx.files:
                return self._send(404, b"not found")
            return self._send(200, fx.files[name], name)

    return Handler


@pytest.fixture(scope="session")
def tls_cert(tmp_path_factory):
    openssl = shutil.which("openssl")
    assert openssl, "openssl is required to build the local HTTPS fixture"
    d = tmp_path_factory.mktemp("tls")
    subprocess.run([openssl, "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "2",
                    "-subj", "/CN=127.0.0.1", "-addext", "subjectAltName=IP:127.0.0.1",
                    "-keyout", str(d / "key.pem"), "-out", str(d / "cert.pem")],
                   check=True, capture_output=True)
    return d / "cert.pem", d / "key.pem"


@pytest.fixture
def server(tls_cert):
    cert, key = tls_cert
    fx = ReleaseFixture()
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), _handler(fx))
    sctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    sctx.load_cert_chain(cert, key)
    httpd.socket = sctx.wrap_socket(httpd.socket, server_side=True)
    fx.base = f"https://127.0.0.1:{httpd.server_address[1]}"
    fx.httpd = httpd
    thread = threading.Thread(target=httpd.serve_forever, kwargs={"poll_interval": 0.02}, daemon=True)
    thread.start()
    yield fx
    httpd.shutdown()
    httpd.server_close()


@pytest.fixture
def client_tls(tls_cert):
    return ssl.create_default_context(cafile=str(tls_cert[0]))


@pytest.fixture
def github(server, monkeypatch):
    """Point from_release()'s GitHub endpoints at the fixture."""
    from stemma_adapter import release

    monkeypatch.setattr(release, "GITHUB_WEB", server.base)
    monkeypatch.setattr(release, "GITHUB_API", server.base)
    return server


def sigstore_available() -> bool:
    import importlib.util

    return importlib.util.find_spec("sigstore") is not None


requires_sigstore = pytest.mark.skipif(
    not sigstore_available() and os.environ.get("STEMMA_REQUIRE_SIGSTORE") != "1",
    reason="stemma-adapter[verify] not installed (CI runs these with STEMMA_REQUIRE_SIGSTORE=1)",
)
