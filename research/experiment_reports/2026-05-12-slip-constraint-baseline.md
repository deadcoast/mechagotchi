# Experiment Report: SLIP Constraint Baseline

Date: 2026-05-12

## Objective

Add the first SLIP constraints from the proposed research sequence and prove
that profile validation can influence generated grid output.

## Scope

Included:

- minimal SLIP validator under `labs/grid_genome/slip.py`
- three valid profile files under `data/slips/valid/`
- two invalid profile files under `data/slips/invalid/`
- constrained-generator `--slip` input
- 50 generated LCD-profile candidates under
  `data/generated_grids/slip_lcd_seed_constrained/`

Not included:

- full JSON Schema for SLIP
- workshop editor
- behavior preview
- mutation preview UI
- evolution weighting
- export/import tooling

## SLIP Fields Tested

- `slip_version`
- `profile_id`
- `name`
- allowed palettes
- body mass bounds
- required organ roles
- mutation-rate maximums
- behavior weights in 0..1
- survival weights in 0..1

## Verification

Command:

```powershell
python -m unittest discover -s labs\grid_genome -p 'test_*.py'
```

Result:

```txt
Ran 24 tests in 0.242s
OK
```

Profile validation:

```json
{
  "valid_profiles": 3,
  "accepted": 3,
  "invalid_profiles": 2,
  "accepted_invalid_profiles": 0,
  "rejected_invalid_profiles": 2
}
```

Generation command:

```powershell
python labs\grid_genome\constrained_generator.py --generated-dir data\generated_grids\slip_lcd_seed_constrained --count 50 --rng-seed 313 --slip data\slips\valid\slip_lcd_seed.json
```

Generation result:

```json
{
  "candidate_count": 50,
  "valid_count": 50,
  "invalid_count": 0,
  "validity_rate": 1.0,
  "unique_signatures": 50,
  "alignment_count": 50,
  "alignment_errors": {}
}
```

## Findings

The first SLIP contract is sufficient to constrain generated output for palette,
body mass, organ roles, and mutation-rate limits. This proves the basic
research claim that a profile can guide generation without replacing the core
engine.

The current profile system is still narrow. It does not yet test behavior,
survival scoring, animation vocabulary, forbidden traits, or profile-weighted
evolution.

## Decision

Keep SLIP constraints in the generator path. The next research step should
either expand SLIP into a JSON Schema/Pydantic contract or proceed to the first
MAP-Elites archive only after the generator emits fitness and descriptor data.

