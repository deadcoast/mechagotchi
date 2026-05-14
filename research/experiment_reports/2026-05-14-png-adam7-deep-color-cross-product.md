# Experiment Report: PNG Adam7 Deep Color Cross Product

Date: 2026-05-14

## Objective

Continue the Stage 7 workshop-editor import/export research by closing the
bounded cross-product between Adam7 interlace and the deep-color PNG sidecar
decoder subset.

This experiment tests whether current SLIP profile grids can be exported as
Adam7 interlaced PNG carriers across low-bit greyscale, low-bit indexed-color,
16-bit samples, and greyscale-alpha color type 4, decoded through seven
reduced images, restored from Mechagotchi sidecars, and rejected safely under
malformed interlace, scanline, filter, pass-manifest, bit-depth, pixel-hash,
and asset-hash inputs.

## Source Position

The research plan requires import/export evidence for standard creative
formats without confusing lab success for package runtime readiness. Existing
PNG labs covered static RGBA PNG, non-interlaced 8-bit color/filter variants,
bounded 8-bit RGBA Adam7 interlace, bounded non-interlaced deep color,
embedded textual sidecars, textual metadata variants, and one private chunk
policy.

The remaining local PNG gap was the Adam7/deep-color cross-product. This lab
stays inside `labs/` and `data/`; it does not create `packages/`, does not
claim APNG or full PNG conformance, and does not claim live external editor
preservation.

## External Anchor

- W3C PNG specification, used for Adam7 pass scheduling, allowed color type
  and bit depth matrix, packed reduced-image scanline sizing, filter method 0,
  PLTE, IDAT, and CRC semantics: https://www.w3.org/TR/png-3/

## Implementation

Added:

- `labs/workshop_editor/test_png_adam7_deep_color_cross_product.py`
- `labs/workshop_editor/png_adam7_deep_color_cross_product.py`
- `data/workshop_editor/png_adam7_deep_color_cross_product_stage0.json`
- `data/workshop_editor/png_adam7_deep_color_cross_product_data.js`
- `data/workshop_editor/png_adam7_deep_color_cross_product_stage0/`
- `research/algorithm_cards/png_adam7_deep_color_cross_product.md`

The lab renders each profile grid to source RGBA pixels, encodes 11 Adam7
deep-color variant carriers, decodes each reduced-image pass into final image
coordinates, validates an `adam7_deep_color_binding` with pass summaries,
color type, bit depth, filter set, and visual hash, then restores the semantic
grid from sidecar metadata.

Low-bit greyscale and indexed-color variants are intentionally quantized
visual carriers. Semantic fidelity is measured against the restored sidecar
grid; pixel fidelity is measured against the decoded visual carrier hash.

## Results

```txt
profile_count: 3
variant_count_per_profile: 11
variant_roundtrip_count: 33
variant_roundtrip_success_count: 33
invalid_probe_count: 7
invalid_probe_rejected_count: 7
variant_roundtrip_success_rate: 1.0
mean_semantic_fidelity: 1.0
mean_pixel_fidelity: 1.0
mean_non_empty_pass_count: 7.0
supported_color_types: [0, 2, 3, 4, 6]
supported_bit_depths: [1, 2, 4, 8, 16]
```

Rejected invalid probe families:

- `png_adam7_deep_color_interlace_required`
- `png_adam7_deep_color_scanline_length_mismatch`
- `png_filter_type_unsupported`
- `png_adam7_deep_color_pass_manifest_mismatch`
- `png_adam7_deep_color_bit_depth_mismatch`
- `png_adam7_deep_color_pixel_hash_mismatch`
- `asset_hash_mismatch`

## Closed States

- `png_adam7_deep_color_cross_product_decoder`
- `png_adam7_deep_color_low_bit_decoder`
- `png_adam7_deep_color_16bit_decoder`
- `png_adam7_deep_color_grayscale_alpha_decoder`
- `png_adam7_deep_color_pass_manifest`
- `png_adam7_deep_color_sidecar_semantic_restore`
- `png_adam7_deep_color_invalid_probe_rejection`

## Still Blocked

- APNG decoding.
- Full PNG conformance.
- Live external editor rewrite validation.
- Private chunk editor preservation matrix.
- Final PNG production carrier selection.
- Package runtime lifecycle integration.
- Manual readability calibration.
- Profile-weighted evolution.

## Verification

RED:

```txt
python -B -m unittest .\labs\workshop_editor\test_png_adam7_deep_color_cross_product.py
ModuleNotFoundError: No module named 'png_adam7_deep_color_cross_product'
```

GREEN:

```txt
python -B -m unittest .\labs\workshop_editor\test_png_adam7_deep_color_cross_product.py
Ran 5 tests in 0.156s
OK
```

Artifact generation:

```txt
python -B .\labs\workshop_editor\png_adam7_deep_color_cross_product.py
artifact_id: png_adam7_deep_color_cross_product_stage0
variant_roundtrip_success_count: 33
invalid_probe_rejected_count: 7
mean_non_empty_pass_count: 7.0
```

## Decision

`prototype_png_adam7_deep_color_cross_product`.

This lab closes bounded Adam7 interlace plus deep-color sidecar decoding as a
Stage 0 import/export proof. It does not close APNG, full PNG conformance,
live external editor validation, final production carrier selection, or
package runtime integration.
