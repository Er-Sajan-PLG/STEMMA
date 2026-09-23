#!/usr/bin/env python3
"""Owner-key signing for R6 release bundles (increment 3).

Mechanics only: signs release/R6-bundle-*/SHA256SUMS.txt with the OWNER'S
gpg key (detached signature SHA256SUMS.sig). The executor never invents or
handles private keys — this script uses the pre-existing local keyring
owned by the human reviewer. Alignment: ADR-0007 release bundle; signing
proves provenance (Layer 2), independent of the identifier-base question.

Usage:
  python3 scripts/sign_release_bundle.py <release/R6-bundle-...> --key <key-id-or-email>
  python3 scripts/sign_release_bundle.py <release/R6-bundle-...> --verify-only

If no key is available/configured the script exits 2 with setup guidance —
no signature is faked; bundles remain verifiable by checksums meanwhile.
"""
from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def _gpg() -> str:
    from shutil import which
    return which("gpg")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("bundle_dir")
    ap.add_argument("--key", help="gpg key id or email of the owner key")
    ap.add_argument("--verify-only", action="store_true")
    args = ap.parse_args()
    bundle = ROOT / args.bundle_dir if not args.bundle_dir.startswith("/") else pathlib.Path(args.bundle_dir)
    sums = bundle / "SHA256SUMS.txt"
    sig = bundle / "SHA256SUMS.sig"
    if not bundle.exists() or not sums.exists():
        print(f"FAIL: bundle not found at {bundle} (run scripts/build_release_bundle.py)", file=sys.stderr)
        return 1

    if not _gpg():
        print("SETUP: gpg not installed on this machine — signing skipped.\n"
              "  Owner: install gnupg and create/import your key, then:\n"
              f"  python3 scripts/sign_release_bundle.py {args.bundle_dir} --key <key-id>")
        return 2

    if args.verify_only:
        if not sig.exists():
            print("FAIL: no signature present (unsigned bundle)", file=sys.stderr)
            return 1
        r = subprocess.run(["gpg", "--verify", str(sig), str(sums)], capture_output=True, text=True)
        print(r.stdout or r.stderr)
        return 0 if r.returncode == 0 else 1

    if not args.key:
        print("SETUP: --key required (owner key id/email). No key material is created by this tool.",
              file=sys.stderr)
        return 2
    r = subprocess.run(["gpg", "--batch", "--yes", "--armor",
                        "--local-user", args.key,
                        "--detach-sign", "-o", str(sig), str(sums)],
                       capture_output=True, text=True, cwd=bundle)
    if r.returncode != 0:
        print(f"FAIL: gpg signing failed: {r.stderr[-300:]}", file=sys.stderr)
        return 1
    manifest = bundle / "manifest.json"
    import json
    m = json.loads(manifest.read_text(encoding="utf-8"))
    m["signature"] = {"file": "SHA256SUMS.sig", "key": args.key, "type": "gpg-detached-armor"}
    manifest.write_text(json.dumps(m, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"OK: signed {sig.name} with {args.key}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
