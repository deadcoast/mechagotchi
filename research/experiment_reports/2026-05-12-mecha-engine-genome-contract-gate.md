# Experiment Report: Mecha Engine Genome Contract Gate

Date: 2026-05-12

## Objective

Define the acceptance contract for the future `mecha_engine.genome` package
module before moving the grid validator out of `labs/grid_genome`.

## Method

1. Re-read the post-v0.4 handoff sequence.
2. Re-read the module interface specs for `mecha_engine`.
3. Re-read the grid genome invariants and schema.
4. Re-used the existing validator baseline evidence for the seed and invalid
   corpora.
5. Checked current external documentation for JSON Schema validation and Python
   `unittest` discovery.
6. Wrote a prose gate and a machine-readable architecture artifact.

## Outputs

- `research/package_specs/mecha_engine_genome_contract_gate.md`
- `data/architecture/mecha_engine_genome_contract_gate_stage0.json`

## Findings

The next package-facing risk is not the empty scaffold itself; it is losing the
semantic validator guarantees when the validator becomes a public package
module.

The package contract therefore needs to prove the same corpus behavior as the
lab baseline:

- all 50 seed grids accepted;
- all 200 invalid counterexamples rejected;
- schema checks and semantic checks remain aligned;
- input dictionaries are not mutated;
- package tests import through `mecha_engine.genome`, not `labs`.

The required public surface is:

```python
from mecha_engine.genome import (
    ValidationResult,
    grid_signature,
    render_packet_from_grid,
    validate_grid,
    validate_grid_file,
)
```

## Decision

Adopt the genome contract gate as the first package implementation acceptance
check. Do not create `packages/mecha_engine` in this research step.

Status: `research_genome_contract_gate_no_package_code`

## Verification Targets

These checks are valid after package implementation begins:

```powershell
python -B -m unittest discover -s .\packages\mecha_engine\tests -p "test_*.py"
python -c "from mecha_engine.genome import validate_grid, validate_grid_file, grid_signature, render_packet_from_grid"
rg -n "from labs|import labs|labs/|labs\\|sys\\.path" .\packages\mecha_engine
python -B .\labs\package_promotion\package_promotion_gate.py --root . --output-dir .\data\package_promotion
```

This research step only verifies the new gate artifacts and the existing lab
validator baseline.

## Sources

- `research/package_specs/mecha_engine_module_interfaces.md`
- `research/grid_genome/grid_invariants.md`
- `research/grid_genome/grid_genome.schema.json`
- `research/experiment_reports/2026-05-12-grid-validator-baseline.md`
- `data/architecture/mecha_engine_module_interface_specs_stage0.json`
- JSON Schema Draft 2020-12 validation specification:
  https://json-schema.org/draft/2020-12/json-schema-validation
- Python `unittest` documentation:
  https://docs.python.org/3/library/unittest.html
