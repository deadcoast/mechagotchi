# Aseprite User Data Chunk Writer

## Purpose

Embed and recover Mechagotchi semantic sidecar metadata inside an
Aseprite/LibreSprite `0x2020` User Data Chunk for a Stage 0 one-frame project
subset.

## Binary Contract

The writer emits a small `.aseprite` carrier:

```txt
ASE header 0xA5E0
frame header 0xF1FA
Layer Chunk 0x2004
User Data Chunk 0x2020, associated with the preceding layer
Cel Chunk 0x2005, compressed RGBA image
```

The embedded metadata separates byte identity from visual identity:

```txt
canonical_project_hash = sha256(project after User Data chunk removal)
cel_visual_hash = sha256(decompressed RGBA cel bytes)
sidecar_hash = sha256(canonical sidecar JSON)
```

## Inputs

- Valid SLIP profile
- Generated profile-aligned grid
- Aseprite/LibreSprite one-frame project carrier
- Mechagotchi sidecar JSON

## Outputs

- `.aseprite` files with native User Data Chunk metadata
- Decoded layer, user-data, and compressed cel summaries
- Restored SLIP-aligned semantic grids
- Invalid-probe rejection report

## Strengths

- Proves a real binary chunk writer/reader for `0x2004`, `0x2020`, and
  compressed `0x2005` chunks.
- Keeps the embedded sidecar bound to canonical project bytes after User Data
  removal, avoiding self-referential hashing.
- Rejects missing User Data, sidecar hash mismatch, and visual cel mutation.
- Avoids embedding LibreSprite or Aseprite editor code.

## Weaknesses

- Covers one frame, one layer, one compressed RGBA cel, and one text User Data
  chunk only.
- Live external editor open-save validation is not proven.
- Advanced layer/tag/timeline variants, palettes, linked cels, tilemaps, and
  arbitrary editor schemas remain outside this proof. The separate Aseprite
  tags/layers semantics lab covers only one explicit three-frame, three-layer
  subset.

## Failure Modes

- Missing Mechagotchi User Data must reject import.
- Tampered embedded sidecar must reject import.
- Mutated compressed cel payload must reject import through the visual hash.
- Treating this subset as full Aseprite project coverage would overclaim the
  lab.

## Integration Risk

High.

## License Status

No external code selected. The Aseprite file-format document is used as a
binary layout anchor. LibreSprite remains a compatibility boundary; GPL editor
code is not embedded.

## Prototype Result

Stage 0 Aseprite/LibreSprite User Data Chunk writer proof completed on
2026-05-14.

```txt
profile_count: 3
user_data_roundtrip_success_count: 3
invalid_probe_rejected_count: 3
user_data_roundtrip_success_rate: 1.0
mean_semantic_fidelity: 1.0
cel_visual_hash_preservation_rate: 1.0
invalid_probe_rejection_rate: 1.0
live_external_editor_verified: false
```

## Decision

Keep as active prototype for the Aseprite/LibreSprite Stage 0 User Data subset.
This closes the User Data Chunk writer blocker only for the one-frame,
one-layer, compressed RGBA cel subset. It does not close live editor
validation, advanced tags/layers timeline schema coverage, arbitrary Aseprite
schema coverage, package runtime integration, manual readability calibration,
or full project-format coverage.

## Go/No-Go Gate

Promote only after live external Aseprite/LibreSprite open-save fixtures,
broader multi-layer/tag/timeline fixtures, and broader chunk/schema tests
preserve semantic restore and visual hash validation.
