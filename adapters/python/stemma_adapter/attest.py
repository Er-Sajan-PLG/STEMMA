"""Sigstore build-attestation checks for release files (``stemma-adapter[verify]``).

Imported only when attestation verification is requested; the core loader and
``import stemma_adapter`` never import ``sigstore``.

The policy is built from caller-supplied values only:

* certificate identity  ``https://github.com/<repo>/.github/workflows/release.yml@<ref>``
* OIDC issuer           ``https://token.actions.githubusercontent.com``
* workflow repository   ``<repo>``, workflow ref ``<ref>``, trigger ``push``

and one verified in-toto statement (SLSA provenance v1) must list every
required subject by name *and* sha256 digest (manifest, checksum list, export).

Trust root: the Sigstore public-good root embedded in the installed
``sigstore`` package (``Verifier.production(offline=True)``) — no TUF network
refresh, so verification also works offline and in locked-down networks.
Keep ``sigstore`` updated to pick up trust-root rotations.
"""

from __future__ import annotations

import json
from typing import Any

from sigstore.models import Bundle
from sigstore.verify import Verifier
from sigstore.verify import policy as P

from .release import RELEASE_WORKFLOW, ReleaseError, _strict_json

OIDC_ISSUER = "https://token.actions.githubusercontent.com"
IN_TOTO_PAYLOAD = "application/vnd.in-toto+json"
STATEMENT_TYPE = "https://in-toto.io/Statement/v1"
SLSA_PROVENANCE = "https://slsa.dev/provenance/v1"

_verifier: Verifier | None = None


def _get_verifier() -> Verifier:
    global _verifier
    if _verifier is None:
        _verifier = Verifier.production(offline=True)
    return _verifier


def _policy(repository: str, ref: str, workflow: str) -> P.VerificationPolicy:
    return P.AllOf([
        P.Identity(identity=f"https://github.com/{repository}/.github/workflows/{workflow}@{ref}",
                   issuer=OIDC_ISSUER),
        P.GitHubWorkflowRepository(repository),
        P.GitHubWorkflowRef(ref),
        P.GitHubWorkflowTrigger("push"),
    ])


def verify_bundle(bundle_raw: bytes, *, repository: str, ref: str, subjects: dict[str, str],
                  workflow: str = RELEASE_WORKFLOW) -> None:
    """Raise ReleaseError unless `bundle_raw` is a valid attestation for all `subjects`.

    `subjects` maps asset name -> sha256 hex of the bytes actually downloaded or cached.
    `workflow` is fixed to release.yml for callers; the parameter exists for tests.
    """
    if not repository or not ref or not subjects:
        raise ReleaseError("attestation check needs repository, ref and subjects")
    try:
        bundle = Bundle.from_json(bundle_raw)
    except Exception as exc:  # malformed bundle: fail closed
        raise ReleaseError(f"attestation bundle is malformed: {exc}") from None
    try:
        payload_type, payload = _get_verifier().verify_dsse(bundle, _policy(repository, ref, workflow))
    except Exception as exc:  # any sigstore failure is a rejection
        raise ReleaseError(f"attestation verification failed: {exc}") from None
    if payload_type != IN_TOTO_PAYLOAD:
        raise ReleaseError(f"attestation payload type {payload_type!r} is not in-toto")
    statement = _strict_json(payload, "attestation statement")
    if not isinstance(statement, dict) or statement.get("_type") != STATEMENT_TYPE:
        raise ReleaseError("attestation is not an in-toto v1 statement")
    if statement.get("predicateType") != SLSA_PROVENANCE:
        raise ReleaseError(f"attestation predicate {statement.get('predicateType')!r} is not SLSA provenance v1")
    listed: dict[str, set[str]] = {}
    for subject in statement.get("subject") or []:
        if isinstance(subject, dict) and isinstance(subject.get("digest"), dict):
            listed.setdefault(subject.get("name"), set()).add(subject["digest"].get("sha256"))
    missing = [name for name, digest in sorted(subjects.items()) if digest not in listed.get(name, set())]
    if missing:
        raise ReleaseError(f"attestation does not cover {missing} with the downloaded digests")


def select_bundle(api_response: bytes, *, repository: str, ref: str, subjects: dict[str, str]) -> bytes:
    """From a GitHub attestations API response, return the first bundle that verifies."""
    doc = _strict_json(api_response, "attestations API response")
    items = doc.get("attestations") if isinstance(doc, dict) else None
    if not isinstance(items, list) or not items:
        raise ReleaseError("no attestations published for this release")
    errors: list[str] = []
    for item in items[:20]:
        bundle: Any = item.get("bundle") if isinstance(item, dict) else None
        if not isinstance(bundle, dict):
            errors.append("entry without bundle")
            continue
        raw = json.dumps(bundle, sort_keys=True, separators=(",", ":")).encode("utf-8")
        try:
            verify_bundle(raw, repository=repository, ref=ref, subjects=subjects)
            return raw
        except ReleaseError as exc:
            errors.append(str(exc))
    raise ReleaseError("no attestation verified: " + " | ".join(errors))
