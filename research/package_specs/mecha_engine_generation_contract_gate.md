# Mecha Engine Generation Contract Gate

Date: 2026-05-12

## Status

Research acceptance gate. This document does not create or modify
`packages/mecha_engine`.

## Purpose

Define the package-level contract for the future `mecha_engine.generation`
module before generator code is moved out of `labs/grid_genome`.

## Source Evidence

The Stage 0 generation labs already prove:

- Random mutation baseline: 42 valid candidates out of 100.
- Raw local Markov generation: 13 valid candidates out of 100.
- Constrained WFC-style stabilization: 100 valid candidates out of 100 and
  100 unique signatures.
- SLIP-constrained generation: 50 valid candidates out of 50 and 50 aligned
  candidates out of 50.

The package generator must reproduce the constrained-path guarantees through
the package import surface, not through `labs/` imports.

## Required Public Surface

```python
from mecha_engine.generation import (
    explain_generation,
    generate_batch,
    generate_candidate,
    train_generation_model,
)
```

Required contracts:

- `train_generation_model(seed_grids) -> GenerationModel`
- `generate_candidate(parent_grid, model, slip_profile=None, rng_seed=None) -> dict`
- `generate_batch(seed_grids, count, slip_profile=None, rng_seed=None) -> list[dict]`
- `explain_generation(candidate) -> dict`

## Model Acceptance

`train_generation_model` must:

- accept the 50 valid seed grids;
- reject an empty seed corpus;
- reject seed corpora containing invalid grids;
- preserve enough local-pattern evidence for constrained generation;
- avoid mutating seed-grid dictionaries;
- record model metadata sufficient to identify the training corpus and generator
  strategy.

Raw Markov-style local probabilities may be part of the model, but the package
generator must not expose raw Markov output as the sole production path.

## Candidate Acceptance

`generate_candidate` must:

- require a parent grid that passes `mecha_engine.genome.validate_grid`;
- return a grid genome that passes `mecha_engine.genome.validate_grid`;
- preserve `parent_grid_id`, lineage generation, and ancestor IDs;
- include mutation or generation events in lineage metadata;
- support deterministic output for the same parent, model, SLIP profile, and
  RNG seed;
- return a candidate whose ID is stable enough for batch traceability;
- preserve JSON Schema 2020-12 grid compatibility;
- avoid mutating the parent grid, model, or SLIP profile.

## Batch Acceptance

`generate_batch` must:

- return exactly `count` candidates;
- produce unique candidate IDs within the batch;
- produce deterministic batches for the same inputs and RNG seed;
- validate every returned candidate through the package genome API;
- beat the random mutation validity baseline of 42 valid candidates per 100;
- reproduce the constrained generator gate of 100 valid candidates per 100
  before package promotion;
- reproduce the SLIP-constrained gate of 50 valid and aligned candidates per 50
  when a valid SLIP profile is supplied.

## SLIP Acceptance

When `slip_profile` is supplied, generation must:

- validate the profile before candidate generation;
- fail clearly if no seed or parent grid can satisfy the profile;
- constrain allowed palettes;
- enforce body-mass bounds;
- enforce required organ roles;
- enforce mutation-rate maximums;
- return alignment evidence in the generation explanation.

## Explanation Acceptance

`explain_generation(candidate)` must return a JSON-serializable dictionary with
at least:

- `grid_id`
- `parent_grid_id`
- `generator_strategy`
- `rng_seed`
- `mutation_events`
- `validation`
- `slip_alignment`
- `accepted_proposals`
- `rejected_proposals`

The explanation must be sufficient for lineage, archive scoring, debugging, and
provenance without requiring access to `labs/`.

## Negative Checks

The generation package gate fails if:

- `packages/mecha_engine/src/mecha_engine/generation` imports `labs`;
- package tests import `labs`;
- package tests mutate `sys.path` to reach `labs`;
- raw Markov output is treated as the production generator without a validation
  or constraint pass;
- invalid candidates are silently dropped without trace data;
- generated candidates omit lineage or parent information;
- generated candidates mutate seed, parent, model, or SLIP inputs;
- package documentation claims full Wave Function Collapse adoption without
  implementing and testing entropy selection, propagation, and contradiction
  handling.

## Future Verification Commands

Run these after the scaffold and `generation` implementation exist:

```powershell
python -B .\labs\grid_genome\test_markov_grid.py
python -B .\labs\grid_genome\test_constrained_generator.py
python -B .\labs\grid_genome\test_slip_constraints.py
python -B -m unittest discover -s .\packages\mecha_engine\tests -p "test_*.py"
python -c "from mecha_engine.generation import train_generation_model, generate_candidate, generate_batch, explain_generation"
rg -n "from labs|import labs|labs/|labs\\|sys\\.path" .\packages\mecha_engine
python -B .\labs\package_promotion\package_promotion_gate.py --root . --output-dir .\data\package_promotion
git diff --check
```

Expected implementation-stage result:

- Lab generator tests still pass.
- Package generation tests pass through `mecha_engine.generation`.
- Package candidates validate through `mecha_engine.genome`.
- 100 unconstrained package candidates pass the constrained validity gate.
- 50 SLIP-constrained package candidates pass validation and alignment.
- The package contains no runtime or test imports from `labs`.
- Package-promotion gate is rerun after package generation tests exist.

## Non-Goals

- No package creation in this research step.
- No generator implementation migration.
- No full overlapping WFC claim.
- No lifecycle simulation implementation.
- No archive scoring implementation.
- No frontend or workshop generation UI.

## Sources

- `research/package_specs/mecha_engine_module_interfaces.md`
- `research/experiment_reports/2026-05-12-markov-local-generator.md`
- `research/experiment_reports/2026-05-12-constrained-wfc-style-generator.md`
- `research/experiment_reports/2026-05-12-slip-constraint-baseline.md`
- `research/algorithm_cards/random_mutation_baseline.md`
- `research/algorithm_cards/wave_function_collapse.md`
- `research/algorithm_cards/slip_schema_validator.md`
- `data/generated_grids/markov_local/README.md`
- `data/generated_grids/constrained_wfc_style/README.md`
- Procedural Content Generation in Games:
  https://www.pcgbook.com/
- WaveFunctionCollapse reference implementation:
  https://github.com/mxgmn/WaveFunctionCollapse
