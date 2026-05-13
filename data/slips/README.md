# SLIP Profile Corpus

This directory contains the first lab-level SLIP profiles.

The current scope is narrow:

- validate profile shape
- constrain palettes
- constrain body mass
- require organ roles
- cap mutation rates
- test generator alignment

Current generated compatibility evidence:

- `slip_schema_validation_stage0.json` records the Stage 0 schema
  validation run: 3 valid profiles accepted, 3 research examples accepted, 12
  failure cases rejected, and no unexpected acceptances or rejections.
- `slip_pydantic_contract_stage0.json` records the Pydantic v2 contract run:
  3 valid profiles accepted, 3 research examples accepted, 12 failure cases
  rejected, and no unexpected acceptances or rejections.
- `slip_schema_migration_dependency_gate_stage0.json` records the Stage 0
  migration/dependency decision: authored and generated schemas match on the
  core surface, only `0.1.0` is accepted without migration, and runtime
  `jsonschema` remains deferred until dependency declaration exists.
- `../workshop_editor/slip_authoring_panel_stage0.json` records the minimal
  workshop SLIP authoring panel proof: 3 current profile drafts accepted and
  3 invalid authoring probes rejected by the validator, Pydantic contract, and
  migration gate.
- `../workshop_editor/slip_behavior_mutation_preview_stage0.json` records the
  deterministic workshop preview proof: 3 current behavior previews, 3 bounded
  mutation previews, and 2 invalid preview probes rejected before activation.
- `../workshop_editor/slip_lifecycle_archive_effects_stage0.json` records the
  measured preview-to-effects bridge: 3 current profiles linked to lifecycle
  and extended archive measurements, 3 distinct preview/lifecycle/archive
  fingerprints, and 2 invalid or mismatched probes rejected before effects.
- `../workshop_editor/slip_runtime_selection_policy_stage0.json` records the
  runtime lifecycle/archive selection proof: 3 current profiles selected
  profile-weighted archive elites from switchboard lifecycle metrics, 3
  distinct selected grid ids, 3 distinct selected archive niches, and 2 invalid
  selection probes rejected before selection.
- `../workshop_editor/external_metadata_sidecar_stage0.json` records the
  external metadata sidecar strategy proof: 3 current profile sidecar round
  trips, 2 invalid binding probes rejected, and 5 adapter formats marked
  sidecar-required.
- `../workshop_editor/standard_image_sidecar_decoder_stage0.json` records the
  static RGBA PNG sidecar decoder proof: 3 current profile PNG round trips, 2
  invalid PNG/binding probes rejected, and mean semantic and pixel fidelity of
  1.0.
- `../workshop_editor/png_variant_sidecar_decoder_stage0.json` records the
  PNG variant sidecar decoder proof: 15 current profile PNG variant round
  trips across 8-bit non-interlaced color types 0/2/3/6 and filter types
  0..4, 3 invalid variant probes rejected, and mean semantic and visual
  carrier fidelity of 1.0.
- `../workshop_editor/spritesheet_sidecar_decoder_stage0.json` records the
  fixed horizontal spritesheet PNG sidecar decoder proof: 3 current profile
  spritesheet round trips, 2 invalid PNG/frame probes rejected, and mean
  semantic and frame-pixel fidelity of 1.0.
- `../workshop_editor/spritesheet_layout_variant_decoder_stage0.json` records
  the layout-variant spritesheet sidecar decoder proof: 12 current profile
  layout round trips across vertical strips, row-major matrix sheets,
  padded/guttered grids, and sparse atlas rects; 3 invalid layout probes
  rejected; and mean semantic and frame-pixel fidelity of 1.0.
- `../workshop_editor/third_party_project_decoder_stage0.json` records the
  third-party project decoder boundary proof: 3 current profile project
  payloads covering Piskel JSON, Pixelorama `.pxo`, and Aseprite/LibreSprite
  header boundaries, 3 sidecar restores, 3 invalid project/binding probes
  rejected, and mean semantic fidelity of 1.0.
- `failure_cases/` contains authored negative profile fixtures covering
  required fields, type errors, enums, unit intervals, additional properties,
  body-mass order, and boolean numeric mistakes.
- `multi_profile_generation_stage0/slip_multi_profile_generation_stage0.json`
  summarizes 150 generated candidates across the three valid profiles.
- `multi_profile_generation_stage0/slip_lcd_seed/` contains 50 valid,
  profile-aligned generated grids.
- `multi_profile_generation_stage0/slip_gray_stable/` contains 50 valid,
  profile-aligned generated grids.
- `multi_profile_generation_stage0/slip_amber_social/` contains 50 valid,
  profile-aligned generated grids.

It does not yet cover package/runtime lifecycle behavior integration, offspring
mutation selection, lineage replacement policy, held-out long-horizon behavior
tests, manual readability calibration, packed rotation/trim atlas handling,
runtime animation playback, full third-party project-format coverage,
Adam7/APNG/full PNG conformance, embedded/native metadata writers, runtime JSON
Schema dependency installation, declared package dependency policy, or
profile-weighted evolution.
