#!/usr/bin/env python3
"""
Physics-Core Profile Check (ADR-0040/0041/0042)

Enforces minimal profile for physics domain:
- Forbidden fields: learning_objectives, real_world_applications, key_experiments, common_misconceptions
- Allowed relations only: mathematically_requires, derived_from, appears_in_law, applies_to, generalizes, special_case_of, part_of, approximates
- No related_to in physics/

Usage:
  python3 scripts/physics_core_profile_check.py [--profile physics-core] [--warn]
  --warn: exit 0 even on violations (advisory for CI)
  --profile physics-core: enforce physics-core rules (default)
"""

import argparse
import glob
import sys
import yaml
from pathlib import Path

# Minimal allowed relations per ADR-0042
PHYSICS_MINIMAL_RELATIONS = {
    "mathematically_requires",
    "derived_from",
    "appears_in_law",
    "applies_to",
    "generalizes",
    "special_case_of",
    "part_of",
    "approximates",
}

FORBIDDEN_ENTITY_FIELDS = {
    "learning_objectives",
    "real_world_applications",
    "key_experiments",
    "common_misconceptions",
}

def load_yaml(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def check_physics_entities(root: Path):
    violations = []
    # content/physics/**/*.md
    for md_path in root.glob("content/physics/**/*.md"):
        if md_path.name.startswith("."):
            continue
        text = md_path.read_text(encoding='utf-8')
        if not text.startswith("---"):
            continue
        try:
            frontmatter = text.split("---")[1]
            data = yaml.safe_load(frontmatter)
        except Exception as e:
            violations.append(f"{md_path}: failed to parse frontmatter: {e}")
            continue
        if not isinstance(data, dict):
            continue
        # Forbidden fields ADR-0041
        for field in FORBIDDEN_ENTITY_FIELDS:
            if field in data and data[field] not in (None, [], {}):
                violations.append(f"{md_path}: forbidden field '{field}' present (ADR-0041 minimal profile) — found {data[field]}")

        # ADR-0043: Mandatory source + dual verification
        prov = data.get("provenance", {}) or {}
        if not prov.get("source_kind"):
            violations.append(f"{md_path}: missing provenance.source_kind (ADR-0043 mandatory source)")
        if not prov.get("source"):
            violations.append(f"{md_path}: missing provenance.source (embedded citation) (ADR-0043)")
        # New fields: writer, link, retrieved_at - check raw text for presence (since schema may not require yet)
        # We check if they exist in provenance dict (profile check enforces even before schema bump)
        if not prov.get("writer"):
            violations.append(f"{md_path}: missing provenance.writer (who wrote entity) (ADR-0043 dual verification)")
        if not prov.get("link"):
            violations.append(f"{md_path}: missing provenance.link (URL/DOI) (ADR-0043)")
        else:
            link = str(prov.get("link"))
            if not (link.startswith("http://") or link.startswith("https://") or link.startswith("doi:")):
                violations.append(f"{md_path}: provenance.link must be URL or DOI, got '{link}'")
        if not prov.get("retrieved_at"):
            violations.append(f"{md_path}: missing provenance.retrieved_at (ADR-0043)")

        # source_refs array mandatory for physics
        source_refs = data.get("source_refs")
        if not source_refs or not isinstance(source_refs, list) or len(source_refs) == 0:
            violations.append(f"{md_path}: missing source_refs array >=1 (ADR-0043 dual verification, must point to sources/*.yaml)")
        else:
            for ref in source_refs:
                if not isinstance(ref, str) or not ref.startswith("stemma:src."):
                    violations.append(f"{md_path}: source_ref '{ref}' must be stemma:src.xxx")
                else:
                    # Check file exists
                    slug = ref.replace("stemma:", "")
                    src_path = root / f"sources/{slug}.yaml"
                    if not src_path.exists():
                        violations.append(f"{md_path}: source_ref '{ref}' has no file {src_path} (must have canonical source record)")

        # History: optional for draft, mandatory for human_reviewed/canonical for law/model/equation
        entity_type = data.get("type")
        status = data.get("status")
        if entity_type in ("law", "model", "equation", "experiment") and status in ("human_reviewed", "canonical"):
            hist = data.get("historical")
            if not hist:
                violations.append(f"{md_path}: type={entity_type} status={status} requires historical block (ADR-0043 optional for draft, mandatory for canonical)")
            else:
                if not hist.get("stated_by"):
                    violations.append(f"{md_path}: historical.stated_by missing")
                if not hist.get("year"):
                    violations.append(f"{md_path}: historical.year missing")
    return violations

def check_physics_connections(root: Path):
    violations = []
    for conn_path in root.glob("connections/*.yaml"):
        try:
            data = load_yaml(conn_path)
        except Exception as e:
            violations.append(f"{conn_path}: failed to parse: {e}")
            continue
        if not isinstance(data, dict):
            continue
        source = data.get("source", "")
        target = data.get("target", "")
        relation = data.get("relation", "")
        # Only check if source or target is physics domain
        is_physics = source.startswith("stemma:phys.") or target.startswith("stemma:phys.") or \
                     (isinstance(data.get("context"), dict) and data["context"].get("domain") == "physics")
        if not is_physics:
            # Also check if file is in physics context via evidence? For now only physics ids
            # But for empty repo, we check all connections as physics-core
            if source.startswith("stemma:") and target.startswith("stemma:"):
                is_physics = True
            else:
                continue
        if relation == "related_to":
            violations.append(f"{conn_path}: 'related_to' forbidden in physics-core (ADR-0042) — source={source} target={target}")
        elif relation not in PHYSICS_MINIMAL_RELATIONS:
            violations.append(f"{conn_path}: relation '{relation}' not in minimal set {PHYSICS_MINIMAL_RELATIONS} (ADR-0042) — source={source} target={target}")

        # ADR-0043: evidence mandatory >=1 with source_ref, locator, description
        evidence = data.get("evidence", [])
        if not evidence or len(evidence) == 0:
            violations.append(f"{conn_path}: evidence array mandatory >=1 for physics-core (ADR-0043), got empty")
        else:
            for idx, ev in enumerate(evidence):
                if not isinstance(ev, dict):
                    violations.append(f"{conn_path}: evidence[{idx}] not dict")
                    continue
                if not ev.get("source_ref"):
                    violations.append(f"{conn_path}: evidence[{idx}] missing source_ref (must point to canonical source)")
                else:
                    ref = ev["source_ref"]
                    if not ref.startswith("stemma:src."):
                        violations.append(f"{conn_path}: evidence[{idx}] source_ref '{ref}' must be stemma:src.xxx")
                    else:
                        slug = ref.replace("stemma:", "")
                        src_path = root / f"sources/{slug}.yaml"
                        if not src_path.exists():
                            violations.append(f"{conn_path}: evidence[{idx}] source_ref '{ref}' has no file {src_path}")
                if not ev.get("locator"):
                    violations.append(f"{conn_path}: evidence[{idx}] missing locator (page/section) (ADR-0043)")
                if not ev.get("description"):
                    violations.append(f"{conn_path}: evidence[{idx}] missing description (why source supports claim)")
                if not ev.get("type"):
                    violations.append(f"{conn_path}: evidence[{idx}] missing type")
                if not ev.get("stance"):
                    violations.append(f"{conn_path}: evidence[{idx}] missing stance")

        # Check provenance writer/link for connection too (optional but encouraged)
        prov = data.get("provenance", {}) or {}
        # For connections, writer is optional in v0.1, but we check if present
    return violations

def check_sources(root: Path):
    violations = []
    for src_path in root.glob("sources/*.yaml"):
        try:
            data = load_yaml(src_path)
        except Exception as e:
            violations.append(f"{src_path}: failed to parse: {e}")
            continue
        if not isinstance(data, dict):
            continue
        # Must have url OR doi OR isbn for verifiability
        if not (data.get("url") or data.get("doi") or data.get("isbn")):
            violations.append(f"{src_path}: must have url OR doi OR isbn for verifiability (ADR-0043)")
        if not data.get("authors") and not data.get("title"):
            violations.append(f"{src_path}: should have authors or title")
    return violations

def main():
    parser = argparse.ArgumentParser(description="Physics-core profile check")
    parser.add_argument("--warn", action="store_true", help="Advisory mode, exit 0 even on violations")
    parser.add_argument("--profile", default="physics-core", help="Profile name")
    args = parser.parse_args()

    root = Path(__file__).parent.parent
    entity_violations = check_physics_entities(root)
    conn_violations = check_physics_connections(root)
    source_violations = check_sources(root)
    all_violations = entity_violations + conn_violations + source_violations

    if all_violations:
        print(f"Physics-core profile check: {len(all_violations)} violation(s) found:")
        for v in all_violations:
            print(f"  - {v}")
        if args.warn:
            print("WARN mode: exiting 0 despite violations")
            return 0
        else:
            return 1
    else:
        print(f"OK: physics-core profile check passed — 0 violations (profile={args.profile})")
        print(f"  Allowed relations: {sorted(PHYSICS_MINIMAL_RELATIONS)}")
        print(f"  Forbidden entity fields: {sorted(FORBIDDEN_ENTITY_FIELDS)}")
        print(f"  Enforces: mandatory source_kind, source, writer, link, retrieved_at, source_refs>=1, evidence>=1 with source_ref+locator+description, historical mandatory for law/model/equation canonical (ADR-0043)")
        return 0

if __name__ == "__main__":
    sys.exit(main())
