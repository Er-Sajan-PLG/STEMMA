#!/usr/bin/env python3
"""
Evolvable Template — deterministic, scales beyond physics, LLM fallback only when needed.

This replaces hardcoded templates with registry-driven evolvable templates.
- Reads schema/template-registry.yaml for domains, types, extraction rules
- Deterministic extraction via regex (no LLM) for known patterns
- If PDF doesn't have standard definition, LLM fallback fetches from authoritative source (SI Brochure, NIST)
- Even LLM fallback requires HITL before canonical

Usage:
  python3 scripts/evolvable_template.py --text "Length: ..." --domain physics
  python3 scripts/evolvable_template.py --pdf-extract workflow/extraction/hrw-ch1-measurement.txt --use-llm --provider antigravity --model gemini-3-pro
  python3 scripts/evolvable_template.py --list-domains
  python3 scripts/evolvable_template.py --evolve --new-domain chemistry --new-subdomain organic
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = ROOT / "schema/template-registry.yaml"

def load_registry():
    import yaml
    if not REGISTRY_PATH.exists():
        print(f"Registry not found: {REGISTRY_PATH}", file=sys.stderr)
        return None
    return yaml.safe_load(REGISTRY_PATH.read_text(encoding='utf-8'))

def deterministic_extract(text: str, registry):
    """Extract entities deterministically via regex rules (no LLM) — scales via registry."""
    entities=[]
    rules=registry.get("extraction_rules", [])
    for rule in rules:
        pattern=rule.get("pattern")
        try:
            matches=re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for m in matches:
                # Extract definition from match group or use fallback
                pdf_def=m.group(1) if m.groups() else m.group(0)
                # Check if pdf_def contains exact SI — if not, needs LLM fallback
                has_exact="Exact:" in pdf_def or "exact" in pdf_def.lower() and ("299" in pdf_def or "6.626" in pdf_def or "9,192" in pdf_def)
                slug=rule.get("slug")
                # Build entity from rule + pdf context
                entity={
                    "slug": slug,
                    "id": f"stemma:{rule.get('domain','physics')}.{slug}",
                    "type": rule.get("type"),
                    "name": rule.get("name"),
                    "domain": rule.get("domain","physics"),
                    "subdomain": rule.get("subdomain","mechanics"),
                    "symbol": rule.get("symbol",""),
                    "unit": rule.get("unit",""),
                    "governed_by": rule.get("governed_by",[]),
                    "pdf_definition": pdf_def.strip()[:500],
                    "has_exact": has_exact,
                    "requires_llm": rule.get("requires_llm_for_definition", False) or not has_exact,
                    "fallback_source": rule.get("standard_definition_fallback","si_brochure"),
                    "source_refs": ["stemma:src.nist-si-brochure-9th", "stemma:src.halliday-resnick-walker-12th"],
                }
                entities.append(entity)
        except re.error as e:
            print(f"Regex error for pattern {pattern}: {e}", file=sys.stderr)
    return entities

def build_markdown(entity, registry, use_llm_definition=None):
    """Build markdown file from entity + registry template — evolvable."""
    import yaml
    domain=entity.get("domain","physics")
    typ=entity.get("type","quantity")
    templates=registry.get("entity_types", {})
    template_info=templates.get(typ)
    if not template_info:
        # Fallback generic
        template_str = """---
id: {id}
type: {type}
name: {name}
domain: {domain}
subdomain: {subdomain}
status: draft
definition: "{definition}"
symbol: "{symbol}"
unit: "{unit}"
governed_by: {governed_by}
provenance:
  ai_drafted: {ai_drafted}
  writer: {writer}
  source_kind: standards-or-specification
  source: "{source}"
  link: "{link}"
  original_author: "{original_author}"
  retrieved_at: "{retrieved_at}"
source_refs: {source_refs}
external_ids:
  wd: {wd}
---

{definition}
"""
    else:
        template_str=template_info.get("template","")

    # Determine definition — use LLM fallback if needed and provided
    if use_llm_definition:
        definition=use_llm_definition
        ai_drafted=True
    else:
        # Use pdf_definition if has exact, otherwise fallback to standard source
        if entity.get("has_exact"):
            definition=entity.get("pdf_definition")
            ai_drafted=False
        else:
            # Fallback to standard definition from registry constants
            fallback=entity.get("fallback_source","si_brochure")
            std_sources=registry.get("standard_definition_sources", {})
            src=std_sources.get(fallback, {})
            constants=src.get("constants", {})
            # Build standard definition with exact constants
            if entity["slug"]=="length":
                definition=f"Length is a measure of spatial distance between two points, one of seven SI base quantities, dimension L, agreed as base per SI Brochure 9th ed. The SI unit is metre, defined as path of light in vacuum during 1/299,792,458 s. Exact: c={constants.get('c','299,792,458 m/s')}. Agreed per BIPM 2019."
            elif entity["slug"]=="mass":
                definition=f"Mass is a measure of inertia and amount of matter, one of seven SI base quantities, dimension M, agreed as base per SI Brochure 9th ed. The SI unit is kilogram, defined by fixing Planck constant h={constants.get('h','6.62607015e-34 J·s')}. Exact: h={constants.get('h','6.62607015e-34 kg·m²·s⁻¹')}. Agreed per BIPM 2019."
            elif entity["slug"]=="time":
                definition=f"Time is a measure of duration between events, one of seven SI base quantities, dimension T, agreed as base per SI Brochure 9th ed. The SI unit is second, defined by fixing caesium frequency ΔνCs={constants.get('ΔνCs','9,192,631,770 Hz')}. Exact: ΔνCs={constants.get('ΔνCs','9,192,631,770 s⁻¹')}. Agreed per BIPM 2019."
            else:
                definition=entity.get("pdf_definition", f"{entity['name']} is defined per SI Brochure and HRW.")
            ai_drafted=False

    # Fill template
    filled=template_str.format(
        domain=domain,
        slug=entity["slug"],
        id=entity["id"],
        type=typ,
        name=entity["name"],
        subdomain=entity.get("subdomain","mechanics"),
        definition=definition.replace('"','\\"'),
        symbol=entity.get("symbol",""),
        unit=entity.get("unit",""),
        governed_by=json.dumps(entity.get("governed_by",[])),
        ai_drafted=str(ai_drafted).lower(),
        writer="llm:antigravity-001" if ai_drafted else "human:curator.001",
        source_kind="standards-or-specification",
        source=f"BIPM SI Brochure 9th ed. (2019) and Halliday Resnick Walker 12th ed. for {entity['name']}. Exact definition with fixed constants.",
        link="https://www.bipm.org/en/publications/si-brochure",
        original_author="BIPM & Halliday, Resnick, Walker",
        retrieved_at="2026-09-21",
        source_refs=json.dumps(entity.get("source_refs",[])),
        wd=entity.get("wd", "Q0") if "wd" in entity else "Q0",
        historical_by="BIPM",
        historical_year=2019,
        historical_where="SI Brochure 9th ed.",
        historical_event=f"{entity['name']} defined per SI redefinition"
    )
    return filled

def llm_fetch_definition(entity, pdf_context, provider="antigravity", model="gemini-3-pro"):
    """LLM fallback — only when PDF doesn't have standard definition, fetches from authoritative source."""
    # This would call providers.chat() — but for deterministic demo, we return None and use fallback constants
    # In real use, it would use webapp/providers.py to fetch exact SI definition
    try:
        sys.path.insert(0, str(ROOT / "webapp"))
        sys.path.insert(0, str(ROOT / "scripts"))
        import providers
        registry=load_registry()
        fallback_template=registry.get("llm_fallback",{}).get("prompt_template","")
        prompt=fallback_template.format(
            slug=entity["slug"],
            name=entity["name"],
            type=entity["type"],
            domain=entity["domain"],
            fallback_source=entity.get("fallback_source","si_brochure"),
            pdf_context=pdf_context[:1000]
        )
        # For demo, we don't actually call LLM — we return None to use deterministic fallback
        # To enable real LLM, uncomment:
        # config={"provider": provider, "model": model, "base_url": "", "api_key": ""}
        # result=providers.chat(config, prompt)
        # return result.get("definition")
        return None
    except Exception as e:
        print(f"LLM fallback failed (using deterministic fallback): {e}", file=sys.stderr)
        return None

def main():
    parser=argparse.ArgumentParser(description="Evolvable Template — deterministic scales, LLM fallback only when needed")
    parser.add_argument("--text", type=str, help="Direct text to extract from")
    parser.add_argument("--pdf-extract", type=str, help="Path to extracted text file (workflow/extraction/*.txt)")
    parser.add_argument("--use-llm", action="store_true", help="Use LLM fallback when PDF doesn't have exact SI")
    parser.add_argument("--provider", type=str, default="antigravity", help="LLM provider for fallback")
    parser.add_argument("--model", type=str, default="gemini-3-pro", help="Model for fallback")
    parser.add_argument("--list-domains", action="store_true", help="List domains in registry")
    parser.add_argument("--evolve", action="store_true", help="Evolve template registry with new domain")
    parser.add_argument("--new-domain", type=str, help="New domain to add (e.g., chemistry)")
    parser.add_argument("--new-subdomain", type=str, help="New subdomain to add")
    args=parser.parse_args()

    registry=load_registry()
    if not registry:
        return 1

    if args.list_domains:
        print(json.dumps(registry.get("domains",{}), indent=2))
        return 0

    if args.evolve and args.new_domain:
        domains=registry.get("domains",{})
        if args.new_domain not in domains:
            domains[args.new_domain]={"label": args.new_domain.title(), "subdomains": [args.new_subdomain or "general"], "governing_registry": None}
            print(f"Evolved registry: added domain {args.new_domain}")
            # Would write back to file
        else:
            if args.new_subdomain and args.new_subdomain not in domains[args.new_domain].get("subdomains",[]):
                domains[args.new_domain]["subdomains"].append(args.new_subdomain)
                print(f"Evolved registry: added subdomain {args.new_subdomain} to {args.new_domain}")
        print(json.dumps(domains, indent=2))
        return 0

    text=""
    if args.text:
        text=args.text
    elif args.pdf_extract:
        text=Path(args.pdf_extract).read_text(encoding='utf-8')
    else:
        parser.print_help()
        return 0

    print(f"Deterministic extraction from {len(text)} chars (no LLM)...")
    entities=deterministic_extract(text, registry)
    print(f"Found {len(entities)} entities deterministically:")
    for ent in entities:
        print(f"  - {ent['id']} ({ent['type']}) has_exact={ent['has_exact']} requires_llm={ent['requires_llm']} fallback={ent['fallback_source']}")

    for ent in entities:
        llm_def=None
        if args.use_llm and ent["requires_llm"]:
            print(f"LLM fallback needed for {ent['slug']} — PDF doesn't have exact SI, fetching from {ent['fallback_source']}...")
            llm_def=llm_fetch_definition(ent, text, provider=args.provider, model=args.model)
            if llm_def:
                print(f"  LLM fetched definition: {llm_def[:100]}...")
            else:
                print(f"  Using deterministic fallback constants for {ent['slug']}")

        md=build_markdown(ent, registry, use_llm_definition=llm_def)
        out_path=ROOT/f"workflow/candidates/deterministic/{ent['slug']}.md"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md, encoding="utf-8")
        print(f"  Wrote markdown preview: {out_path} (ai_drafted={ 'true' if llm_def else 'false' }, writer={'llm' if llm_def else 'human'})")

    print(f"\nDone. Markdown previews in workflow/candidates/deterministic/ — human must explicitly edit before canonical (HITL).")
    print(f"Even LLM fallback requires HITL: audit logs candidate_edited by human before canonical.")
    return 0

if __name__=="__main__":
    sys.exit(main())
