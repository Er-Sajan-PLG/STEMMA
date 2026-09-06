---
id: stemma:math.exponential-function
type: concept
name: Exponential Function
domain: mathematics
status: draft
definition: >-
  A function of the form f(x) = a·bˣ where the base b is positive and not equal to 1, with x as
  the exponent. The function multiplies by a fixed factor b over each unit interval, producing
  constant relative growth (or decay) rather than constant absolute change.
symbol: f(x)
unit: null
equation: "f(x) = a·bˣ   (b > 0, b ≠ 1)"
examples:
  - "f(x) = 2ˣ doubles with each unit increase in x"
  - "f(x) = 3·4ˣ models a population increasing fourfold each unit"
  - "f(x) = (1/2)ˣ models exponential decay, halving per unit"
  - "f(x) = eˣ uses Euler's number e as the natural base"
common_misconceptions:
  - "Exponential growth and linear growth are similar (linear adds constants; exponential multiplies by constants and grows far faster)"
  - "A negative base is allowed for every exponent (b must be positive so bˣ is real for all real x)"
learning_objectives:
  - Identify exponential functions and distinguish growth from decay by the base
  - Evaluate and graph exponential functions
  - Model repeated proportional change with exponential functions
  - Use the natural base e and convert between different bases
real_world_applications:
  - Population growth, radioactive decay, and compound interest
  - Epidemiological spread and cooling laws governed by proportional change
key_experiments:
  - "Fold a sheet repeatedly to observe area halving and thickness doubling (exponential change)"
provenance:
  ai_drafted: true
  source_kind: standards-or-specification
  source: "NCTM Principles and Standards for School Mathematics"
  reviewer: null
  reviewed_at: null
historical:
  stated_by: "Leonhard Euler (formalized e^x)"
  year: 1748
  where: "Introductio in Analysin Infinitorum"
  context: "Calculus and analysis"
  note: "Euler formalized the natural exponential function e^x and the constant e. Earlier exponential ideas predate the formal function: Bombelli (16th c.) worked on iterative growth, and exponential processes were used in finance and astronomy before the 18th century."
---