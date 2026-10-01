#!/usr/bin/env python3
"""MACP state tree — structural invariants (state/PROTOCOL.md §7 completion criteria).

The `state/` directory is the shared memory every agent reads before touching the
working tree. Its failure mode is not a crash: it is a file that *looks* like state
and is wrong. A confidently incorrect DASHBOARD is the most expensive artefact in
the protocol, because every later session trusts it and nothing downstream re-checks
it against reality.

This file was **rewritten** after the authoritative protocol text replaced an earlier
truncated copy. The first version encoded the agent's own assumptions about naming —
a date-only session filename, an agent id like `coding-agent.001`, and `INDEX.md` as
a navigation file. The protocol specifies otherwise (§2, §6), so these tests now
enforce the specification rather than the guess.

What is asserted, and why each one earns its place:

* the §2 structure exists in full — a missing file invites an agent to invent a
  differently-named one, which is how two sources of truth start;
* session filenames follow `YYYYMMDD-HHMM-<AGENT-ID>-<slug>.md` and agent ids are 4
  alphanumeric characters, so the log stays sortable and greppable;
* `DASHBOARD.md` carries a parseable **Last Reconciled** timestamp — without it the
  §6 staleness policy (24 h / 48 h) cannot be applied at all;
* every session file appears in `INDEX.md`, or targeted history silently misses it;
* no placeholder text — a file containing a bare `TODO` is worse than an absent file;
* every relative link resolves, because a broken link in `INDEX.md` is how an agent
  concludes the state is untrustworthy;
* **DASHBOARD.md's counts equal the live registries** — the guard against the exact
  drift MACP exists to prevent. It is not brittle in the way a hardcoded count would
  be, because it compares against the registries rather than a literal: the numbers
  may change freely, they just may not disagree.
"""
from __future__ import annotations

import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
STATE = ROOT / "state"

# state/PROTOCOL.md §2 — the structure is the contract. Do not invent extra dirs.
REQUIRED_FILES = (
    "PROTOCOL.md",
    "DASHBOARD.md",
    "REGISTRY.md",
    "INDEX.md",
    "ARCHITECTURE.md",
    "DECISIONS.md",
    "DEBT.md",
    "BLOCKERS.md",
)
REQUIRED_DIRS = ("sessions", "plans", "conflicts", "archive")

# Protocol §6 step 8 / §Shutdown step 3.
SESSION_NAME_RE = re.compile(r"^(\d{8})-(\d{4})-([A-Za-z0-9]{4})-([a-z0-9][a-z0-9-]*)\.md$")
AGENT_ID_RE = re.compile(r"^[A-Za-z0-9]{4}$")
PLAN_NAME_RE = re.compile(r"^agent-([A-Za-z0-9]{4})-[a-z0-9][a-z0-9-]*\.md$")

# A placeholder is a *marker*, not a mention. Prose that explains the rule ("no
# placeholder text", "flags `TODO`/`TBD`") must not be flagged, or the check punishes
# the very documentation that defines it. So a placeholder is recognised only when it
# is the *first meaningful token on its line* — which is what an unfinished stub
# actually looks like. Anything mid-sentence is discussion, not a hole.
PLACEHOLDER_RE = re.compile(
    r"^[\s>*+\-#]*(?:TODO|TBD|FIXME|XXX|<PLACEHOLDER>|lorem ipsum)\b",
    re.IGNORECASE | re.MULTILINE,
)


def _state_markdown() -> list[pathlib.Path]:
    return sorted(STATE.rglob("*.md"))


def test_required_structure_exists() -> None:
    missing_files = [f for f in REQUIRED_FILES if not (STATE / f).is_file()]
    missing_dirs = [d for d in REQUIRED_DIRS if not (STATE / d).is_dir()]
    assert not missing_files, f"missing required state files: {missing_files}"
    assert not missing_dirs, f"missing required state directories: {missing_dirs}"


def test_no_placeholder_text() -> None:
    offenders: dict[str, list[str]] = {}
    for path in _state_markdown():
        hits = PLACEHOLDER_RE.findall(path.read_text(encoding="utf-8"))
        if hits:
            offenders[str(path.relative_to(ROOT))] = hits
    assert not offenders, (
        "placeholder marker at the start of a line in state files — write UNKNOWN and "
        f"list it in DEBT.md instead: {offenders}"
    )


def test_every_relative_link_resolves() -> None:
    """A broken link in INDEX.md is how an agent decides the state is untrustworthy."""
    link_re = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
    broken: dict[str, list[str]] = {}
    for path in _state_markdown():
        text = path.read_text(encoding="utf-8")
        for target in link_re.findall(text):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            clean = target.split("#", 1)[0].strip()
            if not clean:
                continue
            if not (path.parent / clean).resolve().exists():
                broken.setdefault(str(path.relative_to(ROOT)), []).append(target)
    assert not broken, f"broken relative links in state/: {broken}"


# ── Naming conventions (protocol §2, §6 step 8) ──────────────────────────────

def test_session_filenames_follow_the_protocol_convention() -> None:
    sessions = sorted(p for p in (STATE / "sessions").iterdir() if p.is_file()
                      and p.name != ".gitkeep")
    assert sessions, "no session files exist — the protocol requires a log per session"
    bad = [p.name for p in sessions if not SESSION_NAME_RE.match(p.name)]
    assert not bad, (
        "session files must be named YYYYMMDD-HHMM-<AGENT-ID>-<slug>.md "
        f"(4-alphanumeric agent id): {bad}"
    )


def test_registry_agent_ids_are_four_alphanumeric_characters() -> None:
    """Protocol §6 step 8: 'Choose an agent ID: 4 alphanumeric characters.'"""
    registry = (STATE / "REGISTRY.md").read_text(encoding="utf-8")
    # First column of a data row in the Active Agents table.
    ids = re.findall(r"^\|\s*`([^`]+)`\s*\|\s*`\d{8}-\d{4}-", registry, re.MULTILINE)
    assert ids, "REGISTRY.md has no agent rows in the expected shape"
    bad = [i for i in ids if not AGENT_ID_RE.match(i)]
    assert not bad, f"agent ids must be 4 alphanumeric characters: {bad}"


def test_plan_filenames_follow_the_protocol_convention() -> None:
    plans = sorted(p for p in (STATE / "plans").iterdir() if p.is_file()
                   and p.name != ".gitkeep")
    bad = [p.name for p in plans if not PLAN_NAME_RE.match(p.name)]
    assert not bad, f"plan files must be named agent-<AGENT-ID>-<slug>.md: {bad}"


def test_every_session_file_has_an_index_row() -> None:
    """Protocol §Shutdown step 3. A session missing from INDEX.md is invisible history."""
    index = (STATE / "INDEX.md").read_text(encoding="utf-8")
    sessions = sorted(p.stem for p in (STATE / "sessions").iterdir()
                      if p.is_file() and p.name != ".gitkeep")
    missing = [s for s in sessions if s not in index]
    assert not missing, f"session files with no INDEX.md row: {missing}"


def test_dashboard_has_a_parseable_last_reconciled_timestamp() -> None:
    """Protocol §6 step 3: without this the 24 h / 48 h staleness policy is unenforceable."""
    text = (STATE / "DASHBOARD.md").read_text(encoding="utf-8")
    m = re.search(r"\*\*Last Reconciled:\*\*\s*(\S+)", text)
    assert m, "DASHBOARD.md has no '**Last Reconciled:** <timestamp>' line (protocol §6 step 3)"
    stamp = m.group(1)
    assert re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2})?Z?$", stamp), (
        f"Last Reconciled must be an ISO-8601 UTC timestamp, got {stamp!r}"
    )


# ── The guard that matters: DASHBOARD must not drift from the registries ─────

def _dashboard_counts() -> dict[str, tuple[int, ...]]:
    text = (STATE / "DASHBOARD.md").read_text(encoding="utf-8")
    req = re.search(r"\*\*(\d+) VERIFIED · (\d+) FAILED · (\d+) UNVERIFIED\*\* of (\d+)", text)
    unres = re.search(r"\*\*(\d+) CLOSED · (\d+) DEFERRED · (\d+) OPEN\*\* of (\d+)", text)
    assert req, (
        "DASHBOARD.md no longer states requirements as "
        "'**N VERIFIED · N FAILED · N UNVERIFIED** of N' — keep the machine-readable shape"
    )
    assert unres, (
        "DASHBOARD.md no longer states UNRES as "
        "'**N CLOSED · N DEFERRED · N OPEN** of N' — keep the machine-readable shape"
    )
    return {
        "requirements": tuple(int(g) for g in req.groups()),
        "unres": tuple(int(g) for g in unres.groups()),
    }


def test_dashboard_requirement_counts_match_the_registry() -> None:
    """MACP Rule 3: DASHBOARD shows what IS. If it disagrees with the registry, it lies."""
    data = yaml.safe_load((ROOT / "spec/machine-readable/verification.yaml").read_text(encoding="utf-8"))
    records = data["verification_records"]
    verified = sum(1 for r in records if r["status"] == "VERIFIED")
    failed = sum(1 for r in records if r["status"] == "FAILED")
    unverified = sum(1 for r in records if r["status"] not in ("VERIFIED", "FAILED"))

    stated = _dashboard_counts()["requirements"]
    expected = (verified, failed, unverified, len(records))
    assert stated == expected, (
        f"DASHBOARD.md says VERIFIED/FAILED/UNVERIFIED/total = {stated} but "
        f"spec/machine-readable/verification.yaml says {expected}"
    )


def test_dashboard_unres_counts_match_the_registry() -> None:
    data = yaml.safe_load((ROOT / "spec/machine-readable/open_questions.yaml").read_text(encoding="utf-8"))
    questions = data["open_questions"]
    closed = sum(1 for q in questions if q["status"] == "CLOSED")
    deferred = sum(1 for q in questions if q["status"] == "DEFERRED")
    open_ = sum(1 for q in questions if q["status"] == "OPEN")

    stated = _dashboard_counts()["unres"]
    expected = (closed, deferred, open_, len(questions))
    assert stated == expected, (
        f"DASHBOARD.md says CLOSED/DEFERRED/OPEN/total = {stated} but "
        f"spec/machine-readable/open_questions.yaml says {expected}"
    )


def test_tier_boundary_stays_documented() -> None:
    """CONFLICT-001: state/ must never read as a source of specification rulings.

    DECISIONS.md is where coordination decisions live; it must point at spec/ rather
    than restating a ruling. This asserts the boundary is documented, so a future
    agent that reads only state/ still learns that Tier 2 is not theirs.
    """
    decisions = (STATE / "DECISIONS.md").read_text(encoding="utf-8")
    protocol = (STATE / "PROTOCOL.md").read_text(encoding="utf-8")
    for name, text in (("DECISIONS.md", decisions), ("PROTOCOL.md", protocol)):
        assert "Constraint D" in text, f"{name} no longer names the owner's authority constraint"
        assert "Tier 2" in text, f"{name} no longer documents the Tier 1/Tier 2 boundary"


def test_index_status_matches_the_registry() -> None:
    """INDEX.md and REGISTRY.md must agree on whether a session is active or ended.

    Both files carry a per-session status, so they can disagree. They did: the INDEX
    row for the in-flight session said `ended` while REGISTRY still had it `active`,
    because the row was written during an earlier (wrong) attempt to close the
    session. That is the same class of defect as a drifted DASHBOARD — two state
    files, two answers, and the reader has to guess which one is true.

    Deliberately asserts non-vacuity: if the table shape changes so no rows parse,
    this fails loudly instead of passing by finding nothing.
    """
    def rows(text: str) -> list[list[str]]:
        out = []
        for line in text.splitlines():
            if line.startswith("|") and "`" in line:
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                if len(cells) >= 6:
                    out.append(cells)
        return out

    def unquote(cell: str) -> str:
        return cell.strip().strip("*").strip().strip("`").strip()

    registry_status: dict[str, str] = {}
    for cells in rows((STATE / "REGISTRY.md").read_text(encoding="utf-8")):
        agent_id, session_id = unquote(cells[0]), unquote(cells[1])
        if AGENT_ID_RE.match(agent_id) and session_id.startswith("20"):
            registry_status[session_id] = unquote(cells[5]).lower()

    index_status: dict[str, str] = {}
    for cells in rows((STATE / "INDEX.md").read_text(encoding="utf-8")):
        session_id = unquote(cells[0])
        if session_id.startswith("20") and "-" in session_id:
            index_status[session_id] = unquote(cells[5]).lower()

    # Non-vacuity: both parses must actually have found rows.
    assert registry_status, "parsed no agent rows from REGISTRY.md — table shape changed?"
    assert index_status, "parsed no session rows from INDEX.md — table shape changed?"

    disagreements = {
        sid: (index_status[sid], registry_status[sid])
        for sid in index_status.keys() & registry_status.keys()
        if index_status[sid] != registry_status[sid]
    }
    assert not disagreements, (
        "INDEX.md and REGISTRY.md disagree on session status "
        f"(session: (INDEX, REGISTRY)): {disagreements}. "
        "Per DEC-007 a session stays `active` until the owner declares it over."
    )


def test_session_headers_match_the_schema_and_registry() -> None:
    """A6: every session file's metadata block exists and agrees with REGISTRY.md.

    The protocol requires a session file to open with a metadata block (Agent,
    Session ID, Started, Status, Branch, Base commit, Task, Files owned) and for
    those fields to match the agent's row in REGISTRY.md. Without the schema the
    rule "matches REGISTRY" is unenforceable — which is why it was added.

    This immediately found a real inconsistency when it was written: the in-flight
    session's header still said `Status: ended` from an earlier (wrong) attempt to
    close the session, while REGISTRY said `active`.
    """
    required = ("Agent", "Session ID", "Started", "Status", "Branch", "Base commit")
    sessions = sorted(p for p in (STATE / "sessions").iterdir()
                      if p.is_file() and p.name != ".gitkeep")
    assert sessions, "no session files to check — this test would pass vacuously"

    def field(text: str, name: str) -> str | None:
        m = re.search(rf"^\*\*{re.escape(name)}:\*\*\s*(.+?)\s*$", text, re.MULTILINE)
        return m.group(1).replace("`", "").strip() if m else None

    registry = (STATE / "REGISTRY.md").read_text(encoding="utf-8")
    reg_status = {
        m.group(1): m.group(2).lower()
        for m in re.finditer(r"^\|\s*`[A-Za-z0-9]{4}`\s*\|\s*`([^`]+)`\s*\|[^|]*\|[^|]*\|[^|]*\|\s*\*{0,2}(\w+)\*{0,2}\s*\|",
                             registry, re.MULTILINE)
    }
    assert reg_status, "parsed no session statuses from REGISTRY.md — table shape changed?"

    problems: list[str] = []
    for path in sessions:
        text = path.read_text(encoding="utf-8")
        missing = [f for f in required if field(text, f) is None]
        if missing:
            problems.append(f"{path.name}: missing header field(s) {missing}")
            continue
        sid = field(text, "Session ID")
        header_status = (field(text, "Status") or "").lower()
        if sid in reg_status and header_status != reg_status[sid]:
            problems.append(
                f"{path.name}: header Status={header_status!r} but REGISTRY says "
                f"{reg_status[sid]!r} (DEC-007: a session stays active until the owner ends it)"
            )
        # The filename must carry the same session id as the header (protocol §2).
        if sid and path.stem != sid:
            problems.append(f"{path.name}: filename does not match Session ID {sid!r}")

    assert not problems, "session header schema violations: " + "; ".join(problems)


def test_no_duplicate_record_ids() -> None:
    """DEBT/DEC/CONFLICT/BLK ids must be unique within their register.

    A duplicated entry makes the register ambiguous — two records, one id, and a
    reader cannot tell which is authoritative. It happened for real: a DEBT-007
    append ran twice and the file carried the entry at two places, identical except
    for the separator. Nothing caught it; it was found by accident while editing the
    same file.

    Cheap to check, and it is the kind of thing that only ever gets harder to spot
    as a register grows.
    """
    registers = {
        "DEBT.md": r"^## (DEBT-\d+)",
        "DECISIONS.md": r"^## (DEC-\d+)",
        "BLOCKERS.md": r"^#{2,3} (BLK-\d+)",
        "INDEX.md": None,  # no id column of its own
    }
    duplicates: dict[str, list[str]] = {}
    for name, pattern in registers.items():
        if pattern is None:
            continue
        text = (STATE / name).read_text(encoding="utf-8")
        ids = re.findall(pattern, text, re.MULTILINE)
        assert ids, f"found no record ids in {name} — heading shape changed?"
        repeated = sorted({i for i in ids if ids.count(i) > 1})
        if repeated:
            duplicates[name] = repeated
    assert not duplicates, f"duplicate record ids (a register became ambiguous): {duplicates}"

    # Conflict files are keyed by filename.
    conflict_ids = sorted(p.stem.split("-")[1] for p in (STATE / "conflicts").glob("CONFLICT-*.md"))
    assert conflict_ids, "found no conflict files — glob shape changed?"
    assert len(conflict_ids) == len(set(conflict_ids)), (
        f"duplicate conflict numbers: {conflict_ids}"
    )


def test_active_session_files_owned_covers_what_it_changed() -> None:
    """A session's `files_owned` must cover every file it actually changed.

    `files_owned` is the ownership claim other agents read before editing. If it
    under-declares, another agent sees a file as free and can edit it while the
    session is still working there — the exact conflict the field exists to prevent.

    Found by running the protocol's own verification loop (Amendment 1 §A2) against
    this repository's state: the active row claimed `state/**` and `AGENTS.md` while
    the session had also changed four files outside that claim
    (`.github/workflows/{ci,release}.yml`, `tests/repo/test_promotion_chain.py`,
    `tests/repo/test_state_tree.py`).

    Only ACTIVE rows are checked: an ended session's claim is deliberately cleared.
    The comparison is `git diff --name-only <base>..HEAD`, using the `Base commit`
    from the session header — so it measures the session's real footprint.
    """
    import fnmatch
    import subprocess

    registry = (STATE / "REGISTRY.md").read_text(encoding="utf-8")
    rows = re.findall(
        r"^\|\s*`[A-Za-z0-9]{4}`\s*\|\s*`([^`]+)`\s*\|[^|]*\|[^|]*\|\s*([^|]*?)\s*\|\s*\*{0,2}(\w+)\*{0,2}\s*\|",
        registry, re.MULTILINE,
    )
    # Zero active sessions is the NORMAL post-shutdown state, not a parse failure.
    # An earlier version asserted `active` was non-empty to avoid vacuity, which
    # broke the very shutdown sequence this guard belongs to. The parse is still
    # verified separately, so an empty result here means "nobody is working", not
    # "the table shape changed".
    assert rows, "parsed no agent rows from REGISTRY.md — table shape changed?"
    active = [(sid, owned) for sid, owned, status in rows if status.lower() == "active"]

    problems: list[str] = []
    for sid, owned in active:
        header = STATE / "sessions" / f"{sid}.md"
        assert header.is_file(), f"active session {sid} has no session file"
        base = re.search(r"^\*\*Base commit:\*\*\s*`?([0-9a-f]{7,40})`?", header.read_text(encoding="utf-8"), re.MULTILINE)
        if not base:
            problems.append(f"{sid}: no Base commit in the header, cannot measure its footprint")
            continue
        changed = subprocess.run(
            ["git", "diff", "--name-only", f"{base.group(1)}..HEAD"],
            cwd=ROOT, capture_output=True, text=True,
        ).stdout.split()
        if not changed:
            continue  # nothing committed yet this session
        globs = [g.strip().strip("`") for g in owned.split(",") if g.strip() and g.strip() != "—"]
        uncovered = [f for f in changed if not any(fnmatch.fnmatch(f, g) for g in globs)]
        if uncovered:
            problems.append(
                f"{sid}: files_owned does not cover {uncovered} (declared: {globs}) — "
                "another agent would read these as free"
            )

    assert not problems, "ownership claim under-declares: " + "; ".join(problems)


def test_commitlint_accepts_the_protocol_commit_type() -> None:
    """CONFLICT-002 / DEC-006: the protocol's shutdown commit format must stay valid.

    MACP §Shutdown step 6 mandates `state: <agent-id> session <session-id>`, and
    `Conventional Commits (commitlint)` is a *required* status check on main. If
    `state` is ever dropped from the type-enum, every future MACP shutdown commit
    fails a required check — at a distance from the change that caused it, which is
    exactly the kind of coupling that should be guarded rather than documented.

    This asserts the coupling mechanically instead of trusting the inline comment in
    commitlint.config.cjs to survive.
    """
    import json
    import subprocess

    config = ROOT / "commitlint.config.cjs"
    assert config.is_file(), "commitlint.config.cjs is missing — the commit gate cannot run"
    # Parse the CJS config through node so we read the real exported value, not a regex guess.
    out = subprocess.run(
        ["node", "-e", f"console.log(JSON.stringify(require({json.dumps(str(config))}).rules['type-enum'][2]))"],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert out.returncode == 0, f"could not read commitlint config: {out.stderr}"
    types = json.loads(out.stdout)
    assert "state" in types, (
        "commitlint no longer accepts the `state` type, but MACP §Shutdown step 6 mandates "
        f"`state: <agent-id> session <session-id>`. Types are: {types}. "
        "See state/conflicts/CONFLICT-002-protocol-commit-type.md"
    )


if __name__ == "__main__":  # self-hosting runner, matching tests/repo/test_gate_fail_closed.py
    checks = [
        test_required_structure_exists,
        test_no_placeholder_text,
        test_every_relative_link_resolves,
        test_session_filenames_follow_the_protocol_convention,
        test_registry_agent_ids_are_four_alphanumeric_characters,
        test_plan_filenames_follow_the_protocol_convention,
        test_every_session_file_has_an_index_row,
        test_dashboard_has_a_parseable_last_reconciled_timestamp,
        test_dashboard_requirement_counts_match_the_registry,
        test_dashboard_unres_counts_match_the_registry,
        test_tier_boundary_stays_documented,
        test_commitlint_accepts_the_protocol_commit_type,
        test_index_status_matches_the_registry,
        test_session_headers_match_the_schema_and_registry,
        test_no_duplicate_record_ids,
        test_active_session_files_owned_covers_what_it_changed,
    ]
    failures = 0
    for fn in checks:
        try:
            fn()
            print(f"PASS: {fn.__name__}")
        except Exception as exc:  # noqa: BLE001
            failures += 1
            print(f"FAIL: {fn.__name__} — {exc}")
    print(f"{'FAIL' if failures else 'PASS'}: state tree ({len(checks) - failures}/{len(checks)})")
    sys.exit(1 if failures else 0)
