"""Review-aware graph/export policy — shared consumer-side filter.

Policies:
  all        — all active connections regardless of review
  reviewed   — review.status in (reviewed, canonical)
  canonical  — review.status == canonical only
  trusted    — reviewed or canonical AND not llm-unreviewed (documented semantics)
"""
from __future__ import annotations

POLICIES = {"all", "reviewed", "canonical", "trusted"}


def should_include_connection(conn: dict, policy: str) -> bool:
    if policy not in POLICIES:
        raise ValueError(f"unknown policy {policy!r}, expected one of {POLICIES}")
    # Only active connections are considered; deprecated/rejected excluded for all
    if conn.get("assertion", {}).get("status") != "active":
        return False
    review = conn.get("assertion", {}).get("review", {}).get("status")
    if policy == "all":
        # ADR-0031: the default `all` view is active AND not rejected. Rejected
        # assertions surface only via the explicit rejected view / query.
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


def filter_connections(connections: list[dict], policy: str) -> list[dict]:
    return [conn for conn in connections if should_include_connection(conn, policy)]


def filtered_connections(connections: list[dict], policy: str) -> list[dict]:
    return filter_connections(connections, policy)
