"""Load one export from a published STEMMA release, verified before use.

Consumers pull the same files everyone else gets (GitHub Releases, or a mirror
via ``from_url``). Nothing is parsed until it has been checked:

1. ``manifest.json`` and ``SHA256SUMS.txt`` are fetched (HTTPS only, size-capped,
   strict parsing). They must agree on every file's digest.
2. The requested ``file`` must be listed with ``kind: export``; anything else is
   refused *before* its body is requested.
3. The export is downloaded (capped at its manifest ``bytes``), hashed and
   compared with ``SHA256SUMS.txt``, then validated by ``load_export``.
4. By default the Sigstore build attestation is verified (``[verify]`` extra):
   one statement must cover the manifest, the checksum list and the export,
   signed by ``.github/workflows/release.yml`` at ``refs/tags/<tag>`` of the
   expected repository. The expected identity always comes from the caller,
   never from downloaded data.
5. Only then is anything written to the cache, file by file, atomically.

``verify_attestation=False`` is *checksum-only*: it detects corruption, but a
server that replaces both a file and the checksum list is not detected. The
owner's GPG signature (``SHA256SUMS.sig``) is not checked by this module.

Release tags are treated as immutable: a valid cached copy is reused without
any request. Moving or replacing a published tag is unsupported.

Standard library only. ``sigstore`` is imported lazily (``attest.py``) and
only when attestation verification is requested.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import ssl
import stat
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from .loader import ExportError, load_export

__all__ = ["ReleaseError", "load_release", "load_url", "DEFAULT_MAX_EXPORT_BYTES"]

GITHUB_WEB = "https://github.com"
GITHUB_API = "https://api.github.com"
RELEASE_WORKFLOW = "release.yml"

MANIFEST = "manifest.json"
SUMS = "SHA256SUMS.txt"
ATTESTATION = "attestation.json"

MAX_MANIFEST_BYTES = 1 << 20          # 1 MiB (rc1: ~3 KB)
MAX_SUMS_BYTES = 256 << 10            # 256 KiB (rc1: <1 KB)
MAX_ATTESTATION_BYTES = 8 << 20       # 8 MiB (rc1: ~12 KB)
DEFAULT_MAX_EXPORT_BYTES = 512 << 20  # 512 MiB; the manifest's exact `bytes` is the real cap
_CHUNK = 64 << 10
_USER_AGENT = "stemma-adapter/0.3.0 (+release-loader)"

VERIFY_EXTRA_HINT = 'Release attestation verification requires:\npip install "stemma-adapter[verify]"'

_OWNER = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})")
_REPO = re.compile(r"[A-Za-z0-9._-]{1,100}")
_TAG = re.compile(r"v[0-9]+\.[0-9]+\.[0-9]+(?:-rc[0-9]+)?")  # same rule as release.yml
_REF = re.compile(r"refs/tags/(v[0-9]+\.[0-9]+\.[0-9]+(?:-rc[0-9]+)?)")
_FILE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}")
_HEX64 = re.compile(r"[0-9a-f]{64}")
_CONTENT_HASH = re.compile(r"sha256:([0-9a-f]{64})")
_SUMS_LINE = re.compile(r"([0-9a-f]{64})  ([A-Za-z0-9][A-Za-z0-9._-]{0,127})")


class ReleaseError(ExportError):
    """A release could not be fetched, verified or loaded. Always fail closed."""


# --------------------------------------------------------------------------- inputs

def _check_repo(repo: Any) -> tuple[str, str]:
    if not isinstance(repo, str) or repo.count("/") != 1:
        raise ReleaseError(f"repo must be 'owner/name', got {repo!r}")
    owner, name = repo.split("/")
    if not _OWNER.fullmatch(owner) or not _REPO.fullmatch(name) or name in (".", ".."):
        raise ReleaseError(f"repo must be 'owner/name', got {repo!r}")
    return owner, name


def _check_tag(tag: Any) -> str:
    if not isinstance(tag, str) or not _TAG.fullmatch(tag):
        raise ReleaseError(f"tag must be an explicit vX.Y.Z or vX.Y.Z-rcN (never 'latest'), got {tag!r}")
    return tag


def _check_file(file: Any) -> str:
    if not isinstance(file, str) or not _FILE.fullmatch(file) or ".." in file:
        raise ReleaseError(f"file must be a plain release asset name such as 'knowledge.json', got {file!r}")
    return file


def _check_https(url: Any, label: str) -> urllib.parse.SplitResult:
    if not isinstance(url, str):
        raise ReleaseError(f"{label} must be a string")
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or not parts.hostname or "@" in parts.netloc:
        raise ReleaseError(f"{label} must be an https:// URL without credentials, got {_redact(url)}")
    return parts


def _redact(url: str) -> str:
    """Drop query/fragment (signed CDN URLs carry credentials in the query)."""
    try:
        p = urllib.parse.urlsplit(url)
        return urllib.parse.urlunsplit((p.scheme, p.netloc.rsplit("@", 1)[-1], p.path, "", ""))
    except ValueError:
        return "<unparseable url>"


# --------------------------------------------------------------------------- network

class _HTTPSOnlyRedirect(urllib.request.HTTPRedirectHandler):
    max_redirections = 5

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: D401
        if urllib.parse.urlsplit(newurl).scheme != "https":
            raise ReleaseError(f"refusing redirect from {_redact(req.full_url)} to non-HTTPS {_redact(newurl)}")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class _Net:
    """All network access goes through here, so offline mode can never fetch."""

    def __init__(self, *, offline: bool, timeout: float, ssl_context: ssl.SSLContext | None) -> None:
        self.offline = offline
        self.timeout = timeout
        ctx = ssl_context or ssl.create_default_context()
        self._opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx), _HTTPSOnlyRedirect())

    def get(self, url: str, *, limit: int, expected_size: int | None = None, accept: str = "*/*") -> bytes:
        if self.offline:
            raise ReleaseError(f"offline=True: refusing network request for {_redact(url)}")
        _check_https(url, "URL")
        req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT, "Accept": accept})
        try:
            with self._opener.open(req, timeout=self.timeout) as resp:
                _check_https(resp.geturl(), "final URL")
                length = resp.headers.get("Content-Length")
                if length is not None:
                    try:
                        declared = int(length)
                    except ValueError:
                        raise ReleaseError(f"bad Content-Length {length!r} from {_redact(url)}") from None
                    if declared > limit:
                        raise ReleaseError(f"{_redact(url)}: Content-Length {declared} exceeds limit {limit}")
                buf = bytearray()
                while True:
                    chunk = resp.read(min(_CHUNK, limit + 1 - len(buf)))
                    if not chunk:
                        break
                    buf += chunk
                    if len(buf) > limit:
                        raise ReleaseError(f"{_redact(url)}: body exceeds limit {limit} bytes")
        except ReleaseError:
            raise
        except urllib.error.HTTPError as exc:
            raise ReleaseError(f"HTTP {exc.code} for {_redact(url)}") from None
        except (urllib.error.URLError, OSError, ValueError) as exc:
            reason = getattr(exc, "reason", exc)
            raise ReleaseError(f"cannot fetch {_redact(url)}: {reason}") from None
        if expected_size is not None and len(buf) != expected_size:
            raise ReleaseError(f"{_redact(url)}: got {len(buf)} bytes, manifest lists {expected_size}")
        return bytes(buf)


# --------------------------------------------------------------------------- parsing

def _strict_json(raw: bytes, label: str) -> Any:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for key, value in items:
            if key in out:
                raise ReleaseError(f"{label}: duplicate JSON key {key!r}")
            out[key] = value
        return out

    def no_constants(name: str) -> Any:
        raise ReleaseError(f"{label}: non-standard JSON constant {name}")

    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=pairs, parse_constant=no_constants)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReleaseError(f"{label}: invalid JSON ({exc})") from None


def _parse_sums(raw: bytes) -> dict[str, str]:
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError:
        raise ReleaseError(f"{SUMS}: not ASCII") from None
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    sums: dict[str, str] = {}
    for n, line in enumerate(lines, 1):
        m = _SUMS_LINE.fullmatch(line)
        if not m:
            raise ReleaseError(f"{SUMS} line {n}: expected '<64 lowercase hex>  <name>'")
        digest, name = m.groups()
        if ".." in name:
            raise ReleaseError(f"{SUMS} line {n}: unsafe name {name!r}")
        if name in sums:
            raise ReleaseError(f"{SUMS}: duplicate entry for {name!r}")
        sums[name] = digest
    if not sums:
        raise ReleaseError(f"{SUMS}: empty")
    return sums


def _check_manifest(manifest: Any, sums: dict[str, str], file: str, *, expected_tag: str | None,
                    max_export_bytes: int) -> tuple[dict[str, Any], str]:
    """Return (entry for `file`, content-hash hex). Raises before any export download."""
    if not isinstance(manifest, dict):
        raise ReleaseError(f"{MANIFEST}: not an object")
    tag = manifest.get("release_tag")
    if not isinstance(tag, str) or not _TAG.fullmatch(tag):
        raise ReleaseError(f"{MANIFEST}: release_tag {tag!r} is not vX.Y.Z[-rcN]")
    if expected_tag is not None and tag != expected_tag:
        raise ReleaseError(f"{MANIFEST}: release_tag {tag!r} != requested {expected_tag!r}")
    chash = manifest.get("content_hash")
    m = _CONTENT_HASH.fullmatch(chash) if isinstance(chash, str) else None
    if not m:
        raise ReleaseError(f"{MANIFEST}: content_hash {chash!r} is not sha256:<64 hex>")
    files = manifest.get("files")
    if not isinstance(files, dict) or not files:
        raise ReleaseError(f"{MANIFEST}: files must be a non-empty object")
    if set(files) != set(sums):
        raise ReleaseError(f"{MANIFEST} and {SUMS} list different files: "
                           f"{sorted(set(files) ^ set(sums))}")
    for name, meta in files.items():
        if not isinstance(meta, dict) or meta.get("sha256") != sums[name]:
            raise ReleaseError(f"{MANIFEST} and {SUMS} disagree on the digest of {name!r}")
    if file not in files:
        raise ReleaseError(f"{file!r} is not an asset of release {tag}")
    entry = files[file]
    if entry.get("kind") != "export":
        raise ReleaseError(f"{file!r} is kind {entry.get('kind')!r}, not 'export' — refusing to load it")
    size = entry.get("bytes")
    if not isinstance(size, int) or isinstance(size, bool) or size <= 0:
        raise ReleaseError(f"{MANIFEST}: {file} has no valid byte size")
    if size > max_export_bytes:
        raise ReleaseError(f"{file} is {size} bytes, above max_export_bytes={max_export_bytes}")
    return entry, m.group(1)


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _load_verified_export(raw: bytes, file: str, sums: dict[str, str], chash_hex: str) -> dict[str, Any]:
    digest = _sha256(raw)
    if digest != sums[file]:
        raise ReleaseError(f"{file}: sha256 {digest} does not match {SUMS} ({sums[file]})")
    data = _strict_json(raw, file)
    try:
        export = load_export(data)
    except ReleaseError:
        raise
    except ExportError as exc:
        raise ReleaseError(f"{file}: {exc}") from None
    if export.get("content_hash") != f"sha256:{chash_hex}":
        raise ReleaseError(f"{file}: content_hash does not match {MANIFEST}")
    return data


# --------------------------------------------------------------------------- attestation

def _attest():
    try:
        from . import attest
    except ImportError as exc:
        raise ReleaseError(VERIFY_EXTRA_HINT) from exc
    return attest


def _subjects(file: str, manifest_raw: bytes, sums_raw: bytes, export_raw: bytes) -> dict[str, str]:
    return {MANIFEST: _sha256(manifest_raw), SUMS: _sha256(sums_raw), file: _sha256(export_raw)}


# --------------------------------------------------------------------------- cache

def _default_cache_dir() -> Path:
    base = os.environ.get("XDG_CACHE_HOME") or os.path.join(os.path.expanduser("~"), ".cache")
    return Path(base) / "stemma-adapter"


_COMPONENT = re.compile(r"[A-Za-z0-9._-]{1,128}")


def _cache_path(root: Path, parts: tuple[str, ...]) -> Path:
    """root/parts... with every component validated and no symlink below root."""
    path = root
    for part in parts:
        if not _COMPONENT.fullmatch(part) or part in (".", ".."):
            raise ReleaseError(f"unsafe cache path component {part!r}")
        path = path / part
        if path.is_symlink():
            raise ReleaseError(f"cache path {path} is a symlink — refusing")
        if path.exists() and not path.is_dir():
            raise ReleaseError(f"cache path {path} is not a directory")
    if not path.resolve().is_relative_to(root):
        raise ReleaseError(f"cache path escapes cache_dir: {path}")
    return path


def _read_cached(path: Path, limit: int) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_BINARY", 0)
    try:
        st = os.lstat(path)
        if not stat.S_ISREG(st.st_mode):
            raise ReleaseError(f"cached {path.name} is not a regular file")
        if st.st_size > limit:
            raise ReleaseError(f"cached {path.name} exceeds {limit} bytes")
        fd = os.open(path, flags)
        with os.fdopen(fd, "rb") as fh:
            data = fh.read(limit + 1)
    except FileNotFoundError:
        raise ReleaseError(f"cached {path.name} missing") from None
    except OSError as exc:
        raise ReleaseError(f"cannot read cached {path.name}: {exc}") from None
    if len(data) > limit:
        raise ReleaseError(f"cached {path.name} exceeds {limit} bytes")
    return data


def _write_atomic(directory: Path, name: str, data: bytes) -> None:
    target = directory / name
    if target.is_symlink():
        raise ReleaseError(f"cache file {target} is a symlink — refusing")
    if target.is_file():
        try:
            if _sha256(_read_cached(target, len(data))) == _sha256(data):
                return  # identical bytes already in place (e.g. a concurrent writer won)
        except ReleaseError:
            pass
    fd, tmp = tempfile.mkstemp(prefix=".tmp-", dir=directory)
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, target)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


class _Identity:
    """Who must have produced the release — always from the caller, never from downloads."""

    def __init__(self, repo: str | None, ref: str | None) -> None:
        self.repo = repo
        self.ref = ref


def _validate_entry(entry: Path, file: str, *, expected_tag: str | None, identity: _Identity | None,
                    max_export_bytes: int) -> tuple[dict[str, Any], dict[str, Any]]:
    """Fully re-verify a cached copy. Returns (export data, info) or raises ReleaseError."""
    manifest_raw = _read_cached(entry / MANIFEST, MAX_MANIFEST_BYTES)
    sums_raw = _read_cached(entry / SUMS, MAX_SUMS_BYTES)
    sums = _parse_sums(sums_raw)
    manifest = _strict_json(manifest_raw, MANIFEST)
    meta, chash_hex = _check_manifest(manifest, sums, file, expected_tag=expected_tag,
                                      max_export_bytes=max_export_bytes)
    if entry.name != chash_hex or entry.parent.name != manifest["release_tag"]:
        raise ReleaseError("cache entry location does not match its manifest")
    export_raw = _read_cached(entry / file, meta["bytes"])
    data = _load_verified_export(export_raw, file, sums, chash_hex)
    verification = "checksum-only"
    if identity is not None:
        bundle_raw = _read_cached(entry / ATTESTATION, MAX_ATTESTATION_BYTES)
        _attest().verify_bundle(bundle_raw, repository=identity.repo, ref=identity.ref,
                                subjects=_subjects(file, manifest_raw, sums_raw, export_raw))
        verification = "sigstore"
    return data, _info(manifest, file, sums[file], verification, entry)


def _info(manifest: dict[str, Any], file: str, sha: str, verification: str, entry: Path) -> dict[str, Any]:
    return {
        "release_tag": manifest["release_tag"],
        "file": file,
        "sha256": sha,
        "content_hash": manifest["content_hash"],
        "export_version": manifest.get("export_version"),
        "schema_version": manifest.get("schema_version"),
        "verification": verification,  # "sigstore" | "checksum-only"
        "cache_entry": str(entry),
    }


def _from_cache(base: Path, file: str, *, expected_tag: str | None, identity: _Identity | None,
                max_export_bytes: int) -> tuple[tuple[dict[str, Any], dict[str, Any]] | None, list[str]]:
    """base = <cache>/.../<tag-or-url-key>. Returns (hit or None, reasons for misses)."""
    if not base.is_dir():
        return None, ["no cached copy"]
    entries = sorted(base.glob("*/*") if expected_tag is None else base.glob("*"))
    valid, reasons = [], []
    for entry in entries:
        if entry.is_symlink() or not entry.is_dir() or not _HEX64.fullmatch(entry.name):
            continue
        if expected_tag is None and not _TAG.fullmatch(entry.parent.name):
            continue
        try:
            valid.append(_validate_entry(entry, file, expected_tag=expected_tag, identity=identity,
                                         max_export_bytes=max_export_bytes))
        except ReleaseError as exc:
            reasons.append(f"{entry.name[:12]}: {exc}")
    if len(valid) > 1:
        raise ReleaseError(f"{base} holds several valid copies; release tags must be immutable — "
                           "delete that directory to re-fetch")
    return (valid[0] if valid else None), (reasons or ["no cached copy"])


# --------------------------------------------------------------------------- flows

def _load(*, base_url: str, cache_base: tuple[str, ...], file: str, expected_tag: str | None,
          identity: _Identity | None, attestation_api: str | None, cache_dir: str | os.PathLike | None,
          offline: bool, timeout: float, ssl_context: ssl.SSLContext | None,
          max_export_bytes: int) -> tuple[dict[str, Any], dict[str, Any]]:
    if identity is not None:
        _attest()  # fail fast, before any request, if the [verify] extra is missing
    root = Path(cache_dir if cache_dir is not None else _default_cache_dir()).expanduser().resolve()
    base = _cache_path(root, cache_base)
    hit, reasons = _from_cache(base / expected_tag if expected_tag else base, file,
                               expected_tag=expected_tag, identity=identity, max_export_bytes=max_export_bytes)
    if hit is not None:
        return hit
    if offline:
        raise ReleaseError(f"offline=True and no valid cached copy of {file}: {'; '.join(reasons)}")

    net = _Net(offline=offline, timeout=timeout, ssl_context=ssl_context)
    manifest_raw = net.get(base_url + MANIFEST, limit=MAX_MANIFEST_BYTES, accept="application/json")
    sums_raw = net.get(base_url + SUMS, limit=MAX_SUMS_BYTES, accept="text/plain")
    sums = _parse_sums(sums_raw)
    manifest = _strict_json(manifest_raw, MANIFEST)
    meta, chash_hex = _check_manifest(manifest, sums, file, expected_tag=expected_tag,
                                      max_export_bytes=max_export_bytes)
    export_raw = net.get(base_url + file, limit=meta["bytes"], expected_size=meta["bytes"])
    data = _load_verified_export(export_raw, file, sums, chash_hex)

    bundle_raw = None
    if identity is not None:
        owner, name = identity.repo.split("/")
        api = f"{attestation_api}/repos/{owner}/{name}/attestations/sha256:{_sha256(manifest_raw)}"
        response = net.get(api, limit=MAX_ATTESTATION_BYTES, accept="application/json")
        bundle_raw = _attest().select_bundle(response, repository=identity.repo, ref=identity.ref,
                                             subjects=_subjects(file, manifest_raw, sums_raw, export_raw))

    tag = manifest["release_tag"]
    entry = _cache_path(root, (*cache_base, tag, chash_hex))
    entry.mkdir(parents=True, exist_ok=True)
    entry = _cache_path(root, (*cache_base, tag, chash_hex))  # re-check after creation
    _write_atomic(entry, file, export_raw)
    _write_atomic(entry, SUMS, sums_raw)
    _write_atomic(entry, MANIFEST, manifest_raw)
    if bundle_raw is not None:
        _write_atomic(entry, ATTESTATION, bundle_raw)
    return data, _info(manifest, file, sums[file], "sigstore" if identity else "checksum-only", entry)


def load_release(repo: str, tag: str, *, cache_dir=None, file: str = "knowledge.json",
                 verify_attestation: bool = True, offline: bool = False, timeout: float = 30,
                 ssl_context: ssl.SSLContext | None = None,
                 max_export_bytes: int = DEFAULT_MAX_EXPORT_BYTES) -> tuple[dict[str, Any], dict[str, Any]]:
    """Verified export data + provenance info for `file` of GitHub release `repo`@`tag`."""
    owner, name = _check_repo(repo)
    _check_tag(tag)
    _check_file(file)
    identity = _Identity(f"{owner}/{name}", f"refs/tags/{tag}") if verify_attestation else None
    return _load(base_url=f"{GITHUB_WEB}/{owner}/{name}/releases/download/{tag}/",
                 cache_base=("github", owner, name), file=file, expected_tag=tag, identity=identity,
                 attestation_api=GITHUB_API, cache_dir=cache_dir, offline=offline, timeout=timeout,
                 ssl_context=ssl_context, max_export_bytes=max_export_bytes)


def load_url(manifest_url: str, *, cache_dir=None, file: str = "knowledge.json",
             verify_attestation: bool = True, expected_repository: str | None = None,
             expected_ref: str | None = None, offline: bool = False, timeout: float = 30,
             ssl_context: ssl.SSLContext | None = None,
             max_export_bytes: int = DEFAULT_MAX_EXPORT_BYTES) -> tuple[dict[str, Any], dict[str, Any]]:
    """Like `load_release`, from a mirror whose manifest lives at `manifest_url`.

    Sibling files are fetched next to the manifest. With attestation (default),
    `expected_repository` ('owner/name') and `expected_ref` ('refs/tags/vX.Y.Z')
    are required: the signer identity is never taken from the mirror.
    """
    parts = _check_https(manifest_url, "manifest_url")
    if parts.query or parts.fragment or not parts.path.endswith("/" + MANIFEST):
        raise ReleaseError(f"manifest_url must end in /{MANIFEST} with no query, got {_redact(manifest_url)}")
    _check_file(file)
    expected_tag = None
    identity = None
    if expected_ref is not None:
        m = _REF.fullmatch(expected_ref) if isinstance(expected_ref, str) else None
        if not m:
            raise ReleaseError(f"expected_ref must be 'refs/tags/vX.Y.Z[-rcN]', got {expected_ref!r}")
        expected_tag = m.group(1)
    if expected_repository is not None:
        owner, name = _check_repo(expected_repository)
        expected_repository = f"{owner}/{name}"
    if verify_attestation:
        if expected_repository is None or expected_ref is None:
            raise ReleaseError("verify_attestation=True needs expected_repository='owner/name' and "
                               "expected_ref='refs/tags/vX.Y.Z' (never read from the mirror); or pass "
                               "verify_attestation=False for checksum-only integrity")
        identity = _Identity(expected_repository, expected_ref)
    key = hashlib.sha256(manifest_url.encode("utf-8")).hexdigest()[:32]
    base_url = manifest_url[: -len(MANIFEST)]
    return _load(base_url=base_url, cache_base=("url", key), file=file, expected_tag=expected_tag,
                 identity=identity, attestation_api=GITHUB_API, cache_dir=cache_dir, offline=offline,
                 timeout=timeout, ssl_context=ssl_context, max_export_bytes=max_export_bytes)
