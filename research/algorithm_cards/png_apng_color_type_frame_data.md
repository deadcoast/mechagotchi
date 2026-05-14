# Algorithm Card: APNG Color Type Frame Data

## Purpose

Define a bounded Stage 0 APNG image-data matrix for PNG color-type frame
reconstruction across greyscale, truecolor, indexed-color, greyscale-alpha, and
truecolor-alpha APNG frames.

## Mathematical Basis

The lab treats APNG color-type reconstruction as:

```txt
samples_i = zlib_decompress(frame_data_i)
rgba_i = color_decode(samples_i, color_type, PLTE, tRNS)
O_{i+1} = source_overwrite(O_i, rgba_i)
```

It validates these 8-bit mappings:

```txt
color_type 0: grey -> (grey, grey, grey, alpha_from_tRNS_or_255)
color_type 2: rgb -> (r, g, b, alpha_from_tRNS_or_255)
color_type 3: index -> (PLTE[index].r, PLTE[index].g, PLTE[index].b, tRNS[index] or 255)
color_type 4: grey_alpha -> (grey, grey, grey, alpha)
color_type 6: rgba -> (r, g, b, a)
```

## Inputs

- Valid SLIP profile
- Generated profile-aligned grid
- 8-bit non-interlaced APNG static-first-frame carrier
- Five color-type frame-data cases

## Outputs

- APNG color-type frame-data report
- Generated APNG fixtures for each current valid profile
- Frame pixel hashes, display hashes, bytes per pixel, and alpha counts
- Invalid color metadata probe results

## External Anchor

The W3C PNG Third Edition specification anchors the rules for:

- PNG color types 0, 2, 3, 4, and 6;
- bit-depth restrictions;
- PLTE and tRNS relationships;
- filter method 0;
- APNG `fdAT` frame data inheriting static-image header properties.

Source: <https://www.w3.org/TR/png-3/>

## Strengths

- Moves APNG image-data evidence beyond 8-bit RGBA-only fixtures.
- Exercises palette transparency and explicit alpha-channel frame data.
- Records per-frame RGBA hashes after color decoding.
- Rejects missing PLTE, invalid tRNS length, unsupported color type, and
  forbidden tRNS-with-alpha combinations.

## Weaknesses

- Uses deterministic 8-bit non-interlaced full-canvas APNG fixtures only.
- Does not cover lower bit depths, 16-bit APNG frame data, APNG Adam7 frames,
  color-management interactions, or every ancillary chunk.
- Does not run live editor open-save preservation.
- Does not choose the final PNG/APNG production metadata carrier.

## Failure Modes

- Treating color-type success as full APNG/PNG conformance.
- Decoding indexed-color frames without requiring PLTE.
- Accepting tRNS on color types that already carry alpha.
- Forgetting that APNG `fdAT` frame data inherits the static image color type.

## Integration Risk

Medium. Color-type reconstruction is needed before production APNG import, but
this remains a bounded lab subset that must be combined with broader
image-data and external-editor evidence.

## License Status

No external code selected. The W3C PNG specification is used as the format
anchor.

## Prototype Result

Stage 0 color-type frame-data matrix completed on 2026-05-14.

```txt
profile_count: 3
case_count: 15
case_success_count: 15
invalid_probe_count: 4
invalid_probe_rejected_count: 4
color_type_family_count: 5
color_types_covered: [0, 2, 3, 4, 6]
```

## Decision

Keep as a bounded APNG image-data proof. It closes only 8-bit non-interlaced
APNG color-type reconstruction, palette/tRNS reconstruction, alpha-channel
reconstruction, and invalid color metadata rejection for deterministic
fixtures.

Full APNG/PNG conformance, live external editor validation, final carrier
selection, package runtime integration, manual readability calibration, and
profile-weighted evolution remain blocked.

## Go/No-Go Gate

Promote APNG image-data policy only after this color-type matrix is combined
with remaining APNG/PNG fixtures and live editor open-save evidence.
