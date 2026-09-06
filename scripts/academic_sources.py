#!/usr/bin/env python3
"""R2 — Academic source backfill driver (derived report; not a gate).

Produces `reports/academic-sources.json` + `.md` describing:

  * entity provenance source strings that do NOT resolve to a canonical
    `sources/*.yaml` record (44 distinct strings in the audit at the time of
    the SOTA review);
  * evidence `source_ref` values on connections that do NOT resolve to a
    canonical source id;
  * counts that let a human decide what backfill is needed.

This is deliberately advisory: it never edits canonical data and never fails
the verification chain.
"""
from __future__ import annotations

import json
import pathlib
import sys
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
CONNECTIONS = ROOT / "connections"
SOURCES = ROOT / "sources"
OUT_JSON = ROOT / "reports" / "academic-sources.json"
OUT_MD = ROOT / "reports" / "academic-sources.md"


def _load_yaml_files(directory: pathlib.Path) -> list[dict]:
    """Load every *.yaml file in a directory (canonical records)."""
    out = []
    if not directory.exists():
        return out
    import yaml
    for path in sorted(directory.glob("*.yaml")):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            out.append({"id": path.stem, "_error": str(exc)})
            continue
        if isinstance(data, dict):
            data["_file"] = str(path.relative_to(ROOT))
            out.append(data)
    return out


def build_report(root: pathlib.Path = ROOT) -> dict:
    import yaml
    content_dir = root / "content"
    connections_dir = root / "connections"
    sources_dir = root / "sources"

    entities = []
    for path in sorted(content_dir.rglob("*.md")):
        raw = path.read_text(encoding="utf-8")
        if not raw.startswith("---"):
            continue
        try:
            data = yaml.safe_load(raw.split("---", 2)[1])
        except Exception as exc:  # noqa: BLE001
            data = {"_file": str(path.relative_to(root)), "_error": str(exc)}
        if isinstance(data, dict):
            data["_file"] = str(path.relative_to(root))
            entities.append(data)

    sources = _load_yaml_files(sources_dir)
    source_ids = {s.get("id") for s in sources if isinstance(s.get("id"), str)}
    source_citations = {s.get("id"): s.get("citation") for s in sources if isinstance(s.get("id"), str)}

    def matches_source(value: str | None) -> bool:
        if not value:
            return False
        if value in source_ids:
            return True
        # Cite-by-text: if the string equals a canonical citation text, resolve.
        return value in source_citations.values()

    entity_sources: list[str] = []
    unresolved_entity_sources: dict[str, list[dict]] = {}
    for ent in entities:
        for key in ("provenance.source", "provenance.reviewer"):
            value = None
            prov = ent.get("provenance") or {}
            if key == "provenance.source":
                value = prov.get("source")
            else:
                # Reviewer is an agent id, not a citation; skip.
                continue
            if isinstance(value, str) and value.strip():
                entity_sources.append(value)
                if not matches_source(value):
                    # Skip agent-style ids (should not appear as source strings).
                    if value.startswith(("human:", "llm:", "process:", "unknown:")):
                        continue
                    unresolved_entity_sources.setdefault(value, []).append(
                        {"id": ent.get("id"), "file": ent.get("_file")}
                    )

    evidence_refs: list[str] = []
    unresolved_evidence_refs: dict[str, list[str]] = {}
    conn_records = _load_yaml_files(connections_dir)
    for conn in conn_records:
        for ev in conn.get("evidence") or []:
            ref = ev.get("source_ref") if isinstance(ev, dict) else None
            if isinstance(ref, str) and ref.strip():
                evidence_refs.append(ref)
                if ref not in source_ids:
                    unresolved_evidence_refs.setdefault(ref, []).append(str(conn.get("id")))

    return {
        "source_count": len(source_ids),
        "entity_count": len(entities),
        "entity_provenance_source_count": len(entity_sources),
        "unresolved_entity_provenance_sources": sorted(unresolved_entity_sources),
        "unresolved_entity_source_count": len(unresolved_entity_sources),
        "evidence_source_ref_count": len(evidence_refs),
        "unresolved_evidence_source_ref_count": len(unresolved_evidence_refs),
        "unresolved_evidence_source_refs": {
            ref: sorted(set(conns)) for ref, conns in sorted(unresolved_evidence_refs.items())
        },
        "by_entity_source": dict(Counter(entity_sources).most_common()),
        "advisory": True,
    }


def write_report(report: dict) -> None:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Academic source backfill drivers (advisory)",
        "",
        "Generated by `scripts/academic_sources.py`. This report drives source",
        "backfill; it does not gate or modify canonical data.",
        "",
        f"- Canonical source records: **{report['source_count']}**",
        f"- Entities: **{report['entity_count']}**",
        f"- Entity provenance.source strings: **{report['entity_provenance_source_count']}**",
        f"- Unresolved entity provenance.source strings: **{report['unresolved_entity_source_count']}**",
        f"- Evidence source_ref values: **{report['evidence_source_ref_count']}**",
        f"- Unresolved evidence source_ref values: **{report['unresolved_evidence_source_ref_count']}**",
        "",
        "## Unresolved entity provenance sources",
        "",
    ]
    if report["unresolved_entity_provenance_sources"]:
        for src in report["unresolved_entity_provenance_sources"]:
            lines.append(f"- `{src}`")
    else:
        lines.append("- none")
    lines += ["", "## Unresolved evidence source_refs", ""]
    if report["unresolved_evidence_source_refs"]:
        for ref, conns in sorted(report["unresolved_evidence_source_refs"].items()):
            lines.append(f"- `{ref}` on {', '.join(conns)}")
    else:
        lines.append("- none")
    lines += ["", "## How to backfill", "",
               "1. Add a `sources/<slug>.yaml` record OR",
               "2. point the canonical record at an existing `stemma:src.*` id, and",
               "3. fix entity provenance.source / evidence source_ref to the canonical id.",
               ""]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    write_report(report)
    print(
        f"OK: academic-sources report — {report['unresolved_entity_source_count']} unresolved "
        f"entity sources, {report['unresolved_evidence_source_ref_count']} unresolved evidence refs "
        f"-> {OUT_JSON.relative_to(ROOT)}, {OUT_MD.relative_to(ROOT)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
