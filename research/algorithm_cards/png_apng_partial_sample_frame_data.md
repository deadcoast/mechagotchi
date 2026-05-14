# Algorithm Card: APNG Partial Sample Frame Data

## Purpose

Define a bounded Stage 0 APNG image-data matrix for partial frame regions that
use packed low-bit, indexed, and 16-bit PNG sample encodings.

## Mathematical Basis

The lab treats each APNG frame as:

```txt
raw_i = zlib_decompress(IDAT_or_fdAT_i)
rows_i = unfilter(raw_i, filter_type, bytes_per_pixel)
samples_i = unpack(rows_i, bit_depth, color_type)
rgba_i = color_decode(samples_i, color_type, PLTE, tRNS)
O_{i+1}[x_offset:x_offset+w, y_offset:y_offset+h] =
  blend(rgba_i, O_i, blend_op)
```

It validates:

```txt
1-bit greyscale partial region: packed sample -> greyscale RGBA
4-bit indexed partial region: packed index -> PLTE[index] + tRNS[index]
16-bit truecolor partial region: big-endian sample triples -> RGB
16-bit greyscale-alpha partial region: sample pair -> grey + alpha
16-bit truecolor-alpha partial region: sample quadruple -> RGBA
```

## Inputs

- Valid SLIP profile
- Generated profile-aligned grid
- Non-interlaced APNG static-first-frame carrier
- Five bounded partial sample frame-data cases

## Outputs

- APNG partial sample frame-data report
- Generated APNG fixtures for each current valid profile
- Frame pixel hashes, display hashes, final canvas hashes, partial scanline
  lengths, filter widths, split-`fdAT` counts, and alpha counts
- Invalid partial-frame/sample probe results

## External Anchor

The W3C PNG Third Edition specification anchors the rules for:

- APNG frame offsets and source/over blend behavior;
- `fcTL`/`fdAT` sequence numbering and frame-data inheritance;
- legal bit depths by PNG color type;
- packed low-bit sample ordering;
- filter method 0 reconstruction;
- `PLTE` and `tRNS` relationships.

Source: <https://www.w3.org/TR/png-3/>

## Strengths

- Tests the intersection of APNG partial-frame offsets and non-8-bit sample
  reconstruction.
- Exercises indexed transparency inside partial regions.
- Records scanline byte length per partial patch rather than assuming canvas
  dimensions.
- Rejects malformed bounds, bit-depth metadata, scanlines, filters, and
  sequence numbers.

## Weaknesses

- Uses deterministic non-interlaced fixtures only.
- Does not cover every legal bit-depth/color-type pair in partial APNG
  regions.
- Does not cover Adam7 APNG frames, gamma/color-management interactions, every
  ancillary chunk, or live editor preservation.
- Does not choose the final PNG/APNG production metadata carrier.

## Failure Modes

- Treating a full-canvas bit-depth proof as sufficient for partial APNG
  regions.
- Computing patch scanline lengths from canvas dimensions.
- Applying alpha-over to the wrong offset region.
- Accepting out-of-bounds partial frame controls.
- Accepting `fdAT` sequence gaps after split continuation chunks.

## Integration Risk

Medium. Partial APNG import needs the exact offset/sample interaction before
runtime promotion, but this remains a bounded lab subset that must be combined
with broader image-data, renderer, and external-editor evidence.

## License Status

No external code selected. The W3C PNG specification is used as the format
anchor.

## Prototype Result

Stage 0 partial sample frame-data matrix completed on 2026-05-14.

```txt
profile_count: 3
case_count: 15
case_success_count: 15
invalid_probe_count: 5
invalid_probe_rejected_count: 5
supported_color_types: [0, 2, 3, 4, 6]
supported_bit_depths: [1, 4, 16]
partial_frame_case_count: 15
split_fdat_frame_count: 15
```

## Decision

Keep as a bounded APNG image-data proof. It closes only non-interlaced partial
frame offset reconstruction for selected packed low-bit, indexed, and 16-bit
sample models plus source/over composition and invalid probe rejection.

Full APNG/PNG conformance, live external editor validation, final carrier
selection, package runtime integration, manual readability calibration, and
profile-weighted evolution remain blocked.

## Go/No-Go Gate

Promote APNG image-data policy only after this partial-sample matrix is
combined with the other APNG fixtures and live editor open-save evidence.
