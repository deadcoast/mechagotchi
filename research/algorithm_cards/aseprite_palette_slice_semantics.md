# Aseprite Palette/Slice Semantics

## Purpose

Encode and recover SLIP palette colors and organ-bounding regions in an
Aseprite/LibreSprite `.aseprite` carrier without claiming arbitrary project
schema coverage or live editor rewrite preservation.

## Binary Contract

The writer emits a constrained `.aseprite` carrier:

```txt
ASE header 0xA5E0
3 frame headers 0xF1FA
1 Palette Chunk 0x2019 in frame 0
3 Layer Chunks 0x2004 in frame 0
3 layer-associated User Data Chunks 0x2020 in frame 0
1 Tags Chunk 0x2018 in frame 0
3 Slice Chunks 0x2022 in frame 0
9 Cel Chunks 0x2005, compressed RGBA, 3 layers x 3 frames
```

The embedded metadata binds:

```txt
canonical_project_hash = sha256(project after User Data chunk removal)
cel_visual_hashes = sha256(decompressed RGBA bytes per frame/layer cel)
sidecar_hash = sha256(canonical sidecar JSON)
palette_semantics = ordered SLIP palette colors and native palette names
slice_semantics = named core/sensors/expression bounds and pivots
```

## Inputs

- Valid SLIP profile
- Generated profile-aligned grid
- SLIP palette colors
- Organ cell coordinates for core, sensors, and expression

## Outputs

- `.aseprite` files with Palette Chunk `0x2019` and Slice Chunk `0x2022`
- Decoded palette, slice, layer, tag, user-data, and compressed cel summaries
- Restored SLIP-aligned semantic grids
- Invalid-probe rejection report

## Strengths

- Proves native palette-color storage for the current SLIP palette subset.
- Proves named slice bounds for semantic organs using the documented slice
  chunk and pivot fields.
- Reuses the tags/layers sidecar restore path while adding palette and slice
  validation before canonical-hash acceptance.
- Avoids embedding LibreSprite or Aseprite editor code.

## Weaknesses

- Covers one explicit three-frame, three-layer, three-slice project subset
  only.
- Does not cover live Aseprite/LibreSprite open-save behavior.
- Does not cover tilemaps, tilesets, linked cels, nested groups, arbitrary
  timelines, old palette chunks, or full project-format coverage.

## Failure Modes

- Missing Palette Chunk must reject import.
- Palette entries that differ from embedded SLIP palette semantics must reject
  import.
- Missing Slice Chunk semantics must reject import.
- Slice bounds outside sprite dimensions must reject import.
- Tampered embedded sidecar must reject import.
- Treating this subset as arbitrary Aseprite project coverage would overclaim
  the lab.

## Integration Risk

High.

## License Status

No external code selected. The Aseprite file-format document is used as a
binary layout anchor, and Aseprite slice documentation is used as a behavior
anchor. LibreSprite remains a compatibility boundary; GPL editor code is not
embedded.

## Prototype Result

Stage 0 Aseprite/LibreSprite palette/slice semantics proof completed on
2026-05-14.

```txt
profile_count: 3
palette_slice_roundtrip_success_count: 3
invalid_probe_rejected_count: 5
palette_slice_roundtrip_success_rate: 1.0
mean_semantic_fidelity: 1.0
cel_visual_hash_preservation_rate: 1.0
invalid_probe_rejection_rate: 1.0
live_external_editor_verified: false
```

## Decision

Keep as active prototype for the Stage 0 Aseprite/LibreSprite palette/slice
semantics subset. This closes only the explicit Palette Chunk `0x2019` and
Slice Chunk `0x2022` subset layered onto the existing tags/layers proof. It
does not close live editor validation, arbitrary Aseprite schema coverage,
tilemap/tileset coverage, linked cels, advanced tags/layers timeline schema
coverage, package runtime integration, manual readability calibration, or full
project-format coverage.

## Go/No-Go Gate

Promote only after live external Aseprite/LibreSprite open-save fixtures and
broader chunk/schema fixtures for tilemaps, tilesets, linked cels, nested
groups, tag user data, and timeline variants preserve semantic restore and
visual hash validation.
