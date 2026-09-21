# STEMMA — Domain Model (BEGINNING, NO LEGACY)

**Status:** Authoritative, beginning. No legacy. Physics core only.

## 1. Object kinds (Beginning)

| Kind | Identity | Lives in | Count Now |
|---|---|---|---|
| Entity | `stemma:phys.<slug>` | `content/physics/**/*.md` | 17 |
| Connection | `stemma:conn.NNNNNN` | `connections/*.yaml` | 27 |
| Source | `stemma:src.<slug>` | `sources/*.yaml` | 3 |

No legacy, this is beginning.

## 2. Entity types (Minimal)

| Type | Represents | Example |
|---|---|---|
| quantity | measurable property | mass, force, velocity |
| unit | measurement standard | kilogram, newton |
| law | governing proposition | newtons-second-law, conservation-energy |
| concept | general idea | inertia, field |
| model | idealized representation | point-mass |
| phenomenon | observable | free-fall |

## 3. Physics Minimal Profile v2 (Mandatory)

Required: `id, type, name, domain, subdomain, status, definition, provenance, source_refs, governed_by`

- `subdomain`: mechanics | measurement-units | electricity-magnetism | thermal-physics — decided by governing law, not LLM
- `governed_by`: array of law ids from `physics-governing-registry.yaml` — every entity must have >=1, deterministic placement
- `source_refs`: array of `stemma:src.xxx` >=1 — canonical records, dual verification
- `provenance`: must have `source_kind, source, writer, original_author, link, retrieved_at` — embedded verification
- `historical`: optional draft, mandatory for law/model/equation when human_reviewed/canonical — timeline for progression

Forbidden for physics: `learning_objectives, real_world_applications, key_experiments, common_misconceptions`

## 4. Governing Laws — What Goes Where

See `PHYSICS-GOVERNING-LAWS.md` + `physics-governing-registry.yaml`.

- `mechanics` governed by Newton + conservation → dimensions M,L,T → quantities: mass, force, velocity...
- `measurement-units` governed by SI definitions + dimensional analysis → only type=unit
- Every entity's subdomain must match subdomain of its governing law(s) — checked by `physics_governing_check.py`

## 5. Assertion model

Connection is reified statement with mandatory evidence:
- `source --relation--> target` (only 7 relations: mathematically_requires, derived_from, appears_in_law, applies_to, generalizes, special_case_of, part_of, approximates)
- `evidence[]` >=1 with `source_ref, locator, description` — no empty evidence
- `governed_by` via connection or entity frontmatter

## 6. No legacy

Old corpus 224/654 archived. Old 74 entities archived to archive/beginning-74-entities/. This is beginning clean: 1 entity (metre) via PDF primary ingestion with HITL, deterministic scales, evolvable templates, model selector like DeepSeek harness (local + frontier models). Workflow has 2 PDFs, 7 candidates, 3 HITL edits. Will grow via primary PDF ingestion.


## Standard Scientific Definition (Added 2026-09-21)

Every entity must have standard agreed definition, not general:
- For units: exact SI Brochure 9th ed. 2019 redefinition with fixed constants (e.g., metre = light path 1/299792458 s, kilogram = h fixed 6.62607015e-34 J·s)
- For quantities: dimension + SI unit + governing law + exact formula (e.g., force F=ma = kg·m/s²)
- For laws: exact equation with constants (G, ε₀, μ₀, R) and regime
- Reference mandatory: provenance.source includes SI Brochure citation, link https://www.bipm.org/en/publications/si-brochure, source_refs [nist-si-brochure-9th, halliday-resnick-walker-12th], writer, original_author BIPM/HRW, external_ids wd/qudt
- Example: metre definition must be: 'The metre (symbol: m) is base unit of length in SI. Defined as length of path travelled by light in vacuum during 1/299,792,458 s. Exact c=299,792,458 m/s.'
- Explorer shows ✓ Scientifically agreed badge and references section for triple-check


## Comprehensive All-STEM Domains — 8 domains, 97 subdomains, mediocre coverage (not minimal physics)

Previously minimal physics only (mechanics, measurement-units) — now comprehensive all-STEM mediocre:

- **physics** (12 subdomains): mechanics, measurement-units, electricity-magnetism, thermal-physics, waves-optics, atomic-nuclear, quantum, relativity, fluid-mechanics, thermodynamics, optics, condensed-matter — textbooks HRW 12th, University Physics, Feynman Lectures — authoritative SI Brochure 9th ed. + NIST
- **chemistry** (11): general, organic, inorganic, physical, analytical, biochemistry, polymer, electrochemistry, quantum-chemistry, materials-chemistry, environmental-chemistry — textbooks Atkins, Clayden, Housecroft, Skoog — authoritative IUPAC Gold Book + CRC Handbook
- **biology** (14): general, molecular, cell-biology, genetics, evolution, ecology, physiology, microbiology, neuroscience, anatomy, botany, zoology, immunology, developmental — textbooks Campbell, Molecular Biology of the Cell, Lehninger — authoritative NCBI + IUPAC + Nature
- **earth-science** (10): geology, meteorology, oceanography, environmental, geography, climatology, seismology, hydrology, atmospheric, mineralogy — textbooks Press & Siever, Essentials of Meteorology — authoritative USGS + NASA + NOAA
- **astronomy** (8): astrophysics, cosmology, planetary, stellar, galactic, observational, astrobiology, celestial-mechanics — textbooks Carroll & Ostlie — authoritative NASA + IAU + ESA
- **computer-science** (15): algorithms, data-structures, programming-languages, software-engineering, artificial-intelligence, machine-learning, databases, networks, cybersecurity, operating-systems, theory, computer-architecture, graphics, compilers, distributed-systems — textbooks CLRS, SICP, Patterson & Hennessy, Tanenbaum, Goodfellow Deep Learning — authoritative ACM + IEEE + arXiv
- **engineering** (13): mechanical, electrical, civil, chemical, aerospace, biomedical, industrial, environmental, materials, software, nuclear, automotive, robotics — textbooks Shigley, Nilsson/Riedel, Hibbeler, Incropera — authoritative IEEE + ASME + ASCE + Handbooks
- **mathematics** (14): algebra, geometry, calculus, statistics, probability, number-theory, discrete, linear-algebra, differential-equations, topology, analysis, logic, combinatorics, optimization — textbooks Stewart, Dummit & Foote, Rudin, Strang — authoritative MathWorld + NIST DLMF + arXiv

Total 97 subdomains, mediocre coverage 50-100 entities per domain = 400-800 total entities, with deterministic templates v2.0.0 that scale, embeddings, RAG, consumer export for LearningHub, PROFESSOR-J.

## Entity Types — 12 types comprehensive, not 3

- concept (generic, any domain), quantity (with symbol + unit), unit (with exact SI), constant (with exact value), law (with equation + history), principle, theorem, equation, process (photosynthesis, mitosis, compilation), structure (DNA, atom, crystal, data structure), algorithm (quicksort, Dijkstra, backprop), material (graphene, steel, polymer)

Each with template in template-registry.yaml v2.0.0, requires [definition] or [definition, symbol, unit, governed_by] etc., evolvable without code change.

## Embeddings + RAG + Consumer Export — NEW

- **Embedding:** YES needed — model generates vectors for entities for RAG and consumer export, 12 models local free + frontier API, deterministic content_hash + model id → same embeddings, stored in exports/embeddings.jsonl + vector_store/ FAISS, for LearningHub (OpenAI text-embedding-3-large 3072), PROFESSOR-J (BGE Large SOTA 1024 offline), general (All-MiniLM fast)
- **RAG:** YES needed — STEMMA is knowledge foundation, RAG is how consumers use it, flow question → embedding → vector search top_k → context definitions + connections + sources → LLM model selector like DeepSeek harness (local + frontier models: DeepSeek R1 free, Claude 3.5 Sonnet, GPT-4o, Gemini 2.5 Pro, Llama 3.3, custom) → answer with citations, API /v2/rag/search GET + /v2/rag/query POST, webapp RAG playground
- **Consumer export:** YES needed — file (knowledge.json deterministic content-hash v2.1.0, embeddings.jsonl, vector_store/, consumers/<consumer>/knowledge.<consumer>.json filtered), API (adapter v0.2.0 endpoints /v2/entities, /v2/embeddings, /v2/rag/search, /v2/rag/query POST, /v2/export?consumer=..., /openapi.yaml), SDK (Python Stemma.from_file + StemmaRAG)
