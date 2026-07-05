# Experiment Report: Evolution Under the Stress Survival Regime

Date: 2026-07-05

## Objective

Break the survival saturation that made evolution's fitness curve flat and
would have made any learning-module claim unfalsifiable: with the fixed
switchboard baseline surviving every episode, neither selection nor a
learner can demonstrate improvement. Give the composed engine a hard
survival regime — the archive's own contracted morphology stress probe —
so survival depends on the creature's body, and measure whether selection
shows a signal. This is the deliberate prerequisite ordering: environment
first, then the learning module (decision record 0009 candidate) has
something real to learn against.

## Design

- New `survival_regime` parameter on the lab evolution loop. The
  `sheltered` default is byte-identical to the previous behavior (the
  package parity pins depend on it; every stress key is
  regime-conditional). `stress_probe` runs every episode — per-cycle and
  final scoring — on the archive's contracted probe
  (`load = clamp(body_mass/16 + (1 − symmetry)·0.65 − sensors·0.08)`,
  mirrored verbatim from `mecha_engine.archive._metrics
  .lifecycle_probe_grid`, cited in-code).
- Deaths are legitimate measured outcomes, never contract failures: the
  composure gates stay validity/alignment/restoration/archival; the
  decision gains measured observations (load and survival deltas, deaths).
- Pre-experiment probe (evidence before build): 16 generated candidates
  under the probe showed 12 distinct loads (0.61–0.95) and one
  `stress_collapse` death at tick 14 — variance confirmed before the
  experiment was written.

## Verification

RED (regime parameter did not exist):

```powershell
python -B -m unittest test_mecha_engine_runtime_loop.StressRegimeEvolutionTests
# TypeError: unexpected keyword argument 'survival_regime' -> FAILED
```

GREEN (full runtime-lab suite, 20 tests):

```txt
Ran 20 tests in 39.454s
OK
```

Lab command (6 generations × 8 creatures × 3 damage cycles, 72-tick
episodes):

```powershell
python -B .\labs\runtime_integration\mecha_engine_runtime_loop.py --mode evolution --regime stress_probe --generations 6
```

```txt
"creature_count": 48, "total_damage_events": 144,
"candidate_valid_rate": 1.0, "slip_alignment_retention_rate": 1.0,
"mean_stress_load_by_generation":    [0.8547, 0.8697, 0.8789, 0.8415, 0.8077, 0.7609],
"mean_survival_ratio_by_generation": [0.8958, 0.7951, 0.7951, 0.7917, 0.8993, 0.7986],
"death_count": 10, "archive": {"filled_niches": 25, "qd_score": 21.265377}
"decision": "evolution_under_stress_composed",
"observations": {"mean_load_last_vs_first": -0.093813,
                 "mean_survival_last_vs_first": -0.097222,
                 "deaths_observed": true}
```

## Findings

1. **Saturation is broken.** 10 of 48 final episodes end in death;
   per-generation survival ranges 0.79–0.90; fitness varies
   (0.83–0.89 vs the sheltered regime's flat 0.92–0.93). The archive
   grows 15 → 25 niches (QD 13.92 → 21.27): the survival axis finally
   spreads bins, exactly what the probe's own design note promised.
   **The falsifiability prerequisite for the learning module now
   exists** — a learned policy can measurably beat or fail to beat the
   frozen switchboard in this regime.
2. **A selection signal, stated conservatively.** Mean structural load
   falls 0.855 → 0.761 (−0.094) across generations: offspring of archive
   elites trend toward lighter, more symmetric, better-sensored
   morphologies. The trend is not monotonic (it rises through generation
   2 before falling) and six generations is short — this is "a
   load-decreasing trend observed," not "adaptation proven." Longer
   horizons are the follow-up.
3. **Mean survival does not climb, and the reason is structural, not a
   bug.** Survival is bistable near the collapse threshold (most of the
   population sits safely below it either way), and MAP-Elites draws
   parents uniformly across ALL niches — including low-survival bins —
   because diversity preservation is its purpose. A survival-maximizing
   breeder would select differently; the archive deliberately does not.
   Recorded as a property of the system, with the observation flags
   carrying the honest numbers (−0.097 survival delta).
4. All module contracts hold under stress: validity, alignment retention,
   and position restoration all 1.0 across 144 damage events; the
   SLIP-aware guard fired 19 times.

## Decision

Status: `evolution_under_stress_composed`. The engine now has a survival
regime where morphology matters and outcomes vary — the evaluation
environment the learning module needs. Next steps, value order:
(a) propose the learning module (decision record 0009) with THIS regime
as its contracted evaluation environment — the claim to beat is the
frozen switchboard's measured survival under stress; (b) longer-horizon
selection studies (more generations, fitness-weighted vs uniform parent
sampling as an explicit comparison); (c) package `runtime.evolve` gains
the regime parameter only after the lab evidence settles (promoted-module
change, parity implications documented).

## Sources

- `labs/runtime_integration/mecha_engine_runtime_loop.py`
- `labs/runtime_integration/test_mecha_engine_runtime_loop.py`
- `data/runtime_integration/mecha_engine_evolution_hard_regime_stage0.json`
- `data/runtime_integration/mecha_engine_evolution_loop_stage0.json` (sheltered baseline)
- `packages/mecha_engine/src/mecha_engine/archive/_metrics.py` (the contracted probe)
- `research/experiment_reports/2026-07-05-mecha-engine-evolution-loop.md`
- `research/algorithm_cards/mecha_engine_runtime_loop.md`
