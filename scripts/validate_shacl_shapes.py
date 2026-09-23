#!/usr/bin/env python3
"""Enforce schema/projection/stemma-shapes.ttl on exports/knowledge.jsonld.

Subset semantics (minimum tooling per project instruction): sh:targetClass,
sh:path, sh:minCount, sh:maxCount, sh:datatype xsd:string. The TTL file is
the canonical spec; this runner is the deterministic gate. Parity between
TTL paths and enforced paths is test-pinned (tests/versioning/
test_release_bundle.py).
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SHAPES = ROOT / "schema" / "projection" / "stemma-shapes.ttl"
PROJECTION = ROOT / "exports" / "knowledge.jsonld"

PROP_RE = re.compile(
    r"sh:targetClass (?P<class>[a-zA-Z:]+[A-Za-z0-9]+) ;(.*?)sh:property \[ sh:path (?P<path>[a-zA-Z:]+[A-Za-z0-9]+) ;(.*?)\"?;",
    re.S)


def parse_shapes(text: str) -> dict:
    shapes: dict[str, list[dict]] = {}
    blocks = re.findall(r"(stemma:[A-Za-z]+Shape a sh:NodeShape ;[\s\S]*?)(?=stemma:[A-Za-z]+Shape|$)", text)
    for block in blocks:
        cls = re.search(r"sh:targetClass ([a-zA-Z:]+[A-Za-z0-9]+)", block).group(1)
        props = []
        for prop in re.findall(r"sh:property \[ (.*?) \]", block):
            entry = {"path": re.search(r"sh:path ([a-zA-Z:]+[A-Za-z0-9]+)", prop).group(1)}
            for k in ("minCount", "maxCount"):
                m = re.search(rf"sh:{k} (\d+)", prop)
                if m:
                    entry[k] = int(m.group(1))
            m = re.search(r"sh:datatype (xsd:[a-z]+)", prop)
            if m:
                entry["datatype"] = m.group(1)
            props.append(entry)
        shapes.setdefault(cls, []).extend(props)
    return shapes


def path_key(iri: str):
    local = iri.split(":")[-1]
    alias = {"prefLabel": "name", "definition": "definition", "status": "status"}
    return alias.get(local, local)


def main() -> int:
    errors: list[str] = []
    shapes = parse_shapes(SHAPES.read_text(encoding="utf-8"))
    doc = json.loads(PROJECTION.read_text(encoding="utf-8"))
    for node in doc.get("@graph", []):
        types = node.get("@type", [])
        types = types if isinstance(types, list) else [types]
        expanded = {"skos:Concept" if t == "skos:Concept" else t for t in types}
        for cls in ("skos:Concept", "stemma:Quantity", "stemma:Unit", "stemma:Assertion"):
            if cls not in expanded:
                continue
            for req in shapes.get(cls, []):
                key = path_key(req["path"])
                values = node.get(key)
                count = 0 if values is None else (len(values) if isinstance(values, list) else 1)
                if req.get("minCount") and count < req["minCount"]:
                    errors.append(f"{node.get('@id')}: {req['path']} minCount {req['minCount']}, got {count}")
                if req.get("maxCount") and count > req["maxCount"]:
                    errors.append(f"{node.get('@id')}: {req['path']} maxCount {req['maxCount']}, got {count}")
                if req.get("datatype") == "xsd:string" and count and not isinstance(
                        values if not isinstance(values, list) else values[0], str):
                    errors.append(f"{node.get('@id')}: {req['path']} not xsd:string")
    if errors:
        print("FAIL: SHACL-subset shape violations:")
        for e in errors[:25]:
            print(f"  - {e}")
        return 1
    print(f"OK: knowledge.jsonld conforms to stemma-shapes.ttl ({sum(len(v) for v in shapes.values())} property constraints)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
