#!/usr/bin/env python3
"""H1: canonical entity provenance agents are checked, and drafted_by is representable.

- concept.schema.json accepts provenance.drafted_by (llm:/process:) so a
  machine-drafted, human-written entity can be canonical (schema 1.3.0);
- validate.check_entity_agents: writer/reviewer/drafted_by resolve in the agent
  registry; reviewer is human; drafted_by is a machine agent.
"""
from __future__ import annotations

import copy
import json
import pathlib
import sys

import pytest
import yaml
from jsonschema import Draft202012Validator

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import validate  # noqa: E402

SCHEMA = Draft202012Validator(json.loads((ROOT / "schema/concept.schema.json").read_text()))
AGENTS = validate.load_agent_registry()


def _metre() -> dict:
    path = next((ROOT / "content").rglob("metre.md"))
    return yaml.safe_load(path.read_text(encoding="utf-8").split("---")[1])


def _agent_errors(entity: dict) -> list[str]:
    errors: list[str] = []
    validate.check_entity_agents({**entity, "_file": "t.md"}, AGENTS, errors)
    return errors


def test_corpus_entity_agents_resolve():
    for path in (ROOT / "content").rglob("*.md"):
        fm = yaml.safe_load(path.read_text(encoding="utf-8").split("---")[1])
        assert _agent_errors(fm) == [], path


@pytest.mark.parametrize("drafted_by", ["llm:antigravity-001", "process:deterministic-draft.v1"])
def test_machine_drafted_human_written_entity_is_valid(drafted_by):
    e = _metre()
    e["provenance"].update(writer="human:curator.001", drafted_by=drafted_by, ai_drafted=True)
    assert [x.message for x in SCHEMA.iter_errors(e)] == []
    assert _agent_errors(e) == []


def test_schema_rejects_human_drafted_by():
    e = _metre()
    e["provenance"]["drafted_by"] = "human:curator.001"
    assert list(SCHEMA.iter_errors(e))


@pytest.mark.parametrize("field,value,needle", [
    ("writer", "human:made-up.999", "not in schema/agent-registry.yaml"),
    ("reviewer", "human:made-up.999", "not in schema/agent-registry.yaml"),
    ("reviewer", "llm:coding-agent.001", "reviewer must be a human"),
    ("drafted_by", "human:curator.001", "drafted_by must be an llm:/process:"),
    ("drafted_by", "llm:unregistered.9", "not in schema/agent-registry.yaml"),
])
def test_entity_agent_violations(field, value, needle):
    e = copy.deepcopy(_metre())
    e["provenance"][field] = value
    errs = _agent_errors(e)
    assert any(needle in x for x in errs), errs


def test_reviewer_stays_optional_on_drafts():
    """reviewer is checked only when present; drafts need none (kilogram/second today)."""
    drafts = []
    for path in (ROOT / "content").rglob("*.md"):
        fm = yaml.safe_load(path.read_text(encoding="utf-8").split("---")[1])
        if fm.get("status") == "draft":
            drafts.append(path.stem)
            assert not (fm.get("provenance") or {}).get("reviewer"), path
            assert [x.message for x in SCHEMA.iter_errors(fm)] == [], path
            assert _agent_errors(fm) == [], path
            errors: list[str] = []
            validate.validate_entity({**fm, "_file": str(path)}, errors, filename_slug=path.stem)
            assert errors == [], errors
    assert drafts, "corpus should contain at least one draft to exercise this"
    # a fresh machine draft with no reviewer at all is also fine for the agent check
    e = _metre()
    e["status"] = "draft"
    e["provenance"].pop("reviewer", None)
    e["provenance"].pop("reviewed_at", None)
    assert _agent_errors(e) == []
