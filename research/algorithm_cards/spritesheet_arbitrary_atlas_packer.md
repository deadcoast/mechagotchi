# Algorithm Card: Spritesheet Arbitrary Atlas Packer

## Purpose

Pack trimmed Mechagotchi animation regions into arbitrary rectangular
spritesheet atlases, compare a shelf baseline against a MaxRects-style
best-short-side-fit policy, and verify sidecar-driven reconstruction and
runtime sampling.

## Mathematical Basis

The lab models texture atlas generation as deterministic two-dimensional
rectangle packing:

```txt
region_i = trim(canonical_frame_i)
placement_i = pack(region_i, policy, rotation_policy, padding)
valid_atlas = no_overlap(placements) and in_bounds(placements)
canonical_frame_i = paste(unrotate(crop(atlas, placement_i)), source_size, trim_i)
```

Two policies are tested:

- `shelf_height_desc`: height-descending shelf baseline.
- `maxrects_best_short_side_fit`: MaxRects-style placement minimizing short
  side waste, then long side waste, then deterministic coordinates.

Runtime playback remains a cumulative interval lookup over sidecar durations.

## Inputs

- Current valid SLIP profiles.
- First generated grid for each current valid profile.
- Five deterministic 8x8 canonical source frames per grid.
- Sidecar metadata with trim rectangles, packed rectangles, rotation flags,
  hashes, policy metadata, frame durations, and source-frame size.

## Outputs

- Two atlas PNGs per profile.
- Sidecar files with packing policy and reconstruction metadata.
- Policy comparison metrics.
- Runtime playback samples.
- Invalid-probe rejection report.

## Strengths

- Closes the local arbitrary rectangle packing gap without package code.
- Tests both a simple baseline and a stronger MaxRects-style policy.
- Verifies overlap, bounds, rotation-policy, duration, and hash rejection.
- Preserves SLIP/grid semantics through sidecar restore rather than treating
  atlas pixels as semantic truth.

## Weaknesses

- Uses generated lab frames, not editor-authored atlas exports.
- Only rectangular regions, 0/90-degree rotation, and one atlas page are
  covered.
- Runtime playback is metadata sampling, not production rendering.
- Does not prove live external editor rewrite preservation.

## Failure Modes

- Overlapping atlas rectangles must be rejected.
- Rectangles outside the atlas bounds must be rejected.
- Packed or reconstructed frame hash mismatches must be rejected.
- Invalid durations must be rejected before playback.
- Unsupported algorithm IDs must be rejected.
- Rotated frames must be rejected when the sidecar policy forbids rotation.

## Integration Risk

Medium.

## License Status

No external code selected. Jylanki's rectangle-packing report and libGDX
TexturePacker documentation are research anchors only.

## Prototype Result

Stage 0 arbitrary atlas packing proof completed on 2026-05-14.

```txt
profile_count: 3
packing_policy_count: 2
atlas_roundtrip_success_count: 6
invalid_probe_rejected_count: 6
atlas_roundtrip_success_rate: 1.0
mean_semantic_fidelity: 1.0
mean_reconstructed_frame_fidelity: 1.0
mean_runtime_frame_fidelity: 1.0
mean_occupancy_rate: 0.682598
best_occupancy_policy: maxrects_best_short_side_fit
```

## Decision

Keep as active prototype. This closes Stage 0 arbitrary atlas packing geometry
for the current profile corpus, but does not close production renderer
playback, live external editor rewrite validation, full project-format
coverage, package runtime integration, manual readability calibration, or
profile-weighted evolution.

## Go/No-Go Gate

Promote only after production runtime draw calls and real editor-exported atlas
fixtures can consume or reject the same metadata without losing Mechagotchi
sidecar semantics.
