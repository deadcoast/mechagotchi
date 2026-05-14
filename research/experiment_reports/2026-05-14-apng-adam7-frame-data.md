# Experiment Report: APNG Adam7 Frame Data

Date: 2026-05-14

Status: `research_apng_adam7_frame_data_no_package_code`

## Question

Can the workshop APNG research path reconstruct Adam7-interlaced APNG frame
data across selected packed, indexed, 8-bit, and 16-bit sample models before
claiming broader APNG/PNG conformance?

## Plan Alignment

This continues the Stage 7 workshop/editor research path in
`docs/02-research_plan.md` and narrows the active APNG/PNG image-data blocker.
It connects the static PNG Adam7/deep-color proof with the non-interlaced APNG
color-type, bit-depth, and partial-sample frame-data proofs.

## External Anchor

Source used:

- [W3C PNG specification, Third Edition](https://www.w3.org/TR/png-3/)

The specification anchors Adam7 interlace pass reconstruction, PNG color-type
and bit-depth restrictions, filter method 0 reconstruction, `PLTE`/`tRNS`
indexed transparency, `IDAT` image data, and APNG `fdAT` frame-data inheritance
and sequencing.

## Method

Added `labs/workshop_editor/test_png_apng_adam7_frame_data.py` first and
confirmed the missing-module RED failure. Then added
`labs/workshop_editor/png_apng_adam7_frame_data.py` with:

- full-canvas APNG fixtures whose IHDR uses Adam7 interlace method 1;
- default first frames carried by `IDAT`;
- second animation frames split across two `fdAT` chunks;
- selected color types 0, 2, 3, 4, and 6;
- selected bit depths 1, 4, 8, and 16;
- 4-bit indexed-color `PLTE`/`tRNS` transparency;
- 16-bit greyscale-alpha and truecolor-alpha APNG over-blend cases;
- filter method 0 filter types 0..4 across Adam7 reduced-image scanlines;
- invalid non-Adam7 interlace, invalid bit-depth/color-type, truncated Adam7
  scanline, invalid filter byte, and `fdAT` sequence-gap probes.

The decoder reconstructs each APNG frame through the existing Adam7/deep-color
PNG path, then records frame hashes, display hashes, final canvas hashes,
sequence numbers, split-`fdAT` counts, filter types, pass order, pass
summaries, transparency counts, and partial-alpha counts.

## Results

Machine-readable artifacts:

- `data/workshop_editor/apng_adam7_frame_data_stage0.json`
- `data/workshop_editor/apng_adam7_frame_data_stage0/apng_adam7_frame_data_stage0.json`
- `data/workshop_editor/apng_adam7_frame_data_stage0/cases/*.png`
- `data/workshop_editor/apng_adam7_frame_data.js`

Summary:

| Metric | Result |
| --- | ---: |
| Current valid profiles covered | 3 |
| Case families | 6 |
| Color types covered | 0, 2, 3, 4, 6 |
| Bit depths covered | 1, 4, 8, 16 |
| Adam7 pass count | 7 |
| APNG Adam7 cases | 18 |
| APNG Adam7 successes | 18 |
| Split-`fdAT` second frames | 18 |
| Alpha-over cases | 6 |
| Invalid probes | 5 |
| Invalid probes rejected | 5 |
| Case success ratio | 1.0 |
| Invalid rejection ratio | 1.0 |

Closed states:

- `apng_adam7_frame_reconstruction`
- `apng_adam7_pass_manifest_reconstruction`
- `apng_adam7_deep_sample_reconstruction`
- `apng_adam7_split_fdat_reconstruction`
- `apng_adam7_invalid_probe_rejection`

Blocked states:

- `full_apng_png_conformance`
- `live_external_editor_rewrite_validation`
- `production_import_export_carrier_selection_final_decision`
- `manual_readability_calibration`
- `package_runtime_lifecycle_integration`

## Interpretation

The APNG image-data evidence now covers Adam7 pass reconstruction for APNG
frame data, including selected low-bit, indexed, 8-bit, and 16-bit sample
models. The proof records seven reduced-image pass manifests per frame,
filter method 0 reconstruction over Adam7 pass rows, split `fdAT`
reconstruction, indexed transparency, alpha-over composition, display hashes,
and final canvas hashes.

This still is not full APNG/PNG conformance. It does not cover every legal PNG
bit-depth/color-type combination in Adam7 APNG frames, partial Adam7 APNG
regions, gamma/color-management behavior, live external editor open-save
preservation, or a final production carrier decision.

## Verification

RED command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_png_apng_adam7_frame_data.py
```

Initial result:

```txt
ModuleNotFoundError: No module named 'png_apng_adam7_frame_data'
```

GREEN command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_png_apng_adam7_frame_data.py
```

Result:

```txt
Ran 5 tests in 0.083s
OK
```

Artifact command:

```powershell
python -B .\labs\workshop_editor\png_apng_adam7_frame_data.py
```

## Decision

Adopt `apng_adam7_frame_data_stage0` as the bounded APNG Adam7 frame-data
proof.

Do not claim full APNG/PNG conformance, live external editor rewrite
validation, final production carrier selection, package runtime integration,
manual readability calibration, or profile-weighted evolution.
