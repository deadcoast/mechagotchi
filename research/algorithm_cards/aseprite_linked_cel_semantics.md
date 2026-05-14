# Aseprite Linked-Cel Semantics

## Purpose

Encode and recover Aseprite/LibreSprite linked-cel frame targets in a native
`.aseprite` carrier without claiming arbitrary project schema coverage or live
editor rewrite preservation.

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
5 Cel Chunks 0x2005, compressed RGBA image type 2
4 Cel Chunks 0x2005, linked cel type 1
```

The embedded metadata binds:

```txt
canonical_project_hash = sha256(project after User Data chunk removal)
cel_visual_hashes = sha256(decompressed or resolved RGBA bytes per frame/layer cel)
linked_cel_semantics = frame/layer to linked-frame target map
sidecar_hash = sha256(canonical sidecar JSON)
palette_semantics = ordered SLIP palette colors and native palette names
slice_semantics = named core/sensors/expression bounds and pivots
```

## Inputs

- Valid SLIP profile
- Generated profile-aligned grid
- Semantic layers for core, sensors, and expression
- Three-frame carrier where unchanged cels can link to frame 0 targets

## Outputs

- `.aseprite` files with linked Cel Chunk `0x2005` type 1 targets
- Decoded linked-cel, compressed-cel, palette, slice, layer, tag, and user-data summaries
- Restored SLIP-aligned semantic grids
- Invalid-probe rejection report

## Strengths

- Proves linked-cel frame-target parsing and validation for the current
  deterministic three-frame subset.
- Resolves linked cels to same-layer compressed RGBA target hashes before
  accepting semantic restore.
- Reuses the palette/slice tags/layers carrier while adding linked-cel target
  and visual-hash validation.
- Avoids embedding LibreSprite or Aseprite editor code.

## Weaknesses

- Covers one explicit three-frame, three-layer linked-cel subset only.
- Does not cover live Aseprite/LibreSprite open-save behavior.
- Does not cover tilemaps, tilesets, nested groups, arbitrary timelines, old
  palette chunks, or full project-format coverage.

## Failure Modes

- Missing linked cel chunks must reject import.
- Linked cel target frame outside the project must reject import.
- Missing same-layer compressed cel target must reject import.
- Tampered compressed target visual bytes must reject import.
- Tampered embedded sidecar must reject import.
- Treating this subset as arbitrary Aseprite project coverage would overclaim
  the lab.

## Integration Risk

High.

## License Status

No external code selected. The Aseprite file-format document is used as a
binary layout anchor for Cel Chunk `0x2005`, linked cel type 1, and compressed
image cel type 2. LibreSprite remains a compatibility boundary; GPL editor code
is not embedded.

## Prototype Result

Stage 0 Aseprite/LibreSprite linked-cel semantics proof completed on
2026-05-14.

```txt
profile_count: 3
linked_cel_roundtrip_success_count: 3
invalid_probe_rejected_count: 5
linked_cel_roundtrip_success_rate: 1.0
mean_semantic_fidelity: 1.0
cel_visual_hash_preservation_rate: 1.0
linked_cel_target_resolution_rate: 1.0
invalid_probe_rejection_rate: 1.0
live_external_editor_verified: false
```

## Decision

Keep as active prototype for the Stage 0 Aseprite/LibreSprite linked-cel
semantics subset. This closes only the explicit Cel Chunk `0x2005` linked cel
type 1 target-resolution subset layered onto the palette/slice tags/layers
proof. It does not close live editor validation, arbitrary Aseprite schema
coverage, tilemap/tileset coverage, advanced tags/layers timeline schema
coverage, package runtime integration, manual readability calibration, or full
project-format coverage.

## Go/No-Go Gate

Promote only after live external Aseprite/LibreSprite open-save fixtures and
broader chunk/schema fixtures for tilemaps, tilesets, nested groups, tag user
data, and timeline variants preserve semantic restore and visual hash
validation.
