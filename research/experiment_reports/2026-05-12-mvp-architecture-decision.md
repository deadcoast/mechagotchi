# Experiment Report: MVP Architecture Decision

Date: 2026-05-12

## Objective

Produce the MVP architecture decision record required by the v0.2 next research
sequence, using the v0.1 report, v0.2 report, package-promotion gate, and the
original brainstorming and research-plan documents.

## Inputs

- `docs/01-brainstorming.md`
- `docs/02-research_plan.md`
- `research/reports/mechagotchi_research_report_v0_1.md`
- `research/reports/mechagotchi_research_report_v0_2.md`
- `research/decision_records/0002-mecha-engine-package-promotion-gate.md`
- `data/package_promotion/mecha_engine_package_promotion_gate_stage0.json`

## MVP Architecture

The MVP should be an engine-first companion loop:

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

The MVP should prove the core thesis before building a full workshop product:

- Generate one valid companion from a semantic grid genome.
- Display or emit a renderable grid packet.
- Simulate hunger, energy, mood, age, and survival.
- Support feed, play, and sleep interactions.
- Log events, lineage, mutations, and survival outcomes.
- Load one minimal SLIP profile.
- Produce a child or next-generation genome through constrained mutation.

## Package-Design Target

The package root does not exist yet, so this is a target architecture rather
than a package creation step:

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

The first design candidates are:

- `genome`: semantic grid schema, invariants, validator, seed/counterexample
  fixtures.
- `generation`: constrained local-pattern generation with validator repair;
  raw Markov remains a proposal source, not the whole generator.
- `lifecycle`: need balance, survival, interaction effects, and death/reset
  causes.
- `learning`: micro-switchboard policy evaluation; online reward shaping stays
  research-only until it beats the frozen baseline.
- `archive`: MAP-Elites-style repertoire, descriptors, fitness scoring, and
  lineage hooks.
- `slip`: minimal profile schema, constraint interpreter, and compatibility
  gate.
- `render`: frontend-neutral render packets.
- `storage`: save files, event logs, lineage records, and metric traces.
- `provenance`: asset and source ledger checks.

## Decisions

Adopt for the MVP:

- Semantic grid genome and validator as the core data contract.
- Constraint-stabilized generation as the default generator path.
- Readability and lifecycle as first-class gates.
- MAP-Elites archive concepts for species diversity.
- Provenance ledger checks for included assets and research artifacts.
- Render packets as the visual-engine boundary.

Prototype inside the MVP:

- Minimal SLIP interpreter.
- Feed/play/sleep lifecycle interaction loop.
- Micro-switchboard action selection.
- Lineage mutation and next-generation creation.
- Archive insertion and descriptor reporting.

Defer beyond the MVP:

- Full `mecha_workshop` editor and community profile packs.
- Trained NCA morphogenesis.
- CTM-like model dependencies.
- Real CuBFF adoption.
- Online reward shaping as production behavior.
- External editor embedding.

Reject for MVP core:

- Direct CuBFF tape-to-pixel mapping.
- Raw Markov generation as the sole creature generator.
- Scalar top-k as the only evolutionary selection strategy.
- Moving lab code into `packages/` before the promotion gate is satisfied.

## Decision Record

The formal decision is recorded in
`research/decision_records/0003-mvp-architecture.md`.

Status: `accepted_for_mvp_design`.

