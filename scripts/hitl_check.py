#!/usr/bin/env python3
"""
HITL Check — Human In The Loop verification before canonicalization.

Enforces that no entity becomes canonical without explicit human authorship
AND review. SCOPE IS ALL DATA (owner ruling 2026-10-01, UNRES-STEMMA-HITL-002):
the check covers content/ (every entity type) and connections/, not only the
git-ignored workflow/ staging area.

This is mandatory for BOTH:
- Primary flow: PDF ingestion → AI extraction → markdown preview → human edit → canonical
- Secondary flow: Direct agent addition (LLM) → markdown draft → human edit → canonical

Gate semantics (a STATUS gate, not a blanket gate):
- Entities whose status is NOT in {human_reviewed, canonical} are EXEMPT. A draft
  is allowed to be LLM-written — that is what draft means.
- Entities at human_reviewed/canonical MUST satisfy, for the entity's own file:
  (1) provenance.writer resolves to an ACTIVE INDIVIDUAL HUMAN in
      schema/agent-registry.yaml (a bare `human:` prefix is not enough — H1);
  (2) a human reviewer is corroborated either by a candidate_edited audit event
      for this entity's markdown (primary/PDF flow) or by the entity's own
      declared human review metadata (secondary direct-authoring flow) — a
      rubber-stamped LLM draft is forbidden by design.

Usage:
  python3 scripts/hitl_check.py --entity stemma:phys.metre
  python3 scripts/hitl_check.py --all
  python3 scripts/hitl_check.py --check-workflow

Exit 0 = HITL satisfied (or nothing canonical yet), 1 = HITL required
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
AGENTS = ROOT / "schema" / "agent-registry.yaml"


def registered_humans() -> set[str]:
    """Active individual humans in the agent registry. Empty on any error, so
    every human check fails closed rather than trusting a `human:` prefix."""
    import yaml
    try:
        data = yaml.safe_load(AGENTS.read_text(encoding="utf-8")) or {}
    except Exception:
        return set()
    return {a["id"] for a in data.get("agents") or []
            if isinstance(a, dict) and a.get("class") == "human"
            and a.get("status") == "active" and a.get("type") != "institution"}


def human_edit_events(audit: list, humans: set[str], slug: str | None = None) -> list:
    """candidate_edited events attributed to a registered human; with `slug`,
    only events whose edited markdown file is exactly `<slug>.md`."""
    out = []
    for e in audit:
        if e.get("event") != "candidate_edited":
            continue
        detail = e.get("detail") or {}
        if detail.get("writer") not in humans:
            continue
        if slug is not None and Path(str(detail.get("markdown_path") or "")).name != f"{slug}.md":
            continue
        out.append(e)
    return out

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

REVIEWED_STATUSES = {"human_reviewed", "canonical"}


def _find_content_file(slug: str):
    """Locate the entity's markdown by exact filename stem (never a glob that
    could match a sibling like centimetre.md for metre)."""
    if not CONTENT.exists():
        return None
    for md in sorted(CONTENT.rglob(f"{slug}.md")):
        return md
    return None


def check_entity(entity_id: str, verbose=False):
    """
    Check HITL for one entity id (e.g., stemma:phys.metre or a bare slug).

    Status-aware: only human_reviewed/canonical entities are gated. Drafts and
    machine_validated entities are exempt (they are allowed to be LLM-written).
    """
    slug = entity_id.split(".")[-1] if "." in entity_id else entity_id
    full_id = entity_id if entity_id.startswith("stemma:") else f"stemma:phys.{slug}"

    violations = []

    # Locate the entity's content markdown by exact stem.
    content_file = _find_content_file(slug)
    proposal_file = PROPOSALS / f"{slug}.md"
    if not proposal_file.exists():
        proposal_file = None
    candidate_files = sorted(CANDIDATES.rglob(f"{slug}.md"))

    if not content_file and not proposal_file and not candidate_files:
        # No file yet — not an error for hitl_check, just not ready.
        if verbose:
            print(f"{full_id}: no file yet in content/ or workflow/ — not ready for HITL check (OK)")
        return True, []

    # Parse frontmatter from the content file to learn status + provenance.
    fm = {}
    if content_file is not None:
        try:
            import yaml
            text = content_file.read_text(encoding="utf-8")
            if text.startswith("---"):
                fm = yaml.safe_load(text.split("---")[1]) or {}
        except Exception as e:
            violations.append(f"{full_id}: failed to parse {content_file}: {e}")
            return False, violations

    status = fm.get("status")
    # STATUS GATE (content only): a content entity whose status is not
    # human_reviewed/canonical is exempt — a draft is allowed to be LLM-written.
    # Workflow staging files (candidates/proposals) are ALWAYS writer-gated,
    # because they are prospective canonical objects regardless of any status
    # field: the whole point of the staging area is that a human owns the file
    # before it graduates. Owner ruling 2026-10-01 (UNRES-STEMMA-HITL-002).
    if content_file is not None and status not in REVIEWED_STATUSES:
        if verbose:
            print(f"{full_id}: status '{status}' — not review-gated (draft may be LLM-written), OK")
        return True, []

    # ---- Gated path ----
    humans = registered_humans()

    # 1. Writer must be a registered active individual human. Read it from the
    #    content file when present, else from the workflow staging file.
    writer = ""
    if content_file is not None:
        writer = (fm.get("provenance") or {}).get("writer", "")
    staging_file = None
    if proposal_file is not None:
        staging_file = proposal_file
    elif candidate_files:
        staging_file = candidate_files[0]

    if not writer and staging_file is not None:
        try:
            import yaml
            sfm = yaml.safe_load(staging_file.read_text(encoding="utf-8").split("---")[1]) or {}
            writer = (sfm.get("provenance") or {}).get("writer", "")
            if not fm:
                fm = sfm  # workflow-only: treat staging frontmatter as the record
        except Exception as e:
            violations.append(f"{full_id}: failed to parse {staging_file}: {e}")
            return False, violations

    if not writer:
        violations.append(f"{full_id}: missing provenance.writer — must be a registered human for HITL")
    elif writer not in humans:
        violations.append(
            f"{full_id}: provenance.writer is '{writer}', not an active human in "
            f"{AGENTS.relative_to(ROOT)} — HITL requires a registered human writer")

    # 2. Human review corroboration. Two accepted forms of evidence:
    #    (a) audit trail: a candidate_edited event by a registered human for
    #        THIS entity's markdown (primary PDF flow / secondary LLM flow), or
    #    (b) declared review metadata authored by a human (direct-authoring flow:
    #        a human writing the file IS the review; they need not "edit a draft").
    audit_entries = load_audit()
    audit_edited_for_entity = human_edit_events(audit_entries, humans, slug)

    prov = fm.get("provenance") or {}
    reviewer = prov.get("reviewer")
    review_history = prov.get("review_history") or []
    reviewed_by = prov.get("reviewed_by") or []
    declared_human_review = (
        (isinstance(reviewer, str) and reviewer in humans)
        or any(isinstance(h, dict) and h.get("reviewer") in humans for h in review_history)
        or any(isinstance(r, dict) and r.get("id") in humans for r in reviewed_by)
    )

    if audit_edited_for_entity:
        pass  # strongest evidence — human edited this file's markdown
    elif declared_human_review and writer in humans:
        # Direct-authoring flow: the human author is the reviewer. Accept only
        # when the author is a human (an LLM-authored file cannot self-certify).
        if verbose:
            print(f"{full_id}: human-authored + declared human review ({reviewer or 'review_history'}) — OK")
    elif declared_human_review and writer not in humans:
        violations.append(
            f"{full_id}: declares human review ({reviewer or 'review_history'}) but provenance.writer "
            f"is '{writer}' (not human) and there is no candidate_edited audit evidence for {slug}.md — "
            f"an LLM-drafted file cannot certify its own human review (HITL required)")
    else:
        violations.append(
            f"{full_id}: no human review evidence — no candidate_edited event for {slug}.md by a registered "
            f"human in the audit trail, and no declared human reviewer in provenance (HITL required)")

    if violations:
        return False, violations
    return True, []

CONNECTIONS = ROOT / "connections"


def check_connections_scope(verbose=False) -> int:
    """HITL over connections/ — a canonical connection must carry a human
    reviewer with review-history evidence. Owner ruling: scope = all data.
    Returns the number of failures."""
    if not CONNECTIONS.exists():
        return 0
    import yaml
    fails = 0
    humans = registered_humans()
    for yml in sorted(CONNECTIONS.rglob("*.yaml")):
        try:
            conn = yaml.safe_load(yml.read_text(encoding="utf-8")) or {}
        except Exception as e:
            print(f"FAIL: {yml.name}: unparseable: {e}")
            fails += 1
            continue
        status = conn.get("status")
        if status not in REVIEWED_STATUSES:
            continue  # draft connection — not gated
        prov = conn.get("provenance") or {}
        reviewers = []
        for r in prov.get("reviewed_by") or []:
            if isinstance(r, dict) and isinstance(r.get("id"), str):
                reviewers.append(r["id"])
        for h in prov.get("review_history") or []:
            if isinstance(h, dict) and isinstance(h.get("reviewer"), str):
                reviewers.append(h["reviewer"])
        human_reviewers = [r for r in reviewers if r in humans]
        if not human_reviewers:
            print(f"FAIL: {yml.name}: status '{status}' but no active-human reviewer "
                  f"in provenance.reviewed_by/review_history (HITL required)")
            fails += 1
        elif verbose:
            print(f"OK: {yml.name}: human-reviewed by {human_reviewers[0]}")
    return fails


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
        # Check ALL data: content/ entities (every type) plus connections/.
        import yaml
        entities = []
        for md in sorted(CONTENT.rglob("*.md")):
            try:
                fm = yaml.safe_load(md.read_text().split("---")[1])
                if fm.get("id"):
                    entities.append(fm["id"])
            except Exception:
                continue
        fails = 0
        gated = 0
        for eid in entities:
            # Count how many are actually review-gated (for an honest summary).
            slug = eid.split(".")[-1]
            cf = _find_content_file(slug)
            if cf is not None:
                try:
                    s = (yaml.safe_load(cf.read_text().split("---")[1]) or {}).get("status")
                    if s in REVIEWED_STATUSES:
                        gated += 1
                except Exception:
                    pass
            ok, violations = check_entity(eid, verbose=args.verbose)
            if not ok:
                fails += 1
                print(f"FAIL: {eid}:")
                for v in violations:
                    print(f"  - {v}")
            elif args.verbose:
                print(f"OK: {eid}")

        # Connections are HITL-gated too (owner ruling: scope = all data).
        conn_fails = check_connections_scope(args.verbose)
        fails += conn_fails

        if fails:
            print(f"\nHITL check: {fails} failure(s) across content/ ({len(entities)} entities, "
                  f"{gated} review-gated) and connections/ — human review required")
            return 1
        else:
            print(f"OK: HITL check passed — all {len(entities)} entities "
                  f"({gated} review-gated) + connections/ satisfy human-review requirements")
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
        human_edits=human_edit_events(audit, registered_humans())
        print(f"Human edits (HITL): {len(human_edits)}")
        if not human_edits and (candidates or proposals):
            print(f"FAIL: No human edits in audit — HITL required, human must explicitly edit markdown")
            return 1
        elif not (candidates or proposals):
            print("OK: no workflow candidates or proposals yet — nothing to check")
            return 0
        else:
            print(f"OK: HITL workflow has {len(human_edits)} registered-human edit(s); per-entity evidence is enforced at review time (review_entity.py)")
            return 0

    parser.print_help()
    return 0

if __name__=="__main__":
    sys.exit(main())
