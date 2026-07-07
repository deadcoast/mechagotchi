# Experiment Report: CuBFF Live Lineage Pressure (R2)

Date: 2026-07-06. Plan: decision record 0018.

## Objective

Wire the CuBFF transducer's Pipeline C (lineage dynamics → mutation
weights) into the ACTUAL evolution loop so Google-CuBFF computational-
life dynamics shape every generation — the identity claim (DR 0017
a.1/a.3) demonstrated in the running engine, not just a lab.

## Design (per DR 0018)

Per generation, one CuBFF snapshot's `extract_cubff_features ->
mutation_pressure` ∈ [0,1] scales that generation's damage severity by
`1 + 1.1·(pressure − 0.5)`, clamped to [0.5, 1.6]. The archive still
selects, SLIP still constrains, the validator still gates — CuBFF
PRESSURES, never dictates. Only pressure scalars cross the boundary
(the semantic-compiler rule: never tape → tokens).

## Verification

RED → GREEN: `test_cubff_pressure.py` (premise: chaotic snapshots carry
higher mutation pressure; per-generation multiplier recorded and banded;
directional damage effect; tokens-never-cross assertion; determinism;
absent-source byte-identical). Full runtime-integration suite green.

## Measurement — CuBFF dynamics visibly move the ecosystem

Same rng seed, 4 generations × 6 creatures × 2 cycles; only the CuBFF
source differs:

```txt
                     dropout multiplier   total cells destroyed
chaotic soup            1.170             111
stable soup             0.900              88
```

A turbulent computational-life substrate produces a measurably more
turbulent generation (+26% damage); a calmly replicating one produces
a gentler generation — from real CuBFF feature extraction, deterministic
and provenance-stamped per generation (each carries its source
snapshot_id). This is the a.4 "living ecosystem the player notices"
claim, demonstrated at the engine level: the substrate is now the
engine's bloodstream.

## Decision

Pipeline C is live in the loop. Absent source stays byte-identical (all
evolution parity pins, the stress regime, the workshop wire, and the
package `evolve` contract untouched). Per DR 0018 the promotion of
`cubff_pressure_source` into `runtime.evolve` is the next plan's
checkpoint, alongside real ingested snapshots and lineage-continuity
study across pressure regimes.

## Sources

- `research/decision_records/0018-cubff-live-lineage-pressure.md`
- `labs/cubff_transducer/cubff_transducer.py` (extract_cubff_features, features_to_traits)
- `labs/runtime_integration/mecha_engine_runtime_loop.py`, `labs/runtime_integration/test_cubff_pressure.py`
- `data/runtime_integration/mecha_engine_evolution_cubff_pressure_stage0.json`
