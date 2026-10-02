#!/usr/bin/env python3
"""Atomic writes for gate-compared derived artifacts (scripts/atomic_write.py).

Regression test for the race that produced a spurious failure in
tests/repo/test_export_consumers.py: running the pytest suite while
scripts/verify_all.py regenerated exports let `export_consumers.py --all --check`
read a half-written bundle and report it stale.

`Path.write_text` opens the destination with mode "w" — truncating it — and only
then writes the bytes, so a concurrent reader can observe an empty or partial
file. The fix stages the content in a sibling temp file and `os.replace`s it over
the destination.

Structure of this file, and why:

* ``test_non_atomic_write_exposes_a_partial_read`` is a **negative control**. It
  reproduces the truncate-then-write window and asserts a reader really does
  observe a state that is neither the old nor the new document. Without it, the
  atomicity assertions below could pass vacuously — e.g. if the reader thread
  simply never got scheduled.
* ``test_atomic_write_holds_the_previous_document_while_staging`` admits the
  reader inside the staging window deterministically (by gating ``os.replace``),
  which is stronger than a timing-based race probe.
* The remaining tests pin the properties the exporters depend on: byte-parity
  with ``write_text`` (so determinism and the CI freshness diff are unaffected),
  staging-file hygiene, failure safety, mode preservation, and a structural guard
  that stops a new gate-compared writer being added non-atomically.
"""
from __future__ import annotations

import json
import pathlib
import stat
import sys
import threading

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import atomic_write  # noqa: E402
from atomic_write import write_text_atomic  # noqa: E402

# Writers whose output a gate byte-compares (CI `git diff --exit-code -- exports
# reports`, a script's `--check` mode, or an assertion in this suite). Every one
# must stage-and-rename. Adding a new gate-compared writer means adding it here.
ATOMIC_WRITER_FILES = (
    "scripts/validate.py",
    "scripts/export_jsonld.py",
    "scripts/export_subsets.py",
    "scripts/export_review_aware.py",
    "scripts/graph_analysis.py",
    "scripts/export_consumers.py",
    "scripts/status_truth.py",
    "scripts/docs.py",
    # G2 (MACP gate design): generates the DASHBOARD's Gate Status block, which CI
    # byte-compares via `gate_status.py --check` plus a blanket `git diff --exit-code`.
    "scripts/gate_status.py",
)

# Globs the exporters and the CI freshness step use to find their artifacts. A
# staging file must match none of them, or a half-written temp could be picked up
# as a real artifact.
ARTIFACT_GLOBS = ("*.json", "*.jsonld", "knowledge.*.json", "*")


# ── Non-vacuity: the window is real ──────────────────────────────────────────

def test_non_atomic_write_exposes_a_partial_read(tmp_path: pathlib.Path) -> None:
    """Negative control for the whole file.

    Reproduces `Path.write_text` exactly — open mode "w" truncates, then the bytes
    are written — and admits the reader while the destination is truncated. The
    reader must observe something that is neither the old nor the new document.
    """
    target = tmp_path / "artifact.json"
    old = json.dumps({"v": "old"})
    new = json.dumps({"v": "new", "pad": "n" * 4096})
    target.write_text(old, encoding="utf-8")

    read_done = threading.Event()
    observed: list[str] = []

    def reader() -> None:
        observed.append(target.read_text(encoding="utf-8"))
        read_done.set()

    with open(target, "w", encoding="utf-8") as handle:  # truncates on open
        handle.flush()
        thread = threading.Thread(target=reader)
        thread.start()
        assert read_done.wait(timeout=10), "reader thread never ran"
        handle.write(new)  # the new bytes land only here
    thread.join(timeout=10)

    assert observed, "negative control never read the file"
    assert observed[0] not in (old, new), (
        "the non-atomic write was NOT observed torn, so this control is vacuous "
        "and the atomicity assertions below would prove nothing"
    )
    # The observed state is exactly the failure the suite hit: content that is not
    # a complete document. For a JSON artifact that is a decode error or a
    # mismatch against freshly generated text.
    with pytest.raises(json.JSONDecodeError):
        json.loads(observed[0])


# ── Atomicity ────────────────────────────────────────────────────────────────

def test_atomic_write_holds_the_previous_document_while_staging(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Deterministic window: the reader runs *inside* the staging step.

    ``os.replace`` is gated open, so the reader is admitted at exactly the moment
    the new content exists but has not yet been published. It must still see the
    complete previous document — the property a bare ``write_text`` cannot offer.
    """
    target = tmp_path / "artifact.json"
    old = json.dumps({"v": "old"})
    new = json.dumps({"v": "new", "pad": "n" * 4096})
    write_text_atomic(target, old)

    staged = threading.Event()
    release = threading.Event()
    real_replace = atomic_write.os.replace

    def gated_replace(src, dst):  # type: ignore[no-untyped-def]
        staged.set()
        assert release.wait(timeout=10), "test deadlocked waiting for release"
        real_replace(src, dst)

    monkeypatch.setattr(atomic_write.os, "replace", gated_replace)

    failures: list[BaseException] = []

    def writer() -> None:
        try:
            write_text_atomic(target, new)
        except BaseException as exc:  # pragma: no cover - surfaced below
            failures.append(exc)

    thread = threading.Thread(target=writer)
    thread.start()
    assert staged.wait(timeout=10), "writer never reached the publish step"

    # Inside the staging window: new content is fully written to the temp file,
    # destination untouched.
    assert target.read_text(encoding="utf-8") == old, (
        "the destination was observable in a partial state while staging"
    )

    release.set()
    thread.join(timeout=10)
    assert not failures, failures
    assert target.read_text(encoding="utf-8") == new


def test_concurrent_readers_never_observe_a_torn_artifact(tmp_path: pathlib.Path) -> None:
    """Stress the real pattern: a reader looping while the artifact is rewritten."""
    target = tmp_path / "artifact.json"
    first = json.dumps({"v": "first", "pad": "a" * 8192})
    second = json.dumps({"v": "second", "pad": "b" * 8192})
    write_text_atomic(target, first)

    stop = threading.Event()
    reads: list[str] = []

    def reader() -> None:
        while not stop.is_set():
            reads.append(target.read_text(encoding="utf-8"))

    thread = threading.Thread(target=reader)
    thread.start()
    try:
        for i in range(400):
            write_text_atomic(target, first if i % 2 else second)
    finally:
        stop.set()
        thread.join(timeout=10)

    assert reads, "reader never ran — the stress assertion would be vacuous"
    torn = sorted({r for r in reads if r not in (first, second)})
    assert not torn, f"observed {len(torn)} torn read(s); first was {torn[0]!r}"


# ── Properties the exporters depend on ───────────────────────────────────────

def test_output_is_byte_identical_to_write_text(tmp_path: pathlib.Path) -> None:
    """Export determinism and the CI freshness diff must be unaffected."""
    payload = json.dumps({"a": 1, "unicode": "café — em dash"}, indent=2, ensure_ascii=False) + "\n"
    plain = tmp_path / "plain.json"
    atomic = tmp_path / "atomic.json"
    plain.write_text(payload, encoding="utf-8")
    write_text_atomic(atomic, payload)
    assert atomic.read_bytes() == plain.read_bytes()


def test_creates_parent_directories(tmp_path: pathlib.Path) -> None:
    target = tmp_path / "deep" / "nested" / "artifact.json"
    write_text_atomic(target, "{}\n")
    assert target.read_text(encoding="utf-8") == "{}\n"


def test_leaves_no_staging_file_behind(tmp_path: pathlib.Path) -> None:
    target = tmp_path / "artifact.json"
    for i in range(25):
        write_text_atomic(target, json.dumps({"i": i}))
    leftovers = sorted(p.name for p in tmp_path.iterdir() if p.name != target.name)
    assert leftovers == [], f"staging files left behind: {leftovers}"


def test_failed_write_preserves_the_previous_artifact(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A failed regeneration must not destroy the last good artifact."""
    target = tmp_path / "artifact.json"
    write_text_atomic(target, '{"v": "good"}')

    class DiskFull(RuntimeError):
        pass

    def exploding_replace(src, dst):  # type: ignore[no-untyped-def]
        raise DiskFull("no space left on device")

    monkeypatch.setattr(atomic_write.os, "replace", exploding_replace)
    with pytest.raises(DiskFull):
        write_text_atomic(target, '{"v": "bad"}')

    assert target.read_text(encoding="utf-8") == '{"v": "good"}'
    leftovers = sorted(p.name for p in tmp_path.iterdir() if p.name != target.name)
    assert leftovers == [], f"staging file stranded after failure: {leftovers}"


def test_staging_name_matches_no_artifact_glob(tmp_path: pathlib.Path,
                                               monkeypatch: pytest.MonkeyPatch) -> None:
    """A staged file must never be mistaken for a real artifact."""
    import fnmatch

    target = tmp_path / "knowledge.json"
    captured: list[str] = []
    real_replace = atomic_write.os.replace

    def capturing_replace(src, dst):  # type: ignore[no-untyped-def]
        captured.append(pathlib.Path(src).name)
        real_replace(src, dst)

    monkeypatch.setattr(atomic_write.os, "replace", capturing_replace)
    write_text_atomic(target, "{}\n")

    assert len(captured) == 1
    staged_name = captured[0]
    for pattern in ARTIFACT_GLOBS:
        if pattern == "*":
            continue  # trivially matches; covered by the gitignore rule below
        assert not fnmatch.fnmatch(staged_name, pattern), (
            f"staging file {staged_name!r} matches artifact glob {pattern!r}"
        )
    # Dot-prefixed so the `.gitignore` rule `.*.tmp` hides it if a crash strands it.
    assert staged_name.startswith(".") and staged_name.endswith(".tmp"), staged_name


def test_mode_matches_a_plain_write(tmp_path: pathlib.Path) -> None:
    """mkstemp creates 0o600; the published file must not become owner-only."""
    plain = tmp_path / "plain.json"
    plain.write_text("x", encoding="utf-8")
    atomic = tmp_path / "atomic.json"
    write_text_atomic(atomic, "x")
    assert stat.S_IMODE(atomic.stat().st_mode) == stat.S_IMODE(plain.stat().st_mode)


# ── Regression guard: no new non-atomic gate-compared writer ─────────────────

def test_gate_compared_writers_use_the_atomic_helper() -> None:
    """Every gate-compared writer stages-and-renames; none calls bare write_text.

    Guards the fix against reintroduction. If a legitimate non-artifact
    ``write_text`` is ever needed in one of these files, add it to an explicit
    allow-list here rather than dropping the check — the point is that the
    decision is made deliberately.
    """
    missing: list[str] = []
    offenders: dict[str, list[str]] = {}
    for rel in ATOMIC_WRITER_FILES:
        src = (ROOT / rel).read_text(encoding="utf-8")
        if "write_text_atomic" not in src:
            missing.append(rel)
        # Strip the helper's name first so `write_text_atomic(` cannot be mistaken
        # for a bare call.
        stripped = src.replace("write_text_atomic", "ATOMIC")
        bare = [ln.strip() for ln in stripped.splitlines() if ".write_text(" in ln]
        if bare:
            offenders[rel] = bare

    assert not missing, f"gate-compared writers not using the atomic helper: {missing}"
    assert not offenders, (
        "these files still write a gate-compared artifact with bare "
        f"write_text (a torn read is observable): {offenders}"
    )


def test_atomic_write_module_is_importable_as_a_script_sibling() -> None:
    """The exporters import it as a sibling (scripts/ is on sys.path)."""
    assert (ROOT / "scripts" / "atomic_write.py").is_file()
    assert callable(write_text_atomic)
