# Experiment Report: APNG Partial Frame Playback

Date: 2026-05-14

Status: `research_apng_partial_frame_playback_no_package_code`

## Question

Can the workshop APNG research path correctly compose partial frames with
offsets, source/over blending, and dispose none/background/previous behavior
before claiming broader APNG/PNG image-data conformance?

## Plan Alignment

This continues the Stage 7 workshop/editor research path in
`docs/02-research_plan.md` and the active SLIP compatibility blocker for
remaining APNG/PNG image-data conformance. It follows the chunk-order
conformance matrix by testing APNG output-buffer behavior rather than chunk
ordering alone.

## External Anchor

Source used:

- [W3C PNG specification, Third Edition](https://www.w3.org/TR/png-3/)

The specification defines APNG output-buffer initialization, frame bounds,
frame offsets, disposal operations, and source/over blend operations. This lab
implements deterministic fixtures against those rules.

## Method

Added `labs/workshop_editor/test_png_apng_partial_frame_playback.py` first and
confirmed the missing-module RED failure. Then added
`labs/workshop_editor/png_apng_partial_frame_playback.py` with:

- a static-first-frame APNG encoder for generated current-profile grids;
- partial source-blend dispose-none patch playback;
- partial alpha-over dispose-none patch playback;
- background-disposal playback;
- previous-disposal playback;
- invalid out-of-bounds, dispose-op, blend-op, missing-default-IDAT, and
  missing-frame-data probes.

The decoder records displayed output hashes and after-disposal output hashes so
the proof distinguishes drawing from disposal state.

## Results

Machine-readable artifacts:

- `data/workshop_editor/apng_partial_frame_playback_stage0.json`
- `data/workshop_editor/apng_partial_frame_playback_stage0/apng_partial_frame_playback_stage0.json`
- `data/workshop_editor/apng_partial_frame_playback_stage0/cases/*.png`
- `data/workshop_editor/apng_partial_frame_playback_data.js`

Summary:

| Metric | Result |
| --- | ---: |
| Current valid profiles covered | 3 |
| Playback scenario families | 4 |
| Playback cases | 12 |
| Playback successes | 12 |
| Invalid probes | 5 |
| Invalid probes rejected | 5 |
| Playback success rate | 1.0 |
| Invalid rejection rate | 1.0 |

Closed states:

- `apng_partial_frame_offset_playback`
- `apng_blend_source_over_playback`
- `apng_dispose_background_previous_playback`
- `apng_partial_frame_invalid_control_rejection`

Blocked states:

- `full_apng_png_conformance`
- `live_external_editor_rewrite_validation`
- `production_import_export_carrier_selection_final_decision`
- `manual_readability_calibration`
- `package_runtime_lifecycle_integration`

## Interpretation

The APNG path now has bounded image-data playback evidence beyond full-canvas
source frames. Source and over blending produce distinct display hashes.
Background disposal clears the affected frame region before the next frame.
Previous disposal restores the output buffer that existed before the frame.

This still is not full APNG/PNG conformance. Remaining proof needs broader
image-data fixtures, live editor open-save preservation, and a final metadata
carrier decision.

## Verification

RED command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_png_apng_partial_frame_playback.py
```

Initial result:

```txt
ModuleNotFoundError: No module named 'png_apng_partial_frame_playback'
```

GREEN command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_png_apng_partial_frame_playback.py
```

Result:

```txt
Ran 6 tests in 0.043s
OK
```

Artifact command:

```powershell
python -B .\labs\workshop_editor\png_apng_partial_frame_playback.py
```

## Decision

Adopt `apng_partial_frame_playback_stage0` as the bounded APNG partial-frame
playback proof.

Do not claim full APNG/PNG conformance, live external editor rewrite
validation, final production carrier selection, package runtime integration,
manual readability calibration, or profile-weighted evolution.
