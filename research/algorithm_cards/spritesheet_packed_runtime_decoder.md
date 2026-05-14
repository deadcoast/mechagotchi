# Algorithm Card: Spritesheet Packed Runtime Decoder

## Purpose

Decode a sidecar-described packed spritesheet atlas with trimmed and rotated
frames, reconstruct canonical 8x8 Mechagotchi frames, and sample deterministic
runtime playback by frame durations.

## Mathematical Basis

Each packed frame is treated as an invertible transform:

```txt
canonical_frame = paste(unrotate(crop(sheet_rect)), source_size, trim_rect, background)
```

Runtime playback is a cumulative interval lookup:

```txt
effective_time = time_ms mod total_duration_ms
selected_frame = first frame where effective_time < cumulative_duration
```

Hashes bind both the packed crop and reconstructed canonical frame.

## Inputs

- Valid SLIP profile
- First generated grid for each current valid profile
- Three deterministic spritesheet frame renders
- Sidecar asset binding, frame rects, trim rects, rotation flags, durations,
  packed hashes, and canonical hashes

## Outputs

- Packed PNG spritesheet carrier
- Sidecar with trim/rotation/runtime playback binding
- Restored semantic grid
- Reconstructed canonical frame summaries
- Runtime playback timeline samples
- Invalid-probe rejection report

## Strengths

- Tests packed trim and 90-degree rotation directly instead of leaving them as
  broad future claims.
- Keeps Mechagotchi semantics in the sidecar rather than PNG pixels.
- Validates both packed crop hashes and reconstructed canonical hashes.
- Separates deterministic playback sampling from production rendering.

## Weaknesses

- Covers only the Stage 0 subset: 8x8 grids, 0/90-degree rotation, and
  sidecar-authored frame metadata.
- Does not parse editor-native tag, layer, cel, or chunk semantics.
- Does not write embedded PNG metadata or native project metadata.
- Does not prove package runtime lifecycle integration.

## Failure Modes

- Unsupported rotation metadata must be rejected.
- Trim rectangles outside the source frame must be rejected.
- Packed or reconstructed frame hash mismatches must be rejected.
- Zero or negative frame durations must be rejected.
- Treating playback samples as production rendering would overclaim the lab.

## Integration Risk

Medium.

## License Status

No external code selected. Aseprite and PNG sources are workflow/specification
anchors only.

## Prototype Result

Stage 0 packed runtime spritesheet proof completed on 2026-05-13.

```txt
profile_count: 3
packed_roundtrip_success_count: 3
invalid_probe_rejected_count: 4
packed_roundtrip_success_rate: 1.0
mean_semantic_fidelity: 1.0
mean_reconstructed_frame_fidelity: 1.0
mean_runtime_frame_fidelity: 1.0
invalid_probe_rejection_rate: 1.0
```

## Decision

Keep as active prototype. This closes the Stage 0 packed trim/rotation decoder
and sidecar runtime playback sampling gap, but does not close arbitrary atlas
packing, tags/layers, production renderer playback, full project-format
coverage, arbitrary Aseprite project schema coverage, live external editor rewrite
preservation, package runtime integration, manual readability calibration, or
profile-weighted evolution.

## Go/No-Go Gate

Promote only after production import surfaces can reject or consume real
editor-exported packed metadata without losing Mechagotchi sidecar semantics.
