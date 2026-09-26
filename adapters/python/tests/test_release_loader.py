"""Release loader: download, verification, cache and input rules — offline, no Sigstore needed.

Attestation is switched off explicitly here (checksum-only); the Sigstore path
is covered in test_release_attestation.py.
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import ASSETS, FIXTURE, REPO, TAG
from stemma_adapter import ExportError, Stemma
from stemma_adapter import release as R
from stemma_adapter.release import ReleaseError

PKG = Path(R.__file__).resolve().parent
CHECKSUM_ONLY = {"verify_attestation": False}


def _url(server, name="manifest.json"):
    return f"{server.base}/mirror/{name}"


def _entry_files(cache: Path) -> list[Path]:
    return sorted(p for p in cache.rglob("*") if p.is_file()) if cache.exists() else []


# ---------------------------------------------------------------- fixture provenance

def test_fixture_matches_published_digests():
    """The fixture is the real rc1 release: SHA256SUMS + manifest agree with the bytes."""
    sums = dict(line.split("  ")[::-1] for line in (FIXTURE / "SHA256SUMS.txt").read_text().splitlines())
    manifest = json.loads((FIXTURE / "manifest.json").read_text())
    assert manifest["release_tag"] == TAG
    for name in ASSETS[2:]:
        digest = hashlib.sha256((FIXTURE / name).read_bytes()).hexdigest()
        assert digest == sums[name] == manifest["files"][name]["sha256"], name
    # published digests (GitHub release API, 2026-09-26)
    assert hashlib.sha256((FIXTURE / "manifest.json").read_bytes()).hexdigest().startswith("648d44e0")
    assert sums["knowledge.learninghub.json"].startswith("c1d6ecde")


# ---------------------------------------------------------------- happy paths

def test_from_url_happy_path(server, client_tls, tmp_path):
    s = Stemma.from_url(_url(server), cache_dir=tmp_path, file="knowledge.learninghub.json",
                        ssl_context=client_tls, **CHECKSUM_ONLY)
    assert len(s.entities_by_id) == 7
    assert {e["status"] for e in s.entities_by_id.values()} == {"canonical"}  # learninghub tier
    info = s.release_info
    assert info["release_tag"] == TAG and info["verification"] == "checksum-only"
    assert info["sha256"].startswith("c1d6ecde")
    entry = Path(info["cache_entry"])
    assert entry.is_relative_to(tmp_path.resolve())
    assert sorted(p.name for p in entry.iterdir()) == ["SHA256SUMS.txt", "knowledge.learninghub.json", "manifest.json"]


def test_from_release_default_file(github, client_tls, tmp_path):
    s = Stemma.from_release(REPO, TAG, cache_dir=tmp_path, ssl_context=client_tls, **CHECKSUM_ONLY)
    assert len(s.entities_by_id) == 9  # knowledge.json = all statuses
    entry = Path(s.release_info["cache_entry"])
    assert entry.relative_to(tmp_path.resolve()).parts[:4] == ("github", "Er-Sajan-PLG", "STEMMA", TAG)
    assert entry.name == s.export["content_hash"].split(":")[1]
    assert github.requests == [f"/{REPO}/releases/download/{TAG}/{n}"
                               for n in ("manifest.json", "SHA256SUMS.txt", "knowledge.json")]


def test_from_file_and_from_dict_unchanged(tmp_path):
    data = json.loads((FIXTURE / "knowledge.learninghub.json").read_text())
    path = tmp_path / "k.json"
    path.write_text(json.dumps(data))
    assert Stemma.from_file(str(path)).release_info is None
    assert Stemma.from_dict(data).stats == Stemma.from_file(str(path)).stats


# ---------------------------------------------------------------- integrity

def test_flipped_byte_fails_closed_and_caches_nothing(server, client_tls, tmp_path):
    raw = bytearray(server.files["knowledge.learninghub.json"])
    raw[1000] ^= 0x01
    server.files["knowledge.learninghub.json"] = bytes(raw)
    with pytest.raises(ReleaseError, match="does not match SHA256SUMS"):
        Stemma.from_url(_url(server), cache_dir=tmp_path, file="knowledge.learninghub.json",
                        ssl_context=client_tls, **CHECKSUM_ONLY)
    assert _entry_files(tmp_path) == []


@pytest.mark.parametrize("name", ["knowledge.canonical.json", "knowledge.hash.json"])
def test_non_export_refused_before_body_download(server, client_tls, tmp_path, name):
    with pytest.raises(ReleaseError, match="not 'export'"):
        Stemma.from_url(_url(server), cache_dir=tmp_path, file=name, ssl_context=client_tls, **CHECKSUM_ONLY)
    assert server.asset_requests(name) == []  # body never requested
    assert _entry_files(tmp_path) == []


def test_unlisted_file_refused(server, client_tls, tmp_path):
    with pytest.raises(ReleaseError, match="not an asset"):
        Stemma.from_url(_url(server), cache_dir=tmp_path, file="knowledge.other.json",
                        ssl_context=client_tls, **CHECKSUM_ONLY)
    assert server.asset_requests("knowledge.other.json") == []


def test_release_error_is_an_export_error():
    assert issubclass(ReleaseError, ExportError)


# ---------------------------------------------------------------- cache

def test_cache_reuse_makes_zero_requests(server, client_tls, tmp_path):
    kw = dict(cache_dir=tmp_path, file="knowledge.learninghub.json", ssl_context=client_tls, **CHECKSUM_ONLY)
    Stemma.from_url(_url(server), **kw)
    before = len(server.requests)
    s = Stemma.from_url(_url(server), **kw)
    assert len(server.requests) == before
    assert len(s.entities_by_id) == 7


def test_offline_loads_valid_cache_with_server_gone(server, client_tls, tmp_path):
    kw = dict(cache_dir=tmp_path, file="knowledge.learninghub.json", ssl_context=client_tls, **CHECKSUM_ONLY)
    Stemma.from_url(_url(server), **kw)
    server.httpd.shutdown()
    server.httpd.server_close()
    s = Stemma.from_url(_url(server), offline=True, **kw)
    assert len(s.entities_by_id) == 7


def test_stale_cache_fails_offline_and_is_refetched_online(server, client_tls, tmp_path):
    kw = dict(cache_dir=tmp_path, file="knowledge.learninghub.json", ssl_context=client_tls, **CHECKSUM_ONLY)
    entry = Path(Stemma.from_url(_url(server), **kw).release_info["cache_entry"])
    cached = entry / "knowledge.learninghub.json"
    raw = bytearray(cached.read_bytes())
    raw[500] ^= 0x01
    cached.write_bytes(bytes(raw))
    before = len(server.requests)
    with pytest.raises(ReleaseError, match="offline=True and no valid cached copy"):
        Stemma.from_url(_url(server), offline=True, **kw)
    assert len(server.requests) == before  # offline never requests
    s = Stemma.from_url(_url(server), **kw)  # online: re-fetched and repaired
    assert len(s.entities_by_id) == 7
    assert hashlib.sha256(cached.read_bytes()).hexdigest() == s.release_info["sha256"]


def test_offline_without_cache_never_requests(server, client_tls, tmp_path):
    with pytest.raises(ReleaseError, match="offline=True"):
        Stemma.from_url(_url(server), cache_dir=tmp_path, offline=True, ssl_context=client_tls, **CHECKSUM_ONLY)
    assert server.requests == []


def test_cache_symlink_escape_refused(github, client_tls, tmp_path):
    cache, outside = tmp_path / "cache", tmp_path / "outside"
    (cache / "github").mkdir(parents=True)
    outside.mkdir()
    (cache / "github" / "Er-Sajan-PLG").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ReleaseError, match=r"Er-Sajan-PLG is a symlink — refusing"):
        Stemma.from_release(REPO, TAG, cache_dir=cache, ssl_context=client_tls, **CHECKSUM_ONLY)
    assert list(outside.iterdir()) == []


def test_cache_escape_is_refused_even_without_the_symlink_check(github, client_tls, tmp_path, monkeypatch):
    """Second layer: the resolved path must stay under cache_dir."""
    cache, outside = tmp_path / "cache", tmp_path / "outside"
    (cache / "github").mkdir(parents=True)
    outside.mkdir()
    (cache / "github" / "Er-Sajan-PLG").symlink_to(outside, target_is_directory=True)
    monkeypatch.setattr(R.Path, "is_symlink", lambda self: False)
    with pytest.raises(ReleaseError, match="cache path escapes cache_dir"):
        Stemma.from_release(REPO, TAG, cache_dir=cache, ssl_context=client_tls, **CHECKSUM_ONLY)
    assert list(outside.iterdir()) == []


def test_cached_file_symlink_refused(server, client_tls, tmp_path):
    kw = dict(cache_dir=tmp_path, file="knowledge.learninghub.json", ssl_context=client_tls, **CHECKSUM_ONLY)
    entry = Path(Stemma.from_url(_url(server), **kw).release_info["cache_entry"])
    real = tmp_path / "elsewhere.json"
    real.write_bytes((entry / "knowledge.learninghub.json").read_bytes())
    (entry / "knowledge.learninghub.json").unlink()
    (entry / "knowledge.learninghub.json").symlink_to(real)
    with pytest.raises(ReleaseError, match="cached knowledge.learninghub.json is not a regular file"):
        Stemma.from_url(_url(server), offline=True, **kw)
    # second layer: O_NOFOLLOW refuses the symlink even if the lstat check were skipped
    import stat as _stat
    real_lstat = R.os.lstat
    fake = lambda p, *a, **k: type("S", (), {"st_mode": _stat.S_IFREG, "st_size": real_lstat(p).st_size})()
    R.os.lstat, saved = fake, real_lstat
    try:
        with pytest.raises(ReleaseError, match="cannot read cached knowledge.learninghub.json"):
            Stemma.from_url(_url(server), offline=True, **kw)
    finally:
        R.os.lstat = saved


def test_failed_download_leaves_no_temp_files(server, client_tls, tmp_path):
    Stemma.from_url(_url(server), cache_dir=tmp_path, file="knowledge.learninghub.json",
                    ssl_context=client_tls, **CHECKSUM_ONLY)
    assert not [p for p in tmp_path.rglob(".tmp-*")]


# ---------------------------------------------------------------- transport

def test_plain_http_refused_without_request(server, tmp_path):
    with pytest.raises(ReleaseError, match="https://"):
        Stemma.from_url(_url(server).replace("https://", "http://"), cache_dir=tmp_path, **CHECKSUM_ONLY)
    assert server.requests == []


def test_https_redirect_to_cdn_is_followed(github, client_tls, tmp_path):
    github.redirect = "https"
    s = Stemma.from_release(REPO, TAG, cache_dir=tmp_path, file="knowledge.learninghub.json",
                            ssl_context=client_tls, **CHECKSUM_ONLY)
    assert len(s.entities_by_id) == 7
    assert any(p.startswith("/cdn/") for p in github.requests)


def test_redirect_to_http_refused(github, client_tls, tmp_path):
    github.redirect = "http"
    with pytest.raises(ReleaseError, match="non-HTTPS") as exc:
        Stemma.from_release(REPO, TAG, cache_dir=tmp_path, ssl_context=client_tls, **CHECKSUM_ONLY)
    assert "secret" not in str(exc.value)  # signed query strings are redacted
    assert not any(p.startswith("/cdn/") for p in github.requests)
    assert _entry_files(tmp_path) == []


def test_oversized_content_length_refused(server, client_tls, tmp_path):
    server.fake_length["manifest.json"] = R.MAX_MANIFEST_BYTES + 1
    with pytest.raises(ReleaseError, match="Content-Length"):
        Stemma.from_url(_url(server), cache_dir=tmp_path, ssl_context=client_tls, **CHECKSUM_ONLY)


def test_body_longer_than_manifest_size_stops_reading(server, client_tls, tmp_path):
    server.no_length_extra["knowledge.learninghub.json"] = b" " * 200_000
    with pytest.raises(ReleaseError, match="exceeds limit"):
        Stemma.from_url(_url(server), cache_dir=tmp_path, file="knowledge.learninghub.json",
                        ssl_context=client_tls, **CHECKSUM_ONLY)
    assert _entry_files(tmp_path) == []


def test_max_export_bytes_checked_before_download(server, client_tls, tmp_path):
    with pytest.raises(ReleaseError, match="max_export_bytes"):
        Stemma.from_url(_url(server), cache_dir=tmp_path, file="knowledge.learninghub.json",
                        max_export_bytes=1000, ssl_context=client_tls, **CHECKSUM_ONLY)
    assert server.asset_requests("knowledge.learninghub.json") == []


# ---------------------------------------------------------------- strict parsing

def _serve_manifest(server, mutate):
    m = json.loads(server.files["manifest.json"])
    server.files["manifest.json"] = mutate(m) if callable(mutate) else mutate


def test_manifest_duplicate_keys_refused(server, client_tls, tmp_path):
    raw = server.files["manifest.json"].decode()
    server.files["manifest.json"] = raw.replace('{\n', '{\n  "release_tag": "v9.9.9",\n', 1).encode()
    with pytest.raises(ReleaseError, match="duplicate JSON key"):
        Stemma.from_url(_url(server), cache_dir=tmp_path, ssl_context=client_tls, **CHECKSUM_ONLY)


def test_manifest_and_sums_must_agree(server, client_tls, tmp_path):
    def mutate(m):
        m["files"]["knowledge.learninghub.json"]["sha256"] = "0" * 64
        return json.dumps(m).encode()
    _serve_manifest(server, mutate)
    with pytest.raises(ReleaseError, match="disagree"):
        Stemma.from_url(_url(server), cache_dir=tmp_path, file="knowledge.learninghub.json",
                        ssl_context=client_tls, **CHECKSUM_ONLY)


@pytest.mark.parametrize("mutate,match", [
    (lambda s: s + s.splitlines(True)[0], "duplicate entry"),
    (lambda s: s.replace(s[:64], s[:64].upper(), 1), "lowercase"),
    (lambda s: s.replace("  knowledge.json", "  ../knowledge.json"), "lowercase hex|unsafe"),
    (lambda s: s.replace("  ", " *", 1), "lowercase"),
])
def test_sums_strict(server, client_tls, tmp_path, mutate, match):
    server.files["SHA256SUMS.txt"] = mutate(server.files["SHA256SUMS.txt"].decode()).encode()
    with pytest.raises(ReleaseError, match=match):
        Stemma.from_url(_url(server), cache_dir=tmp_path, ssl_context=client_tls, **CHECKSUM_ONLY)


def test_release_tag_must_match_request(github, client_tls, tmp_path):
    github.tags.add("v3.0.0-rc2")  # rc1 files served under another tag
    with pytest.raises(ReleaseError, match="release_tag 'v3.0.0-rc1' != requested 'v3.0.0-rc2'"):
        Stemma.from_release(REPO, "v3.0.0-rc2", cache_dir=tmp_path, ssl_context=client_tls, **CHECKSUM_ONLY)


def test_expected_ref_pins_mirror_tag(server, client_tls, tmp_path):
    with pytest.raises(ReleaseError, match="!= requested 'v3.0.0'"):
        Stemma.from_url(_url(server), cache_dir=tmp_path, expected_ref="refs/tags/v3.0.0",
                        ssl_context=client_tls, **CHECKSUM_ONLY)


# ---------------------------------------------------------------- input validation (no request made)

@pytest.mark.parametrize("tag", ["latest", "", "v3", "3.0.0", "v3.0.0-beta", "v3.0.0-rc1/../x", "v3.0.0\n", None])
def test_tag_must_be_explicit(server, tmp_path, tag):
    with pytest.raises(ReleaseError, match="tag must be"):
        Stemma.from_release(REPO, tag, cache_dir=tmp_path, **CHECKSUM_ONLY)


@pytest.mark.parametrize("repo", ["../x", "a/b/c", "owner/..", "own er/x", "owner", "-x/y", "o/./"])
def test_repo_validated(tmp_path, repo):
    with pytest.raises(ReleaseError, match="repo must be"):
        Stemma.from_release(repo, TAG, cache_dir=tmp_path, **CHECKSUM_ONLY)


@pytest.mark.parametrize("file", ["../x.json", "/etc/passwd", "a/b.json", "a\\b.json", "%2e%2e", "..",
                                  "", ".hidden", "knowledge..json", "k json"])
def test_file_validated(server, tmp_path, file):
    with pytest.raises(ReleaseError, match="file must be"):
        Stemma.from_url(_url(server), cache_dir=tmp_path, file=file, **CHECKSUM_ONLY)
    assert server.requests == []


@pytest.mark.parametrize("url", ["https://" + "user:" + "pw" + "@example.org/manifest.json",  # creds in URL "https://example.org/x.json",
                                 "https://example.org/manifest.json?x=1", "file:///etc/manifest.json",
                                 "ftp://example.org/manifest.json"])
def test_manifest_url_validated(tmp_path, url):
    with pytest.raises(ReleaseError):
        Stemma.from_url(url, cache_dir=tmp_path, **CHECKSUM_ONLY)


def test_from_url_attestation_needs_caller_identity(server, tmp_path):
    with pytest.raises(ReleaseError, match="expected_repository"):
        Stemma.from_url(_url(server), cache_dir=tmp_path, expected_ref=f"refs/tags/{TAG}")
    with pytest.raises(ReleaseError, match="expected_repository"):
        Stemma.from_url(_url(server), cache_dir=tmp_path, expected_repository=REPO)
    with pytest.raises(ReleaseError, match="expected_ref must be"):
        Stemma.from_url(_url(server), cache_dir=tmp_path, expected_repository=REPO, expected_ref="main")
    assert server.requests == []


def test_cache_dir_is_keyword_only():
    with pytest.raises(TypeError):
        Stemma.from_release(REPO, TAG, "/tmp/cache")  # type: ignore[misc]
    with pytest.raises(TypeError):
        Stemma.from_url("https://x/manifest.json", "/tmp/cache")  # type: ignore[misc]


# ---------------------------------------------------------------- verification extra / isolation

def _hide_sigstore(monkeypatch):
    import stemma_adapter

    for name in list(sys.modules):
        if name == "sigstore" or name.startswith("sigstore."):
            monkeypatch.setitem(sys.modules, name, None)
    monkeypatch.setitem(sys.modules, "sigstore", None)
    monkeypatch.delitem(sys.modules, "stemma_adapter.attest", raising=False)
    monkeypatch.delattr(stemma_adapter, "attest", raising=False)


def test_default_verification_without_extra_fails_before_any_request(github, monkeypatch, tmp_path):
    _hide_sigstore(monkeypatch)
    with pytest.raises(ReleaseError) as exc:
        Stemma.from_release(REPO, TAG, cache_dir=tmp_path)
    assert str(exc.value) == 'Release attestation verification requires:\npip install "stemma-adapter[verify]"'
    assert github.requests == []


def test_package_import_is_lean():
    code = ("import sys, stemma_adapter; from stemma_adapter import Stemma; "
            "assert 'stemma_adapter.release' not in sys.modules; "
            "import stemma_adapter.release; "
            "bad = [m for m in ('sigstore', 'stemma_adapter.attest', 'stemma_adapter.server', 'stemma_adapter.cli') "
            "if m in sys.modules]; assert not bad, bad; "
            "from stemma_adapter import ReleaseError; print('ok')")
    env = {**os.environ, "PYTHONPATH": str(PKG.parent)}
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=env, cwd="/")
    assert r.returncode == 0 and r.stdout.strip() == "ok", r.stderr


@pytest.mark.parametrize("module", ["release.py", "client.py", "loader.py"])
def test_release_path_has_no_repo_coupling(module):
    tree = ast.parse((PKG / module).read_text(encoding="utf-8"))
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    attrs = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    imported = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom):
            imported |= {n.module or ""} | {a.name for a in n.names}
        elif isinstance(n, ast.Import):
            imported |= {a.name for a in n.names}
    assert "__file__" not in names and "ROOT" not in names and "parents" not in attrs  # no repo paths
    assert not imported & {"server", "cli", "stemma_adapter.server", "stemma_adapter.cli"}
    assert not any(m.split(".")[0] == "sigstore" for m in imported)
    if module != "release.py":
        assert "attest" not in imported  # only release.py may (lazily) load the verifier


def test_adapter_versions_agree():
    import stemma_adapter
    from stemma_adapter import server

    pyproject = (PKG.parent / "pyproject.toml").read_text()
    assert 'version = "0.3.0"' in pyproject
    assert stemma_adapter.__version__ == server.ADAPTER_VERSION == "0.3.0"
    assert 'verify = ["sigstore>=4,<5"]' in pyproject


def test_base_group_really_lacks_sigstore():
    """CI's base group sets STEMMA_FORBID_SIGSTORE=1 to prove the SDK works without the extra."""
    if os.environ.get("STEMMA_FORBID_SIGSTORE") != "1":
        pytest.skip("only meaningful in the base CI group")
    import importlib.util

    assert importlib.util.find_spec("sigstore") is None
