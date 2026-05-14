# Experiment Report: PNG/APNG Zlib Compression Matrix

Date: 2026-05-14

Status: `research_png_apng_zlib_compression_no_package_code`

## Question

Can the workshop PNG/APNG research path reconstruct identical pixels when the
same uncompressed scanline payload is encoded with selected valid zlib-wrapped
DEFLATE variants in static PNG IDAT and APNG fdAT image data?

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
validation. RFC 1950 anchors the zlib CMF/FLG header, CM=8 deflate method,
FDICT/Adler-32 handling, and decompressor error expectations. RFC 1951 anchors
DEFLATE block families including stored blocks, fixed Huffman blocks, and
dynamic/strategy-dependent compressed streams.

## Method

Added `labs/workshop_editor/test_png_apng_zlib_compression_matrix.py` first and
confirmed the missing-module RED failure. Then added
`labs/workshop_editor/png_apng_zlib_compression_matrix.py` with:

- three static PNG IDAT zlib/DEFLATE encoding families;
- three APNG second-frame fdAT zlib/DEFLATE encoding families;
- level-0 stored-block zlib streams;
- fixed-Huffman zlib streams;
- filtered and RLE zlib strategy streams;
- pixel/hash validation through the existing static PNG deep-color decoder;
- APNG final-output hash validation through the existing filtered frame-data
  decoder;
- raw scanline hash validation to prove the image-data payload remains
  unchanged across compression variants;
- invalid unsupported IHDR compression method, corrupt IDAT zlib header,
  truncated IDAT, truncated fdAT, corrupt fdAT Adler-32, and fdAT sequence-gap
  probes.

## Results

Machine-readable artifacts:

- `data/workshop_editor/png_apng_zlib_compression_stage0.json`
- `data/workshop_editor/png_apng_zlib_compression_stage0/png_apng_zlib_compression_stage0.json`
- `data/workshop_editor/png_apng_zlib_compression_stage0/cases/*.png`
- `data/workshop_editor/png_apng_zlib_compression.js`

Summary:

| Metric | Result |
| --- | ---: |
| Current valid profiles covered | 3 |
| Case families | 6 |
| Total cases | 18 |
| Static PNG IDAT cases | 9 |
| APNG fdAT cases | 9 |
| IHDR compression-method-0 cases | 18 |
| Zlib CM=8 cases | 18 |
| Split fdAT cases | 9 |
| Case successes | 18 |
| Invalid probes | 6 |
| Invalid probes rejected | 6 |
| Case success ratio | 1.0 |
| Invalid rejection ratio | 1.0 |

Closed states:

- `png_idat_zlib_deflate_variant_reconstruction`
- `apng_fdat_zlib_deflate_variant_reconstruction`
- `png_apng_zlib_header_and_adler_error_rejection`
- `png_apng_zlib_compression_invalid_probe_rejection`

Blocked states:

- `full_apng_png_conformance`
- `live_external_editor_rewrite_validation`
- `production_import_export_carrier_selection_final_decision`
- `manual_readability_calibration`
- `package_runtime_lifecycle_integration`

## Interpretation

The image-data evidence now proves that selected valid zlib-wrapped DEFLATE
streams preserve decoded pixels and APNG playback when the raw scanline payload
is unchanged. This closes a different conformance gap than chunk-boundary
splitting: the compressed byte stream itself changes while the zlib method and
uncompressed image data stay valid.

This still is not full APNG/PNG conformance. It does not inspect every possible
DEFLATE block graph, broaden every color-type/bit-depth/interlace cross
product, prove preset-dictionary rejection, prove gamma/color-management
behavior, validate live external editor open-save preservation, or choose a
final production carrier.

## Verification

RED command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_png_apng_zlib_compression_matrix.py
```

Initial result:

```txt
ModuleNotFoundError: No module named 'png_apng_zlib_compression_matrix'
```

GREEN command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_png_apng_zlib_compression_matrix.py
```

Result:

```txt
Ran 5 tests in 0.040s
OK
```

Artifact command:

```powershell
python -B .\labs\workshop_editor\png_apng_zlib_compression_matrix.py
```

## Decision

Adopt `png_apng_zlib_compression_stage0` as the bounded PNG/APNG zlib
compression-method-0 proof.

Do not claim full APNG/PNG conformance, live external editor rewrite
validation, final production carrier selection, package runtime integration,
manual readability calibration, or profile-weighted evolution.
