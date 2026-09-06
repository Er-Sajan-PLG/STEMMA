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

`0.1.0` is an in-repo first-party adapter release. Promotion to adapter
`1.0` and any PyPI publication remain human-gated decisions.

## Install

From the repository root:

```bash
pip install ./adapters/python
```

Or for local development without installation:

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
