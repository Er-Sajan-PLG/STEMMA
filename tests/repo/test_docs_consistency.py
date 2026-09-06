#!/usr/bin/env python3
"""Documentation consistency invariant (ADR-0029).

The authoritative documentation set is exactly one document per subject, the
index (docs/README.md) lists exactly the files that exist, required root
documents exist, and no living doc links to a retired document.
"""
from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"

REQUIRED_DOCS = [
    "docs/README.md", "docs/VISION.md", "docs/ARCHITECTURE.md",
    "docs/DOMAIN-MODEL.md", "docs/SCHEMA-SPECIFICATION.md",
    "docs/METADATA-SPECIFICATION.md", "docs/RELATIONSHIP-SPECIFICATION.md",
    "docs/PIPELINES.md", "docs/IMPLEMENTATION-STATUS.md", "docs/ROADMAP.md",
    "docs/TESTING.md", "docs/STANDARDS.md", "docs/GOVERNANCE.md",
    "docs/SECURITY-INTEGRITY-PROVENANCE.md", "docs/CONSUMERS.md",
    "docs/VERSIONING.md", "docs/MIGRATIONS.md", "docs/GLOSSARY.md",
    "docs/CURATION-PROTOCOL.md", "docs/INGESTION.md", "docs/SOURCES.md",
    "docs/CONTRIBUTING.md", "docs/decisions/README.md",
    "README.md", "AGENTS.md", "LICENSE", "LICENSE-CODE", "VERSION",
]

# Documents retired with the refoundation must not be linked from living docs.
RETIRED = [
    "NORTHSTAR.md", "MASTER-VISION.md", "STEMMA-SPECIFICATION.md",
    "STEMMA-ROADMAP.md", "STEMMA-IMPLEMENTATION-PLAN.md",
    "STEMMA-IMPLEMENTATION-PLAN-v2.md", "STEMMA-CONSUMER-SEAM.md",
    "ARCHITECTURE-AUDIT-v1.0.md", "ARCHITECTURE-REVIEW-v0.3.md",
    "EXPORT-VERSION-MIGRATION-Q3.md", "HISTORY-RENAME.md",
    "REVIEW-RESPONSE.md", "AXIOM-KERNEL-PLAN.md",
    "grade12-curriculum-mapping.md", "RELATIONSHIP-MODEL-ADR-0011-note.md",
]

ALLOWED_HISTORICAL = {"docs/MIGRATIONS.md", "docs/decisions/README.md"} | {
    str(p.relative_to(ROOT).as_posix()) for p in (DOCS / "decisions").glob("*.md")
}


def check_required() -> list[str]:
    return [f"missing required document: {rel}" for rel in REQUIRED_DOCS
            if not (ROOT / rel).exists()]


def check_index_matches_files() -> list[str]:
    problems = []
    index = (DOCS / "README.md").read_text(encoding="utf-8")
    md_files = {p.name for p in DOCS.glob("*.md")}
    linked = set(re.findall(r"\(([A-Z][A-Za-z0-9-]*\.md)\)", index))
    unlisted = md_files - linked - {"README.md"}
    if unlisted:
        problems.append(f"docs/README.md does not list: {sorted(unlisted)}")
    for name in linked:
        if name == "README.md":
            continue
        if not (DOCS / name).exists():
            problems.append(f"docs/README.md links to nonexistent {name}")
    return problems


def check_no_retired_links() -> list[str]:
    problems = []
    living = [p for p in DOCS.rglob("*.md")
              if p.relative_to(ROOT).as_posix() not in ALLOWED_HISTORICAL]
    living += [ROOT / "README.md", ROOT / "AGENTS.md"]
    for path in living:
        text = path.read_text(encoding="utf-8")
        for name in RETIRED:
            if name in text:
                problems.append(
                    f"{path.relative_to(ROOT)} references retired document {name}"
                )
    return problems


def check_versions_single_sourced() -> list[str]:
    import yaml  # noqa: PLC0415
    problems = []
    versions = yaml.safe_load((ROOT / "schema" / "VERSION.yaml").read_text())
    for key in ("schema_version", "export_version", "relation_registry_version"):
        if not versions.get(key):
            problems.append(f"schema/VERSION.yaml missing {key}")
    if versions.get("legacy_export_version"):
        problems.append("legacy_export_version key still present (window closed)")
    return problems


def main() -> int:
    problems = (check_required() + check_index_matches_files()
                + check_no_retired_links() + check_versions_single_sourced())
    if problems:
        print("DOCS CONSISTENCY FAILURES:")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("ALL DOCS CONSISTENCY TESTS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
