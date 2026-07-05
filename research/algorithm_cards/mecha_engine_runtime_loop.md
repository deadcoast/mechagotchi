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

Implemented 2026-07-05. 12 creatures, 72-tick episodes, dropout 0.2:
candidate validity 12/12, repaired validity 12/12, alignment retention
11/12 (0.9167 — the measured gap), position restoration 1.0, token
restoration 0.9729, survival 1.0 pre and post, archive 9 niches
(QD 8.35), provenance ledger + CI green, fully deterministic.

## Decision

Prototype (adopt as the standing integration harness). Status
`runtime_loop_gaps_measured` until the SLIP-aware repair guard turns
alignment retention green; only then propose a runtime package target
(decision record required).

## Go-No-Go Gate

Go for the SLIP-aware repair guard batch; no-go for any `runtime` package
target until `slip_alignment_retention_rate == 1.0` at full size.
