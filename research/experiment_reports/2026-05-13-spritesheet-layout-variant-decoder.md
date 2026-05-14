# Experiment Report: Spritesheet Layout Variant Decoder

Date: 2026-05-13

Status: `research_spritesheet_layout_variant_decoder_no_package_code`

## Question

Can Mechagotchi broaden the fixed horizontal spritesheet proof to common
spritesheet layouts while preserving `SLIP` semantics through sidecar metadata
instead of treating layout metadata as native Mechagotchi schema?

## Plan Alignment

This continues the Stage 7 workshop/editor track in
`docs/02-research_plan.md`. The prior spritesheet proof covered only fixed
equal-size horizontal strips. This experiment tests explicit layout variants:
vertical strip, row-major matrix, padded/guttered grid, and sparse atlas rects.
No `packages/` code was created.

## External Source Refresh

Sources used:

- Aseprite sprite-sheet docs: https://www.aseprite.org/docs/sprite-sheet/
- Aseprite CLI docs: https://aseprite.com/docs/cli/
- Pixelorama import docs: https://pixelorama.org/user_manual/Import/
- W3C PNG specification: https://www.w3.org/TR/png-3/

Aseprite documents horizontal, vertical, matrix, rows/columns, and packed sheet
types, plus JSON data export context. Pixelorama treats spritesheets as import
workflow surface. PNG remains only the image carrier.

## Method

Added `labs/workshop_editor/spritesheet_layout_variant_decoder.py` with:

- `export_spritesheet_layout_variant_suite_with_sidecars`
- `import_spritesheet_layout_variant_with_sidecar`
- `validate_layout_variant_sidecar_binding`
- `extract_layout_variant_frames`
- `run_spritesheet_layout_variant_decoder_lab`
- `write_spritesheet_layout_variant_decoder_artifacts`

Added `labs/workshop_editor/test_spritesheet_layout_variant_decoder.py` first,
watched it fail on the missing module, then implemented the decoder.

The layout suite exports the first generated grid for each current valid
profile into four PNG carriers:

| Layout | Sheet model | Rect coverage |
| --- | --- | --- |
| `vertical_strip` | equal frames top-to-bottom | 3 stacked frame rects |
| `row_major_matrix` | 2x2 row-major matrix | 3 occupied matrix cells |
| `padded_grid` | horizontal row with margin/gutter | explicit padding and spacing |
| `sparse_atlas` | unrotated sparse atlas rects | non-contiguous explicit rects |

Every exported asset is bound to a Mechagotchi sidecar. Import validates PNG
bytes, asset binding, sheet dimensions, frame rectangles, non-overlap,
per-frame pixel hashes, restored grid validity, `SLIP` alignment, semantic
fidelity, and frame-pixel fidelity.

Invalid probes cover out-of-bounds frame rectangles, overlapping frame
rectangles, and frame hash mismatch.

## Results

Machine-readable artifacts:

- `data/workshop_editor/spritesheet_layout_variant_decoder_stage0.json`
- `data/workshop_editor/spritesheet_layout_variant_decoder_stage0/spritesheet_layout_variant_decoder_stage0.json`
- `data/workshop_editor/spritesheet_layout_variant_decoder_stage0/*.png`
- `data/workshop_editor/spritesheet_layout_variant_decoder_stage0/*_sidecar.json`
- `data/workshop_editor/spritesheet_layout_variant_decoder_data.js`

Summary:

| Metric | Result |
| --- | ---: |
| Current valid profiles covered | 3 |
| Layouts per profile | 4 |
| Layout round-trip successes | 12 |
| Invalid probes rejected | 3 |
| Layout round-trip success rate | 1.0 |
| Mean semantic fidelity | 1.0 |
| Mean frame pixel fidelity | 1.0 |
| Invalid probe rejection rate | 1.0 |

Closed states:

- `spritesheet_vertical_matrix_padded_sparse_layout_decoder`
- `spritesheet_layout_variant_sidecar_export`
- `spritesheet_layout_variant_sidecar_import`
- `spritesheet_layout_rect_duration_hash_validation`
- `spritesheet_layout_sidecar_semantic_restore`

Blocked states:

- `spritesheet_packed_rotation_trim_decoder`
- `runtime_animation_playback`
- `full_project_format_coverage`
- `embedded_png_metadata_writer`
- `project_file_native_metadata_writer`
- `profile_weighted_evolution`

## Interpretation

The generic `spritesheet_variant_layout_coverage` blocker is now too coarse and
has been replaced in current ledgers by the precise remaining spritesheet gaps
above.

This is not a claim that all atlas formats are supported. Rotated frames,
trimmed frames, arbitrary packing algorithms, tags, layers, and runtime
animation playback remain open. The semantic contract remains unchanged:
Mechagotchi profile, organ, mutation, and lineage semantics come from the
sidecar, not from PNG pixels or third-party spritesheet metadata.

## Verification

RED command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_spritesheet_layout_variant_decoder.py
```

Initial result:

```txt
ModuleNotFoundError: No module named 'spritesheet_layout_variant_decoder'
```

GREEN command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_spritesheet_layout_variant_decoder.py
```

Result:

```txt
Ran 5 tests in 0.069s
OK
```

Artifact command:

```powershell
python -B .\labs\workshop_editor\spritesheet_layout_variant_decoder.py
```

## Decision

Adopt `spritesheet_layout_variant_decoder_stage0` as the Stage 0 proof for
vertical, matrix, padded-grid, and sparse-atlas spritesheet sidecar
import/export.

Runtime lifecycle/archive selection is now covered by
`research/experiment_reports/2026-05-13-slip-runtime-selection-policy.md`.
Packed trim/rotation and sidecar runtime playback are now covered by
`research/experiment_reports/2026-05-13-spritesheet-packed-runtime-decoder.md`
for the Stage 0 subset. Next research should keep arbitrary atlas packing,
tags/layers, production renderer playback, full project-format coverage, and
project-file native metadata writers explicitly blocked until separately
proven. PNG `tEXt` embedded sidecar writing is tracked separately in
`research/experiment_reports/2026-05-13-png-embedded-sidecar-writer.md`.
