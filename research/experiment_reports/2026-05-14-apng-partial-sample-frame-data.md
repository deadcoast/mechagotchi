# Experiment Report: APNG Partial Sample Frame Data

Date: 2026-05-14

Status: `research_apng_partial_sample_frame_data_no_package_code`

## Question

Can the workshop APNG research path reconstruct non-8-bit and indexed sample
data when the frame is a partial region with a non-zero APNG offset?

## Plan Alignment

This continues the Stage 7 workshop/editor research path in
`docs/02-research_plan.md` and narrows the active APNG/PNG image-data blocker.
It connects the existing partial-frame playback proof, which was 8-bit RGBA
only, with the bit-depth/color-type frame-data proofs, which were full-canvas
only.

## External Anchor

Source used:

- [W3C PNG specification, Third Edition](https://www.w3.org/TR/png-3/)

The specification anchors APNG frame offsets, source/over blend behavior,
`fdAT` sequence inheritance, packed sample scanline sizing, PNG filter method
0 reconstruction, and indexed-color `PLTE`/`tRNS` transparency.

## Method

Added `labs/workshop_editor/test_png_apng_partial_sample_frame_data.py` first
and confirmed the missing-module RED failure. Then added
`labs/workshop_editor/png_apng_partial_sample_frame_data.py` with:

- default full-canvas static APNG frames plus second-frame partial regions;
- non-zero `x_offset` and `y_offset` reconstruction on every second frame;
- 1-bit greyscale partial source-blend patches;
- 4-bit indexed-color partial source-blend patches with `PLTE`/`tRNS`;
- 16-bit truecolor partial source-blend patches;
- 16-bit greyscale-alpha and truecolor-alpha partial alpha-over patches;
- filter method 0 filter types 0..4 on patch scanlines;
- two-`fdAT` split continuation data on each partial second frame;
- invalid out-of-bounds frame, invalid bit-depth/color-type, truncated
  partial scanline, invalid filter byte, and `fdAT` sequence-gap probes.

## Results

Machine-readable artifacts:

- `data/workshop_editor/apng_partial_sample_frame_data_stage0.json`
- `data/workshop_editor/apng_partial_sample_frame_data_stage0/apng_partial_sample_frame_data_stage0.json`
- `data/workshop_editor/apng_partial_sample_frame_data_stage0/cases/*.png`
- `data/workshop_editor/apng_partial_sample_frame_data.js`

Summary:

| Metric | Result |
| --- | ---: |
| Current valid profiles covered | 3 |
| Case families | 5 |
| Color types covered | 0, 2, 3, 4, 6 |
| Bit depths covered | 1, 4, 16 |
| Partial-frame cases | 15 |
| Partial-frame successes | 15 |
| Split-`fdAT` partial frames | 15 |
| Alpha-over partial cases | 6 |
| Invalid probes | 5 |
| Invalid probes rejected | 5 |
| Case success ratio | 1.0 |
| Invalid rejection ratio | 1.0 |

Closed states:

- `apng_partial_sample_offset_reconstruction`
- `apng_partial_low_bit_region_reconstruction`
- `apng_partial_16bit_region_reconstruction`
- `apng_partial_alpha_over_sample_reconstruction`
- `apng_partial_sample_invalid_probe_rejection`

Blocked states:

- `full_apng_png_conformance`
- `live_external_editor_rewrite_validation`
- `production_import_export_carrier_selection_final_decision`
- `manual_readability_calibration`
- `package_runtime_lifecycle_integration`

## Interpretation

The APNG image-data evidence now covers the intersection of partial-frame
composition and non-8-bit or indexed sample decoding. The proof records real
partial frame offsets, patch scanline byte lengths, filter types, split
`fdAT` reconstruction, palette transparency, alpha-over composition, display
hashes, and final canvas hashes.

This still is not full APNG/PNG conformance. It does not cover every legal PNG
bit-depth/color-type combination in partial APNG regions, Adam7 APNG frames,
gamma/color-management behavior, live external editor open-save preservation,
or a final production carrier decision.

## Verification

RED command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_png_apng_partial_sample_frame_data.py
```

Initial result:

```txt
ModuleNotFoundError: No module named 'png_apng_partial_sample_frame_data'
```

GREEN command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_png_apng_partial_sample_frame_data.py
```

Result:

```txt
Ran 5 tests in 0.059s
OK
```

Artifact command:

```powershell
python .\labs\workshop_editor\png_apng_partial_sample_frame_data.py
```

## Decision

Adopt `apng_partial_sample_frame_data_stage0` as the bounded APNG partial
sample-frame proof.

Do not claim full APNG/PNG conformance, live external editor rewrite
validation, final production carrier selection, package runtime integration,
manual readability calibration, or profile-weighted evolution.
