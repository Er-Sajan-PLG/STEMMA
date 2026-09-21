#!/usr/bin/env python3
"""Migrates a STEMMA export JSON from v2.0.0 to v2.1.0.

It injects `relation_registry` and `vocabularies` from the current canonical schema/ directory
into an older v2.0.0 export file, bumping the version to v2.1.0.
"""

import json
import sys
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = ROOT / "schema"

def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 migrate_export_v2_to_v21.py <input_v2.json> <output_v2.1.json>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    if not input_path.exists():
        print(f"Error: {input_path} not found.")
        sys.exit(1)

    with input_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if data.get("export_version") != "2.0.0":
        print(f"Warning: Expected export_version 2.0.0, found {data.get('export_version')}")

    # Load relation registry and vocabularies from repo
    reg = load_yaml(SCHEMA_DIR / "relation-registry.yaml")
    voc = load_yaml(SCHEMA_DIR / "vocabularies.yaml")

    data["export_version"] = "2.1.0"
    data["relation_registry_version"] = reg.get("version", "1.0")
    
    if "relations" in reg:
        data["relation_registry"] = reg["relations"]
    if voc:
        data["vocabularies"] = voc

    # Write output deterministically
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    
    print(f"Migration complete! Wrote v2.1.0 export to {output_path}")

if __name__ == "__main__":
    main()
