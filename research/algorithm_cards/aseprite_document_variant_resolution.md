# Aseprite Document Variant Resolution

## Purpose

Encode and recover deterministic Aseprite/LibreSprite document variants across
indexed 8 bpp, grayscale-alpha 16 bpp, and RGBA 32 bpp compressed cel payloads
with hash-checked External Files Chunk asset resolution. This is a bounded
Stage 0 schema-coverage lab, not a live editor or arbitrary project decoder.

## Binary Contract

The writer emits three constrained `.aseprite` carriers per current SLIP
profile:

```txt
ASE header 0xA5E0
1 frame header 0xF1FA
1 External Files Chunk 0x2008 with 3 entries
0 or 1 Palette Chunk 0x2019, required for indexed 8 bpp
1 Layer Chunk 0x2004
1 User Data Chunk 0x2020 with Mechagotchi metadata
1 Cel Chunk 0x2005, compressed image type 2
```

The embedded metadata binds:

```txt
variant_id = indexed_8 | grayscale_alpha_16 | rgba_32
color_depth_bpp = 8 | 16 | 32
bytes_per_pixel = 1 | 2 | 4
canonical_project_hash = sha256(project after User Data chunk removal)
variant_pixel_hash = sha256(decompressed variant pixel payload)
external_asset_manifest = sha256 generated palette, tileset, resolver assets
sidecar_hash = sha256(canonical sidecar JSON)
```

## Inputs

- Valid SLIP profile
- Generated profile-aligned grid
- Deterministic external palette, tileset summary, and resolver assets
- Aseprite file-format layouts for color depth, compressed cels, palette, and
  external files

## Outputs

- Nine `.aseprite` project files across the three current profiles and three
  document variants
- External palette, tileset, and resolver payloads
- Decoded variant, palette, external-file, cel, and hash summaries
- Restored SLIP-aligned semantic grids
- Invalid-probe rejection report

## Strengths

- Proves the Aseprite 8/16/32 bpp pixel-size split against deterministic cel
  payloads.
- Proves indexed Palette Chunk `0x2019` validation for the 8 bpp subset.
- Proves External Files Chunk `0x2008` entries can be resolved against
  generated assets by content hash.
- Separates deterministic external asset resolution from arbitrary external
  asset loading.
- Avoids embedding LibreSprite or Aseprite editor code.

## Weaknesses

- Covers one explicit single-frame, single-layer carrier per color depth.
- Does not collect live Aseprite/LibreSprite open-save fixtures.
- Does not parse arbitrary editor-authored projects.
- Does not resolve arbitrary external assets outside the generated manifest.
- Does not prove package runtime integration or full project-format coverage.

## Failure Modes

- Missing External Files chunk must reject import.
- Tampered external asset payload must reject import.
- Unsupported color depth must reject import.
- Tampered indexed palette must reject import.
- Tampered compressed cel payload must reject import.
- Tampered embedded sidecar must reject import.
- Treating this subset as arbitrary Aseprite project coverage would overclaim
  the lab.

## Integration Risk

High.

## License Status

No external code selected. The Aseprite file-format document is used as a
binary layout anchor for 8/16/32 bpp pixel sizes, compressed Cel Chunk
`0x2005`, Palette Chunk `0x2019`, and External Files Chunk `0x2008`.
LibreSprite remains a compatibility boundary; GPL editor code is not embedded.

## Prototype Result

Stage 0 Aseprite/LibreSprite document variant resolution proof completed on
2026-05-14.

```txt
profile_count: 3
document_variant_roundtrip_count: 9
document_variant_roundtrip_success_count: 9
invalid_probe_rejected_count: 6
document_variant_roundtrip_success_rate: 1.0
mean_semantic_fidelity: 1.0
variant_pixel_hash_preservation_rate: 1.0
external_asset_resolution_rate: 1.0
invalid_probe_rejection_rate: 1.0
live_external_editor_verified: false
```

## Decision

Keep as active prototype for deterministic Aseprite document-variant and
external-asset-resolution coverage. This closes only the indexed 8 bpp,
grayscale-alpha 16 bpp, RGBA 32 bpp, generated external asset resolution, and
variant hash-validation subsets. It does not close live editor validation,
arbitrary Aseprite schema coverage, arbitrary external asset resolution,
package runtime integration, manual readability calibration, or full
project-format coverage.

## Go/No-Go Gate

Promote only after live external Aseprite/LibreSprite open-save fixtures,
editor-authored schema fixtures, and broader external asset corpora preserve
semantic restore and hash validation without package-boundary regressions.
