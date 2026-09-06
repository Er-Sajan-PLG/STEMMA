#!/usr/bin/env python3
"""D3: Canonicalization state machine — single authoritative implementation."""
from __future__ import annotations

# Allowed transitions: (from_status, to_status) -> required conditions
# Statuses are assertion.review.status + assertion.type handling via type
# Simplified: review.status values: proposed/unreviewed, reviewed, canonical, rejected, deprecated
# assertion.type: proposed/asserted/inferred — orthogonal but affects gate

ALLOWED = {
    ("proposed", "reviewed"),      # accept
    ("proposed", "rejected"),      # reject
    ("proposed", "proposed"),      # defer (no-op)
    ("asserted", "reviewed"),
    ("asserted", "canonical"),
    ("asserted", "rejected"),
    ("reviewed", "canonical"),     # canonicalize
    ("reviewed", "rejected"),
    ("reviewed", "reviewed"),      # defer
    ("canonical", "deprecated"),
    ("canonical", "rejected"),     # dispute after canonical
    ("rejected", "proposed"),      # reopen (human-only)
    ("rejected", "unreviewed"),    # reopen (human-only, explicit)
    ("inferred", "reviewed"),
    ("inferred", "canonical"),
    ("inferred", "rejected"),
}

FORBIDDEN = {
    ("rejected", "canonical"),  # without reopen
    ("proposed", "canonical"),  # must go via reviewed
    ("rejected", "reviewed"),
}


def can_transition(from_review: str, to_review: str, assertion_type: str = "proposed") -> bool:
    # Inferred type handled separately
    key = (from_review, to_review)
    if key in FORBIDDEN:
        return False
    # proposed->canonical forbidden
    if from_review == "proposed" and to_review == "canonical":
        return False
    if from_review == "rejected" and to_review in ("canonical", "reviewed"):
        # only to proposed/unreviewed via reopen
        return False
    return key in ALLOWED


def requires_reviewer(to_review: str, from_review: str = "") -> bool:
    # Reject and reopen are human decisions with an auditable reviewer.
    if to_review == "rejected":
        return True
    if from_review == "rejected" and to_review in ("proposed", "unreviewed"):
        return True
    return to_review in ("reviewed", "canonical")


def requires_reason(to_review: str, from_review: str = "") -> bool:
    # Rejection is never silent; reopen records a reason too.
    if to_review == "rejected":
        return True
    return from_review == "rejected" and to_review in ("proposed", "unreviewed")


def validate_transition(conn: dict, to_review: str, reviewer: str | None, reason: str | None = None) -> list[str]:
    errs = []
    cur = conn.get("assertion", {}).get("review", {}).get("status", "unreviewed")
    # Map unreviewed -> proposed for the state machine; `unreviewed` is the
    # canonical file value, `proposed` is the state-machine alias.
    cur_mapped = "proposed" if cur == "unreviewed" else cur
    atype = conn.get("assertion", {}).get("type", "proposed")
    if cur == "unreviewed" and to_review == "unreviewed":
        errs.append("no transition (already unreviewed)")
        return errs
    if not can_transition(cur_mapped, to_review, atype):
        errs.append(f"forbidden transition {cur_mapped} -> {to_review} (type {atype})")
    if requires_reviewer(to_review, cur_mapped) and not reviewer:
        errs.append(f"reviewer required for {to_review}")
    if requires_reason(to_review, cur_mapped) and not (reason and reason.strip()):
        errs.append(f"reason required for {to_review}")
    # Evidence per family would be checked in review gate, not here
    # Origin preservation: never overwrite asserted_by
    return errs
