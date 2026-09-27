#!/usr/bin/env python3
"""Distribution item 3: the release bundle is the published file contract.

Built into a temp dir (never the repo). Asserts contents, manifest fields,
checksums, determinism, loadability, and the hard guards (no embeddings /
placeholder vectors, no stale consumer bundles, tamper detection).
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "adapters" / "python"))

import build_release_bundle as B  # noqa: E402
from stemma_adapter.loader import load_export  # noqa: E402

CONSUMERS = ("general", "learninghub", "professor-j", "stemma-explorer")
EPOCH = "1790000000"


@pytest.fixture
def bundle(tmp_path, monkeypatch):
    monkeypatch.setenv("SOURCE_DATE_EPOCH", EPOCH)
    return B.build(tmp_path / "out", release_tag="v0.0.0-test")


def _manifest(bundle):
    return json.loads((bundle / "manifest.json").read_text())


def test_bundle_contents(bundle):
    names = {p.name for p in bundle.iterdir()}
    expected = {"knowledge.json", "knowledge.hash.json", "connections.canonical.json", "knowledge.jsonld",
                "stemma-shapes.ttl", "SHA256SUMS.txt", "manifest.json"} | {f"knowledge.{c}.json" for c in CONSUMERS}
    assert names == expected
    assert not any("embedding" in n or "vector" in n for n in names)


def test_manifest_fields(bundle):
    m = _manifest(bundle)
    base = json.loads((ROOT / "exports/knowledge.json").read_text())
    assert m["export_version"] == base["export_version"]
    assert m["schema_version"] == base["schema_version"]
    assert m["content_hash"] == base["content_hash"]
    assert m["license"] == "CC-BY-4.0" and m["license_url"].startswith("https://creativecommons.org/licenses/by/4.0")
    assert m["generated_at"] == "2026-09-21T14:13:20Z"  # SOURCE_DATE_EPOCH, not the wall clock
    assert m["release_tag"] == "v0.0.0-test"
    assert m["release_status"].startswith("PENDING-PUBLICATION")  # no identifier-base decision yet
    listed = dict(line.split("  ")[::-1] for line in (bundle / "SHA256SUMS.txt").read_text().splitlines())
    assert set(m["files"]) == set(listed)
    for name, meta in m["files"].items():
        assert meta["sha256"] == hashlib.sha256((bundle / name).read_bytes()).hexdigest() == listed[name]


def test_hash_pointer_matches_knowledge_json(bundle):
    ptr = json.loads((bundle / "knowledge.hash.json").read_text())
    assert ptr["sha256"] == hashlib.sha256((bundle / "knowledge.json").read_bytes()).hexdigest()
    assert ptr["content_hash"] == _manifest(bundle)["content_hash"]


def test_every_export_kind_loads_with_the_sdk(bundle):
    kinds = {n: meta["kind"] for n, meta in _manifest(bundle)["files"].items()}
    exports = [n for n, k in kinds.items() if k == "export"]
    assert set(exports) == {"knowledge.json"} | {f"knowledge.{c}.json" for c in CONSUMERS}
    assert kinds["connections.canonical.json"] == "connections-view"
    # the name `knowledge.*.json` is reserved for loadable exports (+ the hash pointer)
    assert {n for n in kinds if n.startswith("knowledge.") and n.endswith(".json")} == set(exports) | {"knowledge.hash.json"}
    for name in exports:
        load_export(bundle / name)  # raises ExportError if not a valid export


def test_build_is_deterministic(tmp_path, monkeypatch):
    monkeypatch.setenv("SOURCE_DATE_EPOCH", EPOCH)
    a = B.build(tmp_path / "a", release_tag="v1")
    b = B.build(tmp_path / "b", release_tag="v1")
    assert a.name == b.name
    for f in a.iterdir():
        assert f.read_bytes() == (b / f.name).read_bytes(), f.name


def test_verify_detects_tampering_and_smuggled_files(bundle):
    assert B.verify(bundle) == 0
    (bundle / "embeddings.jsonl").write_text("{}\n")
    assert B.verify(bundle) == 1
    (bundle / "embeddings.jsonl").unlink()
    p = bundle / "knowledge.learninghub.json"
    p.write_text(p.read_text().replace('"canonical"', '"draft"', 1))
    assert B.verify(bundle) == 1


def _fake_root(tmp_path, monkeypatch):
    (tmp_path / "exports" / "consumers" / "x").mkdir(parents=True)
    (tmp_path / "exports" / "knowledge.json").write_text(json.dumps({"export_version": "2.2.0", "schema_version": "1.3.0"}))
    monkeypatch.setattr(B, "ROOT", tmp_path)
    return tmp_path


def test_guard_refuses_embeddings_by_name(tmp_path, monkeypatch):
    _fake_root(tmp_path, monkeypatch)
    with pytest.raises(B.BundleError, match="embeddings"):
        B.guard_payload("exports/embeddings.jsonl", "embeddings.jsonl")
    with pytest.raises(B.BundleError):
        B.guard_payload("exports/vector_store/meta.json", "meta.json")


def test_guard_refuses_placeholder_vectors(tmp_path, monkeypatch):
    root = _fake_root(tmp_path, monkeypatch)
    (root / "exports" / "sneaky.json").write_text(json.dumps({"model": "stemma:placeholder-hash"}))
    with pytest.raises(B.BundleError, match="placeholder"):
        B.guard_payload("exports/sneaky.json", "sneaky.json")


def test_guard_refuses_stale_consumer_bundle(tmp_path, monkeypatch):
    root = _fake_root(tmp_path, monkeypatch)
    (root / "exports/consumers/x/knowledge.x.json").write_text(json.dumps({"export_version": "2.1.0", "schema_version": "1.3.0"}))
    with pytest.raises(B.BundleError, match="stale consumer bundle"):
        B.guard_payload("exports/consumers/x/knowledge.x.json", "knowledge.x.json")


def test_export_like_name_for_non_export_is_refused(tmp_path, monkeypatch):
    monkeypatch.setenv("SOURCE_DATE_EPOCH", EPOCH)
    bad = [(s, "knowledge.canonical.json" if d == "connections.canonical.json" else d) for s, d in B.STATIC_PAYLOAD]
    monkeypatch.setattr(B, "STATIC_PAYLOAD", bad)
    monkeypatch.setattr(B, "file_kind", lambda n, _k=B.file_kind: "connections-view" if n == "knowledge.canonical.json" else _k(n))
    with pytest.raises(B.BundleError, match="named like an export"):
        B.build(tmp_path, release_tag="v0.0.0-test")


def test_release_workflow_never_publishes_unsigned_finals():
    """rc = CI-attested pre-release; final = draft until the owner attaches SHA256SUMS.sig.
    The owner GPG key must never reach Actions."""
    wf = ROOT / ".github" / "workflows"
    release = (wf / "release.yml").read_text(encoding="utf-8")
    assert 'flag="--draft"' in release and 'flag="--prerelease"' in release
    assert "--draft=false" not in release  # publishing a final is the owner's manual step
    for path in wf.glob("*.y*ml"):
        text = path.read_text(encoding="utf-8").lower()
        for needle in ("gpg --import", "gpg_private", "gpg_key", "gpg_passphrase", "sign_release_bundle.py"):
            if needle == "sign_release_bundle.py" and path.name == "release.yml":
                # only allowed as an instruction in comments, never executed
                assert all(l.lstrip().startswith("#") for l in text.splitlines() if needle in l), path
                continue
            assert needle not in text, f"{path.name}: {needle}"
