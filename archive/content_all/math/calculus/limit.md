---
id: stemma:math.limit
type: concept
name: Limit
domain: mathematics
status: draft
definition: >-
  The value a function or sequence approaches as its input or index approaches a given value.
  Written lim_{x→c} f(x) = L, a limit describes the behaviour of f near the point c without
  requiring f to be defined there. Limits formalize instantaneous change and underpin the
  derivative and the integral.
symbol: "lim_{x→c} f(x)"
unit: null
equation: "lim_{x→c} f(x) = L"
examples:
  - "lim_{x→2} (3x - 1) = 5"
  - "lim_{x→0} (sin x)/x = 1"
  - "lim_{x→∞} 1/x = 0"
  - "lim_{x→0} (x² + 2x)/x = 2 (even though the expression is undefined at 0)"
common_misconceptions:
  - "If f(c) is undefined, the limit does not exist (the limit depends on nearby values, not the value at c)"
  - "A limit must equal the function value f(c) (they coincide for continuous functions, but not in general)"
learning_objectives:
  - Estimate limits from tables and graphs of values
  - Evaluate limits by direct substitution, factoring, and rationalization
  - Distinguish one-sided, two-sided, and infinite limits
  - Relate the limit to the formal definition in terms of neighborhoods
  - Use limits to analyze the behaviour of functions at points where they are undefined
real_world_applications:
  - Instantaneous velocity as the limiting average velocity over shrinking time intervals
  - Predict the behaviour of a model (population, price) as a parameter grows without bound
key_experiments:
  - "Zooming on a function graph to observe values clustering toward a single output"
provenance:
  ai_drafted: true
  source_kind: standards-or-specification
  source: "NCTM Principles and Standards for School Mathematics"
  reviewer: null
  reviewed_at: null
---