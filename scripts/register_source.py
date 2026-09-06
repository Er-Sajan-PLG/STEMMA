#!/usr/bin/env python3
"""Register a new source record in STEMMA."""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
SOURCES_DIR = ROOT / "sources"

SOURCE_TYPES = {
    "textbook", "academic-paper", "standard", "institutional",
    "web", "dataset", "oer", "other"
}

SOURCE_ROLES = {"primary", "secondary", "aggregator", "retrieval"}

COPYRIGHT_STATUSES = {
    "copyrighted", "public-domain", "cc0", "cc-by", "cc-by-sa", 
    "cc-by-nc", "cc-by-nd", "cc-by-nc-sa", "cc-by-nc-nd", "unknown"
}

LICENSES = {
    "CC0", "CC BY 4.0", "CC BY-SA 4.0", "CC BY-NC 4.0", "CC BY-NC-SA 4.0",
    "CC BY-ND 4.0", "CC BY-NC-ND 4.0", "Public Domain", "Other"
}


def load_existing_sources() -> dict[str, dict]:
    sources = {}
    if SOURCES_DIR.exists():
        for path in SOURCES_DIR.glob("*.yaml"):
            try:
                data = yaml.safe_load(path.read_text())
                if isinstance(data, dict) and data.get("id"):
                    sources[data["id"]] = data
            except Exception:
                pass
    return sources


def generate_slug(title: str, year: int | None = None) -> str:
    import re
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
    if year:
        slug = f"{slug}-{year}"
    return slug[:80]


def main() -> int:
    parser = argparse.ArgumentParser(description="Register a new source in STEMMA")
    parser.add_argument("--type", required=True, choices=sorted(SOURCE_TYPES),
                        help="Source type")
    parser.add_argument("--title", required=True, help="Full title")
    parser.add_argument("--authors", help="Comma-separated authors")
    parser.add_argument("--year", type=int, help="Publication year")
    parser.add_argument("--publisher", help="Publisher")
    parser.add_argument("--journal", help="Journal name")
    parser.add_argument("--volume", help="Volume")
    parser.add_argument("--doi", help="DOI identifier")
    parser.add_argument("--isbn", help="ISBN")
    parser.add_argument("--edition", help="Edition")
    parser.add_argument("--language", default="en", help="Language code")
    parser.add_argument("--source-role", choices=sorted(SOURCE_ROLES), default="primary",
                        help="Source role")
    parser.add_argument("--license", choices=sorted(LICENSES), default="CC BY 4.0",
                        help="License")
    parser.add_argument("--copyright-status", choices=sorted(COPYRIGHT_STATUSES), default="copyrighted",
                        help="Copyright status")
    parser.add_argument("--url", help="Canonical URL")
    parser.add_argument("--archive-url", help="Archive URL (Wayback)")
    parser.add_argument("--checksum", help="SHA256 checksum")
    parser.add_argument("--citation", help="Full citation text")
    parser.add_argument("--lifecycle", choices=["active", "superseded", "withdrawn", "unavailable", "retracted"],
                        default="active", help="Lifecycle state")
    parser.add_argument("--supersedes", help="Comma-separated list of source IDs this supersedes")
    parser.add_argument("--superseded-by", help="Source ID that supersedes this")
    parser.add_argument("--notes", help="Additional notes")
    
    args = parser.parse_args()
    
    # Generate ID
    slug = generate_slug(args.title, args.year)
    source_id = f"lhs:src.{slug}"
    
    # Check for duplicate
    existing = load_existing_sources()
    if source_id in existing:
        print(f"Source {source_id} already exists!", file=sys.stderr)
        return 1
    
    # Build source record
    source = {
        "id": source_id,
        "type": args.type,
        "title": args.title,
        "citation": args.citation or args.title,
        "publisher": args.publisher,
        "journal": args.journal,
        "volume": args.volume,
        "doi": args.doi,
        "isbn": args.isbn,
        "edition": args.edition,
        "language": args.language,
        "source_role": args.source_role,
        "license": args.license,
        "copyright_status": args.copyright_status,
        "url": args.url,
        "archive_url": args.archive_url,
        "checksum": args.checksum,
        "lifecycle": args.lifecycle,
        "accessed_at": datetime.now(timezone.utc).isoformat(),
        "canonical_source_url": args.url,
        "archive_url": args.archive_url,
        "checksum": args.checksum,
    }
    
    if args.authors:
        source["authors"] = [a.strip() for a in args.authors.split(",")]
    if args.year:
        source["year"] = args.year
    if args.supersedes:
        source["supersedes"] = [s.strip() for s in args.supersedes.split(",")]
    if args.superseded_by:
        source["superseded_by"] = args.superseded_by
    if args.notes:
        source["notes"] = args.notes
    
    # Remove None values
    source = {k: v for k, v in source.items() if v is not None and v != ""}
    
    # Write
    SOURCES_DIR.mkdir(parents=True, exist_ok=True)
    path = SOURCES_DIR / f"{source_id}.yaml"
    path.write_text(yaml.safe_dump(source, sort_keys=False, allow_unicode=True))
    
    print(f"Registered source: {source_id}")
    print(f"Written to: {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())