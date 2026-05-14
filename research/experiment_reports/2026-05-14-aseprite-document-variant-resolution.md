# Aseprite Document Variant Resolution

Date: 2026-05-14

## Objective

Continue the workshop editor research plan by broadening Aseprite/LibreSprite
coverage beyond fixed 32 bpp RGBA carriers. This report proves deterministic
indexed 8 bpp, grayscale-alpha 16 bpp, and RGBA 32 bpp document variants plus
hash-checked External Files Chunk asset resolution for the current Stage 0
grid corpus. It does not claim live external editor validation, arbitrary
Aseprite schemas, arbitrary external asset resolution, package runtime
integration, or full project-format coverage.

## Source Position

`docs/02-research_plan.md` defines the workshop as a semantic pixel editor:
normal sprite editors cannot express mutation weights, organ roles, survival
semantics, or SLIP constraints by themselves. This lab treats Aseprite color
depths and external-file references as editor-native carrier structures while
semantic restore remains bound to explicit Mechagotchi metadata and sidecar
hashes.

## External Anchors

- Aseprite file-format specification:
  https://github.com/aseprite/aseprite/blob/main/docs/ase-file-specs.md
- Aseprite files documentation:
  https://www.aseprite.org/docs/files
- LibreSprite GitHub:
  https://github.com/LibreSprite/LibreSprite

The Aseprite specification anchors 8/16/32 bpp pixel payload sizes, compressed
image Cel Chunk `0x2005`, Palette Chunk `0x2019`, and External Files Chunk
`0x2008`. LibreSprite remains a compatibility boundary and workflow
reference; no GPL editor code is embedded.

## Prototype

Implemented:

- `labs/workshop_editor/aseprite_document_variant_resolution.py`
- `labs/workshop_editor/test_aseprite_document_variant_resolution.py`
- `data/workshop_editor/aseprite_document_variant_resolution_stage0.json`
- `data/workshop_editor/aseprite_document_variant_resolution_stage0/`
- `research/algorithm_cards/aseprite_document_variant_resolution.md`

The lab writes three constrained `.aseprite` carriers per current valid SLIP
profile:

```txt
indexed_8: color_depth_bpp 8, 1 byte per pixel, Palette Chunk 0x2019
grayscale_alpha_16: color_depth_bpp 16, 2 bytes per pixel
rgba_32: color_depth_bpp 32, 4 bytes per pixel
all variants: External Files Chunk 0x2008, User Data Chunk 0x2020,
Layer Chunk 0x2004, compressed image Cel Chunk 0x2005 type 2
```

Each import validates:

- ASE header and frame header boundaries;
- supported color depth and byte-per-pixel contract;
- external file entry IDs, types, names, and generated payload hashes;
- indexed palette hash for 8 bpp documents;
- decompressed variant pixel hash;
- sidecar hash;
- canonical project hash after User Data removal;
- restored grid validity and SLIP alignment.

## Results

```txt
profile_count: 3
document_variant_roundtrip_count: 9
document_variant_roundtrip_success_count: 9
invalid_probe_count: 6
invalid_probe_rejected_count: 6
document_variant_roundtrip_success_rate: 1.0
mean_semantic_fidelity: 1.0
variant_pixel_hash_preservation_rate: 1.0
external_asset_resolution_rate: 1.0
invalid_probe_rejection_rate: 1.0
live_external_editor_verified: false
```

Invalid probes:

- missing External Files chunk;
- tampered external asset payload hash;
- unsupported color depth;
- tampered indexed palette;
- tampered compressed cel payload;
- tampered embedded sidecar hash.

## Closed States

- `aseprite_indexed_8bpp_document_subset`
- `aseprite_grayscale_alpha_16bpp_document_subset`
- `aseprite_rgba_32bpp_document_subset`
- `aseprite_external_asset_resolution_subset`
- `aseprite_document_variant_hash_validation`

## Still Blocked

- `live_external_editor_rewrite_validation`
- `arbitrary_aseprite_project_schema_coverage`
- `arbitrary_external_asset_resolution`
- `full_project_format_coverage`
- `package_runtime_lifecycle_integration`
- `manual_readability_calibration`
- `profile_weighted_evolution`
- `community_profile_packs`

## Decision

Keep as an active Stage 0 prototype. The lab proves concrete color-depth
document variants and deterministic hash-checked external asset resolution for
one generated carrier family. It does not prove live editor rewrite behavior,
arbitrary Aseprite project schemas, arbitrary external asset resolution,
package runtime integration, or full project-format coverage.

## Verification

Ran:

```powershell
python -B -m unittest .\labs\workshop_editor\test_aseprite_document_variant_resolution.py
python -B .\labs\workshop_editor\aseprite_document_variant_resolution.py
```

The focused test suite passed, and the artifact generator produced 9/9 valid
round trips with 6/6 invalid probes rejected.

## Next Step

Collect live external Aseprite/LibreSprite open-save fixtures or broaden the
Aseprite schema corpus with editor-authored projects and arbitrary external
asset fixtures before removing any remaining project-format blockers.
