# Algorithm Card: PNG Adam7 Deep Color Cross Product

## Purpose

Decode and validate bounded PNG carriers that combine Adam7 interlace method 1
with the previously proven low-bit, 16-bit, indexed-color, and greyscale-alpha
PNG sidecar subset.

## Mathematical Basis

The lab composes two already proven Stage 0 surfaces:

```txt
Adam7 pass_i = (x_start, y_start, x_step, y_step)
reduced_width_i = ceil((width - x_start) / x_step)
reduced_height_i = ceil((height - y_start) / y_step)
scanline_bytes_i = ceil(reduced_width_i * channels(color_type) * bit_depth / 8)
filter_bpp = max(1, ceil(channels(color_type) * bit_depth / 8))
```

Each Adam7 reduced image uses the PNG color-type/bit-depth rules from the
deep-color lab. Packed 1/2/4-bit samples are packed per reduced-image scanline,
then PNG filters 0..4 are applied bytewise to those packed scanline bytes.

## Inputs

- Current valid SLIP profiles.
- First generated grid for each current valid profile.
- Adam7 interlaced PNG carriers across the 11 deep-color variants.
- Sidecar metadata with Adam7 pass summaries, color type, bit depth, filter
  set, visual-carrier hash, source-render hash, and asset hash binding.

## Outputs

- Adam7/deep-color PNG variant files.
- Sidecar files with `adam7_deep_color_binding`.
- Restored SLIP-aligned semantic grids.
- Invalid-probe rejection report.
- Browser-inspectable JS payload.

## Strengths

- Closes the explicit local Adam7/deep-color cross-product gap.
- Verifies reduced-image scanline sizing across packed low-bit and 16-bit
  variants, pass manifests, filter types 0..4, PLTE indexed-color decoding,
  visual carrier hashes, and asset binding.
- Keeps semantic truth in the sidecar when visual carriers are quantized or
  greyscale.

## Weaknesses

- Supports only bounded current-fixture Adam7/deep-color carriers.
- Does not cover APNG, arbitrary PNG ancillary/color-management behavior, live
  editor rewrite behavior, or final PNG production carrier selection.
- Low-bit and greyscale carriers can intentionally differ from the source
  render; pixel fidelity is measured against the visual carrier binding.

## Failure Modes

- Non-Adam7 PNGs must reject.
- Reduced-image scanline length mismatches must reject.
- Unsupported filter types must reject.
- Adam7/deep-color pass-manifest mismatches must reject.
- Bit-depth binding mismatches must reject.
- Visual carrier hash mismatches must reject.
- Asset hash mismatches must reject.

## Integration Risk

Medium.

## License Status

No external code selected. The W3C PNG specification is used as the format
anchor.

## Prototype Result

Stage 0 Adam7/deep-color cross-product proof completed on 2026-05-14.

```txt
profile_count: 3
variant_count_per_profile: 11
variant_roundtrip_success_count: 33
invalid_probe_rejected_count: 7
variant_roundtrip_success_rate: 1.0
mean_semantic_fidelity: 1.0
mean_pixel_fidelity: 1.0
mean_non_empty_pass_count: 7.0
```

## Decision

Keep as active prototype. This closes bounded Adam7/deep-color cross-product
coverage for current profile fixtures. It does not close APNG, full PNG
conformance, live external editor rewrite validation, final PNG production
carrier selection, package runtime integration, manual readability calibration,
or profile-weighted evolution.

## Go/No-Go Gate

Promote only after final PNG carrier policy decides how static PNG, Adam7,
deep color, APNG, textual/private metadata, and external sidecars fit into a
production import/export contract.
