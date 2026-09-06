#!/usr/bin/env python3
"""Evidence Ledger / Audit Trail for STEMMA.

Maintains an immutable append-only log of all acquisition and canonicalization events.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
LEDGER_DIR = ROOT / "ledger"
LEDGER_FILE = LEDGER_DIR / "evidence_ledger.jsonl"

LEDGER_DIR.mkdir(parents=True, exist_ok=True)


EVENT_TYPES = {
    "source_registered",
    "source_updated",
    "source_retracted",
    "source_corrected",
    "source_superseded",
    "document_ingested",
    "evidence_extracted",
    "candidate_created",
    "candidate_validated",
    "candidate_reviewed",
    "canonical_admitted",
    "canonical_deprecated",
    "canonical_superseded",
    "entity_merged",
    "entity_aliased",
    "retraction_handled",
    "correction_handled",
    "supersession_handled",
}


def compute_hash(entry: dict) -> str:
    """Compute hash of ledger entry for integrity."""
    # Hash the entry content (excluding the hash field itself)
    content = {k: v for k, v in entry.items() if k != "hash"}
    return hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()


def verify_chain() -> tuple[bool, list[str]]:
    """Verify the integrity of the ledger chain."""
    if not LEDGER_FILE.exists():
        return True, []
    
    errors = []
    prev_hash = "0" * 64  # Genesis hash
    
    for i, line in enumerate(LEDGER_FILE.read_text().strip().split("\n")):
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            errors.append(f"Line {i}: Invalid JSON")
            continue
        
        # Verify hash
        expected_hash = compute_hash(entry)
        if entry.get("hash") != expected_hash:
            errors.append(f"Line {i}: Hash mismatch (tampering detected)")
            continue
        
        # Verify chain link
        if entry.get("prev_hash") != prev_hash:
            errors.append(f"Line {i}: Chain broken (prev_hash mismatch)")
            continue
        
        prev_hash = entry["hash"]
    
    return len(errors) == 0, errors


def append_entry(event_type: str, data: dict) -> dict:
    """Append a new entry to the ledger."""
    if event_type not in EVENT_TYPES:
        raise ValueError(f"Unknown event type: {event_type}")
    
    # Get previous hash
    prev_hash = "0" * 64
    if LEDGER_FILE.exists():
        lines = LEDGER_FILE.read_text().strip().split("\n")
        if lines and lines[-1].strip():
            try:
                last_entry = json.loads(lines[-1])
                prev_hash = last_entry.get("hash", "0" * 64)
            except:
                pass
    
    entry = {
        "id": f"lhs:ledger.{__import__('uuid').uuid4().hex[:12]}",
        "event_type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "prev_hash": prev_hash,
        "data": data,
    }
    
    entry["hash"] = compute_hash(entry)
    
    # Append to file
    LEDGER_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    
    return entry


def query_ledger(event_type: str | None = None, 
                 canonical_ref: str | None = None,
                 source_ref: str | None = None,
                 since: str | None = None,
                 limit: int = 100) -> list[dict]:
    """Query the ledger with filters."""
    if not LEDGER_FILE.exists():
        return []
    
    results = []
    since_dt = datetime.fromisoformat(since.replace("Z", "+00:00")) if since else None
    
    for line in LEDGER_FILE.read_text().strip().split("\n"):
        if not line.strip():
            continue
        entry = json.loads(line)
        
        if event_type and entry["event_type"] != event_type:
            continue
        
        if since_dt:
            entry_dt = datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))
            if entry_dt < since_dt:
                continue
        
        data = entry.get("data", {})
        if canonical_ref and data.get("canonical_ref") != canonical_ref:
            continue
        if source_ref and data.get("source_ref") != source_ref:
            continue
        
        results.append(entry)
        if len(results) >= limit:
            break
    
    return results


def get_lineage(canonical_id: str) -> list[dict]:
    """Get full lineage for a canonical object."""
    lineage = []
    
    # Find canonical admission
    entries = query_ledger(event_type="canonical_admitted", canonical_ref=canonical_id)
    for entry in entries:
        lineage.append(entry)
        # Trace back through candidate, evidence, source
        trace_back(entry["data"], lineage)
    
    return lineage


def trace_back(data: dict, lineage: list[dict]) -> None:
    """Recursively trace back through the lineage."""
    refs = [
        ("candidate_ref", "candidate_created"),
        ("evidence_ref", "evidence_extracted"),
        ("source_ref", "source_registered"),
    ]
    
    for ref_key, event_type in refs:
        ref = data.get(ref_key)
        if ref:
            if isinstance(ref, list):
                for r in ref:
                    entries = query_ledger(event_type=event_type, canonical_ref=r)
                    for e in entries:
                        if e not in lineage:
                            lineage.append(e)
                            trace_back(e["data"], lineage)
            else:
                entries = query_ledger(event_type=event_type, canonical_ref=ref)
                for e in entries:
                    if e not in lineage:
                        lineage.append(e)
                        trace_back(e["data"], lineage)


def main() -> int:
    import argparse
    
    p = argparse.ArgumentParser(description="Evidence Ledger / Audit Trail")
    p.add_argument("--event", help="Event type to log")
    p.add_argument("--data", help="JSON data for event")
    p.add_argument("--data-file", help="JSON file with event data")
    p.add_argument("--query", action="store_true", help="Query ledger")
    p.add_argument("--type", help="Filter by event type")
    p.add_argument("--canonical", help="Filter by canonical ref")
    p.add_argument("--source", help="Filter by source ref")
    p.add_argument("--since", help="Filter by timestamp (ISO)")
    p.add_argument("--limit", type=int, default=100, help="Limit results")
    p.add_argument("--verify", action="store_true", help="Verify chain integrity")
    p.add_argument("--lineage", help="Get full lineage for canonical object")
    
    args = p.parse_args()
    
    if args.verify:
        valid, errors = verify_chain()
        if valid:
            print("Ledger chain: VALID")
        else:
            print("Ledger chain: INVALID")
            for err in errors:
                print(f"  ERROR: {err}")
            return 1
        return 0
    
    if args.lineage:
        lineage = get_lineage(args.lineage)
        print(f"Lineage for {args.lineage}:")
        for entry in lineage:
            print(f"  {entry['timestamp']} [{entry['event_type']}] {entry['id']}")
            print(f"    {json.dumps(entry['data'], indent=6)}")
        return 0
    
    if args.query:
        results = query_ledger(
            event_type=args.type,
            canonical_ref=args.canonical,
            source_ref=args.source,
            since=args.since,
            limit=args.limit,
        )
        print(f"Found {len(results)} entries:")
        for entry in results:
            print(f"  {entry['timestamp']} [{entry['event_type']}] {entry['id']}")
            print(f"    {json.dumps(entry['data'], indent=6)}")
        return 0
    
    if not args.event:
        print("Error: --event required for logging", file=sys.stderr)
        return 1
    
    if args.data_file:
        data = json.loads(Path(args.data_file).read_text())
    elif args.data:
        data = json.loads(args.data)
    else:
        data = {}
    
    entry = append_entry(args.event, data)
    print(f"Logged: {entry['id']} [{entry['event_type']}]")
    print(f"  Hash: {entry['hash'][:16]}...")
    return 0


if __name__ == "__main__":
    sys.exit(main())