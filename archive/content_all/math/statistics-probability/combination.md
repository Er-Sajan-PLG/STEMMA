---
id: stemma:math.combination
type: quantity
name: Combination
domain: mathematics
status: draft
definition: >-
  An unordered selection of items taken from a larger collection, where order does not matter. The
  number of ways to choose r items from n distinct items is C(n, r) = n! / (r! (n − r)!),
  often written as a binomial coefficient (n choose r).
symbol: C(n, r)
unit: null
equation: "C(n, r) = n! / (r! (n − r)!)   (0 ≤ r ≤ n)"
examples:
  - "C(4, 2) = 6: from {a, b, c, d} there are six two-element subsets"
  - "Choosing 3 members of a committee from 5 people gives C(5, 3) = 10"
  - "C(5, 2) = C(5, 3) by symmetry C(n, r) = C(n, n − r)"
  - "The coefficients of (x + y)ⁿ are binomial coefficients C(n, r)"
common_misconceptions:
  - "A combination counts the same as a permutation (a combination ignores order, giving fewer arrangements)"
  - "C(n, r) counts selections with repetition allowed (it assumes distinct items and no repetition)"
learning_objectives:
  - Distinguish combinations from permutations by whether order matters
  - Compute combinations with C(n, r) = n!/(r!(n − r)!)
  - Recognize binomial coefficients in expansion
  - Use combinations in probability counting
real_world_applications:
  - Selecting committees, teams, or samples where order is irrelevant
  - Lottery and sampling probabilities built on unordered draws
key_experiments:
  - "Form all handshakes among a small group and count the unordered pairs to match C(n, 2)"
provenance:
  ai_drafted: true
  source_kind: standards-or-specification
  source: "NCTM Principles and Standards for School Mathematics"
  reviewer: null
  reviewed_at: null
---