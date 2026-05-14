# Algorithm Card: APNG Bit Depth Frame Data

## Purpose

Define a bounded Stage 0 APNG image-data matrix for packed low-bit and 16-bit
frame reconstruction across the current SLIP profile corpus.

## Mathematical Basis

The lab treats APNG bit-depth reconstruction as:

```txt
raw_i = zlib_decompress(frame_data_i)
rows_i = unfilter(raw_i, filter_type, bytes_per_pixel)
samples_i = unpack(rows_i, bit_depth, color_type)
rgba_i = color_decode(samples_i, color_type, PLTE, tRNS)
O_{i+1} = source_overwrite(O_i, rgba_i)
```

It validates:

```txt
1/2/4-bit greyscale: packed sample -> quantized greyscale RGBA
1/2/4-bit indexed: packed index -> PLTE[index] + tRNS[index]
16-bit greyscale: big-endian sample -> 8-bit display byte
16-bit truecolor: three big-endian samples -> RGB
16-bit greyscale-alpha: sample pair -> grey + alpha
16-bit truecolor-alpha: four big-endian samples -> RGBA
```

## Inputs

- Valid SLIP profile
- Generated profile-aligned grid
- Non-interlaced APNG static-first-frame carrier
- Ten bounded bit-depth frame-data cases

## Outputs

- APNG bit-depth frame-data report
- Generated APNG fixtures for each current valid profile
- Frame pixel hashes, display hashes, scanline lengths, filter widths, and
  split-`fdAT` counts
- Invalid bit-depth/frame-data probe results

## External Anchor

The W3C PNG Third Edition specification anchors the rules for:

- legal bit depths by PNG color type;
- packed low-bit sample ordering;
- filter method 0 reconstruction;
- `PLTE` and `tRNS` relationships;
- APNG `fcTL`/`fdAT` sequence numbering and frame-data inheritance.

Source: <https://www.w3.org/TR/png-3/>

## Strengths

- Moves APNG image-data evidence beyond 8-bit frame data.
- Exercises packed sample decoding and 16-bit sample width reconstruction.
- Records actual per-frame filter types and scanline byte lengths.
- Rejects malformed bit-depth/color-type metadata, scanline length, filter,
  and `fdAT` sequence inputs.

## Weaknesses

- Uses deterministic non-interlaced full-canvas APNG fixtures only.
- Does not cover Adam7 APNG frames, gamma/color-management interactions, every
  ancillary chunk, or live editor preservation.
- Does not choose the final PNG/APNG production metadata carrier.

## Failure Modes

- Treating bit-depth success as full APNG/PNG conformance.
- Miscomputing packed low-bit scanline lengths.
- Applying filter bytes with the wrong bytes-per-pixel width.
- Accepting invalid `fdAT` sequence gaps.
- Dropping alpha while down-converting 16-bit alpha samples.

## Integration Risk

Medium. Bit-depth frame reconstruction is needed before production APNG import,
but this remains a bounded lab subset that must be combined with broader
image-data, renderer, and external-editor evidence.

## License Status

No external code selected. The W3C PNG specification is used as the format
anchor.

## Prototype Result

Stage 0 bit-depth frame-data matrix completed on 2026-05-14.

```txt
profile_count: 3
case_count: 30
case_success_count: 30
invalid_probe_count: 4
invalid_probe_rejected_count: 4
supported_color_types: [0, 2, 3, 4, 6]
supported_bit_depths: [1, 2, 4, 16]
split_fdat_frame_count: 30
```

## Decision

Keep as a bounded APNG image-data proof. It closes only non-interlaced packed
1/2/4-bit and 16-bit frame reconstruction, filter method 0 row reconstruction,
split-`fdAT` reconstruction, and invalid bit-depth/frame-data probe rejection
for deterministic fixtures.

Full APNG/PNG conformance, live external editor validation, final carrier
selection, package runtime integration, manual readability calibration, and
profile-weighted evolution remain blocked.

## Go/No-Go Gate

Promote APNG image-data policy only after this bit-depth matrix is combined
with the other APNG fixtures and live editor open-save evidence.
