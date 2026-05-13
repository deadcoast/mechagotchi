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

It does not yet cover lifecycle-accurate behavior integration, external
image/project metadata sidecars, runtime JSON Schema dependency installation,
declared package dependency policy, or profile-weighted evolution.
