#!/usr/bin/env python3
"""
Proposal Generation — AI-Assisted Semantic Acquisition Pipeline — Evidence First-Class.

Every AI-generated candidate claim must retain precise provenance.
At minimum: source_id, document_hash, page, section, text_span
Where possible: character offsets, page coordinates, figure/table identifiers, equation identifiers, surrounding context, source version, acquisition timestamp, extraction pipeline version, model identifier, extraction prompt/version, extraction output, confidence/uncertainty metadata.

System must answer "Why does STEMMA contain this?" and trace answer back to original evidence.

AI output must be proposal, never directly canonical:
AI → proposal → verification → review → canonicalization
Example proposals/proposal-000123.yaml with proposal_id, source document_id document_hash, claim subject relation object, evidence page text_span, extraction model model_version pipeline_version prompt_version, verification status pending. Proposal is not canonical STEMMA knowledge.

Usage:
  python3 scripts/proposal_generate.py --doc-id <id>
  python3 scripts/proposal_generate.py --claims workflow/candidates/<doc_id>/semantic_claims_verified.json --doc-id <id>
  python3 scripts/proposal_generate.py --check-evidence

Proposals go to proposals/ and workflow/proposals/ — NOT canonical content/.
"""

import argparse
import json
import hashlib
import sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import yaml

def content_hash(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode('utf-8')).hexdigest()

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def load_version():
    try:
        data = yaml.safe_load((ROOT / "schema/VERSION.yaml").read_text())
        return data
    except:
        return {"schema_version": "unknown", "export_version": "unknown"}

def generate_proposals(claims_data, doc_id="test-doc"):
    """
    Generate proposals from verified claims with evidence first-class
    Each proposal contains: proposal_id, source document_id document_hash, claim subject relation object, evidence page text_span, extraction model model_version pipeline_version prompt_version, verification status pending
    Proposal is NOT canonical STEMMA knowledge
    """
    claims = claims_data.get("claims", []) if isinstance(claims_data, dict) else claims_data
    source_info = claims_data.get("source", {}) if isinstance(claims_data, dict) else {}
    extraction_info = claims_data.get("extraction", {}) if isinstance(claims_data, dict) else {}

    version_info = load_version()

    print(f"Generating proposals for {len(claims)} claims from doc {doc_id} — evidence first-class, NOT canonical")

    proposals = []
    for i, claim_data in enumerate(claims):
        claim = claim_data.get("claim", {})
        evidence = claim_data.get("evidence", {})
        extraction = claim_data.get("extraction", {})
        verification = claim_data.get("verification", {})
        conflict = claim_data.get("conflict", {})

        proposal_id = f"proposal-{i:06d}"
        source = claim_data.get("source", source_info)

        proposal = {
            "proposal_id": proposal_id,
            "schema_version": version_info.get("schema_version", "unknown"),
            "created_at": now_iso(),
            "source": {
                "document_id": source.get("document_id", doc_id),
                "document_hash": source.get("document_hash", evidence.get("document_hash", "sha256:unknown")),
                "source_id": source.get("source_id", evidence.get("source_id", "stemma:src.unknown"))
            },
            "claim": {
                "subject": claim.get("subject"),
                "relation": claim.get("relation"),
                "object": claim.get("object"),
                "conditions": claim.get("conditions", {}),
                "quantitative": claim.get("quantitative", {})
            },
            "evidence": {
                "source_id": evidence.get("source_id"),
                "document_hash": evidence.get("document_hash"),
                "page": evidence.get("page"),
                "section": evidence.get("section"),
                "text_span": evidence.get("text_span"),
                "char_offsets": evidence.get("char_offsets"),
                "page_coordinates": evidence.get("page_coordinates"),
                "figure_id": evidence.get("figure_id"),
                "surrounding_context": evidence.get("surrounding_context"),
                "source_version": evidence.get("source_version")
            },
            "extraction": {
                "model_provider": extraction.get("model_provider"),
                "model_id": extraction.get("model_id"),
                "model_version": extraction.get("model_version", "unknown"),
                "pipeline_version": extraction.get("pipeline_version", version_info.get("schema_version", "1.0.0")),
                "prompt_version": extraction.get("prompt_version", "v1"),
                "extraction_config": extraction.get("extraction_config", {}),
                "confidence": extraction.get("confidence"),
                "extraction_output": extraction.get("extraction_output", "")
            },
            "verification": {
                "status": verification.get("status", "pending"),
                "deterministic_checks": verification.get("deterministic_checks", []),
                "independent_model": verification.get("independent_model", {}),
                "source_corroboration": verification.get("source_corroboration", [])
            },
            "conflict": {
                "status": conflict.get("status", "no_conflict"),
                "competing_claims": conflict.get("competing_claims", []),
                "resolution": conflict.get("resolution")
            },
            "provenance": {
                "created_at": now_iso(),
                "created_by": "proposal_generate.py",
                "content_hash": content_hash(json.dumps(claim, sort_keys=True)),
                "extraction": extraction,
                "verification": verification
            },
            "destination": {
                "canonical": "content/ | connections/ | sources/",
                "note": "NOT written by this app. AI output must be proposal, never directly canonical. A human must verify and run scripts/review_entity.py + scripts/verify_all.py before any canonical change. Human review is final authority."
            },
            "workflow_status": "proposed",
            "human_review": {
                "required": True,
                "reviewer": None,
                "note": "",
                "at": None
            }
        }

        proposals.append(proposal)

    print(f"Generated {len(proposals)} proposals with evidence first-class — NOT canonical, must go through human review")

    for prop in proposals[:3]:
        print(f"  - {prop['proposal_id']}: {prop['claim']['subject']} {prop['claim']['relation']} {prop['claim']['object']} evidence={prop['evidence']['text_span'][:60]}... verification={prop['verification']['status']}")

    return proposals

def write_proposals(proposals, doc_id):
    """
    Write proposals to proposals/ and workflow/proposals/ — NOT canonical content/
    """
    proposals_dir = ROOT / "proposals"
    proposals_dir.mkdir(parents=True, exist_ok=True)

    workflow_proposals_dir = ROOT / "workflow/proposals"
    workflow_proposals_dir.mkdir(parents=True, exist_ok=True)

    written = []

    for prop in proposals:
        proposal_id = prop["proposal_id"]

        # Write to proposals/proposal-*.yaml (canonical proposal store, not canonical STEMMA knowledge)
        yaml_path = proposals_dir / f"{proposal_id}.yaml"
        # Use json for simplicity, but yaml would be more readable
        # We'll write yaml via yaml.dump
        try:
            yaml_path.write_text(yaml.safe_dump(prop, sort_keys=False, allow_unicode=True), encoding='utf-8')
        except:
            # Fallback to json if yaml fails
            yaml_path = proposals_dir / f"{proposal_id}.json"
            yaml_path.write_text(json.dumps(prop, indent=2), encoding='utf-8')

        # Also write to workflow/proposals/<slug>.proposal.yaml for webapp
        # Slug from subject
        subject = prop["claim"]["subject"].replace(":", "-").replace("/", "-")[:30]
        workflow_yaml_path = workflow_proposals_dir / f"{subject}.{proposal_id}.proposal.yaml"
        try:
            workflow_yaml_path.write_text(yaml.safe_dump(prop, sort_keys=False, allow_unicode=True), encoding='utf-8')
        except:
            workflow_yaml_path = workflow_proposals_dir / f"{subject}.{proposal_id}.proposal.json"
            workflow_yaml_path.write_text(json.dumps(prop, indent=2), encoding='utf-8')

        written.append(str(yaml_path))

    print(f"Wrote {len(written)} proposals to {proposals_dir} and {workflow_proposals_dir} — NOT canonical, must go through human review")

    return written

def check_evidence():
    """
    Check evidence must be first-class — every proposal must have precise provenance
    """
    print("Checking evidence must be first-class — every AI-generated candidate claim must retain precise provenance")

    proposals_dir = ROOT / "proposals"
    if not proposals_dir.exists():
        print(f"No proposals dir {proposals_dir} — no proposals yet, OK for CI")
        return 0

    proposals = list(proposals_dir.glob("*.yaml")) + list(proposals_dir.glob("*.json"))
    if not proposals:
        print(f"No proposals in {proposals_dir} — OK for CI")
        return 0

    fails = []
    for p in proposals:
        try:
            if p.suffix == ".yaml":
                data = yaml.safe_load(p.read_text())
            else:
                data = json.loads(p.read_text())

            evidence = data.get("evidence", {})
            # Check required evidence fields
            if not evidence.get("source_id"):
                fails.append(f"{p}: missing evidence.source_id")
            if not evidence.get("document_hash"):
                fails.append(f"{p}: missing evidence.document_hash")
            if not evidence.get("text_span"):
                fails.append(f"{p}: missing evidence.text_span")

            # Check extraction provenance
            extraction = data.get("extraction", {})
            if not extraction.get("model_id"):
                fails.append(f"{p}: missing extraction.model_id")
            if not extraction.get("pipeline_version"):
                fails.append(f"{p}: missing extraction.pipeline_version")

            # Check verification
            verification = data.get("verification", {})
            if not verification.get("status"):
                fails.append(f"{p}: missing verification.status")

        except Exception as e:
            fails.append(f"{p}: failed to parse: {e}")

    if fails:
        print(f"FAIL: Evidence first-class check failed — {len(fails)} failures:")
        for f in fails[:10]:
            print(f"  - {f}")
        return 1
    else:
        print(f"OK: Evidence first-class — all {len(proposals)} proposals have precise provenance source_id, document_hash, text_span, model_id, pipeline_version, verification status")
        return 0

def main():
    parser = argparse.ArgumentParser(description="Proposal Generation — Evidence First-Class — AI Output Must Be Proposal, Never Directly Canonical")
    parser.add_argument("--doc-id", type=str, help="Document ID from workflow/documents/<doc_id>/")
    parser.add_argument("--claims", type=str, help="Path to claims JSON file (verified claims with conflicts)")
    parser.add_argument("--output", type=str, help="Output dir for proposals")
    parser.add_argument("--check-evidence", action="store_true", help="Check evidence must be first-class — every proposal must have precise provenance")
    args = parser.parse_args()

    if args.check_evidence:
        return check_evidence()

    doc_id = args.doc_id or "test-doc"
    claims_data = None

    if args.claims:
        p = Path(args.claims)
        if not p.exists():
            print(f"Claims file not found: {p}", file=sys.stderr)
            return 1
        claims_data = json.loads(p.read_text())
        print(f"Loaded {len(claims_data.get('claims', []))} claims from {p}")
    elif args.doc_id:
        # Try to load from workflow/candidates/<doc_id>/semantic_claims_verified.json or similar
        wf_root = ROOT / "workflow"
        candidates_dir = wf_root / "candidates" / doc_id
        possible_files = [
            candidates_dir / "semantic_claims_verified.json",
            candidates_dir / "semantic_claims.json",
            candidates_dir / f"{doc_id}_verified.json"
        ]
        for pf in possible_files:
            if pf.exists():
                claims_data = json.loads(pf.read_text())
                print(f"Loaded claims from {pf}")
                break
        if not claims_data:
            print(f"No claims found for doc {doc_id} in {candidates_dir}", file=sys.stderr)
            print(f"Tried: {possible_files}")
            return 1
    else:
        parser.print_help()
        print("\nExample:")
        print("  python3 scripts/proposal_generate.py --doc-id <id>")
        print("  python3 scripts/proposal_generate.py --claims workflow/candidates/<doc_id>/semantic_claims_verified.json --doc-id <id>")
        print("  python3 scripts/proposal_generate.py --check-evidence")
        return 0

    proposals = generate_proposals(claims_data, doc_id=doc_id)
    written = write_proposals(proposals, doc_id)

    print(f"\nNext steps (HUMAN REVIEW is final authority):")
    print(f"  1. Open webapp: python3 webapp/server.py --port 8081")
    print(f"  2. View proposals in workflow/proposals/ — evidence first-class, verification status, conflicts")
    print(f"  3. Human explicitly edits markdown file — verification becomes easy")
    print(f"  4. Stage → validation runs including hitl_check.py")
    print(f"  5. Review: python3 scripts/review_entity.py accept <slug> --reviewer human:curator.001")
    print(f"  6. Canonicalize: python3 scripts/review_entity.py canonicalize <slug> --reviewer human:curator.001")
    print(f"  7. Verify: python3 scripts/verify_all.py + python3 scripts/verify_strong.py --quick")

    print(f"\nProposals are NOT canonical STEMMA knowledge — must go through verification, conflict analysis, human review, explicit canonicalization")
    print(f"System must answer Why does STEMMA contain this? and trace back to original evidence")

    return 0

if __name__ == "__main__":
    sys.exit(main())
