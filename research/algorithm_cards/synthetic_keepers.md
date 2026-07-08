# Algorithm Card: Synthetic Keepers + Scale Benchmark

## Purpose

The dossier's five synthetic user models (attentive, neglectful,
erratic, punitive, exploratory) as deterministic interaction policies,
plus the 100k-tick × 500-lifecycle two-arm welfare benchmark — the
instrument D6's documented ablation gates run on (gap-analysis
Phase D, D5).

## Mathematical Basis

- Keeper = a per-tick policy `(state, rng) → feed | play | None`
  layered over the switchboard's autonomous behavior; deterministic
  under seeds; both arms replay paired seeds per lifecycle.
- Welfare = the engine's own per-tick need `balance`, mean over the
  episode — no new statistics invented.
- Scale = 5 keepers × 100 lifecycles × 200 ticks per arm (the
  documented 100k ticks), frozen switchboard vs fully opted-in fleet.
- Wall-clock protocol (DR 0028): pilot measured FIRST, projection
  against a 600 s bound, dependency decision recorded from the number.

## Inputs

- The 50-seed corpus (cycled), the LCD evidence bundles (D4), the
  full fleet opt-in (D1–D4 threads), per-lifecycle seeds

## Outputs

- Per-keeper, per-arm welfare/survival/interaction aggregates;
  `data/micro_threads/synthetic_keepers_stage0.json`

## Strengths

- Stdlib holds with a 33× margin (measured 17.9 s vs the 600 s bound);
  the NumPy trigger is honestly NOT met
- Paired seeds make the two-arm comparison clean
- The five documented models produce measurably distinct keeper
  behavior (attentive interacts most and fares best; neglectful least)

## Weaknesses

- **The sheltered environment is welfare-saturated** (balance spread
  0.0095 across all keeper×arm cells, survival 100% everywhere): the
  switchboard feeds its own companion, so thread effects have no
  headroom to show welfare value — the measured deltas are ~0%
- Keeper models are lab operationalizations of the documented names;
  real player telemetry is a GAME-track concern

## Failure Modes

- Running D6's ≥15% gate in the saturated mode guarantees failure —
  the named remedy is a keeper-dependent mode (feeding as a USER
  action, the game's actual interaction model) with real headroom

## Integration Risk

None to the engine: the harness owns its loop (history trimming is
bench-side); the engine is untouched.

## License Status

Original stdlib-only code, Apache-2.0.

## Prototype Result

76 lab tests green; full-scale artifact recorded: stdlib holds,
welfare deltas −0.11%…−0.002% with the saturation evidence attached.

## Decision

**Adopt the harness; carry the honest zero to D6.** Go gate for D6:
the documented ablation gates run with real welfare headroom
(keeper-dependent feeding) or the failure recorded as measured.

## Sources

- `labs/micro_threads/synthetic_keepers.py` (+ `test_synthetic_keepers.py`)
- `data/micro_threads/synthetic_keepers_stage0.json`
- `research/experiment_reports/2026-07-08-synthetic-keepers.md`
- `docs/project-research/deep-research/01/deep-research.md`
- `audits/TODO.md` (cycle 12 D5), `docs/gap-analysis.md` (Phase D)
