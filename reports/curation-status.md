# Curation Status — v0.2

- Total connections: 654 (canonical objects)
- Canonical assertions (`review.status==canonical`): 50
- Reviewed-only: 0, Canonical: 50, Unreviewed: 604 (total reviewed inc. canonical: 50)
- Proposed: 653, Inferred: 0
- Migrated: 641, Human-authored: 13, LLM: 0
- Rejected: 0, Deprecated: 4
- Semantics: `reviewed-only` vs `canonical` (terminal); canonical implies reviewed

## By relation
{'special_case_of': 14, 'related_to': 371, 'logically_requires': 90, 'part_of': 24, 'derived_from': 3, 'mathematically_requires': 98, 'applies_to': 24, 'appears_in_law': 11, 'bridges': 6, 'analogous_to': 3, 'approximates': 3, 'generalizes': 7}

## By family
{'hierarchical': 21, 'associative': 371, 'dependency': 188, 'structural': 24, 'derivation': 38, 'cross_domain': 6, 'analogy': 3, 'model': 3}

## By domain
{'biology': 80, 'chemistry': 94, 'earth-space': 33, 'engineering': 1, 'physics': 302, 'scientific-practice': 2, 'mathematics': 142}

## By review
{'canonical': 50, 'unreviewed': 604}

## By origin
{'migrated': 641, 'human-authored': 13}

## Top reviewed (canonical)
- stemma:conn.000001: special_case_of stemma:bio.animal-cell -> stemma:bio.cell
- stemma:conn.000005: logically_requires stemma:bio.cellular-respiration -> stemma:bio.cell
- stemma:conn.000012: part_of stemma:bio.nucleus -> stemma:bio.cell
- stemma:conn.000014: logically_requires stemma:bio.osmosis -> stemma:chem.diffusion
- stemma:conn.000025: part_of stemma:bio.dna -> stemma:bio.cell
- stemma:conn.000048: logically_requires stemma:chem.atom -> stemma:chem.matter
- stemma:conn.000049: logically_requires stemma:chem.atom -> stemma:phys.electric-charge
- stemma:conn.000053: logically_requires stemma:chem.element -> stemma:chem.atom
- stemma:conn.000060: logically_requires stemma:chem.compound -> stemma:chem.atom
- stemma:conn.000069: logically_requires stemma:chem.matter -> stemma:phys.mass
- stemma:conn.000130: mathematically_requires stemma:phys.current -> stemma:phys.electric-charge
- stemma:conn.000131: mathematically_requires stemma:phys.current -> stemma:phys.time
- stemma:conn.000165: mathematically_requires stemma:phys.voltage -> stemma:phys.electric-charge
- stemma:conn.000173: logically_requires stemma:phys.measurement -> stemma:phys.unit
- stemma:conn.000177: logically_requires stemma:phys.time -> stemma:phys.measurement

## Remaining highest priority
none

## Gaps
- Evidence gaps: 599 (sample ['stemma:conn.000002', 'stemma:conn.000003', 'stemma:conn.000004'])
- Provenance gaps (no reviewed_by): 604

## Entity review coverage
- Entities: 224
- Human-reviewed/canonical entities: 0 (0.0%)
- Canonical entities: 0
- By status: {'draft': 224}
- By domain: {"biology": {"canonical": 0, "human_reviewed": 0, "total": 33}, "chemistry": {"canonical": 0, "human_reviewed": 0, "total": 40}, "earth-space": {"canonical": 0, "human_reviewed": 0, "total": 9}, "engineering": {"canonical": 0, "human_reviewed": 0, "total": 1}, "mathematics": {"canonical": 0, "human_reviewed": 0, "total": 43}, "physics": {"canonical": 0, "human_reviewed": 0, "total": 96}, "scientific-practice": {"canonical": 0, "human_reviewed": 0, "total": 2}}

## Note
Schema correctness != semantic acceptance. Canonical objects (397) include 382 proposed/unreviewed.
