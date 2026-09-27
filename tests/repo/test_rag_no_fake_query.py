#!/usr/bin/env python3
"""H5 residue: scripts/rag.py must not rank REAL vectors against a hash query.

Before: if sentence-transformers could not load, get_embedding_for_query
silently returned a hash vector and vector_search returned confident noise.
Placeholder stores (embed.py --placeholder) still use the hash, flagged.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import rag  # noqa: E402

HAS_ST = importlib.util.find_spec("sentence_transformers") is not None


def _store(placeholder: bool):
    row = {"entity_id": "stemma:phys.metre", "dimensions": 8, "vector": [0.1] * 8,
           "model": "stemma:placeholder-hash" if placeholder else "sentence-transformers/all-MiniLM-L6-v2"}
    if placeholder:
        row["placeholder"] = True
    return [row]


@pytest.mark.skipif(HAS_ST, reason="real model available; the refusal path is not reachable")
def test_real_store_without_model_is_refused(monkeypatch):
    monkeypatch.setattr(rag, "load_embeddings", lambda *a, **k: _store(False))
    with pytest.raises(RuntimeError, match="refusing to fake"):
        rag.vector_search("metre", top_k=1)


def test_placeholder_store_uses_flagged_hash_query(monkeypatch):
    monkeypatch.setattr(rag, "load_embeddings", lambda *a, **k: _store(True))
    monkeypatch.setattr(rag, "load_export", lambda *a, **k: {"entities": [{"id": "stemma:phys.metre", "name": "Metre"}]})
    results = rag.vector_search("metre", top_k=1)
    assert results and results[0].get("placeholder") is True
