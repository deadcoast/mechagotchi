# Algorithm Card: APNG Partial Adam7 Frame Data

## Purpose

Define a bounded Stage 0 APNG image-data matrix for non-zero-offset partial
frames whose frame datastreams are Adam7-interlaced.

## Mathematical Basis

The lab treats each partial APNG frame as an Adam7 PNG image stream with a
frame-local coordinate system:

```txt
raw_i = zlib_decompress(IDAT_or_fdAT_i)
for pass in Adam7:
  rows_pass = unfilter(raw_i[pass], filter_type, bytes_per_pixel)
  samples_pass = unpack(rows_pass, bit_depth, color_type)
  rgba_pass = color_decode(samples_pass, color_type, PLTE, tRNS)
  scatter(rgba_pass, frame_pixels, Adam7_pass_coordinates)
O_{i+1}[x_offset:x_offset+w, y_offset:y_offset+h] =
  blend(frame_pixels, O_i, blend_op)
```

It validates:

```txt
8-bit RGBA partial Adam7: pass rows -> RGBA
1-bit greyscale partial Adam7: packed sample -> greyscale RGBA
4-bit indexed partial Adam7: packed index -> PLTE[index] + tRNS[index]
16-bit truecolor partial Adam7: three big-endian samples -> RGB
16-bit greyscale-alpha partial Adam7: sample pair -> grey + alpha
16-bit truecolor-alpha partial Adam7: four big-endian samples -> RGBA
```

## Inputs

- Valid SLIP profile
- Generated profile-aligned grid
- Adam7-interlaced APNG static-first-frame carrier
- Six bounded partial Adam7 frame-data cases

## Outputs

- APNG partial Adam7 frame-data report
- Generated APNG fixtures for each current valid profile
- Frame pixel hashes, display hashes, final canvas hashes, pass summaries,
  filter types, offset metadata, split-`fdAT` counts, and alpha counts
- Invalid partial Adam7/APNG frame-data probe results

## External Anchor

The W3C PNG Third Edition specification anchors the rules for:

- APNG `fcTL` frame dimensions and offsets;
- output-buffer composition and source/over blend behavior;
- `fcTL`/`fdAT` sequence numbering and frame-data inheritance;
- Adam7 interlace pass order and reduced-image reconstruction;
- legal bit depths by PNG color type;
- packed low-bit sample ordering;
- filter method 0 reconstruction;
- `PLTE` and `tRNS` relationships.

Source: <https://www.w3.org/TR/png-3/>

## Strengths

- Tests the intersection of APNG partial-frame offsets and Adam7 pass
  reconstruction.
- Exercises selected packed, indexed, 8-bit, and 16-bit sample models.
- Uses a 6x6 non-zero-offset patch so every Adam7 pass is non-empty.
- Records pass manifests per partial frame rather than assuming canvas-sized
  scanlines.
- Rejects malformed interlace mode, partial bounds, bit-depth metadata,
  scanlines, filters, and `fdAT` sequence inputs.

## Weaknesses

- Uses deterministic 6x6 patch fixtures only.
- Does not cover every legal bit-depth/color-type pair or every possible
  partial-frame dimension.
- Does not cover gamma/color-management interactions, every ancillary chunk, or
  live editor preservation.
- Does not choose the final PNG/APNG production metadata carrier.

## Failure Modes

- Treating full-canvas Adam7 APNG success as sufficient for partial APNG
  regions.
- Computing Adam7 pass scanline lengths from the full canvas instead of the
  frame-local dimensions.
- Applying the patch at the wrong output-buffer offset.
- Accepting out-of-bounds `fcTL` frame controls.
- Accepting invalid `fdAT` sequence gaps after split continuation chunks.

## Integration Risk

Medium. Partial Adam7 APNG frame reconstruction is a specific import-path risk
before broad APNG image-data coverage can be promoted, but this remains a
bounded lab subset that must be combined with broader image-data, renderer, and
external-editor evidence.

## License Status

No external code selected. The W3C PNG specification is used as the format
anchor.

## Prototype Result

Stage 0 partial Adam7 frame-data matrix completed on 2026-05-14.

```txt
profile_count: 3
case_count: 18
case_success_count: 18
invalid_probe_count: 6
invalid_probe_rejected_count: 6
supported_color_types: [0, 2, 3, 4, 6]
supported_bit_depths: [1, 4, 8, 16]
adam7_pass_count: 7
partial_adam7_frame_count: 18
split_fdat_frame_count: 18
```

## Decision

Keep as a bounded APNG image-data proof. It closes only non-zero-offset partial
Adam7 APNG frame reconstruction for selected packed low-bit, indexed, 8-bit,
and 16-bit sample models, plus split-`fdAT` reconstruction, APNG source/over
composition, and invalid probe rejection for deterministic fixtures.

Full APNG/PNG conformance, live external editor validation, final carrier
selection, package runtime integration, manual readability calibration, and
profile-weighted evolution remain blocked.

## Go/No-Go Gate

Promote APNG image-data policy only after this partial Adam7 matrix is
combined with the other APNG fixtures and live editor open-save evidence.
