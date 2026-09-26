#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
import tempfile
import threading
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve()
PYTHON_ROOT = HERE.parents[1]
REPO_ROOT = HERE.parents[3]
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from stemma_adapter import ExportError, Stemma, load_export  # noqa: E402
from stemma_adapter.client import BadRequestError, NotFoundError  # noqa: E402
from stemma_adapter.policies import filter_connections  # noqa: E402
from stemma_adapter.server import serve  # noqa: E402


def expect_raises(exc_type: type[BaseException], func, *args, **kwargs) -> BaseException:
    try:
        func(*args, **kwargs)
    except exc_type as exc:  # type: ignore[misc]
        return exc
    raise AssertionError(f"expected {exc_type.__name__} to be raised")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def make_entity(
    entity_id: str,
    *,
    name: str | None = None,
    status: str = "draft",
    deprecated_by: str | None = None,
    external_ids: dict[str, Any] | None = None,
) -> dict[str, Any]:
    slug = entity_id.split(".", 1)[1]
    entity = {
        "id": entity_id,
        "type": "concept",
        "name": name or slug.replace("-", " ").title(),
        "domain": "testing",
        "status": status,
        "definition": f"Definition for {entity_id}.",
        "provenance": {"ai_drafted": False},
    }
    if deprecated_by is not None:
        entity["deprecated_by"] = deprecated_by
    if external_ids is not None:
        entity["external_ids"] = external_ids
    return entity


def make_connection(
    conn_id: str,
    source: str,
    relation: str,
    target: str,
    *,
    assertion_status: str = "active",
    review_status: str = "canonical",
    evidence_source: str | None = None,
) -> dict[str, Any]:
    connection = {
        "id": conn_id,
        "type": "connection",
        "source": source,
        "relation": relation,
        "target": target,
        "assertion": {
            "status": assertion_status,
            "type": "proposed",
            "review": {"status": review_status},
        },
        "provenance": {
            "asserted_by": {"type": "human", "id": "human:tester.001"},
            "generated_by": {"type": "human", "id": "human:tester.001"},
            "method": {"type": "manual"},
        },
    }
    if evidence_source is not None:
        connection["evidence"] = [
            {
                "type": "textbook",
                "source_ref": evidence_source,
                "description": "synthetic evidence",
            }
        ]
    return connection


SYNTHETIC_RELATION_REGISTRY = {
    "requires": {
        "family": "dependency",
        "transitive": False,
        "symmetric": False,
        "domain": ["concept"],
        "range": ["concept"],
        "status": "adopted",
    },
    "mathematically_requires": {
        "family": "dependency",
        "transitive": True,
        "symmetric": False,
        "domain": ["concept", "quantity"],
        "range": ["concept", "quantity"],
        "status": "adopted",
    },
    "depends_on": {
        "family": "dependency",
        "transitive": False,
        "symmetric": False,
        "domain": ["concept"],
        "range": ["concept"],
        "status": "adopted",
    },
    "logically_requires": {
        "family": "dependency",
        "transitive": True,
        "symmetric": False,
        "domain": ["concept"],
        "range": ["concept"],
        "status": "adopted",
    },
}
SYNTHETIC_VOCABULARIES = {
    "domains": ["testing"],
    "subdomains": {"testing": ["basic"]},
    "regimes": ["classical"],
    "scales": ["micro", "macro"],
}


def synthetic_export() -> dict[str, Any]:
    entities = [
        make_entity("stemma:test.root", name="Root"),
        make_entity("stemma:test.alpha", name="Alpha"),
        make_entity("stemma:test.beta", name="Beta"),
        make_entity("stemma:test.gamma", name="Gamma"),
        make_entity("stemma:test.velocity", name="Velocity"),
        make_entity(
            "stemma:test.alias-old",
            name="Alias Old",
            status="deprecated",
            deprecated_by="stemma:test.alias-mid",
        ),
        make_entity(
            "stemma:test.alias-mid",
            name="Alias Mid",
            status="superseded",
            deprecated_by="stemma:test.alias-new",
        ),
        make_entity("stemma:test.alias-new", name="Alias New", external_ids={"wd": "Q-test"}),
    ]
    sources = [
        {
            "id": "stemma:src.synthetic",
            "type": "textbook",
            "citation": "Synthetic source",
        }
    ]
    connections = [
        make_connection(
            "stemma:conn.000001",
            "stemma:test.root",
            "requires",
            "stemma:test.alpha",
            review_status="canonical",
            evidence_source="stemma:src.synthetic",
        ),
        make_connection(
            "stemma:conn.000002",
            "stemma:test.alpha",
            "mathematically_requires",
            "stemma:test.beta",
            review_status="canonical",
        ),
        make_connection(
            "stemma:conn.000003",
            "stemma:test.beta",
            "depends_on",
            "stemma:test.gamma",
            review_status="canonical",
        ),
        make_connection(
            "stemma:conn.000004",
            "stemma:test.gamma",
            "logically_requires",
            "stemma:test.root",
            review_status="canonical",
        ),
        make_connection(
            "stemma:conn.000005",
            "stemma:test.root",
            "logically_requires",
            "stemma:test.velocity",
            review_status="unreviewed",
        ),
        make_connection(
            "stemma:conn.000006",
            "stemma:test.root",
            "requires",
            "stemma:test.alias-old",
            assertion_status="superseded",
            review_status="canonical",
        ),
    ]
    return {
        "export_version": "2.2.0",
        "schema_version": "1.2.0",
        "content_hash": "sha256:" + ("0" * 64),
        "kernel_version": "3.0.0",
        "relation_registry_version": "1.0.0",
        "relation_registry": SYNTHETIC_RELATION_REGISTRY,
        "vocabularies": SYNTHETIC_VOCABULARIES,
        "source": "synthetic",
        "entity_count": len(entities),
        "connection_count": len(connections),
        "source_count": len(sources),
        "entities": entities,
        "connections": connections,
        "sources": sources,
    }


def http_json(url: str, *, etag: str | None = None) -> tuple[int, dict[str, str], Any]:
    request = urllib.request.Request(url)
    if etag is not None:
        request.add_header("If-None-Match", etag)
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            body = response.read().decode("utf-8")
            payload = json.loads(body) if body else None
            return response.status, dict(response.headers.items()), payload
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        payload = json.loads(body) if body else None
        return exc.code, dict(exc.headers.items()), payload


def _raw_export() -> dict[str, Any]:
    return json.loads((REPO_ROOT / "exports" / "knowledge.json").read_text(encoding="utf-8"))


def test_real_export() -> None:
    """The committed export must load and behave per contract.

    Expectations are derived from the export itself (not frozen corpus numbers),
    so the test stays meaningful as the knowledge base grows.
    """
    export_path = REPO_ROOT / "exports" / "knowledge.json"
    raw = _raw_export()
    export = load_export(export_path)
    if export["entity_count"] == 0:
        print("SKIP: test_real_export (0 entities in empty knowledge base)")
        return
    n_ent, n_conn, n_src = len(raw["entities"]), len(raw["connections"]), len(raw["sources"])
    assert (export["entity_count"], export["connection_count"], export["source_count"]) == (n_ent, n_conn, n_src)

    client = Stemma.from_file(str(export_path))
    assert (client.stats["entity_count"], client.stats["connection_count"], client.stats["source_count"]) == (
        n_ent, n_conn, n_src)
    assert len(client.entities_by_id) == n_ent
    assert len(client.all_connections) == n_conn
    assert len(client.sources_by_id) == n_src

    # Policy views agree with the producer's published per-policy exports.
    for policy in ("all", "reviewed", "canonical", "trusted"):
        filtered = filter_connections(client.all_connections, policy)
        exported = json.loads((REPO_ROOT / "exports" / f"knowledge.{policy}.json").read_text(encoding="utf-8"))
        assert exported["count"] == len(filtered)
        assert [conn["id"] for conn in filtered] == [conn["id"] for conn in exported["connections"]]
        assert len(client.connections(policy=policy)) == len(filtered)
    all_ids = {conn["id"] for conn in client.connections(policy="all")}
    canonical_ids = {conn["id"] for conn in client.connections(policy="canonical")}
    assert canonical_ids <= all_ids

    # External-id round trip for every entity that declares one.
    for entity in raw["entities"]:
        for scheme, ext in (entity.get("external_ids") or {}).items():
            assert client.by_external_id(scheme, ext)["id"] == entity["id"]

    # ADR-0045: relational vs valued claims are exposed through the right API.
    valued = [c for c in raw["connections"] if c.get("value") is not None]
    relational = [c for c in raw["connections"] if c.get("target") is not None]
    assert len(valued) + len(relational) == n_conn
    for conn in valued:
        got = {v["connection_id"]: v for v in client.values(conn["source"])}
        assert conn["id"] in got and got[conn["id"]]["value"]["amount"] == conn["value"]["amount"]
    for entity_id in client.entities_by_id:
        for edge in client.neighbors(entity_id, include_retired=True):
            assert edge["target"] is not None, "valued claims must not appear as graph edges"
        prereqs = {e["id"] for e in client.prerequisites(entity_id, policy="all", include_retired=True)}
        assert entity_id not in prereqs
        assert {e["id"] for e in client.prerequisites(entity_id, policy="canonical", include_retired=True)} <= prereqs

    # Search is deterministic and finds an entity by its own name.
    first = raw["entities"][0]
    token = first["name"].split()[0]
    results = client.search(token, domain=first["domain"])
    assert first["id"] in [e["id"] for e in results]
    assert results == client.search(token, domain=first["domain"])


def test_valued_claim_contract() -> None:
    """ADR-0045 value-slot: exactly one of target/value; value shape enforced."""
    export = synthetic_export()
    src = export["connections"][0]["source"]
    valued = copy.deepcopy(export["connections"][0])
    valued["id"] = "stemma:conn.999999"
    valued["target"] = None
    valued["value"] = {"amount": "299792458", "lowerBound": None, "upperBound": None,
                       "unit": "qudt:unit-MeterPerSecond"}
    export["connections"].append(valued)
    export["connection_count"] += 1
    load_export(export)
    client = Stemma.from_dict(export)
    vals = client.values(src, policy="all")
    assert [v["connection_id"] for v in vals] == ["stemma:conn.999999"]
    assert vals[0]["value"]["unit"] == "qudt:unit-MeterPerSecond"
    assert all(edge["connection_id"] != "stemma:conn.999999" for edge in client.neighbors(src))

    def rejects(mutate, needle: str) -> None:
        bad = copy.deepcopy(export)
        mutate(bad["connections"][-1])
        try:
            load_export(bad)
        except ExportError as exc:
            assert needle in str(exc), str(exc)
        else:
            raise AssertionError(f"expected ExportError containing {needle!r}")

    rejects(lambda c: c.update(target=c["source"]), "exactly one of")  # both
    rejects(lambda c: c.update(value=None), "exactly one of")  # neither
    rejects(lambda c: c["value"].update(amount=42), "decimal string")
    rejects(lambda c: c["value"].update(amount="4e"), "decimal string")
    rejects(lambda c: c["value"].update(currency="USD"), "unknown member")
    rejects(lambda c: c["value"].update(upperBound="abc"), "upperBound")
    print("PASS: test_valued_claim_contract")


def test_synthetic_export() -> None:
    export = synthetic_export()
    load_export(export)
    client = Stemma.from_dict(export)

    resolved = client.resolve("stemma:test.alias-old")
    assert resolved["resolved"] == "stemma:test.alias-new"
    assert resolved["chain"] == [
        "stemma:test.alias-old",
        "stemma:test.alias-mid",
        "stemma:test.alias-new",
    ]

    visible_ids = [entity["id"] for entity in client.entities()]
    assert "stemma:test.alias-old" not in visible_ids
    assert "stemma:test.alias-mid" not in visible_ids
    expect_raises(NotFoundError, client.entity, "stemma:test.alias-old")
    assert client.entity("stemma:test.alias-old", include_retired=True)["status"] == "deprecated"

    prereqs_all = [entity["id"] for entity in client.prerequisites("stemma:test.root", policy="all")]
    assert prereqs_all == [
        "stemma:test.alpha",
        "stemma:test.beta",
        "stemma:test.gamma",
        "stemma:test.velocity",
    ]
    prereqs_canonical = [entity["id"] for entity in client.prerequisites("stemma:test.root", policy="canonical")]
    assert prereqs_canonical == [
        "stemma:test.alpha",
        "stemma:test.beta",
        "stemma:test.gamma",
    ]
    assert "stemma:test.root" not in prereqs_all
    assert "stemma:test.alias-old" not in prereqs_all
    assert len(client.connections(policy="all")) == 5
    assert all(connection["id"] != "stemma:conn.000006" for connection in client.connections(policy="all"))

    invalid_version = copy.deepcopy(export)
    invalid_version["export_version"] = "1.9.0"
    expect_raises(ExportError, load_export, invalid_version)

    dangling = copy.deepcopy(export)
    dangling["connections"][0]["target"] = "stemma:test.unknown"
    expect_raises(ExportError, load_export, dangling)

    dup = copy.deepcopy(export)
    dup["entities"] = dup["entities"] + [copy.deepcopy(dup["entities"][0])]
    dup["entity_count"] = len(dup["entities"])
    expect_raises(ExportError, load_export, dup)

    missing_member = copy.deepcopy(export)
    missing_member.pop("sources")
    expect_raises(ExportError, load_export, missing_member)

    bad_source_ref = copy.deepcopy(export)
    bad_source_ref["connections"][0]["evidence"][0]["source_ref"] = "stemma:src.missing"
    expect_raises(ExportError, load_export, bad_source_ref)

    # ADR-0032 / export v2.1: registry-present exports must fail closed on a
    # connection whose relation is not declared.
    unknown_relation = copy.deepcopy(export)
    unknown_relation["connections"][0]["relation"] = "unknown_relation_x"
    expect_raises(ExportError, load_export, unknown_relation)

    registry_without_version = copy.deepcopy(export)
    registry_without_version.pop("relation_registry_version")
    expect_raises(ExportError, load_export, registry_without_version)

    # Pre-2.1 (no registry) exports remain loadable and do not offer registry
    # introspection or fail-closed relation checks.
    v20 = copy.deepcopy(export)
    v20["export_version"] = "2.0.0"
    v20.pop("relation_registry_version")
    v20.pop("relation_registry")
    v20.pop("vocabularies")
    v20["connections"][0]["relation"] = "unknown_relation_x"
    v20_client = Stemma.from_dict(v20)
    assert len(v20_client.connections(policy="all")) == 5
    expect_raises(ExportError, v20_client.relations)
    expect_raises(ExportError, v20_client.relation, "requires")


def test_rejected_visibility() -> None:
    """ADR-0031: default/all views exclude rejected; stats expose it and the
    rejected set is queryable explicitly (rejected is still an active record)."""
    export = synthetic_export()
    target = export["connections"][0]
    target["assertion"]["review"]["status"] = "rejected"
    target["lifecycle"] = {"reason": "contradicts primary source", "replaced_by": None}
    client = Stemma.from_dict(export)
    assert client.stats["rejected_connection_count"] == 1
    assert client.stats["active_connection_count"] == 4
    assert len(client.connections(policy="all")) == 4
    assert all(c["id"] != target["id"] for c in client.connections())
    assert client.connections(review="rejected") == [target]
    print("OK: rejected visibility")


def test_relation_introspection() -> None:
    export = synthetic_export()
    client = Stemma.from_dict(export)
    assert client.stats["export_version"] == "2.2.0"
    assert client.stats["relation_registry_version"] == "1.0.0"

    registry = client.relations()
    assert registry == SYNTHETIC_RELATION_REGISTRY
    assert sorted(registry) == [
        "depends_on",
        "logically_requires",
        "mathematically_requires",
        "requires",
    ]

    descriptor = client.relation("mathematically_requires")
    assert descriptor["family"] == "dependency"
    assert descriptor["transitive"] is True
    expect_raises(BadRequestError, client.relation, "not_a_relation")

    assert client.vocabularies == SYNTHETIC_VOCABULARIES

    # The client is also a loader consumer: connection relations are still
    # visible through the public query API.
    assert {conn["relation"] for conn in client.connections(policy="all")} == {
        "depends_on",
        "logically_requires",
        "mathematically_requires",
        "requires",
    }


def test_cli_smoke() -> None:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(PYTHON_ROOT)
    export_path = REPO_ROOT / "exports" / "knowledge.json"

    def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", "-m", "stemma_adapter", *args],
            cwd=str(REPO_ROOT),
            env=env,
            text=True,
            capture_output=True,
        )

    validate = run_cli("validate", str(export_path))
    assert validate.returncode == 0, validate.stderr
    assert json.loads(validate.stdout)["ok"] is True

    stats = run_cli("stats", str(export_path))
    assert stats.returncode == 0, stats.stderr
    loaded = json.loads(stats.stdout)
    if loaded["entity_count"] == 0:
        print("SKIP: test_cli_smoke (0 entities in empty knowledge base)")
        return
    assert loaded["entity_count"] == len(_raw_export()["entities"])

    for conn in (c for c in _raw_export()["connections"] if c.get("value") is not None):
        values = run_cli("values", str(export_path), conn["source"])
        assert values.returncode == 0, values.stderr
        assert conn["id"] in [v["connection_id"] for v in json.loads(values.stdout)]

    resolve = run_cli("resolve", str(export_path), "stemma:phys.force")
    assert resolve.returncode == 0, resolve.stderr
    assert json.loads(resolve.stdout)["resolved"] == "stemma:phys.force"

    search = run_cli("search", str(export_path), "force", "--domain", "physics", "--limit", "1")
    assert search.returncode == 0, search.stderr
    assert json.loads(search.stdout)[0]["id"] == "stemma:phys.force"

    relations = run_cli("relations", str(export_path))
    assert relations.returncode == 0, relations.stderr
    registry = json.loads(relations.stdout)
    assert "related_to" in registry

    relation = run_cli("relation", str(export_path), "mathematically_requires")
    assert relation.returncode == 0, relation.stderr
    assert json.loads(relation.stdout)["family"] == "dependency"

    unknown_relation = run_cli("relation", str(export_path), "not_a_real_relation")
    assert unknown_relation.returncode == 1

    vocabularies = run_cli("vocabularies", str(export_path))
    assert vocabularies.returncode == 0, vocabularies.stderr
    assert "physics" in json.loads(vocabularies.stdout)["domains"]

    with tempfile.TemporaryDirectory() as tmpdir:
        invalid_path = Path(tmpdir) / "invalid.json"
        invalid_export = synthetic_export()
        invalid_export["export_version"] = "1.0.0"
        write_json(invalid_path, invalid_export)
        invalid = run_cli("validate", str(invalid_path))
        assert invalid.returncode == 2


def test_server() -> None:
    client = Stemma.from_file(str(REPO_ROOT / "exports" / "knowledge.json"))
    server = serve(client, host="127.0.0.1", port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.port}"
    try:
        status, headers, payload = http_json(base_url + "/")
        assert status == 200
        assert headers["Access-Control-Allow-Origin"] == "*"
        if payload["stats"]["entity_count"] == 0:
            print("SKIP: test_server (0 entities in empty knowledge base)")
            return
        assert payload["stats"]["entity_count"] == len(_raw_export()["entities"])
        etag = headers["ETag"]

        status, _, payload = http_json(base_url + "/v2/stats")
        assert status == 200
        assert payload["connection_count"] == len(_raw_export()["connections"])

        status, _, payload = http_json(base_url + "/v2/stats", etag=etag)
        assert status == 304
        assert payload is None

        for conn in (c for c in _raw_export()["connections"] if c.get("value") is not None):
            status, _, payload = http_json(base_url + "/v2/values/" + conn["source"].replace(":", "%3A"))
            assert status == 200
            assert [v["value"] for v in payload if v["connection_id"] == conn["id"]] == [conn["value"]]

        status, _, payload = http_json(base_url + "/v2/entities/stemma%3Aphys.force")
        assert status == 200
        assert payload["id"] == "stemma:phys.force"

        status, _, payload = http_json(base_url + "/v2/resolve/stemma%3Aphys.force")
        assert status == 200
        assert payload["resolved"] == "stemma:phys.force"

        status, _, payload = http_json(base_url + "/v2/search?q=force&domain=physics")
        assert status == 200
        assert payload[0]["id"] == "stemma:phys.force"

        status, _, payload = http_json(base_url + "/v2/external/wd/Q14038")
        assert status == 200
        assert payload["id"] == "stemma:phys.force"

        status, _, payload = http_json(base_url + "/v2/relations")
        assert status == 200
        assert "related_to" in payload

        status, _, payload = http_json(base_url + "/v2/relations/mathematically_requires")
        assert status == 200
        assert payload["family"] == "dependency"

        status, _, payload = http_json(base_url + "/v2/relations/not_a_real_relation")
        assert status == 400

        status, _, payload = http_json(base_url + "/v2/vocabularies")
        assert status == 200
        assert "physics" in payload["domains"]

        status, _, payload = http_json(base_url + "/v2/entities/stemma%3Aphys.unknown")
        assert status == 404
        assert "unknown entity id" in payload["error"]

        status, _, payload = http_json(base_url + "/v2/search")
        assert status == 400
        assert payload["error"] == "missing required query parameter: q"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def main() -> int:
    test_real_export()
    test_synthetic_export()
    test_valued_claim_contract()
    test_rejected_visibility()
    test_relation_introspection()
    test_cli_smoke()
    test_server()
    print("OK: adapter tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
