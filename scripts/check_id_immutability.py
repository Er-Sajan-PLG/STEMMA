#!/usr/bin/env python3
"""ID-immutability guard — an identifier once assigned to a canonical
entity can NEVER later represent a different entity or meaning (ADR-0003).

This is NOT a naive "union all IDs in git history and compare sets" check. The real invariant
(plan v4.0) is **semantic identity**: an identity is reconstructed from the schema/history as
(id, name, domain) — the stable, identity-defining fields. Reassigning an ID to a *different*
entity (a different name or domain) is never allowed; deprecation and aliasing are the only
legal ways to retire/resurface an identifier, and they reserve the ID forever.

Single source of truth for history = git. Reconstruction walks each canonical entity file's
git history and records the identity fields at each version.

Outcomes (must match the plan's TDD table):
  new                       -> PASS   (an ID introduced, never present before)
  unchanged identity        -> PASS   (name/domain identical across all versions)
  deprecated                -> PASS   (status: deprecated; ID reserved forever)
  aliased                   -> PASS   (deprecated_by / aliases; alias references must be valid)
  reassigned                -> FAIL   (same ID now means a DIFFERENT entity: name/domain changed)
  deleted-and-reused        -> FAIL   (an ID was deleted, then a different entity reused it)

---

Plan v2 E4.5 extends the same invariant to CONNECTIONS (ADR-0026): an assertion's
(source, relation, target) triple is what a connection id *means*, so it is immutable for
the life of the id. Correcting a claim is not an edit — it is a supersession:
`assertion.status: superseded` + `lifecycle.replaced_by: <new id>` and a NEW id for
the corrected claim. Deleting a connection file without superseding it is also a violation
(the id vanishes while its claim is still referenced by consumers).

  new triple                        -> PASS
  unchanged triple                  -> PASS   (only evidence/review metadata changed)
  triple corrected via supersession -> PASS   (old id superseded + replaced_by set)
  triple edited in place            -> FAIL   (the same id now asserts a different claim)
  deleted without supersession      -> FAIL
"""
from __future__ import annotations
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
CONNECTIONS = ROOT / "connections"

# Connection statuses that legally retire an assertion (ADR-0011 / ADR-0026).
CONNECTION_RETIRED_STATUSES = ("superseded", "deprecated")


def normalize_id(id_: str | None) -> str | None:
    """One-time namespace migration equivalence (ADR-0027, 2026-09-04).

    The canonical namespace moved `lhs:` -> `stemma:` in a single governed bulk
    migration that changed NO identity-defining fields. Git history is the source
    of truth for this guard, so historical `lhs:` ids and HEAD `stemma:` ids must
    reconcile through this alias rule. This function exists ONLY for that
    migration; it must never be extended to map other prefixes.
    """
    if isinstance(id_, str) and id_.startswith("lhs:"):
        return "stemma:" + id_[len("lhs:"):]
    return id_

# Both prefixes appear in git history (lhs: pre-ADR-0027, stemma: after);
# normalize_id() maps them onto one identity space.
_ID_RE = re.compile(r"^id:\s*((?:lhs|stemma):[a-z][a-z0-9-]*\.[a-z0-9][a-z0-9-]*)", re.MULTILINE)
_NAME_RE = re.compile(r"^name:\s*(.+)$", re.MULTILINE)
_DOMAIN_RE = re.compile(r"^domain:\s*(.+)$", re.MULTILINE)
_STATUS_RE = re.compile(r"^status:\s*(.+)$", re.MULTILINE)

# Identity-defining fields. Editing prose (definition/examples/notes) does NOT change identity;
# only these two fields, if changed under the same id, constitute reassignment.
_IDENTITY_FIELDS = ("name", "domain")


def git(*args: str) -> str:
    r = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {r.stderr}")
    return r.stdout


def parse_file(text: str) -> dict:
    """Extract (id, name, domain, status) from a canonical entity's YAML frontmatter."""
    if not text.startswith("---"):
        return {}
    fm = text.split("---", 2)[1]
    out: dict[str, str] = {}
    for pattern, key in ((_ID_RE, "id"), (_NAME_RE, "name"), (_DOMAIN_RE, "domain"), (_STATUS_RE, "status")):
        m = pattern.search(fm)
        if m:
            val = m.group(1).strip().strip("\"'>")
            if key == "name":
                # name may be quoted or plain; keep the visible name text
                val = m.group(1).strip().strip("'\"")
            out[key] = val
    return out


def build_id_history() -> dict[str, list[dict]]:
    """For each canonical id, record every (name, domain, status) version across git history.

    Returns mapping id -> list of dict(commit, name, domain, status) in oldest->newest order.
    """
    history: dict[str, list[dict]] = {}
    for path in sorted(CONTENT.rglob("*.md")):
        rel = path.relative_to(ROOT).as_posix()
        # SHAs where this file changed, oldest first
        shas = [
            s for s in reversed(git("log", "--format=%H", "--", rel).split())
        ]
        seen = set()
        for sha in shas:
            try:
                blob = git("show", f"{sha}:{rel}")
            except RuntimeError:
                continue  # file absent at that sha (deleted or not yet added)
            ent = parse_file(blob)
            if not ent.get("id"):
                continue
            ent["id"] = normalize_id(ent["id"])
            key = (ent.get("name"), ent.get("domain"), ent.get("status"))
            if key in seen:
                continue  # drop duplicate identity across consecutive commits
            seen.add(key)
            history.setdefault(ent["id"], []).append(
                {"commit": sha[:9], "name": ent.get("name"), "domain": ent.get("domain"),
                 "status": ent.get("status")}
            )
    return history


def live_entities() -> dict[str, dict]:
    """Entities currently in HEAD content: id -> (name, domain, status)."""
    live: dict[str, dict] = {}
    for path in CONTENT.rglob("*.md"):
        ent = parse_file(path.read_text())
        if ent.get("id"):
            ent["id"] = normalize_id(ent["id"])
            live[ent["id"]] = ent
    return live


def parse_connection(text: str) -> dict:
    """Extract a connection's identity fields without a YAML dependency.

    Kept deliberately dependency-free (this guard must run in a bare CI checkout):
    top-level `id/source/relation/target`, plus `assertion.status` and
    `lifecycle.replaced_by` from their two-space-indented blocks.
    """
    out: dict[str, str] = {}
    block: str | None = None
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("---"):
            continue
        indent = len(line) - len(line.lstrip())
        if indent == 0:
            key, _, val = stripped.partition(":")
            key = key.strip()
            if val.strip() == "":
                block = key  # start of a nested block (assertion:/lifecycle:/...)
                continue
            block = key
            out[key] = val.strip().strip("\"'")
        elif indent == 2 and block in ("assertion", "lifecycle"):
            key, _, val = stripped.partition(":")
            out[f"{block}.{key.strip()}"] = val.strip().strip("\"'")
    return out


def build_connection_history() -> dict[str, list[dict]]:
    """For each connection id, record every distinct (source, relation, target) version.

    History comes from git (the single source of truth), following renames so the
    pending E4.6 colon-filename migration cannot be mistaken for a deletion.
    """
    history: dict[str, list[dict]] = {}
    if not CONNECTIONS.exists():
        return history
    for path in sorted(CONNECTIONS.rglob("*.yaml")):
        rel = path.relative_to(ROOT).as_posix()
        shas = list(reversed(git("log", "--format=%H", "--follow", "--", rel).split()))
        seen: set[tuple] = set()
        for sha in shas:
            try:
                blob = git("show", f"{sha}:{rel}")
            except RuntimeError:
                continue  # path did not exist at that commit (pre-rename history)
            conn = parse_connection(blob)
            cid = normalize_id(conn.get("id"))
            if not cid:
                continue
            stamp = (
                conn.get("source"),
                conn.get("relation"),
                conn.get("target"),
                conn.get("assertion.status"),
                conn.get("lifecycle.replaced_by"),
            )
            if stamp in seen:
                continue  # drop consecutive identical versions
            seen.add(stamp)
            history.setdefault(cid, []).append(
                {
                    "commit": sha[:9],
                    "source": normalize_id(conn.get("source")),
                    "relation": conn.get("relation"),
                    "target": normalize_id(conn.get("target")),
                    "status": conn.get("assertion.status"),
                    "replaced_by": normalize_id(conn.get("lifecycle.replaced_by")) or None,
                }
            )
    return history


def live_connections() -> dict[str, dict]:
    """Connections present in HEAD: id -> parsed identity fields."""
    live: dict[str, dict] = {}
    if not CONNECTIONS.exists():
        return live
    for path in sorted(CONNECTIONS.rglob("*.yaml")):
        conn = parse_connection(path.read_text(encoding="utf-8"))
        if conn.get("id"):
            conn["id"] = normalize_id(conn["id"])
            live[conn["id"]] = conn
    return live


def detect_connection_violations(history: dict[str, list[dict]], live: dict[str, dict]) -> list[str]:
    """Pure detection for connection-triple immutability (E4.5) — dict-in, list-out."""
    violations: list[str] = []

    # 1. The (source, relation, target) triple under an id never changes.
    for cid in sorted(history):
        stamps: list[tuple] = []
        for v in history[cid]:
            stamp = (v.get("source"), v.get("relation"), v.get("target"))
            if any(part is None for part in stamp):
                continue  # unparsable version — nothing to compare
            if not stamps or stamps[-1][0] != stamp:
                stamps.append((stamp, v["commit"]))
        if len(stamps) > 1:
            (first, first_sha), (second, second_sha) = stamps[0], stamps[1]
            violations.append(
                f"[connection-triple-changed] {cid}: "
                f"{first[0]} –{first[1]}→ {first[2]} @{first_sha} became "
                f"{second[0]} –{second[1]}→ {second[2]} @{second_sha}. "
                "An assertion's (source, relation, target) triple is immutable: supersede this "
                "connection (assertion.status: superseded + lifecycle.replaced_by) and assert "
                "the corrected claim under a NEW connection id (ADR-0026)."
            )

    # 2. A connection id that disappears from HEAD must have been superseded/deprecated,
    #    never silently dropped (consumers may still hold a reference to it).
    for cid in sorted(set(history) - set(live)):
        last = history[cid][-1]
        if (last.get("status") or "").strip() in CONNECTION_RETIRED_STATUSES or last.get("replaced_by"):
            continue
        violations.append(
            f"[connection-deleted-without-supersession] {cid}: present in history as "
            f"{last.get('source')} –{last.get('relation')}→ {last.get('target')} "
            f"(status {last.get('status')!r} @{last['commit']}) but gone from HEAD without "
            "being superseded or deprecated. Restore it with assertion.status: superseded and "
            "lifecycle.replaced_by, or delete only after a replacement connection exists."
        )
    return violations


def detect_violations(history: dict[str, list[dict]], live: dict[str, dict]) -> list[str]:
    """Pure detection: given an id->[versions] history and a HEAD id->entity map, return any
    immutability violations. Empty = all pass.

    This is the testable core (TDD) — it operates on plain dicts, so the six plan cases can be
    exercised directly, independent of git.
    """
    violations: list[str] = []
    # 2. Reassignment / deleted-and-reused: name/domain change under the same id.
    for id_, versions in history.items():
        identity_stamps: list[tuple[tuple[str, str], str]] = []
        seen_stamps: set[tuple[str, str]] = set()
        for v in versions:
            if v.get("name") and v.get("domain"):
                stamp = (v["name"], v["domain"])
                if stamp not in seen_stamps:
                    seen_stamps.add(stamp)
                    identity_stamps.append((stamp, v["commit"]))
        if len(identity_stamps) > 1:
            first = identity_stamps[0]
            for stamp, commit in identity_stamps[1:]:
                violations.append(
                    f"[reassigned] {id_}: '{first[0][0]}' ({first[0][1]}) @{first[1]} -> "
                    f"'{stamp[0]}' ({stamp[1]}) @{commit}. Reassigning an id to a different "
                    f"entity is forbidden; deprecate + deprecated_by instead."
                )
                break

    # 1. Every historical id that is gone from HEAD must be deprecated (else it was dropped).
    for id_ in sorted(set(history) - set(live)):
        last = history[id_][-1]
        if last["status"] != "deprecated" and last.get("name"):
            violations.append(
                f"[deleted-without-deprecation] {id_}: present in history as '{last.get('name')}' "
                f"({last.get('domain')}) but dropped from HEAD without status: deprecated"
            )

    # 3. HEAD-tree invariants: uniqueness.
    seen_ids: set[str] = set()
    for id_ in live:
        if id_ in seen_ids:
            violations.append(f"[duplicate-id] {id_}: present more than once in HEAD")
        seen_ids.add(id_)

    # 4. Alias / deprecated_by validity: the target must be a real, current-or-historical lhs id.
    known = set(live) | set(history)
    for id_, ent in live.items():
        target = ent.get("deprecated_by")
        if target and target not in known:
            violations.append(
                f"[alias-invalid] {id_} -> deprecated_by '{target}' but target is not a known canonical id"
            )
        for alias in ent.get("aliases", []) or []:
            if alias and alias not in known:
                violations.append(f"[alias-invalid] {id_}: alias '{alias}' is not a known canonical id")
    return violations


def check_id_immutability() -> list[str]:
    """Reconstruct history + live tree from HEAD, then run pure detection."""
    return detect_violations(build_id_history(), live_entities())


def check_connection_immutability() -> list[str]:
    """E4.5: reconstruct connection-triple history from git, then run pure detection."""
    return detect_connection_violations(build_connection_history(), live_connections())


def main() -> int:
    violations = check_id_immutability() + check_connection_immutability()
    if violations:
        print("ID-IMMUTABILITY FAILURES:")
        for v in violations:
            print(f"  - {v}")
        return 1
    print("PASS: all identifiers are immutable (no reassignment/reuse); "
          f"{len(live_entities())} live entities, {len(build_id_history())} historical ids")
    live_conns = live_connections()
    print("PASS: all connection triples are immutable (no in-place claim edits); "
          f"{len(live_conns)} live connections, {len(build_connection_history())} historical connection ids")
    return 0


if __name__ == "__main__":
    sys.exit(main())