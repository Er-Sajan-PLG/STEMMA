# CURATION-PROTOCOL (BEGINNING, NO LEGACY, HITL, EVOLVABLE, FRONTIER)

**Status:** Beginning clean, 1 entity (metre) via PDF primary ingestion with HITL, deterministic scales, evolvable templates, model selector like DeepSeek harness (local + frontier models). Old 74 entities archived.

## Evidence mandatory for physics-core + HITL

Every connection must have >=1 evidence with:
- type, stance, source_ref (must resolve to sources/), locator (page), description

Every entity must have:
- source_kind, source, writer human:*, original_author, link bipm.org, retrieved_at
- source_refs >=1 resolving to sources/ with url/doi/isbn
- governed_by >=1 law from registry, deterministic placement, no LLM
- Standard scientific definition with exact SI (see below)

History:
- Draft: optional
- Law/model/equation human_reviewed/canonical: historical mandatory with stated_by, year, where, timeline[]

HITL (Human In The Loop) before canonical — mandatory for both primary PDF and secondary direct LLM:
- AI shows markdown preview in webapp (textarea + rendered + checklist)
- Human explicitly edits markdown file for easy verification (plain text diffable)
- Audit trail workflow/audit/audit.jsonl must contain candidate_edited by human:* after AI draft
- Writer must be human:*, not llm:*
- hitl_check.py verifies before canonical — fails if no human edit
- Even LLM fallback requires HITL

No legacy, this is beginning clean with HITL.

## Promotion chain — canonical is never a single act (ADR-0057, 2026-10-01)

An object does **not** go from draft to canonical in one step. Promotion is a
pipeline of recorded stages, applied one at a time:

```text
draft → machine_validated → validator_validated → independently_validated → board_approved → canonical
```

**While the board waiver is active** (the owner is the only validator —
`ENF-STEMMA-HITL-003.board_waiver`) the board stage is **omitted**, not faked, and the
chain shortens:

```text
draft → machine_validated → validator_validated → independently_validated → canonical
```

Rules (all machine-enforced; see `spec/machine-readable/enforcement_rules.yaml`,
`ENF-STEMMA-HITL-001`..`004`):

- **One stage per act.** `python3 scripts/review_entity.py stage <id> --actor human:*`
  advances exactly one stage of the *currently required* chain. `canonicalize` is
  refused outright — the validator is not the final canonicalizer. Writing a board
  stage while the waiver holds is refused.
- **Separate days.** Consecutive stages of the same record MUST land on different
  calendar days (≥1). The CLI refuses a same-day second stage in real time and the
  gate re-checks every history, so this cannot be shortcut by hand-editing
  frontmatter. The rule is **data** (`enforcement_rules.yaml`); deleting that file
  fails the gate closed rather than waiving the rule.
- **Distinct humans — or a recorded waiver.** Stage 2 must be a different human than
  stage 1, and (when present) the board must name ≥2 humans. While a single owner
  holds the roles, promotions MUST carry an owner-sanctioned
  `independence_waiver {sanctioned_by, reason, retire_when}`; the gate fails if the
  actors are not distinct and the waiver is absent.
- **Revalidation debt blocks the record outright (pilot scale).** A record carrying
  `revalidation_debt.status: outstanding` is **invalid** while it holds any reviewed
  status — not merely barred from advancing. The gate reports the debt **by name** for
  the record being validated. Clear it (`review_entity.py clear-debt`) or have the
  owner defer it (`defer-debt`). The owner chose the full block deliberately at this
  small scale, to observe when it starts to bite; relaxing to forward-only is a
  registry edit (`ENF-STEMMA-HITL-002.pilot_scale_block`), not a code change.
- **Applies to all canonical datasets** — entities **and** connections.

"Canonical" is therefore a claim with a machine-checked chain behind it: who
validated it, when, and whether an independent human was involved. Where that chain
rests on one person, or is shorter than the full three stages, the artifact says so.

## Standard Scientific Definition (Added 2026-09-21, Updated 2026-09-21 with evolvable + frontier)

Every entity must have standard agreed definition, not general, with exact SI constants and reference:

- For units: exact SI Brochure 9th ed. 2019 redefinition with fixed constants (e.g., metre = light path 1/299,792,458 s, kilogram = h fixed 6.62607015e-34 J·s, second = ΔνCs fixed 9,192,631,770 Hz, ampere = e fixed 1.602176634e-19 C, kelvin = k fixed 1.380649e-23 J/K, mole = N_A fixed 6.02214076e23, candela = K_cd fixed 683 lm/W)
  - Example metre (user specified exactly): "The metre (symbol: m) is the base unit of length in the International System of Units (SI). It is scientifically defined as the length of the path travelled by light in a vacuum during a time interval of 1/299,792,458 of a second. Exact: c=299,792,458 m/s."
  - Must include "Exact:" with value and agreed status per BIPM 2019

- For quantities: dimension + SI unit + governing law + exact formula + agreed per SI/HRW (e.g., length dimension L unit metre governed_by si-definitions, force F=ma = kg·m/s², area L² = m × m exact 1 m² = 1 m × 1 m)

- For laws: exact equation with constants (G=6.67430e-11, ε₀=8.8541878128e-12, μ₀=4πe-7, R=8.314462618) and regime, historical timeline

- Reference mandatory — triple verification:
  - provenance.source includes SI Brochure citation with page and exact value: "BIPM SI Brochure 9th ed. (2019) §2.3.1, p130: The metre is defined via c=299,792,458 m/s. Exact c=299,792,458 m/s."
  - link https://www.bipm.org/en/publications/si-brochure — mandatory
  - source_refs [stemma:src.nist-si-brochure-9th, stemma:src.halliday-resnick-walker-12th] — each must have canonical file in sources/ with url/doi/isbn, >=1 mandatory
  - writer human:curator.001 — must be human:* for HITL, not llm:*
  - original_author BIPM/HRW, retrieved_at, source_kind standards-or-specification
  - external_ids wd: Q... + qudt — mandatory wd

- Explorer shows ✓ Scientifically agreed badge and references section for triple-check

## Deterministic Scales, Evolvable Templates, LLM Fallback Only When Needed

- **Deterministic (no LLM) scales:** Uses schema/template-registry.yaml with regex rules (e.g., `Length:\s*(.+)`) + exact SI constants c,h,ΔνCs,e,k,N_A,K_cd — no model, no cost, no hallucination, scales to 1000s PDFs, any domain (physics, chemistry, biology, math)
- **Evolvable:** Add new domain via `python3 scripts/evolvable_template.py --evolve --new-domain chemistry --new-subdomain organic` without code change — templates in YAML with placeholders {definition}, {symbol}, etc.
- **LLM fallback only when PDF missing exact SI:** If PDF text says "Length is distance" without "Exact: c=...", then LLM fetches standard definition from SI Brochure/NIST authoritative source using frontier model (DeepSeek R1 free, Claude 3.5 Sonnet, GPT-4o, Gemini 2.5 Pro, Llama 3.3 70B free) or custom model via OpenRouter/NVIDIA NIM/OpenAI-compatible, selector like DeepSeek harness (search, categories Frontier/Reasoning/Free/Custom, 25 models, custom input)
- **Even LLM requires HITL:** LLM output → markdown preview → human explicitly edits markdown → audit logs candidate_edited by human → stage → validate (including hitl_check) → canonical — no entity without human edit

## Verification

```bash
python3 scripts/validate.py  # schema, identity, refs, 1 entity now
python3 scripts/physics_core_profile_check.py  # mandatory fields, no forbidden, 0 violations
python3 scripts/physics_governing_check.py  # governed_by in registry, subdomain matches, 0 violations
python3 scripts/hitl_check.py --check-workflow  # HITL audit trail, writer human:*, markdown explicit
python3 scripts/evolvable_template.py --pdf-extract workflow/extraction/hrw-ch1-measurement.txt  # deterministic extraction, scales
python3 scripts/verify_all.py  # full chain with HITL — green
```

All must pass before PR.
