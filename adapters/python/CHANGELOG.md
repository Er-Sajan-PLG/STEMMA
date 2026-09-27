# stemma-adapter changelog

Adapter package versions are independent of the repository `VERSION`, the
schema version and the export version.

## 0.3.0 — 2026-09-26

Added (additive; no existing behaviour changed):

- `Stemma.from_release(repo, tag, *, cache_dir=None, file="knowledge.json",
  verify_attestation=True, offline=False, timeout=30, ssl_context=None,
  max_export_bytes=None)` — load one `kind: export` asset of a GitHub release.
- `Stemma.from_url(manifest_url, *, ..., expected_repository=None,
  expected_ref=None)` — same, from a mirror/CDN; attestation requires the
  caller-supplied identity.
- Verification before parsing: HTTPS-only (incl. redirects), size caps, strict
  `manifest.json` / `SHA256SUMS.txt` parsing, sha256 check, `load_export`,
  `content_hash` match; optional-by-extra Sigstore attestation, **on by
  default** (`pip install "stemma-adapter[verify]"`).
- Content-addressed, atomically written cache
  (`<cache>/github/<owner>/<repo>/<tag>/<content_hash>/`), fully re-verified on
  every load; `offline=True`.
- `Stemma.release_info` (None for `from_file` / `from_dict`), `ReleaseError`
  (subclass of `ExportError`), `[verify]` extra (`sigstore>=4,<5`).

Unchanged: `from_file()`, `from_dict()`, `load_export()`, CLI, `/v2` server
behaviour. Not published to PyPI.

## 0.2.0

In-repo SDK, CLI and local JSON API (`/v2/*`) against export contract 2.2.0.
