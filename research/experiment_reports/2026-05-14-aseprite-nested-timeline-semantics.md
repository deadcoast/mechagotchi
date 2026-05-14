# Aseprite Nested Timeline Semantics

Date: 2026-05-14

## Objective

Continue the workshop editor research plan by broadening Aseprite/LibreSprite
chunk coverage beyond the fixed tilemap/tileset and linked-cel carriers. This
report proves group Layer Chunk `0x2004` type 1 hierarchy, tag-associated User
Data Chunk `0x2020` color/text payloads, and all documented Tags Chunk `0x2018`
loop directions for the current Stage 0 grid corpus. It does not claim live
external editor validation, arbitrary Aseprite schemas, or full project-format
coverage.

## Source Position

`docs/02-research_plan.md` defines the workshop as a semantic pixel editor:
normal sprite editors cannot express mutation weights, organ roles, survival
semantics, or SLIP constraints by themselves. This lab therefore treats nested
groups and tag timelines as editor-native organization and playback structures,
while Mechagotchi semantic restore remains bound to explicit metadata.

## External Anchors

- Aseprite file-format specification:
  https://github.com/aseprite/aseprite/blob/main/docs/ase-file-specs.md
- Aseprite tags documentation:
  https://www.aseprite.org/docs/tags/
- Aseprite layers documentation:
  https://www.aseprite.org/docs/layers/
- LibreSprite GitHub:
  https://github.com/LibreSprite/LibreSprite

The Aseprite specification anchors Layer Chunk `0x2004` group type and child
levels, Tags Chunk `0x2018` loop directions and repeat counts, tag-associated
User Data Chunk `0x2020` ordering, and compressed image Cel Chunk `0x2005`
payloads. LibreSprite remains a compatibility boundary and workflow reference;
no GPL editor code is embedded.

## Prototype

Implemented:

- `labs/workshop_editor/aseprite_nested_timeline_semantics.py`
- `labs/workshop_editor/test_aseprite_nested_timeline_semantics.py`
- `data/workshop_editor/aseprite_nested_timeline_semantics_stage0.json`
- `data/workshop_editor/aseprite_nested_timeline_semantics_stage0/`
- `research/algorithm_cards/aseprite_nested_timeline_semantics.md`

The lab writes one constrained `.aseprite` carrier per current valid SLIP
profile:

```txt
4 frames
2 group layers: Mechagotchi organs, Mechagotchi affordances
3 image layers: Core mass, Sensor affordances, Expression affordances
Child levels: 0, 1, 1, 2, 2
4 tags: Forward, Reverse, Ping-pong, Ping-pong Reverse
4 tag User Data chunks with text and color
12 compressed RGBA cels
```

Each import validates:

- ASE header and frame header boundaries;
- group and image layer types;
- child-level hierarchy;
- one layer User Data chunk per layer;
- one tag User Data chunk per tag after the Tags Chunk;
- tag frame ranges, loop directions, repeat counts, and User Data colors;
- cel visual hashes;
- sidecar hash;
- canonical project hash after User Data removal;
- restored grid validity and SLIP alignment.

## Results

```txt
profile_count: 3
nested_timeline_roundtrip_success_count: 3
invalid_probe_count: 6
invalid_probe_rejected_count: 6
nested_timeline_roundtrip_success_rate: 1.0
mean_semantic_fidelity: 1.0
cel_visual_hash_preservation_rate: 1.0
tag_user_data_preservation_rate: 1.0
invalid_probe_rejection_rate: 1.0
live_external_editor_verified: false
```

Invalid probes:

- missing group layers;
- tampered child-level hierarchy;
- missing tag User Data chunks;
- invalid tag loop direction;
- tampered tag User Data color;
- tampered embedded sidecar hash.

## Closed States

- `aseprite_nested_group_layer_subset`
- `aseprite_layer_child_level_hierarchy_subset`
- `aseprite_tag_user_data_subset`
- `aseprite_timeline_loop_direction_subset`
- `aseprite_nested_timeline_hash_validation`

## Still Blocked

- `live_external_editor_rewrite_validation`
- `arbitrary_aseprite_project_schema_coverage`
- `full_project_format_coverage`
- `package_runtime_lifecycle_integration`
- `manual_readability_calibration`
- `profile_weighted_evolution`
- `community_profile_packs`

## Decision

Keep as an active Stage 0 prototype. The lab proves concrete nested group and
tag timeline chunk parsing for one deterministic carrier. It does not prove
live editor rewrite behavior, arbitrary Aseprite project schemas, external file
references, multiple document variants, package runtime integration, or full
project-format coverage.

## Verification

Ran:

```powershell
python -B -m unittest .\labs\workshop_editor\test_aseprite_nested_timeline_semantics.py
python -B .\labs\workshop_editor\aseprite_nested_timeline_semantics.py
```

The focused test suite passed, and the artifact generator produced 3/3 valid
round trips with 6/6 invalid probes rejected.

## Next Step

Collect live external Aseprite/LibreSprite open-save fixtures or broaden the
Aseprite schema corpus with external file references, property maps, multiple
tilesets, multiple documents, and editor-authored variants before removing any
remaining project-format blockers.
