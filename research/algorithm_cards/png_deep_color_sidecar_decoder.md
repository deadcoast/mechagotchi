# Algorithm Card: PNG Deep Color Sidecar Decoder

## Purpose

Decode and validate bounded non-interlaced PNG carriers that use low bit-depth
packed samples, 16-bit samples, and greyscale-alpha color type 4 while
preserving Mechagotchi semantic restore through JSON sidecars.

## Mathematical Basis

The lab follows the PNG color-type/bit-depth combinations allowed by the W3C
PNG specification for the missing local subset:

```txt
greyscale: 1, 2, 4, 16 bpp proof variants
indexed-color: 1, 2, 4 bpp proof variants with PLTE
truecolor: 16 bpp proof variant
greyscale-alpha: 8 and 16 bpp proof variants
truecolor-alpha: 16 bpp proof variant
```

Packed 1/2/4-bit samples are serialized most-significant-bit first in each
scanline byte. PNG filters operate on the packed scanline bytes, with filter
bytes-per-pixel computed as `max(1, ceil(bits_per_pixel / 8))`.

## Inputs

- Current valid SLIP profiles.
- First generated grid for each current valid profile.
- Non-interlaced PNG carriers across 11 deep-color variants.
- Sidecar metadata with color type, bit depth, scanline length, filter set,
  visual-carrier hash, source-render hash, and asset hash binding.

## Outputs

- PNG variant files.
- Sidecar files with `deep_color_binding`.
- Restored SLIP-aligned semantic grids.
- Invalid-probe rejection report.
- Browser-inspectable JS payload.

## Strengths

- Closes the explicit local 1/2/4/16-bit and greyscale-alpha PNG gap.
- Verifies packed low-bit scanline sizing, 16-bit sample rescaling, PLTE
  indexed-color decoding, filter types 0..4, visual carrier hashes, and asset
  binding.
- Keeps semantic truth in the sidecar when visual carriers are quantized or
  greyscale.

## Weaknesses

- Supports only bounded non-interlaced PNG fixtures.
- Does not cover APNG, arbitrary PNG ancillary/color-management behavior,
  Adam7/deep-color cross-products, live editor rewrite behavior, or final PNG
  production carrier selection.
- Low-bit and greyscale carriers can intentionally differ from the source
  render; pixel fidelity is measured against the visual carrier binding.

## Failure Modes

- Invalid color-type/bit-depth combinations must reject.
- Scanline length mismatches must reject.
- Unsupported filter types must reject.
- Deep-color binding mismatches must reject.
- Visual carrier hash mismatches must reject.
- Asset hash mismatches must reject.

## Integration Risk

Medium.

## License Status

No external code selected. The W3C PNG specification is used as the format
anchor.

## Prototype Result

Stage 0 deep-color PNG sidecar proof completed on 2026-05-14.

```txt
profile_count: 3
variant_count_per_profile: 11
variant_roundtrip_success_count: 33
invalid_probe_rejected_count: 6
variant_roundtrip_success_rate: 1.0
mean_semantic_fidelity: 1.0
mean_pixel_fidelity: 1.0
```

## Decision

Keep as active prototype. This closes bounded non-interlaced PNG deep-color
coverage for current profile fixtures. It does not close APNG, full PNG
conformance, Adam7/deep-color cross-products, live external editor rewrite
validation, final production carrier selection, package runtime integration,
manual readability calibration, or profile-weighted evolution.

## Go/No-Go Gate

Promote only after final PNG carrier policy decides how static PNG, Adam7,
APNG, textual/private metadata, deep color, and external sidecars fit into a
production import/export contract.
