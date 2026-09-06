---
id: stemma:math.fundamental-theorem-of-calculus
type: law
name: Fundamental Theorem of Calculus
domain: mathematics
status: draft
definition: >-
  A theorem connecting differentiation and integration. Part 1 states that the derivative of the
  integral of f from a to x is exactly f(x); Part 2 states that a definite integral is evaluated
  by an antiderivative: ∫ₐᵇ f(x) dx = F(b) − F(a) whenever F′ = f. The theorem makes derivatives
  and integrals inverse operations.
symbol: null
unit: null
equation: "d/dx ∫ₐˣ f(t) dt = f(x)   and   ∫ₐᵇ f(x) dx = F(b) − F(a)"
examples:
  - "Since F = x³ is an antiderivative of f = 3x², ∫₁² 3x² dx = 2³ − 1³ = 7"
  - "The area under f(x) = 2x from 0 to 4 is F(4) − F(0) = 4² − 0 = 16"
common_misconceptions:
  - "The fundamental theorem applies only to areas (it links any rate of change to its accumulation)"
  - "Differentiation and integration are independent ideas (the theorem shows they are inverse)"
learning_objectives:
  - State both parts of the fundamental theorem of calculus
  - Use the theorem to evaluate definite integrals through antiderivatives
  - Explain how differentiation and integration are inverse operations
  - Apply the theorem to compute cumulative change from a rate of change
real_world_applications:
  - Converting velocity into distance travelled, and acceleration into velocity
  - Relating rates (marginal measures) to accumulated totals in science and finance
key_experiments:
  - "Show that the area-accumulation function F(x) = ∫ₐˣ f(t) dt has derivative f(x)"
provenance:
  ai_drafted: true
  source_kind: academic-or-research
  source: "Standard content of calculus curricula; classical theorem (Newton, Leibniz)"
  reviewer: null
  reviewed_at: null
historical:
  stated_by: "Isaac Newton and Gottfried Wilhelm Leibniz (independent)"
  year: 1666
  where: "Newton's early work; Leibniz's published formulation"
  context: "Calculus"
  note: "Developed independently by Newton (c. 1665-1666) and Leibniz (1670s; published 1693), giving rise to a priority dispute."
  timeline:
    - year: 1665
      by: "Isaac Newton"
      event: "Early development of the calculus relating differentiation and integration"
    - year: 1666
      by: "Isaac Newton"
      event: "Further development of the calculus (fluxions)"
    - year: 1693
      by: "Gottfried Wilhelm Leibniz"
      event: "Publication of the fundamental theorem of calculus"
---