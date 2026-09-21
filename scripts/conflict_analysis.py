#!/usr/bin/env python3
"""
Conflict Analysis — AI-Assisted Semantic Acquisition Pipeline — Explicit Conflict Detection.

Scientific sources can disagree. Example Source A X property P=10, Source B P=12, do not force P=11 and do not allow LLM to arbitrarily choose one.
Instead Entity X with Source A → P=10 and Source B → P=12 → CONFLICT → investigation/review.

Canonical layer should represent uncertainty, conditions, measurement context, competing claims, historical values, source quality, unresolved conflicts rather than flattening literature into one unsupported value.

Usage:
  python3 scripts/conflict_analysis.py --claims workflow/candidates/<doc_id>/semantic_claims_verified.json
  python3 scripts/conflict_analysis.py --claims claims.json --output conflicts.json
  python3 scripts/conflict_analysis.py --demo-conflict (creates deliberate conflicting source P=10 vs P=12 for testing)

This is NOT canonical — conflict analysis result goes into proposal conflict field, then human review.
"""

import argparse
import json
import sys
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent

def analyze_conflicts(claims_data):
    """
    Explicit conflict detection:
    - Group claims by subject+relation+object (same scientific property)
    - If same property has different quantitative values from different sources → CONFLICT
    - Do not force average, do not allow LLM to arbitrarily choose one
    - Instead represent competing claims, uncertainty, conditions, measurement context, source quality, unresolved
    """
    claims = claims_data.get("claims", []) if isinstance(claims_data, dict) else claims_data

    print(f"Conflict analysis for {len(claims)} claims — explicit conflict detection, do not force average")

    # Group by subject+relation+object
    grouped = defaultdict(list)
    for c in claims:
        claim = c.get("claim", {})
        key = (claim.get("subject"), claim.get("relation"), claim.get("object"))
        grouped[key].append(c)

    conflicts = []
    no_conflicts = []
    all_competing = []

    for key, group in grouped.items():
        subject, relation, obj = key
        print(f"\nAnalyzing {subject} {relation} {obj}: {len(group)} sources")

        # Extract quantitative values
        values_with_source = []
        for g in group:
            quant = g.get("claim", {}).get("quantitative", {})
            value = quant.get("value")
            unit = quant.get("unit")
            conditions = g.get("claim", {}).get("conditions", {})
            source_id = g.get("source", {}).get("source_id") or g.get("evidence", {}).get("source_id")
            source_quality = "unknown"  # Could be from source registry
            if value is not None:
                values_with_source.append({
                    "source_id": source_id,
                    "value": value,
                    "unit": unit,
                    "conditions": conditions,
                    "source_quality": source_quality,
                    "claim_id": g.get("claim_id")
                })

        if len(values_with_source) <= 1:
            print(f"  No conflict — single source or no quantitative values")
            no_conflicts.append({
                "key": key,
                "status": "no_conflict",
                "claims": group
            })
            continue

        # Check if values agree
        values = [v["value"] for v in values_with_source]
        units = [v["unit"] for v in values_with_source]

        # If values differ → CONFLICT
        if len(set(values)) > 1:
            print(f"  CONFLICT detected: values {values} from sources {[v['source_id'] for v in values_with_source]} — do not force average {sum(values)/len(values)}")
            print(f"  Instead: Entity {subject} — Source A → P={values[0]}, Source B → P={values[1]} → CONFLICT → investigation/review")

            conflict = {
                "key": {
                    "subject": subject,
                    "relation": relation,
                    "object": obj
                },
                "status": "conflict",
                "competing_claims": values_with_source,
                "values": values,
                "units": units,
                "message": f"CONFLICT: {subject} {relation} {obj} has competing values {values} from different sources — do not force average, investigation/review required",
                "resolution": None,
                "claims": group
            }
            conflicts.append(conflict)
            all_competing.extend(values_with_source)
        else:
            # Values agree
            print(f"  No conflict — values agree: {values[0]} from {len(values_with_source)} sources")
            no_conflicts.append({
                "key": key,
                "status": "no_conflict",
                "values": values,
                "claims": group
            })

    # Also check for condition conflicts — same subject+relation+object but different conditions
    # Example: ideal gas at constant temperature vs at constant pressure — different conditions, not conflict but different scope
    print(f"\nConflict analysis summary: {len(conflicts)} conflicts, {len(no_conflicts)} no conflicts out of {len(grouped)} unique properties")

    for conf in conflicts:
        print(f"  CONFLICT: {conf['key']} values {conf['values']} — competing claims: {conf['competing_claims']}")

    return {
        "total_claims": len(claims),
        "unique_properties": len(grouped),
        "conflicts": conflicts,
        "no_conflicts": no_conflicts,
        "conflict_count": len(conflicts),
        "no_conflict_count": len(no_conflicts),
        "all_competing_claims": all_competing,
        "summary": {
            "total": len(claims),
            "conflicts": len(conflicts),
            "no_conflicts": len(no_conflicts),
            "requires_human_review": len(conflicts) > 0
        }
    }

def demo_conflict():
    """
    Creates deliberate conflicting source P=10 vs P=12 for testing vertical slice
    Example from proposal: Source A X property P=10, Source B P=12 → CONFLICT
    """
    print("Creating demo conflict: Source A X property P=10, Source B P=12 → CONFLICT (deliberate for testing)")

    claims = [
        {
            "claim_id": "claim.000001",
            "source": {"document_id": "doc-a", "document_hash": "sha256:aaa", "source_id": "stemma:src.paper-a"},
            "claim": {
                "subject": "ionic_conductivity",
                "relation": "has_value",
                "object": "material_x",
                "conditions": {"temperature": {"value": 25, "unit": "°C"}},
                "quantitative": {"value": 10, "unit": "mS/cm"}
            },
            "evidence": {
                "source_id": "stemma:src.paper-a",
                "document_hash": "sha256:aaa",
                "page": 1,
                "text_span": "Material X has ionic conductivity 10 mS/cm at 25°C",
                "surrounding_context": "Material X was measured at 25°C and showed 10 mS/cm"
            },
            "extraction": {"model_provider": "openrouter", "model_id": "deepseek/deepseek-r1:free", "pipeline_version": "1.0.0", "prompt_version": "v1"}
        },
        {
            "claim_id": "claim.000002",
            "source": {"document_id": "doc-b", "document_hash": "sha256:bbb", "source_id": "stemma:src.paper-b"},
            "claim": {
                "subject": "ionic_conductivity",
                "relation": "has_value",
                "object": "material_x",
                "conditions": {"temperature": {"value": 25, "unit": "°C"}},
                "quantitative": {"value": 12, "unit": "mS/cm"}
            },
            "evidence": {
                "source_id": "stemma:src.paper-b",
                "document_hash": "sha256:bbb",
                "page": 2,
                "text_span": "Material X exhibits ionic conductivity of 12 mS/cm at 25°C",
                "surrounding_context": "In contrast to previous work, Material X showed 12 mS/cm at 25°C"
            },
            "extraction": {"model_provider": "openrouter", "model_id": "deepseek/deepseek-r1:free", "pipeline_version": "1.0.0", "prompt_version": "v1"}
        }
    ]

    result = analyze_conflicts({"claims": claims})

    print("\nDemo conflict result:")
    print(json.dumps(result, indent=2))

    print("\nExpected: CONFLICT detected, do not force P=11, do not allow LLM to arbitrarily choose one")
    print("Instead: Entity X — Source A → P=10, Source B → P=12 → CONFLICT → investigation/review")
    print("Canonical layer should represent uncertainty, conditions, measurement context, competing claims, historical values, source quality, unresolved conflicts")

    return result

def main():
    parser = argparse.ArgumentParser(description="Conflict Analysis — Explicit Conflict Detection — Do Not Force Average")
    parser.add_argument("--claims", type=str, help="Path to claims JSON file (verified claims)")
    parser.add_argument("--output", type=str, help="Output file for conflict analysis")
    parser.add_argument("--demo-conflict", action="store_true", help="Create demo conflict P=10 vs P=12 deliberate for testing vertical slice")
    args = parser.parse_args()

    if args.demo_conflict:
        result = demo_conflict()
        if args.output:
            Path(args.output).write_text(json.dumps(result, indent=2), encoding='utf-8')
            print(f"Wrote demo conflict to {args.output}")
        else:
            out_path = ROOT / "reports/conflict-demo.json"
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(json.dumps(result, indent=2), encoding='utf-8')
            print(f"Wrote demo conflict to {out_path}")
        return 0

    if not args.claims:
        parser.print_help()
        print("\nExample:")
        print("  python3 scripts/conflict_analysis.py --claims workflow/candidates/<doc_id>/semantic_claims_verified.json")
        print("  python3 scripts/conflict_analysis.py --demo-conflict (creates P=10 vs P=12 deliberate)")
        return 0

    p = Path(args.claims)
    if not p.exists():
        print(f"Claims file not found: {p}", file=sys.stderr)
        return 1

    data = json.loads(p.read_text())
    result = analyze_conflicts(data)

    if args.output:
        out_path = Path(args.output)
        out_path.write_text(json.dumps(result, indent=2), encoding='utf-8')
        print(f"Wrote conflict analysis to {out_path} — {result['conflict_count']} conflicts, {result['no_conflict_count']} no conflicts")
    else:
        out_path = p.parent / f"{p.stem}_conflicts.json"
        out_path.write_text(json.dumps(result, indent=2), encoding='utf-8')
        print(f"Wrote conflict analysis to {out_path}")

    print(json.dumps(result["summary"], indent=2))

    if result["conflict_count"] > 0:
        print(f"\nCONFLICTS detected: {result['conflict_count']} — requires human review, do not force average, do not allow LLM to arbitrarily choose")
        print(f"Next: human review where required → explicit canonicalization with uncertainty, conditions, measurement context, competing claims")
        # For CI, conflicts are INFO not FAIL — they require human review, not automatic failure
        # But we log that human review is required
        print(f"INFO: {result['conflict_count']} conflicts require human review — not FAIL, but must be investigated")

    print(f"\nNext steps:")
    print(f"  1. Proposal generation: python3 scripts/proposal_generate.py --claims {args.claims}")
    print(f"  2. Human review: open webapp and investigate conflicts")
    print(f"  3. Canonicalization with uncertainty, conditions, competing claims")

    return 0

if __name__ == "__main__":
    sys.exit(main())
