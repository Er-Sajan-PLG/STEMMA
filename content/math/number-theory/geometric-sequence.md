---
id: stemma:math.geometric-sequence
type: concept
name: Geometric Sequence
domain: mathematics
status: draft
definition: >-
  A sequence in which each term is obtained from the previous one by multiplying by a constant
  called the common ratio r, so aₙ = a₁·rⁿ⁻¹. The terms change by a constant factor, growing
  exponentially when |r| > 1 and shrinking toward zero when |r| < 1. The sum of the first n terms
  is Sₙ = a₁(1 − rⁿ)/(1 − r) for r ≠ 1.
symbol: aₙ
unit: null
equation: "aₙ = a₁·rⁿ⁻¹   |   Sₙ = a₁(1 − rⁿ)/(1 − r)   (r ≠ 1)"
examples:
  - "2, 6, 18, 54, … has common ratio 3"
  - "aₙ = 100·(1/2)ⁿ⁻¹ halves each term"
  - "aₙ = 3·2ⁿ⁻¹ doubles each term from the first term 3"
  - "The infinite geometric sum with |r| < 1 converges: 1 + 1/2 + 1/4 + … = 2"
common_misconceptions:
  - "The common ratio is the difference between terms (it is the factor by which each term is multiplied)"
  - "All geometric sequences diverge (those with a ratio of magnitude less than 1 converge)"
learning_objectives:
  - Identify the common ratio of a geometric sequence
  - Write the general term from the first term and ratio
  - Compute partial sums of geometric series
  - Sum infinite geometric series when |r| < 1
real_world_applications:
  - Compound interest, population growth, and radioactive decay
  - Bouncing heights and folding problems that change by constant factors
key_experiments:
  - "Halving a strip of paper repeatedly to observe a geometric decreasing pattern"
provenance:
  ai_drafted: true
  source_kind: standards-or-specification
  source: "NCTM Principles and Standards for School Mathematics"
  reviewer: null
  reviewed_at: null
---