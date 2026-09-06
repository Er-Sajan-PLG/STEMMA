---
id: stemma:math.probability
type: concept
name: Probability
domain: mathematics
status: draft
definition: >-
  A measure of the likelihood that an event will occur, expressed as a number between
  0 (impossible) and 1 (certain). P(E) = Number of favorable outcomes / Total number
  of possible outcomes (for equally likely outcomes).
symbol: P(E)
unit: null
equation: P(E) = n(E) / n(S)
examples:
  - "Fair coin: P(heads) = 1/2 = 0.5"
  - "Standard die: P(rolling 4) = 1/6 ≈ 0.167"
  - "Drawing an ace from deck: 4/52 = 1/13"
common_misconceptions:
  - "Probability can be greater than 1 or less than 0 (it's always 0 ≤ P ≤ 1)"
  - "Past outcomes affect future independent events (gambler's fallacy)"
  - "All outcomes are equally likely (often not true)"
learning_objectives:
  - Calculate probability for simple events
  - Understand sample space and events
  - "Apply addition rule: P(A or B) = P(A) + P(B) - P(A and B)"
  - Apply multiplication rule for independent events
  - Distinguish theoretical vs experimental probability
real_world_applications:
  - Weather forecasting
  - Insurance risk assessment
  - Genetics (inheritance patterns)
  - Games of chance
key_experiments:
  - "Coin toss experiment: experimental probability approaches theoretical as trials increase"
provenance:
  ai_drafted: true
  source_kind: standards-or-specification
  source: "NCTM Principles and Standards for School Mathematics"
  reviewer: null
  reviewed_at: null
historical:
  stated_by: "Blaise Pascal and Pierre de Fermat"
  year: 1654
  where: "Correspondence on the problem of points (dice problem)"
  context: "Probability and statistics"
  note: "The mathematical foundations of probability began in 1654 through the Pascal-Fermat correspondence; Girolamo Cardano had earlier written on games of chance (Liber de Ludo Aleae, c. 1560s, published posthumously 1663)."
  timeline:
    - year: 1560
      by: "Girolamo Cardano"
      event: "Early work on games of chance (Liber de Ludo Aleae, published 1663)"
    - year: 1654
      by: "Blaise Pascal and Pierre de Fermat"
      event: "Correspondence founding the mathematical theory of probability"
---