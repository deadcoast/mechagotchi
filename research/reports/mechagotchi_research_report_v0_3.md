# Mechagotchi Research Report v0.3

Date: 2026-05-12

## Executive Summary

The post-v0.2 research sequence closes the remaining research-to-architecture
loop. The project now has a manual readability intake gate, a lifecycle reward
feedback benchmark, repeated stochastic CA/NCA repair stress, a package
promotion gate, and an accepted MVP architecture decision.

The strongest conclusion is conservative: Mechagotchi is ready for package
design, not package promotion. `packages/mecha_engine` does not exist yet, real
human readability ratings have not been collected, reward feedback does not yet
beat the frozen baseline, and CA/NCA repair remains an assisted lab benchmark.

The MVP architecture should start from engine contracts, not workshop polish:

```txt
SLIP profile
  -> seed or parent grid genome
  -> constrained generator
  -> validator, readability, and lifecycle gates
  -> switchboard policy
  -> archive and lineage update
  -> render packet
  -> event log
  -> next mutation or generation
```

## Research Scope

This report consolidates the v0.2 follow-up sequence:

1. Create manual readability rating intake and aggregation gate.
2. Connect lifecycle rewards back into switchboard action-reward updates.
3. Add repeated stochastic damage to the CA/NCA repair benchmark.
4. Define package promotion criteria for `packages/mecha_engine`.
5. Produce an MVP architecture decision record from the v0.1 and v0.2 reports.

## Primary Artifacts

| Area | Artifact |
| --- | --- |
| Manual readability intake | `data/readability/manual_readability_rating_intake_stage0.json` |
| Switchboard feedback | `data/micro_learners/switchboard_lifecycle_feedback_stage0.json` |
| Repeated stochastic repair | `data/cellular_automata/ca_nca_repeated_stochastic_damage_stage0.json` |
| Package promotion gate | `data/package_promotion/mecha_engine_package_promotion_gate_stage0.json` |
| MVP architecture | `data/architecture/mvp_architecture_decision_stage0.json` |
| Package decision | `research/decision_records/0002-mecha-engine-package-promotion-gate.md` |
| MVP decision | `research/decision_records/0003-mvp-architecture.md` |

## Experiment Results

| Experiment | Result | Decision |
| --- | ---: | --- |
| Manual readability intake | 30 template rows; 0 reviewer rows; 0 rated samples | Block proxy calibration until ratings exist |
| Switchboard lifecycle feedback | 48 reward updates; feedback and frozen both survived 48/48 ticks; need-balance delta 0.0 | Keep lab-only feedback loop |
| Repeated stochastic CA/NCA stress | 8 samples; 5 cycles each; 40 damage events; final validity 1.0; mean final overlap 1.0 | Prototype repeated stress benchmark |
| Package promotion gate | 7 criteria; 6 candidates; 3 package-design-ready; 0 promotion-ready | Define gate only; do not promote lab code |
| MVP architecture | 9 target modules; engine-first loop accepted | Adopt for MVP design |

## Decisions

### Adopt

- MVP architecture decision for engine-first package design.
- Package promotion criteria as the gate before moving lab code.
- Lifecycle, archive, and provenance as the first package-design candidates.

### Prototype

- Manual readability intake workflow, pending real reviewer data.
- Lifecycle reward updates inside the lab switchboard.
- Repeated stochastic damage as part of the CA/NCA benchmark contract.

### Watch

- Online reward shaping. It updates preferences safely in the Stage 0 scenario,
  but does not yet beat the frozen baseline.
- CA/NCA-style repair. The repeated stress result is strong, but still uses an
  assisted target-template repair rule.

### Blocked

- Human readability calibration, because no reviewer ratings are present.
- Actual package promotion, because `packages/mecha_engine` does not exist.

## Package Design Handoff

The package-promotion gate identifies three package-design-ready candidates:

- `lifecycle_simulator` -> `packages/mecha_engine/lifecycle`
- `map_elites_archive` -> `packages/mecha_engine/archive`
- `provenance_ci` -> `packages/mecha_engine/provenance`

The MVP architecture decision adds the surrounding target modules:

```txt
packages/mecha_engine/
  genome/
  generation/
  lifecycle/
  learning/
  archive/
  slip/
  render/
  storage/
  provenance/
```

This is a design handoff only. No lab code should move into `packages/` until
the package root exists intentionally and the promotion gate is satisfied.

## Risks

- Readability remains proxy-only until human ratings are collected.
- Reward feedback is not yet a production learner because it tied the frozen
  baseline on survival and need balance.
- CA/NCA repair should not be described as learned morphogenesis.
- The package boundary is defined in research, but not implemented in source.
- Full workshop/editor work remains outside the MVP core.

## Next Research Sequence

1. Create package module interface specs for `genome`, `generation`,
   `lifecycle`, `archive`, and `provenance`.
2. Collect or import real human readability ratings using the Stage 0 template.
3. Stress switchboard feedback under changing needs and user-interaction
   patterns to determine whether it can beat the frozen baseline.
4. Compare a trained or learned repair rule against the assisted CA/NCA repair
   baseline.
5. Produce a package-scaffold decision record before creating
   `packages/mecha_engine`.

## Publication Status

This is an internal research publication. It completes the v0.2 follow-up
sequence and defines the evidence-backed handoff from research into MVP package
design.

