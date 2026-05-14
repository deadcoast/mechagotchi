# Experiment Report: Spritesheet Packed Runtime Decoder

Date: 2026-05-13

Status: `research_spritesheet_packed_runtime_decoder_no_package_code`

## Question

Can Mechagotchi close the Stage 0 packed trim/rotation spritesheet gap and
prove a deterministic sidecar runtime playback model without claiming full
project-format coverage, native metadata writing, or package runtime
integration?

## Plan Alignment

This continues the Stage 7 workshop/editor track in
`docs/02-research_plan.md`. The earlier spritesheet labs covered fixed
horizontal strips plus vertical, matrix, padded, and sparse unrotated
full-frame layouts. This experiment tests sidecar-described trim, one
90-degree packed frame rotation, canonical 8x8 frame reconstruction, and
looped frame-duration playback sampling. No `packages/` code was created.

## External Anchors

Sources used:

- Aseprite sprite-sheet docs: https://www.aseprite.org/docs/sprite-sheet/
- Aseprite CLI docs: https://aseprite.com/docs/cli/
- W3C PNG specification: https://www.w3.org/TR/png-3/

Aseprite's docs frame sprite sheets as image carriers with frame layout,
padding, tags, texture atlases, and import/export workflows. Its CLI surface
includes packed sheet type, packing, trimming, sheet dimensions, and JSON data
export options. PNG remains the byte carrier. Mechagotchi semantics still come
from the sidecar.

## Method

Added `labs/workshop_editor/test_spritesheet_packed_runtime_decoder.py` first
and watched it fail on the missing module. Then added
`labs/workshop_editor/spritesheet_packed_runtime_decoder.py` with:

- `export_packed_runtime_spritesheet_with_sidecar`
- `import_packed_runtime_spritesheet_with_sidecar`
- `validate_packed_runtime_sidecar_binding`
- `reconstruct_packed_runtime_frames`
- `build_runtime_playback_timeline`
- `run_spritesheet_packed_runtime_decoder_lab`
- `write_spritesheet_packed_runtime_decoder_artifacts`

The packed atlas uses three generated frames per current valid profile:

| Frame | Transform | Validation target |
| --- | --- | --- |
| `base_pose` | untrimmed 8x8 | canonical reference frame |
| `sensor_blink` | trimmed and rotated 90 degrees clockwise | rotation undo and trim paste |
| `anchor_pulse` | trimmed, unrotated | trim paste |

Import validates PNG bytes, asset binding, sheet dimensions, frame geometry,
non-overlap, transform dimensions, per-frame packed hashes, reconstructed
canonical hashes, restored grid validity, `SLIP` alignment, semantic fidelity,
and runtime playback samples.

Invalid probes cover unsupported rotation, trim outside source bounds,
canonical frame hash mismatch, and invalid runtime frame duration.

## Results

Machine-readable artifacts:

- `data/workshop_editor/spritesheet_packed_runtime_decoder_stage0.json`
- `data/workshop_editor/spritesheet_packed_runtime_decoder_stage0/spritesheet_packed_runtime_decoder_stage0.json`
- `data/workshop_editor/spritesheet_packed_runtime_decoder_stage0/*.png`
- `data/workshop_editor/spritesheet_packed_runtime_decoder_stage0/*_sidecar.json`
- `data/workshop_editor/spritesheet_packed_runtime_decoder_data.js`

Summary:

| Metric | Result |
| --- | ---: |
| Current valid profiles covered | 3 |
| Packed round-trip successes | 3 |
| Invalid probes rejected | 4 |
| Packed round-trip success rate | 1.0 |
| Mean semantic fidelity | 1.0 |
| Mean reconstructed frame fidelity | 1.0 |
| Mean runtime frame fidelity | 1.0 |
| Invalid probe rejection rate | 1.0 |

Closed states:

- `spritesheet_packed_rotation_trim_decoder`
- `runtime_animation_playback_sidecar_model`
- `spritesheet_packed_runtime_sidecar_export`
- `spritesheet_packed_runtime_sidecar_import`
- `spritesheet_packed_frame_hash_validation`
- `spritesheet_packed_sidecar_semantic_restore`

Blocked states:

- `Adam7/APNG/full PNG conformance`
- `full project-format coverage`
- `arbitrary Aseprite project schema coverage`
- `live external editor rewrite validation`
- `package runtime lifecycle integration`
- `manual readability calibration`
- `profile-weighted evolution`
- `community profile packs`

## Interpretation

Packed trim/rotation handling is now proven for the Stage 0 sidecar subset:
one explicitly described 90-degree clockwise rotation, trim rectangles within
an 8x8 source frame, canonical reconstruction over the profile background, and
hash-checked playback samples.

This is not a claim that arbitrary third-party atlas packing, tag/layer
semantics, full editor-native project files, embedded metadata, or production
runtime rendering are solved. The runtime proof is a deterministic sidecar
playback model that selects frames by duration boundaries.

## Verification

RED command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_spritesheet_packed_runtime_decoder.py
```

Initial result:

```txt
ModuleNotFoundError: No module named 'spritesheet_packed_runtime_decoder'
```

GREEN command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_spritesheet_packed_runtime_decoder.py
```

Result:

```txt
Ran 6 tests in 0.038s
OK
```

Artifact command:

```powershell
python -B .\labs\workshop_editor\spritesheet_packed_runtime_decoder.py
```

## Decision

Adopt `spritesheet_packed_runtime_decoder_stage0` as the Stage 0 proof for
sidecar-described packed trim/rotation frame reconstruction and deterministic
runtime playback sampling.

PNG `tEXt` embedded sidecar writing is now covered by
`research/experiment_reports/2026-05-13-png-embedded-sidecar-writer.md` for
the Stage 0 subset. Next workshop research should keep full project-format
coverage, arbitrary Aseprite project schema coverage, live external editor rewrite
preservation, arbitrary atlas packing, tags/layers, and production renderer
playback blocked until each has its own explicit test surface.
