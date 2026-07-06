# Algorithm Card: Mecha Engine Runtime Loop

## Purpose

Compose all six promoted `mecha_engine` modules (genome, generation,
lifecycle, archive, provenance, repair) into one deterministic
creature-lifetime loop, measuring whether the module contracts hold under
composition and producing the evidence a future `runtime` package surface
would need.

## Mathematical Basis

No new algorithm: the loop is a pipeline over already-proven components
(constrained generation, bounded lifecycle simulation, wound-site softmax
repair, MAP-Elites insertion). Its own contributions are integration
metrics — SLIP-alignment retention, position/token restoration fidelity
against the runtime's held pre-damage truth, pre/post-repair survival
ratios — and a strict all-stages-green decision derivation.

## Inputs

- The 50-grid seed corpus (profile-aligned subset as the parent pool)
- A SLIP profile (`data/slips/valid/slip_lcd_seed.json`)
- Seeded stochastic damage events reporting `removed_cells`
- The real provenance ledger (`data/asset_provenance/ledger.json`)

## Outputs

- Per-run stage flags, episode digests, damage events, restoration
  fidelity, archive decisions
- Loop summary (validity rates, alignment retention, survival ratios,
  archive coverage/QD) and an evidence-derived decision
- `data/runtime_integration/mecha_engine_runtime_loop_stage0.json`

## Strengths

- First full-loop evidence that the promoted engine composes
- Surfaces cross-module seams no per-module contract test can see
- Deterministic and cheap (~40 s full size)

## Weaknesses

- Single-generation, single-damage-cycle; no evolution over archive
  elites yet
- Damage source is the lab reference synthesizer, not lifecycle-coupled
- Readability in scoring is the uncalibrated proxy (deferred)

## Failure Modes

- Treating the composed-loop flag as per-module proof (it is not; the
  module contract tests remain the per-module truth)
- Letting the alignment gap hide inside means — hence the dedicated
  retention rate and per-run stage flags

## Integration Risk

Low as a lab. The measured seam (repair guard is validator-aware but not
SLIP-aware) is the known risk for any future runtime surface.

## License Status

Internal Mechagotchi research code; composes only in-repo modules.

## Prototype Result

Implemented 2026-07-05. First run (12 creatures, 72-tick episodes,
dropout 0.2): candidate validity 12/12, repaired validity 12/12,
alignment retention 11/12 (0.9167 — the measured gap), position
restoration 1.0, token restoration 0.9729, survival 1.0 pre and post,
archive 9 niches (QD 8.35), provenance green, fully deterministic.

Second run (same day, after the SLIP-aware repair guard): alignment
retention 1.0, all 12 runs archived, exactly 1 guard substitution
(the previously failing creature), token restoration 0.9654 (the
documented constraint-not-template consequence), archive 10 niches
(QD 9.29), decision `runtime_loop_composed`.

Evolution mode (same day): 4 generations × 8 creatures × 3 damage
cycles — 32/32 creatures complete everything (96 damage events,
retention 1.0, 12 guard substitutions), archive elites reproduce,
archive grows to 15 niches (QD 13.92), fitness flat at ~0.92-0.93
(honest: survival saturated, readability uncalibrated). Decision
`evolution_loop_composed`. Lineage-counter reset through repair
recorded as parity-reviewed future work.

Stress regime (same day): episodes on the archive's contracted
morphology stress probe (regime-conditional; sheltered default
byte-identical). 6 generations x 8 x 3 cycles: saturation broken
(10/48 deaths, survival 0.79-0.90 by generation), archive 25 niches
(QD 21.27), mean structural load falls 0.855 -> 0.761 (a selection
signal, stated conservatively — not monotonic, short horizon), mean
survival flat (bistability + MAP-Elites uniform-niche parenting,
recorded as a system property). Decision
`evolution_under_stress_composed`.

## Decision

Prototype (adopt as the standing integration harness). Status is now
`runtime_loop_composed` (the SLIP-aware guard closed the seam). A
`runtime` package target proposal is evidence-ready; creating it stays
decision-record-gated (owner go required). Next: multi-generation
evolution over archive elites.

## Go-No-Go Gate

The SLIP-aware guard batch shipped and `slip_alignment_retention_rate ==
1.0` at full size — the evidence gate is satisfied. Go for a `runtime`
package target proposal only with an owner-approved decision record.

## Workshop Wire Result (2026-07-05, audit T1)

`workshop_grids_dir` admits released workshop creatures as
generation-0 founders through the engine's own gates; lineages are
traced via `ancestor_ids` (founder ids survive per-cycle renames).
First run (2 founders, stress regime, 6 generations): both lineages
went extinct at founding (fitness 0.762 vs corpus 0.868, zero
archive entries) — user assets compete, they are not granted
survival. The wire also exposed a latent gate gap (episodes gated on
alignment only) now hardened to `valid and aligned` with the
`skipped_invalid` outcome; pinned artifacts unchanged.
