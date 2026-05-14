# Experiment Report: PNG/APNG Zlib Header Policy

Date: 2026-05-14

Status: `research_png_apng_zlib_header_policy_no_package_code`

## Question

Can the workshop PNG/APNG research path reconstruct identical pixels when valid
zlib CMF/FLG window headers vary, and can it reject preset-dictionary and
malformed zlib headers before semantic restore?

## Plan Alignment

This continues the Stage 7 workshop/editor research path in
`docs/02-research_plan.md` and narrows the remaining APNG/PNG image-data
conformance blocker. It does not start package/runtime work.

## External Anchors

Sources used:

- [W3C PNG specification, Third Edition](https://www.w3.org/TR/png-3/)
- [RFC 1950: ZLIB Compressed Data Format Specification](https://www.rfc-editor.org/rfc/rfc1950)
- [RFC 1951: DEFLATE Compressed Data Format Specification](https://www.rfc-editor.org/rfc/rfc1951)

The PNG specification anchors compression method 0, IDAT image-data storage,
APNG fdAT frame-data inheritance from IDAT, and APNG sequence-number
validation. RFC 1950 anchors CMF/FLG, CM=8, CINFO window size, FCHECK
divisibility, FDICT preset-dictionary flag, and Adler-32 handling. RFC 1951
anchors the deflate payload context behind zlib method 8 streams.

## Method

Added `labs/workshop_editor/test_png_apng_zlib_header_policy.py` first and
confirmed the missing-module RED failure. Then added
`labs/workshop_editor/png_apng_zlib_header_policy.py` with:

- three static PNG IDAT zlib window-header families;
- three APNG second-frame fdAT zlib window-header families;
- valid CINFO values 1, 4, and 7, representing 512-byte, 4096-byte, and
  32768-byte windows;
- FDICT=false validation for all valid cases;
- pixel/hash validation through the existing static PNG deep-color decoder;
- APNG final-output hash validation through the existing filtered frame-data
  decoder;
- raw scanline hash validation to prove the image-data payload remains
  unchanged across header-window variants;
- invalid PNG/APNG FDICT preset-dictionary probes;
- invalid PNG/APNG CMF/FLG check probes;
- invalid PNG reserved compression method and APNG too-large CINFO probes.

## Results

Machine-readable artifacts:

- `data/workshop_editor/png_apng_zlib_header_policy_stage0.json`
- `data/workshop_editor/png_apng_zlib_header_policy_stage0/png_apng_zlib_header_policy_stage0.json`
- `data/workshop_editor/png_apng_zlib_header_policy_stage0/cases/*.png`
- `data/workshop_editor/png_apng_zlib_header_policy.js`

Summary:

| Metric | Result |
| --- | ---: |
| Current valid profiles covered | 3 |
| Case families | 6 |
| Total cases | 18 |
| Static PNG IDAT cases | 9 |
| APNG fdAT cases | 9 |
| Zlib CINFO values covered | 1, 4, 7 |
| Zlib window sizes covered | 512, 4096, 32768 |
| FDICT=false valid cases | 18 |
| CMF/FLG check passed valid cases | 18 |
| Case successes | 18 |
| Invalid probes | 6 |
| Invalid probes rejected | 6 |
| Case success ratio | 1.0 |
| Invalid rejection ratio | 1.0 |

Closed states:

- `png_zlib_window_header_reconstruction`
- `apng_fdat_zlib_window_header_reconstruction`
- `png_apng_fdict_rejection`
- `png_apng_zlib_cmf_flg_error_rejection`
- `png_apng_zlib_header_policy_invalid_probe_rejection`

Blocked states:

- `full_apng_png_conformance`
- `live_external_editor_rewrite_validation`
- `production_import_export_carrier_selection_final_decision`
- `manual_readability_calibration`
- `package_runtime_lifecycle_integration`

## Interpretation

The image-data evidence now proves selected legal zlib header windows for both
static PNG IDAT and APNG fdAT streams while preserving decoded pixels and APNG
playback. The invalid probes also close the previously explicit
preset-dictionary gap by using real FDICT streams and proving the current
decoder path rejects them before semantic restore.

This still is not full APNG/PNG conformance. It does not enumerate every
CMF/FLG/FLEVEL combination, every possible DEFLATE payload, gamma/color
management behavior, live external editor open-save preservation, or final
production carrier choice.

## Verification

RED command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_png_apng_zlib_header_policy.py
```

Initial result:

```txt
ModuleNotFoundError: No module named 'png_apng_zlib_header_policy'
```

GREEN command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_png_apng_zlib_header_policy.py
```

Result:

```txt
Ran 5 tests in 0.036s
OK
```

Artifact command:

```powershell
python -B .\labs\workshop_editor\png_apng_zlib_header_policy.py
```

## Decision

Adopt `png_apng_zlib_header_policy_stage0` as the bounded PNG/APNG zlib header
policy and FDICT rejection proof.

Do not claim full APNG/PNG conformance, live external editor rewrite
validation, final production carrier selection, package runtime integration,
manual readability calibration, or profile-weighted evolution.
