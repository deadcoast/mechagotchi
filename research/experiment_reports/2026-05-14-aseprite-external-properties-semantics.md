# Aseprite External Properties Semantics

Date: 2026-05-14

## Objective

Continue the workshop editor research plan by broadening Aseprite/LibreSprite
chunk coverage beyond the fixed nested timeline carrier. This report proves
Color Profile Chunk `0x2007`, External Files Chunk `0x2008`, User Data Chunk
`0x2020` property maps, and Cel Extra Chunk `0x2006` precise bounds for the
current Stage 0 grid corpus. It does not claim live external editor validation,
arbitrary Aseprite schemas, multiple document variants, or full project-format
coverage.

## Source Position

`docs/02-research_plan.md` defines the workshop as a semantic pixel editor:
normal sprite editors cannot express mutation weights, organ roles, survival
semantics, or SLIP constraints by themselves. This lab treats color profiles,
external file entries, extension property maps, and cel precision data as
editor-native carrier structures while Mechagotchi semantic restore remains
bound to explicit metadata.

## External Anchors

- Aseprite file-format specification:
  https://github.com/aseprite/aseprite/blob/main/docs/ase-file-specs.md
- Aseprite properties API documentation:
  https://aseprite.org/api/properties
- Aseprite color-profile documentation:
  https://www.aseprite.org/docs/color-profile/
- Aseprite files documentation:
  https://www.aseprite.org/docs/files
- LibreSprite GitHub:
  https://github.com/LibreSprite/LibreSprite

The Aseprite specification anchors Color Profile Chunk `0x2007`, External
Files Chunk `0x2008`, Cel Extra Chunk `0x2006`, User Data Chunk `0x2020`
property maps, and compressed image Cel Chunk `0x2005` payloads. The API docs
anchor user-defined and extension-defined property workflow boundaries.
LibreSprite remains a compatibility boundary and workflow reference; no GPL
editor code is embedded.

## Prototype

Implemented:

- `labs/workshop_editor/aseprite_external_properties_semantics.py`
- `labs/workshop_editor/test_aseprite_external_properties_semantics.py`
- `data/workshop_editor/aseprite_external_properties_semantics_stage0.json`
- `data/workshop_editor/aseprite_external_properties_semantics_stage0/`
- `research/algorithm_cards/aseprite_external_properties_semantics.md`

The lab writes one constrained `.aseprite` carrier per current valid SLIP
profile:

```txt
2 frames
1 Color Profile Chunk 0x2007, sRGB fixed-gamma subset
1 External Files Chunk 0x2008 with palette, tileset, and extension entries
1 User Data Chunk 0x2020 with text, color, and two property maps
2 compressed RGBA cels
2 Cel Extra Chunks 0x2006 with precise bounds
```

Each import validates:

- ASE header and frame header boundaries;
- color profile type, flags, and fixed-gamma semantics;
- external file entry IDs, types, and names;
- user and extension property maps, including extension key `303`;
- cel visual hashes;
- Cel Extra precise bounds;
- sidecar hash;
- canonical project hash after User Data removal;
- restored grid validity and SLIP alignment.

## Results

```txt
profile_count: 3
external_properties_roundtrip_success_count: 3
invalid_probe_count: 6
invalid_probe_rejected_count: 6
external_properties_roundtrip_success_rate: 1.0
mean_semantic_fidelity: 1.0
cel_visual_hash_preservation_rate: 1.0
property_map_preservation_rate: 1.0
invalid_probe_rejection_rate: 1.0
live_external_editor_verified: false
```

Invalid probes:

- missing External Files chunk;
- tampered color profile type;
- missing User Data property maps;
- tampered extension property-map key;
- tampered Cel Extra precise bounds;
- tampered embedded sidecar hash.

## Closed States

- `aseprite_color_profile_subset`
- `aseprite_external_file_reference_subset`
- `aseprite_user_data_properties_subset`
- `aseprite_extension_property_map_subset`
- `aseprite_cel_extra_precise_bounds_subset`
- `aseprite_external_properties_hash_validation`

## Still Blocked

- `live_external_editor_rewrite_validation`
- `arbitrary_aseprite_project_schema_coverage`
- `multiple_aseprite_document_variants`
- `full_project_format_coverage`
- `package_runtime_lifecycle_integration`
- `manual_readability_calibration`
- `profile_weighted_evolution`
- `community_profile_packs`

## Decision

Keep as an active Stage 0 prototype. The lab proves concrete color-profile,
external-file, property-map, extension-key, and Cel Extra parsing for one
deterministic carrier. It does not prove live editor rewrite behavior,
arbitrary Aseprite project schemas, multiple color-depth documents, package
runtime integration, or full project-format coverage.

## Verification

Ran:

```powershell
python -B -m unittest .\labs\workshop_editor\test_aseprite_external_properties_semantics.py
python -B .\labs\workshop_editor\aseprite_external_properties_semantics.py
```

The focused test suite passed, and the artifact generator produced 3/3 valid
round trips with 6/6 invalid probes rejected.

## Next Step

Collect live external Aseprite/LibreSprite open-save fixtures or broaden the
Aseprite schema corpus with multiple color-depth document variants,
editor-authored projects, and external asset resolution before removing any
remaining project-format blockers.
