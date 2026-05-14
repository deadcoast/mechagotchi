# Algorithm Card: APNG Partial Frame Playback

## Purpose

Define a bounded Stage 0 APNG playback matrix for partial-frame offsets,
source/over blending, and dispose none/background/previous behavior.

## Mathematical Basis

The lab treats APNG playback as deterministic output-buffer evolution:

```txt
O_0 = transparent_black_canvas
display_i = composite(frame_i, O_i, x_offset, y_offset, blend_op)
O_{i+1} = dispose(display_i, O_i, frame_region, dispose_op)
```

It validates:

```txt
blend_op source = overwrite region
blend_op over = alpha composite source over current output buffer
dispose none = keep displayed output
dispose background = clear frame region to transparent black
dispose previous = restore output buffer before the frame
```

## Inputs

- Valid SLIP profile
- Generated profile-aligned grid
- 8-bit RGBA APNG static-first-frame carrier
- Four partial-frame playback scenarios

## Outputs

- APNG playback report
- Generated APNG fixtures for each current valid profile
- Display-frame hashes and after-disposal hashes
- Invalid frame-control probe results

## External Anchor

The W3C PNG Third Edition specification anchors the rules for:

- APNG output buffer initialization;
- frame width, height, and offset bounds;
- `APNG_DISPOSE_OP_NONE`, `APNG_DISPOSE_OP_BACKGROUND`, and
  `APNG_DISPOSE_OP_PREVIOUS`;
- `APNG_BLEND_OP_SOURCE` and `APNG_BLEND_OP_OVER`.

Source: <https://www.w3.org/TR/png-3/>

## Strengths

- Moves APNG evidence beyond full-canvas source frames.
- Measures displayed output and after-disposal output separately.
- Exercises both valid blend modes and all three valid disposal modes.
- Rejects out-of-bounds frames, invalid dispose values, invalid blend values,
  missing default IDAT, and missing frame data.

## Weaknesses

- Uses deterministic 8-bit RGBA filter-0 fixtures only.
- Does not cover interlaced APNG frames, alternate filters, split fdAT payloads,
  color-management chunks, or every ancillary interaction.
- Does not run live editor open-save preservation.
- Does not choose the final PNG/APNG production metadata carrier.

## Failure Modes

- Treating partial-frame playback success as full APNG/PNG conformance.
- Misapplying dispose previous as dispose none.
- Compositing alpha-over frames as direct source replacement.
- Accepting frame offsets that exceed the IHDR canvas.

## Integration Risk

Medium. The playback rules are needed before production APNG import, but they
remain a bounded lab subset and must be combined with broader image-data and
external-editor evidence.

## License Status

No external code selected. The W3C PNG specification is used as the format
anchor.

## Prototype Result

Stage 0 partial-frame playback matrix completed on 2026-05-14.

```txt
profile_count: 3
playback_case_count: 12
playback_case_success_count: 12
invalid_probe_count: 5
invalid_probe_rejected_count: 5
scenario_family_count: 4
```

## Decision

Keep as a bounded APNG partial-frame image-data proof. It closes only
partial-frame offset, source/over blend, background disposal, previous
disposal, and invalid control rejection for deterministic 8-bit RGBA fixtures.

Full APNG/PNG conformance, live external editor validation, final carrier
selection, package runtime integration, manual readability calibration, and
profile-weighted evolution remain blocked.

## Go/No-Go Gate

Promote APNG playback policy only after this partial-frame matrix is combined
with remaining APNG/PNG image-data fixtures and live editor open-save evidence.
