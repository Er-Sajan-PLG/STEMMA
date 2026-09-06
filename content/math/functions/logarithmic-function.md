---
id: stemma:math.logarithmic-function
type: concept
name: Logarithmic Function
domain: mathematics
status: draft
definition: >-
  The inverse of the exponential function: y = log_b(x) is the power to which the base b must be
  raised to obtain x, so bʸ = x. Logarithms convert multiplication into addition and satisfy
  identities such as log_b(xy) = log_b(x) + log_b(y).
symbol: log_b(x)
unit: null
equation: "y = log_b(x)   ⇔   bʸ = x   (b > 0, b ≠ 1)"
examples:
  - "log₂(8) = 3 because 2³ = 8"
  - "log₁₀(1000) = 3 because 10³ = 1000"
  - "log_e(e²) = 2 (the natural log)"
  - "log_b(1) = 0 for any valid base b"
common_misconceptions:
  - "The logarithm of a sum equals the sum of the logarithms (log(x+y) ≠ log x + log y)"
  - "Logarithms are numbers only for positive input (log of a non-positive number is undefined in the reals)"
learning_objectives:
  - Convert between exponential and logarithmic forms
  - Apply the product, quotient, and power laws of logarithms
  - Solve exponential equations using logarithms
  - Recognize logarithms as inverses of exponential functions
real_world_applications:
  - The decibel scale and Richter magnitude as logarithmic measures of intensity
  - Growth and decay times (half-life, doubling time) solved logarithmically
key_experiments:
  - "Measure sound loudness in decibels and relate successive stages to multiplicative intensity"
provenance:
  ai_drafted: true
  source_kind: standards-or-specification
  source: "NCTM Principles and Standards for School Mathematics"
  reviewer: null
  reviewed_at: null
historical:
  stated_by: "John Napier (with Henry Briggs)"
  year: 1614
  where: "Mirifici Logarithmorum Canonis Descriptio"
  context: "Computation and functions"
  note: "Napier introduced logarithms in 1614; Henry Briggs developed common (base-10) logarithms from 1617."
  timeline:
    - year: 1614
      by: "John Napier"
      event: "Publication of Mirifici Logarithmorum Canonis Descriptio introducing logarithms"
    - year: 1617
      by: "Henry Briggs"
      event: "Development of common (base-10) logarithms"
---