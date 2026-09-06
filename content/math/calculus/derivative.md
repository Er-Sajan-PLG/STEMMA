---
id: stemma:math.derivative
type: quantity
name: Derivative
domain: mathematics
status: draft
definition: >-
  The instantaneous rate of change of a function with respect to its variable; the limit of the
  average rate of change as the interval shrinks to zero. Written f′(x) = lim_{h→0} (f(x+h) − f(x))/h,
  the derivative gives the slope of the tangent line to the graph at a point.
symbol: f′(x)
unit: null
equation: "f′(x) = lim_{h→0} (f(x+h) − f(x)) / h"
examples:
  - "If f(x) = x², then f′(x) = 2x"
  - "If f(x) = x³, then f′(x) = 3x²"
  - "The derivative of a constant function is 0"
  - "The derivative of f(x) = 3x + 5 is the constant 3 (its slope)"
common_misconceptions:
  - "The derivative is the value of the function at a point (it measures change, not the function value)"
  - "A function must have a derivative everywhere (functions can fail to be differentiable at corners or breaks)"
learning_objectives:
  - Compute derivatives using the limit definition
  - Apply the power, product, quotient, and chain rules
  - Interpret the derivative as slope of a tangent and as instantaneous rate of change
  - Find extrema, tangents, and intervals of increase or decrease using derivatives
real_world_applications:
  - Velocity and acceleration as derivatives of position with respect to time
  - Marginal cost and marginal revenue in economics as derivatives of cost and revenue functions
  - Optimization of area, volume, profit, and other quantities
key_experiments:
  - "Approximate instantaneous velocity by averaging over shrinking time intervals"
provenance:
  ai_drafted: true
  source_kind: standards-or-specification
  source: "NCTM Principles and Standards for School Mathematics"
  reviewer: null
  reviewed_at: null
---