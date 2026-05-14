# Aseprite External Properties Semantics

## Purpose

Encode and recover a fixed Aseprite/LibreSprite carrier containing external
file references, color profile metadata, User Data property maps, and Cel Extra
precise bounds without claiming arbitrary project schema coverage or live
editor rewrite preservation.

## Binary Contract

The writer emits a constrained `.aseprite` carrier:

```txt
ASE header 0xA5E0
2 frame headers 0xF1FA
1 Color Profile Chunk 0x2007
1 External Files Chunk 0x2008 with 3 entries
1 Layer Chunk 0x2004
1 User Data Chunk 0x2020 with text, color, and property maps
2 Cel Chunks 0x2005, compressed RGBA image type 2
2 Cel Extra Chunks 0x2006 with precise bounds
```

The embedded metadata binds:

```txt
canonical_project_hash = sha256(project after User Data chunk removal)
cel_visual_hashes = sha256(decompressed RGBA bytes per frame/layer cel)
color_profile_semantics = sRGB fixed-gamma policy
external_file_semantics = palette, tileset, and extension-property entries
property_map_semantics = user map key 0 and extension map key 303
cel_extra_semantics = per-cel precise bounds
sidecar_hash = sha256(canonical sidecar JSON)
```

## Inputs

- Valid SLIP profile
- Generated profile-aligned grid
- Deterministic external file IDs for palette, tileset, and properties
- Two-frame compressed RGBA carrier

## Outputs

- `.aseprite` files with color profile, external file references, property maps,
  and Cel Extra chunks
- Decoded color profile, external files, property, cel, and hash summaries
- Restored SLIP-aligned semantic grids
- Invalid-probe rejection report

## Strengths

- Proves Color Profile Chunk `0x2007` parsing for one sRGB fixed-gamma subset.
- Proves External Files Chunk `0x2008` references for external palette,
  external tileset, and extension-property entry types.
- Proves User Data Chunk `0x2020` property-map parsing for user and
  extension-keyed maps.
- Proves Cel Extra Chunk `0x2006` precise bounds validation.
- Avoids embedding LibreSprite or Aseprite editor code.

## Weaknesses

- Covers one explicit two-frame, 32-bit RGBA carrier only.
- Does not dereference or execute external palette, tileset, or extension files.
- Does not cover live Aseprite/LibreSprite open-save behavior.
- Does not cover arbitrary property types, multiple color-depth documents,
  multiple documents, or full project-format coverage.

## Failure Modes

- Missing External Files chunk must reject import.
- Tampered color profile must reject import.
- Missing User Data property maps must reject import.
- Tampered extension property-map key must reject import.
- Tampered Cel Extra precise bounds must reject import.
- Tampered embedded sidecar must reject import.
- Treating this subset as arbitrary Aseprite project coverage would overclaim
  the lab.

## Integration Risk

High.

## License Status

No external code selected. The Aseprite file-format document is used as a
binary layout anchor for Color Profile Chunk `0x2007`, External Files Chunk
`0x2008`, Cel Extra Chunk `0x2006`, User Data Chunk `0x2020`, and Cel Chunk
`0x2005`. LibreSprite remains a compatibility boundary; GPL editor code is not
embedded.

## Prototype Result

Stage 0 Aseprite/LibreSprite external properties semantics proof completed on
2026-05-14.

```txt
profile_count: 3
external_properties_roundtrip_success_count: 3
invalid_probe_rejected_count: 6
external_properties_roundtrip_success_rate: 1.0
mean_semantic_fidelity: 1.0
cel_visual_hash_preservation_rate: 1.0
property_map_preservation_rate: 1.0
invalid_probe_rejection_rate: 1.0
live_external_editor_verified: false
```

## Decision

Keep as active prototype for the Stage 0 Aseprite/LibreSprite external
properties subset. This closes only the explicit color-profile,
external-file-reference, User Data property-map, extension property-map, and
Cel Extra precise-bounds carrier. It does not close live editor validation,
arbitrary Aseprite schema coverage, package runtime integration, manual
readability calibration, or full project-format coverage.

## Go/No-Go Gate

Promote only after live external Aseprite/LibreSprite open-save fixtures and
broader project-schema fixtures for arbitrary property maps, external asset
resolution, multiple color-depth documents, multiple documents, and
editor-authored variants preserve semantic restore and hash validation.
