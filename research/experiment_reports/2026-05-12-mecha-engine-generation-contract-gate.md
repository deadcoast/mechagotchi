# Experiment Report: Mecha Engine Generation Contract Gate

Date: 2026-05-12

## Objective

Define the acceptance contract for the future `mecha_engine.generation` package
module before moving generator code out of `labs/grid_genome`.

## Method

1. Re-read the research plan's generation track and package handoff sequence.
2. Re-read the `mecha_engine` module interface spec.
3. Re-read the Markov, constrained WFC-style, and SLIP generation experiment
   reports.
4. Re-read the generation lab tests and corpus summaries.
5. Checked current public references for PCG framing and the WFC reference
   implementation.
6. Wrote a prose gate and a machine-readable architecture artifact.

## Outputs

- `research/package_specs/mecha_engine_generation_contract_gate.md`
- `data/architecture/mecha_engine_generation_contract_gate_stage0.json`

## Findings

The package generator must preserve the research distinction between proposal
sources and production candidates:

- random mutation remains a baseline comparator: 42 valid out of 100;
- raw local Markov remains a weak proposal source: 13 valid out of 100;
- constrained local-pattern stabilization is the current package candidate:
  100 valid out of 100 and 100 unique signatures;
- SLIP-constrained generation is required in the generator path: 50 valid and
  aligned out of 50.

The required public surface is:

```python
from mecha_engine.generation import (
    explain_generation,
    generate_batch,
    generate_candidate,
    train_generation_model,
)
```

The package gate therefore requires generated candidates to pass the future
`mecha_engine.genome` API, preserve lineage and trace data, and avoid `labs/`
imports.

## Decision

Adopt the generation contract gate as the package acceptance checklist for the
future `mecha_engine.generation` module. Do not create `packages/mecha_engine`
in this research step.

Status: `research_generation_contract_gate_no_package_code`

## Verification Targets

These checks are valid after package implementation begins:

```powershell
python -B -m unittest discover -s .\packages\mecha_engine\tests -p "test_*.py"
python -c "from mecha_engine.generation import train_generation_model, generate_candidate, generate_batch, explain_generation"
rg -n "from labs|import labs|labs/|labs\\|sys\\.path" .\packages\mecha_engine
python -B .\labs\package_promotion\package_promotion_gate.py --root . --output-dir .\data\package_promotion
```

This research step only verifies the new gate artifacts and existing generation
lab evidence.

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
