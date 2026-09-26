#!/usr/bin/env python3
"""H1 regression tests: the webapp must never forge human provenance.

Before the fix, machine-drafted candidates were labelled ``human:curator.001``,
any client could flip ``human_edited`` to mint a human audit event, the staged
reviewer was free text from the request body, and markdown defaulted a missing
writer to a human id. The rules now enforced:

* machine output carries a registered machine identity (process:/llm:);
* the human identity is server configuration (STEMMA_REVIEWER_ID), verified as
  an active individual human in schema/agent-registry.yaml; unset => refuse;
* a request can neither set authorship fields nor claim a different reviewer;
* a human edit records the operator as writer and keeps the machine origin
  as drafted_by (origin preserved, never rewritten).
"""
from __future__ import annotations

import json
import pathlib
import sys
import threading
import urllib.error
import urllib.request
import uuid

import pytest
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "webapp"))

import core  # noqa: E402
import evolvable_template  # noqa: E402
import server as S  # noqa: E402
from core import DETERMINISTIC_DRAFT_WRITER, REVIEWER_ENV, WebappError, Workflow  # noqa: E402

OPERATOR = "human:curator.001"
MACHINE_DRAFT = {
    "id": "stemma:phys.test-provenance", "type": "concept", "name": "Provenance test",
    "domain": "physics", "status": "draft", "definition": "A machine draft.",
    "same_dimensional_quantities": None,
    "provenance": {"ai_drafted": False, "writer": DETERMINISTIC_DRAFT_WRITER,
                   "source": "stemma:src.webapp-x"},
}


def _registry() -> dict[str, dict]:
    doc = yaml.safe_load((ROOT / "schema/agent-registry.yaml").read_text())
    return {e["id"]: e for e in doc["agents"]}


def _workflow_with_candidate(tmp_path: pathlib.Path, reviewer_id: str | None) -> tuple[Workflow, str, str]:
    wf = Workflow(tmp_path / "wf", reviewer_id=reviewer_id)
    doc = wf.accept_upload(original_name="x.txt", mime="text/plain", data=b"content")
    wf.extract_document(doc["id"])
    cid = uuid.uuid4().hex[:12]
    (wf.candidates / f"{doc['id']}.json").write_text(json.dumps({
        "doc_id": doc["id"], "generated_at": "",
        "candidates": [{"id": cid, "doc_id": doc["id"], "kind": "entity",
                        "proposal": json.loads(json.dumps(MACHINE_DRAFT)), "findings": []}],
    }), encoding="utf-8")
    return wf, doc["id"], cid


def _audit_edits(wf: Workflow) -> list[dict]:
    return [e for e in wf.read_audit() if e.get("event") == "candidate_edited"]


# --------------------------------------------------------------------------- #
# Machine identities are real, registered, and not human
# --------------------------------------------------------------------------- #
def test_machine_writers_are_registered_non_human():
    reg = _registry()
    for ident in (DETERMINISTIC_DRAFT_WRITER, "llm:antigravity-001"):
        assert ident in reg, f"{ident} must be registered in schema/agent-registry.yaml"
        assert reg[ident]["class"] != "human" and reg[ident]["status"] == "active"


def test_evolvable_template_never_labels_machine_output_human():
    src = (ROOT / "scripts/evolvable_template.py").read_text()
    assert '"human:curator.001"' not in src
    reg = evolvable_template.load_registry()
    ent = {"slug": "test-q", "id": "stemma:phys.test-q", "name": "Test Q"}
    md = evolvable_template.build_markdown(ent, reg)
    fm = yaml.safe_load(md.split("---")[1])
    assert fm["provenance"]["writer"] in (DETERMINISTIC_DRAFT_WRITER, "llm:antigravity-001")


# --------------------------------------------------------------------------- #
# Operator identity: server config, verified against the registry
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("ident,why", [
    ("human:nobody.999", "not registered"),
    ("llm:coding-agent.001", "not an individual human"),
    (DETERMINISTIC_DRAFT_WRITER, "not an individual human"),
])
def test_operator_must_be_registered_active_human(tmp_path, ident, why):
    with pytest.raises(WebappError, match=why):
        Workflow(tmp_path / "wf", reviewer_id=ident).operator_identity()


def test_operator_rejects_institution_and_inactive(tmp_path, monkeypatch):
    inst = next(i for i, e in _registry().items() if e.get("type") == "institution")
    with pytest.raises(WebappError, match="not an individual human"):
        Workflow(tmp_path / "wf", reviewer_id=inst).operator_identity()
    fake = tmp_path / "agent-registry.yaml"
    fake.write_text(yaml.safe_dump({"version": "0.2", "agents": [
        {"id": "human:retired.001", "class": "human", "status": "retired"}]}))
    monkeypatch.setattr(core, "AGENT_REGISTRY", fake)
    with pytest.raises(WebappError, match="not active"):
        Workflow(tmp_path / "wf", reviewer_id="human:retired.001").operator_identity()


def test_operator_read_from_env(tmp_path, monkeypatch):
    monkeypatch.setenv(REVIEWER_ENV, OPERATOR)
    assert Workflow(tmp_path / "wf").operator_identity() == OPERATOR
    monkeypatch.delenv(REVIEWER_ENV)
    with pytest.raises(WebappError, match=REVIEWER_ENV):
        Workflow(tmp_path / "wf").operator_identity()


# --------------------------------------------------------------------------- #
# Edits
# --------------------------------------------------------------------------- #
def test_human_edit_refused_without_configured_operator(tmp_path, monkeypatch):
    monkeypatch.delenv(REVIEWER_ENV, raising=False)
    wf, _doc, cid = _workflow_with_candidate(tmp_path, None)
    for kwargs in ({"human_edited": True}, {"edited_markdown": "---\nid: x\n---\n"}):
        with pytest.raises(WebappError, match=REVIEWER_ENV):
            wf.update_candidate(cid, proposal=dict(MACHINE_DRAFT), **kwargs)
    assert not any("human:" in json.dumps(e) for e in _audit_edits(wf))


def test_human_edit_records_operator_and_preserves_machine_origin(tmp_path):
    wf, _doc, cid = _workflow_with_candidate(tmp_path, OPERATOR)
    out = wf.update_candidate(cid, proposal=dict(MACHINE_DRAFT), human_edited=True,
                              edited_markdown="---\nid: stemma:phys.test-provenance\n---\n")
    prov = out["proposal"]["provenance"]
    assert prov["writer"] == OPERATOR and prov["edited_by"] == OPERATOR
    assert prov["drafted_by"] == DETERMINISTIC_DRAFT_WRITER
    assert prov["ai_drafted"] is False
    edits = _audit_edits(wf)
    assert edits[-1]["detail"]["writer"] == OPERATOR
    assert edits[-1]["detail"]["attested_via"] == REVIEWER_ENV
    # A second edit keeps the original machine origin, not the human.
    out = wf.update_candidate(cid, proposal=out["proposal"], human_edited=True)
    assert out["proposal"]["provenance"]["drafted_by"] == DETERMINISTIC_DRAFT_WRITER


def test_client_cannot_set_authorship_fields(tmp_path):
    wf, _doc, cid = _workflow_with_candidate(tmp_path, None)
    forged = json.loads(json.dumps(MACHINE_DRAFT))
    forged["provenance"].update(writer=OPERATOR, edited_by=OPERATOR, drafted_by=OPERATOR, ai_drafted=True)
    out = wf.update_candidate(cid, proposal=forged)  # not a human edit
    prov = out["proposal"]["provenance"]
    assert prov["writer"] == DETERMINISTIC_DRAFT_WRITER
    assert prov["ai_drafted"] is False
    assert "edited_by" not in prov and "drafted_by" not in prov
    assert not any("human:" in json.dumps(e) for e in _audit_edits(wf))


def test_markdown_has_no_default_human_writer(tmp_path):
    wf = Workflow(tmp_path / "wf")
    md = wf._proposal_to_markdown({"id": "stemma:phys.x", "name": "X", "provenance": {"source": "s"}})
    assert "human:" not in md


# --------------------------------------------------------------------------- #
# Staging
# --------------------------------------------------------------------------- #
def test_stage_uses_operator_and_rejects_claimed_reviewer(tmp_path):
    wf, _doc, cid = _workflow_with_candidate(tmp_path, OPERATOR)
    with pytest.raises(WebappError, match="claimed"):
        wf.stage_candidate(cid, reviewer="human:reviewer.physics-001")
    rec = wf.stage_candidate(cid, note="checked")["record"]
    assert rec["human_review"]["reviewer"] == OPERATOR
    assert rec["human_review"]["attested_via"] == REVIEWER_ENV


def test_stage_refused_without_operator(tmp_path, monkeypatch):
    monkeypatch.delenv(REVIEWER_ENV, raising=False)
    wf, _doc, cid = _workflow_with_candidate(tmp_path, None)
    with pytest.raises(WebappError, match=REVIEWER_ENV):
        wf.stage_candidate(cid, reviewer=OPERATOR)  # a body claim alone is not enough


# --------------------------------------------------------------------------- #
# Live server: deterministic draft + stage over HTTP
# --------------------------------------------------------------------------- #
class _Live:
    def __init__(self, wf: Workflow):
        self.srv = S.serve(host="127.0.0.1", port=0, workflow=wf)
        self.port = self.srv.server_address[1]
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()

    def call(self, method, path, body=None):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(f"http://127.0.0.1:{self.port}{path}", data=data,
                                     headers={"Content-Type": "application/json"}, method=method)
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.status, json.loads(r.read().decode() or "null")
        except urllib.error.HTTPError as exc:
            return exc.code, json.loads(exc.read().decode() or "null")

    def close(self):
        self.srv.shutdown()
        self.srv.server_close()


def test_live_deterministic_draft_is_machine_attributed_and_stage_needs_operator(tmp_path, monkeypatch):
    monkeypatch.delenv(REVIEWER_ENV, raising=False)
    wf = Workflow(tmp_path / "wf")
    doc = wf.accept_upload(original_name="u.txt", mime="text/plain",
                           data=b"Length: the metre\nMass: the kilogram\n")
    wf.extract_document(doc["id"])
    live = _Live(wf)
    try:
        status, payload = live.call("POST", f"/api/documents/{doc['id']}/deterministic-draft", {})
        assert status in (200, 201), payload
        stored = json.loads((wf.candidates / f"{doc['id']}.json").read_text())["candidates"]
        assert stored, "fixture text should produce deterministic candidates"
        for cand in stored:
            prov = cand["proposal"]["provenance"]
            assert prov["writer"] == DETERMINISTIC_DRAFT_WRITER and prov["ai_drafted"] is False
        for md in (wf.candidates / doc["id"]).glob("*.md"):
            assert "human:" not in md.read_text(), md
        cid = stored[0]["id"]
        status, payload = live.call("POST", f"/api/candidates/{cid}/stage",
                                    {"reviewer": OPERATOR, "note": "spoof"})
        assert status == 400 and REVIEWER_ENV in json.dumps(payload)
    finally:
        live.close()
