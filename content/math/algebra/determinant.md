---
id: stemma:math.determinant
type: quantity
name: Determinant
domain: mathematics
status: draft
definition: >-
  A scalar value computed from a square matrix that encodes geometric and algebraic properties of
  the matrix, such as whether its linear transformation is invertible. For a 2 × 2 matrix
  [[a, b], [c, d]] the determinant is ad − bc. A zero determinant means the matrix is singular.
symbol: det(A)  |  |A|
unit: null
equation: "det([[a, b], [c, d]]) = ad − bc"
examples:
  - "det([[2, 1], [4, 3]]) = 6 − 4 = 2"
  - "det([[1, 2], [2, 4]]) = 4 − 4 = 0 (singular)"
  - "For a 3 × 3 matrix the determinant is found by cofactor expansion"
  - "The determinant of an identity matrix is 1"
common_misconceptions:
  - "The determinant is defined for any rectangular matrix (it is defined only for square matrices)"
  - "A non-zero determinant and invertibility are unrelated (a non-zero determinant guarantees an inverse)"
learning_objectives:
  - Compute 2 × 2 determinants directly and larger ones by cofactor expansion
  - Use the determinant to decide invertibility of a matrix
  - Relate the absolute determinant to signed area in two dimensions
  - Solve systems using Cramer's rule where appropriate
real_world_applications:
  - Testing whether a system of linear equations has a unique solution
  - Computing areas and volumes from coordinates of geometric shapes
key_experiments:
  - "Verify that det maps a pair of vectors to the signed area of their parallelogram"
provenance:
  ai_drafted: true
  source_kind: standards-or-specification
  source: "NCTM Principles and Standards for School Mathematics"
  reviewer: null
  reviewed_at: null
---