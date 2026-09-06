---
id: stemma:math.permutation
type: quantity
name: Permutation
domain: mathematics
status: draft
definition: >-
  An ordered arrangement of a subset of items drawn from a larger collection, where order matters.
  The number of ways to arrange r items selected from n distinct items is
  P(n, r) = n! / (n − r)!; arranging all n items gives n! possibilities.
symbol: P(n, r)
unit: null
equation: "P(n, r) = n! / (n − r)!   (0 ≤ r ≤ n)"
examples:
  - "P(3, 2) = 6: from {a, b, c} there are 3 × 2 ordered pairs"
  - "The letters of a 4-token word can be ordered in 4! = 24 ways"
  - "Choosing a president, vice-president, and treasurer from 5 people gives P(5, 3) = 60 ordered outcomes"
  - "P(n, 0) = 1 for any n (the empty arrangement)"
common_misconceptions:
  - "Permutations and combinations are the same (permutations count ordered arrangements; combinations ignore order)"
  - "Factorials count arrangements only when all items are distinct (repeated items require dividing out repeats)"
learning_objectives:
  - Distinguish situations where order matters from those where it does not
  - Compute permutations with the formula P(n, r) = n!/(n − r)!
  - Use the multiplication principle to count ordered outcomes
  - Translate counting problems into permutation statements
real_world_applications:
  - Ranking outcomes and scheduling where order determines meaning
  - Cryptographic and lock arrangements built on ordered selections
key_experiments:
  - "List systematically all two-letter arrangements of a small set to verify the formula by counting"
provenance:
  ai_drafted: true
  source_kind: standards-or-specification
  source: "NCTM Principles and Standards for School Mathematics"
  reviewer: null
  reviewed_at: null
---