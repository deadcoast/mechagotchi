# Experiment Report: Spritesheet Multi-Page Atlas

Date: 2026-05-14

## Objective

Continue the Stage 7 workshop-editor research by closing the generated
multi-page atlas fixture gap left by the arbitrary atlas packer.

This experiment tests whether current SLIP profile grids can be exported as a
multi-page atlas bundle, restored exactly from sidecar page/frame metadata, and
rejected safely under malformed page manifests, frame bindings, hashes, and
runtime order metadata.

## Source Position

The research plan requires workshop authoring, export/import, visual
legibility, and modular profile compatibility evidence before package
promotion. Existing spritesheet labs already covered fixed strips, layout
variants, trim/rotation reconstruction, metadata playback sampling, and
single-page arbitrary atlas packing.

The remaining local gap was generated multi-page atlas fixtures. This lab stays
inside `labs/` and `data/`; it does not create `packages/`, does not claim
production renderer playback, and does not claim editor-authored atlas import.

## External Anchors

- libGDX TexturePacker documentation, used for multi-page atlas workflow,
  texture bind/page grouping, rotation, whitespace stripping, padding, and
  atlas metadata context:
  https://libgdx.com/wiki/tools/texture-packer
- W3C PNG specification, used only because PNG remains the atlas page carrier:
  https://www.w3.org/TR/png-3/

## Implementation

Added:

- `labs/workshop_editor/test_spritesheet_multi_page_atlas.py`
- `labs/workshop_editor/spritesheet_multi_page_atlas.py`
- `data/workshop_editor/spritesheet_multi_page_atlas_stage0.json`
- `data/workshop_editor/spritesheet_multi_page_atlas_data.js`
- `data/workshop_editor/spritesheet_multi_page_atlas_stage0/`
- `research/algorithm_cards/spritesheet_multi_page_atlas.md`

The lab generates seven canonical 8x8 source frames per profile, trims them
into variable rectangular regions, packs them into bounded atlas pages through
a deterministic first-fit scan, writes real PNG page carriers, restores
semantic grids from sidecars, reconstructs canonical frames, and samples looped
playback across page switches.

## Results

```txt
profile_count: 3
bundle_roundtrip_count: 3
bundle_roundtrip_success_count: 3
invalid_probe_count: 6
invalid_probe_rejected_count: 6
bundle_roundtrip_success_rate: 1.0
mean_semantic_fidelity: 1.0
mean_reconstructed_frame_fidelity: 1.0
mean_runtime_frame_fidelity: 1.0
mean_page_count: 3.0
mean_frame_count: 7.0
```

Rejected invalid probe families:

- `atlas_page_missing`
- `atlas_page_hash_mismatch`
- `atlas_frame_page_unknown`
- `atlas_frame_rect_out_of_bounds`
- `atlas_frame_hash_mismatch`
- `runtime_frame_order_invalid`

## Closed States

- `multi_page_atlas_page_manifest`
- `multi_page_atlas_frame_page_binding`
- `multi_page_atlas_page_hash_validation`
- `multi_page_atlas_runtime_page_switch_sampling`
- `multi_page_atlas_sidecar_semantic_restore`
- `multi_page_atlas_invalid_probe_rejection`

## Still Blocked

- Editor-authored atlas fixtures.
- Production renderer playback.
- Live external editor rewrite validation.
- Full project-format coverage.
- Arbitrary Aseprite project schema coverage.
- Package runtime lifecycle integration.
- Manual readability calibration.
- Profile-weighted evolution.

## Verification

RED:

```txt
python -B -m unittest .\labs\workshop_editor\test_spritesheet_multi_page_atlas.py
ModuleNotFoundError: No module named 'spritesheet_multi_page_atlas'
```

GREEN:

```txt
python -B -m unittest .\labs\workshop_editor\test_spritesheet_multi_page_atlas.py
Ran 5 tests in 0.053s
OK
```

Artifact generation:

```txt
python -B .\labs\workshop_editor\spritesheet_multi_page_atlas.py
artifact_id: spritesheet_multi_page_atlas_stage0
bundle_roundtrip_success_count: 3
invalid_probe_rejected_count: 6
mean_page_count: 3.0
```

## Decision

`prototype_spritesheet_multi_page_atlas`.

This lab closes generated multi-page atlas page manifests and frame-to-page
bindings as a Stage 0 local sidecar-reconstruction proof. It does not close
editor-authored atlas fixtures, production renderer playback, or live external
editor validation.
