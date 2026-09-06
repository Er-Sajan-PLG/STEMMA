---
id: stemma:math.integral
type: quantity
name: Integral
domain: mathematics
status: draft
definition: >-
  A quantity that accumulates a function over an interval: the definite integral
  ∫ₐᵇ f(x) dx measures the signed area under the curve y = f(x) between a and b, while the
  indefinite integral is an antiderivative or a family of functions whose derivative is f.
  Integration reverses differentiation.
symbol: "∫ f(x) dx"
unit: null
equation: "∫ₐᵇ f(x) dx  =  F(b) − F(a)  where  F′ = f"
examples:
  - "∫ 2x dx = x² + C"
  - "∫₀¹ x² dx = 1/3"
  - "∫ (cos x) dx = sin x + C"
  - "∫₀² 3 dx = 6 (area of a rectangle of base 2 and height 3)"
common_misconceptions:
  - "The integral is only an area (it also accumulates any quantity being accumulated by the rate f)"
  - "The +C constant is unimportant (it is essential: antiderivatives differ by a constant)"
learning_objectives:
  - Interpreting the definite integral as accumulated change and signed area
  - Computing integrals of elementary functions using antiderivative rules
  - Relating the integrand f to its antiderivative F via the fundamental theorem
  - Using integrals to compute areas and volumes
real_world_applications:
  - Computing distances, work, volume, and total change from rates of change
  - Accumulating probability over an interval from a density function
key_experiments:
  - "Approximate area under a curve with rectangles (Riemann sums), refining the partition"
provenance:
  ai_drafted: true
  source_kind: standards-or-specification
  source: "NCTM Principles and Standards for School Mathematics"
  reviewer: null
  reviewed_at: null
---