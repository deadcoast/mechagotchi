# Experiment Report: PNG Deep Color Sidecar Decoder

Date: 2026-05-14

## Objective

Continue the Stage 7 workshop-editor import/export research by closing the
bounded PNG bit-depth and greyscale-alpha gap that remained after the
non-interlaced 8-bit PNG variant lab and the bounded 8-bit RGBA Adam7 lab.

This experiment tests whether current SLIP profile grids can be exported as
non-interlaced PNG carriers across low-bit greyscale, low-bit indexed-color,
16-bit samples, and greyscale-alpha color type 4, decoded back to a validated
visual carrier, restored from Mechagotchi sidecars, and rejected safely under
malformed bit-depth, scanline, filter, binding, pixel-hash, and asset-hash
inputs.

## Source Position

The research plan requires import/export evidence for standard creative
formats without confusing lab success for package runtime readiness. Existing
PNG labs covered static RGBA PNG, non-interlaced 8-bit color/filter variants,
8-bit RGBA Adam7 interlace, embedded textual sidecars, textual metadata
variants, and one private chunk policy.

The remaining local PNG gap was deeper bit-depth/color-type coverage. This
lab stays inside `labs/` and `data/`; it does not create `packages/`, does not
claim APNG or full PNG conformance, and does not claim live external editor
preservation.

## External Anchor

- W3C PNG specification, used for the allowed color type and bit depth matrix,
  packed scanline sizing, filter method 0, PLTE, IDAT, and CRC semantics:
  https://www.w3.org/TR/png-3/

## Implementation

Added:

- `labs/workshop_editor/test_png_deep_color_sidecar_decoder.py`
- `labs/workshop_editor/png_deep_color_sidecar_decoder.py`
- `data/workshop_editor/png_deep_color_sidecar_decoder_stage0.json`
- `data/workshop_editor/png_deep_color_sidecar_decoder_data.js`
- `data/workshop_editor/png_deep_color_sidecar_decoder_stage0/`
- `research/algorithm_cards/png_deep_color_sidecar_decoder.md`

The lab renders each profile grid to source RGBA pixels, encodes 11 PNG
variant carriers, decodes each visual carrier, validates a `deep_color_binding`
with color type, bit depth, scanline length, filter set, and visual hash, then
restores the semantic grid from sidecar metadata.

Low-bit greyscale and indexed-color variants are intentionally quantized
visual carriers. Semantic fidelity is measured against the restored sidecar
grid; pixel fidelity is measured against the decoded visual carrier hash.

## Results

```txt
profile_count: 3
variant_count_per_profile: 11
variant_roundtrip_count: 33
variant_roundtrip_success_count: 33
invalid_probe_count: 6
invalid_probe_rejected_count: 6
variant_roundtrip_success_rate: 1.0
mean_semantic_fidelity: 1.0
mean_pixel_fidelity: 1.0
supported_color_types: [0, 2, 3, 4, 6]
supported_bit_depths: [1, 2, 4, 8, 16]
```

Rejected invalid probe families:

- `png_bit_depth_color_type_invalid`
- `png_scanline_length_mismatch`
- `png_filter_type_unsupported`
- `png_deep_color_bit_depth_mismatch`
- `png_deep_color_pixel_hash_mismatch`
- `asset_hash_mismatch`

## Closed States

- `png_grayscale_low_bit_depth_decoder`
- `png_indexed_low_bit_depth_decoder`
- `png_16bit_sample_decoder`
- `png_color_type_4_grayscale_alpha_decoder`
- `png_deep_color_sidecar_semantic_restore`
- `png_deep_color_invalid_probe_rejection`

## Still Blocked

- APNG decoding.
- Full PNG conformance.
- Adam7/deep-color cross-product decoding.
- Live external editor rewrite validation.
- Private chunk editor preservation matrix.
- Final PNG production carrier selection.
- Package runtime lifecycle integration.
- Manual readability calibration.
- Profile-weighted evolution.

## Verification

RED:

```txt
python -B -m unittest .\labs\workshop_editor\test_png_deep_color_sidecar_decoder.py
ModuleNotFoundError: No module named 'png_deep_color_sidecar_decoder'
```

GREEN:

```txt
python -B -m unittest .\labs\workshop_editor\test_png_deep_color_sidecar_decoder.py
Ran 5 tests in 0.152s
OK
```

Artifact generation:

```txt
python -B .\labs\workshop_editor\png_deep_color_sidecar_decoder.py
artifact_id: png_deep_color_sidecar_decoder_stage0
variant_roundtrip_success_count: 33
invalid_probe_rejected_count: 6
supported_bit_depths: [1, 2, 4, 8, 16]
```

## Decision

`prototype_png_deep_color_sidecar_decoder`.

This lab closes bounded non-interlaced PNG low-bit, 16-bit, indexed low-bit,
and greyscale-alpha sidecar decoding as a Stage 0 import/export proof. It does
not close APNG, full PNG conformance, Adam7/deep-color cross-products, live
external editor validation, final production carrier selection, or package
runtime integration.
