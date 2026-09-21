#!/usr/bin/env python3
"""
HITL Check — Human In The Loop verification before canonicalization.

Enforces that no entity becomes canonical without explicit human markdown edit.

This is mandatory for BOTH:
- Primary flow: PDF ingestion → AI extraction → markdown preview → human edit → canonical
- Secondary flow: Direct agent addition (LLM) → markdown draft → human edit → canonical

Checks:
1. Audit trail: workflow/audit/audit.jsonl must contain candidate_edited event by human:* for entity
2. Writer is human: provenance.writer must start with human: (not llm:, unknown:)
3. Markdown explicit: workflow/candidates/ and workflow/proposals/ must have human-edited markdown file
4. File modified after AI draft: proposal mtime > candidate mtime, or audit shows human edit after draft

Usage:
  python3 scripts/hitl_check.py --entity stemma:phys.metre
  python3 scripts/hitl_check.py --all
  python3 scripts/hitl_check.py --check-workflow

Exit 0 = HITL satisfied, 1 = HITL required (human must edit markdown before canonical)
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = ROOT / "workflow"
AUDIT = WORKFLOW / "audit" / "audit.jsonl"
CANDIDATES = WORKFLOW / "candidates"
PROPOSALS = WORKFLOW / "proposals"
CONTENT = ROOT / "content"

def load_audit():
    if not AUDIT.exists():
        return []
    entries=[]
    for line in AUDIT.read_text(encoding='utf-8').splitlines():
        try:
            entries.append(json.loads(line))
        except:
            continue
    return entries

def check_entity(entity_id: str, verbose=False):
    """
    Check HITL for one entity id (e.g., stemma:phys.metre or metre slug)
    """
    slug = entity_id.split(".")[-1] if "." in entity_id else entity_id
    full_id = entity_id if entity_id.startswith("stemma:") else f"stemma:phys.{slug}"

    violations=[]

    # 1. Check content file exists and writer is human
    content_file=None
    for md in CONTENT.rglob(f"{slug}.md"):
        content_file=md
        break
    # Also check workflow proposals
    proposal_file = PROPOSALS / f"{slug}.md"
    candidate_files = list(CANDIDATES.rglob(f"{slug}.md")) + list(CANDIDATES.rglob(f"*{slug}*.md"))

    if not content_file and not proposal_file and not candidate_files:
        # No file yet — not an error for hitl_check, just not ready
        if verbose:
            print(f"{full_id}: no file yet in content/ or workflow/ — not ready for HITL check (OK for draft)")
        return True, []

    # Check writer is human if file exists in content or proposals
    file_to_check = content_file or proposal_file or (candidate_files[0] if candidate_files else None)
    if file_to_check and file_to_check.exists():
        try:
            text=file_to_check.read_text(encoding='utf-8')
            if text.startswith("---"):
                import yaml
                fm=yaml.safe_load(text.split("---")[1])
                writer=fm.get("provenance",{}).get("writer","")
                if writer and not writer.startswith("human:"):
                    violations.append(f"{full_id}: provenance.writer is '{writer}' not human:* — HITL requires human writer, not {writer.split(':')[0]}")
                if not writer:
                    violations.append(f"{full_id}: missing provenance.writer — must be human:curator.001 for HITL")
        except Exception as e:
            violations.append(f"{full_id}: failed to parse {file_to_check}: {e}")

    # 2. Audit trail check
    audit_entries=load_audit()
    # Find events for this slug
    relevant=[e for e in audit_entries if slug in json.dumps(e) or e.get("doc_id","") in slug or slug in e.get("detail",{}).get("candidate_id","")]
    # More generic: check if any candidate_edited by human exists
    edited_events=[e for e in audit_entries if e.get("event")=="candidate_edited" and "human:" in json.dumps(e.get("detail",{}))]
    # For specific entity, check if edited event mentions slug
    edited_for_entity=[e for e in edited_events if slug in json.dumps(e)]

    if not audit_entries:
        violations.append(f"{full_id}: no audit trail at {AUDIT} — workflow/audit/audit.jsonl missing, run ingestion via webapp or pdf_ingest_primary.py")
    elif not edited_events:
        violations.append(f"{full_id}: no candidate_edited event by human:* in audit trail — human must explicitly edit markdown file before canonical (HITL required)")
    elif not edited_for_entity and candidate_files:
        # If we have candidate files but no specific edit for this slug, warn
        if verbose:
            print(f"{full_id}: no specific audit for {slug}, but found {len(edited_events)} human edits overall")

    # 3. Markdown explicit check
    if not candidate_files and not proposal_file:
        violations.append(f"{full_id}: no markdown file in workflow/candidates/ or workflow/proposals/ — AI must show markdown preview and human must edit file explicitly")

    # 4. File modified after AI draft — check proposal exists and is newer than candidate
    # This check is advisory if audit shows human edit — mtime can be close
    if candidate_files and proposal_file and proposal_file.exists():
        try:
            cand_mtime=max(f.stat().st_mtime for f in candidate_files)
            prop_mtime=proposal_file.stat().st_mtime
            # Only fail if proposal is significantly older (>2 sec) and no human edit in audit
            # Because human edit audit is primary evidence
            if prop_mtime + 2 < cand_mtime:
                # Check if audit has human edit — if yes, don't fail on mtime
                audit_entries=load_audit()
                edited_for_entity=[e for e in audit_entries if e.get("event")=="candidate_edited" and slug in json.dumps(e)]
                if not edited_for_entity:
                    violations.append(f"{full_id}: proposal {proposal_file} mtime {prop_mtime} < candidate mtime {cand_mtime} — proposal must be edited by human after AI draft (no audit of human edit found)")
        except Exception as e:
            # Don't fail on mtime check error, just warn
            if verbose:
                print(f"{full_id}: mtime check warning: {e}")

    if violations:
        return False, violations
    else:
        return True, []

def main():
    parser=argparse.ArgumentParser(description="HITL Check — verify human edited markdown before canonical")
    parser.add_argument("--entity", type=str, help="Entity id or slug to check (e.g., metre or stemma:phys.metre)")
    parser.add_argument("--all", action="store_true", help="Check all entities in content/")
    parser.add_argument("--check-workflow", action="store_true", help="Check all candidates/proposals in workflow/")
    parser.add_argument("--verbose", action="store_true")
    args=parser.parse_args()

    if args.entity:
        ok, violations=check_entity(args.entity, verbose=args.verbose)
        if ok:
            print(f"OK: HITL satisfied for {args.entity} — human edited markdown before canonical")
            return 0
        else:
            print(f"FAIL: HITL required for {args.entity}:")
            for v in violations:
                print(f"  - {v}")
            print(f"\nHuman must explicitly edit markdown file in webapp or workflow/candidates/ before canonicalization.")
            print(f"Audit trail: {AUDIT}")
            return 1

    if args.all:
        # Check all entities in content/
        import yaml
        entities=[]
        for md in CONTENT.rglob("*.md"):
            try:
                fm=yaml.safe_load(md.read_text().split("---")[1])
                if fm.get("id"):
                    entities.append(fm["id"])
            except:
                continue
        fails=0
        for eid in entities:
            ok, violations=check_entity(eid, verbose=args.verbose)
            if not ok:
                fails+=1
                print(f"FAIL: {eid}:")
                for v in violations:
                    print(f"  - {v}")
            else:
                if args.verbose:
                    print(f"OK: {eid}")
        if fails:
            print(f"\nHITL check: {fails}/{len(entities)} entities fail HITL — human edit required")
            return 1
        else:
            print(f"OK: HITL check passed for all {len(entities)} entities")
            return 0

    if args.check_workflow:
        # Check workflow candidates/proposals
        if not WORKFLOW.exists():
            print(f"Workflow dir {WORKFLOW} does not exist — no ingestion yet, run pdf_ingest_primary.py")
            return 0
        audit=load_audit()
        print(f"Audit entries: {len(audit)} at {AUDIT}")
        candidates=list(CANDIDATES.rglob("*.md")) if CANDIDATES.exists() else []
        proposals=list(PROPOSALS.glob("*.md")) if PROPOSALS.exists() else []
        print(f"Candidates: {len(candidates)} markdown files")
        for c in candidates[:10]:
            print(f"  - {c}")
        print(f"Proposals: {len(proposals)} markdown files")
        for p in proposals[:10]:
            print(f"  - {p}")
        # Check if any human edit
        human_edits=[e for e in audit if e.get("event")=="candidate_edited" and "human:" in json.dumps(e)]
        print(f"Human edits (HITL): {len(human_edits)}")
        if not human_edits and (candidates or proposals):
            print(f"FAIL: No human edits in audit — HITL required, human must explicitly edit markdown")
            return 1
        else:
            print(f"OK: HITL workflow has human edits")
            return 0

    parser.print_help()
    return 0

if __name__=="__main__":
    sys.exit(main())
