# Aseprite Tags/Layers Semantics

Date: 2026-05-14

## Objective

Continue the workshop editor research plan by proving a narrower
Aseprite/LibreSprite tags/layers semantic subset after the one-frame User Data
Chunk writer. This report does not claim live external editor validation,
arbitrary Aseprite schemas, or full project-format coverage.

## Source Position

`docs/02-research_plan.md` defines the workshop as a semantic pixel editor:
normal sprite editors cannot express mutation weights, organ roles, survival
semantics, or SLIP constraints by themselves. The current compatibility matrix
therefore requires editor-format proofs to preserve Mechagotchi semantics
explicitly rather than infer them from pixels.

## External Anchors

- Aseprite file-format specification:
  https://github.com/aseprite/aseprite/blob/main/docs/ase-file-specs.md
- LibreSprite GitHub:
  https://github.com/LibreSprite/LibreSprite

The Aseprite specification anchors the little-endian ASE header, frame header,
Layer Chunk `0x2004`, Cel Chunk `0x2005`, Tags Chunk `0x2018`, and User Data
Chunk `0x2020` layouts. It also states that layer chunks define layer order in
the first frame, cels target layers by layer index, tags carry frame ranges and
loop direction, and User Data is associated with the last read chunk/object.
LibreSprite remains a compatibility boundary and workflow reference; no GPL
editor code is embedded.

## Prototype

Implemented:

- `labs/workshop_editor/aseprite_tags_layers_semantics.py`
- `labs/workshop_editor/test_aseprite_tags_layers_semantics.py`
- `data/workshop_editor/aseprite_tags_layers_semantics_stage0.json`
- `data/workshop_editor/aseprite_tags_layers_semantics_stage0/`
- `research/algorithm_cards/aseprite_tags_layers_semantics.md`

The lab writes one constrained `.aseprite` carrier per current valid SLIP
profile:

```txt
3 frames
3 semantic layers: body, sensors, expression
3 layer User Data chunks
3 frame tags: idle_loop, sensor_blink, expression_pulse
9 compressed RGBA cels
```

Each import validates:

- ASE header and frame header boundaries;
- semantic layer names and layer User Data bindings;
- Tags Chunk frame ranges and documented loop-direction values;
- sidecar hash;
- canonical project hash after User Data removal;
- per-frame/per-layer decompressed cel visual hashes;
- restored grid validity and SLIP alignment.

## Results

```txt
profile_count: 3
tags_layers_roundtrip_success_count: 3
invalid_probe_count: 4
invalid_probe_rejected_count: 4
tags_layers_roundtrip_success_rate: 1.0
mean_semantic_fidelity: 1.0
cel_visual_hash_preservation_rate: 1.0
invalid_probe_rejection_rate: 1.0
live_external_editor_verified: false
```

Invalid probes:

- missing Tags Chunk `0x2018`;
- tag range outside the project frame count;
- tampered embedded sidecar hash;
- mutated compressed cel visual payload.

## Closed States

- `aseprite_tags_layers_native_semantics_subset`
- `aseprite_frame_tags_semantic_ranges`
- `aseprite_layer_user_data_semantic_roles`
- `aseprite_multilayer_compressed_rgba_cel_subset`
- `aseprite_tags_layers_sidecar_semantic_restore`
- `aseprite_tags_layers_hash_validation`

## Still Blocked

- `live_external_editor_rewrite_validation`
- `arbitrary_aseprite_project_schema_coverage`
- `advanced_tags_layers_timeline_schema_coverage`
- `full_project_format_coverage`
- `package_runtime_lifecycle_integration`
- `manual_readability_calibration`
- `profile_weighted_evolution`
- `community_profile_packs`

## Decision

Keep as an active Stage 0 prototype. The lab proves a concrete tags/layers
semantic subset and removes the older generic tags/layers native project
semantics blocker from the active ledger. It does not prove live editor rewrite
behavior, arbitrary Aseprite project schemas, nested layer/tag/timeline
variants, tilemaps, tilesets, linked cels, package runtime integration, or
full project-format coverage. Palette Chunk `0x2019` and Slice Chunk `0x2022`
coverage is handled by the separate palette/slice semantics lab.

## Verification

Ran:

```powershell
python -B -m unittest .\labs\workshop_editor\test_aseprite_tags_layers_semantics.py
python -B .\labs\workshop_editor\aseprite_tags_layers_semantics.py
```

The focused test suite passed, and the artifact generator produced 3/3 valid
round trips with 4/4 invalid probes rejected.

## Next Step

Collect live external Aseprite/LibreSprite open-save fixtures or broaden the
Aseprite chunk/schema corpus with nested groups, tag user data, tilemaps,
tilesets, linked cels, and timeline variants before removing any remaining
project-format blockers.
