#!/usr/bin/env python3
"""The published-release signature auditor (scripts/audit_release_signature.py).

The gap this guards: `release.yml` can only create finals as drafts, so the
remaining steps — sign locally, upload SHA256SUMS.sig, publish — are performed by
a human, and nothing verified the end state. On 2026-10-01 v3.0.0 was published
~80s before its signature was uploaded.

These tests stub GitHub state (no network, no `gh` needed) and assert the
auditor's *decision*, including the exact lapse it was written to catch.
"""
from __future__ import annotations

import importlib.util
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]

_spec = importlib.util.spec_from_file_location(
    "audit_release_signature", ROOT / "scripts" / "audit_release_signature.py")
aud = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(aud)

FULL = ["knowledge.json", "knowledge.jsonld", "manifest.json", "SHA256SUMS.txt"]


def _release(tag, *, draft, prerelease, assets):
    return {"tagName": tag, "isDraft": draft, "isPrerelease": prerelease,
            "publishedAt": None if draft else "2026-10-01T04:20:01Z",
            "assets": [{"name": n} for n in assets]}


def _audit(monkeypatch, rel):
    monkeypatch.setattr(aud, "_view", lambda tag, _r=rel: _r)
    return aud.audit(rel["tagName"])


def test_published_final_without_signature_fails(monkeypatch):
    """The exact v3.0.0 lapse: public, marked final, no SHA256SUMS.sig."""
    r = _audit(monkeypatch, _release("v3.0.0", draft=False, prerelease=False, assets=FULL))
    assert not r["ok"]
    assert any("SHA256SUMS.sig" in f for f in r["findings"])
    assert r["kind"] == "final" and r["published"] is True


def test_published_final_with_signature_passes(monkeypatch):
    r = _audit(monkeypatch, _release("v3.0.0", draft=False, prerelease=False,
                                     assets=FULL + ["SHA256SUMS.sig"]))
    assert r["ok"], r["findings"]
    assert r["has_owner_signature"] is True


def test_draft_final_passes_without_signature(monkeypatch):
    """A draft is not a public claim — the owner has not published it yet."""
    r = _audit(monkeypatch, _release("v3.0.0", draft=True, prerelease=False,
                                     assets=["SHA256SUMS.txt"]))
    assert r["ok"], r["findings"]
    assert r["kind"] == "draft" and r["published"] is False


def test_prerelease_without_signature_passes_and_is_noted(monkeypatch):
    """rcs are CI-attested only by design (docs/keys/README.md)."""
    r = _audit(monkeypatch, _release("v3.0.0-rc4", draft=False, prerelease=True,
                                     assets=FULL))
    assert r["ok"], r["findings"]
    assert r["kind"] == "pre-release"
    assert any("layer 2" in n for n in r["notes"])
    assert not r["has_owner_signature"]


def test_prerelease_is_detected_by_suffix_even_if_github_says_otherwise(monkeypatch):
    """An -rcN tag must not be treated as a final even if isPrerelease is false."""
    r = _audit(monkeypatch, _release("v3.0.0-rc9", draft=False, prerelease=False,
                                     assets=FULL))
    assert r["ok"], "an -rcN suffix means candidate, not final"


def test_published_final_missing_manifest_fails(monkeypatch):
    r = _audit(monkeypatch, _release("v3.0.0", draft=False, prerelease=False,
                                     assets=["knowledge.json", "SHA256SUMS.txt",
                                             "SHA256SUMS.sig"]))
    assert not r["ok"]
    assert any("manifest.json" in f for f in r["findings"])


def test_auditor_never_writes_or_signs():
    """It must stay read-only: no signing/uploading/editing commands anywhere."""
    src = (ROOT / "scripts" / "audit_release_signature.py").read_text(encoding="utf-8")
    for forbidden in ("--detach-sign", "release upload", "release edit",
                      "release delete", "gpg --import"):
        assert forbidden not in src, f"auditor must not use {forbidden!r}"
    # The only gh subcommand consulted is the read-only 'release view'/'release list'.
    assert "release view" in src
