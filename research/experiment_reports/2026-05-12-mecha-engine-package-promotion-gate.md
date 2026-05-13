# Experiment Report: Mecha Engine Package Promotion Gate

Date: 2026-05-12

## Objective

Define when research labs may be considered for promotion into
`packages/mecha_engine`, without creating or moving package code prematurely.

This follows the v0.2 next-step requirement to define package promotion
criteria for `packages/mecha_engine`.

## Method

The gate evaluates each candidate against seven criteria:

1. Research artifacts are complete.
2. Candidate metrics meet component-specific thresholds.
3. The intended package boundary is named.
4. A focused verification command exists.
5. Provenance, source, license, and attribution checks are clean.
6. `packages/mecha_engine` exists.
7. Open research blockers are resolved.

The package criteria were informed by the Python Packaging User Guide guidance
for modern `pyproject.toml` metadata and import layout choices, especially the
need for an explicit package boundary before moving lab code.

## Outputs

- Gate implementation: `labs/package_promotion/package_promotion_gate.py`
- Gate tests: `labs/package_promotion/test_package_promotion_gate.py`
- Metric artifact:
  `data/package_promotion/mecha_engine_package_promotion_gate_stage0.json`
- Criteria summary:
  `data/package_promotion/mecha_engine_package_promotion_criteria.md`
- Decision record:
  `research/decision_records/0002-mecha-engine-package-promotion-gate.md`

## Results

Summary from the gate run:

- Package root exists: false
- Criteria count: 7
- Candidate count: 6
- Research-ready count: 5
- Package-design-ready count: 3
- Promotion-ready count: 0
- Blocked count: 1
- Hold-research-only count: 2

Candidate outcomes:

- `lifecycle_simulator`: ready for package design, blocked from promotion
  because the package root and target package are absent.
- `map_elites_archive`: ready for package design, blocked from promotion
  because the package root and target package are absent.
- `provenance_ci`: ready for package design, blocked from promotion because the
  package root and target package are absent.
- `switchboard_feedback`: hold as research only because reward shaping is wired
  but has not beaten the frozen baseline.
- `ca_nca_repair`: hold as research only because the current result is an
  assisted target-template lab baseline, not a trained NCA.
- `readability_gate`: blocked because real human ratings have not been
  collected.

## Decision

Status: `criteria_defined_no_package_promotion`.

Research evidence is now strong enough to identify package-design candidates,
but `packages/mecha_engine` does not exist. No lab code should be promoted yet.

The first candidates for package design are:

1. `lifecycle_simulator` -> `packages/mecha_engine/lifecycle`
2. `map_elites_archive` -> `packages/mecha_engine/archive`
3. `provenance_ci` -> `packages/mecha_engine/provenance`

Promotion remains blocked until the package root exists, target boundaries are
created intentionally, and all candidate-specific research blockers are cleared.

## Sources

- Python Packaging User Guide, "Writing your pyproject.toml":
  https://packaging.python.org/en/latest/guides/writing-pyproject-toml/
- Python Packaging User Guide, "src layout vs flat layout":
  https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/

