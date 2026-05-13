# Decision Record 0003: MVP Architecture

Date: 2026-05-12

## Status

Accepted for MVP design.

## Context

The v0.1 and v0.2 reports support the same architectural direction:
Mechagotchi should be a semantic grid-genome companion engine composed of small,
measurable systems. The original brainstorming document defines the first MVP as
one generated companion that can be displayed, simulated, interacted with,
mutated, saved, and linked to a SLIP profile.

The package-promotion gate also found that `packages/mecha_engine` does not
exist yet. This decision therefore defines the MVP architecture and package
boundaries, but does not create package code or move lab code into production
paths.

## Decision

The MVP architecture is engine-first:

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

The target package design is:

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

The MVP must prove:

1. One companion can be generated from a semantic grid genome.
2. The companion can be rendered through a frontend-neutral packet.
3. Hunger, energy, mood, age, and survival can be simulated.
4. Feed, play, and sleep interactions affect lifecycle state.
5. Survival, mutation, lineage, and archive events are logged.
6. One minimal SLIP profile can constrain generation and mutation.
7. A next-generation genome can be produced without violating validation,
   readability, lifecycle, or provenance gates.

## Adopted Components

- Semantic grid genome and validator.
- Constraint-stabilized generator path.
- Readability and lifecycle gates.
- MAP-Elites-style archive and lineage concepts.
- Minimal SLIP interpreter.
- Micro-switchboard policy evaluation.
- Render packets as the visual boundary.
- Provenance ledger checks.

## Deferred Components

- Full `mecha_workshop` editor.
- Community profile packs.
- Trained NCA morphogenesis.
- CTM-like model dependencies.
- Real CuBFF adoption.
- Online reward shaping as production behavior.
- External editor embedding.

## Rejected For MVP Core

- Direct CuBFF tape-to-pixel mapping.
- Raw Markov generation as the sole creature generator.
- Scalar top-k as the only evolutionary selection strategy.
- Lab-code promotion before the package gate is satisfied.

## Consequences

- MVP implementation should start with engine contracts, not workshop polish.
- `packages/mecha_engine` should be created only when the promotion gate is
  intentionally satisfied.
- The first package design should prioritize `genome`, `generation`,
  `lifecycle`, `archive`, and `provenance` before broader learning features.
- Research-only systems remain available as labs until they clear their gates.

## Evidence

- `docs/01-brainstorming.md`
- `docs/02-research_plan.md`
- `research/reports/mechagotchi_research_report_v0_1.md`
- `research/reports/mechagotchi_research_report_v0_2.md`
- `research/decision_records/0002-mecha-engine-package-promotion-gate.md`
- `research/experiment_reports/2026-05-12-mvp-architecture-decision.md`

