# Experiment Report: SLIP Profile Compatibility Matrix

Date: 2026-05-12

## Objective

Continue the research plan's SLIP track by defining the Stage 0
`profile_compatibility_tests.md` artifact: a compatibility matrix connecting
current SLIP fixtures to generation, lifecycle, archive, workshop, and future
package gates.

## Method

1. Re-read `docs/01-brainstorming.md` and `docs/02-research_plan.md` for the
   SLIP role and required outputs.
2. Inspected current valid and invalid SLIP fixtures under `data/slips/`.
3. Inspected the lab validator and tests under `labs/grid_genome/`.
4. Re-read the SLIP constraint baseline, generation contract gate, property and
   negative test strategy, workshop round-trip report, and CA/NCA report.
5. Queried current JSON Schema and Pydantic documentation for future schema
   contract context.
6. Created a prose compatibility matrix and machine-readable JSON mirror.

## Outputs

- `research/slip/README.md`
- `research/slip/profile_compatibility_tests.md`
- `data/slips/slip_profile_compatibility_matrix_stage0.json`

## Findings

The current SLIP evidence is real but narrow:

```txt
valid profiles accepted: 3/3
invalid profiles rejected: 2/2
SLIP-constrained LCD generated grids: 50
SLIP-aligned LCD generated grids: 50
```

The validator currently proves palette constraints, body-mass bounds, required
organ roles, mutation caps, and bounded numeric weights. It does not yet prove
complete behavior vocabulary, behavior preview, mutation preview UI,
profile-weighted evolution, or community profile compatibility.

At authoring time, the most important uncovered gap was multi-profile
compatibility: `slip_lcd_seed` had a generated 50/50 valid-and-aligned
candidate corpus, while `slip_gray_stable` and `slip_amber_social` had only
profile-validator evidence.

Supersession note: the follow-up benchmark in
`research/experiment_reports/2026-05-12-slip-multi-profile-generation-benchmark.md`
closed that specific gap for the current three valid Stage 0 profiles.

## Decision

Adopt the Stage 0 SLIP compatibility matrix as the active profile compatibility
test plan. Do not claim full SLIP authoring compatibility until the blocked
surfaces are tested directly.

Status: `research_slip_profile_compatibility_matrix_no_package_code`

## Verification Plan

Research-stage verification:

```powershell
python -m json.tool .\data\slips\slip_profile_compatibility_matrix_stage0.json
Test-Path .\packages
rg -n "slip_profile_compatibility_matrix|research_slip_profile_compatibility_matrix_no_package_code|profile_compatibility_tests" .\research .\data
git diff --check
```

Existing lab reference checks:

```powershell
python -B -m unittest discover -s .\labs\grid_genome -p "test_*.py"
python -B -m unittest discover -s .\labs\workshop_editor -p "test_*.py"
```

Future package checks are valid only after package work starts.

## References

- `docs/01-brainstorming.md`
- `docs/02-research_plan.md`
- `data/slips/README.md`
- `labs/grid_genome/slip.py`
- `labs/grid_genome/test_slip_constraints.py`
- `research/algorithm_cards/slip_schema_validator.md`
- `research/experiment_reports/2026-05-12-slip-constraint-baseline.md`
- `research/experiment_reports/2026-05-12-workshop-roundtrip-baseline.md`
- `research/experiment_reports/2026-05-12-ca-nca-growth-repair.md`
- `research/package_specs/mecha_engine_generation_contract_gate.md`
- `research/package_specs/mecha_engine_property_negative_test_strategy.md`
