"""Sigstore attestation policy — real v3.0.0-rc1 bundle, verified offline (embedded trust root).

Runs in CI's verify group (`pip install -e "adapters/python[verify]"`,
STEMMA_REQUIRE_SIGSTORE=1). No live network.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from conftest import FIXTURE, REPO, TAG, requires_sigstore
from stemma_adapter import Stemma
from stemma_adapter.release import ReleaseError

pytestmark = requires_sigstore

REF = f"refs/tags/{TAG}"
EXPORT = "knowledge.learninghub.json"


def _bundle() -> bytes:
    return json.dumps(json.loads((FIXTURE / "attestations-api.json").read_text())["attestations"][0]["bundle"]).encode()


def _subjects(export: str = EXPORT) -> dict[str, str]:
    return {n: hashlib.sha256((FIXTURE / n).read_bytes()).hexdigest()
            for n in ("manifest.json", "SHA256SUMS.txt", export)}


def _verify(**kw):
    from stemma_adapter.attest import verify_bundle

    args = dict(repository=REPO, ref=REF, subjects=_subjects())
    args.update(kw)
    bundle = args.pop("bundle", _bundle())
    return verify_bundle(bundle, **args)


# ---------------------------------------------------------------- policy (direct)

def test_correct_identity_and_digests_pass():
    _verify()
    _verify(subjects=_subjects("knowledge.json"))


@pytest.mark.parametrize("kw,match", [
    ({"repository": "evil-org/STEMMA"}, "verification failed"),
    ({"repository": "Er-Sajan-PLG/STEMMA-fork"}, "verification failed"),
    ({"workflow": "ci.yml"}, "verification failed"),
    ({"ref": "refs/tags/v3.0.0"}, "verification failed"),
    ({"ref": "refs/heads/main"}, "verification failed"),
])
def test_wrong_identity_fails(kw, match):
    with pytest.raises(ReleaseError, match=match):
        _verify(**kw)


def test_modified_digest_fails():
    subjects = _subjects()
    subjects[EXPORT] = hashlib.sha256(b"tampered").hexdigest()
    with pytest.raises(ReleaseError, match="does not cover"):
        _verify(subjects=subjects)


def test_digest_under_wrong_name_fails():
    subjects = _subjects()
    subjects["knowledge.json"] = subjects.pop(EXPORT)  # right bytes, wrong asset name
    with pytest.raises(ReleaseError, match="does not cover"):
        _verify(subjects=subjects)


def test_unattested_name_fails():
    subjects = _subjects()
    subjects["extra.json"] = subjects[EXPORT]
    with pytest.raises(ReleaseError, match="does not cover"):
        _verify(subjects=subjects)


@pytest.mark.parametrize("bundle", [b"", b"not json", b"{}", b'{"mediaType": "x"}',
                                    b"[1, 2]", None])
def test_malformed_bundle_fails(bundle):
    raw = bundle if bundle is not None else _bundle()[:-40]  # truncated real bundle
    with pytest.raises(ReleaseError, match="malformed|verification failed"):
        _verify(bundle=raw)


def test_tampered_signature_fails():
    doc = json.loads(_bundle())
    sig = doc["dsseEnvelope"]["signatures"][0]["sig"]
    doc["dsseEnvelope"]["signatures"][0]["sig"] = ("A" if sig[0] != "A" else "B") + sig[1:]
    with pytest.raises(ReleaseError):
        _verify(bundle=json.dumps(doc).encode())


def test_tampered_payload_fails():
    import base64

    doc = json.loads(_bundle())
    statement = json.loads(base64.b64decode(doc["dsseEnvelope"]["payload"]))
    statement["subject"][0]["digest"]["sha256"] = "0" * 64
    doc["dsseEnvelope"]["payload"] = base64.b64encode(json.dumps(statement).encode()).decode()
    with pytest.raises(ReleaseError, match="verification failed"):
        _verify(bundle=json.dumps(doc).encode())


def test_api_response_without_attestations_fails():
    from stemma_adapter.attest import select_bundle

    for body in (b'{"attestations": []}', b"{}", b'{"attestations": [{"no": "bundle"}]}'):
        with pytest.raises(ReleaseError):
            select_bundle(body, repository=REPO, ref=REF, subjects=_subjects())


# ---------------------------------------------------------------- end to end (fixture HTTPS host)

def test_from_release_verifies_attestation_by_default(github, client_tls, tmp_path):
    s = Stemma.from_release(REPO, TAG, cache_dir=tmp_path, file=EXPORT, ssl_context=client_tls)
    assert s.release_info["verification"] == "sigstore"
    entry = Path(s.release_info["cache_entry"])
    assert (entry / "attestation.json").is_file()
    assert any("/attestations/sha256:" in p for p in github.requests)


def test_attested_cache_is_reverified_offline(github, client_tls, tmp_path):
    kw = dict(cache_dir=tmp_path, file=EXPORT, ssl_context=client_tls)
    entry = Path(Stemma.from_release(REPO, TAG, **kw).release_info["cache_entry"])
    before = len(github.requests)
    assert Stemma.from_release(REPO, TAG, offline=True, **kw).release_info["verification"] == "sigstore"
    assert len(github.requests) == before
    # evidence is re-checked, not trusted: a broken attestation file fails offline
    (entry / "attestation.json").write_bytes(b'{"mediaType": "broken"}')
    with pytest.raises(ReleaseError, match="offline=True and no valid cached copy"):
        Stemma.from_release(REPO, TAG, offline=True, **kw)


def test_checksum_only_cache_does_not_satisfy_attested_load(github, client_tls, tmp_path):
    kw = dict(cache_dir=tmp_path, file=EXPORT, ssl_context=client_tls)
    Stemma.from_release(REPO, TAG, verify_attestation=False, **kw)
    with pytest.raises(ReleaseError, match="attestation.json missing"):
        Stemma.from_release(REPO, TAG, offline=True, **kw)
    s = Stemma.from_release(REPO, TAG, **kw)  # online: fetches and verifies the attestation
    assert s.release_info["verification"] == "sigstore"


def test_from_url_uses_caller_identity_not_mirror(server, client_tls, tmp_path, monkeypatch):
    """The fixture API answers for ANY repo with the rc1 bundle (attacker-hosted mirror).
    Only the caller's expected identity makes it pass or fail."""
    from stemma_adapter import release

    monkeypatch.setattr(release, "GITHUB_API", server.base)
    url = f"{server.base}/mirror/manifest.json"
    s = Stemma.from_url(url, cache_dir=tmp_path / "a", file=EXPORT, expected_repository=REPO,
                        expected_ref=REF, ssl_context=client_tls)
    assert s.release_info["verification"] == "sigstore"
    with pytest.raises(ReleaseError, match="no attestation verified"):
        Stemma.from_url(url, cache_dir=tmp_path / "b", file=EXPORT, expected_repository="evil-org/STEMMA",
                        expected_ref=REF, ssl_context=client_tls)
    assert not list((tmp_path / "b").rglob("*.json"))  # nothing cached on failure


def test_tampered_export_with_matching_sums_fails_attestation(github, client_tls, tmp_path):
    """A host that swaps the export AND rewrites SHA256SUMS + manifest passes checksum-only
    mode but is caught by the attestation (this is why verification is on by default)."""
    data = json.loads(github.files[EXPORT])
    entity = data["entities"][0]
    key = "definition" if isinstance(entity.get("definition"), str) else "label"
    entity[key] = str(entity[key]) + " (edited by a hostile mirror)"
    raw = (json.dumps(data, indent=2, ensure_ascii=False) + "\n").encode()
    old = hashlib.sha256(github.files[EXPORT]).hexdigest()
    new = hashlib.sha256(raw).hexdigest()
    github.files[EXPORT] = raw
    github.files["SHA256SUMS.txt"] = github.files["SHA256SUMS.txt"].replace(old.encode(), new.encode())
    manifest = json.loads(github.files["manifest.json"])
    manifest["files"][EXPORT].update(sha256=new, bytes=len(raw))
    github.files["manifest.json"] = (json.dumps(manifest, indent=2) + "\n").encode()
    github.replay_any_digest = True  # attacker replays the genuine rc1 attestation
    kw = dict(file=EXPORT, ssl_context=client_tls)
    with pytest.raises(ReleaseError, match="no attestation verified: attestation does not cover"):
        Stemma.from_release(REPO, TAG, cache_dir=tmp_path / "a", **kw)
    assert not list((tmp_path / "a").rglob("*.json"))
    # checksum-only cannot tell (documented): it loads the swapped file
    s = Stemma.from_release(REPO, TAG, cache_dir=tmp_path / "b", verify_attestation=False, **kw)
    assert s.release_info["sha256"] == new
