---
id: stemma:math.matrix
type: concept
name: Matrix
domain: mathematics
status: draft
definition: >-
  A rectangular array of numbers (or other entries) arranged in rows and columns, usually written
  within brackets. A matrix with m rows and n columns has size m × n. Matrices have defined
  operations — addition, scalar multiplication, multiplication, and transposition — and provide a
  compact representation for systems of linear equations and linear transformations.
symbol: A
unit: null
equation: "A = [aᵢⱼ]  (i = 1,…,m; j = 1,…,n)"
examples:
  - "A 2 × 2 matrix: [[1, 2], [3, 4]]"
  - "A column vector is a matrix with one column: [[1], [2], [3]]"
  - "Matrix multiplication is defined only when the inner dimensions match"
  - "An identity matrix I has 1s on the diagonal and 0s elsewhere"
common_misconceptions:
  - "Matrix multiplication is commutative (in general AB ≠ BA)"
  - "A number times a matrix equals the matrix times an added constant (scalar multiplication multiplies every entry)"
learning_objectives:
  - Identify the size and entries of a matrix
  - Add, subtract, and scalar-multiply matrices
  - Multiply matrices and understand the dimension requirement
  - Represent systems of linear equations and transformations with matrices
real_world_applications:
  - Computer graphics transformations (rotation, scaling, translation) encoded as matrices
  - Organizing and solving systems in economics, statistics, and engineering
key_experiments:
  - "Encode a rotations and scalings on a shape by multiplying column vectors by matrices"
provenance:
  ai_drafted: true
  source_kind: standards-or-specification
  source: "NCTM Principles and Standards for School Mathematics"
  reviewer: null
  reviewed_at: null
historical:
  stated_by: "Arthur Cayley"
  year: 1858
  where: "'A Memoir on the Theory of Matrices'"
  context: "Algebra / linear algebra"
  note: "Cayley formalized the theory of matrices in 1858. Earlier matrix-like techniques existed, notably Gauss's elimination method for solving linear systems (c. early 1800s)."
  timeline:
    - year: 1810
      by: "Carl Friedrich Gauss"
      event: "Elimination method for solving systems of linear equations (predecessor technique)"
    - year: 1858
      by: "Arthur Cayley"
      event: "Publication of A Memoir on the Theory of Matrices, founding matrix algebra"
---