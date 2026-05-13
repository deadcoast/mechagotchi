# Experiment Report: Spritesheet Sidecar Decoder

Date: 2026-05-12

Status: `research_spritesheet_sidecar_decoder_no_package_code`

## Question

Can Mechagotchi export a real fixed-grid spritesheet PNG, import it through the
Stage 0 PNG decoder, bind frame rectangles and durations through a sidecar, and
restore the semantic grid without inferring organ metadata from pixels?

## Plan Alignment

This continues the Stage 7 workshop/editor track in `docs/02-research_plan.md`.
The prior sidecar and static PNG decoder proofs established the metadata
contract and image decoder subset. This experiment tests the next narrower
claim: fixed equal-size horizontal spritesheet PNG import/export for current
generated `SLIP` profile grids. No `packages/` code was created.

## External Source Refresh

The experiment uses three format/workflow anchors:

- W3C PNG specification: https://www.w3.org/TR/png-3/
- Aseprite sprite sheet documentation:
  https://www.aseprite.org/docs/sprite-sheet/
- Pixelorama import/export documentation:
  https://www.pixelorama.org/user_manual/Import/

The implementation keeps Mechagotchi semantics in a sidecar. The PNG carries
pixels; the sidecar carries asset binding, frame rectangles, frame durations,
per-frame pixel hashes, semantic overlay hashes, and the `SLIP` profile
snapshot.

## Method

Added `labs/workshop_editor/spritesheet_sidecar_decoder.py` with:

- `render_spritesheet_frame_pixels`
- `export_spritesheet_with_sidecar`
- `extract_spritesheet_frames`
- `validate_spritesheet_sidecar_binding`
- `import_spritesheet_with_sidecar`
- `run_spritesheet_sidecar_decoder_lab`
- `write_spritesheet_sidecar_decoder_artifacts`

The lab reuses the Stage 0 static PNG encoder/decoder and renders three
8-by-8 frames into one 24-by-8 horizontal strip. Frame 0 is the base pose,
frame 1 blinks sensor pixels, and frame 2 pulses animation-anchor pixels. Each
frame is checked by rectangle, duration, pixel hash, semantic overlay hash, and
`SLIP` alignment.

Invalid probes cover a corrupt PNG signature and a frame pixel-hash mismatch.

## Results

Machine-readable artifacts:

- `data/workshop_editor/spritesheet_sidecar_decoder_stage0.json`
- `data/workshop_editor/spritesheet_sidecar_decoder_stage0/spritesheet_sidecar_decoder_stage0.json`
- `data/workshop_editor/spritesheet_sidecar_decoder_stage0/slip_lcd_seed_spritesheet.png`
- `data/workshop_editor/spritesheet_sidecar_decoder_stage0/slip_lcd_seed_spritesheet_sidecar.json`
- `data/workshop_editor/spritesheet_sidecar_decoder_stage0/slip_gray_stable_spritesheet.png`
- `data/workshop_editor/spritesheet_sidecar_decoder_stage0/slip_gray_stable_spritesheet_sidecar.json`
- `data/workshop_editor/spritesheet_sidecar_decoder_stage0/slip_amber_social_spritesheet.png`
- `data/workshop_editor/spritesheet_sidecar_decoder_stage0/slip_amber_social_spritesheet_sidecar.json`
- `data/workshop_editor/spritesheet_sidecar_decoder_data.js`

Summary:

| Metric | Result |
| --- | ---: |
| Current valid profiles covered | 3 |
| Spritesheet round-trip successes | 3 |
| Invalid probes rejected | 2 |
| Spritesheet round-trip success rate | 1.0 |
| Mean semantic fidelity | 1.0 |
| Mean frame pixel fidelity | 1.0 |
| Invalid probe rejection rate | 1.0 |
| Frame count per profile | 3 |

Closed states:

- `spritesheet_fixed_grid_frame_metadata_decoder`
- `spritesheet_sidecar_export`
- `spritesheet_sidecar_import`
- `spritesheet_frame_rect_duration_hash_validation`
- `spritesheet_sidecar_semantic_restore`

Blocked states:

- `spritesheet_packed_rotation_trim_decoder`
- `runtime_animation_playback`
- `full_project_format_coverage`
- `embedded_png_metadata_writer`
- `project_file_native_metadata_writer`
- `profile_weighted_evolution`

## Interpretation

The fixed spritesheet path is now proven for the exact Stage 0 subset:
non-interlaced 8-bit RGBA PNG, filter type 0, three equal-size frames, and a
horizontal strip layout. Frame metadata is validated from the sidecar, not
guessed from pixels.

This does not prove packed or rotated spritesheets, trimmed frames,
layer-aware editor projects, runtime animation playback, animated GIF/APNG,
Piskel project animation semantics, arbitrary Pixelorama project schemas,
complete LibreSprite/Aseprite chunk parsing, or embedded PNG metadata writing.
Vertical strips, row-major matrix sheets, padded/guttered grids, and sparse
atlas rects are now covered by
`research/experiment_reports/2026-05-13-spritesheet-layout-variant-decoder.md`.

## Verification

RED command:

```powershell
python -B -m unittest labs\workshop_editor\test_spritesheet_sidecar_decoder.py
```

Initial result:

```txt
ModuleNotFoundError: No module named 'spritesheet_sidecar_decoder'
```

GREEN command:

```powershell
python -B -m unittest labs\workshop_editor\test_spritesheet_sidecar_decoder.py
```

Result:

```txt
Ran 6 tests in 0.027s
OK
```

Artifact command:

```powershell
python -B labs\workshop_editor\spritesheet_sidecar_decoder.py --output-dir data\workshop_editor\spritesheet_sidecar_decoder_stage0
```

JSON checks:

```powershell
python -m json.tool data\workshop_editor\spritesheet_sidecar_decoder_stage0.json
python -m json.tool data\workshop_editor\spritesheet_sidecar_decoder_stage0\spritesheet_sidecar_decoder_stage0.json
```

## Decision

Adopt `spritesheet_sidecar_decoder_stage0` as the Stage 0 proof for fixed-grid
horizontal spritesheet PNG sidecar import/export.

Project-file boundary decoding is now covered by
`research/experiment_reports/2026-05-13-third-party-project-decoder-boundary.md`.
Runtime lifecycle/archive selection is now covered by
`research/experiment_reports/2026-05-13-slip-runtime-selection-policy.md`.
Next research should define offspring mutation and lineage replacement gates
before claiming profile-weighted evolution. The explicit PNG color/filter
variant subset is now covered by
`research/experiment_reports/2026-05-13-png-variant-sidecar-decoder.md`, and
the measured lifecycle/archive bridge is now covered in
`research/experiment_reports/2026-05-12-slip-lifecycle-archive-effects.md`.
