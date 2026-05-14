# Experiment Report: Mecha Engine Runtime Boundary Gate

Date: 2026-05-13

## Objective

Continue the research plan's current next step by integrating
package/runtime lifecycle boundaries without creating `packages/`, moving lab
code, fabricating readability ratings, or claiming profile-weighted evolution.

## Source Basis

Internal sources:

- `docs/01-brainstorming.md`
- `docs/02-research_plan.md`
- `research/decision_records/0004-mecha-engine-package-scaffold.md`
- `research/package_specs/mecha_engine_module_interfaces.md`
- `research/package_specs/mecha_engine_lifecycle_contract_gate.md`
- `research/package_specs/mecha_engine_archive_contract_gate.md`
- `research/package_specs/mecha_engine_contract_traceability_matrix.md`
- `research/package_specs/mecha_engine_formal_invariant_dependency_gate.md`
- `research/slip/profile_compatibility_tests.md`
- `data/slips/slip_profile_compatibility_matrix_stage0.json`
- `data/readability/slip_readability_calibration_gate_stage0.json`
- `data/package_promotion/mecha_engine_package_promotion_gate_stage0.json`

External anchors:

- https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/
- https://packaging.python.org/en/latest/guides/writing-pyproject-toml/
- https://json-schema.org/draft/2020-12

## Method

1. Re-read the current package-scaffold decision, package promotion gate,
   lifecycle/archive package contracts, formal invariant gate, and SLIP
   compatibility matrix.
2. Verified that the next documented SLIP research step requires package/runtime
   lifecycle boundaries and 63 manual readability reviewer rows.
3. Treated the 63 reviewer rows as unavailable external human input rather than
   a value to synthesize.
4. Added a lab gate that defines runtime boundary contracts and negative probes
   while preserving package absence.
5. Generated a machine-readable Stage 0 boundary artifact.

## Outputs

- Lab implementation:
  `labs/architecture/mecha_engine_runtime_boundary_gate.py`
- Lab tests:
  `labs/architecture/test_mecha_engine_runtime_boundary_gate.py`
- Package spec:
  `research/package_specs/mecha_engine_runtime_boundary_gate.md`
- Machine-readable artifact:
  `data/architecture/mecha_engine_runtime_boundary_gate_stage0.json`
- Artifact folder:
  `data/architecture/mecha_engine_runtime_boundary_gate_stage0/`

## Results

Summary from the generated artifact:

- contracts: `5`;
- contracts with source evidence: `5`;
- package root exists: `false`;
- manual readability rating rows: `0`;
- expected manual readability rows: `63`;
- manual readability calibration ready: `false`;
- package runtime integration ready: `false`;
- profile-weighted evolution ready: `false`;
- negative probes rejected: `5 / 5`;
- package promotion-ready contracts: `0`.

## Findings

The current Stage 0 runtime selector, offspring lineage gate, long-horizon
behavior gate, and multigeneration lineage runner are strong lab evidence. They
are not package runtime integration because there is no package import surface,
no package dependency manifest, no package lifecycle/archive implementation, and
no manual readability calibration.

The correct research move is therefore a boundary gate, not a package scaffold
and not an evolution claim.

## Blocked States

These remain blocked:

- runtime JSON Schema validation;
- declared Pydantic package dependency;
- package runtime lifecycle integration;
- manual readability calibration;
- profile-weighted evolution;
- package import-surface tests;
- package promotion.

## Decision

Status: `research_runtime_boundary_gate_no_package_code`.

Adopt the runtime boundary gate as the current package-handoff layer. Continue
to require explicit package implementation authorization before creating
`packages/mecha_engine`. Continue to require 63 real SLIP readability reviewer
rows before claiming profile-weighted evolution.

## Verification

Research-step verification:

```powershell
python -B -m unittest .\labs\architecture\test_mecha_engine_runtime_boundary_gate.py
python -B .\labs\architecture\mecha_engine_runtime_boundary_gate.py --root . --report-path .\data\architecture\mecha_engine_runtime_boundary_gate_stage0.json --output-dir .\data\architecture\mecha_engine_runtime_boundary_gate_stage0
python -m json.tool .\data\architecture\mecha_engine_runtime_boundary_gate_stage0.json
Test-Path .\packages
rg -n "mecha_engine_runtime_boundary_gate|research_runtime_boundary_gate_no_package_code" .\research .\data .\labs
git diff --check
```

Future package verification remains invalid until package implementation starts.
