# Experiment Report: APNG Partial Adam7 Frame Data

Date: 2026-05-14

Status: `research_apng_partial_adam7_frame_data_no_package_code`

## Question

Can the workshop APNG research path reconstruct Adam7-interlaced frame data
when the APNG frame is a non-zero-offset partial region?

## Plan Alignment

This continues the Stage 7 workshop/editor research path in
`docs/02-research_plan.md` and narrows the active APNG/PNG image-data blocker.
It connects the non-interlaced partial-frame sample proof with the full-canvas
APNG Adam7 frame-data proof.

## External Anchor

Source used:

- [W3C PNG specification, Third Edition](https://www.w3.org/TR/png-3/)

The specification anchors APNG `fcTL` frame offsets, output-buffer
composition, source/over blend behavior, `fdAT` sequence inheritance, Adam7
pass reconstruction, PNG filter method 0 reconstruction, and selected
packed/indexed/8-bit/16-bit sample decoding.

## Method

Added `labs/workshop_editor/test_png_apng_partial_adam7_frame_data.py` first
and confirmed the missing-module RED failure. Then added
`labs/workshop_editor/png_apng_partial_adam7_frame_data.py` with:

- full-canvas Adam7 default frames carried by `IDAT`;
- non-zero 6x6 second-frame regions at `x_offset = 1`, `y_offset = 1`;
- second frames encoded through Adam7 interlace method 1 and split across two
  `fdAT` chunks;
- selected color types 0, 2, 3, 4, and 6;
- selected bit depths 1, 4, 8, and 16;
- 4-bit indexed-color `PLTE`/`tRNS` transparency;
- 16-bit greyscale-alpha and truecolor-alpha APNG over-blend patch cases;
- filter method 0 filter types 0..4 across Adam7 reduced-image scanlines;
- invalid non-Adam7 interlace, out-of-bounds partial frame, invalid
  bit-depth/color-type, truncated partial Adam7 scanline, invalid filter byte,
  and `fdAT` sequence-gap probes.

The 6x6 patch size is deliberate: with the chosen offset it fits inside the
8x8 canvas while still producing non-empty reduced images for all seven Adam7
passes.

## Results

Machine-readable artifacts:

- `data/workshop_editor/apng_partial_adam7_frame_data_stage0.json`
- `data/workshop_editor/apng_partial_adam7_frame_data_stage0/apng_partial_adam7_frame_data_stage0.json`
- `data/workshop_editor/apng_partial_adam7_frame_data_stage0/cases/*.png`
- `data/workshop_editor/apng_partial_adam7_frame_data.js`

Summary:

| Metric | Result |
| --- | ---: |
| Current valid profiles covered | 3 |
| Case families | 6 |
| Color types covered | 0, 2, 3, 4, 6 |
| Bit depths covered | 1, 4, 8, 16 |
| Adam7 pass count | 7 |
| Partial Adam7 cases | 18 |
| Partial Adam7 successes | 18 |
| Non-zero-offset Adam7 frames | 18 |
| Split-`fdAT` second frames | 18 |
| Alpha-over cases | 6 |
| Invalid probes | 6 |
| Invalid probes rejected | 6 |
| Case success ratio | 1.0 |
| Invalid rejection ratio | 1.0 |

Closed states:

- `apng_partial_adam7_offset_reconstruction`
- `apng_partial_adam7_pass_manifest_reconstruction`
- `apng_partial_adam7_deep_sample_reconstruction`
- `apng_partial_adam7_split_fdat_reconstruction`
- `apng_partial_adam7_invalid_probe_rejection`

Blocked states:

- `full_apng_png_conformance`
- `live_external_editor_rewrite_validation`
- `production_import_export_carrier_selection_final_decision`
- `manual_readability_calibration`
- `package_runtime_lifecycle_integration`

## Interpretation

The APNG image-data evidence now covers the intersection of partial-frame
offset composition and Adam7 pass reconstruction. The proof records non-zero
frame offsets, seven reduced-image pass manifests for each second-frame patch,
filter method 0 reconstruction over Adam7 pass rows, split `fdAT`
reconstruction, indexed transparency, alpha-over composition, display hashes,
and final canvas hashes.

This still is not full APNG/PNG conformance. It does not cover every legal PNG
bit-depth/color-type combination in partial Adam7 APNG regions,
gamma/color-management behavior, every ancillary chunk, live external editor
open-save preservation, or a final production carrier decision.

## Verification

RED command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_png_apng_partial_adam7_frame_data.py
```

Initial result:

```txt
ModuleNotFoundError: No module named 'png_apng_partial_adam7_frame_data'
```

GREEN command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_png_apng_partial_adam7_frame_data.py
```

Result:

```txt
Ran 5 tests in 0.073s
OK
```

Artifact command:

```powershell
python -B .\labs\workshop_editor\png_apng_partial_adam7_frame_data.py
```

## Decision

Adopt `apng_partial_adam7_frame_data_stage0` as the bounded APNG partial
Adam7 frame-data proof.

Do not claim full APNG/PNG conformance, live external editor rewrite
validation, final production carrier selection, package runtime integration,
manual readability calibration, or profile-weighted evolution.
