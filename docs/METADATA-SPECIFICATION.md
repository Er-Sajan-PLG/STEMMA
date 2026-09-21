# METADATA-SPECIFICATION (BEGINNING, NO LEGACY, HITL, EVOLVABLE, FRONTIER)

**Status:** Beginning clean, 1 entity (metre) via PDF primary ingestion with HITL, deterministic scales, evolvable templates, model selector like DeepSeek harness (local + frontier models). Old 74 entities archived.

## Provenance (Dual Verification + HITL + Exact SI)

Entity provenance mandatory for physics-core v2 with HITL:

- ai_drafted: bool — true if LLM drafted, false if human authored — but writer must be human:* for HITL
- source_kind: textbook | standards-or-specification | academic-or-research | institutional | other — mandatory, textbook = HRW, standards = SI Brochure 9th ed. 2019
- source: embedded citation with page + Exact: value — mandatory, e.g., "BIPM SI Brochure 9th ed. (2019) §2.3.1, p130: The metre is defined via c=299,792,458 m/s. Exact c=299,792,458 m/s. Agreed internationally."
- writer: agent id who wrote file — must be human:* for HITL (human:curator.001), not llm:* — mandatory, must resolve in agent-registry.yaml, enforced by hitl_check.py
- original_author: who stated science — BIPM or Halliday, Resnick, Walker — mandatory
- link: URL/DOI — mandatory, e.g., https://www.bipm.org/en/publications/si-brochure for triple-check
- retrieved_at: ISO date — mandatory
- reviewer, reviewed_at: after human review via review_entity.py

Plus source_refs array >=1 pointing to canonical sources/*.yaml — each must resolve, each source must have url/doi/isbn for verifiability

Source record mandatory:
- url OR doi OR isbn for verifiability — at least one
- writer human:*, retrieved_at, title, authors[], year, citation

Connection evidence mandatory >=1 with type, stance, source_ref (must resolve), locator (page), description (why source supports claim)

HITL: workflow/audit/audit.jsonl must contain candidate_edited by human:* after AI draft, writer must be human:*, markdown file explicit edit before canonical — hitl_check.py enforces, even LLM fallback requires HITL

## Historical + Exact SI

Optional for draft, mandatory for law/model/equation when human_reviewed/canonical. Must have stated_by, year, where, timeline[] with year, by, event — shows progression for verification.

For units: exact SI Brochure 9th ed. 2019 redefinition with fixed constants:
- metre: c=299,792,458 m/s exact, light path 1/299,792,458 s
- kilogram: h=6.62607015e-34 J·s exact
- second: ΔνCs=9,192,631,770 Hz exact
- ampere: e=1.602176634e-19 C exact
- kelvin: k=1.380649e-23 J/K exact
- mole: N_A=6.02214076e23 exact
- candela: K_cd=683 lm/W exact

Must include "Exact:" with value and agreed status per BIPM 2019.

## Evolvable Templates + Frontier

- Template registry: schema/template-registry.yaml — evolvable, domain-agnostic, regex rules, exact SI constants, domains physics/chemistry/biology/math, add new domain without code change
- Deterministic scales: no LLM needed, uses regex + exact SI constants, scales to 1000s PDFs, no cost
- LLM fallback only when PDF missing exact SI: frontier models DeepSeek R1/V3 free, Claude 3.5 Sonnet/Opus, GPT-4o/o1, Gemini 2.5 Pro/2.0 Flash free, Llama 3.3 70B free via OpenRouter/NVIDIA NIM, selector like DeepSeek harness (search, categories Frontier/Reasoning/Free/Custom, 25 models, custom input)
- Even LLM requires HITL: human explicitly edits markdown before canonical

## No legacy

Old provenance unknown:legacy-relationship deleted. Old 74 entities archived to archive/beginning-74-entities/. This is beginning clean with HITL, deterministic scales, evolvable templates, model selector like DeepSeek harness (local + frontier models).
