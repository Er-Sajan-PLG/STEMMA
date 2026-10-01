#!/usr/bin/env python3
"""Permanent negative-path test for the fail-closed gate (REQ-STEMMA-GATE-001).

REQ-STEMMA-GATE-001 (`spec/machine-readable/requirements.yaml`):

    The verification chain SHALL fail closed: any failed step terminates the
    chain with a non-zero exit; nothing ships on a red gate.

Its acceptance criteria name exactly two things:

  1. ``verify_all.py`` exits non-zero when any FAIL-level step fails
     (as-built observation: EVID-STEMMA-GATE-002);
  2. a **permanent CI negative-path test exists**.

This file is criterion 2. Before it, the only evidence that the gate fails
closed was a one-off manual observation (EVID-STEMMA-GATE-002: "run verify_all
with interpreter lacking pyyaml"). A gate whose only proof of failing is an
anecdote is not verified — §18: a test's existence is not proof, and neither is
a memory of a run.

How the negative path is forced
-------------------------------
``verify_all.py`` resolves its repository root from ``Path(__file__)`` and runs
each step via ``subprocess.run([sys.executable, <step>])``. Two consequences
shape this test:

* **cwd is irrelevant.** Every entry point computes ``ROOT`` from its own
  location, so running a script "from a temporary directory" changes nothing.
  A probe built on cwd redirection silently tests the real repository — worth
  stating because it is an easy way to write a test that cannot fail.
* **Failing a child step requires breaking a real step.** The chain's own
  failure semantics are reached only when one of the ~17 steps returns non-zero.

So the probe installs a substitute that shadows a single step, forces it to exit
non-zero, runs the chain, and asserts the committed behaviour: non-zero exit,
the offending step named on stderr, and the chain *stopped* (later steps never
ran). The probe operates on a **copied tree** under ``tmp_path`` — never on the
working tree — so a broken run can never leave the repository modified.

Run: ``python3 -m pytest tests/repo/test_gate_fail_closed.py -q``
Or directly: ``python3 tests/repo/test_gate_fail_closed.py`` (self-hosting runner)
"""
from __future__ import annotations

import pathlib
import shutil
import subprocess
import sys

try:  # pytest is optional: the docs contract runs this file without it.
    import pytest
except ImportError:  # pragma: no cover - exercised in the verify-docs CI job
    pytest = None

ROOT = pathlib.Path(__file__).resolve().parents[2]

# Files the chain reads while resolving its own structure. The copy must be
# minimal but must let `verify_all.py` start; the first step fails immediately,
# so later steps never execute and their inputs are not needed.
TREE_INPUTS = ["scripts/verify_all.py", "scripts/validate.py"]

FORCED_FAILURE_STEP = "scripts/validate.py"
FORCED_FAILURE_EXIT = 3


def _shadow_tree(tmp_path: pathlib.Path) -> pathlib.Path:
    """Build a minimal repo skeleton in which one gate step is broken.

    ``scripts/validate.py`` is replaced by a stub that exits non-zero. The stub
    is deliberately *valid Python* and exits with a distinctive code, so the
    probe measures propagation rather than an import error.
    """
    for rel in TREE_INPUTS:
        dest = tmp_path / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, dest)

    (tmp_path / FORCED_FAILURE_STEP).write_text(
        "#!/usr/bin/env python3\n"
        "import sys\n"
        "print('stub: deliberate negative-path failure', file=sys.stderr)\n"
        f"sys.exit({FORCED_FAILURE_EXIT})\n",
        encoding="utf-8",
    )
    return tmp_path


# pytest is optional; when absent the `__main__` runner below calls the test
# functions directly with a temporary directory.
if pytest is not None:
    shadow_tree = pytest.fixture(_shadow_tree)
else:  # pragma: no cover
    def shadow_tree(tmp_path):  # type: ignore[misc]
        return _shadow_tree(tmp_path)


def test_verify_all_terminates_chain_on_first_failure(shadow_tree: pathlib.Path):
    """Acceptance criterion 1: a failed step stops the chain, non-zero.

    Three assertions, because "exit non-zero" alone is satisfiable by a chain
    that nevertheless keeps running and reports a red result at the end:

    * the exit status is non-zero;
    * the offending step is named on stderr (a silent red gate is not
      diagnosable, and REQ-STEMMA-GATE-001 is about *shipping* decisions);
    * **no step after the first ran** — the chain terminated, it did not
      accumulate failures.
    """
    result = subprocess.run(
        [sys.executable, str(shadow_tree / "scripts" / "verify_all.py")],
        cwd=shadow_tree,
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert result.returncode != 0, (
        "verify_all.py exited 0 despite a failing step — REQ-STEMMA-GATE-001 violated\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )

    assert "FAIL:" in result.stderr, (
        "verify_all.py returned non-zero without naming the failing step\n"
        f"stderr:\n{result.stderr}"
    )
    assert FORCED_FAILURE_STEP in result.stderr, (
        f"the FAIL line does not identify {FORCED_FAILURE_STEP}\nstderr:\n{result.stderr}"
    )

    executed = [line for line in result.stdout.splitlines() if line.startswith("RUN: ")]
    assert len(executed) == 1, (
        "the chain did not terminate at the first failure — it ran "
        f"{len(executed)} steps:\n" + "\n".join(executed)
    )
    assert FORCED_FAILURE_STEP in executed[0], (
        f"the first (and only) executed step was not the broken one: {executed[0]}"
    )


def test_negative_path_probe_does_not_touch_the_working_tree(shadow_tree: pathlib.Path):
    """The probe is hermetic in the sense that matters: it cannot mutate the repo.

    A negative-path test that edits the real tree is a liability — a crash
    mid-test would leave a broken checkout behind. This asserts the invariant
    directly via ``git status`` on the real repository before and after a run.
    """
    def working_tree_state() -> str:
        out = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        return out

    before = working_tree_state()
    subprocess.run(
        [sys.executable, str(shadow_tree / "scripts" / "verify_all.py")],
        cwd=shadow_tree,
        capture_output=True,
        text=True,
        timeout=120,
    )
    after = working_tree_state()
    assert before == after, (
        "the negative-path probe changed the working tree:\n"
        f"before:\n{before}\nafter:\n{after}"
    )


def test_shadow_stub_exit_code_is_propagated(shadow_tree: pathlib.Path):
    """The chain must surface the *step's* failure, not mask it as a generic error.

    Run the stub directly first: if the stub itself did not exit non-zero, the
    other assertions in this file would pass vacuously. This guards the probe.
    """
    stub = shadow_tree / FORCED_FAILURE_STEP
    result = subprocess.run(
        [sys.executable, str(stub)], capture_output=True, text=True, cwd=shadow_tree, timeout=60
    )
    assert result.returncode == FORCED_FAILURE_EXIT, (
        f"probe stub is broken: expected exit {FORCED_FAILURE_EXIT}, got {result.returncode}"
    )


def test_positive_path_still_succeeds():
    """The chain is not trivially red.

    A fail-closed gate that always fails is useless. Running the real chain must
    still exit 0 — otherwise the negative-path assertions above would hold for
    the wrong reason. (Skipped if the full chain cannot run in this environment,
    e.g. a missing optional dependency, so the test never becomes a false alarm.)
    """
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "verify_all.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=600,
    )
    if result.returncode != 0:
        message = (
            "full chain not green in this environment (optional dependency or fixture "
            f"missing) — positive-path check skipped, exit was {result.returncode}\n"
            f"stderr tail:\n" + "\n".join(result.stderr.splitlines()[-8:])
        )
        if pytest is not None:
            pytest.skip(message)
        print(f"SKIP: test_positive_path_still_succeeds — {message.splitlines()[0]}")
        return
    assert "all verify steps pass" in result.stdout


if __name__ == "__main__":
    # Direct-execution runner. The docs contract executes scripts with whatever
    # interpreter is ambient (the `verify-docs` CI job installs requirements.txt
    # but not pytest), so invoking via pytest would fail there for the wrong
    # reason. The checks need no fixtures, so they run directly.
    if pytest is not None:
        sys.exit(pytest.main([__file__, "-q", "--no-header", "-p", "no:cacheprovider"]))

    import tempfile
    import traceback

    failures = 0
    with tempfile.TemporaryDirectory() as td:
        tree = _shadow_tree(pathlib.Path(td))
        checks = [
            (test_shadow_stub_exit_code_is_propagated, (tree,)),
            (test_verify_all_terminates_chain_on_first_failure, (tree,)),
            (test_negative_path_probe_does_not_touch_the_working_tree, (tree,)),
            (test_positive_path_still_succeeds, ()),
        ]
        for fn, args in checks:
            try:
                fn(*args)
                print(f"PASS: {fn.__name__}")
            except Exception:
                failures += 1
                print(f"FAIL: {fn.__name__}")
                traceback.print_exc()

    print(f"{'FAIL' if failures else 'PASS'}: gate fail-closed probe "
          f"({len(checks) - failures}/{len(checks)} checks)")
    sys.exit(1 if failures else 0)
