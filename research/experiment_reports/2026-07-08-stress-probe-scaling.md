# Experiment Report: Stress-Probe Scaling — the /16 Denominator Re-derived from Evidence (Cycle 09 · ENGINE · A3)

Date: 2026-07-08

## WHY

The archive's morphology stress probe
(`load = clamp(body_mass/16 + (1−symmetry)·0.65 − sensors·0.08)`) is what
spreads candidates across the survival descriptor axis. DR 0014 flagged
the `/16` as 8×8-coupled and required its replacement be "re-derived
from evidence, never scaled by fiat", naming the `mass/(w·h/4)` family
as the candidate. The A3 first slice deliberately deferred the change to
a measurement — and predicted the named family would fail on saturation.
Both the deferral and the prediction needed testing.

## WHAT

`labs/map_elites_archive/stress_probe_scaling.py` measures the EXACT
engine statistic (the engine's own `body_mass`/`symmetry_score`/
`sensor_count`/`clamp`, real `run_episode` survival at the archive's own
24-tick default, fixed seed) over both proven corpora under three
denominator laws that all reproduce the shipped `/16` at 8×8:

| Law | D at 8×8 | D at 16×16 |
| --- | ---: | ---: |
| `status_quo_16` (shipped) | 16 | 16 |
| `area_over_4` (DR 0014's family) | 16 | 64 |
| `four_x_floor` (4 × DR 0029 floor law) | 16 | 72 |

Gates, from the probe's own documented purpose: 8×8 identity, survival
axis alive at 16×16 (≥2 of the archive's 5 bins), no bin regression
against the measured 8×8 baseline, saturation not total. Adoption picks
the surviving law with the most bins, then the closest 16×16 load median
to the measured 8×8 baseline (distribution preservation) — the rule was
fixed in code before the measurement ran.

## FINDINGS

| Measure (50-creature corpora) | 8×8 baseline (D=16) | 16×16 D=16 | 16×16 D=64 | 16×16 D=72 |
| --- | --- | --- | --- | --- |
| Load p50 | 0.815 | **1.0** | 0.694 | 0.604 |
| Saturated fraction | 0.0 | **0.98** | 0.18 | 0.04 |
| Survival ratio p50 | 1.0 | **0.5 (all)** | 1.0 | 1.0 |
| Full-survival fraction | 0.92 | **0.0** | 0.72 | 0.88 |
| Survival bins covered | {2, 4} = 2 | **{2} = 1** | {2, 4} = 2 | {2, 4} = 2 |

- **The shipped `/16` collapses totally at 16×16**: 98% saturation,
  every creature dead at exactly tick 12, ONE survival bin — precisely
  the failure the probe exists to prevent, now measured rather than
  assumed. DR 0014's warning was exact.
- **The first-slice prediction is REFUTED**: `mass/64` does saturate
  the nine heaviest creatures (core ≥ 64: fennec, ray, bunny, horned
  beetle…), but the axis stays alive and every gate passes. Heavy
  bodies reading as high-stress is coherent selection pressure, not a
  defect.
- Both surviving laws cover the same bins as the 8×8 baseline ({2, 4} —
  the lifecycle's documented bistability leaves intermediate bins rare
  at 24 ticks, at both scales). The tie broke on load-median proximity:
  |0.694 − 0.815| < |0.604 − 0.815|, so **`area_over_4` is adopted** —
  which is also the family DR 0014 documented. `four_x_floor` is the
  recorded runner-up (less saturation, closer full-survival fraction);
  if a future difficulty pass judges the 18% saturation too harsh, it
  is the named alternative, not a new search.

## VERDICT — adopted across the engine and every mirror

`lifecycle_probe_grid` now computes `body_mass / max(1, w·h//4)` with
the historical constant as the malformed-size fallback; the same change
landed in the four verbatim mirrors (the runtime lab's `_stress_probe`,
the archive contract oracle, the extended-descriptors lab, the workshop
morphology panel). 8×8 is byte-identical by the identity gate — every
pre-existing pin passed unmodified.

## Verification

RED (the adoption pin before the engine change — the engine still
shipped `/16` at 16×16):

```powershell
PS> python -B -m unittest test_stress_probe_scaling
AssertionError: 1.0 != 0.68375 within 9 places : mg_seed16_001_beetle
FAILED (failures=1)
```

GREEN (after adoption; every consumer suite):

```powershell
PS> python -B -m unittest discover -s labs/map_elites_archive -p "test_*.py"
Ran 31 tests in 4.209s
OK
PS> python -B -m unittest discover -s packages/mecha_engine/tests -p "test_*.py"
Ran 291 tests in 5.173s
OK
PS> python -B -m unittest discover -s labs/runtime_integration -p "test_*.py"
Ran 65 tests in 60.853s
OK
PS> python -B -m unittest discover -s labs/game_loop -p "test_*.py"
Ran 81 tests in 4.478s
OK
PS> python -B -m unittest discover -s workshop/tests -p "test_*.py"
Ran 58 tests in 87.019s
OK
```

Lab (artifact production):

```powershell
PS> python -B labs/map_elites_archive/stress_probe_scaling.py
"adopted": {"law": "area_over_4", "denominator_16x16": 64, "denominator_8x8": 16}
```

## Sources

- `labs/map_elites_archive/stress_probe_scaling.py` (+ `test_stress_probe_scaling.py`)
- `data/archives/stress_probe_scaling_stage0.json`
- `research/algorithm_cards/stress_probe_scaling.md`
- `packages/mecha_engine/src/mecha_engine/archive/_metrics.py`
- `labs/runtime_integration/mecha_engine_runtime_loop.py`, `labs/map_elites_archive/extended_descriptors.py`, `packages/mecha_engine/tests/helpers/archive_contract_driver.py`, `workshop/server/workshop_server.py`
- `research/decision_records/0014-grid-size-commitment.md` (the requirement), `0029-16x16-default-grid-scale.md` (decision 7)
- `research/experiment_reports/2026-07-08-16x16-validator-generation.md` (the corrected prediction)
- `data/seed_grids/`, `data/seed_grids_16x16/`
