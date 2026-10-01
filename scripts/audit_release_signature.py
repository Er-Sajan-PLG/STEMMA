#!/usr/bin/env python3
"""Audit a PUBLISHED release for owner-signature completeness (ADR-0054 layer 1).

Mechanics only: reads a GitHub Release (via `gh`) and asserts that a *final*
release — one that is published and not a pre-release — carries both trust
layers. It never signs, never writes to the release, and never touches key
material. Exit 1 on any gap.

Why this exists: the ordering in docs/API.md ("Owner signature") is

    draft -> sign locally -> upload SHA256SUMS.sig -> publish

and CI can only enforce the *first* step (`release.yml` creates finals as
drafts). The remaining steps are performed by a human, and nothing verified the
end state. On 2026-10-01 v3.0.0 was published ~80s before its SHA256SUMS.sig was
uploaded: the release was public and marked `Latest` carrying layer 2 (Sigstore)
but not layer 1 (owner signature). No test could catch that, because the gap is
between two human actions rather than inside a workflow.

A release candidate (`-rcN`) is legitimately layer-2-only (docs/keys/README.md),
so this auditor reports it as OK-with-note rather than a failure.

Usage:
    python3 scripts/audit_release_signature.py v3.0.0
    python3 scripts/audit_release_signature.py --all
    python3 scripts/audit_release_signature.py v3.0.0 --json

Requires `gh` (authenticated). Read-only: uses `gh release view` only.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys

RC_RE = re.compile(r"-rc\d+$")

# Layer-1 artifacts that must accompany a published final release.
REQUIRED_FINAL_ASSETS = ("SHA256SUMS.txt", "SHA256SUMS.sig")


def _gh() -> str | None:
    return shutil.which("gh")


def _view(tag: str) -> dict:
    """Return the release's GitHub state, or raise RuntimeError."""
    r = subprocess.run(
        ["gh", "release", "view", tag, "--json",
         "tagName,isDraft,isPrerelease,publishedAt,assets"],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip() or f"gh release view failed for {tag}")
    return json.loads(r.stdout)


def audit(tag: str) -> dict:
    """Audit one tag. Returns a result dict; never raises for a *finding*."""
    rel = _view(tag)
    assets = {a["name"] for a in rel.get("assets", [])}
    is_draft = bool(rel.get("isDraft"))
    is_pre = bool(rel.get("isPrerelease"))
    is_rc = bool(RC_RE.search(tag))

    findings: list[str] = []
    notes: list[str] = []

    if is_draft:
        # A draft is not a public claim: neither layer is required yet.
        notes.append("draft — unpublished; the owner has not published it yet")
    elif is_pre or is_rc:
        # Legitimate: rcs are CI-attested only (docs/keys/README.md).
        if "SHA256SUMS.sig" in assets:
            notes.append("pre-release also carries an owner signature")
        else:
            notes.append("pre-release — layer 2 (Sigstore) only, as intended")
    else:
        # Published final: BOTH layers are required.
        for name in REQUIRED_FINAL_ASSETS:
            if name not in assets:
                findings.append(
                    f"published final release is missing {name} — "
                    f"docs/API.md requires draft -> sign -> upload -> publish")
        if "manifest.json" not in assets:
            findings.append("published final release is missing manifest.json")

    return {
        "tag": tag,
        "kind": "draft" if is_draft else ("pre-release" if (is_pre or is_rc) else "final"),
        "published": (not is_draft),
        "published_at": rel.get("publishedAt"),
        "asset_count": len(assets),
        "has_owner_signature": "SHA256SUMS.sig" in assets,
        "findings": findings,
        "notes": notes,
        "ok": not findings,
    }


def _all_tags() -> list[str]:
    r = subprocess.run(["gh", "release", "list", "--limit", "200",
                        "--json", "tagName"], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip() or "gh release list failed")
    return [x["tagName"] for x in json.loads(r.stdout)]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("tag", nargs="?", help="release tag, e.g. v3.0.0")
    ap.add_argument("--all", action="store_true", help="audit every published release")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    if not args.all and not args.tag:
        ap.error("give a tag, or --all")
        return 2

    if not _gh():
        print("SETUP: gh not installed — cannot read release state.\n"
              "  Install the GitHub CLI and authenticate, then re-run.", file=sys.stderr)
        return 2

    tags = _all_tags() if args.all else [args.tag]
    results = []
    try:
        for t in tags:
            results.append(audit(t))
    except RuntimeError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            mark = "OK  " if r["ok"] else "FAIL"
            print(f"{mark} {r['tag']:16} {r['kind']:12} assets={r['asset_count']:3} "
                  f"sig={'yes' if r['has_owner_signature'] else 'no'}")
            for n in r["notes"]:
                print(f"       note: {n}")
            for f in r["findings"]:
                print(f"       {f}")

    bad = [r for r in results if not r["ok"]]
    if bad:
        print(f"\nFAIL: {len(bad)} release(s) lack a required owner signature", file=sys.stderr)
        return 1
    print(f"\nOK: {len(results)} release(s) audited — no owner-signature gaps")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
