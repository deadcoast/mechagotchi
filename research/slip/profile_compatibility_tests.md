# SLIP Profile Compatibility Tests

Date: 2026-05-12

Status: `research_slip_profile_compatibility_matrix_no_package_code`

## Purpose

Define the current and future compatibility tests for `SLIP` profiles across
grid validation, generation, lifecycle simulation, archive scoring, workshop
round trips, and future package gates.

This file satisfies the research plan's required
`profile_compatibility_tests.md` output at research stage. It does not create a
package module, package tests, a final SLIP JSON Schema, or a workshop authoring
UI.

## Source Position

The research plan defines `SLIP` as:

```txt
SLIP = constraints + priors + weights + validators
```

The current Stage 0 implementation is narrower:

```txt
SLIP v0.1.0 =
  profile metadata
  + palette constraints
  + body-mass bounds
  + required organ roles
  + mutation-rate caps
  + bounded behavior weights
  + bounded survival weights
```

Any broader claim about animation vocabulary, forbidden traits, behavior
preview, export UX, profile-weighted evolution, or community profile packs is
not yet proven.

## External Anchors

The future profile contract should remain JSON-compatible:

- JSON Schema Draft 2020-12 is the interchange target for machine-readable
  profile schemas.
- Pydantic v2 is a candidate Python authoring/validation model because it can
  validate typed models and emit JSON Schema through `model_json_schema()`.

Neither source changes the current Stage 0 facts. The current repository
validator remains `labs/grid_genome/slip.py`.

## Current Fixture Corpus

| Group | Path | Count | Current result |
| --- | --- | ---: | --- |
| Valid profiles | `data/slips/valid/*.json` | 3 | accepted by lab validator |
| Invalid profiles | `data/slips/invalid/*.json` | 2 | rejected by lab validator |
| SLIP-constrained grids | `data/generated_grids/slip_lcd_seed_constrained/*.json` | 50 | valid and aligned with `slip_lcd_seed` |
| Multi-profile constrained grids | `data/slips/multi_profile_generation_stage0/*/*.json` | 150 | valid and aligned across all 3 valid profiles |
| Workshop round trip | `data/workshop_editor/workshop_roundtrip_stage0_report.json` | 1 | native JSON round trip with `slip_lcd_seed` |
| Lifecycle comparator | `data/lifecycle/lifecycle_stage0.json` | 1 | profile ID recorded as `slip_lcd_seed` |

## Current Valid Profiles

| Profile | Palette | Body mass | Required organ roles | Behavior weights | Survival weights |
| --- | --- | --- | --- | --- | --- |
| `slip_lcd_seed` | `lcd_green` | `4..24` | `sensor`, `expression` | curiosity `0.6`, neediness `0.4`, sleepiness `0.5` | stability `0.5`, novelty `0.25`, bond `0.25` |
| `slip_gray_stable` | `gameboy_gray` | `5..24` | `sensor`, `expression` | curiosity `0.35`, neediness `0.3`, sleepiness `0.65` | stability `0.7`, novelty `0.1`, bond `0.2` |
| `slip_amber_social` | `amber_terminal` | `6..24` | `sensor`, `expression` | curiosity `0.7`, neediness `0.6`, sleepiness `0.35` | stability `0.4`, novelty `0.25`, bond `0.35` |

## Current Invalid Profiles

| Profile | Fault | Expected rejection |
| --- | --- | --- |
| `slip_invalid_bad_weight` | `behavior.curiosity = 1.2` | value outside `0..1` |
| `slip_invalid_palette` | `grid.allowed_palettes = ["unknown_palette"]` | unknown palette |

These invalid fixtures are profile-shape and value tests. They are not enough
to prove grid/profile cross-product compatibility.

## Validator Contract Observed

The current lab validator enforces:

- `slip_version` exactly equals `0.1.0`;
- `profile_id` and `name` are non-empty strings;
- `grid.allowed_palettes` is a non-empty list of known palettes;
- `grid.body_mass_min` and `grid.body_mass_max` are integers;
- body mass minimum is at least `1`;
- body mass maximum is not below minimum;
- `grid.required_organ_roles` is a non-empty list;
- required organ roles are limited to `sensor`, `expression`, and `body_core`;
- provided `behavior` values are numbers in `[0, 1]`;
- provided `survival_weights` values are numbers in `[0, 1]`;
- mutation caps are numbers in `[0, 1]`;
- grid alignment checks palette ID, core-cell body mass, required organ roles,
  and mutation-rate caps.

Important Stage 0 limitation:

```txt
The validator bounds provided behavior and survival keys, but it does not yet
require a complete behavior vocabulary or survival-weight vocabulary.
```

## Compatibility Matrix

| Surface | Current proof | Current status | Required next proof |
| --- | --- | --- | --- |
| Profile validation | 3 valid profiles accepted, 2 invalid profiles rejected | proven narrow | versioned schema/failure corpus |
| Generation alignment | 150/150 current valid-profile constrained candidates valid and aligned | proven for current 3-profile corpus | expanded community and unsatisfiable-profile corpus |
| Grid validator | generated candidates pass grid validation | proven for current profile-aware candidate corpora | profile-aware negative cases and held-out profiles |
| Lifecycle | lifecycle fixture records `slip_lcd_seed`; profile can be passed into lab simulator | partial | behavior-weight effect tests and invalid-profile rejection |
| Archive | extended descriptors include `slip_alignment` | partial | multi-profile descriptor calibration and blocked-state reporting |
| Workshop round trip | native JSON round trip preserves semantics under `slip_lcd_seed` | proven single profile/single seed | multi-profile and held-out grid round trips |
| CA/NCA growth/repair | growth/repair measured against LCD profile; mixed palettes lower alignment to `0.25` | diagnostic only | profile-matched CA/NCA alignment by palette family |
| CuBFF hybrid transducer | hybrid path reports 12/12 valid and aligned under active profile | limited | real snapshot and multi-profile transducer compatibility |
| Future package tests | generation/lifecycle/property strategies mention SLIP rejection and alignment | specified only | package import-surface tests after package work starts |

## Required Future Compatibility Tests

### 1. Profile Schema Tests

Future tests must validate:

- exact version handling;
- required metadata;
- known palette IDs;
- legal body-mass bounds;
- known required organ roles;
- required mutation cap keys;
- behavior values in `[0, 1]`;
- survival values in `[0, 1]`;
- no boolean values accepted as numeric profile weights;
- clear error families for every failed field group.

### 2. Profile-Grid Alignment Tests

For each valid profile, future tests must check:

- at least one aligned seed or generated grid exists;
- a grid with a disallowed palette fails;
- a grid below `body_mass_min` fails;
- a grid above `body_mass_max` fails;
- a grid missing each required organ role fails;
- a grid exceeding each mutation cap fails;
- validation and alignment do not mutate the profile or grid payload.

### 3. Profile-Constrained Generation Tests

For each valid profile, future tests must check:

- generation either produces valid aligned candidates or fails with an explicit
  unsatisfiable-profile result;
- deterministic seed plus same profile reproduces candidate identity and
  semantic grid signature;
- candidate explanation includes `slip_alignment`;
- rejected proposals are counted and surfaced;
- profile-specific palette constraints are visible in generated output.

Current proof exists for all three valid Stage 0 profiles:

```txt
150 generated candidates
150 valid candidates
150 SLIP-aligned candidates
0 alignment failures
```

### 4. Lifecycle Compatibility Tests

For each valid profile, future tests must check:

- invalid profiles fail before state creation;
- behavior weights are normalized or consumed exactly as documented;
- changing behavior weights changes at least one documented lifecycle decision
  or leaves an explicit no-effect trace;
- survival weights contribute to score computation with a documented formula;
- lifecycle state and rewards stay bounded.

Current lifecycle evidence is not enough to claim full behavior compatibility.

### 5. Archive Compatibility Tests

Future archive tests must check:

- `slip_alignment` is a descriptor or score component only when a valid profile
  is present;
- missing or invalid profile produces a blocked/neutral state, not a false
  aligned score;
- descriptor thresholds do not claim human calibration before manual ratings
  exist;
- profile-specific archive coverage can be reported separately from global
  archive coverage.

### 6. Workshop Compatibility Tests

Future workshop tests must check:

- profile import/export preserves all SLIP fields;
- edited grids remain aligned or report actionable alignment errors;
- native JSON round trips pass for all valid profiles;
- held-out generated grids pass import/export fidelity checks;
- invalid profiles cannot be loaded as active workshop constraints;
- standard image/spritesheet imports remain blocked until sidecar metadata can
  preserve organs, mutation weights, and profile constraints.

Current proof is one native JSON round trip under `slip_lcd_seed`.

## Blocked States

The following claims remain blocked:

- full SLIP JSON Schema, because it has not been authored yet;
- Pydantic-backed SLIP contract, because no dependency decision or model exists;
- behavior preview, because behavior weights are bounded but not yet proven to
  drive preview behavior;
- mutation preview UI, because no workshop mutation preview exists;
- profile-weighted evolution, because archive/lifecycle use remains partial;
- community profile packs, because profile versioning and compatibility
  migration are not defined.

## Future Verification Commands

Research-stage checks:

```powershell
python -m json.tool .\data\slips\slip_profile_compatibility_matrix_stage0.json
Test-Path .\packages
rg -n "slip_profile_compatibility_matrix|research_slip_profile_compatibility_matrix_no_package_code|profile_compatibility_tests" .\research .\data
git diff --check
```

Existing lab reference checks:

```powershell
python -B -m unittest discover -s .\labs\grid_genome -p "test_*.py"
python -B -m unittest discover -s .\labs\workshop_editor -p "test_*.py"
```

Future package checks become valid only after package work starts:

```powershell
python -B -m unittest discover -s .\packages\mecha_engine\tests -p "test_*.py"
rg -n "from labs|import labs|labs/|labs\\|sys\.path" .\packages\mecha_engine
```

## Decision

Adopt this matrix as the Stage 0 SLIP compatibility test plan. Keep the current
SLIP validator as a narrow lab prototype. Do not claim full profile-authoring
compatibility until multi-profile generation, lifecycle behavior effects,
archive descriptors, and workshop round trips are proven.

Next research step:

```txt
Either author the versioned SLIP schema/failure-case corpus, or extend workshop
round trips across the generated multi-profile corpora.
```

## References

- `docs/01-brainstorming.md`
- `docs/02-research_plan.md`
- `data/slips/README.md`
- `data/slips/valid/slip_lcd_seed.json`
- `data/slips/valid/slip_gray_stable.json`
- `data/slips/valid/slip_amber_social.json`
- `data/slips/invalid/slip_invalid_bad_weight.json`
- `data/slips/invalid/slip_invalid_palette.json`
- `labs/grid_genome/slip.py`
- `labs/grid_genome/test_slip_constraints.py`
- `research/algorithm_cards/slip_schema_validator.md`
- `research/experiment_reports/2026-05-12-slip-constraint-baseline.md`
- `research/experiment_reports/2026-05-12-slip-multi-profile-generation-benchmark.md`
- `data/generated_grids/slip_lcd_seed_constrained/README.md`
- `data/slips/multi_profile_generation_stage0/slip_multi_profile_generation_stage0.json`
- JSON Schema Draft 2020-12: https://json-schema.org/draft/2020-12
- Pydantic JSON Schema docs: https://docs.pydantic.dev/latest/concepts/json_schema/
