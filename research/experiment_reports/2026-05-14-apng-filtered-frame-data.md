# Experiment Report: APNG Filtered Frame Data

Date: 2026-05-14

Status: `research_apng_filtered_frame_data_no_package_code`

## Question

Can the workshop APNG research path reconstruct PNG filter-method-0 frame data
inside APNG `fdAT` chunks, including split `fdAT` streams, before claiming
broader APNG/PNG image-data conformance?

## Plan Alignment

This continues the Stage 7 workshop/editor research path in
`docs/02-research_plan.md` and the active SLIP compatibility blocker for
remaining APNG/PNG image-data conformance. It follows the partial-frame
playback matrix by testing PNG scanline reconstruction and `fdAT` frame-data
concatenation instead of only output-buffer composition.

## External Anchor

Source used:

- [W3C PNG specification, Third Edition](https://www.w3.org/TR/png-3/)

The specification defines PNG filter method 0, filter types 0 through 4,
zlib-compressed image-data streams, APNG `fdAT` sequence numbers, and the rule
that frame data is reconstructed by concatenating `fdAT` frame-data fields in
ascending sequence-number order.

## Method

Added `labs/workshop_editor/test_png_apng_filtered_frame_data.py` first and
confirmed the missing-module RED failure. Then added
`labs/workshop_editor/png_apng_filtered_frame_data.py` with:

- 8-bit RGBA APNG static-first-frame fixtures;
- partial second-frame source patches using PNG filter types 0, 1, 2, 3, and 4;
- two-`fdAT` split compressed datastreams for every animated frame;
- filter reconstruction for None, Sub, Up, Average, and Paeth;
- invalid filter-type, truncated scanline, `fdAT` sequence-gap, and missing
  `fdAT` continuation probes.

The decoder records frame pixel hashes, display hashes, filter types seen,
sequence numbers, and per-frame `fdAT` chunk counts.

## Results

Machine-readable artifacts:

- `data/workshop_editor/apng_filtered_frame_data_stage0.json`
- `data/workshop_editor/apng_filtered_frame_data_stage0/apng_filtered_frame_data_stage0.json`
- `data/workshop_editor/apng_filtered_frame_data_stage0/cases/*.png`
- `data/workshop_editor/apng_filtered_frame_data.js`

Summary:

| Metric | Result |
| --- | ---: |
| Current valid profiles covered | 3 |
| Filter families | 5 |
| Playback cases | 15 |
| Playback successes | 15 |
| Split-`fdAT` frames | 15 |
| Invalid probes | 4 |
| Invalid probes rejected | 4 |
| Case success rate | 1.0 |
| Invalid rejection rate | 1.0 |

Closed states:

- `apng_filter_method_0_frame_reconstruction`
- `apng_split_fdat_frame_data_reconstruction`
- `apng_filtered_partial_frame_source_playback`
- `apng_filtered_frame_invalid_data_rejection`

Blocked states:

- `full_apng_png_conformance`
- `live_external_editor_rewrite_validation`
- `production_import_export_carrier_selection_final_decision`
- `manual_readability_calibration`
- `package_runtime_lifecycle_integration`

## Interpretation

The APNG path now has bounded image-data evidence that goes beyond filter-0
partial-frame playback. The decoder reconstructs all five PNG filter-method-0
types for APNG frame data and proves that split `fdAT` datastream fragments are
concatenated before decompression and scanline reconstruction.

This still is not full APNG/PNG conformance. Remaining proof needs broader
APNG/PNG fixture coverage, live editor open-save preservation, and a final
metadata carrier decision.

## Verification

RED command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_png_apng_filtered_frame_data.py
```

Initial result:

```txt
ModuleNotFoundError: No module named 'png_apng_filtered_frame_data'
```

GREEN command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_png_apng_filtered_frame_data.py
```

Result:

```txt
Ran 6 tests in 0.052s
OK
```

Artifact command:

```powershell
python -B .\labs\workshop_editor\png_apng_filtered_frame_data.py
```

## Decision

Adopt `apng_filtered_frame_data_stage0` as the bounded APNG filtered
frame-data and split-`fdAT` proof.

Do not claim full APNG/PNG conformance, live external editor rewrite
validation, final production carrier selection, package runtime integration,
manual readability calibration, or profile-weighted evolution.
