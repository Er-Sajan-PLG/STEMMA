---
id: stemma:math.sequence
type: concept
name: Sequence
domain: mathematics
status: draft
definition: >-
  An ordered list of terms a₁, a₂, a₃, … in which a formula or rule assigns a term to each index n
  (usually a natural number). Sequences are functions whose domain is a set of consecutive
  integers, and they are classified by their patterns into types such as arithmetic and geometric
  sequences.
symbol: aₙ
unit: null
equation: "aₙ = f(n)   for n = 1, 2, 3, …"
examples:
  - "aₙ = 2n: 2, 4, 6, 8, …"
  - "aₙ = n²: 1, 4, 9, 16, …"
  - "aₙ = (−1)ⁿ alternates in sign"
  - "The Fibonacci-like rule aₙ = aₙ₋₁ + aₙ₋₂ defines 1, 1, 2, 3, 5, …"
common_misconceptions:
  - "A sequence is the same as its set of values (a sequence preserves order and repetition, a set does not)"
  - "Every sequence has a single obvious formula (many rules may fit finitely many terms)"
learning_objectives:
  - Distinguish sequences from general sets and identify their index domains
  - Generate terms from an explicit formula or a recurrence
  - Classify sequences as arithmetic, geometric, or other
  - Find the sum of a sequence via series
real_world_applications:
  - Numbering of discrete steps in algorithms and amortization schedules
  - Modeling populations, interest compounding, and iterative processes in discrete time
key_experiments:
  - "Construct patterns of matchsticks to generate and predict subsequent terms"
provenance:
  ai_drafted: true
  source_kind: standards-or-specification
  source: "NCTM Principles and Standards for School Mathematics"
  reviewer: null
  reviewed_at: null
---