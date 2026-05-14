# Aseprite Tags/Layers Semantics

## Purpose

Encode and recover Mechagotchi semantic layer roles and animation tag ranges in
an Aseprite/LibreSprite `.aseprite` carrier without claiming arbitrary project
schema coverage or live editor rewrite preservation.

## Binary Contract

The writer emits a constrained `.aseprite` carrier:

```txt
ASE header 0xA5E0
3 frame headers 0xF1FA
3 Layer Chunks 0x2004 in frame 0
3 layer-associated User Data Chunks 0x2020 in frame 0
1 Tags Chunk 0x2018 in frame 0
9 Cel Chunks 0x2005, compressed RGBA, 3 layers x 3 frames
```

The embedded metadata binds:

```txt
canonical_project_hash = sha256(project after User Data chunk removal)
cel_visual_hashes = sha256(decompressed RGBA bytes per frame/layer cel)
sidecar_hash = sha256(canonical sidecar JSON)
```

## Inputs

- Valid SLIP profile
- Generated profile-aligned grid
- Three semantic layer definitions: body, sensors, expression
- Three frame tags: `idle_loop`, `sensor_blink`, `expression_pulse`

## Outputs

- `.aseprite` files with layer User Data and frame tags
- Decoded layer, tag, user-data, and compressed cel summaries
- Restored SLIP-aligned semantic grids
- Invalid-probe rejection report

## Strengths

- Proves a real Tags Chunk `0x2018` writer/parser for the documented frame
  range and loop-direction fields.
- Proves multiple Layer Chunk `0x2004` entries and layer-indexed compressed
  Cel Chunk `0x2005` payloads across three frames.
- Associates Mechagotchi roles with layer User Data `0x2020` and validates the
  sidecar, canonical project hash, tag ranges, and per-cel visual hashes.
- Avoids embedding LibreSprite or Aseprite editor code.

## Weaknesses

- Covers one explicit three-frame, three-layer, three-tag project subset only.
- Does not cover live Aseprite/LibreSprite open-save behavior.
- Does not cover nested groups, tilemaps, tilesets, linked cels, tag user
  data, arbitrary timeline schemas, or full project-format coverage.
- Does not cover Palette Chunk `0x2019` or Slice Chunk `0x2022`; that subset
  is covered by the later palette/slice semantics lab.

## Failure Modes

- Missing Tags Chunk must reject import.
- Tag ranges outside the project frame count must reject import.
- Tampered embedded sidecar must reject import.
- Mutated compressed cel payload must reject import through visual hashes.
- Treating this subset as arbitrary Aseprite project coverage would overclaim
  the lab.

## Integration Risk

High.

## License Status

No external code selected. The Aseprite file-format document is used as a
binary layout anchor. LibreSprite remains a compatibility boundary; GPL editor
code is not embedded.

## Prototype Result

Stage 0 Aseprite/LibreSprite tags/layers semantics proof completed on
2026-05-14.

```txt
profile_count: 3
tags_layers_roundtrip_success_count: 3
invalid_probe_rejected_count: 4
tags_layers_roundtrip_success_rate: 1.0
mean_semantic_fidelity: 1.0
cel_visual_hash_preservation_rate: 1.0
invalid_probe_rejection_rate: 1.0
live_external_editor_verified: false
```

## Decision

Keep as active prototype for the Stage 0 Aseprite/LibreSprite tags/layers
semantics subset. This closes only the explicit three-frame, three-layer,
three-tag subset. It does not close live editor validation, arbitrary Aseprite
schema coverage, advanced tags/layers timeline schema coverage, package runtime
integration, manual readability calibration, or full project-format coverage.

## Go/No-Go Gate

Promote only after live external Aseprite/LibreSprite open-save fixtures,
broader nested layer/tag/timeline fixtures, tilemap/tileset fixtures, linked
cel fixtures, tag user data, and broader chunk/schema tests preserve semantic
restore and visual hash validation.
