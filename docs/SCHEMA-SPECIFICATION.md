# STEMMA — Schema Specification (BEGINNING, NO LEGACY, v1.2.0, HITL, EVOLVABLE, FRONTIER)

**Status:** Authoritative for schema_version 1.2.0, beginning clean. No legacy. 1 entity (metre) via PDF primary ingestion with HITL, deterministic scales, evolvable templates, model selector like DeepSeek harness (local + frontier models). Old 74 entities archived.

## 1. Design rules (Beginning, HITL, Evolvable)

- One envelope per object kind, minimal, evolvable via template-registry.yaml
- No legacy, no pedagogical fields
- Every physics entity must have governed_by + source_refs + writer human:* + link + exact SI + HITL audit
- Versioned as unit in VERSION.yaml single source, no literals, deterministic content-hash
- PDF primary ingestion, deterministic scales, LLM fallback only when PDF missing exact SI, even LLM requires HITL

## 2. Identity

| Object | ID pattern | File rule | After HITL |
|---|---|---|---|
| Entity | `^stemma:phys\.[a-z0-9-]+$` | `content/physics/<subdomain>/<slug>.md` only after HITL + human review | workflow/candidates/<doc_id>/<slug>.md (AI draft) → human edit → workflow/proposals/<slug>.md → content/ |
| Connection | `^stemma:conn\.[0-9]{6}$` | `connections/conn.NNNNNN.yaml` only after HITL + evidence | workflow/candidates/ → proposals → connections/ |
| Source | `^stemma:src\.[a-z0-9-]+$` | `sources/src.<slug>.yaml` with url/doi/isbn | Canonical |

## 3. Entity envelope v1.2.0 (Minimal, Dual Verification, HITL, Exact SI)

Required: `id, type, name, domain, subdomain, status, definition (standard exact SI), provenance (writer human:*), source_refs>=1, governed_by>=1`

- `subdomain`: mechanics | measurement-units | electricity-magnetism | thermal-physics — decided by governing law from physics-governing-registry.yaml, deterministic, no LLM
- `governed_by`: law ids from physics-governing-registry.yaml — mandatory >=1, each in registry, subdomain must match law's subdomain, no self-governance
- `source_refs`: canonical source ids >=1 — dual verification, each must resolve to sources/*.yaml with url/doi/isbn
- `provenance`: must have ai_drafted (bool), source_kind (textbook | standards-or-specification), source (full citation with page + Exact: value), writer human:* (must be human:* for HITL, not llm:*), original_author BIPM/HRW, link https://www.bipm.org/en/publications/si-brochure (mandatory), retrieved_at ISO date, reviewer/reviewed_at after human review
- `historical`: optional draft, mandatory law/model/equation when human_reviewed/canonical with stated_by, year, where, timeline[]
- `symbol`, `unit`: mandatory for unit/quantity
- `definition`: STANDARD scientific definition with exact SI, not general — must include "Exact:" + fixed constant + agreed per SI Brochure 9th ed. 2019 + reference (see below)

Forbidden: learning_objectives, real_world_applications, key_experiments, common_misconceptions, related_to (only 8 relations allowed)

HITL: No entity becomes canonical without human explicitly editing markdown file — workflow/audit/audit.jsonl must contain candidate_edited by human:* after AI draft, writer must be human:*, markdown file explicit edit, hitl_check.py enforces

## 4. Connection envelope

Required: id, type, source, relation, target, assertion, provenance, evidence>=1

- relation only from minimal set (8): mathematically_requires, derived_from, appears_in_law, applies_to, generalizes, special_case_of, part_of, approximates — no related_to
- evidence mandatory >=1 with type, stance, source_ref (must resolve), locator (page), description (why source supports claim)
- provenance asserted_by human:*, generated_by human:*, method manual

## 5. Source envelope

Required: id, type, citation + url/doi/isbn for verifiability (at least one) + writer human:*, retrieved_at, title, authors[], year

- Dual verification: embedded provenance (writer, link) + canonical source record + external URL triple-check

## 6. Export contract + Template Registry

- v2.1.0, deterministic, content-hash sha256, no wall clock, no version literals, byte-identical regeneration ADR-0022, single source schema/VERSION.yaml
- template-registry v1.0.0 NEW: schema/template-registry.yaml — evolvable, domain-agnostic, regex rules, exact SI constants c=299,792,458 m/s, h=6.62607015e-34, ΔνCs=9,192,631,770 Hz, e, k, N_A, K_cd, domains physics/chemistry/biology/math, LLM fallback only when PDF missing exact SI, even LLM requires HITL

## 7. No legacy + Scaling + Frontier

Old schemas 1.0.0/1.1.0 archived. Old 74 entities archived to archive/beginning-74-entities/. This is beginning v1.2.0 clean, 1 entity via HITL.

- **Deterministic scales:** No LLM needed, uses template-registry.yaml regex + exact SI constants, scales to 1000s PDFs, any domain, no cost, no hallucination
- **Evolvable:** Add new domain via `python3 scripts/evolvable_template.py --evolve --new-domain chemistry` without code change
- **LLM only when PDF missing exact SI:** Frontier models DeepSeek R1/V3 free, Claude 3.5 Sonnet/Opus, GPT-4o/o1, Gemini 2.5 Pro/2.0 Flash free, Llama 3.3 70B free, Qwen, Nemotron via OpenRouter/NVIDIA NIM, selector like DeepSeek harness (search, categories Frontier/Reasoning/Free/Custom, 25 models, custom model input)
- **Even LLM requires HITL:** Human explicitly edits markdown before canonical — audit trail + writer human:* + markdown explicit — hitl_check.py

## 8. Standard Scientific Definition (Added 2026-09-21, Updated with evolvable + frontier)

Every entity must have standard agreed definition, not general, with exact SI constants and reference:

- For units: exact SI Brochure 9th ed. 2019 redefinition with fixed constants (e.g., metre = light path 1/299,792,458 s, kilogram = h fixed 6.62607015e-34 J·s, second = ΔνCs fixed 9,192,631,770 Hz)
  - Example metre (user specified exactly): "The metre (symbol: m) is the base unit of length in the International System of Units (SI). It is scientifically defined as the length of the path travelled by light in a vacuum during a time interval of 1/299,792,458 of a second. Exact: c=299,792,458 m/s."
  - Must include "Exact:" with value and agreed status per BIPM 2019

- For quantities: dimension + SI unit + governing law + exact formula (e.g., length dimension L unit metre governed_by si-definitions, force F=ma = kg·m/s², area L² = m × m exact 1 m² = 1 m × 1 m)

- For laws: exact equation with constants (G=6.67430e-11, ε₀=8.8541878128e-12, μ₀=4πe-7, R=8.314462618) and regime, historical timeline

- Reference mandatory — triple verification: provenance.source includes SI Brochure citation with page and exact value, link https://www.bipm.org/en/publications/si-brochure, source_refs [nist-si-brochure-9th, halliday-resnick-walker-12th], writer human:*, original_author BIPM/HRW, external_ids wd/qudt

- Explorer shows ✓ Scientifically agreed badge and references section for triple-check

- Deterministic fallback: If PDF has exact, use it. If PDF lacks exact SI, LLM fallback fetches from SI Brochure/NIST using frontier model you choose, but still requires HITL human edit before canonical
