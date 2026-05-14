# Experiment Report: APNG Bit Depth Frame Data

Date: 2026-05-14

Status: `research_apng_bit_depth_frame_data_no_package_code`

## Question

Can the workshop APNG research path reconstruct packed 1/2/4-bit and 16-bit
frame image data before claiming broader APNG/PNG conformance?

## Plan Alignment

This continues the Stage 7 workshop/editor research path in
`docs/02-research_plan.md` and the active compatibility blocker for remaining
APNG/PNG image-data conformance. It follows the static PNG deep-color proof
and the 8-bit APNG color-type proof by testing APNG frame data at non-8-bit
and 16-bit depths.

## External Anchor

Source used:

- [W3C PNG specification, Third Edition](https://www.w3.org/TR/png-3/)

The specification anchors PNG bit-depth restrictions by color type, packed
sample scanline sizing, filter method 0 reconstruction, `PLTE`/`tRNS`,
`IDAT` image data, and APNG `fdAT` frame-data inheritance and sequencing.

## Method

Added `labs/workshop_editor/test_png_apng_bit_depth_frame_data.py` first and
confirmed the missing-module RED failure. Then added
`labs/workshop_editor/png_apng_bit_depth_frame_data.py` with:

- full-canvas non-interlaced APNG fixtures;
- packed greyscale frame data at 1, 2, and 4 bits;
- packed indexed-color frame data at 1, 2, and 4 bits with `PLTE`/`tRNS`;
- 16-bit greyscale, truecolor, greyscale-alpha, and truecolor-alpha frame data;
- filter method 0 filter types 0..4 on every frame;
- two-`fdAT` split continuation data on the second frame;
- invalid bit-depth/color-type, truncated scanline, invalid filter byte, and
  `fdAT` sequence-gap probes.

The decoder records frame pixel hashes, display hashes, scanline byte lengths,
filter byte widths, per-frame filter types, sequence numbers, split-`fdAT`
counts, and alpha counts.

## Results

Machine-readable artifacts:

- `data/workshop_editor/apng_bit_depth_frame_data_stage0.json`
- `data/workshop_editor/apng_bit_depth_frame_data_stage0/apng_bit_depth_frame_data_stage0.json`
- `data/workshop_editor/apng_bit_depth_frame_data_stage0/cases/*.png`
- `data/workshop_editor/apng_bit_depth_frame_data.js`

Summary:

| Metric | Result |
| --- | ---: |
| Current valid profiles covered | 3 |
| Case families | 10 |
| Color types covered | 0, 2, 3, 4, 6 |
| Bit depths covered | 1, 2, 4, 16 |
| Frame-data cases | 30 |
| Frame-data successes | 30 |
| Split-`fdAT` second frames | 30 |
| Invalid probes | 4 |
| Invalid probes rejected | 4 |
| Case success rate | 1.0 |
| Invalid rejection rate | 1.0 |

Closed states:

- `apng_low_bit_packed_frame_reconstruction`
- `apng_16bit_frame_reconstruction`
- `apng_deep_color_filter_frame_reconstruction`
- `apng_split_fdat_deep_sample_reconstruction`
- `apng_bit_depth_invalid_probe_rejection`

Blocked states:

- `full_apng_png_conformance`
- `live_external_editor_rewrite_validation`
- `production_import_export_carrier_selection_final_decision`
- `manual_readability_calibration`
- `package_runtime_lifecycle_integration`

## Interpretation

The APNG path now has bounded image-data evidence beyond 8-bit color-type
coverage. This proof specifically covers packed low-bit samples, 16-bit sample
widths, per-row filter reconstruction, palette transparency for indexed
low-bit APNG, and split `fdAT` continuation reconstruction.

This still is not full APNG/PNG conformance. Remaining proof needs broader
image-data fixtures, live editor open-save preservation, and a final metadata
carrier decision.

## Verification

RED command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_png_apng_bit_depth_frame_data.py
```

Initial result:

```txt
ModuleNotFoundError: No module named 'png_apng_bit_depth_frame_data'
```

GREEN command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_png_apng_bit_depth_frame_data.py
```

Result:

```txt
Ran 5 tests in 0.076s
OK
```

Artifact command:

```powershell
python -B .\labs\workshop_editor\png_apng_bit_depth_frame_data.py
```

## Decision

Adopt `apng_bit_depth_frame_data_stage0` as the bounded APNG low-bit and
16-bit frame-data proof.

Do not claim full APNG/PNG conformance, live external editor rewrite
validation, final production carrier selection, package runtime integration,
manual readability calibration, or profile-weighted evolution.
