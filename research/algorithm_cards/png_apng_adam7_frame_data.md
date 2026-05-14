# Algorithm Card: APNG Adam7 Frame Data

## Purpose

Define a bounded Stage 0 APNG image-data matrix for Adam7-interlaced APNG
frame reconstruction across selected current SLIP profile fixtures.

## Mathematical Basis

The lab treats each APNG frame as an Adam7 PNG image stream:

```txt
raw_i = zlib_decompress(IDAT_or_fdAT_i)
for pass in Adam7:
  rows_pass = unfilter(raw_i[pass], filter_type, bytes_per_pixel)
  samples_pass = unpack(rows_pass, bit_depth, color_type)
  rgba_pass = color_decode(samples_pass, color_type, PLTE, tRNS)
  scatter(rgba_pass, canvas_pixels, Adam7_pass_coordinates)
O_{i+1} = blend(rgba_i, O_i, blend_op)
```

It validates:

```txt
8-bit RGBA Adam7: pass rows -> RGBA
1-bit greyscale Adam7: packed sample -> greyscale RGBA
4-bit indexed Adam7: packed index -> PLTE[index] + tRNS[index]
16-bit truecolor Adam7: three big-endian samples -> RGB
16-bit greyscale-alpha Adam7: sample pair -> grey + alpha
16-bit truecolor-alpha Adam7: four big-endian samples -> RGBA
```

## Inputs

- Valid SLIP profile
- Generated profile-aligned grid
- Adam7-interlaced APNG static-first-frame carrier
- Six bounded Adam7 frame-data cases

## Outputs

- APNG Adam7 frame-data report
- Generated APNG fixtures for each current valid profile
- Frame pixel hashes, display hashes, final canvas hashes, pass summaries,
  filter types, split-`fdAT` counts, and alpha counts
- Invalid Adam7/APNG frame-data probe results

## External Anchor

The W3C PNG Third Edition specification anchors the rules for:

- Adam7 interlace pass order and reduced-image reconstruction;
- legal bit depths by PNG color type;
- packed low-bit sample ordering;
- filter method 0 reconstruction;
- `PLTE` and `tRNS` relationships;
- APNG `fcTL`/`fdAT` sequence numbering and frame-data inheritance.

Source: <https://www.w3.org/TR/png-3/>

## Strengths

- Tests the APNG frame-data path with Adam7 interlace method 1.
- Reuses the existing static Adam7/deep-color decoder as the frame
  reconstruction oracle.
- Exercises selected packed, indexed, 8-bit, and 16-bit sample models.
- Records reduced-image pass manifests per frame rather than assuming
  row-major non-interlaced scanlines.
- Rejects malformed interlace mode, bit-depth metadata, scanlines, filters,
  and `fdAT` sequence inputs.

## Weaknesses

- Uses deterministic full-canvas APNG fixtures only.
- Does not cover partial Adam7 APNG regions.
- Does not cover every legal bit-depth/color-type pair, gamma/color-management
  interactions, every ancillary chunk, or live editor preservation.
- Does not choose the final PNG/APNG production metadata carrier.

## Failure Modes

- Treating non-interlaced APNG frame-data success as sufficient for Adam7 APNG.
- Computing Adam7 pass scanline lengths from full canvas row length.
- Accepting non-Adam7 APNG files in the Adam7-specific path.
- Accepting invalid `fdAT` sequence gaps after split continuation chunks.
- Dropping indexed transparency or 16-bit alpha during pass reconstruction.

## Integration Risk

Medium. Adam7 APNG frame reconstruction is needed before production APNG import
can claim broad image-data coverage, but this remains a bounded lab subset that
must be combined with broader image-data, renderer, and external-editor
evidence.

## License Status

No external code selected. The W3C PNG specification is used as the format
anchor.

## Prototype Result

Stage 0 Adam7 frame-data matrix completed on 2026-05-14.

```txt
profile_count: 3
case_count: 18
case_success_count: 18
invalid_probe_count: 5
invalid_probe_rejected_count: 5
supported_color_types: [0, 2, 3, 4, 6]
supported_bit_depths: [1, 4, 8, 16]
adam7_pass_count: 7
split_fdat_frame_count: 18
```

## Decision

Keep as a bounded APNG image-data proof. It closes only full-canvas Adam7 APNG
frame reconstruction for selected packed low-bit, indexed, 8-bit, and 16-bit
sample models, plus split-`fdAT` reconstruction, APNG source/over composition,
and invalid probe rejection for deterministic fixtures.

Full APNG/PNG conformance, live external editor validation, final carrier
selection, package runtime integration, manual readability calibration, and
profile-weighted evolution remain blocked.

## Go/No-Go Gate

Promote APNG image-data policy only after this Adam7 matrix is combined with
the other APNG fixtures and live editor open-save evidence.
