# Aseprite Palette/Slice Semantics

Date: 2026-05-14

## Objective

Continue the workshop editor research plan by broadening Aseprite/LibreSprite
chunk coverage beyond the tags/layers subset. This report proves native Palette
Chunk `0x2019` colors and Slice Chunk `0x2022` organ bounds for the current
Stage 0 grid corpus. It does not claim live external editor validation,
arbitrary Aseprite schemas, tilemap/tileset support, linked cels, or full
project-format coverage.

## Source Position

`docs/02-research_plan.md` defines the workshop as a semantic pixel editor:
normal sprite editors cannot express mutation weights, organ roles, survival
semantics, or SLIP constraints by themselves. The compatibility matrix
therefore requires each editor-format proof to preserve explicit Mechagotchi
semantics rather than infer them from pixels alone.

## External Anchors

- Aseprite file-format specification:
  https://github.com/aseprite/aseprite/blob/main/docs/ase-file-specs.md
- Aseprite slice documentation:
  https://www.aseprite.org/docs/slices/
- LibreSprite GitHub:
  https://github.com/LibreSprite/LibreSprite

The Aseprite specification anchors the Palette Chunk `0x2019`, Slice Chunk
`0x2022`, Layer Chunk `0x2004`, Cel Chunk `0x2005`, Tags Chunk `0x2018`, and
User Data Chunk `0x2020` layouts. Aseprite slice documentation anchors slices
as named regions with bounds and pivot-style metadata. LibreSprite remains a
compatibility boundary and workflow reference; no GPL editor code is embedded.

## Prototype

Implemented:

- `labs/workshop_editor/aseprite_palette_slice_semantics.py`
- `labs/workshop_editor/test_aseprite_palette_slice_semantics.py`
- `data/workshop_editor/aseprite_palette_slice_semantics_stage0.json`
- `data/workshop_editor/aseprite_palette_slice_semantics_stage0/`
- `research/algorithm_cards/aseprite_palette_slice_semantics.md`

The lab writes one constrained `.aseprite` carrier per current valid SLIP
profile:

```txt
3 frames
3 semantic layers: body, sensors, expression
3 layer User Data chunks
3 frame tags: idle_loop, sensor_blink, expression_pulse
1 Palette Chunk with 3 SLIP palette entries
3 Slice Chunks for core, sensors, and expression bounds
9 compressed RGBA cels
```

Each import validates:

- ASE header and frame header boundaries;
- Palette Chunk color, alpha, order, and native name semantics;
- Slice Chunk frame key, positive bounds, in-sprite bounds, and pivot
  semantics;
- semantic layer names and layer User Data bindings;
- Tags Chunk frame ranges and documented loop-direction values;
- sidecar hash;
- canonical project hash after User Data removal;
- per-frame/per-layer decompressed cel visual hashes;
- restored grid validity and SLIP alignment.

## Results

```txt
profile_count: 3
palette_slice_roundtrip_success_count: 3
invalid_probe_count: 5
invalid_probe_rejected_count: 5
palette_slice_roundtrip_success_rate: 1.0
mean_semantic_fidelity: 1.0
cel_visual_hash_preservation_rate: 1.0
invalid_probe_rejection_rate: 1.0
live_external_editor_verified: false
```

Invalid probes:

- missing Palette Chunk `0x2019`;
- tampered palette entry;
- missing Slice Chunk `0x2022`;
- slice bounds outside the sprite dimensions;
- tampered embedded sidecar hash.

## Closed States

- `aseprite_palette_chunk_slip_colors_subset`
- `aseprite_slice_chunk_semantic_bounds_subset`
- `aseprite_palette_slice_sidecar_semantic_restore`
- `aseprite_palette_slice_hash_validation`
- `aseprite_palette_slice_multilayer_compressed_rgba_subset`

## Still Blocked

- `live_external_editor_rewrite_validation`
- `arbitrary_aseprite_project_schema_coverage`
- `advanced_tags_layers_timeline_schema_coverage`
- `aseprite_tilemap_tileset_schema_coverage`
- `full_project_format_coverage`
- `package_runtime_lifecycle_integration`
- `manual_readability_calibration`
- `profile_weighted_evolution`
- `community_profile_packs`

## Decision

Keep as an active Stage 0 prototype. The lab proves concrete palette and slice
semantics layered onto the prior tags/layers carrier. It does not prove live
editor rewrite behavior, arbitrary Aseprite project schemas, tilemap/tileset
coverage, linked cels, nested groups, package runtime integration, or full
project-format coverage.

## Verification

Ran:

```powershell
python -B -m unittest .\labs\workshop_editor\test_aseprite_palette_slice_semantics.py
python -B .\labs\workshop_editor\aseprite_palette_slice_semantics.py
```

The focused test suite passed, and the artifact generator produced 3/3 valid
round trips with 5/5 invalid probes rejected.

## Next Step

Collect live external Aseprite/LibreSprite open-save fixtures or broaden the
Aseprite chunk/schema corpus with tilemaps, tilesets, linked cels, nested
groups, tag user data, and timeline variants before removing any remaining
project-format blockers.
