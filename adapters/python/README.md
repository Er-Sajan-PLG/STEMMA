# stemma-adapter

First-party **read-only** Python consumer adapter for STEMMA.

- **Package name:** `stemma-adapter`
- **Python:** 3.10+
- **Dependencies:** none beyond the standard library
- **Surface area:** SDK, CLI, and a local JSON API server
- **License:** MIT (`../../LICENSE-CODE`)

This adapter loads the published STEMMA export, validates the contract it
consumes, and gives downstream tools a small stable API without requiring the
producer repository's validator stack.

## Status

`0.3.0` is an in-repo first-party adapter release: SDK (now including verified
release loading, `Stemma.from_release` / `Stemma.from_url`), CLI, and local JSON
API with embeddings, RAG, and consumer export (`/v2/*` endpoints) against the
2.2.0 export contract. See [CHANGELOG.md](CHANGELOG.md). Promotion to adapter `1.0` and any PyPI publication
remain human-gated decisions.

## Install

From the repository root:

```bash
pip install ./adapters/python              # core: standard library only
pip install "./adapters/python[verify]"    # + Sigstore attestation checks (needed by default for releases)
```

Not published to PyPI yet. Or for local development without installation:

```bash
PYTHONPATH=adapters/python python3 -m stemma_adapter --help
```

## SDK

```python
from stemma_adapter import Stemma

stemma = Stemma.from_file("exports/knowledge.json")
print(stemma.stats)
print(stemma.resolve("stemma:phys.force"))
print(stemma.by_external_id("wd", "Q11402")["id"])
```

### From a published release (verified before use)

```python
stemma = Stemma.from_release("Er-Sajan-PLG/STEMMA", "v3.0.0-rc1",
                             file="knowledge.learninghub.json", cache_dir="/var/cache/stemma")
stemma.release_info["verification"]   # "sigstore"
```

- Explicit tag only (`vX.Y.Z` / `vX.Y.Z-rcN`); one `kind: export` asset per call via `file=`.
- Default: Sigstore attestation for `manifest.json` + `SHA256SUMS.txt` + the
  export, from `release.yml` at `refs/tags/<tag>` (needs `[verify]`).
  `verify_attestation=False` = **checksum-only integrity**, not publisher
  authenticity. The owner's GPG signature is not checked by the SDK.
- `Stemma.from_url(".../manifest.json", expected_repository=..., expected_ref=...)`
  for mirrors/CDNs: the signer identity always comes from the caller.
- Verified copies are cached and reused with zero requests (`offline=True`
  never uses the network). Tags are treated as immutable.

Full rules: [docs/API.md → SDK](../../docs/API.md#sdk).

## CLI

```bash
stemma-adapter validate exports/knowledge.json
stemma-adapter stats exports/knowledge.json
stemma-adapter search exports/knowledge.json force --domain physics --limit 5
stemma-adapter prereqs exports/knowledge.json stemma:phys.newtons-second-law --policy canonical
```

## Local JSON API

```bash
stemma-adapter serve exports/knowledge.json --host 127.0.0.1 --port 8080
curl http://127.0.0.1:8080/v2/stats
curl "http://127.0.0.1:8080/v2/search?q=force&domain=physics"
```

Routes:

- `/`
- `/v2/stats`
- `/v2/entities`
- `/v2/entities/{id}`
- `/v2/resolve/{id}`
- `/v2/connections`
- `/v2/neighbors/{id}`
- `/v2/prerequisites/{id}`
- `/v2/search?q=...`
- `/v2/external/{scheme}/{value}`

## Notes and current gap

The adapter mirrors review-policy filtering from `scripts/graph_policy.py`
exactly, but the export does **not** currently embed the relation registry.
That means relation-family semantics remain a producer-side contract rather
than something the adapter can introspect from the export alone.
