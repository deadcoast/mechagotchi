# Mecha Engine Runtime Boundary Gate

Date: 2026-05-13

Status: `research_runtime_boundary_gate_no_package_code`

Target package root: `packages/mecha_engine`

Package root exists at authoring: no

## Purpose

Define the package/runtime lifecycle boundary required before Stage 0 SLIP
runtime-selection, offspring-lineage, long-horizon, and multigeneration lineage
labs can be treated as package runtime behavior.

This is a research handoff artifact. It does not create package code, package
tests, dependency manifests, or runtime state. It exists to prevent lab-only
selectors from being promoted as profile-weighted evolution before the package
surface and manual readability calibration exist.

## Boundary Contracts

The Stage 0 gate defines five contracts:

| Contract | Package target | Boundary decision |
| --- | --- | --- |
| `package_import_boundary` | `packages/mecha_engine/src/mecha_engine` | Runtime code and tests must import `mecha_engine`, not `labs`. |
| `lifecycle_runtime_boundary` | `packages/mecha_engine/src/mecha_engine/lifecycle` | Lifecycle episodes must be package-validated, bounded, deterministic where specified, and free of online learner memory writes. |
| `slip_profile_runtime_validation_boundary` | deferred `mecha_engine.slip` surface | Runtime JSON Schema validation and any Pydantic dependency must be declared in package metadata before runtime claims. |
| `archive_readability_boundary` | `packages/mecha_engine/src/mecha_engine/archive` | Readability-aware descriptors must expose calibration status and cannot lock human thresholds from proxy scores. |
| `lineage_runtime_state_boundary` | deferred runtime state surface | Persistent lineage state remains lab-only until package lifecycle/archive modules and a state contract exist. |

All five contracts forbid `labs` as a package runtime dependency.

## Negative Probes

The gate rejects these premature transitions:

- package runtime code importing from `labs`;
- package tests mutating `sys.path` to reach lab directories;
- profile-weighted evolution claims before package runtime integration and
  manual readability calibration;
- runtime JSON Schema validation claims without a declared dependency manifest;
- package promotion while `packages/mecha_engine` is absent.

## Stage 0 Evidence

The generated artifact records:

- contract count: `5`;
- contracts with source evidence: `5`;
- package root exists: `false`;
- manual readability rating rows: `0`;
- expected manual readability rows: `63`;
- manual readability calibration ready: `false`;
- package runtime integration ready: `false`;
- profile-weighted evolution ready: `false`;
- negative probes rejected: `5 / 5`;
- package promotion-ready contracts: `0`.

## Blocked States

The following remain blocked:

- runtime JSON Schema validation;
- declared Pydantic package dependency;
- package runtime lifecycle integration;
- manual readability calibration;
- profile-weighted evolution;
- package import-surface tests;
- package promotion.

## Future Package Verification

Only after package implementation is explicitly started:

```powershell
Test-Path .\packages\mecha_engine
python -B -m unittest discover -s .\packages\mecha_engine\tests -p "test_*.py"
python -c "import mecha_engine, mecha_engine.lifecycle, mecha_engine.archive"
rg -n "from labs|import labs|labs/|labs\\|sys\.path" .\packages\mecha_engine
python -B .\labs\package_promotion\package_promotion_gate.py --root . --output-dir .\data\package_promotion
```

These commands are intentionally not valid in the current research-only state
because `packages/mecha_engine` does not exist.

## Research Verification

```powershell
python -B -m unittest .\labs\architecture\test_mecha_engine_runtime_boundary_gate.py
python -B .\labs\architecture\mecha_engine_runtime_boundary_gate.py --root . --report-path .\data\architecture\mecha_engine_runtime_boundary_gate_stage0.json --output-dir .\data\architecture\mecha_engine_runtime_boundary_gate_stage0
python -m json.tool .\data\architecture\mecha_engine_runtime_boundary_gate_stage0.json
Test-Path .\packages
rg -n "mecha_engine_runtime_boundary_gate|research_runtime_boundary_gate_no_package_code" .\research .\data .\labs
git diff --check
```

## Decision

Adopt this runtime boundary gate as the next package-handoff layer.

Do not claim profile-weighted evolution until both conditions are true:

1. package runtime lifecycle/archive integration exists through
   `mecha_engine` package imports; and
2. the 63-row SLIP readability reviewer matrix is collected and passes the
   calibration gate.

## References

- `docs/01-brainstorming.md`
- `docs/02-research_plan.md`
- `research/decision_records/0004-mecha-engine-package-scaffold.md`
- `research/package_specs/mecha_engine_lifecycle_contract_gate.md`
- `research/package_specs/mecha_engine_archive_contract_gate.md`
- `research/package_specs/mecha_engine_contract_traceability_matrix.md`
- `research/package_specs/mecha_engine_formal_invariant_dependency_gate.md`
- `research/slip/profile_compatibility_tests.md`
- `data/architecture/mecha_engine_runtime_boundary_gate_stage0.json`
- Python Packaging User Guide, src layout vs flat layout:
  https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/
- Python Packaging User Guide, writing `pyproject.toml`:
  https://packaging.python.org/en/latest/guides/writing-pyproject-toml/
- JSON Schema Draft 2020-12: https://json-schema.org/draft/2020-12
