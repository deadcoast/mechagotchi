# Experiment Report: Mecha Engine Scaffold Verification Gate

Date: 2026-05-12

## Objective

Continue the post-v0.4 research handoff without creating package code by
defining the acceptance gate for the future `packages/mecha_engine` scaffold.

## Source Basis

Internal sources:

- `research/decision_records/0004-mecha-engine-package-scaffold.md`
- `research/reports/mechagotchi_research_report_v0_4.md`
- `data/architecture/mecha_engine_package_scaffold_decision_stage0.json`
- `data/package_promotion/mecha_engine_package_promotion_gate_stage0.json`

External sources:

- https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/
- https://packaging.python.org/en/latest/specifications/pyproject-toml/

## Scope

Included:

- scaffold verification plan
- import-surface acceptance checks
- negative checks against lab imports, `sys.path` bypasses, early license
  metadata, and lab-code copying
- future verification command list

Not included:

- creating `packages/`
- creating `packages/mecha_engine`
- installing an editable package
- moving lab implementation code
- rerunning the package-promotion gate against a package root

## Method

The v0.4 report allows the empty package scaffold only when package
implementation is explicitly started. This research step therefore defines the
verification gate that should be applied after that future scaffold exists.

The gate keeps the first package step narrow:

1. Create the exact `src/mecha_engine` scaffold.
2. Prove imports through `mecha_engine`.
3. Prove tests do not import or path-inject `labs/`.
4. Prove no lab implementation code was moved.
5. Rerun the package-promotion gate after the scaffold exists.

## Outputs

Specification:

- `research/package_specs/mecha_engine_scaffold_verification_gate.md`

Machine-readable gate:

- `data/architecture/mecha_engine_scaffold_verification_gate_stage0.json`

Status:

- `research_verification_gate_no_package_code`

## Findings

The package scaffold decision was concrete enough to define testable acceptance
criteria before implementation starts. The most important guardrails are the
negative checks: no `labs` imports in package code/tests, no package-test
`sys.path` bypasses, no copied lab implementation, and no release license
metadata before a license decision exists.

This keeps package creation separate from package promotion.

## Verification

Verification commands for this research artifact:

```powershell
python -m json.tool .\data\architecture\mecha_engine_scaffold_verification_gate_stage0.json > $null
Test-Path .\packages
rg -n "mecha_engine_scaffold_verification_gate|research_verification_gate_no_package_code" research data
git diff --check
```

## Decision

Adopt the scaffold verification gate as the next package-handoff artifact. Do
not create `packages/mecha_engine` until package implementation is explicitly
started.

