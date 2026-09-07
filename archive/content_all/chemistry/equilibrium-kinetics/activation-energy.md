---
id: stemma:chem.activation-energy
type: quantity
name: Activation Energy
domain: chemistry
status: draft
definition: >-
  The minimum energy that colliding reactant particles must possess for a reaction to occur, forming
  an activated complex. Activation energy governs the rate of a reaction through the exponential
  Arrhenius relationship with temperature.
symbol: E_a
unit: J mol⁻¹
equation: "k = A e^{−E_a/(RT)}  (Arrhenius equation)"
examples:
  - "Hydrogen and oxygen mixed at room temperature react negligibly despite a favourable equilibrium because E_a is high."
  - "A catalyst lowers activation energy, dramatically accelerating a reaction."
key_experiments:
  - "Measure a rate at several temperatures and extract E_a from an Arrhenius plot of ln k against 1/T."
common_misconceptions:
  - All collisions lead to reaction (only collisions with energy above E_a are effective).
  - Raising temperature always changes the reaction mechanism (it increases the fraction of energetic collisions).
learning_objectives:
  - Explain activation energy in terms of an energy barrier and activated complex.
  - Use the Arrhenius equation to relate rate constant to temperature.
  - Explain how catalysts lower activation energy.
real_world_applications:
  - Designing catalysts for fuel cells and industrial synthesis.
  - Controlling reaction kinetics in food preservation and explosives.
provenance:
  ai_drafted: true
  source_kind: standards-or-specification
  source: IUPAC Compendium of Chemical Terminology
---