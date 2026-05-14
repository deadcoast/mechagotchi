# Experiment Report: APNG Color Type Frame Data

Date: 2026-05-14

Status: `research_apng_color_type_frame_data_no_package_code`

## Question

Can the workshop APNG research path reconstruct frame pixels across the PNG
color types used by APNG before claiming broader APNG/PNG image-data
conformance?

## Plan Alignment

This continues the Stage 7 workshop/editor research path in
`docs/02-research_plan.md` and the active SLIP compatibility blocker for
remaining APNG/PNG image-data conformance. It follows the APNG partial-frame
and filtered-frame-data matrices by testing color-type reconstruction rather
than output-buffer composition or filter reconstruction alone.

## External Anchor

Source used:

- [W3C PNG specification, Third Edition](https://www.w3.org/TR/png-3/)

The specification defines PNG color types, bit-depth restrictions, PLTE/tRNS
relationships, filter method 0, `IDAT` image data, and APNG `fdAT` frame data
inheritance from the static image header.

## Method

Added `labs/workshop_editor/test_png_apng_color_type_frame_data.py` first and
confirmed the missing-module RED failure. Then added
`labs/workshop_editor/png_apng_color_type_frame_data.py` with:

- full-canvas 8-bit non-interlaced APNG fixtures;
- color type 0 greyscale frame data;
- color type 2 truecolor frame data;
- color type 3 indexed-color frame data with PLTE and tRNS;
- color type 4 greyscale-alpha frame data;
- color type 6 truecolor-alpha frame data;
- invalid missing-PLTE, invalid-tRNS, unsupported-color-type, and
  alpha-plus-tRNS conflict probes.

The decoder records frame pixel hashes, display hashes, bytes per pixel,
PLTE/tRNS presence, sequence numbers, and per-frame alpha counts.

## Results

Machine-readable artifacts:

- `data/workshop_editor/apng_color_type_frame_data_stage0.json`
- `data/workshop_editor/apng_color_type_frame_data_stage0/apng_color_type_frame_data_stage0.json`
- `data/workshop_editor/apng_color_type_frame_data_stage0/cases/*.png`
- `data/workshop_editor/apng_color_type_frame_data.js`

Summary:

| Metric | Result |
| --- | ---: |
| Current valid profiles covered | 3 |
| Color type families | 5 |
| Color types covered | 0, 2, 3, 4, 6 |
| Playback cases | 15 |
| Playback successes | 15 |
| Invalid probes | 4 |
| Invalid probes rejected | 4 |
| Case success rate | 1.0 |
| Invalid rejection rate | 1.0 |

Closed states:

- `apng_color_type_frame_reconstruction`
- `apng_palette_trns_frame_reconstruction`
- `apng_alpha_channel_frame_reconstruction`
- `apng_color_type_invalid_metadata_rejection`

Blocked states:

- `full_apng_png_conformance`
- `live_external_editor_rewrite_validation`
- `production_import_export_carrier_selection_final_decision`
- `manual_readability_calibration`
- `package_runtime_lifecycle_integration`

## Interpretation

The APNG path now has bounded image-data evidence for all five PNG color-type
families used in this lab: greyscale, truecolor, indexed-color with palette
transparency, greyscale-alpha, and truecolor-alpha. This complements the
partial-frame playback and filtered-frame-data proofs.

This still is not full APNG/PNG conformance. Remaining proof needs broader
APNG/PNG fixture coverage, live editor open-save preservation, and a final
metadata carrier decision.

## Verification

RED command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_png_apng_color_type_frame_data.py
```

Initial result:

```txt
ModuleNotFoundError: No module named 'png_apng_color_type_frame_data'
```

GREEN command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_png_apng_color_type_frame_data.py
```

Result:

```txt
Ran 6 tests in 0.055s
OK
```

Artifact command:

```powershell
python -B .\labs\workshop_editor\png_apng_color_type_frame_data.py
```

## Decision

Adopt `apng_color_type_frame_data_stage0` as the bounded APNG color-type
frame-data proof.

Do not claim full APNG/PNG conformance, live external editor rewrite
validation, final production carrier selection, package runtime integration,
manual readability calibration, or profile-weighted evolution.
