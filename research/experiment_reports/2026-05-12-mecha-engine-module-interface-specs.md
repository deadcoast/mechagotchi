# Experiment Report: Mecha Engine Module Interface Specs

Date: 2026-05-12

## Objective

Complete the first v0.3 next-step item: create package module interface specs
for `genome`, `generation`, `lifecycle`, `archive`, and `provenance`.

This step is explicitly research-only. It defines the future package contracts
without creating `packages/mecha_engine`.

## Method

Inputs reviewed:

- `research/reports/mechagotchi_research_report_v0_3.md`
- `research/decision_records/0002-mecha-engine-package-promotion-gate.md`
- `research/decision_records/0003-mvp-architecture.md`
- `research/grid_genome/grid_genome.schema.json`
- `research/grid_genome/grid_invariants.md`
- Lab surfaces for validator, constrained generation, lifecycle simulation,
  extended MAP-Elites descriptors, and provenance CI.

External standards checked:

- Python package metadata and package boundary guidance from the Python
  Packaging User Guide.
- JSON Schema Draft 2020-12, matching the current grid-genome schema.
- SPDX license-expression syntax for the provenance module.

## Outputs

- `research/package_specs/mecha_engine_module_interfaces.md`
- `data/architecture/mecha_engine_module_interface_specs_stage0.json`

## Interface Summary

| Module | Target path | Status |
| --- | --- | --- |
| `genome` | `packages/mecha_engine/genome` | Interface specified |
| `generation` | `packages/mecha_engine/generation` | Interface specified |
| `lifecycle` | `packages/mecha_engine/lifecycle` | Interface specified |
| `archive` | `packages/mecha_engine/archive` | Interface specified |
| `provenance` | `packages/mecha_engine/provenance` | Interface specified |

## Decisions

- Keep this as an interface specification, not package scaffolding.
- Preserve the current promotion rule: no lab code moves into `packages/`
  while `packages/mecha_engine` is absent.
- Make `genome.validate_grid` the first cross-module gate.
- Treat constrained generation as the MVP generator path; raw Markov remains a
  proposal source.
- Keep online reward shaping and CA/NCA repair out of this first package
  interface.
- Require provenance checks before package promotion.

## Result

The v0.3 package-design handoff now has concrete module interfaces for the first
five package surfaces. This makes the next decision point narrower: either
collect blocked research evidence, or produce a package-scaffold decision
record before creating `packages/mecha_engine`.

## Sources

- Python Packaging User Guide, `pyproject.toml` specification:
  https://packaging.python.org/en/latest/specifications/pyproject-toml/
- Python Packaging User Guide, `src` layout discussion:
  https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/
- JSON Schema Draft 2020-12:
  https://json-schema.org/draft/2020-12
- SPDX License Expressions:
  https://spdx.github.io/spdx-spec/v2.2.2/SPDX-license-expressions/

