# AGENTS.md — STEMMA

Operating instructions for humans and AI agents working inside this
repository. This file governs this repository; `docs/GOVERNANCE.md` is the
authority it defers to.

## North star

> STEMMA is an open, structured, reusable STEM knowledge foundation.
> Curriculum is external. Products are external. Learning experiences are
> external. AI agents are consumers and drafters — never authorities.

Read `docs/VISION.md` first. The repo must remain understandable and useful
with zero knowledge of any other project.

## Ground rules

1. Canonical knowledge lives only in `content/`, `connections/`, `sources/`.
   Everything under `exports/` and `reports/` is derived and regenerable.
2. No curriculum, grade, course, country, or product appears in canonical
   data. No private-ecosystem references anywhere (machine-checked:
   `tests/repo/test_independence.py`).
3. AI-drafted content stays `status: draft` / `proposed` until a named human
   reviews it (`docs/CURATION-PROTOCOL.md`). AI agents never fill review
   decisions.
4. Stable IDs are never reused or silently reassigned. Connection triples are
   immutable: corrections are supersessions (`assertion.status: superseded` +
   `lifecycle.replaced_by` + a NEW connection id), never in-place edits.
5. Relationships are objects in `connections/` only — entities carry no
   relationship data (ADR-0028).
6. `claim_signature` is derived — never hand-write it into canonical YAML.
7. Every provenance agent id must exist in `schema/agent-registry.yaml`;
   register new agents in the same PR that first uses them.
8. Do not expand scope silently. Classify work NOW / ROADMAP / OUT OF SCOPE
   (`docs/GOVERNANCE.md`, `docs/ROADMAP.md`) and state a short plan.
9. Foundational decisions (schemas, relation semantics, identity, contracts,
   licensing, standards adoption) require an ADR — and several require
   explicit human approval (`docs/GOVERNANCE.md` §4). Flag, don't decide.
10. No secrets in code or docs. Leave a decision trail (`docs/decisions/`).

## Verification

```bash
python3 scripts/validate.py        # gate: exit 0 = valid; regenerates exports/knowledge.json
python3 scripts/verify_all.py      # the full chain (what CI runs)
```

The chain includes the cross-object gates: registry coherence, vocabulary
conformance, cycle detection, duplicate-claim signatures, deterministic
exports, README status-truth, export-contract conformance, agent-registry
resolution, `external_ids` formats, git-history identity and triple
immutability, ecosystem independence, and docs consistency. Derived
artifacts must be regenerated and committed fresh (CI fails on drift).

Review work: `python3 scripts/dependency_review_campaign.py` regenerates
human review worksheets under `reports/dependency-review-campaign/`; a human
fills `decision:` in a `batch-NN.yaml` and applies it with
`python3 scripts/apply_review_decisions.py <sheet> --reviewer human:<id>`.

Explorer (a consumer): `npm --prefix explorer run verify` asserts the graph
is projected from `connections[]` with per-edge trust annotation; `npm
--prefix explorer run dev` syncs its own copy of the export first.

## Starting work

1. Read `docs/README.md`, then the specification for the area you touch.
2. Read the relevant schema and one existing canonical object before editing.
3. State the classification and a short plan before changing anything.
4. Run the chain after changes; finish with a summary and flag any human
   decisions required.
