# MAP-Elites Behavior-Neediness Descriptor Fix

Date: 2026-07-04

Status: `research_map_elites_extended_descriptor_fix_no_package_code`

## Purpose

Fix review finding H-03 from `docs/03-code_review/2026-07-04-code_review.md`:
the `behavior_neediness` descriptor in
`labs/map_elites_archive/extended_descriptors.py` returned the SLIP profile's
`behavior.neediness` directly whenever a profile was supplied. A SLIP profile
is constant for an archive run, so the seventh descriptor axis collapsed to a
single bin for every candidate (`slip_lcd_seed` neediness 0.4 → bin 1
always). The "3 → 7 descriptor expansion" claim was therefore inflated —
effectively six axes varied — and `coverage`, which divides by the full
5^7 = 78,125 niche space, understated reachable coverage ~5×.

## What changed

1. `_behavior_neediness` is now grid-derived per candidate
   (`0.35 + sensors * 0.08 − body_mass * 0.01`), with the SLIP profile's
   neediness applied as a prior shift
   (`+ (profile_neediness − 0.5) * 0.2`) instead of a replacement. The
   profile still influences the axis; it no longer collapses it.
2. The archive now reports `descriptor_bin_spread` — the count of distinct
   bins observed per axis across all candidates — so a degenerate axis is
   visible in the artifact instead of silently inflating
   `total_possible_niches`.
3. `test_extended_descriptors.py` adds two regression tests: the neediness
   axis must produce more than one bin across a diverse candidate set with a
   SLIP supplied, and `descriptor_bin_spread` must cover every axis.

## Result

RED (before): every candidate's `behavior_neediness` bin was 1 with the
default profile; `descriptor_bin_spread` did not exist.

GREEN (after), regenerated with the report's original command:

```powershell
python -B labs\map_elites_archive\extended_descriptors.py --output data\archives\map_elites_extended_stage0.json --count 160 --rng-seed 20260512 --lifecycle-ticks 24
```

```txt
occupied_niches: 33          (was 29)
qd_score: 31.619138          (was 27.773545)
mean_elite_fitness: 0.958156 (was 0.957708)
best_fitness: 0.979592       (unchanged)
descriptor_bin_spread:
  body_mass 3, sensor_count 4, symmetry 4, readability 3,
  lifecycle_survival 1, mutation_stability 1, behavior_neediness 2
```

```powershell
python -B -m unittest discover -s labs/map_elites_archive -p "test_*.py"
# Ran 7 tests in 0.362s
# OK  (was 5 tests before this change)
```

## Findings

The fixed axis adds four genuinely new archive niches on the same corpus.
The new spread diagnostic also shows `lifecycle_survival` and
`mutation_stability` are degenerate (spread 1) for the current seed corpus:
every valid candidate survives the 24-tick probe, and all seed grids share
one mutation vector (review finding L-12). Those axes are honest but
uninformative until the lifecycle probe is harder or the generator varies
mutation blocks — tracked as open calibration work, not fixed here.

## Decision

Keep the extended archive as an active prototype. Descriptor axes must be
candidate-derived; profile constants may only shift, never define, an axis.
Any future descriptor addition should be checked against
`descriptor_bin_spread` before its niche contribution is claimed.

## Verification

```powershell
python -B -m unittest discover -s labs/map_elites_archive -p "test_*.py"
python -B labs\map_elites_archive\extended_descriptors.py --output data\archives\map_elites_extended_stage0.json --count 160 --rng-seed 20260512 --lifecycle-ticks 24
python -m json.tool data\archives\map_elites_extended_stage0.json
```

## Sources

- `docs/03-code_review/2026-07-04-code_review.md`
- `labs/map_elites_archive/extended_descriptors.py`
- `labs/map_elites_archive/test_extended_descriptors.py`
- `data/archives/map_elites_extended_stage0.json`
- `research/algorithm_cards/map_elites_extended_descriptors.md`
- `research/experiment_reports/2026-05-12-map-elites-extended-descriptors.md`
