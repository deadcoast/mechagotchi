# Research Glossary

## Companion Terms

- Mechagotchi: the companion instance generated, simulated, rendered, and
  evolved by the platform.
- Grid genome: the structured grid object that stores cells, semantic roles,
  mutation permissions, organs, palette, and render constraints.
- Phenotype grid: the renderable body expressed by a grid genome after
  validation and interpretation.
- Organ: a named semantic region such as sensor, expression anchor, shell,
  joint, or body core.
- Render packet: the engine output consumed by a visual client. The engine
  should not depend on a specific renderer.

## System Terms

- mecha_engine: core simulation, generation, mutation, learning, archive, and
  render-packet system.
- mecha_workshop: authoring environment for semantic grid editing, SLIP profile
  creation, preview, import, export, and provenance review.
- SLIP: Synthetic Learning Intelligence Profile. A versioned profile that
  defines constraints, priors, mutation permissions, behavior weights, and
  authoring intent.
- mecha_darwin: evolution and archive layer responsible for preserving useful
  lineages and diverse species niches.
- mecha_switchboard: decision integrator that receives micro-learner signals and
  selects the next companion action.

## Research Terms

- Algorithm card: one-page evaluation record for a candidate algorithm.
- Lab prototype: disposable experiment under `labs/`, not production code.
- Decision record: permanent note that explains an adoption, rejection, or
  sequencing decision.
- Baseline: the simplest comparator required before claiming improvement.
- Go/no-go gate: measurable condition that decides whether a candidate advances.
- Provenance ledger: machine-readable record of external source, license,
  creator, hash, modifications, and redistribution status.

## Method Terms

- Markov model: probabilistic local transition model for grid cells, rows,
  organs, animation frames, or behavior sequences.
- WFC: Wave Function Collapse, an example-based local-pattern and constraint
  propagation method.
- MAP-Elites: quality-diversity archive that stores high-performing individuals
  across behavior niches.
- CUBFF: CUDA-capable implementation for BFF-style computational-life
  experiments with self-modifying program soups.
- CTM: Continuous Thought Machine, used here only as inspiration for internal
  time, synchronization, and confidence-gated deliberation.

