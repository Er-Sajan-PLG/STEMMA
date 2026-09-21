# STANDARDS (BEGINNING, NO LEGACY, HITL, EVOLVABLE, FRONTIER)

**Status:** Beginning clean, 1 entity (metre) via PDF primary ingestion with HITL, deterministic scales, evolvable templates, model selector like DeepSeek harness (local + frontier models). Old 74 entities archived.

- SKOS: generalizes=broader, special_case_of=narrower
- QUDT/UCUM via external_ids wd/qudt — mandatory wd for triple-check
- SI Brochure 9th ed. (BIPM 2019): exact SI with fixed constants c=299,792,458 m/s, h=6.62607015e-34 J·s, ΔνCs=9,192,631,770 Hz, e=1.602176634e-19 C, k=1.380649e-23 J/K, N_A=6.02214076e23, K_cd=683 lm/W — authoritative source for standard scientific definitions, must include Exact: + agreed per BIPM 2019
- NIST SI: https://www.nist.gov/pml/owm/si-units — exact SI fallback when PDF missing definition
- HRW 12th ed.: Halliday Resnick Walker Fundamentals of Physics — textbook for quantities/laws, deterministic regex extraction
- Template registry: schema/template-registry.yaml — evolvable, domain-agnostic, exact SI constants, domains physics/chemistry/biology/math
- Frontier models: DeepSeek R1/V3 free, Claude 3.5 Sonnet/Opus, GPT-4o/o1, Gemini 2.5 Pro/2.0 Flash free, Llama 3.3 70B free, Qwen, Nemotron via OpenRouter/NVIDIA NIM — selector like DeepSeek harness (search, categories Frontier/Reasoning/Free/Custom, 25 models, custom input) — LLM fallback only when PDF missing exact SI, even LLM requires HITL human edit before canonical
- No legacy — old 74 entities archived to archive/beginning-74-entities/, this is beginning clean with HITL, deterministic scales, evolvable, frontier
