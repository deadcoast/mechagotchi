# Algorithm Card: Stress-Probe Scaling

## Purpose

Re-derive the archive stress probe's 8×8-coupled mass denominator
(`body_mass/16`) at the ratified 16×16 scale from evidence, as DR 0014
required — measuring the engine's exact statistic instead of scaling the
constant by fiat.

## Mathematical Basis

- The probe maps morphology to a lifecycle starting stress:
  `load = clamp(mass/D + (1−symmetry)·0.65 − sensors·0.08)`. Its purpose
  is survival-axis spread; its failure mode is bin collapse.
- Candidate laws are size-parametric forms that all reproduce D=16 at
  8×8 (identity gate), so the 8×8 evidence base is untouchable by
  construction: the shipped constant, `w·h/4` (DR 0014's family), and
  `4 × body_core_min_cells(w,h)` (tied to the DR 0029 floor law).
- Survival is measured by the real `run_episode` (switchboard policy,
  the archive's 24-tick default, fixed seed) and binned by the archive's
  own `lifecycle_survival` edges — the exact consumer statistic.
- The adoption rule (fixed before the run): most bins, then closest
  16×16 load median to the measured 8×8 baseline, then least saturation.

## Inputs

- The two proven corpora (50 seeds at each ratified scale)
- The engine's own metric functions and lifecycle episode runner

## Outputs

- `data/archives/stress_probe_scaling_stage0.json` — baseline, per-law
  measurements, gates, and the adopted law

## Strengths

- Measures the consumer's actual statistic end to end (probe → episode
  → bin), not a proxy
- The identity gate makes 8×8 regression impossible for any candidate
- Pre-registered adoption rule; the losing prediction is recorded as a
  refuted hypothesis, not hidden

## Weaknesses

- 24-tick episodes leave intermediate survival bins rare at both scales
  (the lifecycle's documented bistability), so "bins covered" saturates
  at 2 — the discrimination is coarse
- The adopted law saturates the nine heaviest 16×16 creatures (18%);
  recorded as selection pressure, with `four_x_floor` the named
  alternative if a difficulty pass judges it too harsh

## Failure Modes

- If A2's corpus composition shifts (heavier/lighter median), the
  distribution-preservation tie-break should be re-run — one lab run

## Integration Risk

Low-medium — the adoption touched the engine metric and four verbatim
mirrors in one change; every consumer suite passed unmodified because
8×8 is byte-identical.

## License Status

Original stdlib-only code (engine imports are first-party), Apache-2.0.

## Prototype Result

Shipped `/16` at 16×16: total collapse (98% saturation, one bin, every
creature dead at tick 12). `area_over_4` (D=64): all gates pass, bins
match the 8×8 baseline, adopted. `four_x_floor` (D=72): all gates pass,
runner-up on load-median proximity.

## Decision

**Adopt** `area_over_4` (engine + all mirrors, 2026-07-08). Go gate:
every consumer suite green with 8×8 pins unmodified — met.

## Sources

- `labs/map_elites_archive/stress_probe_scaling.py` (+ tests)
- `data/archives/stress_probe_scaling_stage0.json`
- `research/experiment_reports/2026-07-08-stress-probe-scaling.md`
- `research/decision_records/0014-grid-size-commitment.md`, `0029-16x16-default-grid-scale.md`
