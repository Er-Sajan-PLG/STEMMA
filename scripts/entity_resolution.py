#!/usr/bin/env python3
"""Entity Resolution / Deduplication for STEMMA acquisition.

Finds potential duplicate entities, synonyms, notation variants, and historical aliases.
Produces candidate matches for human review — never auto-merges.
"""
from __future__ import annotations

import difflib
import json
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
EXPORT = ROOT / "exports" / "knowledge.json"


def load_entities() -> dict[str, dict]:
    """Load all canonical entities from export."""
    if not EXPORT.exists():
        return {}
    data = json.loads(EXPORT.read_text())
    return {e["id"]: e for e in data.get("entities", [])}


def compute_similarity(name1: str, name2: str) -> float:
    """Compute string similarity ratio."""
    return difflib.SequenceMatcher(None, name1.lower(), name2.lower()).ratio()


def find_symbol_matches(entities: dict) -> list[dict]:
    """Find entities with same or similar symbols."""
    symbol_map = {}
    matches = []
    for eid, entity in entities.items():
        symbol = entity.get("symbol")
        if symbol:
            sym_lower = symbol.lower().strip()
            if sym_lower in symbol_map:
                matches.append({
                    "type": "symbol_match",
                    "entities": [symbol_map[sym_lower], eid],
                    "symbol": symbol,
                    "similarity": 1.0,
                })
            else:
                symbol_map[sym_lower] = eid
    return matches


def find_name_matches(entities: dict, threshold: float = 0.85) -> list[dict]:
    """Find entities with similar names."""
    matches = []
    names = [(eid, e.get("name", "")) for eid, e in entities.items() if e.get("name")]
    
    for i, (eid1, name1) in enumerate(names):
        for eid2, name2 in names[i+1:]:
            sim = compute_similarity(name1, name2)
            if sim >= threshold:
                matches.append({
                    "type": "name_similarity",
                    "entities": [eid1, eid2],
                    "names": [name1, name2],
                    "similarity": round(sim, 3),
                })
    return matches


def find_alias_matches(entities: dict) -> list[dict]:
    """Find entities where one's name appears in other's aliases."""
    matches = []
    for eid, entity in entities.items():
        aliases = entity.get("aliases", []) or []
        name = entity.get("name", "")
        for alias in aliases:
            # Check if alias matches another entity's name
            for other_id, other in entities.items():
                if other_id != eid and other.get("name") == alias:
                    matches.append({
                        "type": "alias_match",
                        "entities": [eid, other_id],
                        "alias": alias,
                        "matched_name": alias,
                    })
    return matches


def find_notation_variants(entities: dict) -> list[dict]:
    """Find potential notation variants (e.g., F=ma vs F=dp/dt)."""
    equation_map = {}
    matches = []
    for eid, entity in entities.items():
        eq = entity.get("equation", "") or ""
        if eq:
            # Normalize: remove spaces, common variations
            normalized = eq.lower().replace(" ", "").replace("·", "*").replace("×", "*")
            if normalized in equation_map:
                matches.append({
                    "type": "equation_variant",
                    "entities": [equation_map[normalized], eid],
                    "equations": [entities[equation_map[normalized]].get("equation"), eq],
                    "normalized": normalized,
                })
            else:
                equation_map[normalized] = eid
    return matches


def find_cross_domain_synonyms(entities: dict) -> list[dict]:
    """Find same concept in different domains (e.g., physics 'energy' vs chemistry 'energy')."""
    name_to_entities = {}
    for eid, entity in entities.items():
        name = entity.get("name", "").lower().strip()
        if name:
            name_to_entities.setdefault(name, []).append(eid)
    
    matches = []
    for name, eids in name_to_entities.items():
        if len(eids) > 1:
            domains = set(entities[eid].get("domain") for eid in eids)
            if len(domains) > 1:
                matches.append({
                    "type": "cross_domain_synonym",
                    "entities": eids,
                    "shared_name": name,
                    "domains": list(domains),
                })
    return matches


def main() -> int:
    entities = load_entities()
    if not entities:
        print("No entities found in export", file=sys.stderr)
        return 1
    
    print(f"Loaded {len(entities)} entities from export")
    
    all_matches = []
    all_matches.extend(find_symbol_matches(entities))
    all_matches.extend(find_name_matches(entities))
    all_matches.extend(find_alias_matches(entities))
    all_matches.extend(find_notation_variants(entities))
    all_matches.extend(find_cross_domain_synonyms(entities))
    
    # Deduplicate matches (same entity pair)
    seen_pairs = set()
    unique_matches = []
    for m in all_matches:
        pair = tuple(sorted(m["entities"]))
        if pair not in seen_pairs:
            seen_pairs.add(pair)
            unique_matches.append(m)
    
    print(f"\nFound {len(unique_matches)} candidate matches:")
    for m in unique_matches:
        eids = m["entities"]
        names = [entities[eid].get("name", "?") for eid in eids]
        print(f"  [{m['type']}] {eids[0]} ({names[0]})  ~  {eids[1]} ({names[1]})")
        if "similarity" in m:
            print(f"    similarity: {m['similarity']}")
        if "symbol" in m:
            print(f"    symbol: {m['symbol']}")
        if "alias" in m:
            print(f"    alias: {m['alias']}")
        if "shared_name" in m:
            print(f"    shared name: {m['shared_name']}")
            print(f"    domains: {m['domains']}")
    
    # Write matches for review
    output = ROOT / "proposals" / "entity_resolution_matches.yaml"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(yaml.safe_dump({
        "generated_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "entity_count": len(entities),
        "matches": unique_matches,
    }, sort_keys=False, allow_unicode=True))
    
    print(f"\nMatches written to {output.relative_to(ROOT)}")
    print("Review each match and decide: confirmed_match / possible_duplicate / historical_alias / synonym / notation_variant / keep_separate")
    return 0


if __name__ == "__main__":
    sys.exit(main())