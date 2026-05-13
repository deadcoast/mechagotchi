# SLIP Profile Compatibility Tests

Date: 2026-05-12

Status: `research_slip_profile_compatibility_matrix_no_package_code`

## Purpose

Define the current and future compatibility tests for `SLIP` profiles across
grid validation, generation, lifecycle simulation, archive scoring, workshop
round trips, and future package gates.

This file satisfies the research plan's required
`profile_compatibility_tests.md` output at research stage. It does not create a
package module, package tests, runtime JSON Schema integration, or a
package-level Pydantic dependency.

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

The profile contract should remain JSON-compatible:

- JSON Schema Draft 2020-12 is the interchange target for machine-readable
  profile schemas.
- Pydantic v2 is the current lab Python authoring/validation model because it
  validates typed models and emits JSON Schema through `model_json_schema()`.

Neither source changes the current Stage 0 facts. The current generation and
alignment validator remains `labs/grid_genome/slip.py`; the schema failure
corpus is checked by `labs/slip_validator/slip_validator.py` and the lab
Pydantic contract is checked by `labs/slip_validator/pydantic_contract.py`.

## Current Fixture Corpus

| Group | Path | Count | Current result |
| --- | --- | ---: | --- |
| Valid profiles | `data/slips/valid/*.json` | 3 | accepted by lab validator |
| Research examples | `research/slip/slip_examples/*.json` | 3 | accepted by Stage 0 schema validator |
| Invalid profiles | `data/slips/invalid/*.json` | 2 | rejected by lab validator |
| Schema failure cases | `data/slips/failure_cases/*.json` | 12 | rejected by Stage 0 schema validator |
| Schema validation report | `data/slips/slip_schema_validation_stage0.json` | 1 | 3 valid accepted, 3 examples accepted, 12 failures rejected |
| Pydantic contract report | `data/slips/slip_pydantic_contract_stage0.json` | 1 | 3 valid accepted, 3 examples accepted, 12 failures rejected |
| Migration/dependency report | `data/slips/slip_schema_migration_dependency_gate_stage0.json` | 1 | schema surface parity proven; only `0.1.0` accepted with no migration |
| SLIP authoring panel | `data/workshop_editor/slip_authoring_panel_stage0.json` | 1 | 3 current drafts accepted, 3 invalid probes rejected |
| SLIP behavior/mutation preview | `data/workshop_editor/slip_behavior_mutation_preview_stage0.json` | 1 | 3 behavior previews, 3 mutation previews, 2 invalid preview probes rejected |
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

These invalid fixtures are profile-shape and value tests. The expanded schema
failure corpus adds required-field, type, enum, range, minimum-item,
additional-property, semantic body-mass, and boolean numeric failures. Neither
corpus proves grid/profile cross-product compatibility by itself.

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

The Stage 0 schema validator additionally requires the complete current
behavior vocabulary (`curiosity`, `neediness`, `sleepiness`) and survival
vocabulary (`stability`, `novelty`, `bond`) for file-level profile payloads.

Important generation-validator limitation:

```txt
The validator bounds provided behavior and survival keys, but it does not yet
require a complete behavior vocabulary or survival-weight vocabulary.
```

## Compatibility Matrix

| Surface | Current proof | Current status | Required next proof |
| --- | --- | --- | --- |
| Profile validation | 3 valid profiles accepted, 3 examples accepted, 12 schema failure cases rejected by both dependency-free and Pydantic lab validators; schema surface parity proven; only `0.1.0` accepted with no migration; legacy 2 invalid fixtures also rejected by lab validator | proven Stage 0 schema/failure corpus, lab Pydantic contract, and migration policy | runtime JSON Schema dependency and declared package dependency manifest |
| Generation alignment | 150/150 current valid-profile constrained candidates valid and aligned | proven for current 3-profile corpus | expanded community and unsatisfiable-profile corpus |
| Grid validator | generated candidates pass grid validation | proven for current profile-aware candidate corpora | profile-aware negative cases and held-out profiles |
| Lifecycle | lifecycle fixture records `slip_lcd_seed`; profile can be passed into lab simulator | partial | behavior-weight effect tests and invalid-profile rejection |
| Archive | extended descriptors include `slip_alignment` | partial | multi-profile descriptor calibration and blocked-state reporting |
| Workshop round trip | native JSON round trip preserves semantics across 150 generated candidates under 3 valid profiles | proven for generated multi-profile corpus | external metadata sidecar strategy |
| SLIP authoring panel | 3/3 current profile drafts accepted and 3/3 invalid probes rejected by migration, dependency-free, and Pydantic gates | proven minimal panel for current Stage 0 schema | external metadata sidecar strategy and usability pilot |
| SLIP preview gates | 3/3 current profiles produce deterministic behavior previews and bounded mutation previews; 2/2 invalid preview probes rejected before activation | proven deterministic Stage 0 preview gate | measured lifecycle/archive effects before profile-weighted evolution claims |
| CA/NCA growth/repair | growth/repair measured against LCD profile; mixed palettes lower alignment to `0.25` | diagnostic only | profile-matched CA/NCA alignment by palette family |
| CuBFF hybrid transducer | hybrid path reports 12/12 valid and aligned under active profile | limited | real snapshot and multi-profile transducer compatibility |
| Future package tests | generation/lifecycle/property strategies mention SLIP rejection and alignment | specified only | package import-surface tests after package work starts |

## Required Future Compatibility Tests

### 1. Profile Schema Tests

Current Stage 0 schema tests validate:

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

Current Pydantic contract tests add model validation, model-generated JSON
Schema, extra-forbid handling, and corpus parity. Future schema tests must add
runtime JSON Schema engine parity, declared dependency policy, non-`0.1.0`
migration fixture corpora when a new version exists, and unsatisfiable-profile
diagnostics.

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

- profile import/export preserves all SLIP fields; minimal current-schema
  authoring panel proof is done in
  `data/workshop_editor/slip_authoring_panel_stage0.json`;
- edited grids remain aligned or report actionable alignment errors;
- native JSON round trips pass for all valid profiles; first generated-corpus
  proof is done in
  `data/workshop_editor/multi_profile_roundtrip_stage0/workshop_multi_profile_roundtrip_stage0.json`;
- held-out generated grids pass import/export fidelity checks; first generated
  multi-profile corpus proof is done;
- invalid profiles cannot be loaded as active workshop constraints;
- standard image/spritesheet imports remain blocked until sidecar metadata can
  preserve organs, mutation weights, and profile constraints.

Current proof is 150 native JSON round trips across the generated three-profile
SLIP corpus. External image and project-file round trips remain blocked.

## Blocked States

The following claims remain blocked:

- runtime JSON Schema validation, because the dependency selection is not made;
- declared Pydantic package dependency, because no dependency manifest exists;
- profile-weighted evolution, because archive/lifecycle use remains partial;
- engine lifecycle behavior integration, because the preview gate is not a
  runtime policy or lifecycle simulator;
- external image/project metadata sidecars, because non-native imports cannot
  yet preserve organ, mutation, and profile metadata;
- community profile packs, because profile versioning and compatibility
  migration are not defined.

## Future Verification Commands

Research-stage checks:

```powershell
python -m json.tool .\data\slips\slip_profile_compatibility_matrix_stage0.json
python -m json.tool .\research\slip\slip.schema.json
python -m json.tool .\data\slips\slip_schema_validation_stage0.json
python -m json.tool .\research\slip\slip_pydantic_model.schema.json
python -m json.tool .\data\slips\slip_pydantic_contract_stage0.json
python -m json.tool .\data\slips\slip_schema_migration_dependency_gate_stage0.json
python -m json.tool .\data\workshop_editor\slip_authoring_panel_stage0.json
python -m json.tool .\data\workshop_editor\slip_behavior_mutation_preview_stage0.json
python -B -m unittest discover -s .\labs\slip_validator -p "test_*.py"
python -B -m unittest discover -s .\labs\workshop_editor -p "test_*.py"
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
SLIP validator as a narrow lab prototype. Treat the Stage 0 schema, failure
corpus, Pydantic lab model, and migration/dependency gate as the current
file-level profile contract. Do not claim full profile-authoring compatibility
until runtime JSON Schema validation, declared dependency policy, lifecycle
behavior effects, archive descriptors, usability evidence, and external
metadata strategies are proven.

Next research step:

```txt
Define the external metadata sidecar strategy for non-native image/project
imports, or connect preview signals to measured lifecycle/archive effects
before claiming profile-weighted evolution.
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
- `research/experiment_reports/2026-05-12-workshop-multi-profile-roundtrip.md`
- `research/experiment_reports/2026-05-12-slip-schema-failure-corpus.md`
- `research/slip/slip.schema.json`
- `research/slip/slip_examples/`
- `research/slip/slip_failure_cases.md`
- `data/slips/slip_schema_validation_stage0.json`
- `research/slip/pydantic_contract.md`
- `research/slip/slip_pydantic_model.schema.json`
- `data/slips/slip_pydantic_contract_stage0.json`
- `research/slip/schema_migration_dependency_gate.md`
- `data/slips/slip_schema_migration_dependency_gate_stage0.json`
- `research/experiment_reports/2026-05-12-slip-authoring-panel.md`
- `research/experiment_reports/2026-05-12-slip-behavior-mutation-preview-gate.md`
- `labs/workshop_editor/slip_authoring_panel.py`
- `labs/workshop_editor/slip_preview_gates.py`
- `data/workshop_editor/slip_authoring_panel_stage0.json`
- `data/workshop_editor/slip_behavior_mutation_preview_stage0.json`
- `data/workshop_editor/slip_authoring_panel_stage0/`
- `data/workshop_editor/slip_behavior_mutation_preview_stage0/`
- `data/generated_grids/slip_lcd_seed_constrained/README.md`
- `data/slips/multi_profile_generation_stage0/slip_multi_profile_generation_stage0.json`
- `data/workshop_editor/multi_profile_roundtrip_stage0/workshop_multi_profile_roundtrip_stage0.json`
- JSON Schema Draft 2020-12: https://json-schema.org/draft/2020-12
- Pydantic JSON Schema docs: https://docs.pydantic.dev/latest/concepts/json_schema/
