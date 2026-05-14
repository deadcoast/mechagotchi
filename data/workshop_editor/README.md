# Workshop Editor Stage 0

Minimal semantic editor artifacts for testing Mechagotchi grid authoring.

- Source grid: mg_seed_001
- SLIP profile: slip_lcd_seed
- Export valid: True
- Export SLIP aligned: True
- Decision: prototype

## Round Trip

- Round-trip success: 1
- Semantic fidelity: 1.0
- Changed cells: 0
- Missing cells: 0
- Added cells: 0

## Additional Stage 0 Evidence

- `png_variant_sidecar_decoder_stage0.json` records 15/15 PNG variant sidecar
  round trips across 3 profiles, color types 0/2/3/6, and filter types 0..4.
- `png_adam7_interlace_decoder_stage0.json` records 3/3 bounded 8-bit RGBA
  Adam7 interlaced PNG sidecar round trips, seven reduced-image pass manifests,
  filters 0..4, and 6/6 invalid Adam7 probes rejected before semantic restore.
- `png_embedded_sidecar_writer_stage0.json` records 3/3 embedded PNG `tEXt`
  sidecar round trips, decoded pixel preservation, and 3/3 invalid embedded
  metadata probes rejected before semantic restore.
- `png_textual_metadata_policy_stage0.json` records 12/12 bounded PNG textual
  metadata round trips across `tEXt`, `zTXt`, uncompressed `iTXt`, and
  compressed `iTXt` carriers, with 7/7 invalid metadata policy probes rejected
  before semantic restore.
- `png_private_chunk_policy_stage0.json` records 3/3 bounded app-private PNG
  `mgOT` ancillary chunk metadata round trips, 7/7 invalid private chunk
  policy probes rejected, and a carrier-selection input matrix that keeps the
  final production carrier decision blocked.
- `png_private_chunk_preservation_matrix_stage0.json` records the simulated
  private chunk preservation matrix: 18/18 expected editor-behavior outcomes,
  6 recoverable imports, 6 metadata-loss outcomes, and 6 stale/strict hash
  rejections with live external editor validation still blocked.
- `apng_sidecar_decoder_stage0.json` records 3/3 bounded APNG sidecar round
  trips with two full-canvas 8-bit RGBA source frames, `acTL`/`fcTL`/`fdAT`
  sequence validation, 5/5 invalid APNG probes rejected, and full APNG/PNG
  conformance still blocked.
- `apng_metadata_carrier_cross_product_stage0.json` records 15/15 bounded
  APNG metadata-carrier round trips across `tEXt`, `zTXt`, uncompressed
  `iTXt`, compressed `iTXt`, and private `mgOT` carriers, with 6/6 invalid
  carrier/APNG probes rejected before semantic restore.
- `png_apng_chunk_order_conformance_stage0.json` records 12/12 bounded
  PNG/APNG chunk-order conformance cases across static RGBA, split-IDAT,
  indexed PLTE/tRNS, and APNG static-first-frame carriers, with 7/7 invalid
  IHDR/IEND/PLTE/tRNS/IDAT/APNG sequence probes rejected.
- `spritesheet_layout_variant_decoder_stage0.json` records 12/12
  layout-variant spritesheet sidecar round trips across vertical strips,
  row-major matrix sheets, padded/guttered grids, and sparse atlas rects.
- `spritesheet_packed_runtime_decoder_stage0.json` records 3/3 packed
  trim/rotation spritesheet sidecar round trips, 3 runtime playback timelines,
  and 4/4 invalid packed/runtime probes rejected before semantic restore.
- `spritesheet_arbitrary_atlas_packer_stage0.json` records 6/6 arbitrary
  atlas round trips across shelf and MaxRects-style packing policies, 6/6
  invalid atlas probes rejected, and the final production renderer playback
  claim still blocked.
- `spritesheet_multi_page_atlas_stage0.json` records 3/3 generated multi-page
  atlas bundle round trips, page manifests, per-page hashes, frame-to-page
  bindings, runtime page-switch sampling, and 6/6 invalid page/frame probes
  rejected before semantic restore.
- `project_native_metadata_writer_stage0.json` records 6/6 Piskel and
  Pixelorama native project metadata round trips across the 3 current profiles,
  4/4 invalid native metadata probes rejected, and one explicit unsupported
  Aseprite/LibreSprite User Data chunk writer policy.
- `project_editor_rewrite_preservation_stage0.json` records 6/6 deterministic
  Piskel/Pixelorama rewrite-simulation round trips, visual hash preservation,
  sidecar rebinding to rewritten canonical project hashes, and 3/3 invalid
  rewrite probes rejected.
- `aseprite_user_data_chunk_writer_stage0.json` records 3/3
  Aseprite/LibreSprite User Data Chunk round trips for the one-frame,
  one-layer, compressed RGBA cel subset, with 3/3 invalid User Data probes
  rejected before semantic restore.
- `aseprite_tags_layers_semantics_stage0.json` records 3/3
  Aseprite/LibreSprite tags/layers semantic round trips for the three-frame,
  three-layer, compressed RGBA cel subset, with 4/4 invalid tags/layers
  probes rejected before semantic restore.
- `aseprite_palette_slice_semantics_stage0.json` records 3/3
  Aseprite/LibreSprite palette/slice semantic round trips for Palette Chunk
  `0x2019` SLIP colors and Slice Chunk `0x2022` organ bounds layered onto the
  three-frame tags/layers subset, with 5/5 invalid palette/slice probes
  rejected before semantic restore.
- `aseprite_linked_cel_semantics_stage0.json` records 3/3
  Aseprite/LibreSprite linked-cel semantic round trips for Cel Chunk `0x2005`
  linked cel type 1 frame targets layered onto the palette/slice tags/layers
  carrier, with 5/5 invalid linked-cel probes rejected before semantic
  restore.
- `aseprite_tilemap_tileset_semantics_stage0.json` records 3/3
  Aseprite/LibreSprite tilemap/tileset semantic round trips for one Tilemap
  Layer type 2, one Tileset Chunk `0x2023`, and compressed Tilemap Cel Chunk
  `0x2005` type 3 payloads, with 5/5 invalid tilemap/tileset probes rejected
  before semantic restore.
- `aseprite_nested_timeline_semantics_stage0.json` records 3/3
  Aseprite/LibreSprite nested timeline semantic round trips for two group
  layers, child levels `0..2`, four documented tag loop directions,
  tag-associated User Data Chunk `0x2020` color/text payloads, and 6/6 invalid
  nested/timeline probes rejected before semantic restore.
- `aseprite_external_properties_semantics_stage0.json` records 3/3
  Aseprite/LibreSprite external-properties semantic round trips for Color
  Profile Chunk `0x2007`, External Files Chunk `0x2008`, User Data Chunk
  `0x2020` property maps, and Cel Extra Chunk `0x2006` precise bounds, with
  6/6 invalid external/property probes rejected before semantic restore.
- `aseprite_document_variant_resolution_stage0.json` records 9/9
  Aseprite/LibreSprite document-variant semantic round trips across indexed
  8 bpp, grayscale-alpha 16 bpp, and RGBA 32 bpp compressed cels with
  hash-checked generated External Files Chunk `0x2008` assets, with 6/6
  invalid variant/resolver probes rejected before semantic restore.
- `aseprite_external_asset_resolver_matrix_stage0.json` records 36/36
  generated Aseprite/LibreSprite external-asset resolver round trips across
  direct, relative-path, content-addressed, and multi-root policies, with 5/5
  invalid resolver probes rejected before semantic restore.
- `slip_runtime_selection_policy_stage0.json` records 3/3 profile-weighted
  archive elite selections from switchboard lifecycle metrics, with 2/2 invalid
  selection probes rejected before selection.
- `slip_offspring_lineage_gate_stage0.json` records 3/3 bounded offspring
  selections from runtime-selected parents, 3 lineage decisions, and 2/2
  invalid offspring probes rejected before the gate starts.
- `slip_long_horizon_behavior_gate_stage0.json` records 3/3 selected
  offspring surviving the 96-tick switchboard horizon, 18/18 held-out
  switchboard full-survival probes, 18/18 idle-neglect deaths, and 2/2 invalid
  long-horizon probes rejected before the gate starts.
- `slip_multigeneration_lineage_runner_stage0.json` records 3/3 current
  profiles persisting three-generation candidate lineages, 9/9 selected
  offspring continuing as qualified lineage frontiers, max generation 4, and
  2/2 invalid multigeneration probes rejected before the runner starts.
