# Experiment Report: Third-Party Project Decoder Boundary

Date: 2026-05-13

Status: `research_third_party_project_decoder_boundary_no_package_code`

## Question

Can Mechagotchi decode third-party project-file boundaries far enough to bind
project dimensions, frame count, and content hashes to the existing sidecar
contract, then restore semantic grids without pretending editor-native metadata
is the Mechagotchi schema?

## Plan Alignment

This continues the Stage 7 workshop/editor track in `docs/02-research_plan.md`.
The prior sidecar, static PNG, and fixed spritesheet proofs established the
metadata contract and image-carrier subsets. This experiment tests the next
narrower claim: project container/header decoding for current generated `SLIP`
profile grids. No `packages/` code was created.

## External Source Refresh

The boundary is anchored to primary project/source documentation:

- Piskel serializer:
  https://github.com/piskelapp/piskel/blob/master/src/js/utils/serialization/Serializer.js
- Piskel deserializer:
  https://github.com/piskelapp/piskel/blob/master/src/js/utils/serialization/Deserializer.js
- Pixelorama project documentation:
  https://pixelorama.org/concepts/project/
- Aseprite file format specification:
  https://github.com/aseprite/aseprite/blob/main/docs/ase-file-specs.md
- LibreSprite repository:
  https://github.com/LibreSprite/LibreSprite

Piskel is decoded as a JSON envelope with layer JSON strings and base64 PNG
chunks. Pixelorama `.pxo` is decoded as a ZIP container with `data.json` and
`image_data/frames` assets. Aseprite/LibreSprite is decoded at the header and
empty frame-header boundary using the published little-endian magic, dimension,
frame, and color-depth fields. Full editor-native layer/cel/chunk semantics are
explicitly not claimed.

## Method

Added `labs/workshop_editor/third_party_project_decoder.py` with:

- `decode_piskel_project`
- `decode_pixelorama_pxo`
- `decode_aseprite_header`
- `export_project_with_sidecar`
- `import_project_with_sidecar`
- `run_third_party_project_decoder_lab`
- `write_third_party_project_decoder_artifacts`

The lab exports one current generated grid per valid profile:

- `slip_lcd_seed` as `.piskel`
- `slip_gray_stable` as `.pxo`
- `slip_amber_social` as `.aseprite`

Each payload is decoded, measured, hashed, bound to a Mechagotchi sidecar, and
then imported back by restoring the semantic grid from the sidecar. Invalid
probes cover corrupt project JSON, sidecar content-hash mismatch, and
unsupported format IDs.

## Results

Machine-readable artifacts:

- `data/workshop_editor/third_party_project_decoder_stage0.json`
- `data/workshop_editor/third_party_project_decoder_stage0/third_party_project_decoder_stage0.json`
- `data/workshop_editor/third_party_project_decoder_stage0/slip_lcd_seed.piskel`
- `data/workshop_editor/third_party_project_decoder_stage0/slip_lcd_seed_project_sidecar.json`
- `data/workshop_editor/third_party_project_decoder_stage0/slip_gray_stable.pxo`
- `data/workshop_editor/third_party_project_decoder_stage0/slip_gray_stable_project_sidecar.json`
- `data/workshop_editor/third_party_project_decoder_stage0/slip_amber_social.aseprite`
- `data/workshop_editor/third_party_project_decoder_stage0/slip_amber_social_project_sidecar.json`
- `data/workshop_editor/third_party_project_decoder_data.js`

Summary:

| Metric | Result |
| --- | ---: |
| Current valid profiles covered | 3 |
| Project decoder successes | 3 |
| Sidecar restore successes | 3 |
| Invalid probes rejected | 3 |
| Project decoder success rate | 1.0 |
| Sidecar restore success rate | 1.0 |
| Mean semantic fidelity | 1.0 |
| Invalid probe rejection rate | 1.0 |
| Native metadata writers | 0 |

Closed states:

- `third_party_project_decoder_boundary`
- `piskel_project_json_boundary`
- `pixelorama_pxo_zip_data_json_boundary`
- `aseprite_libresprite_header_boundary`
- `project_file_sidecar_binding_integrity`
- `project_import_rejects_missing_or_mismatched_sidecar`

Blocked states:

- `full_project_format_coverage`
- `png_adam7_interlace_decoder`
- `apng_decoder`
- `full_png_conformance`
- `spritesheet_packed_rotation_trim_decoder`
- `runtime_animation_playback`
- `embedded_png_metadata_writer`
- `project_file_native_metadata_writer`
- `runtime_lifecycle_archive_selection`
- `profile_weighted_evolution`

## Interpretation

The generic `third-party project decoder` blocker is now too broad. The Stage 0
boundary proves that representative Piskel, Pixelorama, and Aseprite/LibreSprite
project payloads can be decoded enough to validate sidecar binding and restore
SLIP-aligned semantic grids.

This does not prove full `.piskel` animation editing, arbitrary Pixelorama
project schemas, complete `.ase/.aseprite` chunk parsing, layer-aware project
round trips, embedded PNG metadata writing, live external editor rewrite
validation, or
Aseprite/LibreSprite arbitrary project schema coverage. Piskel/Pixelorama native metadata
writing is now covered by
`research/experiment_reports/2026-05-13-project-native-metadata-writer.md`;
the remaining risks stay under full project-format coverage and editor rewrite
policy.

## Verification

RED command:

```powershell
python -B -m unittest labs\workshop_editor\test_third_party_project_decoder.py
```

Initial result:

```txt
ModuleNotFoundError: No module named 'third_party_project_decoder'
```

GREEN command:

```powershell
python -B -m unittest labs\workshop_editor\test_third_party_project_decoder.py
```

Result:

```txt
Ran 5 tests in 0.035s
OK
```

Artifact command:

```powershell
python -B labs\workshop_editor\third_party_project_decoder.py --output-dir data\workshop_editor\third_party_project_decoder_stage0
```

JSON checks:

```powershell
python -m json.tool data\workshop_editor\third_party_project_decoder_stage0.json
python -m json.tool data\workshop_editor\third_party_project_decoder_stage0\third_party_project_decoder_stage0.json
```

## Decision

Adopt `third_party_project_decoder_stage0` as the Stage 0 proof for
third-party project-file boundary decoding against the Mechagotchi sidecar
contract.

Runtime lifecycle/archive selection is now covered by
`research/experiment_reports/2026-05-13-slip-runtime-selection-policy.md`.
Next research should run held-out long-horizon behavior tests and manual
readability calibration before claiming profile-weighted evolution. The explicit PNG color/filter
variant subset is now covered by
`research/experiment_reports/2026-05-13-png-variant-sidecar-decoder.md`.
Spritesheet vertical/matrix/padded/sparse layout coverage is now covered by
`research/experiment_reports/2026-05-13-spritesheet-layout-variant-decoder.md`.
