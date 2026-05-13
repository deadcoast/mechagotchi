# Experiment Report: External Metadata Sidecar Strategy

Date: 2026-05-12

Status: `research_external_metadata_sidecar_strategy_no_package_code`

## Question

Can a JSON sidecar preserve Mechagotchi semantic grid metadata for non-native
visual assets and third-party project files without depending on image or
project decoders?

## Plan Alignment

This continues the Stage 7 workshop/editor track in `docs/02-research_plan.md`.
The plan recommends studying external pixel editors while keeping Mechagotchi's
organ roles, mutation weights, survival semantics, and `SLIP` constraints in a
native schema. No `packages/` code was created.

## External Source Refresh

The sidecar strategy uses external tools and formats as interoperability
anchors, not as embedded implementation dependencies:

- W3C PNG specification: https://www.w3.org/TR/png-3/
- Piskel project reference: https://github.com/piskelapp/piskel
- Pixelorama import/export documentation:
  https://www.pixelorama.org/user_manual/Import/
- LibreSprite project reference: https://github.com/LibreSprite/LibreSprite

PNG and spritesheet PNG are treated as visual carriers. Piskel, Pixelorama, and
LibreSprite are treated as non-native project/workflow references. The Stage 0
policy is that all five adapter targets require a Mechagotchi JSON sidecar for
semantic preservation.

## Method

Added `labs/workshop_editor/external_metadata_sidecar.py` with:

- `build_external_asset_stub`
- `build_sidecar_for_grid`
- `validate_sidecar_binding`
- `restore_grid_from_sidecar`
- `run_external_metadata_sidecar_lab`
- `write_external_metadata_sidecar_artifacts`

The lab selects the first generated grid for each current valid profile from
`data/slips/multi_profile_generation_stage0/`, creates a non-native PNG asset
stub, binds it to a sidecar containing the semantic overlay and `SLIP` profile
snapshot, validates hash/dimension/profile binding, restores the semantic grid,
and checks grid validity plus `SLIP` alignment.

Invalid probes mutate the asset hash and dimensions. Both must fail before a
sidecar can be accepted.

## Results

Machine-readable artifacts:

- `data/workshop_editor/external_metadata_sidecar_stage0.json`
- `data/workshop_editor/external_metadata_sidecar_stage0/external_metadata_sidecar_stage0.json`
- `data/workshop_editor/external_metadata_sidecar_stage0/adapter_matrix.json`
- `data/workshop_editor/external_metadata_sidecar_stage0/slip_lcd_seed_external_sidecar.json`
- `data/workshop_editor/external_metadata_sidecar_stage0/slip_gray_stable_external_sidecar.json`
- `data/workshop_editor/external_metadata_sidecar_stage0/slip_amber_social_external_sidecar.json`
- `data/workshop_editor/external_metadata_sidecar_data.js`

Summary:

| Metric | Result |
| --- | ---: |
| Current valid profiles covered | 3 |
| Sidecar round-trip successes | 3 |
| Invalid binding probes rejected | 2 |
| Sidecar round-trip success rate | 1.0 |
| Mean semantic fidelity | 1.0 |
| Invalid probe rejection rate | 1.0 |
| Adapter formats requiring sidecar | 5 |

Closed states:

- `external_metadata_sidecar_strategy`
- `sidecar_asset_binding_integrity`
- `sidecar_restores_semantic_grid`
- `sidecar_preserves_slip_alignment`
- `format_adapter_policy_matrix`

Blocked states:

- `png_adam7_interlace_decoder`
- `apng_decoder`
- `full_png_conformance`
- `spritesheet_packed_rotation_trim_decoder`
- `runtime_animation_playback`
- `full_project_format_coverage`
- `embedded_png_metadata_writer`
- `project_file_native_metadata_writer`
- `profile_weighted_evolution`

## Interpretation

The sidecar strategy is now proven as a Stage 0 metadata preservation contract.
It demonstrates that Mechagotchi semantics can travel alongside non-native
visual/project assets and restore valid, `SLIP`-aligned semantic grids.

This does not prove GIF handling, full Piskel animation semantics, arbitrary
Pixelorama project schemas, complete LibreSprite/Aseprite chunk parsing, or
embedded/native metadata writing. Those require dedicated decoder/importer labs
using this sidecar contract as their acceptance boundary.

Supersession note: static non-interlaced 8-bit RGBA PNG import/export and
fixed horizontal-strip spritesheet PNG import/export against this sidecar
contract are now covered by
`research/experiment_reports/2026-05-12-standard-image-sidecar-decoder.md` and
`research/experiment_reports/2026-05-12-spritesheet-sidecar-decoder.md`.
PNG color/filter variant decoding is now covered by
`research/experiment_reports/2026-05-13-png-variant-sidecar-decoder.md`.
Project-file boundary decoding is now covered by
`research/experiment_reports/2026-05-13-third-party-project-decoder-boundary.md`.
Spritesheet vertical/matrix/padded/sparse layout coverage is now covered by
`research/experiment_reports/2026-05-13-spritesheet-layout-variant-decoder.md`.
Packed rotation/trim atlas handling, runtime animation playback, full PNG
conformance, full project-format coverage, and embedded/native metadata
writers remain open.

## Verification

RED command:

```powershell
python -B -m unittest labs\workshop_editor\test_external_metadata_sidecar.py
```

Initial result:

```txt
ModuleNotFoundError: No module named 'external_metadata_sidecar'
```

GREEN command:

```powershell
python -B -m unittest labs\workshop_editor\test_external_metadata_sidecar.py
```

Result:

```txt
Ran 6 tests in 0.013s
OK
```

Artifact command:

```powershell
python -B labs\workshop_editor\external_metadata_sidecar.py --output-dir data\workshop_editor\external_metadata_sidecar_stage0
```

JSON checks:

```powershell
python -m json.tool data\workshop_editor\external_metadata_sidecar_stage0.json
python -m json.tool data\workshop_editor\external_metadata_sidecar_stage0\external_metadata_sidecar_stage0.json
python -m json.tool data\workshop_editor\external_metadata_sidecar_stage0\adapter_matrix.json
```

## Decision

Adopt `external_metadata_sidecar_stage0` as the Stage 0 strategy for preserving
Mechagotchi semantic metadata beside non-native visual assets and third-party
project files.

Runtime lifecycle/archive selection is now covered by
`research/experiment_reports/2026-05-13-slip-runtime-selection-policy.md`.
Next research should run held-out long-horizon behavior tests and manual
readability calibration before claiming profile-weighted evolution. The measured lifecycle/archive
bridge is now covered in
`research/experiment_reports/2026-05-12-slip-lifecycle-archive-effects.md`.
