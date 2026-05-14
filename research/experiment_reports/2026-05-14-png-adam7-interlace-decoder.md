# Experiment Report: PNG Adam7 Interlace Decoder

Date: 2026-05-14

## Objective

Continue the Stage 7 workshop-editor import/export research by closing the
bounded Adam7 PNG interlace decoder gap that remained after the non-interlaced
PNG variant lab.

This experiment tests whether current SLIP profile grids can be exported as
8-bit RGBA Adam7 interlaced PNG carriers, decoded through the seven reduced
images, restored from Mechagotchi sidecars, and rejected safely under malformed
interlace, scanline, filter, pass-manifest, pixel-hash, and asset-hash inputs.

## Source Position

The research plan requires import/export evidence for standard creative
formats without confusing lab success for package runtime readiness. Existing
PNG labs covered static RGBA PNG, non-interlaced 8-bit color/filter variants,
embedded textual chunks, bounded textual metadata, and one private chunk
policy.

The remaining local PNG gap was Adam7 interlace. This lab stays inside
`labs/` and `data/`; it does not create `packages/`, does not claim APNG or
full PNG conformance, and does not claim live external editor preservation.

## External Anchor

- W3C PNG specification, used for IHDR interlace method values, Adam7 pass
  extraction order, filter method 0, IDAT zlib stream, and chunk validation:
  https://www.w3.org/TR/png-3/

## Implementation

Added:

- `labs/workshop_editor/test_png_adam7_interlace_decoder.py`
- `labs/workshop_editor/png_adam7_interlace_decoder.py`
- `data/workshop_editor/png_adam7_interlace_decoder_stage0.json`
- `data/workshop_editor/png_adam7_interlace_decoder_data.js`
- `data/workshop_editor/png_adam7_interlace_decoder_stage0/`
- `research/algorithm_cards/png_adam7_interlace_decoder.md`

The lab renders each profile grid to RGBA pixels, encodes a valid Adam7 PNG by
walking the seven reduced images, decodes those passes back into final image
coordinates, validates a sidecar `adam7_binding`, and restores the semantic
grid from sidecar metadata.

## Results

```txt
profile_count: 3
png_roundtrip_count: 3
png_roundtrip_success_count: 3
invalid_probe_count: 6
invalid_probe_rejected_count: 6
png_roundtrip_success_rate: 1.0
mean_semantic_fidelity: 1.0
mean_pixel_fidelity: 1.0
mean_non_empty_pass_count: 7.0
```

Rejected invalid probe families:

- `png_adam7_interlace_required`
- `png_adam7_scanline_length_mismatch`
- `png_filter_type_unsupported`
- `png_adam7_pass_manifest_mismatch`
- `png_adam7_pixel_hash_mismatch`
- `asset_hash_mismatch`

## Closed States

- `png_adam7_interlace_decoder`
- `png_adam7_pass_manifest`
- `png_adam7_filter_type_0_to_4_decoder`
- `png_adam7_sidecar_semantic_restore`
- `png_adam7_invalid_probe_rejection`

## Still Blocked

- APNG decoding.
- Full PNG conformance.
- 16-bit/deeper bit-depth channel decoding.
- Grayscale-alpha color type 4 decoding.
- Live external editor rewrite validation.
- Final PNG production carrier selection.
- Package runtime lifecycle integration.
- Manual readability calibration.
- Profile-weighted evolution.

## Verification

RED:

```txt
python -B -m unittest .\labs\workshop_editor\test_png_adam7_interlace_decoder.py
ModuleNotFoundError: No module named 'png_adam7_interlace_decoder'
```

GREEN:

```txt
python -B -m unittest .\labs\workshop_editor\test_png_adam7_interlace_decoder.py
Ran 5 tests in 0.039s
OK
```

Artifact generation:

```txt
python -B .\labs\workshop_editor\png_adam7_interlace_decoder.py
artifact_id: png_adam7_interlace_decoder_stage0
png_roundtrip_success_count: 3
invalid_probe_rejected_count: 6
mean_non_empty_pass_count: 7.0
```

## Decision

`prototype_png_adam7_interlace_decoder`.

This lab closes bounded 8-bit RGBA Adam7 interlace decoding as a Stage 0
sidecar-backed import/export proof. It does not close APNG, full PNG
conformance, deeper bit-depth/color-type coverage, live external editor
validation, final production carrier selection, or package runtime integration.
