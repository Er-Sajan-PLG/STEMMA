#!/usr/bin/env python3
"""R6 increment 1 — project the canonical tier to `exports/knowledge.jsonld`.

Design pinned by ADR-0007 (R6 projection publication), the R5 Amendment
(ADR-0053 + Amendment 0001, 2026-09-22: canonical keeps immutable `stemma:`
URNs; external PID/resolution base NOT claimed, deferred to publication),
ADR-0027 (ids are opaque), and the R4-firm-field owner directive
(quantity_kind / tensor_character / same_dimensional_quantities).

Rules:

- First-class JSON-LD document, NOT a dump: inline @context, entities and
  graph assertions as nodes; dual-typed to standard vocabularies (SKOS,
  QUDT, DCTerms, OWL-as-IRIs for Wikidata) where a defensible mapping
  exists; stemma: vocabulary terms expand as `stemma:scheme` opaque URIs
  (scheme name of the URN family the amendment binds — still internal,
  NOT an external resolution claim).
- Canonical tier ONLY: entity status == canonical; connection assertion
  review status == canonical. Derived from source files (content/,
  connections/) directly, independent of the consumer-export subsets.
- Byte-deterministic: sorted ids, fixed structure, json.dumps(indent=2,
  ensure_ascii=False); regenerated output must be byte-identical
  (tests/versioning/test_jsonld_determinism.py).

Value-slot connections (ADR-0045) project as assertions with
stemma:value (no object entity); relational ones with stemma:object.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
CONNECTIONS = ROOT / "connections"

import yaml  # pinned via /tmp/stemma-venv (repo-wide convention)


def _frontmatter(path: pathlib.Path) -> dict:
    parts = path.read_text(encoding="utf-8").split("\n---\n", 1)
    return yaml.safe_load(parts[0][4:] if parts[0].startswith("---") else parts[0])


CONTEXT = {
    "@version": 1.1,
    "@vocab": "stemma:",
    "stemma": "stemma:",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "dcterms": "http://purl.org/dc/terms/",
    "qudt": "http://qudt.org/schema/qudt/",
    "owl": "http://www.w3.org/2002/07/owl#",
    "name": "skos:prefLabel",
    "definition": "skos:definition",
    "status": "stemma:status",
    "reviewedAt": "stemma:reviewedAt",
    "reviewer": "stemma:reviewer",
    "writer": "dcterms:creator",
    "quantityKind": "stemma:quantityKind",
    "tensorCharacter": "stemma:tensorCharacter",
    "sameDimensionalQuantities": "stemma:sameDimensionalQuantities",
    "symbol": "stemma:symbol",
    "unit": "stemma:unit",
    "governedBy": {"@id": "stemma:governedBy", "@type": "@id"},
    "predicate": "stemma:predicate",
    "subject": "stemma:subject",
    "object": "stemma:object",
    "value": "stemma:value",
    "valueUnit": "stemma:valueUnit",
    "evidence": "stemma:evidence",
    "assertedBy": "stemma:assertedBy",
    "reviewStatus": "stemma:reviewStatus",
    "externalIds": "stemma:externalIds",
    "wikidata": {"@id": "stemma:wikidataEntity", "@type": "@id"},
    "entityType": "stemma:entityType",
    "provenance": "stemma:provenance",
    "aiDrafted": "stemma:aiDrafted",
    "sourceKind": "stemma:sourceKind",
    "sourceCitation": "stemma:sourceCitation",
    "delegatedProvenance": "stemma:delegatedProvenance",
}

ENTITY_TYPE_MAP = {
    "unit": ["skos:Concept", "qudt:Unit", "stemma:Unit"],
    "quantity": ["skos:Concept", "qudt:Quantity", "stemma:Quantity"],
    "law": ["skos:Concept", "stemma:Law"],
    "concept": ["skos:Concept", "stemma:Concept"],
    "misconception": ["skos:Concept", "stemma:Misconception"],
}
WIKIDATA_ORG = "http://www.wikidata.org/entity/"


def project_entity(d: dict) -> dict:
    node = {
        "@id": d["id"],
        "@type": ENTITY_TYPE_MAP.get(d.get("type"), ["skos:Concept", "stemma:Concept"]),
        "name": d.get("name"),
        "entityType": d.get("type"),
        "status": d.get("status"),
        "definition": d.get("definition"),
    }
    if d.get("type") in ("quantity", "unit"):
        node["sameDimensionalQuantities"] = d.get("same_dimensional_quantities") or []
    if d.get("type") == "quantity":
        node["quantityKind"] = d.get("quantity_kind")
        node["tensorCharacter"] = d.get("tensor_character")
    for k in ("symbol", "unit"):
        if d.get(k) is not None:
            node[k] = d[k]
    if d.get("governed_by"):
        node["governedBy"] = sorted(d["governed_by"])
    ext = d.get("external_ids") or {}
    if ext.get("wd"):
        node["externalIds"] = {"wikidata": WIKIDATA_ORG + str(ext["wd"])}
    prov = d.get("provenance") or {}
    node["provenance"] = {
        "aiDrafted": prov.get("ai_drafted"),
        "writer": prov.get("writer"),
        "reviewer": prov.get("reviewer"),
        "reviewedAt": prov.get("reviewed_at"),
        "sourceKind": prov.get("source_kind"),
        "sourceCitation": prov.get("source"),
    }
    return node


def project_connection(d: dict) -> dict:
    review = (d.get("assertion") or {}).get("review") or {}
    node = {
        "@id": d["id"],
        "@type": "stemma:Assertion",
        "predicate": d.get("relation"),
        "subject": d.get("source"),
        "reviewStatus": review.get("status"),
    }
    if d.get("target"):
        node["object"] = d["target"]
    elif d.get("value") is not None:
        node["value"] = d["value"]
        if d.get("unit"):
            node["valueUnit"] = d["unit"]
    if d.get("evidence"):
        node["evidence"] = [
            {"type": e.get("type"), "stance": e.get("stance"),
             "sourceRef": e.get("source_ref"), "locator": e.get("locator")}
            for e in d["evidence"]]
    prov = d.get("provenance") or {}
    ab = prov.get("asserted_by") or {}
    if ab:
        node["assertedBy"] = ab.get("id") if isinstance(ab, dict) else ab
    rb = [r.get("id") for r in prov.get("reviewed_by") or [] if isinstance(r, dict)]
    if rb:
        node["reviewer"] = sorted(rb)
    return node


def build_payload() -> dict:
    entities = []
    for path in sorted(CONTENT.rglob("*.md")):
        d = _frontmatter(path)
        if d.get("id") and d.get("status") == "canonical":
            entities.append(project_entity(d))
    entities.sort(key=lambda e: e["@id"])
    connections = []
    for path in sorted(CONNECTIONS.glob("*.yaml")):
        d = yaml.safe_load(path.read_text(encoding="utf-8"))
        review = (d.get("assertion") or {}).get("review") or {}
        if review.get("status") == "canonical":
            connections.append(project_connection(d))
    connections.sort(key=lambda c: c["@id"])
    return {"@context": CONTEXT,
            "generated_by": "scripts/export_jsonld.py — R6 increment 1 (projection mechanics; provisional external base per ADR-0053 Amendment 0001)",
            "@graph": entities + connections}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="exit non-zero unless committed export is byte-identical")
    args = ap.parse_args()
    payload = build_payload()
    text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    out = ROOT / "exports" / "knowledge.jsonld"
    if args.check:
        if not out.exists() or out.read_text(encoding="utf-8") != text:
            print("FAIL: exports/knowledge.jsonld not byte-identical — run scripts/export_jsonld.py",
                  file=sys.stderr)
            return 1
        print("OK: exports/knowledge.jsonld deterministic")
        return 0
    out.write_text(text, encoding="utf-8")
    nodes = payload["@graph"]
    n_ent = sum(1 for n in nodes if not isinstance(n.get("@type"), str))
    print(f"OK: wrote exports/knowledge.jsonld ({n_ent} entities, {len(nodes) - n_ent} assertions)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
