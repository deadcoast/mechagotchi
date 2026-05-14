# Aseprite Nested Timeline Semantics

## Purpose

Encode and recover a fixed Aseprite/LibreSprite nested layer and timeline
carrier without claiming arbitrary project schema coverage or live editor
rewrite preservation.

## Binary Contract

The writer emits a constrained `.aseprite` carrier:

```txt
ASE header 0xA5E0
4 frame headers 0xF1FA
5 Layer Chunks 0x2004 in frame 0
2 group layers, 3 normal image layers
Layer child levels 0, 1, 1, 2, 2
5 layer-associated User Data Chunks 0x2020
1 Tags Chunk 0x2018 with directions 0, 1, 2, 3
4 tag-associated User Data Chunks 0x2020 with text and color
12 Cel Chunks 0x2005, compressed RGBA image type 2
```

The embedded metadata binds:

```txt
canonical_project_hash = sha256(project after User Data chunk removal)
cel_visual_hashes = sha256(decompressed RGBA bytes per frame/layer cel)
layer_semantics = group/image layer names, child levels, and roles
tag_semantics = frame ranges, directions, repeat counts, and User Data colors
sidecar_hash = sha256(canonical sidecar JSON)
```

## Inputs

- Valid SLIP profile
- Generated profile-aligned grid
- Semantic organ layers for core, sensors, and expression
- Four-frame timeline with deterministic alpha changes

## Outputs

- `.aseprite` files with nested group layers and tag User Data payloads
- Decoded layer hierarchy, tag loop, User Data, cel, and hash summaries
- Restored SLIP-aligned semantic grids
- Invalid-probe rejection report

## Strengths

- Proves group Layer Chunk `0x2004` type 1 parsing and child-level hierarchy
  validation for one deterministic nested project.
- Proves tag-associated User Data Chunk `0x2020` ordering after Tags Chunk
  `0x2018`.
- Covers all documented tag loop directions in one fixed Stage 0 carrier.
- Avoids embedding LibreSprite or Aseprite editor code.

## Weaknesses

- Covers one explicit four-frame, five-layer carrier only.
- Does not cover live Aseprite/LibreSprite open-save behavior.
- Does not cover arbitrary nested groups, external file references, multiple
  tilesets, property maps, multiple documents, or full project-format coverage.

## Failure Modes

- Missing group layers must reject import.
- Tampered child-level hierarchy must reject import.
- Missing tag User Data chunks must reject import.
- Invalid tag loop direction must reject import.
- Tampered tag User Data color must reject import.
- Tampered embedded sidecar must reject import.
- Treating this subset as arbitrary Aseprite project coverage would overclaim
  the lab.

## Integration Risk

High.

## License Status

No external code selected. The Aseprite file-format document is used as a
binary layout anchor for Layer Chunk `0x2004`, Tags Chunk `0x2018`, User Data
Chunk `0x2020`, and Cel Chunk `0x2005`. LibreSprite remains a compatibility
boundary; GPL editor code is not embedded.

## Prototype Result

Stage 0 Aseprite/LibreSprite nested timeline semantics proof completed on
2026-05-14.

```txt
profile_count: 3
nested_timeline_roundtrip_success_count: 3
invalid_probe_rejected_count: 6
nested_timeline_roundtrip_success_rate: 1.0
mean_semantic_fidelity: 1.0
cel_visual_hash_preservation_rate: 1.0
tag_user_data_preservation_rate: 1.0
invalid_probe_rejection_rate: 1.0
live_external_editor_verified: false
```

## Decision

Keep as active prototype for the Stage 0 Aseprite/LibreSprite nested timeline
semantics subset. This closes only the explicit group-layer, tag-User-Data, and
timeline loop-direction carrier. It does not close live editor validation,
arbitrary Aseprite schema coverage, package runtime integration, manual
readability calibration, or full project-format coverage.

## Go/No-Go Gate

Promote only after live external Aseprite/LibreSprite open-save fixtures and
broader project-schema fixtures for external file references, property maps,
multiple tilesets, multiple documents, and editor-authored variants preserve
semantic restore and hash validation.
