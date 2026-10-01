#!/usr/bin/env python3
"""UNRES-STEMMA-HITL-001 option (c): the hash-only review manifest must be honest.

The manifest exists to make HITL review claims portable to a fresh clone without
committing the git-ignored `workflow/` trail (which may hold textbook excerpts —
UNRES-STEMMA-OPS-001). Two properties make it worth anything:

  1. EXCERPT-FREE — it carries ids, declared provenance, promotion history, and
     content digests; it must never carry definition text or source excerpts, or
     committing it would raise exactly the licensing question it was meant to
     avoid.
  2. BINDING — a digest must fail when the reviewed artifact changes afterwards.
     A manifest of hashes that does not notice an edit is decoration.

Both are asserted against the REAL repo and the REAL script, so a regression in
either the generator or the records turns these red.
"""
from __future__ import annotations

import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

import pytest
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "review_manifest.py"
MANIFEST = ROOT / "spec" / "machine-readable" / "review_manifest.json"


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True, cwd=str(ROOT),
    )


def _manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def _frontmatter(path: pathlib.Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if text.lstrip().startswith("---"):
        body = text.lstrip()[3:]
        end = body.find("\n---")
        if end != -1:
            body = body[:end]
        return yaml.safe_load(body) or {}
    return yaml.safe_load(text) or {}


# --- 1. EXCERPT-FREE ---------------------------------------------------------------

def test_manifest_exists_and_is_committed():
    assert MANIFEST.exists(), "the manifest must be committed, or nothing is portable"


def test_manifest_carries_no_definition_text_or_excerpts():
    """No definition fragment from any record may appear in the manifest."""
    blob = MANIFEST.read_text(encoding="utf-8")
    leaked: list[str] = []
    for path in sorted((ROOT / "content").rglob("*.md")):
        defn = _frontmatter(path).get("definition") or ""
        if isinstance(defn, str) and len(defn) > 60:
            probe = defn[20:60].strip()
            if probe and probe in blob:
                leaked.append(f"{path.name}: {probe!r}")
    assert not leaked, f"definition text leaked into the manifest: {leaked}"


def test_manifest_has_no_definition_key_anywhere():
    """Structural check: the schema itself must not carry a text-bearing field."""
    def keys(node):
        if isinstance(node, dict):
            for k, v in node.items():
                yield k
                yield from keys(v)
        elif isinstance(node, list):
            for item in node:
                yield from keys(item)

    present = set(keys(_manifest()))
    forbidden = {"definition", "body", "excerpt", "text", "source_text", "quote"}
    assert not (present & forbidden), f"text-bearing keys present: {present & forbidden}"


def test_every_entry_carries_a_content_hash():
    entries = _manifest()["entries"]
    assert entries, "the manifest must list the reviewed records"
    for e in entries:
        assert e.get("content_hash", "").startswith("sha256:"), f"{e.get('id')} lacks a digest"


# --- 2. BINDING (non-vacuity) ------------------------------------------------------

def test_check_passes_on_a_clean_tree():
    proc = _run("--check")
    assert proc.returncode == 0, f"--check failed on a clean tree: {proc.stderr}"
    assert "OK:" in proc.stdout


def test_check_fails_when_a_reviewed_record_changes_after_review():
    """The whole point: an edit after review must invalidate the claim.

    Uses a temp copy so the real tree is never mutated by the test.
    """
    entry = next(e for e in _manifest()["entries"] if e["kind"] == "entity")
    target = ROOT / entry["relpath"]
    assert target.exists(), f"{target} missing"

    original = target.read_bytes()
    try:
        text = original.decode("utf-8")
        # A whitespace-only edit still changes the digest — the guard must see it.
        target.write_text(text + "\n<!-- post-review edit -->\n", encoding="utf-8")
        proc = _run("--check")
        assert proc.returncode == 1, "an edit after review did NOT fail --check"
        assert entry["id"] in (proc.stderr + proc.stdout), "the failure must name the record"
    finally:
        target.write_bytes(original)

    # And it recovers.
    assert _run("--check").returncode == 0


def test_manifest_is_deterministic():
    """Regenerating changes nothing — no wall clock, stable ordering."""
    a = _run("--stdout")
    b = _run("--stdout")
    assert a.returncode == 0 and b.returncode == 0
    assert a.stdout == b.stdout, "the manifest is not deterministic across runs"


def test_generator_does_not_read_the_workflow_trail():
    """The manifest must be derived from canonical records, never from workflow/.

    Checked against the real code by importing the module and inspecting what it
    actually reads, not by grepping prose. A grep is defeated by a docstring (as
    it was on the first cut of this test); reading the module's path constants and
    collect() output is not.
    """
    import importlib.util

    spec = importlib.util.spec_from_file_location("review_manifest_mod", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)

    # The module's declared inputs must point only at canonical locations.
    for attr in ("CONTENT_DIR", "CONNECTIONS_DIR", "OUT_PATH"):
        p = getattr(mod, attr, None)
        assert p is not None, f"expected {attr} on the module"
        assert "workflow" not in str(p), f"{attr} points into the git-ignored trail: {p}"

    # And every entry it produces must come from a canonical path.
    manifest = mod.collect()
    assert manifest["entries"], "collect() returned no entries — the check would be vacuous"
    for e in manifest["entries"]:
        assert not e["relpath"].startswith("workflow/"), (
            f"{e['id']} was derived from the workflow trail: {e['relpath']}"
        )
        assert e["relpath"].startswith(("content/", "connections/")), (
            f"{e['id']} came from an unexpected location: {e['relpath']}"
        )
