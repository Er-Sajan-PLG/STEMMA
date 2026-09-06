---
id: stemma:math.standard-deviation
type: quantity
name: Standard Deviation
domain: mathematics
status: draft
definition: >-
  A measure of dispersion that quantifies how spread out a data set is around its mean. It is the
  square root of the variance; for a set x₁, …, xₙ it equals sqrt((1/n) Σ (xᵢ − μ)²) where μ is the
  mean. A small standard deviation indicates values clustered near the mean, and a large one
  indicates wide spread.
symbol: σ  (population);  s  (sample)
unit: null
equation: "σ = sqrt( Σ (xᵢ − μ)² / n )"
examples:
  - "The set {5, 5, 5, 5, 5} has standard deviation 0"
  - "The set {2, 4, 6, 8, 10} has a small standard deviation"
  - "The set {1, 1, 10, 10} spreads far around its mean, giving a larger standard deviation"
  - "Standard deviation shares the units of the original data, unlike variance"
common_misconceptions:
  - "Standard deviation and mean measure the same thing (the mean locates the centre; the standard deviation measures spread)"
  - "A larger range always means a larger standard deviation is needed in every set (range ignores order and clustering of values)"
learning_objectives:
  - Compute variance and standard deviation for a data set
  - Interpret standard deviation as a measure of spread around the mean
  - Compare data sets by their dispersion
  - Relate standard deviation to the normal-distribution model
real_world_applications:
  - Assessing risk in finance through return volatility
  - Quality control, where the spread of measurements signals process variation
key_experiments:
  - "Generate two data sets with the same mean but different spreads and compare deviations"
provenance:
  ai_drafted: true
  source_kind: standards-or-specification
  source: "NCTM Principles and Standards for School Mathematics"
  reviewer: null
  reviewed_at: null
historical:
  stated_by: "Karl Pearson"
  year: 1893
  where: "Statistical lectures and writings on the root-mean-square deviation"
  context: "Statistics"
  note: "Pearson introduced the standard deviation in the early 1890s as the root-mean-square deviation, building on Gauss's earlier method of least squares."
---