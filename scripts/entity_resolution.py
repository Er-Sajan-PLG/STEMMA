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


def resolve_claim_entities(claims_data, threshold=0.85):
    """
    AI-Assisted Semantic Acquisition Pipeline — Entity and concept identification.

    Identify STEM entities appearing in natural language:
    Young's modulus, stress, strain, temperature, lithium-ion battery, electrolyte, ionic conductivity
    and map them to STEMMA entities where existing identity can be established.
    If identity is uncertain, produce candidate entity rather than silently creating canonical one.

    This is NOT canonical — produces candidate matches for human review, never auto-merges.
    """
    claims = claims_data.get("claims", []) if isinstance(claims_data, dict) else claims_data
    entities = load_entities()

    print(f"Entity resolution for {len(claims)} claims — mapping to {len(entities)} existing STEMMA entities")
    print(f"Threshold {threshold} — if identity uncertain, produce candidate entity rather than silently creating canonical")

    resolved = []
    for claim_data in claims:
        claim = claim_data.get("claim", {})
        subject = claim.get("subject", "")
        obj = claim.get("object", "")

        # Try to map subject to existing entity
        subject_match = None
        subject_score = 0
        for eid, entity in entities.items():
            name = entity.get("name", "")
            # Exact match
            if subject.lower() == name.lower() or subject.lower() == eid.split(".")[-1].lower():
                subject_match = eid
                subject_score = 1.0
                break
            # Similarity
            sim = compute_similarity(subject, name)
            if sim > subject_score and sim >= threshold:
                subject_match = eid
                subject_score = sim

        # If no match or score < threshold, candidate entity
        if subject_match and subject_score >= threshold:
            print(f"  {claim_data.get('claim_id')}: subject '{subject}' → {subject_match} (score {subject_score:.2f}) — existing identity established")
            resolved_subject = subject_match
            subject_status = "existing"
        else:
            print(f"  {claim_data.get('claim_id')}: subject '{subject}' → candidate:entity_{subject} (score {subject_score:.2f}) — uncertain, candidate entity rather than silently canonical")
            resolved_subject = f"candidate:{subject}"
            subject_status = "candidate"

        # Same for object
        object_match = None
        object_score = 0
        for eid, entity in entities.items():
            name = entity.get("name", "")
            if obj.lower() == name.lower() or obj.lower() == eid.split(".")[-1].lower():
                object_match = eid
                object_score = 1.0
                break
            sim = compute_similarity(obj, name)
            if sim > object_score and sim >= threshold:
                object_match = eid
                object_score = sim

        if object_match and object_score >= threshold:
            print(f"    object '{obj}' → {object_match} (score {object_score:.2f}) — existing")
            resolved_object = object_match
            object_status = "existing"
        else:
            print(f"    object '{obj}' → candidate:entity_{obj} (score {object_score:.2f}) — candidate")
            resolved_object = f"candidate:{obj}"
            object_status = "candidate"

        resolved.append({
            **claim_data,
            "entity_resolution": {
                "subject": {
                    "original": subject,
                    "resolved": resolved_subject,
                    "status": subject_status,
                    "score": subject_score,
                    "matched_entity": subject_match
                },
                "object": {
                    "original": obj,
                    "resolved": resolved_object,
                    "status": object_status,
                    "score": object_score,
                    "matched_entity": object_match
                },
                "threshold": threshold,
                "note": "If identity uncertain, produce candidate entity rather than silently creating canonical one — never auto-merge"
            }
        })

    return resolved

def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Entity Resolution / Deduplication for STEMMA — Semantic Acquisition Pipeline")
    parser.add_argument("--claims", type=str, help="Path to claims JSON file for entity resolution (e.g., workflow/candidates/<doc_id>/semantic_claims.json)")
    parser.add_argument("--threshold", type=float, default=0.85, help="Similarity threshold for entity matching")
    parser.add_argument("--output", type=str, help="Output file for resolved claims")
    args = parser.parse_args()

    if args.claims:
        p = Path(args.claims)
        if not p.exists():
            print(f"Claims file not found: {p}", file=sys.stderr)
            return 1
        data = json.loads(p.read_text())
        resolved = resolve_claim_entities(data, threshold=args.threshold)

        if args.output:
            out_path = Path(args.output)
            out_path.write_text(json.dumps({"claims": resolved, "count": len(resolved)}, indent=2), encoding='utf-8')
            print(f"Wrote {len(resolved)} resolved claims to {out_path} — candidate entity if uncertain, never auto-merge")
        else:
            out_path = p.parent / f"{p.stem}_resolved.json"
            out_path.write_text(json.dumps({"claims": resolved, "count": len(resolved)}, indent=2), encoding='utf-8')
            print(f"Wrote {len(resolved)} resolved claims to {out_path}")

        print(f"\nNext: independent verification — python3 scripts/verify_claim.py --claims {args.output or out_path}")
        return 0

    # Original behavior — find duplicate entities
    entities = load_entities()
    if not entities:
        print("No entities found in export — run python3 scripts/validate.py first", file=sys.stderr)
        print("For semantic claims entity resolution, use --claims path/to/semantic_claims.json")
        return 0
    
    print(f"Loaded {len(entities)} entities from export")
    
    all_matches = []
    all_matches.extend(find_symbol_matches(entities))
    all_matches.extend(find_name_matches(entities))
    all_matches.extend(find_alias_matches(entities))
    all_matches.extend(find_notation_variants(entities))
    all_matches.extend(find_cross_domain_synonyms(entities))
    
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
    
    output = ROOT / "proposals" / "entity_resolution_matches.yaml"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(yaml.safe_dump({
        "generated_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "entity_count": len(entities),
        "matches": unique_matches,
    }, sort_keys=False, allow_unicode=True))
    
    print(f"\nMatches written to {output.relative_to(ROOT)}")
    print("Review each match and decide: confirmed_match / possible_duplicate / historical_alias / synonym / notation_variant / keep_separate")
    print("Never auto-merge — candidate entity if uncertain, never silently canonical")
    return 0


if __name__ == "__main__":
    sys.exit(main())