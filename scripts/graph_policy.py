#!/usr/bin/env python3
"""B5.3: Review-aware graph/export policy — single reusable filter.

Policies:
  all        — all active connections regardless of review
  reviewed   — review.status in (reviewed, canonical)
  canonical  — review.status == canonical only
  trusted    — reviewed or canonical AND not llm-unreviewed (documented semantics)
"""
from __future__ import annotations

import pathlib

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent

POLICIES = {"all", "reviewed", "canonical", "trusted"}


def should_include_connection(conn: dict, policy: str) -> bool:
    if policy not in POLICIES:
        raise ValueError(f"unknown policy {policy!r}, expected one of {POLICIES}")
    # Only active connections are considered; deprecated/rejected excluded for all
    if conn.get("assertion", {}).get("status") != "active":
        return False
    review = conn.get("assertion", {}).get("review", {}).get("status")
    if policy == "all":
        # ADR-0031: `all` is the default consumer view = active AND not rejected.
        # Rejected claims surface only via knowledge.rejected.json.
        return review != "rejected"
    if policy == "reviewed":
        return review in ("reviewed", "canonical")
    if policy == "canonical":
        return review == "canonical"
    if policy == "trusted":
        # Trusted: reviewed/canonical AND not llm-authored unreviewed
        if review not in ("reviewed", "canonical"):
            return False
        prov = conn.get("provenance", {})
        asserted = prov.get("asserted_by", {}).get("type")
        # llm-authored must be at least reviewed to be trusted
        if asserted == "llm" and review != "canonical":
            return False
        return True
    return False


def filtered_connections(policy: str):
    out = []
    for p in sorted((ROOT / "connections").glob("*.yaml")):
        d = yaml.safe_load(p.read_text())
        if should_include_connection(d, policy):
            out.append(d)
    return out


if __name__ == "__main__":
    import sys, json

    policy = sys.argv[1] if len(sys.argv) > 1 else "all"
    conns = filtered_connections(policy)
    print(f"policy={policy} count={len(conns)}")
    # For manual use, print JSON
    if "--json" in sys.argv:
        print(json.dumps([c["id"] for c in conns], indent=2))
