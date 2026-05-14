# Algorithm Card: PNG Adam7 Interlace Decoder

## Purpose

Decode and validate bounded 8-bit RGBA PNG images that use Adam7 interlace
method 1, while preserving Mechagotchi semantic restore through JSON sidecars.

## Mathematical Basis

Adam7 interlace stores one image as seven reduced images. The lab uses the
standard pass schedule:

```txt
pass_i = (x_start, y_start, x_step, y_step)
reduced_width_i = ceil((width - x_start) / x_step)
reduced_height_i = ceil((height - y_start) / y_step)
pixel(x_start + px * x_step, y_start + py * y_step) = pass_i(px, py)
```

Each reduced-image scanline has a PNG filter byte followed by RGBA samples.
Filters 0 through 4 are reversed per reduced image, not across the final
image rows.

## Inputs

- Current valid SLIP profiles.
- First generated grid for each current valid profile.
- 8-bit RGBA PNG carriers encoded with Adam7 interlace method 1.
- Sidecar metadata with pass order, pass summaries, filter set, pixel hash,
  and asset hash binding.

## Outputs

- Adam7 interlaced PNG files.
- Sidecar files with `adam7_binding` pass manifests.
- Restored SLIP-aligned semantic grids.
- Invalid-probe rejection report.
- Browser-inspectable JS payload.

## Strengths

- Closes the explicit Adam7 interlace decoder gap without package code.
- Verifies the seven-pass schedule, reduced-image scanline lengths, filters
  0..4, visual carrier hash, pass manifest, and asset hash binding.
- Keeps semantic truth in the sidecar rather than inferring grid meaning from
  pixels.

## Weaknesses

- Supports only 8-bit RGBA color type 6.
- Does not cover APNG, grayscale-alpha, 1/2/4/16-bit depths, or full PNG
  conformance.
- Does not prove live editor rewrite behavior.
- Does not select a final production PNG carrier policy.

## Failure Modes

- Non-Adam7 PNGs must reject under this decoder.
- Truncated or trailing reduced-image scanline data must reject.
- Unsupported PNG filter types must reject.
- Pass-manifest mismatches must reject.
- Visual carrier hash mismatches must reject.
- Asset hash mismatches must reject.

## Integration Risk

Medium.

## License Status

No external code selected. The W3C PNG specification is used as the format
anchor.

## Prototype Result

Stage 0 Adam7 interlace proof completed on 2026-05-14.

```txt
profile_count: 3
png_roundtrip_success_count: 3
invalid_probe_rejected_count: 6
png_roundtrip_success_rate: 1.0
mean_semantic_fidelity: 1.0
mean_pixel_fidelity: 1.0
mean_non_empty_pass_count: 7.0
```

## Decision

Keep as active prototype. This closes only bounded 8-bit RGBA Adam7 interlace
decoding for current profile fixtures. It does not close APNG, full PNG
conformance, 16-bit/deeper bit-depth support, grayscale-alpha support, live
external editor rewrite validation, final production carrier selection,
package runtime integration, manual readability calibration, or
profile-weighted evolution.

## Go/No-Go Gate

Promote only after broader PNG fixture coverage and production import/export
policy decide how Adam7, APNG, textual/private metadata, and external sidecars
fit together.
