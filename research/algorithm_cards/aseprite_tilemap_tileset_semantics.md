# Aseprite Tilemap/Tileset Semantics

## Purpose

Encode and recover Aseprite/LibreSprite tilemap and tileset semantics in a
native `.aseprite` carrier without claiming arbitrary project schema coverage or
live editor rewrite preservation.

## Binary Contract

The writer emits a constrained `.aseprite` carrier:

```txt
ASE header 0xA5E0
3 frame headers 0xF1FA
1 Palette Chunk 0x2019 in frame 0
1 Tileset Chunk 0x2023 in frame 0
1 Tilemap Layer Chunk 0x2004, layer type 2
1 tilemap-layer User Data Chunk 0x2020 in frame 0
1 Tags Chunk 0x2018 in frame 0
3 Slice Chunks 0x2022 in frame 0
3 Cel Chunks 0x2005, compressed tilemap cel type 3
```

The embedded metadata binds:

```txt
canonical_project_hash = sha256(project after User Data chunk removal)
tileset_image_hash = sha256(decompressed tileset RGBA bytes)
tilemap_hashes = sha256(decompressed tile ID matrices per frame)
tilemap_semantics = empty/core/sensors/expression tile ID mapping
sidecar_hash = sha256(canonical sidecar JSON)
```

## Inputs

- Valid SLIP profile
- Generated profile-aligned grid
- Semantic organ occupancy for core, sensors, and expression
- Three-frame tilemap carrier using one 1x1 semantic tileset

## Outputs

- `.aseprite` files with a Tileset Chunk `0x2023` and tilemap cels
- Decoded tilemap layer, tileset, tile ID, palette, slice, tag, and user-data summaries
- Restored SLIP-aligned semantic grids
- Invalid-probe rejection report

## Strengths

- Proves tilemap layer type 2, Tileset Chunk `0x2023`, and Tilemap Cel Chunk
  `0x2005` type 3 parsing for the current deterministic Stage 0 subset.
- Validates both decompressed tileset image hashes and per-frame tilemap ID
  hashes before accepting semantic restore.
- Keeps visual and full SLIP semantic restore bound to Mechagotchi metadata
  instead of pretending tile IDs alone carry all biology.
- Avoids embedding LibreSprite or Aseprite editor code.

## Weaknesses

- Covers one explicit three-frame, one-layer, one-tileset carrier only.
- Tile IDs encode empty/core/sensors/expression organ occupancy only.
- Does not cover live Aseprite/LibreSprite open-save behavior.
- Does not cover arbitrary nested groups, advanced timelines, multiple
  tilesets, external tilesets, or full project-format coverage.

## Failure Modes

- Missing Tileset Chunk `0x2023` must reject import.
- Missing Tilemap Cel Chunk `0x2005` type 3 payloads must reject import.
- Tampered tileset image bytes must reject import.
- Tampered tile IDs must reject import.
- Tampered embedded sidecar must reject import.
- Treating this subset as arbitrary Aseprite project coverage would overclaim
  the lab.

## Integration Risk

High.

## License Status

No external code selected. The Aseprite file-format document is used as a
binary layout anchor for Layer Chunk `0x2004`, Cel Chunk `0x2005` tilemap type
3, Tileset Chunk `0x2023`, and tile masks. LibreSprite remains a compatibility
boundary; GPL editor code is not embedded.

## Prototype Result

Stage 0 Aseprite/LibreSprite tilemap/tileset semantics proof completed on
2026-05-14.

```txt
profile_count: 3
tilemap_tileset_roundtrip_success_count: 3
invalid_probe_rejected_count: 5
tilemap_tileset_roundtrip_success_rate: 1.0
mean_semantic_fidelity: 1.0
tilemap_hash_preservation_rate: 1.0
tileset_image_hash_preservation_rate: 1.0
invalid_probe_rejection_rate: 1.0
live_external_editor_verified: false
```

## Decision

Keep as active prototype for the Stage 0 Aseprite/LibreSprite tilemap/tileset
semantics subset. This closes only the explicit Tilemap Layer type 2, Tileset
Chunk `0x2023`, and compressed Tilemap Cel Chunk `0x2005` type 3 subset. It
does not close live editor validation, arbitrary Aseprite schema coverage,
advanced tags/layers timeline schema coverage, package runtime integration,
manual readability calibration, or full project-format coverage.

## Go/No-Go Gate

Promote only after live external Aseprite/LibreSprite open-save fixtures and
broader chunk/schema fixtures for multiple tilesets, external tilesets, nested
groups, tag user data, and timeline variants preserve semantic restore and hash
validation.
