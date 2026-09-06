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
        "export_version": "2.1.0",
        "schema_version": "1.1.0",
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


def test_real_export() -> None:
    export_path = REPO_ROOT / "exports" / "knowledge.json"
    export = load_export(export_path)
    assert export["entity_count"] == 224
    assert export["connection_count"] == 654
    assert export["source_count"] == 3

    client = Stemma.from_file(str(export_path))
    assert client.stats["entity_count"] == 224
    assert client.stats["connection_count"] == 654
    assert client.stats["source_count"] == 3
    assert len(client.entities_by_id) == 224
    assert len(client.all_connections) == 654
    assert len(client.sources_by_id) == 3

    expected_counts = {
        "all": 650,
        "reviewed": 50,
        "canonical": 50,
        "trusted": 50,
    }
    for policy, expected in expected_counts.items():
        filtered = filter_connections(client.all_connections, policy)
        assert len(filtered) == expected
        exported = json.loads((REPO_ROOT / "exports" / f"knowledge.{policy}.json").read_text(encoding="utf-8"))
        assert exported["count"] == expected
        assert [conn["id"] for conn in filtered] == [conn["id"] for conn in exported["connections"]]
        assert len(client.connections(policy=policy)) == expected

    proposed_count = sum(
        1
        for connection in client.all_connections
        if connection["assertion"]["review"]["status"] == "unreviewed"
        and connection["assertion"]["type"] == "proposed"
    )
    assert proposed_count == 604

    all_ids = {conn["id"] for conn in client.connections(policy="all")}
    canonical_ids = {conn["id"] for conn in client.connections(policy="canonical")}
    assert canonical_ids <= all_ids

    force = client.by_external_id("wd", "Q11402")
    assert force["id"] == "stemma:phys.force"

    prereqs_all = {entity["id"] for entity in client.prerequisites("stemma:phys.newtons-second-law", policy="all")}
    assert "stemma:phys.newtons-second-law" not in prereqs_all
    for required in {
        "stemma:phys.force",
        "stemma:phys.mass",
        "stemma:phys.acceleration",
        "stemma:phys.vector",
    }:
        assert required in prereqs_all
    assert "stemma:phys.velocity" in prereqs_all

    prereqs_canonical = {
        entity["id"] for entity in client.prerequisites("stemma:phys.newtons-second-law", policy="canonical")
    }
    assert prereqs_canonical <= prereqs_all
    assert "stemma:phys.velocity" not in prereqs_canonical

    search_results = client.search("force", domain="physics")
    assert search_results[0]["id"] == "stemma:phys.force"
    assert [entity["id"] for entity in search_results] == [
        entity["id"] for entity in client.search("force", domain="physics")
    ]


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
    assert client.stats["export_version"] == "2.1.0"
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
    assert json.loads(stats.stdout)["entity_count"] == 224

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
        assert payload["stats"]["entity_count"] == 224
        etag = headers["ETag"]

        status, _, payload = http_json(base_url + "/v2/stats")
        assert status == 200
        assert payload["connection_count"] == 654

        status, _, payload = http_json(base_url + "/v2/stats", etag=etag)
        assert status == 304
        assert payload is None

        status, _, payload = http_json(base_url + "/v2/entities/stemma%3Aphys.force")
        assert status == 200
        assert payload["id"] == "stemma:phys.force"

        status, _, payload = http_json(base_url + "/v2/resolve/stemma%3Aphys.force")
        assert status == 200
        assert payload["resolved"] == "stemma:phys.force"

        status, _, payload = http_json(base_url + "/v2/search?q=force&domain=physics")
        assert status == 200
        assert payload[0]["id"] == "stemma:phys.force"

        status, _, payload = http_json(base_url + "/v2/external/wd/Q11402")
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
    test_rejected_visibility()
    test_relation_introspection()
    test_cli_smoke()
    test_server()
    print("OK: adapter tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
