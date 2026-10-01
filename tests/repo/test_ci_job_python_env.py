#!/usr/bin/env python3
"""CI hygiene: no job may run `pip install` on a bare runner.

Why this test exists
--------------------
`Verify Governance Docs` failed on an unrelated PR with:

    pip._vendor.urllib3.exceptions.ReadTimeoutError:
      HTTPSConnectionPool(host='files.pythonhosted.org', port=443): Read timed out.

That job was the only one in `ci.yml` that ran `pip install` **without**
`actions/setup-python`. Every other Python job pinned 3.11 first. With no
setup step, pip resolves against the runner image's own interpreter, which puts
a network fetch on the critical path of the very step that gates the PR — so a
transient PyPI blip turns into a red governance check and, via the
`All Checks Green` aggregate, blocks the merge.

This is a *structural* defect, not a flake: it recurred as a latent copy in
`no-wall-clock`. Static text assertions are the right tool here because the
invariant is exactly "this job's step list contains a setup step before it
contains a pip install" — readable from the file, no execution needed.

Scope note: this asserts ordering within a job only. It deliberately does not
try to verify that the *right* packages get installed, nor that pip is called
with any particular flags.
"""
from __future__ import annotations

import pathlib
import re

import pytest
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
CI = ROOT / ".github" / "workflows" / "ci.yml"

# A step whose `run` (or `uses`) performs an install from an index. Matches the
# commands actually used in this repo; `pip install -e` and `pip install -r`.
_INSTALL_RE = re.compile(r"^\s*pip3?\s+install\b", re.MULTILINE)
_SETUP_USES = "actions/setup-python"


def _jobs():
    doc = yaml.safe_load(CI.read_text(encoding="utf-8"))
    return doc["jobs"]


def _steps(job: dict) -> list[dict]:
    return list(job.get("steps") or [])


def _is_install_step(step: dict) -> bool:
    run = step.get("run") or ""
    return bool(_INSTALL_RE.search(run))


def _is_setup_step(step: dict) -> bool:
    return _SETUP_USES in (step.get("uses") or "")


def test_ci_yml_is_parseable_and_has_jobs():
    """Guard the guard: if this fails, every other assertion here is vacuous."""
    jobs = _jobs()
    assert jobs, "ci.yml parsed to zero jobs — the file is malformed"
    assert "all-green" in jobs, "the aggregate gate job disappeared from ci.yml"


def test_no_job_installs_before_setting_up_python():
    offenders: list[str] = []
    for name, job in _jobs().items():
        steps = _steps(job)
        install_at = None
        setup_at = None
        for i, step in enumerate(steps):
            if setup_at is None and _is_setup_step(step):
                setup_at = i
            if install_at is None and _is_install_step(step):
                install_at = i
        if install_at is None:
            continue
        if setup_at is None:
            offenders.append(f"{name}: runs pip install but never sets up Python")
        elif setup_at > install_at:
            offenders.append(
                f"{name}: sets up Python at step {setup_at} but installs at step {install_at}"
            )
    assert not offenders, (
        "CI job(s) install packages without a preceding `actions/setup-python` step. "
        "Without it pip runs against the runner image and a PyPI read timeout fails "
        "an unrelated PR. Offenders: " + "; ".join(offenders)
    )


def test_setup_python_steps_pin_a_version():
    """An unpinned setup-python silently tracks whatever the runner default is."""
    unpinned: list[str] = []
    for name, job in _jobs().items():
        for step in _steps(job):
            if not _is_setup_step(step):
                continue
            version = (step.get("with") or {}).get("python-version")
            if not version:
                unpinned.append(name)
    assert not unpinned, (
        "setup-python step without `with: python-version:` in job(s): "
        + ", ".join(sorted(set(unpinned)))
    )


def test_the_regression_that_motivated_this_test_stays_fixed():
    """Pin the two jobs that actually carried the defect.

    Named explicitly so that a future refactor that drops the setup step from
    either job re-fails here with the job's name in the message, rather than
    only in the generic sweep above.
    """
    jobs = _jobs()
    for job_id in ("verify-docs", "no-wall-clock"):
        assert job_id in jobs, f"{job_id} vanished from ci.yml"
        assert any(_is_setup_step(s) for s in _steps(jobs[job_id])), (
            f"{job_id} lost its `Set up Python` step — this is the exact job that "
            f"failed with a PyPI ReadTimeoutError when it ran pip on a bare runner."
        )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
