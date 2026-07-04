# Descriptor Axis Calibration

Date: 2026-07-04

Status: `research_descriptor_axis_calibration_no_package_code`

## Purpose

Fix review finding L-12 from `docs/03-code_review/2026-07-04-code_review.md`:
the `mutation_stability` and `lifecycle_survival` MAP-Elites axes were
degenerate (`descriptor_bin_spread` 1) on the default archive run — every
generated candidate inherited one fixed mutation vector, and every valid
candidate survived the whole lifecycle probe.

## What changed

1. **Mutation temperature** — `constrained_generator.generate_constrained_grid`
   now draws a per-candidate temperature `t = 0.05 + 0.95·random()` from a
   dedicated rng stream (`f"{rng_seed}:{grid_id}:mutation"`, separate from
   the structural stream so cell layouts are byte-identical to before) and
   sets each mutation rate to `round(cap · t, 6)`, where caps are the SLIP
   `*_max` limits when a profile is supplied, else the historical defaults.
   Deterministic; every regenerated grid (550 across all corpora) still
   passes `validate_grid` and `is_grid_aligned`.
2. **Cap-normalized stability metric** — `_mutation_stability` is now
   `1 − mean(rate/cap)`. The old raw-mean form mathematically could not
   leave the top bin under LCD caps (max raw mean 0.075 → stability ≥ 0.925,
   above the 0.9 bin edge), so jitter alone could never have varied the axis.
3. **Morphology-derived lifecycle stress probe** — the archive lab (not
   lifecycle_sim, whose arithmetic stays pinned) simulates each candidate
   under a stress load written to a deep copy's cells:
   `clamp(body_mass/16 + (1 − symmetry)·0.65 − sensor_count·0.08)`.
   Diagnosis behind it: the switchboard lifecycle is fully deterministic and
   reads the grid only through mean stress/damage (previously 0 for every
   candidate), so all candidates shared one trajectory; and the dynamics are
   **bistable** — stress ≤ 0.94 stabilizes forever, ≥ 0.95 collapses at tick
   12–14. On the default run 25/160 candidates die (`stress_collapse`) and
   135 survive.

## Result

Default archive run (`data/archives/map_elites_extended_stage0.json`):

```txt
descriptor_bin_spread: mutation_stability 1 -> 5, lifecycle_survival 1 -> 2
occupied_niches:  33 -> 83
qd_score:         31.619138 -> 72.069987
coverage:         0.000422 -> 0.001062
best_fitness:     0.979592 -> 0.972366
```

Honest limitation, recorded in the artifact and card: the lifecycle axis
yields spread 2, not a continuum — intermediate survival bins await a
harsher lifecycle model; the bistability finding is documented rather than
forced past.

Suites green: grid_genome 65 (+3 jitter tests), map_elites_archive 9 (+2
axis-variance regressions), lifecycle_sim, cellular_automata,
readability_benchmark, ctm_ticks, cubff_transducer, workshop_editor 307.
Regenerated deterministically: all constrained corpora (550 grids), the
extended archive, the multi-profile generation corpora, readability
artifacts, and the seven workshop SLIP gate artifacts (which also pick up
decision record 0005's retired `declared_dependency_manifest` blocker).
Verified byte-identical: legacy archive, lineage, cubff artifacts.

## Decision

Descriptor axes must be checked against `descriptor_bin_spread` before their
niche contribution is claimed (rule from the H-03 fix, now satisfied by all
seven axes with spread ≥ 2). The lifecycle bistability is a real finding for
the future lifecycle model: survival variance requires either stochastic
dynamics or morphology-coupled need decay, tracked as open calibration work.

## Verification

```powershell
python -B -m unittest discover -s labs/grid_genome -p "test_*.py"
python -B -m unittest discover -s labs/map_elites_archive -p "test_*.py"
python -B labs/map_elites_archive/extended_descriptors.py --output data\archives\map_elites_extended_stage0.json --count 160 --rng-seed 20260512 --lifecycle-ticks 24
python -m json.tool data\archives\map_elites_extended_stage0.json
```

## Sources

- `docs/03-code_review/2026-07-04-code_review.md`
- `labs/grid_genome/constrained_generator.py`
- `labs/map_elites_archive/extended_descriptors.py`
- `labs/map_elites_archive/test_extended_descriptors.py`
- `data/archives/map_elites_extended_stage0.json`
- `research/algorithm_cards/map_elites_extended_descriptors.md`
- `research/experiment_reports/2026-07-04-map-elites-neediness-descriptor-fix.md`
