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
- `../workshop_editor/slip_offspring_lineage_gate_stage0.json` records the
  bounded offspring and lineage-decision proof: 3 current profiles selected
  bounded child grids from runtime-selected parents, emitted 3 lineage
  decisions, produced 1 add-niche and 2 hold-parent outcomes, and rejected 2
  invalid offspring probes before the gate started.
- `../workshop_editor/slip_long_horizon_behavior_gate_stage0.json` records the
  held-out long-horizon behavior proof: 3 selected offspring survive the
  96-tick switchboard horizon, 18/18 held-out generated candidates survive
  switchboard care, 18/18 idle-neglect probes die before the horizon, and 2
  invalid long-horizon probes are rejected before the gate starts.
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
- `../workshop_editor/png_adam7_interlace_decoder_stage0.json` records the
  bounded Adam7 PNG sidecar decoder proof: 3 current profile 8-bit RGBA Adam7
  interlaced PNG round trips, seven reduced-image pass manifests, filters
  0..4, 6 invalid Adam7 probes rejected, and mean semantic and pixel fidelity
  of 1.0.
- `../workshop_editor/png_deep_color_sidecar_decoder_stage0.json` records the
  bounded PNG deep-color sidecar decoder proof: 33 current profile round trips
  across 1/2/4-bit greyscale, 1/2/4-bit indexed-color, 16-bit samples,
  greyscale-alpha color type 4, filters 0..4, 6 invalid deep-color probes
  rejected, and mean semantic and visual carrier fidelity of 1.0.
- `../workshop_editor/png_adam7_deep_color_cross_product_stage0.json` records
  the bounded Adam7/deep-color PNG proof: 33 current profile round trips across
  the deep-color subset, seven reduced-image pass manifests, filters 0..4, 7
  invalid cross-product probes rejected, and mean semantic and visual carrier
  fidelity of 1.0.
- `../workshop_editor/apng_sidecar_decoder_stage0.json` records the bounded
  APNG sidecar decoder proof: 3 current profile APNG round trips, two
  full-canvas 8-bit RGBA source frames per asset, `acTL`/`fcTL`/`fdAT`
  sequence validation, 5 invalid APNG probes rejected, and mean semantic and
  frame-pixel fidelity of 1.0.
- `../workshop_editor/apng_metadata_carrier_cross_product_stage0.json`
  records the bounded APNG metadata-carrier cross-product proof: 15 current
  profile round trips across `tEXt`, `zTXt`, uncompressed `iTXt`, compressed
  `iTXt`, and private `mgOT` carriers, 6 invalid carrier/APNG probes rejected,
  and mean semantic and frame-pixel fidelity of 1.0.
- `../workshop_editor/png_embedded_sidecar_writer_stage0.json` records the
  embedded PNG sidecar writer proof: 3 current profile PNG `tEXt` sidecar
  round trips, decoded pixel preservation, 3 invalid embedded metadata probes
  rejected, and mean semantic and pixel fidelity of 1.0.
- `../workshop_editor/png_textual_metadata_policy_stage0.json` records the
  bounded PNG textual metadata policy proof: 12 current profile round trips
  across `tEXt`, `zTXt`, uncompressed `iTXt`, and compressed `iTXt` sidecar
  carriers, 7 invalid metadata policy probes rejected, and mean semantic and
  pixel fidelity of 1.0.
- `../workshop_editor/png_private_chunk_policy_stage0.json` records the
  bounded app-private PNG chunk policy proof: 3 current profile round trips
  using one `mgOT` ancillary private unsafe-to-copy chunk, 7 invalid private
  chunk probes rejected, and a carrier-selection input matrix that keeps the
  final production carrier decision blocked.
- `../workshop_editor/png_private_chunk_preservation_matrix_stage0.json`
  records the simulated private-chunk editor preservation matrix: 18/18
  expected scenario outcomes across 3 profiles and 6 editor-behavior policies,
  6 recoverable imports, 6 metadata-loss outcomes, 6 stale/strict hash
  rejections, and live external editor validation still blocked.
- `../workshop_editor/spritesheet_sidecar_decoder_stage0.json` records the
  fixed horizontal spritesheet PNG sidecar decoder proof: 3 current profile
  spritesheet round trips, 2 invalid PNG/frame probes rejected, and mean
  semantic and frame-pixel fidelity of 1.0.
- `../workshop_editor/spritesheet_layout_variant_decoder_stage0.json` records
  the layout-variant spritesheet sidecar decoder proof: 12 current profile
  layout round trips across vertical strips, row-major matrix sheets,
  padded/guttered grids, and sparse atlas rects; 3 invalid layout probes
  rejected; and mean semantic and frame-pixel fidelity of 1.0.
- `../workshop_editor/spritesheet_packed_runtime_decoder_stage0.json` records
  the packed runtime spritesheet sidecar decoder proof: 3 current profile
  packed trim/rotation round trips, 3 runtime playback timelines, 4 invalid
  packed/runtime probes rejected, and mean semantic, reconstructed-frame, and
  runtime-frame fidelity of 1.0.
- `../workshop_editor/spritesheet_arbitrary_atlas_packer_stage0.json` records
  the arbitrary atlas packing proof: 6 current profile atlas round trips
  across shelf and MaxRects-style policies, 6 invalid atlas probes rejected,
  mean semantic/reconstructed-frame/runtime-frame fidelity of 1.0, and
  `maxrects_best_short_side_fit` selected as best occupancy policy for the
  fixed Stage 0 corpus.
- `../workshop_editor/spritesheet_multi_page_atlas_stage0.json` records the
  generated multi-page atlas proof: 3 current profile bundle round trips, page
  manifests, per-page hashes, frame-to-page bindings, runtime page-switch
  sampling, 6 invalid page/frame probes rejected, mean page count 3.0, and
  mean semantic/reconstructed-frame/runtime-frame fidelity of 1.0.
- `../workshop_editor/third_party_project_decoder_stage0.json` records the
  third-party project decoder boundary proof: 3 current profile project
  payloads covering Piskel JSON, Pixelorama `.pxo`, and Aseprite/LibreSprite
  header boundaries, 3 sidecar restores, 3 invalid project/binding probes
  rejected, and mean semantic fidelity of 1.0.
- `../workshop_editor/project_native_metadata_writer_stage0.json` records the
  project native metadata writer proof: 6 Piskel/Pixelorama project metadata
  round trips across the current profiles, 4 invalid native metadata probes
  rejected, and Aseprite/LibreSprite writing delegated to the dedicated User
  Data Chunk lab.
- `../workshop_editor/project_editor_rewrite_preservation_stage0.json` records
  the deterministic project editor rewrite proof: 6 Piskel/Pixelorama
  rewrite-simulation round trips across the current profiles, visual hash
  preservation, 3 invalid rewrite probes rejected, and live external editor
  validation kept blocked.
- `../workshop_editor/aseprite_user_data_chunk_writer_stage0.json` records the
  Aseprite/LibreSprite User Data Chunk writer proof: 3 one-frame, one-layer,
  compressed RGBA cel User Data round trips across the current profiles and 3
  invalid User Data probes rejected before semantic restore.
- `../workshop_editor/aseprite_tags_layers_semantics_stage0.json` records the
  Aseprite/LibreSprite tags/layers semantic proof: 3 three-frame, three-layer,
  compressed RGBA cel round trips with native Tags Chunk `0x2018`, layer User
  Data `0x2020`, and 4 invalid tags/layers probes rejected before semantic
  restore.
- `../workshop_editor/aseprite_palette_slice_semantics_stage0.json` records
  the Aseprite/LibreSprite palette/slice semantic proof: 3 three-frame,
  three-layer, compressed RGBA cel round trips with native Palette Chunk
  `0x2019` SLIP colors, Slice Chunk `0x2022` organ bounds, and 5 invalid
  palette/slice probes rejected before semantic restore.
- `../workshop_editor/aseprite_linked_cel_semantics_stage0.json` records the
  Aseprite/LibreSprite linked-cel semantic proof: 3 three-frame, three-layer
  round trips with 5 compressed RGBA cels, 4 linked Cel Chunk `0x2005` type 1
  frame targets, and 5 invalid linked-cel probes rejected before semantic
  restore.
- `../workshop_editor/aseprite_tilemap_tileset_semantics_stage0.json` records
  the Aseprite/LibreSprite tilemap/tileset semantic proof: 3 three-frame
  tilemap round trips with one Tilemap Layer type 2, one Tileset Chunk
  `0x2023`, three compressed Tilemap Cel Chunk `0x2005` type 3 payloads, and
  5 invalid tilemap/tileset probes rejected before semantic restore.
- `../workshop_editor/aseprite_nested_timeline_semantics_stage0.json` records
  the Aseprite/LibreSprite nested timeline semantic proof: 3 four-frame round
  trips with two group layers, child levels `0..2`, all four documented tag
  loop directions, tag-associated User Data color/text payloads, and 6 invalid
  nested/timeline probes rejected before semantic restore.
- `../workshop_editor/aseprite_external_properties_semantics_stage0.json`
  records the Aseprite/LibreSprite external-properties semantic proof: 3
  two-frame round trips with Color Profile Chunk `0x2007`, External Files
  Chunk `0x2008`, User Data Chunk `0x2020` property maps, Cel Extra Chunk
  `0x2006` precise bounds, and 6 invalid external/property probes rejected
  before semantic restore.
- `../workshop_editor/aseprite_document_variant_resolution_stage0.json`
  records the Aseprite/LibreSprite document-variant proof: 9 round trips
  across indexed 8 bpp, grayscale-alpha 16 bpp, and RGBA 32 bpp compressed
  cels with generated External Files Chunk `0x2008` assets resolved by hash,
  and 6 invalid variant/resolver probes rejected before semantic restore.
- `../workshop_editor/aseprite_external_asset_resolver_matrix_stage0.json`
  records the generated Aseprite/LibreSprite external-asset resolver matrix:
  36 round trips across 3 profiles, 3 document variants, and direct,
  relative-path, content-addressed, and multi-root resolver policies, with 5
  invalid resolver probes rejected before semantic restore.
- `../workshop_editor/png_apng_chunk_order_conformance_stage0.json` records
  the bounded PNG/APNG chunk-order conformance matrix: 12 valid static RGBA,
  split-IDAT, indexed PLTE/tRNS, and APNG static-first-frame cases across the
  current profiles, with 7 invalid ordering/cardinality probes rejected.
- `../workshop_editor/apng_partial_frame_playback_stage0.json` records the
  bounded APNG partial-frame playback matrix: 12 valid source-blend,
  alpha-over, background-disposal, and previous-disposal cases across the
  current profiles, with 5 invalid frame-control/data probes rejected.
- `../workshop_editor/apng_filtered_frame_data_stage0.json` records the
  bounded APNG filtered frame-data matrix: 15 valid filter-method-0 cases
  across filter types 0..4 and split `fdAT` frame-data reconstruction, with 4
  invalid filter/scanline/sequence probes rejected.
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

It does not yet cover package/runtime lifecycle behavior integration, completed
manual readability calibration, production renderer
playback, full third-party
project-format coverage, full APNG/PNG conformance beyond the bounded
chunk-order, partial-frame playback, and filtered frame-data matrices,
arbitrary Aseprite
project schema coverage, arbitrary
Aseprite external asset resolution, final PNG production carrier selection,
editor-authored Aseprite document variants, live external editor rewrite
validation, runtime JSON Schema dependency installation,
declared package dependency policy, or profile-weighted evolution. The current
SLIP long-horizon readability packet exists under `data/readability/`, but no
reviewer rows have been collected yet. The
multigeneration lineage runner exists as lab evidence under
`data/workshop_editor/`, not as package runtime state.
