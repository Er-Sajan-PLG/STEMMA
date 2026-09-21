#!/usr/bin/env python3
"""docs — documentation synchronization & enforcement engine for STEMMA.

Layered canonical commands (same logic locally and in CI — anti CI-only drift):

  python3 scripts/docs.py impact [--paths F..|--all|--base REF]   explain affected docs (read-only)
  python3 scripts/docs.py sync                                     run declared doc generators (mutates)
  python3 scripts/docs.py validate                                 check documentation invariants (read-only)
  python3 scripts/docs.py check                                    CI-equivalent gate: validate + declared checks
  python3 scripts/docs.py coverage [--write|--check]               taxonomy census (generated doc)

Contract: docs/docs-contract.yaml (ownership kinds, sources, generators, checks).
Census data: docs/meta/doc-taxonomy.yaml (220-artifact disposition vs task Appendix A).

Determinism: generated output contains no timestamps; it is a pure function of
the contract + taxonomy. Idempotency: sync twice == sync once.
"""
from __future__ import annotations

import fnmatch
import os
import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = Path("docs/docs-contract.yaml")
TAXONOMY_PATH = Path("docs/meta/doc-taxonomy.yaml")
COVERAGE_PATH = Path("docs/meta/documentation-coverage.md")
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
STATUSES = ("present", "partial", "missing", "na")

# ---------------------------------------------------------------- model layer


def load_contract(root: Path = ROOT) -> dict:
    return yaml.safe_load((root / CONTRACT_PATH).read_text(encoding="utf-8"))


def load_taxonomy(root: Path = ROOT) -> dict:
    return yaml.safe_load((root / TAXONOMY_PATH).read_text(encoding="utf-8"))


def artifacts(contract: dict) -> list[dict]:
    return contract.get("artifacts", [])


def match_source(pattern: str, path: str) -> bool:
    if pattern.endswith("/"):
        return path.startswith(pattern)
    if "*" in pattern:
        return fnmatch.fnmatch(path, pattern)
    return path == pattern or path.startswith(pattern + "/")


def direct_impact(changed: list[str], contract: dict) -> dict[str, set[str]]:
    """Map artifact path -> set of triggering changed paths (direct source match
    or the artifact file itself changed)."""
    hits: dict[str, set[str]] = {}
    for art in artifacts(contract):
        triggers: set[str] = set()
        for c in changed:
            if c == art["path"]:
                triggers.add("self")
                continue
            for src in art.get("sources") or []:
                if match_source(src, c):
                    triggers.add(c)
        if triggers:
            hits[art["path"]] = triggers
    return hits


def transitive_impact(direct: dict[str, set[str]], contract: dict) -> set[str]:
    """Closure over depends_on edges (artifact -> dependencies)."""
    out = set(direct)
    changed = True
    while changed:
        changed = False
        for art in artifacts(contract):
            p = art["path"]
            if p in out:
                continue
            for dep in art.get("depends_on") or []:
                if dep in out:
                    out.add(p)
                    changed = True
    return out

# ------------------------------------------------------------- change capture


def git(*args: str) -> list[str]:
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        return []
    return [ln.strip() for ln in r.stdout.splitlines() if ln.strip()]


def changed_files(base: str | None = None) -> list[str]:
    files: set[str] = set(git("diff", "--name-only", "HEAD"))
    files |= set(git("ls-files", "--others", "--exclude-standard"))
    if base:
        files |= set(git("diff", "--name-only", f"{base}...HEAD"))
    # never consider the tool's own scratch; only repo-tracked surface
    return sorted(f for f in files if not f.startswith((".git/", "__pycache__")))

# ---------------------------------------------------------------- impact CLI


def cmd_impact(argv: list[str]) -> int:
    base = None
    paths: list[str] | None = None
    force_all = "--all" in argv
    i = 0
    while i < len(argv):
        if argv[i] == "--paths":
            i += 1
            paths = []
            while i < len(argv) and not argv[i].startswith("--"):
                paths.append(argv[i])
                i += 1
            continue
        if argv[i] == "--base":
            i += 1
            base = argv[i] if i < len(argv) else None
            i += 1
            continue
        i += 1
    contract = load_contract()
    changed = sorted(a["path"] for a in artifacts(contract)) if force_all else \
        (sorted(paths) if paths is not None else changed_files(base))
    if not changed:
        print("impact: no changed files detected (nothing affected)")
        return 0
    direct = direct_impact(changed, contract)
    closure = transitive_impact(direct, contract)
    mapped_triggers = {t for triggers in direct.values() for t in triggers if t != "self"}
    unmapped = [c for c in changed
                if c not in mapped_triggers and all(a["path"] != c for a in artifacts(contract))]
    print(f"impact: {len(changed)} changed file(s) -> {len(closure)} affected doc artifact(s)")
    for p in sorted(closure):
        why = ", ".join(sorted(direct.get(p, {"(transitive)"})))[:100]
        print(f"  - {p}   [{why}]")
    if unmapped:
        known_prefixes = tuple({s for a in artifacts(contract) for s in (a.get("sources") or [])})
        print(f"  unmapped ({len(unmapped)}) — conservative: validate all invariants anyway")
        for c in unmapped:
            print(f"    ? {c}")
        if not known_prefixes:
            print("    (contract has no sources)")
    print("next: python3 scripts/docs.py sync && python3 scripts/docs.py check")
    return 0

# --------------------------------------------------------------- sync engine


def render_coverage(contract: dict, taxonomy: dict, root: Path = ROOT) -> str:
    """Deterministic census markdown (no timestamps)."""
    arts = taxonomy["artifacts"]
    cats = taxonomy["categories"]
    lines = [
        "<!-- GENERATED by scripts/docs.py coverage — do not edit by hand.",
        "     regenerate: python3 scripts/docs.py coverage --write -->",
        "",
        "# Documentation Coverage Census — STEMMA",
        "",
        "Disposition of the 220-artifact documentation taxonomy for this repository,",
        "generated from `docs/meta/doc-taxonomy.yaml` joined with `docs/docs-contract.yaml`.",
        "",
        "## Summary by category",
        "",
        "| Category | Total | Applicable | Present | Partial | Missing | N/A |",
        "|---|---|---|---|---|---|---|",
    ]
    totals = {"total": 0, "app": 0, "present": 0, "partial": 0, "missing": 0, "na": 0}
    for cid in sorted(cats, key=lambda c: int(c[1:])):
        rows = [a for a in arts if a["cat"] == cid]
        by = {s: sum(1 for a in rows if a["status"] == s) for s in STATUSES}
        app = len(rows) - by["na"]
        lines.append(f"| {cid} {cats[cid]} | {len(rows)} | {app} | {by['present']} | {by['partial']} | {by['missing']} | {by['na']} |")
        totals["total"] += len(rows)
        totals["app"] += app
        for s in STATUSES:
            totals[s] += by[s]
    lines.append(
        f"| **All** | **{totals['total']}** | **{totals['app']}** | "
        f"**{totals['present']}** | **{totals['partial']}** | **{totals['missing']}** | **{totals['na']}** |"
    )
    lines += ["", "## Summary by tier (applicable artifacts only)", "",
              "| Tier | Applicable | Present | Partial | Missing |", "|---|---|---|---|---|"]
    for tier in range(5):
        rows = [a for a in arts if a["tier"] == tier and a["status"] != "na"]
        if not rows:
            continue
        by = {s: sum(1 for a in rows if a["status"] == s) for s in STATUSES}
        lines.append(f"| Tier {tier} | {len(rows)} | {by['present']} | {by['partial']} | {by['missing']} |")
    lines += ["", "## Artifact detail", ""]
    for cid in sorted(cats, key=lambda c: int(c[1:])):
        lines += [f"### {cid} — {cats[cid]}", "", "| # | Artifact | Status | Path / note |",
                  "|---|---|---|---|"]
        for a in sorted((x for x in arts if x["cat"] == cid), key=lambda x: x["id"]):
            detail = a.get("path", "")
            if a.get("note"):
                detail = (detail + " — " if detail else "") + a["note"]
            lines.append(f"| {a['id']} | {a['name']} | {a['status']} | {detail or '—'} |")
        lines.append("")
    lines += [
        "## Reading guide",
        "",
        "- `present` — artifact exists and is maintained under the contract.",
        "- `partial` — artifact exists in reduced/embedded form (see note).",
        "- `missing` — applicable to this repo but not yet created (Tier candidates).",
        "- `na` — deliberately not applicable to a public, file-based, sole-owner",
        "  knowledge foundation (reason recorded per row, reviewable).",
        "",
    ]
    return "\n".join(lines) + "\n"


def _run_declared(cmd: str, **kw) -> subprocess.CompletedProcess:
    argv = cmd.split()
    if argv[0] in ("python", "python3"):
        argv[0] = sys.executable
    return subprocess.run(argv, cwd=ROOT, capture_output=True, text=True, **kw)


def run_generator(gen_id: str, gen: dict, write: bool) -> list[str]:
    """Returns list of output paths that changed (or would change in check mode)."""
    changed_or_dirty: list[str] = []
    for out in gen.get("outputs", []):
        (ROOT / out).parent.mkdir(parents=True, exist_ok=True)
    write_cmd = gen["write"] if write else gen["check"]
    if write_cmd.startswith("internal:coverage"):
        want = "--check" not in write_cmd.replace("internal:coverage", "")
        rendered = render_coverage(load_contract(), load_taxonomy())
        cur = (ROOT / COVERAGE_PATH).read_text(encoding="utf-8") if (ROOT / COVERAGE_PATH).exists() else ""
        if rendered != cur:
            changed_or_dirty.append(str(COVERAGE_PATH))
            if want:
                (ROOT / COVERAGE_PATH).write_text(rendered, encoding="utf-8")
        return changed_or_dirty
    before = {o: ((ROOT / o).read_bytes() if (ROOT / o).exists() else None) for o in gen.get("outputs", [])}
    r = _run_declared(write_cmd)
    if r.returncode != 0:
        print(f"generator {gen_id} failed:\n{r.stdout}\n{r.stderr}", file=sys.stderr)
        raise SystemExit(2)
    for o, old in before.items():
        new = (ROOT / o).read_bytes() if (ROOT / o).exists() else None
        if new != old:
            changed_or_dirty.append(o)
    return changed_or_dirty


def cmd_sync(argv: list[str]) -> int:
    contract = load_contract()
    any_change: list[str] = []
    for gen_id, gen in (contract.get("generators") or {}).items():
        diff = run_generator(gen_id, gen, write=True)
        any_change.extend(diff)
        print(f"sync: generator {gen_id} -> " + (f"updated {diff}" if diff else "already fresh"))
    if any_change:
        print(f"sync: {len(any_change)} file(s) updated — review the diff, do not discard silently")
    print("next: python3 scripts/docs.py check")
    return 0

# ------------------------------------------------------------ validate layer


def _validate_contract_vs_disk(contract: dict, taxonomy: dict, root: Path, problems: list[str]) -> None:
    kinds = set(contract.get("kinds", []))
    cats = set((contract.get("categories") or {}).keys())
    for art in artifacts(contract):
        p, kind, cat = art["path"], art.get("kind"), art.get("cat")
        if kind not in kinds:
            problems.append(f"contract: {p}: illegal kind {kind!r}")
        if cat not in cats:
            problems.append(f"contract: {p}: illegal category {cat!r}")
        tier = art.get("tier")
        if not (isinstance(tier, int) and 0 <= tier <= 4):
            problems.append(f"contract: {p}: illegal tier {tier!r}")
        if not (root / p).exists():
            problems.append(f"contract: artifact {p} does not exist")
    declared = {a["path"] for a in artifacts(contract)}
    for f in sorted((root / "docs").glob("*.md")):
        rel = f.relative_to(root).as_posix()
        if rel not in declared:
            problems.append(f"contract: docs file {rel} missing from contract (orphan)")
    seen_ids = set()
    for t in taxonomy["artifacts"]:
        if t["id"] in seen_ids:
            problems.append(f"taxonomy: duplicate id {t['id']}")
        seen_ids.add(t["id"])
        if t["status"] not in STATUSES:
            problems.append(f"taxonomy: {t['id']}: illegal status {t['status']!r}")
        if t["status"] in ("present",) and not t.get("path") and not t.get("note"):
            problems.append(f"taxonomy: {t['id']} present without path or note")
        if t.get("path") and t["status"] == "na":
            problems.append(f"taxonomy: {t['id']} marked na but has path {t['path']}")
        if t.get("path") and t["status"] in ("present", "partial") and not (root / t["path"]).exists() and not any(ch in t["path"] for ch in "*[]"):
            problems.append(f"taxonomy: {t['id']} path {t['path']} does not exist")
    for gen_id, gen in (contract.get("generators") or {}).items():
        for out in gen.get("outputs", []):
            if not (root / out).exists():
                problems.append(f"contract: generator {gen_id} output {out} missing")
        marker = gen.get("marker")
        if marker:
            for out in gen.get("outputs", []):
                if (root / out).exists() and marker not in (root / out).read_text(encoding="utf-8"):
                    problems.append(f"contract: generated marker missing in {out}")


def _validate_links(contract: dict, root: Path, problems: list[str]) -> None:
    for pattern in contract.get("link_scope", []):
        for f in sorted(root.glob(pattern)):
            text = f.read_text(encoding="utf-8")
            for m in LINK_RE.finditer(text):
                target = m.group(1).strip()
                if SCHEME_RE.match(target) or target.startswith("#") or target.startswith("<"):
                    continue
                target = target.split("#", 1)[0].strip()
                if not target or target.startswith("!"):
                    continue
                resolved = (f.parent / target).resolve()
                try:
                    resolved.relative_to(root.resolve())
                except ValueError:
                    problems.append(f"{f.relative_to(root)}: link escapes repo: {target}")
                    continue
                if not resolved.exists():
                    problems.append(f"{f.relative_to(root)}: broken link {target}")


def validate(root: Path = ROOT) -> list[str]:
    contract = load_contract(root)
    taxonomy = load_taxonomy(root)
    problems: list[str] = []
    _validate_contract_vs_disk(contract, taxonomy, root, problems)
    _validate_links(contract, root, problems)
    # generated-doc drift (non-mutating): regenerate in memory, compare
    rendered = render_coverage(contract, taxonomy)
    cur = (root / COVERAGE_PATH).read_text(encoding="utf-8") if (root / COVERAGE_PATH).exists() else None
    if rendered != cur:
        problems.append(f"generated drift: {COVERAGE_PATH} stale (repair: python3 scripts/docs.py sync)")
    return problems


def cmd_validate(argv: list[str]) -> int:
    problems = validate()
    if problems:
        print("DOCUMENTATION VALIDATE FAILED")
        for p in problems:
            print(f"  - {p}")
        print("Repair: python3 scripts/docs.py sync   Verify: python3 scripts/docs.py check")
        return 1
    print("validate: all contract invariants pass (contract integrity, links, generated freshness)")
    return 0

# --------------------------------------------------------------- check layer

CAT_LABELS = {
    "A1": "Project & Governance", "A2": "Requirements & Specifications",
    "A3": "Architecture & Design", "A4": "Source Code", "A5": "API Documentation",
    "A6": "Configuration", "A7": "Testing", "A8": "Operations & SRE",
    "A9": "Security", "A10": "User-Facing", "A11": "Developer & Contributor",
    "A12": "Compliance & Legal", "A13": "Analytics & Metrics", "A14": "Meta-Documentation",
}


def cmd_check(argv: list[str]) -> int:
    contract = load_contract()
    taxonomy = load_taxonomy()
    failures: list[tuple[str, str, str]] = []  # (check, subject essay, output tail)

    problems = validate()
    if problems:
        failures.append(("docs-contract", "contract integrity + links + generated freshness",
                         "\n".join(f"    - {p}" for p in problems)))

    for chk in contract.get("checks", []):
        r = _run_declared(chk["run"])
        if r.returncode != 0:
            tail = "\n".join((r.stdout.strip().splitlines() + r.stderr.strip().splitlines())[-8:])
            failures.append((chk["id"], chk.get("subject", ""), tail))

    if failures:
        print("DOCUMENTATION CHECK FAILED")
        for cid, subject, tail in failures:
            print(f"\nCheck:       {cid}")
            print(f"Invariant:   {subject}")
            print(f"Actual:\n{tail}")
        print("\nRepair:      python3 scripts/docs.py sync   (then review the diff)")
        print("Verify:      python3 scripts/docs.py check")
        return 1

    # success: per-category census line (honest — derived from taxonomy)
    arts = taxonomy["artifacts"]
    print("Documentation contract (14 categories)")
    for cid in sorted(CAT_LABELS, key=lambda c: int(c[1:])):
        rows = [a for a in arts if a["cat"] == cid]
        app = [a for a in rows if a["status"] != "na"]
        pres = sum(1 for a in app if a["status"] in ("present", "partial"))
        missing = sum(1 for a in app if a["status"] == "missing")
        flag = f"{pres}/{len(app)} applicable present+partial"
        if missing:
            flag += f", {missing} missing-by-plan"
        print(f"  PASS  {cid} {CAT_LABELS[cid]:<34} {flag}")
    print("  PASS  meta         contract integrity, links resolve, generated docs fresh")
    print("  PASS  checks       " + ", ".join(c["id"] for c in contract.get("checks", [])))
    print("Status: PASS")
    return 0

# ----------------------------------------------------------------- main


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    cmd, rest = argv[0], argv[1:]
    dispatch = {"impact": cmd_impact, "sync": cmd_sync,
                "validate": cmd_validate, "check": cmd_check}
    if cmd == "coverage":
        contract = load_contract()
        rendered = render_coverage(contract, load_taxonomy())
        cur = (ROOT / COVERAGE_PATH).read_text(encoding="utf-8") if (ROOT / COVERAGE_PATH).exists() else None
        if "--write" in rest:
            if rendered != cur:
                (ROOT / COVERAGE_PATH).write_text(rendered, encoding="utf-8")
                print(f"coverage: wrote {COVERAGE_PATH}")
            else:
                print("coverage: already fresh")
            return 0
        if rendered == cur:
            print("coverage: fresh")
            return 0
        print(f"coverage: STALE — repair: python3 scripts/docs.py coverage --write")
        return 1
    if cmd in dispatch:
        return dispatch[cmd](rest)
    print(f"unknown command: {cmd}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
