---
id: stemma:math.continuity
type: concept
name: Continuity
domain: mathematics
status: draft
definition: >-
  A property of a function at a point when the function value equals its limit there:
  lim_{x→c} f(x) = f(c). A function is continuous on an interval if it is continuous at every
  point of that interval, meaning its graph can be drawn without lifting the pen. Continuity is
  a prerequisite for differentiability and for many fundamental results of calculus.
symbol: null
unit: null
equation: "lim_{x→c} f(x) = f(c)"
examples:
  - "f(x) = x² is continuous at every real input"
  - "f(x) = 1/x is discontinuous at 0 (no finite value or limit there)"
  - "f(x) = |x| is continuous everywhere but not differentiable at 0"
  - "Piecewise functions often show jump discontinuities at their breakpoints"
common_misconceptions:
  - "A function continuous at every point is necessarily differentiable there (continuity does not imply differentiability)"
  - "A removable hole (point discontinuity) means the whole function is unreliable (only that single point is affected)"
learning_objectives:
  - Determine continuity at a point by comparing the limit and the function value
  - Classify discontinuities as removable, jump, or infinite
  - State the intermediate-value property and the extreme-value theorem on closed intervals
  - Recognize that differentiability implies continuity
real_world_applications:
  - Spline interpolation in computer graphics relies on continuous curves joining segments
  - Continuity assumptions justify modelling population size, position, and temperature as smooth trajectories
key_experiments:
  - "Trace graphs with breakpoints and holes to identify where continuity fails"
provenance:
  ai_drafted: true
  source_kind: standards-or-specification
  source: "NCTM Principles and Standards for School Mathematics"
  reviewer: null
  reviewed_at: null
---