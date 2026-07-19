# Algorithm Card: APNG Sidecar Decoder

## Purpose

Prove a bounded APNG sidecar decoder for Mechagotchi workshop assets without
claiming full APNG or PNG conformance.

## Mathematical Basis

The Stage 0 APNG proof treats animation frames as visual carriers and keeps
semantics sidecar-bound:

```txt
asset_hash = sha256(APNG bytes)
frame_pixel_hash[i] = sha256(decoded RGBA frame i)
semantic_hash = sha256(sidecar semantic overlay)
```

Import succeeds only if the APNG asset binding matches, the `acTL`/`fcTL`/`fdAT`
sequence is valid for the bounded policy, every frame hash matches the sidecar
manifest, and the restored grid remains valid and SLIP-aligned.

## Inputs

- Valid SLIP profile
- Generated profile-aligned grid
- Two full-canvas 8-bit RGBA source frames
- APNG frame control manifest
- Mechagotchi semantic sidecar

## Outputs

- APNG file with `acTL`, `fcTL`, `IDAT`, and `fdAT` chunks
- Sidecar with APNG frame hash manifest
- Restored semantic grid
- Invalid-probe rejection report

## External Anchor

The W3C PNG specification anchors APNG chunk semantics:

- `acTL` declares animation frame count and play count;
- `fcTL` carries sequence number, frame rectangle, delay, disposal, and blend;
- `fdAT` carries animation frame data with sequence numbers;
- blend/disposal behavior affects how frames compose.

Source: <https://www.w3.org/TR/png-3/>

## Strengths

- Proves a real APNG chunk path rather than a spritesheet substitute.
- Validates animation sequence numbers across `fcTL` and `fdAT`.
- Rejects unsupported blend/disposal/partial-frame behavior under the bounded
  Stage 0 policy.
- Binds every decoded frame to a sidecar frame hash.
- Restores SLIP-aligned semantic grids without inferring organs from pixels.

## Weaknesses

- Supports two to sixteen full-canvas 8-bit RGBA source frames (the bound
  relaxed from exactly-two by cycle 18 H3 so the carrier can hold the
  engine's clip frames; the pulse export stays the two-frame floor).
- Does not support partial-frame offsets, `APNG_BLEND_OP_OVER`, disposal
  variants, Adam7-interlaced animation frames, or arbitrary APNGs.
- Does not prove live external editor preservation.
- Does not create package runtime code.

## Failure Modes

- Missing `acTL` must reject import.
- Non-consecutive `fcTL`/`fdAT` sequence numbers must reject import.
- Unsupported blend/disposal/partial frame controls must reject import.
- Frame hash mismatch must reject import.
- APNG asset hash mismatch must reject import before semantic restore.

## Integration Risk

Medium-high.

## License Status

No external code selected. The W3C PNG specification is used as the format
anchor.

## Prototype Result

Stage 0 bounded APNG sidecar decoder completed on 2026-05-14.

```txt
profile_count: 3
apng_roundtrip_success_count: 3
invalid_probe_rejected_count: 5
apng_roundtrip_success_rate: 1.0
mean_semantic_fidelity: 1.0
mean_frame_pixel_fidelity: 1.0
invalid_probe_rejection_rate: 1.0
```

## Decision

Keep as active prototype for bounded full-canvas APNG sidecar imports. This
closes only the Stage 0 APNG sidecar subset. Full APNG/PNG conformance, APNG
metadata carrier behavior is handled by a separate bounded cross-product lab.
Live external editor rewrite validation, final PNG production carrier
selection, package runtime integration, manual readability calibration, and
profile-weighted evolution remain blocked.

## Go/No-Go Gate

Promote only after broader APNG fixtures cover partial frames, blend/disposal
variants, external editor preservation, and package runtime import surfaces.
