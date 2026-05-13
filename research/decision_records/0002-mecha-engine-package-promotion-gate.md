# Decision Record 0002: Mecha Engine Package Promotion Gate

Date: 2026-05-12

## Status

Accepted.

## Context

The v0.2 research report names package promotion criteria for
`packages/mecha_engine` as the next required research step. The repository does
not currently contain a `packages/` directory or `packages/mecha_engine` package
root.

Research has produced several lab candidates with algorithm cards, experiment
reports, metric artifacts, and focused tests. Some are ready to inform package
design; none should be moved into package code without an explicit package
boundary and verification surface.

## Decision

Adopt a promotion gate with seven required checks:

1. Research artifacts complete.
2. Metric thresholds met.
3. Package boundary defined.
4. Verification surface defined.
5. Provenance gate clean.
6. `packages/mecha_engine` exists.
7. Candidate-specific research blockers resolved.

The current gate decision is `criteria_defined_no_package_promotion`.

The following candidates may inform package design once a package root is
created:

- `lifecycle_simulator` for `packages/mecha_engine/lifecycle`
- `map_elites_archive` for `packages/mecha_engine/archive`
- `provenance_ci` for `packages/mecha_engine/provenance`

The following candidates remain research-only:

- `switchboard_feedback`, because reward shaping is wired but has not yet
  beaten the frozen baseline.
- `ca_nca_repair`, because the current result is a lab-only assisted
  target-template baseline.

The readability gate remains blocked until real human ratings are collected.

## Consequences

- Research labs can be evaluated consistently before package design starts.
- Lab code does not move into `packages/` just because it passed a local
  experiment.
- Package design should begin with lifecycle, archive, and provenance surfaces.
- Human evaluation, reward shaping, and trained repair remain open research
  risks.

## Evidence

- `labs/package_promotion/package_promotion_gate.py`
- `labs/package_promotion/test_package_promotion_gate.py`
- `data/package_promotion/mecha_engine_package_promotion_gate_stage0.json`
- `data/package_promotion/mecha_engine_package_promotion_criteria.md`
- `research/experiment_reports/2026-05-12-mecha-engine-package-promotion-gate.md`

