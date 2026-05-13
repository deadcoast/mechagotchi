# Mechagotchi Research Report v0.2

Date: 2026-05-12

## Executive Summary

The post-v0.1 research sequence strengthens the original architecture: the
project should remain a semantic grid-genome companion engine built from small,
measurable systems.

The new evidence adds lifecycle survival, held-out readability, richer
quality-diversity descriptors, workshop round-trip fidelity, real CuBFF ingest
gating, provenance CI, CA/NCA-style repair, and CTM-inspired internal ticks.

The most important decision change is that lifecycle and readability are now
first-class gates. A generator is not promising merely because it emits valid
grids; it must also preserve readable form, survive the simulator, and remain
explainable through lineage, provenance, and decision traces.

## Research Scope

This report consolidates the post-v0.1 continuation recorded in
`research/experiment_reports/`:

1. Lifecycle simulator baseline.
2. Held-out readability benchmark and manual rating protocol.
3. Extended MAP-Elites descriptors.
4. Workshop import/export round trip.
5. Real CuBFF snapshot ingest gate.
6. Provenance CI and SPDX expression parser.
7. CA/NCA growth, repair, persistence, and deterministic damage stress.
8. CTM-inspired confidence-gated internal ticks.

## Primary Artifacts

| Area | Artifact |
| --- | --- |
| Lifecycle | `data/lifecycle/lifecycle_stage0.json` |
| Readability | `data/readability/readability_stage0.json` |
| Extended archive | `data/archives/map_elites_extended_stage0.json` |
| Workshop round trip | `data/workshop_editor/workshop_roundtrip_stage0_report.json` |
| Real CuBFF ingest | `data/cubff_real_ingest/real_snapshot_ingest_stage0_report.json` |
| Provenance CI | `data/asset_provenance/provenance_ci_report.json` |
| CA/NCA repair | `data/cellular_automata/ca_nca_growth_repair_stage0.json` |
| CA/NCA stress | `data/cellular_automata/ca_nca_persistence_damage_stage0.json` |
| CTM-inspired ticks | `data/ctm_ticks/ctm_inspired_ticks_stage0.json` |

## Experiment Results

| Experiment | Result | Decision |
| --- | ---: | --- |
| Lifecycle simulator | Switchboard survived 72/72 ticks; idle died at 11; random died at 21 | Prototype switchboard policy |
| Readability benchmark | Seed mean 0.867316; constrained mean 0.830172; Markov mean 0.374730 | Keep readability gate |
| Extended MAP-Elites | 7 descriptor dimensions; 29 occupied niches; best fitness 0.979592; QD score 27.773545 | Prototype richer descriptors |
| Workshop round trip | Round-trip success 1; semantic fidelity 1.0; preview accuracy 1.0 | Prototype semantic workshop IO |
| Real CuBFF ingest | 0 real snapshots available; upstream audit found no committed soup/checkpoints | Block CuBFF adoption |
| Provenance CI | Ledger ok; SPDX expressions 7/7 parsed; hashes and decision gate ok | Adopt for research artifacts |
| CA/NCA growth/repair | Growth validity 1.0; repair validity 1.0; repair lifecycle survival 1.0 | Prototype lab-only attractor |
| CA/NCA damage stress | 24 cases; repair validity 1.0; persistence validity 1.0; hardest mask center_cut | Prototype persistence benchmark |
| CTM-inspired ticks | Accuracy held at 1.0; mean confidence improved from 0.805435 to 0.824067 | Prototype concept-only ticks |

## Decisions

### Adopt

- Lifecycle and readability as gates for future generator comparisons.
- Provenance CI and SPDX expression parsing for research artifacts.

### Prototype

- Switchboard policy evaluation through lifecycle simulation.
- Extended MAP-Elites descriptors using readability, survival, mutation
  stability, and behavior neediness.
- Semantic workshop import/export round trips.
- CA/NCA-inspired growth, repair, and persistence as a lab-only benchmark.
- CTM-inspired confidence-gated internal ticks as a small switchboard wrapper.

### Watch

- Trained NCA or CTM model dependencies. Current evidence supports concepts and
  benchmarks, not heavyweight model adoption.
- Human readability ratings. The protocol exists, but ratings are not collected
  yet.

### Blocked

- CuBFF adoption. The real-ingest gate found no committed upstream
  soup/checkpoint artifacts and no local real snapshots.

## Interpretation

The platform now has enough research infrastructure to compare algorithms
across more than validity:

```txt
validity
  -> readability
  -> lifecycle survival
  -> SLIP alignment
  -> archive diversity
  -> lineage continuity
  -> provenance clarity
  -> workshop round-trip fidelity
```

The best current engine path remains modular:

```txt
SLIP profile
  -> constrained generator
  -> validator/readability/lifecycle gates
  -> switchboard policy
  -> MAP-Elites archive
  -> lineage and workshop IO
  -> optional lab-only influences from CUBFF, CA/NCA, or CTM concepts
```

The research does not support adopting large external ML systems into the core
engine yet. It supports small, inspectable mechanisms with measurable reports.

## Risks

- Readability still depends on proxy scoring until human ratings are collected.
- The CA/NCA repair rule is target-template assisted and should not be
  overclaimed as learned morphogenesis.
- CTM-inspired ticks improved confidence on synthetic scenarios only.
- CuBFF remains blocked by unavailable real snapshot artifacts.
- Extended archive coverage is sparse because the descriptor space is large.

## Next Research Sequence

1. Collect manual readability ratings using the existing protocol.
2. Connect lifecycle rewards back into switchboard action-reward updates.
3. Add repeated or stochastic damage to the CA/NCA benchmark.
4. Define package promotion criteria for `packages/mecha_engine`.
5. Produce an MVP architecture decision record from the v0.1 and v0.2 reports.

## Publication Status

This is an internal research publication. It consolidates post-v0.1 evidence and
does not promote any lab code into production packages by itself.
