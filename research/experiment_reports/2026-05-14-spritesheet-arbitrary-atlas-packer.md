# Experiment Report: Spritesheet Arbitrary Atlas Packer

Date: 2026-05-14

## Objective

Continue the Stage 7 workshop-editor research by closing the local arbitrary
atlas packing gap left by the fixed layout and packed-runtime spritesheet labs.

This experiment tests whether current SLIP profile grids can be exported as
deterministic arbitrary rectangle atlases, reconstructed exactly from sidecar
metadata, and rejected safely under malformed packing metadata.

## Source Position

The research plan requires workshop authoring, export/import, visual
legibility, and modular profile compatibility evidence before package
promotion. Existing spritesheet labs already covered fixed strips, layout
variants, trim/rotation reconstruction, and metadata playback sampling.

The remaining local gap was arbitrary rectangle packing. This lab stays inside
`labs/` and `data/`; it does not create `packages/` or claim runtime package
integration.

## External Anchors

- Jukka Jylanki, *A Thousand Ways to Pack the Bin*, used as the MaxRects and
  rectangle bin-packing policy anchor:
  https://trszdev.github.io/maxrects-bssf-global-demo/RectangleBinPack.pdf
- libGDX TexturePacker documentation, used for texture-atlas workflow,
  rotation, whitespace stripping, padding, and atlas metadata context:
  https://libgdx.com/wiki/tools/texture-packer
- W3C PNG specification, used only because PNG remains the atlas image carrier:
  https://www.w3.org/TR/png-3/

## Implementation

Added:

- `labs/workshop_editor/test_spritesheet_arbitrary_atlas_packer.py`
- `labs/workshop_editor/spritesheet_arbitrary_atlas_packer.py`
- `data/workshop_editor/spritesheet_arbitrary_atlas_packer_stage0.json`
- `data/workshop_editor/spritesheet_arbitrary_atlas_packer_data.js`
- `data/workshop_editor/spritesheet_arbitrary_atlas_packer_stage0/`
- `research/algorithm_cards/spritesheet_arbitrary_atlas_packer.md`

The lab generates five canonical 8x8 source frames per profile, trims them
into variable rectangular regions, packs them through two policies, writes real
PNG atlas carriers, restores semantic grids from sidecars, reconstructs
canonical frames, and samples looped playback by duration boundaries.

## Results

```txt
profile_count: 3
packing_policy_count: 2
atlas_roundtrip_count: 6
atlas_roundtrip_success_count: 6
invalid_probe_count: 6
invalid_probe_rejected_count: 6
atlas_roundtrip_success_rate: 1.0
mean_semantic_fidelity: 1.0
mean_reconstructed_frame_fidelity: 1.0
mean_runtime_frame_fidelity: 1.0
mean_occupancy_rate: 0.682598
best_occupancy_policy: maxrects_best_short_side_fit
```

Rejected invalid probe families:

- `atlas_frame_rect_overlap`
- `atlas_frame_rect_out_of_bounds`
- `atlas_frame_hash_mismatch`
- `runtime_frame_duration_invalid`
- `atlas_packing_algorithm_unsupported`
- `atlas_frame_rotation_policy_violation`

## Closed States

- `arbitrary_atlas_packing_geometry`
- `maxrects_best_short_side_fit_policy`
- `shelf_height_desc_baseline_policy`
- `atlas_rotation_trim_reconstruction`
- `atlas_frame_overlap_and_bounds_rejection`
- `atlas_runtime_sidecar_playback_sampling`
- `atlas_sidecar_semantic_restore`

## Still Blocked

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
python -B -m unittest .\labs\workshop_editor\test_spritesheet_arbitrary_atlas_packer.py
ModuleNotFoundError: No module named 'spritesheet_arbitrary_atlas_packer'
```

GREEN:

```txt
python -B -m unittest .\labs\workshop_editor\test_spritesheet_arbitrary_atlas_packer.py
Ran 5 tests in 0.059s
OK
```

Artifact generation:

```txt
python -B .\labs\workshop_editor\spritesheet_arbitrary_atlas_packer.py
artifact_id: spritesheet_arbitrary_atlas_packer_stage0
atlas_roundtrip_success_count: 6
invalid_probe_rejected_count: 6
```

## Decision

`prototype_spritesheet_arbitrary_atlas_packer`.

This lab closes arbitrary atlas packing as a Stage 0 local geometry and
sidecar-reconstruction proof. It does not close production renderer playback
or live external editor validation.
