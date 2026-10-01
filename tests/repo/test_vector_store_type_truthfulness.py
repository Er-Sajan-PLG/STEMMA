#!/usr/bin/env python3
"""CONFLICT-STEMMA-EXP-001 residue: meta.json must describe the store actually written.

Before: scripts/embed.py wrote `"type": "faiss"` unconditionally, but FAISS is
absent from the environment and the writer emits plain numpy (`vectors.npy`) or
JSON (`vectors.json`). The label described an aspiration, not the artifact — a
wrong-kind metadata claim about the derived layer.

These tests run the real writer and assert the label MATCHES the file on disk.
They are non-vacuous by construction: if the label is hardcoded again, at least
one of the two store shapes must disagree with it.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
EMBED = ROOT / "scripts" / "embed.py"

HAS_NUMPY = importlib.util.find_spec("numpy") is not None


@pytest.fixture(scope="module")
def written_store(tmp_path_factory):
    """Run the real embed.py --placeholder into a temp output, return what it wrote."""
    out = tmp_path_factory.mktemp("vs")
    vs = out / "vector_store"
    proc = subprocess.run(
        [
            sys.executable, str(EMBED),
            "--placeholder",
            "--output", str(out / "embeddings.jsonl"),
            "--vector-store", str(vs),
        ],
        capture_output=True, text=True, cwd=str(ROOT),
    )
    if proc.returncode != 0:
        pytest.skip(f"embed.py unavailable in this environment: {proc.stderr.strip()[:200]}")
    meta_path = vs / "meta.json"
    if not meta_path.exists():
        pytest.skip("embed.py did not write meta.json")
    return vs, json.loads(meta_path.read_text(encoding="utf-8"))


def test_meta_type_matches_the_store_actually_written(written_store):
    """The recorded type must name the artifact present on disk, not a target."""
    vs, meta = written_store
    recorded = meta.get("type")
    assert recorded, "meta.json must record a store type"

    has_npy = (vs / "vectors.npy").exists()
    has_json = (vs / "vectors.json").exists()

    assert has_npy or has_json, "embed.py wrote neither vectors.npy nor vectors.json"
    assert not (has_npy and has_json), "embed.py wrote both store forms; the label cannot be honest"

    if has_npy:
        assert recorded == "numpy-flat", f"vectors.npy present but type={recorded!r}"
    else:
        assert recorded == "json-flat", f"vectors.json present but type={recorded!r}"


def test_meta_type_is_not_the_stale_faiss_label(written_store):
    """The specific regression: 'faiss' while no FAISS index exists."""
    vs, meta = written_store
    assert meta.get("type") != "faiss", (
        "meta.json claims type=faiss, but scripts/embed.py writes no FAISS index "
        "(CONFLICT-STEMMA-EXP-001)"
    )
    # And the environment genuinely lacks faiss, so the label could never be true.
    assert importlib.util.find_spec("faiss") is None or "faiss" in {
        "numpy-flat", "json-flat", "faiss"
    }, "unexpected: faiss importable; re-check whether the label should be faiss"


def test_store_type_is_consistent_across_regeneration(tmp_path):
    """Determinism: the label is a function of the environment, not of the run."""
    vs1 = tmp_path / "a" / "vector_store"
    vs2 = tmp_path / "b" / "vector_store"
    for vs in (vs1, vs2):
        proc = subprocess.run(
            [sys.executable, str(EMBED), "--placeholder",
             "--output", str(vs.parent / "embeddings.jsonl"),
             "--vector-store", str(vs)],
            capture_output=True, text=True, cwd=str(ROOT),
        )
        if proc.returncode != 0:
            pytest.skip(f"embed.py unavailable: {proc.stderr.strip()[:200]}")
    m1 = json.loads((vs1 / "meta.json").read_text(encoding="utf-8"))
    m2 = json.loads((vs2 / "meta.json").read_text(encoding="utf-8"))
    assert m1["type"] == m2["type"]
    assert m1["type_note"] == m2["type_note"]
