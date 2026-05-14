# Algorithm Card: APNG Filtered Frame Data

## Purpose

Define a bounded Stage 0 APNG image-data matrix for PNG filter-method-0
scanline reconstruction and split-`fdAT` frame-data concatenation.

## Mathematical Basis

The lab treats a filtered APNG frame as:

```txt
compressed_frame_i = concat(fdAT_i.sequence_ordered.frame_data)
filtered_scanlines_i = zlib_decompress(compressed_frame_i)
pixels_i = unfilter(filtered_scanlines_i, filter_type in {0,1,2,3,4})
O_{i+1} = source_overwrite(O_i, pixels_i, x_offset, y_offset)
```

For each scanline byte `x`, it validates the PNG reconstruction functions:

```txt
None:    Recon(x) = Filt(x)
Sub:     Recon(x) = Filt(x) + Recon(a)
Up:      Recon(x) = Filt(x) + Recon(b)
Average: Recon(x) = Filt(x) + floor((Recon(a) + Recon(b)) / 2)
Paeth:   Recon(x) = Filt(x) + PaethPredictor(Recon(a), Recon(b), Recon(c))
```

All arithmetic is modulo 256.

## Inputs

- Valid SLIP profile
- Generated profile-aligned grid
- 8-bit RGBA non-interlaced APNG static-first-frame carrier
- Five filter-method-0 frame-data cases

## Outputs

- APNG filtered frame-data report
- Generated APNG fixtures for each current valid profile
- Frame pixel hashes, display hashes, filter types seen, and `fdAT` counts
- Invalid frame-data probe results

## External Anchor

The W3C PNG Third Edition specification anchors the rules for:

- PNG filter method 0;
- filter types None, Sub, Up, Average, and Paeth;
- zlib image-data streams;
- `fdAT` sequence numbers and frame-data concatenation.

Source: <https://www.w3.org/TR/png-3/>

## Strengths

- Moves APNG image-data evidence beyond filter-0 frame fixtures.
- Exercises all five PNG filter-method-0 reconstruction functions.
- Exercises multi-`fdAT` frame-data concatenation for every current profile.
- Rejects invalid filter bytes, truncated scanlines, `fdAT` sequence gaps, and
  missing `fdAT` continuations.

## Weaknesses

- Uses deterministic 8-bit RGBA non-interlaced APNG fixtures only.
- Does not cover APNG Adam7 frames, APNG deep-color frames, palette-inherited
  APNG frames, color-management chunks, or every ancillary interaction.
- Does not run live editor open-save preservation.
- Does not choose the final PNG/APNG production metadata carrier.

## Failure Modes

- Treating filtered-frame success as full APNG/PNG conformance.
- Applying Sub/Up/Average/Paeth filters to pixels instead of bytes.
- Failing to concatenate all `fdAT` frame-data fields before decompression.
- Accepting out-of-sequence or missing `fdAT` chunks.

## Integration Risk

Medium. Filter reconstruction and split-frame data are needed before production
APNG import, but this remains a bounded lab subset that must be combined with
broader image-data and external-editor evidence.

## License Status

No external code selected. The W3C PNG specification is used as the format
anchor.

## Prototype Result

Stage 0 filtered frame-data matrix completed on 2026-05-14.

```txt
profile_count: 3
case_count: 15
case_success_count: 15
invalid_probe_count: 4
invalid_probe_rejected_count: 4
filter_family_count: 5
split_fdat_frames: 15
```

## Decision

Keep as a bounded APNG image-data proof. It closes only 8-bit RGBA
non-interlaced APNG filter-method-0 reconstruction, split-`fdAT` concatenation,
and invalid frame-data rejection for deterministic fixtures.

Full APNG/PNG conformance, live external editor validation, final carrier
selection, package runtime integration, manual readability calibration, and
profile-weighted evolution remain blocked.

## Go/No-Go Gate

Promote APNG image-data policy only after this filtered-frame matrix is
combined with remaining APNG/PNG fixtures and live editor open-save evidence.
