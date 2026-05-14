# Experiment Report: PNG/APNG Image Data Chunking

Date: 2026-05-14

Status: `research_png_apng_image_data_chunking_no_package_code`

## Question

Can the workshop PNG/APNG research path reconstruct identical pixels when the
same compressed image datastream is split across different IDAT and fdAT chunk
boundaries?

## Plan Alignment

This continues the Stage 7 workshop/editor research path in
`docs/02-research_plan.md` and narrows the remaining APNG/PNG image-data
conformance blocker. It does not start package/runtime work.

## External Anchor

Source used:

- [W3C PNG specification, Third Edition](https://www.w3.org/TR/png-3/)

The specification anchors PNG IDAT image-data concatenation, APNG fdAT
`frame_data` concatenation in sequence-number order, zlib compression method 0,
filter-byte scanline payloads, and the fact that APNG fdAT `frame_data` fields
may be empty even though the fdAT chunk itself carries a sequence number.

## Method

Added `labs/workshop_editor/test_png_apng_image_data_chunking.py` first and
confirmed the missing-module RED failure. Then added
`labs/workshop_editor/png_apng_image_data_chunking.py` with:

- three static PNG IDAT segmentation families;
- three APNG second-frame fdAT segmentation families;
- leading empty IDAT data fields;
- leading empty APNG fdAT `frame_data` fields;
- zlib-header splits across chunk boundaries;
- Adler-32 trailer splits across chunk boundaries;
- pixel/hash validation through the existing static PNG deep-color decoder;
- APNG final-output hash validation through the existing filtered frame-data
  decoder;
- invalid nonconsecutive IDAT, corrupt IDAT, missing IDAT, missing fdAT, fdAT
  sequence-gap, and corrupt fdAT probes.

## Results

Machine-readable artifacts:

- `data/workshop_editor/png_apng_image_data_chunking_stage0.json`
- `data/workshop_editor/png_apng_image_data_chunking_stage0/png_apng_image_data_chunking_stage0.json`
- `data/workshop_editor/png_apng_image_data_chunking_stage0/cases/*.png`
- `data/workshop_editor/png_apng_image_data_chunking.js`

Summary:

| Metric | Result |
| --- | ---: |
| Current valid profiles covered | 3 |
| Case families | 6 |
| Total cases | 18 |
| Static PNG IDAT cases | 9 |
| APNG fdAT cases | 9 |
| Zero-length data chunk cases | 6 |
| Zlib-header split cases | 6 |
| Adler-32 split cases | 6 |
| Case successes | 18 |
| Invalid probes | 6 |
| Invalid probes rejected | 6 |
| Case success ratio | 1.0 |
| Invalid rejection ratio | 1.0 |

Closed states:

- `png_idat_arbitrary_boundary_reconstruction`
- `png_idat_zero_length_data_field_reconstruction`
- `apng_fdat_arbitrary_boundary_reconstruction`
- `apng_fdat_zero_length_frame_data_reconstruction`
- `png_apng_image_data_chunking_invalid_probe_rejection`

Blocked states:

- `full_apng_png_conformance`
- `live_external_editor_rewrite_validation`
- `production_import_export_carrier_selection_final_decision`
- `manual_readability_calibration`
- `package_runtime_lifecycle_integration`

## Interpretation

The image-data evidence now proves that selected static PNG and APNG carriers
survive arbitrary compressed-datastream chunk boundaries without changing
decoded pixels or final APNG playback hashes. This closes one concrete
conformance gap left by earlier frame-data labs: chunk boundaries are tested as
transport segmentation, not as image semantics.

This still is not full APNG/PNG conformance. It does not broaden color types,
bit depths, interlace behavior, gamma/color-management behavior, ancillary
chunk policy, live external editor open-save preservation, or final production
carrier selection.

## Verification

RED command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_png_apng_image_data_chunking.py
```

Initial result:

```txt
ModuleNotFoundError: No module named 'png_apng_image_data_chunking'
```

GREEN command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_png_apng_image_data_chunking.py
```

Result:

```txt
Ran 5 tests in 0.052s
OK
```

Artifact command:

```powershell
python -B .\labs\workshop_editor\png_apng_image_data_chunking.py
```

## Decision

Adopt `png_apng_image_data_chunking_stage0` as the bounded PNG/APNG
image-data chunk-boundary proof.

Do not claim full APNG/PNG conformance, live external editor rewrite
validation, final production carrier selection, package runtime integration,
manual readability calibration, or profile-weighted evolution.
