#!/usr/bin/env python3
"""Atomic writes for gate-compared derived artifacts.

Why this exists
---------------
Every exporter used ``Path.write_text``, which opens the destination with mode
``"w"`` — truncating it — and only then writes the new bytes. Between those two
moments the file is empty or a prefix of the new content. A reader that opens it
in that window sees a partial document.

That window is invisible in CI, where each artifact set is produced and consumed
by a single job. It is real locally: running the pytest suite while
``scripts/verify_all.py`` regenerated exports produced a spurious failure in
``tests/repo/test_export_consumers.py``, because ``export_consumers.py --all
--check`` read a half-written bundle and reported it stale.

The fix
-------
Write to a temporary file in the *same directory*, flush it, then ``os.replace``
it over the destination. ``os.replace`` is atomic on POSIX and on Windows, so a
concurrent reader observes either the previous complete file or the new complete
file — never an intermediate state.

Scope
-----
Applied to artifacts whose bytes are compared by a gate (the CI
``git diff --exit-code -- exports reports`` freshness step, a script's ``--check``
mode, or a pytest assertion): everything under ``exports/`` and ``reports/`` that
the verification chain regenerates, plus the README status block and the
documentation-coverage table that the pre-push hook regenerates and then
byte-compares.

Deliberately NOT applied to writers whose output no gate byte-compares: campaign
and triage reports, ingestion workflow staging, and canonical ``content/`` /
``connections/`` / ``sources/`` edits made by the review tools. Those are not
read concurrently with a regeneration, and converting them would widen the change
without closing a real window. ``tests/repo/test_atomic_artifact_writes.py``
pins the list so a new gate-compared writer cannot be added non-atomically by
accident.

Note on the residual window: atomicity makes each *file* consistent, but the
chain still publishes a *set* of artifacts over time (base export first, bundles
derived from it after). A ``--check`` running concurrently with a genuine content
change could therefore still see a new base against an old bundle. That is not a
torn read and is not fixable by atomicity; it is why the chain and the suite are
separate CI jobs and why content changes are not made concurrently with a run.
"""
from __future__ import annotations

import os
import pathlib
import tempfile
from typing import Any, Callable

__all__ = ["write_text_atomic", "write_bytes_atomic"]


def _default_file_mode() -> int:
    """The mode a plain ``open(path, "w")`` would give a new file.

    ``tempfile.mkstemp`` creates files with mode 0o600. Without this, every
    atomically-written artifact would silently become owner-only, which is a
    behaviour change relative to ``Path.write_text``.
    """
    current = os.umask(0)
    os.umask(current)
    return 0o666 & ~current


def _atomic_replace(path: pathlib.Path, writer: Callable[[Any], Any], *,
                    mode: str, encoding: str | None = None) -> None:
    """Stage ``writer(handle)`` in ``path``'s directory, then rename it over.

    Any failure removes the staging file and leaves the destination untouched — a
    failed regeneration must not destroy the last good artifact.
    """
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Dot-prefixed and suffixed `.tmp` so the staging file matches none of the
    # artifact globs (`*.json`, `knowledge.*.json`, `exports/consumers/*/*.json`)
    # and is covered by the `.*.tmp` rule in .gitignore if a crash strands it.
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp")
    tmp = pathlib.Path(tmp_name)
    try:
        with os.fdopen(fd, mode, encoding=encoding) as handle:
            writer(handle)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(tmp, _default_file_mode())
        os.replace(tmp, path)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise


def write_text_atomic(path: str | os.PathLike[str], text: str, encoding: str = "utf-8") -> None:
    """Write ``text`` to ``path`` atomically (readers never see a partial file).

    Byte-for-byte equivalent to ``Path.write_text(text, encoding=encoding)`` for
    the same inputs — same encoding, same default newline handling — so export
    determinism and the CI freshness diff are unaffected.
    """
    _atomic_replace(pathlib.Path(path), lambda handle: handle.write(text),
                    mode="w", encoding=encoding)


def write_bytes_atomic(path: str | os.PathLike[str], data: bytes) -> None:
    """Byte-oriented counterpart to :func:`write_text_atomic`."""
    _atomic_replace(pathlib.Path(path), lambda handle: handle.write(data), mode="wb")
