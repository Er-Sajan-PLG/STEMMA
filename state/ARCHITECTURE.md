# ARCHITECTURE — STEMMA

> Stable system understanding. Update when understanding changes, not when code
> churns. **Last verified against the code:** 2026-10-01.
> Anything here that contradicts the code is a bug in this file.

---

## Cold start (do this before your first gate run)

A **fresh clone is not ready to work in.** Git does not clone `.git/hooks`, and
`requirements-dev.txt` is separate from `requirements.txt`. Verified by cloning the branch
cold and following these steps literally.

```bash
python3 -m venv .venv
source .venv/bin/activate                                 # or export VIRTUAL_ENV=$PWD/.venv
pip install -r requirements.txt -r requirements-dev.txt
python3 scripts/install_hooks.py                          # installs pre-commit + pre-push
python3 scripts/verify_all.py                             # expect exit 0
python3 tests/repo/test_state_tree.py                     # expect 12/12
```

> **Use a venv.** A bare `pip install` fails on PEP 668 systems
> (`error: externally-managed-environment`). Activating the venv also matters for the
> pre-push hook, which resolves its interpreter as
> `"${VIRTUAL_ENV:+$VIRTUAL_ENV/bin/python}"` and falls back to the ambient `python3` —
> so an *inactive* venv means the hook runs pytest-less.

**What happens if you skip a step — none of it fails loudly:**

| Skipped | Symptom | Why it matters |
|---|---|---|
| `requirements-dev.txt` | `verify_all.py` prints `SKIP: promotion-chain guards — no interpreter with pytest` and still exits **0** | **18 promotion/debt guards do not execute at all.** The chain is green, so nothing else tells you. |
| `install_hooks.py` | nothing — pushes are simply not gated | The chain, strong checks, exports freshness and docs checks run *only* from the hook. An ungated push can land a broken tree. |

Both are deliberate, not defects: the chain must not fail on a pytest-less interpreter (a bare
`python3` is the normal hook environment), and hooks are not version-controlled. But neither is
discoverable from the failure, which is why this section exists.

### Do not read the `OK` count as a health score

A cold clone reports **39 OK** where a warm tree reports **42**. That difference has **nothing
to do with the setup steps** — three checks are *informational* and only report when
git-ignored derived artifacts exist:

| Missing check | Needs | Ignored by |
|---|---|---|
| `OK: embeddings exist …` | `exports/embeddings.jsonl`, `exports/vector_store/` | `.gitignore` (ADR-0054: embeddings are never committed) |
| `OK: Evidence first-class …` | `proposals/` | `.gitignore` (ingestion staging) |
| `OK: RAG vector search works …` | the vector store | same as embeddings |

They are regenerable and absent by design in a fresh clone. **`FAIL` count is the signal;
`OK` count is not comparable across environments.**

**Already present in a cold clone:** `pyyaml` and `jsonschema` are usually in the system
interpreter, so `validate.py` and most of the chain run immediately. `pytest` is the one
normally missing.

---

## What STEMMA Is

An open, version-controlled, machine-readable knowledge graph of STEM concepts,
governed by the **Specification Recovery Protocol v3.1**. Curriculum is external.
Products are external. AI agents are consumers.

## Canonical Truth vs Derived (the load-bearing distinction)

| Layer | Location | Authority |
|---|---|---|
| **Canonical** | `content/**/*.md` (frontmatter + prose), `connections/*.yaml`, `sources/*.yaml` | **SOURCE OF TRUTH** |
| **Contracts** | `schema/*.schema.json`, `schema/relation-registry.yaml`, `schema/VERSION.yaml` | Contract |
| **Derived** | `exports/**`, `reports/**` | Regenerable; never hand-edited |
| **Consumer** | `explorer/`, `webapp/`, `adapters/` | Consumers; never canonical |

Derived artifacts regenerate **byte-identically** from canonical. If a derived file
differs from a regeneration, the derived file is wrong.

## The Verification Chain (`scripts/verify_all.py`)

42 steps, fail-closed: the first non-zero exit stops the chain and prints
`FAIL: <step>` to stderr. Roughly: validate → export → jsonld/shacl → status truth →
physics checks → HITL → review manifest → graph analysis → review-aware export →
subsets → consumer bundles → registry coherence → domain identity → promotion chain →
validation report → deterministic export → semantic pipeline.

`tests/repo/test_gate_fail_closed.py` proves the chain is *fail-closed*: a shadow tree
with one step stubbed to exit non-zero must produce a named `FAIL`, non-zero exit, and
**no further steps executed**.

## Gate Layers

| Layer | Command | Enforces |
|---|---|---|
| Chain | `scripts/verify_all.py` | Everything above |
| Tests | `pytest tests/ -q` (349) | Unit + integration + mutation guards |
| Docs | `scripts/docs.py check` | Contract integrity, links, generated freshness, recovery registries |
| Strong | `scripts/verify_strong.py` | Secrets, wall-clock, registries, explorer, webapp |
| Recovery | `spec/machine-readable/validate_recovery.py` | Cross-registry reference integrity (9 checks) |
| Pre-push | `.git/hooks/pre-push` | Chain + strong + exports/reports freshness + docs sync/check |

## Three Registries, Three Lifecycles

Conflating these is a recurring source of confusion:

| Registry | Question it answers | Statuses |
|---|---|---|
| `spec/machine-readable/open_questions.yaml` (`UNRES-`) | An **open question** | `OPEN` / `CLOSED` / `DEFERRED` |
| `spec/CONFLICTS.md` + registry (`CONFLICT-`) | Two sources **disagree** | `OPEN` / `RESOLVED` |
| `spec/machine-readable/verification.yaml` | A requirement's **L4 verification state** | `VERIFIED` / `FAILED` / `UNVERIFIED` |

A requirement deferral is **not** a `UNRES` record — it is a status on the
requirement. `REQ-STEMMA-OPS-002` is the live example.

## Authority Model

`spec/ROLES_AND_AUTHORITY.md` **Constraint D**: the executor may run work and record
results but may **NOT**
- approve / reject / defer a requirement,
- close any `UNRES-` record,
- promote an `INFERENCE` to a `FACT`.

The owner is `human:curator.001`, `SOLE_OWNER`. Rulings are recorded as decision
sheets in `spec/` (e.g. `spec/UNVERIFIED-DECISIONS.md`, `spec/UNRES-DECISIONS.md`).

## Enforcement Registries (data, not code)

`spec/machine-readable/enforcement_rules.yaml` holds live policy as **data** so the
owner can change behaviour with a one-value edit:

| Rule | Current value |
|---|---|
| `ENF-STEMMA-HITL-001` | day-separated stages (≥1 day between promotion stages) |
| `ENF-STEMMA-HITL-002.pilot_scale_block` | `active: true` — debt blocks **fully** at pilot scale |
| `ENF-STEMMA-HITL-003.board_waiver` | `active: true` — two-stage chain `validator → independent_validator` while waived |

Deleting the registry **fails closed**. Flipping `board_waiver.active` to false
restores the three-stage, ≥2-human chain.

## Writing Derived Artifacts

All gate-compared artifacts are written **atomically** (`scripts/atomic_write.py`:
stage in a dot-prefixed sibling temp file, then `os.replace`). Reason: `Path.write_text`
truncates before writing, so a concurrent reader can observe a partial file — this
caused a real spurious test failure. `tests/repo/test_atomic_artifact_writes.py` pins
the list of writers that must use the helper.

## Release Provenance (two layers)

- `-rcN` tags: **CI-attested only**.
- Final `vX.Y.Z`: CI attestation **plus** an owner GPG signature over
  `SHA256SUMS.txt`. The signing key **must never** enter Actions secrets.

`release.yml` creates a final release as a **draft**; nothing goes public before
signing. `VERSION` is the only version source and `release.yml` enforces `tag == VERSION`.
Tags are **immutable** — a mistake is fixed with a new `-rcN`, never a moved tag.

## HITL Model

Human-in-the-loop applies to **all** data. Canonical entities must carry a registered
human writer *and* human reviewer. Enforced by `validate.py::check_entity_agents` and
`scripts/hitl_check.py --all` (which audits `content/` **and** `connections/`).

## Repository Map

```
content/      canonical entities (Markdown + YAML frontmatter)   ← SOURCE OF TRUTH
connections/  first-class qualified assertions                   ← SOURCE OF TRUTH
sources/      canonical citations                                ← SOURCE OF TRUTH
schema/       JSON Schema + registries + VERSION.yaml            ← contracts
spec/         Specification Recovery Protocol artefacts (reqs, evidence, UNRES, conflicts)
docs/         living documentation set (docs-contract.yaml gates it)
exports/      derived artifacts (regenerable, byte-identical)
reports/      derived reports
scripts/      pipeline + gates
tests/        pytest suites (repo/, registry/, versioning/, curation/, webapp/, ...)
explorer/     consumer: graph viewer + grounded chat
webapp/       consumer: ingestion UI (no login)
adapters/     consumer: python SDK
state/        MACP agent coordination state (see PROTOCOL.md)
```
