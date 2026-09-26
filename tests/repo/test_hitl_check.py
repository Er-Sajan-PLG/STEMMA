#!/usr/bin/env python3
"""H1: scripts/hitl_check.py must fail closed.

Previously any writer starting with ``human:`` passed (no registry lookup), and
ANY candidate_edited event containing ``human:`` satisfied EVERY entity (a
missing per-entity edit was only a verbose warning).
"""
from __future__ import annotations

import json
import pathlib
import sys

import pytest
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import hitl_check as H  # noqa: E402
import review_entity as R  # noqa: E402

HUMAN = "human:curator.001"


@pytest.fixture
def tree(tmp_path, monkeypatch):
    wf = tmp_path / "workflow"
    for d in ("audit", "candidates/doc1", "proposals"):
        (wf / d).mkdir(parents=True)
    (tmp_path / "content").mkdir()
    monkeypatch.setattr(H, "ROOT", tmp_path)
    monkeypatch.setattr(H, "WORKFLOW", wf)
    monkeypatch.setattr(H, "AUDIT", wf / "audit" / "audit.jsonl")
    monkeypatch.setattr(H, "CANDIDATES", wf / "candidates")
    monkeypatch.setattr(H, "PROPOSALS", wf / "proposals")
    monkeypatch.setattr(H, "CONTENT", tmp_path / "content")
    agents = tmp_path / "schema" / "agent-registry.yaml"
    agents.parent.mkdir()
    agents.write_text(yaml.safe_dump({"version": "0.2", "agents": [
        {"id": HUMAN, "class": "human", "status": "active"},
        {"id": "human:retired.001", "class": "human", "status": "retired"},
        {"id": "human:institution.x", "class": "human", "status": "active", "type": "institution"},
        {"id": "process:deterministic-draft.v1", "class": "process", "status": "active"},
    ]}))
    monkeypatch.setattr(H, "AGENTS", agents)
    return wf


def _candidate(wf, slug, writer):
    (wf / "candidates" / "doc1" / f"{slug}.md").write_text(
        f"---\nid: stemma:phys.{slug}\nprovenance:\n  writer: {writer}\n---\nbody\n")


def _edit(wf, slug, writer):
    entry = {"event": "candidate_edited", "doc_id": "doc1",
             "detail": {"candidate_id": "c1", "human_edited": True, "writer": writer,
                        "markdown_path": f"candidates/doc1/{slug}.md"}}
    with (wf / "audit" / "audit.jsonl").open("a") as f:
        f.write(json.dumps(entry) + "\n")


def test_registered_humans_excludes_retired_institution_and_machines(tree):
    assert H.registered_humans() == {HUMAN}


def test_registry_unreadable_fails_closed(tree, monkeypatch):
    monkeypatch.setattr(H, "AGENTS", tree / "missing.yaml")
    _candidate(tree, "metre", HUMAN)
    _edit(tree, "metre", HUMAN)
    ok, v = H.check_entity("stemma:phys.metre")
    assert not ok


def test_properly_edited_entity_passes(tree):
    _candidate(tree, "metre", HUMAN)
    _edit(tree, "metre", HUMAN)
    ok, v = H.check_entity("stemma:phys.metre")
    assert ok, v


@pytest.mark.parametrize("writer", ["human:made-up.999", "human:retired.001",
                                    "human:institution.x", "process:deterministic-draft.v1"])
def test_unregistered_or_non_individual_writer_fails(tree, writer):
    _candidate(tree, "metre", writer)
    _edit(tree, "metre", HUMAN)
    ok, v = H.check_entity("stemma:phys.metre")
    assert not ok and any("provenance.writer" in x for x in v)


def test_edit_of_another_entity_is_not_evidence(tree):
    _candidate(tree, "metre", HUMAN)
    _candidate(tree, "kilogram", HUMAN)
    _edit(tree, "kilogram", HUMAN)          # only kilogram was edited
    ok, v = H.check_entity("stemma:phys.metre")
    assert not ok and any("metre.md" in x for x in v)


def test_edit_by_unregistered_human_is_not_evidence(tree):
    _candidate(tree, "metre", HUMAN)
    _edit(tree, "metre", "human:made-up.999")
    ok, v = H.check_entity("stemma:phys.metre")
    assert not ok


def test_substring_slug_does_not_match(tree):
    """'metre' must not be satisfied by an edit of 'centimetre.md'."""
    _candidate(tree, "metre", HUMAN)
    _edit(tree, "centimetre", HUMAN)
    ok, _ = H.check_entity("stemma:phys.metre")
    assert not ok


def test_similar_slug_file_is_not_checked_as_this_entity(tree):
    """A machine-written centimetre.md must not be read as metre's file."""
    _candidate(tree, "centimetre", "process:deterministic-draft.v1")
    ok, _ = H.check_entity("stemma:phys.metre")
    assert ok  # metre has no file of its own yet -> not ready, not a violation


def test_check_workflow_counts_only_registered_humans(tree, capsys, monkeypatch):
    _candidate(tree, "metre", HUMAN)
    _edit(tree, "metre", "human:made-up.999")
    monkeypatch.setattr(sys, "argv", ["hitl_check.py", "--check-workflow"])
    assert H.main() == 1
    _edit(tree, "metre", HUMAN)
    assert H.main() == 0


def test_review_entity_registered_human_fails_closed(tmp_path):
    # Unreadable registry under `root` -> nobody verifies (was: any human:* passed).
    assert R._registered_human(HUMAN, tmp_path) is False
    assert R._registered_human(HUMAN, ROOT) is True
    assert R._registered_human("human:institution.wikidata-community", ROOT) is False
    assert R._registered_human("human:made-up.999", ROOT) is False
