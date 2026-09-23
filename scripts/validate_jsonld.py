#!/usr/bin/env python3
"""Validate exports/knowledge.jsonld (R6 increment 1, gate discipline)."""
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CANONICAL = ROOT / "content"
CONNECTIONS = ROOT / "connections"


def main() -> int:
    import yaml  # venv
    out = ROOT / "exports" / "knowledge.jsonld"
    errors: list[str] = []
    if not out.exists():
        print("FAIL: exports/knowledge.jsonld missing — run scripts/export_jsonld.py", file=sys.stderr)
        return 1
    try:
        d = json.loads(out.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:  # pragma: no cover - fatal layout
        print(f"FAIL: knowledge.jsonld invalid JSON: {exc}", file=sys.stderr)
        return 1

    ctx = d.get("@context") or {}
    for key in ("skos", "qudt", "stemma", "dcterms"):
        if key not in ctx:
            errors.append(f"@context missing prefix: {key}")
    graph = d.get("@graph")
    if not isinstance(graph, list):
        errors.append("@graph missing or not a list")
    else:
        ent_nodes = [n for n in graph if isinstance(n.get("@type"), list)]
        conn_nodes = [n for n in graph if n.get("@type") == "stemma:Assertion"]

        # source-of-truth cross-check: canonical entities in content/
        canon_ids = set()
        for path in sorted(CANONICAL.rglob("*.md")):
            fm = yaml.safe_load(path.read_text(encoding="utf-8").split("\n---\n", 1)[0][4:])
            if fm.get("id") and fm.get("status") == "canonical":
                canon_ids.add(fm["id"])
        proj_ids = {n["@id"] for n in ent_nodes}
        if proj_ids != canon_ids:
            errors.append(f"entity projection mismatch: {sorted(proj_ids ^ canon_ids)}")

        canon_conn = set()
        for path in sorted(CONNECTIONS.glob("*.yaml")):
            cd = yaml.safe_load(path.read_text(encoding="utf-8"))
            if ((cd.get("assertion") or {}).get("review") or {}).get("status") == "canonical":
                canon_conn.add(cd["id"])
        proj_conn = {n["@id"] for n in conn_nodes}
        if proj_conn != canon_conn:
            errors.append(f"connection projection mismatch: {sorted(proj_conn ^ canon_conn)}")

        for n in graph:  # per-node shape
            for req in ("@id", "@type"):
                if req not in n:
                    errors.append(f"node missing {req}: {n.get('@id', '?')}")
            if isinstance(n.get("@type"), list):  # entity node
                if not n.get("definition") or not n.get("name"):
                    errors.append(f"entity {n['@id']}: missing skos fields")
                if n.get("status") != "canonical":
                    errors.append(f"entity {n['@id']}: non-canonical leaked into projection")
                if "stemma:Quantity" in n["@type"]:
                    for f in ("quantityKind", "tensorCharacter", "sameDimensionalQuantities"):
                        if not n.get(f):
                            errors.append(f"quantity {n['@id']}: firm field {f} missing in projection")
                if "stemma:Unit" in n["@type"] and not n.get("sameDimensionalQuantities"):
                    errors.append(f"unit {n['@id']}: sameDimensionalQuantities missing")
            else:  # assertion node
                if not n.get("predicate") or not n.get("subject"):
                    errors.append(f"assertion {n['@id']}: missing predicate/subject")
                if not n.get("object") and n.get("value") is None:
                    errors.append(f"assertion {n['@id']}: needs object (relational) or value (value-slot)")
                if n.get("reviewStatus") != "canonical":
                    errors.append(f"assertion {n['@id']}: non-canonical leaked into projection")

    if errors:
        print("FAIL: knowledge.jsonld validation:")
        for e in errors[:25]:
            print(f"  - {e}")
        return 1
    print(f"OK: knowledge.jsonld validated ({sum(1 for n in graph if isinstance(n.get('@type'), list))} entities,"
          f" {sum(1 for n in graph if n.get('@type') == 'stemma:Assertion')} assertions, canonical-only)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
