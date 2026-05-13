# Experiment Report: Mecha Engine Package Scaffold Decision

Date: 2026-05-12

## Objective

Complete the final v0.3 next-step item: produce a package-scaffold decision
record before creating `packages/mecha_engine`.

## Source Basis

Internal sources:

- `research/reports/mechagotchi_research_report_v0_3.md`
- `research/decision_records/0002-mecha-engine-package-promotion-gate.md`
- `research/decision_records/0003-mvp-architecture.md`
- `research/package_specs/mecha_engine_module_interfaces.md`
- `data/package_promotion/mecha_engine_package_promotion_gate_stage0.json`
- `data/architecture/mecha_engine_module_interface_specs_stage0.json`

External sources:

- https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/
- https://packaging.python.org/en/latest/specifications/pyproject-toml/

## Scope

Included:

- package scaffold decision record
- machine-readable scaffold decision artifact
- reconciliation between logical module specs and physical `src` layout
- creation gate for future scaffold work

Not included:

- creating `packages/`
- creating `packages/mecha_engine`
- moving lab code from `labs/`
- adding package metadata files
- package publishing

## Method

The decision was built from the current package-promotion gate, MVP
architecture, module interface specs, and current repository state.

The repository state check confirmed that `packages/` does not exist. The
promotion gate remains a design gate with zero promotion-ready candidates. The
package scaffold therefore defines a physical package shape without creating
it.

The physical scaffold uses a `src` layout:

```txt
packages/mecha_engine/src/mecha_engine/
```

This reconciles the earlier logical module paths with current Python packaging
guidance: modules such as `genome`, `generation`, `lifecycle`, `archive`, and
`provenance` are import modules under `mecha_engine`, not direct repository-root
imports.

## Decision Output

Decision record:

- `research/decision_records/0004-mecha-engine-package-scaffold.md`

Machine-readable artifact:

- `data/architecture/mecha_engine_package_scaffold_decision_stage0.json`

Status:

- `accepted_scaffold_design_package_creation_deferred`

Initial modules:

- `genome`
- `generation`
- `lifecycle`
- `archive`
- `provenance`

Deferred modules:

- `learning`
- `repair`
- `render`
- `storage`
- `slip`

## Findings

The package scaffold can be safely designed now, but package creation should be
a separate implementation step. The first scaffold may add metadata, import
package directories, type-marker plumbing, README text, and package import
tests. It must not move lab implementation code.

The next authorized implementation action is:

```txt
create_empty_src_layout_scaffold_when_explicitly_authorized
```

## Verification

Planned verification for this research step:

```powershell
python -m json.tool .\data\architecture\mecha_engine_package_scaffold_decision_stage0.json > $null
Test-Path .\packages
rg -n "0004-mecha-engine-package-scaffold|mecha_engine_package_scaffold_decision_stage0" research data
git diff --check
```

## Decision

Accept the scaffold design, defer package creation, and keep lab-code promotion
blocked until the package root exists, package tests exercise the installed
surface, and the package-promotion gate is re-run.

