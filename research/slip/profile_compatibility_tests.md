# SLIP Profile Compatibility Tests

Date: 2026-05-14

Status: `research_slip_profile_compatibility_matrix_no_package_code`

## Purpose

Define the current and future compatibility tests for `SLIP` profiles across
grid validation, generation, lifecycle simulation, archive scoring, workshop
round trips, and future package gates.

This file satisfies the research plan's required
`profile_compatibility_tests.md` output at research stage. It does not create a
package module, package tests, runtime JSON Schema integration, or a
package-level Pydantic dependency.

## Source Position

The research plan defines `SLIP` as:

```txt
SLIP = constraints + priors + weights + validators
```

The current Stage 0 implementation is narrower:

```txt
SLIP v0.1.0 =
  profile metadata
  + palette constraints
  + body-mass bounds
  + required organ roles
  + mutation-rate caps
  + bounded behavior weights
  + bounded survival weights
```

Any broader claim about animation vocabulary, forbidden traits, export UX,
runtime behavior integration, profile-weighted evolution, or community profile
packs is not yet proven.

## External Anchors

The profile contract should remain JSON-compatible:

- JSON Schema Draft 2020-12 is the interchange target for machine-readable
  profile schemas.
- Pydantic v2 is the current lab Python authoring/validation model because it
  validates typed models and emits JSON Schema through `model_json_schema()`.

Neither source changes the current Stage 0 facts. The current generation and
alignment validator remains `labs/grid_genome/slip.py`; the schema failure
corpus is checked by `labs/slip_validator/slip_validator.py` and the lab
Pydantic contract is checked by `labs/slip_validator/pydantic_contract.py`.

Long-horizon behavior evidence is anchored by the Avida digital-evolution
platform, JaxLife artificial-life simulator paper, and the Sutton/Barto
reinforcement-learning text. These sources support explicit long-running
behavior protocols, but they do not turn the current lab gate into package
runtime evolution.

## Current Fixture Corpus

| Group | Path | Count | Current result |
| --- | --- | ---: | --- |
| Valid profiles | `data/slips/valid/*.json` | 3 | accepted by lab validator |
| Research examples | `research/slip/slip_examples/*.json` | 3 | accepted by Stage 0 schema validator |
| Invalid profiles | `data/slips/invalid/*.json` | 2 | rejected by lab validator |
| Schema failure cases | `data/slips/failure_cases/*.json` | 12 | rejected by Stage 0 schema validator |
| Schema validation report | `data/slips/slip_schema_validation_stage0.json` | 1 | 3 valid accepted, 3 examples accepted, 12 failures rejected |
| Pydantic contract report | `data/slips/slip_pydantic_contract_stage0.json` | 1 | 3 valid accepted, 3 examples accepted, 12 failures rejected |
| Migration/dependency report | `data/slips/slip_schema_migration_dependency_gate_stage0.json` | 1 | schema surface parity proven; only `0.1.0` accepted with no migration |
| SLIP authoring panel | `data/workshop_editor/slip_authoring_panel_stage0.json` | 1 | 3 current drafts accepted, 3 invalid probes rejected |
| SLIP behavior/mutation preview | `data/workshop_editor/slip_behavior_mutation_preview_stage0.json` | 1 | 3 behavior previews, 3 mutation previews, 2 invalid preview probes rejected |
| SLIP lifecycle/archive effects | `data/workshop_editor/slip_lifecycle_archive_effects_stage0.json` | 1 | 3 lifecycle effects, 3 archive effects, 3 distinct preview/lifecycle/archive fingerprints, 2 invalid probes rejected |
| SLIP runtime selection policy | `data/workshop_editor/slip_runtime_selection_policy_stage0.json` | 1 | 3 profile-weighted archive elite selections from switchboard lifecycle metrics, 3 distinct selected grid ids, 2 invalid selection probes rejected |
| SLIP offspring lineage gate | `data/workshop_editor/slip_offspring_lineage_gate_stage0.json` | 1 | 3 bounded offspring selections, 3 lineage decisions, 1 add-niche outcome, 2 invalid offspring probes rejected |
| SLIP long-horizon behavior gate | `data/workshop_editor/slip_long_horizon_behavior_gate_stage0.json` | 1 | 3 selected-offspring full-survival probes, 18/18 held-out switchboard full-survival probes, 18/18 idle deaths, 2 invalid long-horizon probes rejected |
| SLIP multigeneration lineage runner | `data/workshop_editor/slip_multigeneration_lineage_runner_stage0.json` | 1 | 3 three-generation profile runs, 9 qualified selected offspring, max generation 4, 2 invalid multigeneration probes rejected |
| Mecha engine runtime boundary gate | `data/architecture/mecha_engine_runtime_boundary_gate_stage0.json` | 1 | 5 package/runtime contracts defined, 5/5 premature package/evolution probes rejected, package root absent, package runtime integration not ready |
| External metadata sidecar | `data/workshop_editor/external_metadata_sidecar_stage0.json` | 1 | 3 sidecar round trips, 2 invalid binding probes rejected, 5 adapter formats require sidecar |
| Standard image sidecar decoder | `data/workshop_editor/standard_image_sidecar_decoder_stage0.json` | 1 | 3 static RGBA PNG sidecar round trips, 2 invalid PNG/binding probes rejected |
| PNG variant sidecar decoder | `data/workshop_editor/png_variant_sidecar_decoder_stage0.json` | 1 | 15 variant PNG sidecar round trips, color types 0/2/3/6, filters 0..4, 3 invalid variant probes rejected |
| PNG Adam7 interlace decoder | `data/workshop_editor/png_adam7_interlace_decoder_stage0.json` | 1 | 3 bounded 8-bit RGBA Adam7 PNG sidecar round trips, seven reduced-image pass manifests, filters 0..4, 6 invalid Adam7 probes rejected |
| PNG deep color sidecar decoder | `data/workshop_editor/png_deep_color_sidecar_decoder_stage0.json` | 1 | 33 deep-color PNG sidecar round trips across 1/2/4-bit greyscale, 1/2/4-bit indexed-color, 16-bit greyscale/truecolor/greyscale-alpha/RGBA, 8-bit greyscale-alpha, filters 0..4, 6 invalid deep-color probes rejected |
| PNG Adam7 deep color cross product | `data/workshop_editor/png_adam7_deep_color_cross_product_stage0.json` | 1 | 33 Adam7 deep-color PNG sidecar round trips across 1/2/4-bit greyscale, 1/2/4-bit indexed-color, 16-bit greyscale/truecolor/greyscale-alpha/RGBA, 8-bit greyscale-alpha, seven reduced-image pass manifests, filters 0..4, 7 invalid cross-product probes rejected |
| APNG sidecar decoder | `data/workshop_editor/apng_sidecar_decoder_stage0.json` | 1 | 3 bounded APNG sidecar round trips, two full-canvas 8-bit RGBA source frames, `acTL`/`fcTL`/`fdAT` sequence validation, 5 invalid APNG probes rejected |
| APNG metadata carrier cross product | `data/workshop_editor/apng_metadata_carrier_cross_product_stage0.json` | 1 | 15 bounded APNG metadata-carrier round trips across `tEXt`, `zTXt`, uncompressed `iTXt`, compressed `iTXt`, and private `mgOT`; 6 invalid carrier/APNG probes rejected |
| PNG/APNG chunk order conformance | `data/workshop_editor/png_apng_chunk_order_conformance_stage0.json` | 1 | 12 PNG/APNG chunk-order cases across static RGBA, split-IDAT, indexed PLTE/tRNS, and APNG static-first-frame carriers; 7 invalid ordering/cardinality probes rejected |
| APNG partial frame playback | `data/workshop_editor/apng_partial_frame_playback_stage0.json` | 1 | 12 APNG partial-frame playback cases across source blend, alpha-over blend, background disposal, and previous disposal; 5 invalid frame-control/data probes rejected |
| APNG filtered frame data | `data/workshop_editor/apng_filtered_frame_data_stage0.json` | 1 | 15 APNG filter-method-0 frame-data cases across filter types 0..4 and split `fdAT` reconstruction; 4 invalid filter/scanline/sequence probes rejected |
| APNG color type frame data | `data/workshop_editor/apng_color_type_frame_data_stage0.json` | 1 | 15 APNG color-type frame-data cases across color types 0/2/3/4/6, PLTE/tRNS, and alpha-channel reconstruction; 4 invalid color metadata probes rejected |
| APNG bit depth frame data | `data/workshop_editor/apng_bit_depth_frame_data_stage0.json` | 1 | 30 APNG bit-depth frame-data cases across packed 1/2/4-bit and 16-bit samples, filter types 0..4, and split `fdAT`; 4 invalid bit-depth/frame-data probes rejected |
| APNG partial sample frame data | `data/workshop_editor/apng_partial_sample_frame_data_stage0.json` | 1 | 15 APNG partial-frame sample cases across packed 1-bit greyscale, 4-bit indexed `PLTE`/`tRNS`, and 16-bit truecolor/alpha regions, filter types 0..4, source/over composition, and split `fdAT`; 5 invalid bounds/sample/frame-data probes rejected |
| APNG Adam7 frame data | `data/workshop_editor/apng_adam7_frame_data_stage0.json` | 1 | 18 APNG Adam7 frame-data cases across color types 0/2/3/4/6, bit depths 1/4/8/16, seven reduced-image pass manifests, filter types 0..4, indexed `PLTE`/`tRNS`, source/over composition, and split `fdAT`; 5 invalid interlace/sample/frame-data probes rejected |
| APNG partial Adam7 frame data | `data/workshop_editor/apng_partial_adam7_frame_data_stage0.json` | 1 | 18 APNG partial Adam7 frame-data cases across non-zero 6x6 patch offsets, color types 0/2/3/4/6, bit depths 1/4/8/16, seven reduced-image pass manifests, filter types 0..4, indexed `PLTE`/`tRNS`, source/over composition, and split `fdAT`; 6 invalid bounds/interlace/sample/frame-data probes rejected |
| PNG/APNG image data chunking | `data/workshop_editor/png_apng_image_data_chunking_stage0.json` | 1 | 18 PNG/APNG image-data chunk-boundary cases across static PNG IDAT and APNG fdAT datastream splits, zero-length IDAT data fields, zero-length fdAT `frame_data` fields, zlib-header splits, and Adler-32 trailer splits; 6 invalid IDAT/fdAT chunking and datastream probes rejected |
| PNG/APNG zlib compression matrix | `data/workshop_editor/png_apng_zlib_compression_stage0.json` | 1 | 18 PNG/APNG zlib compression-method-0 cases across static PNG IDAT and APNG fdAT streams, stored-block, fixed-Huffman, filtered, and RLE zlib strategies, raw scanline hash preservation, zlib CM=8 headers, and 6 invalid compression/datastream probes rejected |
| PNG/APNG zlib header policy | `data/workshop_editor/png_apng_zlib_header_policy_stage0.json` | 1 | 18 PNG/APNG zlib header-policy cases across static PNG IDAT and APNG fdAT streams, CINFO values 1/4/7, 512/4096/32768-byte windows, FDICT=false valid streams, raw scanline hash preservation, and 6 invalid FDICT/CMF/FLG/header probes rejected |
| PNG embedded sidecar writer | `data/workshop_editor/png_embedded_sidecar_writer_stage0.json` | 1 | 3 embedded PNG `tEXt` sidecar round trips, decoded pixels preserved, 3 invalid embedded metadata probes rejected |
| PNG textual metadata policy | `data/workshop_editor/png_textual_metadata_policy_stage0.json` | 1 | 12 bounded PNG textual metadata round trips across `tEXt`, `zTXt`, uncompressed `iTXt`, and compressed `iTXt`; 7 invalid metadata policy probes rejected |
| PNG private chunk policy | `data/workshop_editor/png_private_chunk_policy_stage0.json` | 1 | 3 app-private PNG `mgOT` ancillary chunk round trips; 7 invalid private chunk probes rejected; carrier-selection inputs recorded without final production decision |
| PNG private chunk preservation matrix | `data/workshop_editor/png_private_chunk_preservation_matrix_stage0.json` | 1 | 18/18 simulated editor-behavior outcomes matched across 3 profiles and 6 policies; 6 recoverable imports, 6 metadata-loss outcomes, 6 stale/strict hash rejections |
| Spritesheet sidecar decoder | `data/workshop_editor/spritesheet_sidecar_decoder_stage0.json` | 1 | 3 fixed-grid spritesheet sidecar round trips, 2 invalid PNG/frame probes rejected |
| Spritesheet layout variant decoder | `data/workshop_editor/spritesheet_layout_variant_decoder_stage0.json` | 1 | 12 layout-variant spritesheet sidecar round trips, vertical/matrix/padded/sparse layouts, 3 invalid layout probes rejected |
| Spritesheet packed runtime decoder | `data/workshop_editor/spritesheet_packed_runtime_decoder_stage0.json` | 1 | 3 packed trim/rotation sidecar round trips, 3 runtime playback timelines, 4 invalid packed/runtime probes rejected |
| Spritesheet arbitrary atlas packer | `data/workshop_editor/spritesheet_arbitrary_atlas_packer_stage0.json` | 1 | 6 arbitrary atlas round trips across shelf and MaxRects-style policies, 6 invalid atlas probes rejected, best occupancy policy `maxrects_best_short_side_fit` |
| Spritesheet multi-page atlas | `data/workshop_editor/spritesheet_multi_page_atlas_stage0.json` | 1 | 3 generated multi-page atlas bundle round trips, page manifests, per-page hashes, frame-to-page bindings, runtime page-switch sampling, 6 invalid page/frame probes rejected |
| Third-party project decoder boundary | `data/workshop_editor/third_party_project_decoder_stage0.json` | 1 | 3 project decoder successes, 3 sidecar restores, 3 invalid project/binding probes rejected |
| Project native metadata writer | `data/workshop_editor/project_native_metadata_writer_stage0.json` | 1 | 6 Piskel/Pixelorama native metadata round trips, 4 invalid native metadata probes rejected, 1 delegated Aseprite/LibreSprite User Data policy |
| Project editor rewrite preservation | `data/workshop_editor/project_editor_rewrite_preservation_stage0.json` | 1 | 6 deterministic Piskel/Pixelorama rewrite round trips, visual hash preserved, 3 invalid rewrite probes rejected |
| Aseprite User Data Chunk writer | `data/workshop_editor/aseprite_user_data_chunk_writer_stage0.json` | 1 | 3 Aseprite/LibreSprite User Data Chunk round trips, one-frame compressed RGBA cel subset, 3 invalid User Data probes rejected |
| Aseprite tags/layers semantics | `data/workshop_editor/aseprite_tags_layers_semantics_stage0.json` | 1 | 3 Aseprite/LibreSprite tags/layers semantic round trips, three-frame/three-layer compressed RGBA cel subset, 4 invalid tags/layers probes rejected |
| Aseprite palette/slice semantics | `data/workshop_editor/aseprite_palette_slice_semantics_stage0.json` | 1 | 3 Aseprite/LibreSprite palette/slice semantic round trips, Palette Chunk `0x2019`, Slice Chunk `0x2022`, three-frame/three-layer compressed RGBA cel subset, 5 invalid palette/slice probes rejected |
| Aseprite linked-cel semantics | `data/workshop_editor/aseprite_linked_cel_semantics_stage0.json` | 1 | 3 Aseprite/LibreSprite linked-cel semantic round trips, Cel Chunk `0x2005` linked cel type 1 targets, 5 compressed RGBA cels, 4 linked cels, 5 invalid linked-cel probes rejected |
| Aseprite tilemap/tileset semantics | `data/workshop_editor/aseprite_tilemap_tileset_semantics_stage0.json` | 1 | 3 Aseprite/LibreSprite tilemap/tileset semantic round trips, Tilemap Layer type 2, Tileset Chunk `0x2023`, Tilemap Cel Chunk `0x2005` type 3 payloads, 5 invalid tilemap/tileset probes rejected |
| Aseprite nested timeline semantics | `data/workshop_editor/aseprite_nested_timeline_semantics_stage0.json` | 1 | 3 Aseprite/LibreSprite nested timeline semantic round trips, group Layer Chunk `0x2004` hierarchy, all 4 tag loop directions, tag User Data `0x2020`, 6 invalid nested/timeline probes rejected |
| Aseprite document variant resolution | `data/workshop_editor/aseprite_document_variant_resolution_stage0.json` | 1 | 9 Aseprite/LibreSprite document-variant semantic round trips across indexed 8 bpp, grayscale-alpha 16 bpp, and RGBA 32 bpp compressed cels with generated External Files Chunk `0x2008` assets resolved by hash; 6 invalid variant/resolver probes rejected |
| Aseprite external asset resolver matrix | `data/workshop_editor/aseprite_external_asset_resolver_matrix_stage0.json` | 1 | 36 generated Aseprite/LibreSprite resolver round trips across 3 profiles, 3 document variants, and direct/relative/content-addressed/multi-root policies; 5 invalid resolver probes rejected |
| SLIP-constrained grids | `data/generated_grids/slip_lcd_seed_constrained/*.json` | 50 | valid and aligned with `slip_lcd_seed` |
| Multi-profile constrained grids | `data/slips/multi_profile_generation_stage0/*/*.json` | 150 | valid and aligned across all 3 valid profiles |
| Workshop round trip | `data/workshop_editor/workshop_roundtrip_stage0_report.json` | 1 | native JSON round trip with `slip_lcd_seed` |
| Lifecycle comparator | `data/lifecycle/lifecycle_stage0.json` | 1 | profile ID recorded as `slip_lcd_seed` |

## Current Valid Profiles

| Profile | Palette | Body mass | Required organ roles | Behavior weights | Survival weights |
| --- | --- | --- | --- | --- | --- |
| `slip_lcd_seed` | `lcd_green` | `4..24` | `sensor`, `expression` | curiosity `0.6`, neediness `0.4`, sleepiness `0.5` | stability `0.5`, novelty `0.25`, bond `0.25` |
| `slip_gray_stable` | `gameboy_gray` | `5..24` | `sensor`, `expression` | curiosity `0.35`, neediness `0.3`, sleepiness `0.65` | stability `0.7`, novelty `0.1`, bond `0.2` |
| `slip_amber_social` | `amber_terminal` | `6..24` | `sensor`, `expression` | curiosity `0.7`, neediness `0.6`, sleepiness `0.35` | stability `0.4`, novelty `0.25`, bond `0.35` |

## Current Invalid Profiles

| Profile | Fault | Expected rejection |
| --- | --- | --- |
| `slip_invalid_bad_weight` | `behavior.curiosity = 1.2` | value outside `0..1` |
| `slip_invalid_palette` | `grid.allowed_palettes = ["unknown_palette"]` | unknown palette |

These invalid fixtures are profile-shape and value tests. The expanded schema
failure corpus adds required-field, type, enum, range, minimum-item,
additional-property, semantic body-mass, and boolean numeric failures. Neither
corpus proves grid/profile cross-product compatibility by itself.

## Validator Contract Observed

The current lab validator enforces:

- `slip_version` exactly equals `0.1.0`;
- `profile_id` and `name` are non-empty strings;
- `grid.allowed_palettes` is a non-empty list of known palettes;
- `grid.body_mass_min` and `grid.body_mass_max` are integers;
- body mass minimum is at least `1`;
- body mass maximum is not below minimum;
- `grid.required_organ_roles` is a non-empty list;
- required organ roles are limited to `sensor`, `expression`, and `body_core`;
- provided `behavior` values are numbers in `[0, 1]`;
- provided `survival_weights` values are numbers in `[0, 1]`;
- mutation caps are numbers in `[0, 1]`;
- grid alignment checks palette ID, core-cell body mass, required organ roles,
  and mutation-rate caps.

The Stage 0 schema validator additionally requires the complete current
behavior vocabulary (`curiosity`, `neediness`, `sleepiness`) and survival
vocabulary (`stability`, `novelty`, `bond`) for file-level profile payloads.

Important generation-validator limitation:

```txt
The validator bounds provided behavior and survival keys, but it does not yet
require a complete behavior vocabulary or survival-weight vocabulary.
```

## Compatibility Matrix

| Surface | Current proof | Current status | Required next proof |
| --- | --- | --- | --- |
| Profile validation | 3 valid profiles accepted, 3 examples accepted, 12 schema failure cases rejected by both dependency-free and Pydantic lab validators; schema surface parity proven; only `0.1.0` accepted with no migration; legacy 2 invalid fixtures also rejected by lab validator | proven Stage 0 schema/failure corpus, lab Pydantic contract, and migration policy | runtime JSON Schema dependency and declared package dependency manifest |
| Generation alignment | 150/150 current valid-profile constrained candidates valid and aligned | proven for current 3-profile corpus | expanded community and unsatisfiable-profile corpus |
| Grid validator | generated candidates pass grid validation | proven for current profile-aware candidate corpora | profile-aware negative cases and held-out profiles |
| Lifecycle | 3/3 current valid profiles produce measured 24-tick switchboard lifecycle effects from preview-validated grids; runtime selection policy consumes switchboard lifecycle episodes for 3/3 profile-specific archive elite choices; offspring lineage gate evaluates selected children with mean survival ratio `1.0`; long-horizon gate records 18/18 held-out switchboard full-survival runs and 18/18 idle deaths at 96 ticks | measured Stage 0 selection, offspring-lineage, and long-horizon behavior bridge only | package runtime integration and manual readability calibration |
| Archive | extended descriptors include `slip_alignment`; 3/3 current valid profiles build profile-specific extended archives; 3/3 runtime selection probes choose profile-weighted archive elites from distinct niches; offspring lineage gate emits 3 lineage decisions with 1 add-niche and 2 hold-parent outcomes | measured Stage 0 selection and lineage decision bridge only | held-out multi-profile calibration and manual readability calibration |
| Workshop round trip | native JSON round trip preserves semantics across 150 generated candidates under 3 valid profiles | proven for generated multi-profile corpus | full project-format coverage, production renderer playback, and live external editor rewrite validation |
| External metadata sidecar | 3/3 current profile sidecars bind a non-native PNG asset stub to the semantic overlay and restore SLIP-aligned grids; 2/2 invalid binding probes rejected; 5 adapter formats marked sidecar-required | proven Stage 0 strategy only | full project-format coverage and live external editor rewrite validation |
| Standard image sidecar decoder | 3/3 current profile grids export to real static RGBA PNG, decode with PNG signature/chunk/CRC/IDAT checks, restore SLIP-aligned semantic grids from sidecars, and reject 2/2 corrupt PNG or hash-mismatch probes | proven static non-interlaced 8-bit RGBA PNG only; superseded for broader color/filter variants by PNG variant sidecar decoder and Adam7 interlace by the Adam7 decoder lab | full APNG/PNG conformance remains separate |
| PNG variant sidecar decoder | 15/15 current profile PNG variants export/import with sidecars across 8-bit non-interlaced color types 0, 2, 3, and 6; filter types 0 through 4; PLTE indexed-color decoding; 3/3 invalid interlace/PLTE/carrier-hash probes rejected | proven Stage 0 PNG variant subset only; Adam7 interlace and deep-color coverage are handled by separate decoder labs | full APNG/PNG conformance remains separate |
| PNG Adam7 interlace decoder | 3/3 current profile 8-bit RGBA Adam7 interlaced PNG exports/imports round-trip sidecar semantics with seven reduced-image pass manifests, filters 0..4, exact pixel reconstruction, and 6/6 invalid non-Adam7, scanline-length, filter, pass-manifest, pixel-hash, and asset-hash probes rejected | proven Stage 0 bounded 8-bit RGBA Adam7 subset only; Adam7/deep-color cross-products are handled by a separate decoder lab | full APNG/PNG conformance, live external editor rewrite validation, and final production carrier selection |
| PNG deep color sidecar decoder | 33/33 current profile PNG deep-color variants export/import with sidecars across 1/2/4-bit greyscale, 1/2/4-bit indexed-color with PLTE, 16-bit greyscale/truecolor/greyscale-alpha/RGBA, 8-bit greyscale-alpha, and filters 0..4; 6/6 invalid bit-depth, scanline, filter, binding, pixel-hash, and asset-hash probes rejected | proven Stage 0 bounded non-interlaced deep-color subset only; Adam7/deep-color cross-products are handled by a separate decoder lab | full APNG/PNG conformance, live external editor rewrite validation, and final production carrier selection |
| PNG Adam7 deep color cross product | 33/33 current profile Adam7 PNG deep-color variants export/import with sidecars across 1/2/4-bit greyscale, 1/2/4-bit indexed-color with PLTE, 16-bit greyscale/truecolor/greyscale-alpha/RGBA, 8-bit greyscale-alpha, filters 0..4, and seven reduced-image pass manifests; 7/7 invalid interlace, scanline, filter, pass-manifest, bit-depth, pixel-hash, and asset-hash probes rejected | proven Stage 0 bounded Adam7/deep-color cross-product subset only | full APNG/PNG conformance, live external editor rewrite validation, and final production carrier selection |
| APNG sidecar decoder | 3/3 current profile APNG files round-trip sidecar semantics with two full-canvas 8-bit RGBA source frames per asset, `acTL`/`fcTL`/`fdAT` sequence validation, frame hash validation, and 5/5 invalid missing-control, sequence, blend, frame-hash, and asset-hash probes rejected | proven Stage 0 bounded full-canvas APNG sidecar subset only; metadata-carrier cross-products are handled by a separate APNG carrier lab | full APNG/PNG conformance, live external editor rewrite validation, and final production carrier selection |
| APNG metadata carrier cross product | 15/15 current profile APNG metadata-carrier variants round-trip sidecar semantics across `tEXt`, `zTXt`, uncompressed `iTXt`, compressed `iTXt`, and private unsafe-to-copy `mgOT`; canonical APNG hashes and frame hashes are preserved after carrier removal; 6/6 missing-carrier, duplicate-text, corrupt-compression, private-hash, and APNG-sequence probes rejected | proven Stage 0 bounded APNG textual/private carrier cross-product only | full APNG/PNG conformance, live external editor rewrite validation, and final production carrier selection |
| PNG/APNG chunk order conformance | 12/12 current profile chunk-order cases pass across static RGBA single-IDAT PNG, static RGBA split-IDAT PNG, indexed PLTE/tRNS PNG, and APNG static-first-frame carriers; 7/7 duplicate-IHDR, post-IEND, PLTE-after-IDAT, tRNS-before-PLTE, nonconsecutive-IDAT, acTL-after-IDAT, and fcTL sequence-gap probes rejected | proven Stage 0 bounded structural chunk-order matrix only | remaining APNG/PNG image-data conformance, live external editor rewrite validation, and final production carrier selection |
| APNG partial frame playback | 12/12 current profile playback cases pass across partial source-blend dispose-none patches, alpha-over dispose-none patches, background disposal, and previous disposal; display and after-disposal hashes recorded separately; 5/5 out-of-bounds, invalid-dispose, invalid-blend, missing-default-IDAT, and missing-frame-data probes rejected | proven Stage 0 bounded APNG partial-frame playback matrix only | remaining APNG/PNG image-data conformance, live external editor rewrite validation, and final production carrier selection |
| APNG filtered frame data | 15/15 current profile APNG frame-data cases pass across PNG filter method 0 filter types 0..4 with two-`fdAT` split datastream reconstruction; frame pixel hashes and display hashes recorded; 4/4 invalid filter-byte, truncated-scanline, `fdAT` sequence-gap, and missing-`fdAT` continuation probes rejected | proven Stage 0 bounded APNG filtered frame-data matrix only | remaining APNG/PNG image-data conformance, live external editor rewrite validation, and final production carrier selection |
| APNG color type frame data | 15/15 current profile APNG frame-data cases pass across 8-bit color types 0, 2, 3, 4, and 6; indexed-color PLTE/tRNS transparency and explicit alpha-channel pixels are reconstructed; frame pixel hashes and display hashes recorded; 4/4 missing-PLTE, invalid-tRNS, unsupported-color-type, and alpha+tRNS conflict probes rejected | proven Stage 0 bounded APNG color-type frame-data matrix only | remaining APNG/PNG image-data conformance, live external editor rewrite validation, and final production carrier selection |
| APNG bit depth frame data | 30/30 current profile APNG frame-data cases pass across packed 1/2/4-bit greyscale and indexed-color samples plus 16-bit greyscale, truecolor, greyscale-alpha, and truecolor-alpha samples; filter types 0..4, split `fdAT`, frame pixel hashes, display hashes, scanline byte lengths, and alpha counts recorded; 4/4 invalid bit-depth/color-type, truncated-scanline, invalid-filter, and `fdAT` sequence-gap probes rejected | proven Stage 0 bounded APNG bit-depth frame-data matrix only | remaining APNG/PNG image-data conformance, live external editor rewrite validation, and final production carrier selection |
| APNG partial sample frame data | 15/15 current profile APNG partial-frame sample cases pass across packed 1-bit greyscale, 4-bit indexed-color `PLTE`/`tRNS`, 16-bit truecolor, 16-bit greyscale-alpha, and 16-bit truecolor-alpha regions; filter types 0..4, source/over composition, split `fdAT`, frame pixel hashes, display hashes, patch scanline byte lengths, and alpha counts recorded; 5/5 out-of-bounds frame, invalid bit-depth/color-type, truncated partial scanline, invalid filter, and `fdAT` sequence-gap probes rejected | proven Stage 0 bounded APNG partial-sample frame-data matrix only | remaining APNG/PNG image-data conformance, live external editor rewrite validation, and final production carrier selection |
| APNG Adam7 frame data | 18/18 current profile APNG Adam7 frame-data cases pass across selected color types 0, 2, 3, 4, and 6 plus bit depths 1, 4, 8, and 16; seven reduced-image pass manifests, filter types 0..4, indexed-color `PLTE`/`tRNS` transparency, source/over composition, split `fdAT`, frame pixel hashes, display hashes, final canvas hashes, and alpha counts recorded; 5/5 non-Adam7 interlace, invalid bit-depth/color-type, truncated Adam7 scanline, invalid filter, and `fdAT` sequence-gap probes rejected | proven Stage 0 bounded APNG Adam7 frame-data matrix only | remaining APNG/PNG image-data conformance, live external editor rewrite validation, and final production carrier selection |
| APNG partial Adam7 frame data | 18/18 current profile APNG partial Adam7 frame-data cases pass across non-zero 6x6 patch offsets, selected color types 0, 2, 3, 4, and 6, and bit depths 1, 4, 8, and 16; seven reduced-image pass manifests, filter types 0..4, indexed-color `PLTE`/`tRNS` transparency, source/over composition, split `fdAT`, frame pixel hashes, display hashes, final canvas hashes, patch offset metadata, and alpha counts recorded; 6/6 non-Adam7 interlace, out-of-bounds frame, invalid bit-depth/color-type, truncated partial Adam7 scanline, invalid filter, and `fdAT` sequence-gap probes rejected | proven Stage 0 bounded APNG partial Adam7 frame-data matrix only | remaining APNG/PNG image-data conformance, live external editor rewrite validation, and final production carrier selection |
| PNG/APNG image data chunking | 18/18 current profile PNG/APNG image-data chunk-boundary cases pass across 9 static PNG IDAT datastream splits and 9 APNG fdAT frame-data splits; zero-length IDAT data fields, zero-length fdAT `frame_data` fields, zlib-header splits, Adler-32 trailer splits, IDAT/fdAT data lengths, data chunk counts, static pixel hashes, APNG display hashes, and final output hashes recorded; 6/6 nonconsecutive IDAT, corrupt IDAT, missing IDAT, missing fdAT, fdAT sequence-gap, and corrupt fdAT probes rejected | proven Stage 0 bounded PNG/APNG image-data chunking matrix only | remaining APNG/PNG image-data conformance, live external editor rewrite validation, and final production carrier selection |
| PNG/APNG zlib compression matrix | 18/18 current profile PNG/APNG zlib compression-method-0 cases pass across 9 static PNG IDAT streams and 9 APNG fdAT frame-data streams; stored-block, fixed-Huffman, filtered, and RLE zlib strategies, raw scanline hashes, compressed stream hashes, zlib CM=8 headers, static pixel hashes, APNG display hashes, and final output hashes recorded; 6/6 unsupported IHDR compression method, corrupt IDAT zlib header, truncated IDAT, truncated fdAT, corrupt fdAT Adler-32, and fdAT sequence-gap probes rejected | proven Stage 0 bounded PNG/APNG zlib compression matrix only; zlib header-policy and FDICT rejection handled separately | remaining APNG/PNG image-data conformance, live external editor rewrite validation, and final production carrier selection |
| PNG/APNG zlib header policy | 18/18 current profile PNG/APNG zlib header-policy cases pass across 9 static PNG IDAT streams and 9 APNG fdAT frame-data streams; CINFO values 1/4/7, 512/4096/32768-byte windows, FDICT=false valid streams, raw scanline hashes, compressed stream hashes, zlib CM=8 headers, static pixel hashes, APNG display hashes, and final output hashes recorded; 6/6 PNG/APNG FDICT, CMF/FLG check, reserved compression-method, and too-large CINFO probes rejected | proven Stage 0 bounded PNG/APNG zlib header policy matrix only | remaining APNG/PNG image-data conformance, live external editor rewrite validation, and final production carrier selection |
| PNG embedded sidecar writer | 3/3 current profile PNG files embed Mechagotchi sidecar JSON in a PNG `tEXt` ancillary chunk, preserve decoded pixels, restore SLIP-aligned semantic grids, and reject 3/3 missing metadata, invalid JSON, or canonical-hash mismatch probes | proven Stage 0 embedded PNG text-chunk sidecar subset; textual variant policy is superseded by PNG textual metadata policy | live external editor rewrite validation, full APNG/PNG conformance, and project-file native metadata beyond Piskel/Pixelorama |
| PNG textual metadata policy | 12/12 current profile PNG textual metadata variants round-trip sidecar semantics across `tEXt` ASCII JSON, `zTXt` compressed ASCII JSON, uncompressed `iTXt` UTF-8 JSON, and compressed `iTXt` UTF-8 JSON; 7/7 invalid missing, duplicate, non-ASCII text-policy, compression, UTF-8, and canonical-hash probes rejected | proven Stage 0 bounded textual metadata carrier policy only; private chunk policy is handled separately | live external editor rewrite validation, full APNG/PNG conformance, and production import/export carrier selection |
| PNG private chunk policy | 3/3 current profile PNG files round-trip sidecar semantics through one `mgOT` ancillary private unsafe-to-copy chunk with a magic-prefixed UTF-8 JSON payload; 7/7 invalid missing, duplicate, safe-to-copy type, magic, JSON, canonical-hash, and sidecar-hash probes rejected; carrier-selection inputs recorded | proven Stage 0 bounded private ancillary chunk policy and carrier-selection input matrix only; simulated preservation matrix handled separately | live external editor rewrite validation, full APNG/PNG conformance, and final production import/export carrier selection |
| PNG private chunk preservation matrix | 18/18 deterministic editor-behavior outcomes matched across exact preservation, private-chunk stripping, ancillary-only append, lossless IDAT reencoding, stale unsafe-copy preservation, and Mechagotchi-aware rebinding; 6 recoverable imports, 6 metadata-loss outcomes, 6 stale/strict hash rejections; recoverable semantic and pixel fidelity means `1.0` | proven Stage 0 simulated preservation matrix only | live external editor rewrite validation, full APNG/PNG conformance, and final production import/export carrier selection |
| Spritesheet sidecar decoder | 3/3 current profile grids export to fixed horizontal-strip spritesheet PNG, decode with PNG signature/chunk/CRC/IDAT checks, validate frame rectangles/durations/pixel hashes, restore SLIP-aligned semantic grids from sidecars, and reject 2/2 corrupt PNG or frame-hash mismatch probes | proven fixed-grid horizontal strip only; superseded for layout variants, packed-runtime playback, and arbitrary-atlas packing by later decoder labs | production renderer playback remains separate |
| Spritesheet layout variant decoder | 12/12 current profile spritesheet layout variants export/import with sidecars across vertical strips, row-major matrix sheets, padded/guttered grids, and sparse atlas rects; 3/3 invalid out-of-bounds/overlap/frame-hash probes rejected | proven Stage 0 layout variant subset only; arbitrary atlas policy is handled separately | production renderer playback |
| Spritesheet packed runtime decoder | 3/3 current profile packed spritesheet atlases export/import with sidecars; trimmed frames reconstruct to canonical 8x8 frames; one 90-degree rotated frame per profile is decoded; looped runtime playback samples frame-duration boundaries; 4/4 invalid unsupported-rotation, trim, hash, and duration probes rejected | proven Stage 0 packed trim/rotation and sidecar runtime playback subset; arbitrary atlas policy is handled separately | production renderer playback and full project-format coverage |
| Spritesheet arbitrary atlas packer | 6/6 current profile arbitrary atlas exports/imports round-trip sidecar semantics across shelf and MaxRects-style best-short-side-fit packing policies; five variable-size regions per atlas are reconstructed to canonical 8x8 frames; 6/6 invalid overlap, bounds, hash, duration, algorithm, and rotation-policy probes rejected; `maxrects_best_short_side_fit` is the best occupancy policy for this fixed corpus | proven Stage 0 arbitrary rectangle atlas packing and policy comparison only; generated multi-page atlas fixtures are handled separately | production renderer playback, live external editor validation, and editor-authored atlas fixtures |
| Spritesheet multi-page atlas | 3/3 current profile generated multi-page atlas bundles round-trip sidecar semantics with page manifests, per-page hashes, frame-to-page bindings, three pages per profile, seven reconstructed canonical frames per profile, runtime page-switch sampling, and 6/6 invalid missing-page, page-hash, unknown-page, out-of-bounds, frame-hash, and playback-order probes rejected | proven Stage 0 generated multi-page atlas fixture subset only | production renderer playback, live external editor validation, and editor-authored atlas fixtures |
| Third-party project decoder boundary | 3/3 current profile project payloads decode Piskel JSON, Pixelorama `.pxo` ZIP/data.json, and Aseprite/LibreSprite header boundaries, restore SLIP-aligned semantic grids from sidecars, and reject 3/3 corrupt project, mismatched sidecar, or unsupported format probes | proven Stage 0 boundary only | full project-format coverage, live external editor rewrite validation, and broader Aseprite chunk/schema coverage |
| Project native metadata writer | 6/6 current profile project payloads embed Mechagotchi sidecar JSON into Piskel description metadata and Pixelorama `.pxo` `data.json` metadata, restore SLIP-aligned semantic grids without external sidecars, and reject 4/4 missing metadata, sidecar-hash, canonical-hash, or unsupported-format probes | proven Stage 0 Piskel/Pixelorama native metadata subset only | live external editor rewrite validation, full project-format coverage, and cross-lab Aseprite dispatch if promoted |
| Project editor rewrite preservation | 6/6 current profile project payloads survive deterministic Piskel description and Pixelorama `data.json` rewrite simulation; visual hashes are preserved; sidecars rebind to rewritten canonical project hashes; 3/3 missing metadata, sidecar hash, and visual hash probes rejected | proven Stage 0 simulated rewrite subset only | live external Piskel/Pixelorama open-save validation, arbitrary Aseprite project schema coverage, and full project-format coverage |
| Aseprite User Data Chunk writer | 3/3 current profile `.aseprite` payloads write an ASE header, frame header, Layer Chunk `0x2004`, User Data Chunk `0x2020`, and compressed RGBA Cel Chunk `0x2005`; restore SLIP-aligned semantic grids from native User Data metadata; reject 3/3 missing User Data, sidecar hash, or visual hash probes | proven Stage 0 one-frame one-layer compressed cel User Data subset only; superseded for the tags/layers, palette/slice, linked-cel, tilemap/tileset, and nested timeline subsets by later Aseprite labs | live external Aseprite/LibreSprite open-save validation, arbitrary project schemas, and full project-format coverage |
| Aseprite tags/layers semantics | 3/3 current profile `.aseprite` payloads write three frames, three semantic layers, Tags Chunk `0x2018`, layer User Data Chunk `0x2020` metadata, and 9 compressed RGBA Cel Chunk `0x2005` payloads; restore SLIP-aligned semantic grids; reject 4/4 missing-tags, invalid-tag-range, sidecar-hash, and visual-hash probes | proven Stage 0 native layer/tag semantics subset only; superseded for palette/slice, linked-cel, tilemap/tileset, and nested timeline coverage by later Aseprite labs | live external Aseprite/LibreSprite open-save validation, arbitrary Aseprite project schemas, and full project-format coverage |
| Aseprite palette/slice semantics | 3/3 current profile `.aseprite` payloads write Palette Chunk `0x2019` SLIP colors, Slice Chunk `0x2022` core/sensors/expression bounds, three frames, three semantic layers, Tags Chunk `0x2018`, layer User Data Chunk `0x2020` metadata, and 9 compressed RGBA Cel Chunk `0x2005` payloads; restore SLIP-aligned semantic grids; reject 5/5 missing-palette, palette-mismatch, missing-slices, invalid-slice-bounds, and sidecar-hash probes | proven Stage 0 native palette/slice semantics subset only; superseded for linked-cel, tilemap/tileset, and nested timeline coverage by later Aseprite labs | live external Aseprite/LibreSprite open-save validation, arbitrary Aseprite project schemas, and full project-format coverage |
| Aseprite linked-cel semantics | 3/3 current profile `.aseprite` payloads write Palette Chunk `0x2019`, Slice Chunk `0x2022`, Tags Chunk `0x2018`, three semantic layers, 5 compressed RGBA Cel Chunk `0x2005` payloads, and 4 linked Cel Chunk `0x2005` type 1 frame targets; restore SLIP-aligned semantic grids; reject 5/5 missing-linked-cels, invalid-target, missing-target, visual-hash, and sidecar-hash probes | proven Stage 0 native linked-cel semantics subset only; superseded for tilemap/tileset and nested timeline coverage by later Aseprite labs | live external Aseprite/LibreSprite open-save validation, arbitrary Aseprite project schemas, and full project-format coverage |
| Aseprite tilemap/tileset semantics | 3/3 current profile `.aseprite` payloads write one Tilemap Layer type 2, one Tileset Chunk `0x2023`, three compressed Tilemap Cel Chunk `0x2005` type 3 payloads, Palette Chunk `0x2019`, Slice Chunk `0x2022`, and Tags Chunk `0x2018`; restore SLIP-aligned semantic grids; reject 5/5 missing-tileset, missing-tilemap-cels, tileset-image-hash, tile-ID, and sidecar-hash probes | proven Stage 0 native tilemap/tileset semantics subset only; superseded for nested timeline coverage by Aseprite nested timeline semantics | live external Aseprite/LibreSprite open-save validation, arbitrary Aseprite project schemas, and full project-format coverage |
| Aseprite nested timeline semantics | 3/3 current profile `.aseprite` payloads write two group Layer Chunk `0x2004` type 1 entries, three image layers, child levels `0..2`, four documented Tags Chunk `0x2018` loop directions and repeat counts, tag-associated User Data Chunk `0x2020` color/text payloads, and 12 compressed RGBA Cel Chunk `0x2005` payloads; restore SLIP-aligned semantic grids; reject 6/6 missing-group, hierarchy, missing-tag-User-Data, invalid-direction, tag-color, and sidecar-hash probes | proven Stage 0 native nested timeline subset only | live external Aseprite/LibreSprite open-save validation, arbitrary Aseprite project schemas, arbitrary external asset resolution, editor-authored document variants, and full project-format coverage |
| Aseprite external properties semantics | 3/3 current profile `.aseprite` payloads write Color Profile Chunk `0x2007`, External Files Chunk `0x2008` entries for palette/tileset/extension properties, User Data Chunk `0x2020` property maps keyed by user map `0` and extension map `303`, two Cel Extra Chunk `0x2006` precise-bound payloads, and two compressed RGBA Cel Chunk `0x2005` payloads; restore SLIP-aligned semantic grids; reject 6/6 missing-external-files, color-profile, missing-properties, extension-map-key, cel-extra-bounds, and sidecar-hash probes | proven Stage 0 native external-properties subset only | live external Aseprite/LibreSprite open-save validation, arbitrary Aseprite project schemas, arbitrary external asset resolution, editor-authored document variants, and full project-format coverage |
| Aseprite document variant resolution | 9/9 current profile `.aseprite` payloads write indexed 8 bpp, grayscale-alpha 16 bpp, and RGBA 32 bpp compressed Cel Chunk `0x2005` variants; indexed documents write Palette Chunk `0x2019`; all variants write External Files Chunk `0x2008` entries resolved against generated palette, tileset, and resolver payload hashes; restore SLIP-aligned semantic grids; reject 6/6 missing-external-files, external-asset-hash, unsupported-depth, indexed-palette, pixel-hash, and sidecar-hash probes | proven Stage 0 deterministic document-variant and generated external-asset-resolution subset only | live external Aseprite/LibreSprite open-save validation, arbitrary Aseprite project schemas, arbitrary external asset resolution, editor-authored document variants, and full project-format coverage |
| Aseprite external asset resolver matrix | 36/36 generated resolver round trips restore SLIP-aligned semantics across 3 profiles, indexed 8 bpp, grayscale-alpha 16 bpp, RGBA 32 bpp document variants, and direct manifest, relative file-map, content-addressed pool, and multi-root priority resolver policies; 5/5 missing-asset, hash-mismatch, ambiguity, path-traversal, and unsupported-policy probes rejected | proven Stage 0 generated external-asset resolver matrix subset only | live external Aseprite/LibreSprite open-save validation, editor-authored Aseprite document variants, arbitrary Aseprite project schemas, and full project-format coverage |
| SLIP authoring panel | 3/3 current profile drafts accepted and 3/3 invalid probes rejected by migration, dependency-free, and Pydantic gates | proven minimal panel for current Stage 0 schema | usability pilot |
| SLIP preview gates | 3/3 current profiles produce deterministic behavior previews and bounded mutation previews; measured lifecycle/archive bridge records 3 distinct preview, lifecycle, and archive fingerprints; 2/2 invalid preview/effect probes rejected before activation | proven deterministic Stage 0 preview gate plus measured effects bridge | manual readability calibration before profile-weighted evolution claims |
| SLIP runtime selection policy | 3/3 current profiles select one profile-weighted extended MAP-Elites archive elite using switchboard lifecycle metrics; selected grid ids: 3 distinct; selected niches: 3 distinct; mean selection score `0.955828`; 2/2 invalid version/mismatched-corpus probes rejected before selection | proven Stage 0 runtime selection policy superseded for offspring by offspring lineage gate | package runtime integration and manual readability calibration |
| SLIP offspring lineage gate | 3/3 current profiles produce bounded selected offspring from runtime-selected parents; 3 lineage decisions emitted; mean selected offspring score `0.928194`; 1 add-niche and 2 hold-parent outcomes; 2/2 invalid version/mismatched-corpus probes rejected before the offspring gate starts | proven Stage 0 offspring mutation selection and lineage policy superseded for depth by multigeneration runner | manual readability calibration and package runtime integration |
| SLIP long-horizon behavior gate | 3/3 current profiles pass selected-offspring long-horizon switchboard survival; 18/18 held-out generated candidates survive 96 switchboard ticks; 18/18 held-out idle probes die before the horizon; mean switchboard survival ratio `1.0`; mean idle survival ratio `0.114583`; mean need-balance delta vs idle `0.691676`; 2/2 invalid version/mismatched-corpus probes rejected before the long-horizon gate starts; manual readability calibration remains not collected | proven Stage 0 held-out long-horizon behavior gate only | manual readability calibration and package runtime integration |
| SLIP readability calibration gate | 21/21 current long-horizon samples bound to the manual readability protocol; 3 selected offspring and 18 held-out candidates scored by the proxy metric; expected completed reviewer rows: 63; rating rows collected: 0; manual readability calibration ready: false | packet and proxy snapshot prepared; human calibration still absent | collect 63 reviewer rows, verify agreement and proxy-human rank correlation, then rerun calibration |
| SLIP multigeneration lineage runner | 3/3 current profiles persist three-generation candidate lineages; 9/9 selected offspring continue as qualified lineage frontiers; max generation reached: 4; mean selected offspring score `0.925309`; mean selected runtime survival ratio `1.0`; 2 add-niche and 7 hold-parent archive actions; 2/2 invalid version/mismatched-corpus probes rejected before the runner starts | proven Stage 0 lab-only persistent multigeneration lineage runner | package runtime integration and manual readability calibration |
| Mecha engine runtime boundary gate | 5 package/runtime contracts defined; 5/5 premature package/evolution probes rejected; package root exists: false; manual readability rows: 0/63; promotion-ready contracts: 0 | proven Stage 0 package/runtime boundary gate with no package code | explicit package implementation authorization, package import-surface tests, and manual readability calibration |
| CA/NCA growth/repair | growth/repair measured against LCD profile; mixed palettes lower alignment to `0.25` | diagnostic only | profile-matched CA/NCA alignment by palette family |
| CuBFF hybrid transducer | hybrid path reports 12/12 valid and aligned under active profile | limited | real snapshot and multi-profile transducer compatibility |
| Future package tests | generation/lifecycle/property strategies mention SLIP rejection and alignment | specified only | package import-surface tests after package work starts |

## Required Future Compatibility Tests

### 1. Profile Schema Tests

Current Stage 0 schema tests validate:

- exact version handling;
- required metadata;
- known palette IDs;
- legal body-mass bounds;
- known required organ roles;
- required mutation cap keys;
- behavior values in `[0, 1]`;
- survival values in `[0, 1]`;
- no boolean values accepted as numeric profile weights;
- clear error families for every failed field group.

Current Pydantic contract tests add model validation, model-generated JSON
Schema, extra-forbid handling, and corpus parity. Future schema tests must add
runtime JSON Schema engine parity, declared dependency policy, non-`0.1.0`
migration fixture corpora when a new version exists, and unsatisfiable-profile
diagnostics.

### 2. Profile-Grid Alignment Tests

For each valid profile, future tests must check:

- at least one aligned seed or generated grid exists;
- a grid with a disallowed palette fails;
- a grid below `body_mass_min` fails;
- a grid above `body_mass_max` fails;
- a grid missing each required organ role fails;
- a grid exceeding each mutation cap fails;
- validation and alignment do not mutate the profile or grid payload.

### 3. Profile-Constrained Generation Tests

For each valid profile, future tests must check:

- generation either produces valid aligned candidates or fails with an explicit
  unsatisfiable-profile result;
- deterministic seed plus same profile reproduces candidate identity and
  semantic grid signature;
- candidate explanation includes `slip_alignment`;
- rejected proposals are counted and surfaced;
- profile-specific palette constraints are visible in generated output.

Current proof exists for all three valid Stage 0 profiles:

```txt
150 generated candidates
150 valid candidates
150 SLIP-aligned candidates
0 alignment failures
```

### 4. Lifecycle Compatibility Tests

For each valid profile, future tests must check:

- invalid profiles fail before state creation;
- behavior weights are normalized or consumed exactly as documented;
- changing behavior weights changes at least one documented lifecycle decision
  or leaves an explicit no-effect trace;
- survival weights contribute to score computation with a documented formula;
- lifecycle state and rewards stay bounded.

Current lifecycle evidence now proves short-horizon, profile-specific lab
effects for the three current valid profiles and a Stage 0 selector that
consumes lifecycle metrics for profile-specific archive elite choices. The
offspring lineage gate evaluates selected child lifecycle episodes, and the
long-horizon behavior gate proves selected-offspring and held-out switchboard
survival against an idle-neglect contrast. The multigeneration runner now
persists qualified candidate lineages across three generations in the lab.
This is still not enough to claim package runtime behavior integration, manual
readability calibration, or profile-weighted evolution.

### 5. Archive Compatibility Tests

Future archive tests must check:

- `slip_alignment` is a descriptor or score component only when a valid profile
  is present;
- missing or invalid profile produces a blocked/neutral state, not a false
  aligned score;
- descriptor thresholds do not claim human calibration before manual ratings
  exist;
- profile-specific archive coverage can be reported separately from global
  archive coverage.

Current archive evidence now includes profile-specific extended archive probes
and a Stage 0 profile-weighted elite selector for the three current valid
profiles. The offspring lineage gate now specifies bounded child selection and
lineage actions, and the multigeneration runner now exercises three-generation
candidate lineages. It is still not enough to claim package runtime evolution
or final archive replacement thresholds.

### 6. Workshop Compatibility Tests

Future workshop tests must check:

- profile import/export preserves all SLIP fields; minimal current-schema
  authoring panel proof is done in
  `data/workshop_editor/slip_authoring_panel_stage0.json`;
- edited grids remain aligned or report actionable alignment errors;
- native JSON round trips pass for all valid profiles; first generated-corpus
  proof is done in
  `data/workshop_editor/multi_profile_roundtrip_stage0/workshop_multi_profile_roundtrip_stage0.json`;
- held-out generated grids pass import/export fidelity checks; first generated
  multi-profile corpus proof is done;
- invalid profiles cannot be loaded as active workshop constraints;
- static RGBA PNG import/export, 8-bit non-interlaced PNG color/filter variant
  import/export, bounded 8-bit RGBA Adam7 interlace import/export, bounded
  non-interlaced low-bit/16-bit/greyscale-alpha PNG import/export, bounded
  Adam7/deep-color cross-product PNG import/export, bounded full-canvas APNG
  sidecar import/export, bounded PNG/APNG chunk-order conformance, bounded
  APNG partial-frame playback, bounded APNG filtered frame data, bounded APNG
  color-type frame data, bounded APNG bit-depth frame data, bounded APNG
  partial-sample frame data, bounded APNG Adam7 frame data, bounded APNG
  partial Adam7 frame data, bounded PNG/APNG image-data chunking, and bounded
  PNG/APNG zlib compression, and bounded PNG/APNG zlib header policy,
  fixed horizontal-strip spritesheet PNG import/export, and
  vertical/matrix/padded/sparse spritesheet layout import/export, packed
  trim/rotation reconstruction, arbitrary atlas packing, and generated
  multi-page atlas page/frame binding are proven against
  the sidecar contract, and Piskel JSON, Pixelorama `.pxo`, and
  Aseprite/LibreSprite header project boundaries are proven against the same
  sidecar contract;
- full APNG/PNG image-data conformance beyond the bounded chunk-order,
  partial-frame playback, filtered frame-data, color-type frame-data,
  bit-depth frame-data, partial-sample frame-data, Adam7 frame-data, partial
  Adam7 frame-data, image-data chunking, zlib compression, and zlib
  header-policy matrices, full
  project-file coverage, production
  renderer playback, arbitrary Aseprite/LibreSprite project schema coverage,
  and live external editor rewrite validation remain blocked.

Current proof is 150 native JSON round trips across the generated three-profile
SLIP corpus. External sidecar strategy is proven for metadata preservation,
static RGBA PNG sidecar import/export is proven, the PNG variant sidecar decoder
is proven for the explicit 8-bit non-interlaced color/filter subset, bounded
8-bit RGBA Adam7 interlace is proven in
`data/workshop_editor/png_adam7_interlace_decoder_stage0.json`, bounded
non-interlaced low-bit, 16-bit, indexed low-bit, and greyscale-alpha PNG
coverage is proven in
`data/workshop_editor/png_deep_color_sidecar_decoder_stage0.json`, bounded
Adam7/deep-color cross-product coverage is proven in
`data/workshop_editor/png_adam7_deep_color_cross_product_stage0.json`, bounded
full-canvas APNG sidecar coverage is proven in
`data/workshop_editor/apng_sidecar_decoder_stage0.json`, fixed
horizontal-strip spritesheet PNG sidecar import/export is proven, bounded
PNG/APNG chunk-order conformance is proven in
`data/workshop_editor/png_apng_chunk_order_conformance_stage0.json`, bounded
APNG partial-frame playback is proven in
`data/workshop_editor/apng_partial_frame_playback_stage0.json`, bounded
APNG filtered frame data is proven in
`data/workshop_editor/apng_filtered_frame_data_stage0.json`, bounded APNG
color-type frame data is proven in
`data/workshop_editor/apng_color_type_frame_data_stage0.json`, bounded APNG
bit-depth frame data is proven in
`data/workshop_editor/apng_bit_depth_frame_data_stage0.json`, bounded APNG
partial-sample frame data is proven in
`data/workshop_editor/apng_partial_sample_frame_data_stage0.json`, bounded
APNG Adam7 frame data is proven in
`data/workshop_editor/apng_adam7_frame_data_stage0.json`, bounded APNG partial
Adam7 frame data is proven in
`data/workshop_editor/apng_partial_adam7_frame_data_stage0.json`, bounded
PNG/APNG image-data chunking is proven in
`data/workshop_editor/png_apng_image_data_chunking_stage0.json`, bounded
PNG/APNG zlib compression method-0 handling is proven in
`data/workshop_editor/png_apng_zlib_compression_stage0.json`, bounded
PNG/APNG zlib header policy and FDICT rejection are proven in
`data/workshop_editor/png_apng_zlib_header_policy_stage0.json`, the PNG
embedded sidecar writer is proven for the `tEXt` chunk subset, the bounded
PNG textual metadata policy is proven for `tEXt`/`zTXt`/`iTXt` carriers, the
bounded PNG private chunk policy is proven for one app-private `mgOT` carrier,
the simulated private chunk preservation matrix is proven for six
deterministic editor-behavior policies,
and spritesheet layout variants are proven for vertical/matrix/padded/sparse
layouts. Packed trim/rotation spritesheets and sidecar runtime playback are
proven for the Stage 0 subset in
`data/workshop_editor/spritesheet_packed_runtime_decoder_stage0.json`, and
arbitrary atlas packing is proven for shelf and MaxRects-style policies in
`data/workshop_editor/spritesheet_arbitrary_atlas_packer_stage0.json`, and
generated multi-page atlas page/frame binding is proven in
`data/workshop_editor/spritesheet_multi_page_atlas_stage0.json`.
Third-party project boundary decoding is proven for Piskel JSON, Pixelorama
`.pxo` ZIP/data.json, and Aseprite/LibreSprite header payloads.
full APNG/PNG image-data conformance beyond the bounded chunk-order,
partial-frame playback, filtered frame-data, color-type frame-data, and
bit-depth frame-data, partial-sample frame-data, Adam7 frame-data, partial
Adam7 frame-data, image-data chunking, zlib compression, and zlib
header-policy matrices, production
renderer playback, full
editor-native project coverage, arbitrary Aseprite/LibreSprite project schema
coverage, and live external editor rewrite validation remain blocked. Project
native metadata writing is proven only for the Piskel description and
Pixelorama `data.json` subset, deterministic rewrite simulation is proven only
for that same subset, Aseprite/LibreSprite User Data Chunk writing is proven
only for the one-frame compressed RGBA cel subset, and Aseprite/LibreSprite
tags/layers, palette/slice, linked-cel, tilemap/tileset, nested timeline,
external-properties semantics, and document-variant resolution are proven only
for their explicit Stage 0 Aseprite carrier subsets.

## Blocked States

The following claims remain blocked:

- runtime JSON Schema validation, because the dependency selection is not made;
- declared Pydantic package dependency, because no dependency manifest exists;
- profile-weighted evolution, because the runtime selector, offspring gate,
  long-horizon gate, and multigeneration runner are still lab artifacts rather
  than package runtime evolution with calibrated readability thresholds;
- package runtime lifecycle integration, because the runtime boundary gate
  defines the required contracts but the lab selector is not a production
  lifecycle simulator or package import surface;
- manual readability calibration, because archive readability is still proxy
  scored;
- full APNG/PNG conformance,
  because the PNG proofs now cover 8-bit non-interlaced color types 0/2/3/6,
  filters 0..4, bounded 8-bit RGBA Adam7 interlace, and bounded
  non-interlaced and Adam7-interlaced low-bit/16-bit/greyscale-alpha variants,
  plus two-frame full-canvas APNG source-frame carriers, bounded APNG
  textual/private metadata carriers, structural chunk-order fixtures,
  partial-frame playback fixtures, filtered split-`fdAT` frame-data fixtures,
  color-type frame-data fixtures, bit-depth frame-data fixtures,
  partial-sample frame-data fixtures, Adam7 frame-data fixtures, partial
  Adam7 frame-data fixtures, image-data chunking fixtures, zlib compression
  fixtures, and zlib header-policy fixtures only;
- production renderer playback,
  because the packed runtime, arbitrary atlas, and multi-page atlas proofs
  cover only sidecar-described reconstruction and deterministic playback
  sampling;
- full project-format coverage, because the current project-file proof parses
  Piskel JSON, Pixelorama `.pxo` ZIP/data.json, and Aseprite/LibreSprite header
  boundaries only, not full editor-native layer/cel/chunk semantics;
- arbitrary Aseprite/LibreSprite project schema coverage, because the Aseprite
  labs cover fixed User Data, tags/layers, palette/slice, linked-cel,
  tilemap/tileset, nested timeline, external-properties, and deterministic
  document-variant subsets plus a generated external-asset resolver matrix,
  not arbitrary editor-authored project schemas or live editor-authored
  external asset resolution;
- live external editor rewrite validation, because no live editor open-save
  round trip has been collected for the embedded metadata payloads;
- community profile packs, because profile versioning and compatibility
  migration are not defined.

## Future Verification Commands

Research-stage checks:

```powershell
python -m json.tool .\data\slips\slip_profile_compatibility_matrix_stage0.json
python -m json.tool .\research\slip\slip.schema.json
python -m json.tool .\data\slips\slip_schema_validation_stage0.json
python -m json.tool .\research\slip\slip_pydantic_model.schema.json
python -m json.tool .\data\slips\slip_pydantic_contract_stage0.json
python -m json.tool .\data\slips\slip_schema_migration_dependency_gate_stage0.json
python -m json.tool .\data\workshop_editor\slip_authoring_panel_stage0.json
python -m json.tool .\data\workshop_editor\slip_behavior_mutation_preview_stage0.json
python -m json.tool .\data\workshop_editor\slip_lifecycle_archive_effects_stage0.json
python -m json.tool .\data\workshop_editor\slip_runtime_selection_policy_stage0.json
python -m json.tool .\data\workshop_editor\slip_offspring_lineage_gate_stage0.json
python -m json.tool .\data\workshop_editor\slip_long_horizon_behavior_gate_stage0.json
python -m json.tool .\data\workshop_editor\slip_multigeneration_lineage_runner_stage0.json
python -m json.tool .\data\architecture\mecha_engine_runtime_boundary_gate_stage0.json
python -m json.tool .\data\workshop_editor\external_metadata_sidecar_stage0.json
python -m json.tool .\data\workshop_editor\standard_image_sidecar_decoder_stage0.json
python -m json.tool .\data\workshop_editor\png_variant_sidecar_decoder_stage0.json
python -m json.tool .\data\workshop_editor\png_adam7_interlace_decoder_stage0.json
python -m json.tool .\data\workshop_editor\png_deep_color_sidecar_decoder_stage0.json
python -m json.tool .\data\workshop_editor\png_adam7_deep_color_cross_product_stage0.json
python -m json.tool .\data\workshop_editor\apng_sidecar_decoder_stage0.json
python -m json.tool .\data\workshop_editor\apng_metadata_carrier_cross_product_stage0.json
python -m json.tool .\data\workshop_editor\png_apng_chunk_order_conformance_stage0.json
python -m json.tool .\data\workshop_editor\apng_partial_frame_playback_stage0.json
python -m json.tool .\data\workshop_editor\apng_filtered_frame_data_stage0.json
python -m json.tool .\data\workshop_editor\apng_color_type_frame_data_stage0.json
python -m json.tool .\data\workshop_editor\apng_bit_depth_frame_data_stage0.json
python -m json.tool .\data\workshop_editor\apng_partial_sample_frame_data_stage0.json
python -m json.tool .\data\workshop_editor\apng_adam7_frame_data_stage0.json
python -m json.tool .\data\workshop_editor\apng_partial_adam7_frame_data_stage0.json
python -m json.tool .\data\workshop_editor\png_apng_image_data_chunking_stage0.json
python -m json.tool .\data\workshop_editor\png_apng_zlib_compression_stage0.json
python -m json.tool .\data\workshop_editor\png_apng_zlib_header_policy_stage0.json
python -m json.tool .\data\workshop_editor\png_embedded_sidecar_writer_stage0.json
python -m json.tool .\data\workshop_editor\png_textual_metadata_policy_stage0.json
python -m json.tool .\data\workshop_editor\png_private_chunk_policy_stage0.json
python -m json.tool .\data\workshop_editor\png_private_chunk_preservation_matrix_stage0.json
python -m json.tool .\data\workshop_editor\project_native_metadata_writer_stage0.json
python -m json.tool .\data\workshop_editor\project_editor_rewrite_preservation_stage0.json
python -m json.tool .\data\workshop_editor\aseprite_user_data_chunk_writer_stage0.json
python -m json.tool .\data\workshop_editor\aseprite_tags_layers_semantics_stage0.json
python -m json.tool .\data\workshop_editor\aseprite_palette_slice_semantics_stage0.json
python -m json.tool .\data\workshop_editor\aseprite_linked_cel_semantics_stage0.json
python -m json.tool .\data\workshop_editor\aseprite_tilemap_tileset_semantics_stage0.json
python -m json.tool .\data\workshop_editor\aseprite_nested_timeline_semantics_stage0.json
python -m json.tool .\data\workshop_editor\aseprite_external_properties_semantics_stage0.json
python -m json.tool .\data\workshop_editor\aseprite_document_variant_resolution_stage0.json
python -m json.tool .\data\workshop_editor\aseprite_external_asset_resolver_matrix_stage0.json
python -m json.tool .\data\workshop_editor\spritesheet_sidecar_decoder_stage0.json
python -m json.tool .\data\workshop_editor\spritesheet_layout_variant_decoder_stage0.json
python -m json.tool .\data\workshop_editor\spritesheet_packed_runtime_decoder_stage0.json
python -m json.tool .\data\workshop_editor\spritesheet_arbitrary_atlas_packer_stage0.json
python -m json.tool .\data\workshop_editor\spritesheet_multi_page_atlas_stage0.json
python -m json.tool .\data\workshop_editor\third_party_project_decoder_stage0.json
python -B -m unittest .\labs\workshop_editor\test_spritesheet_packed_runtime_decoder.py
python -B -m unittest .\labs\workshop_editor\test_spritesheet_arbitrary_atlas_packer.py
python -B -m unittest .\labs\workshop_editor\test_spritesheet_multi_page_atlas.py
python -B -m unittest .\labs\workshop_editor\test_png_adam7_interlace_decoder.py
python -B -m unittest .\labs\workshop_editor\test_png_deep_color_sidecar_decoder.py
python -B -m unittest .\labs\workshop_editor\test_png_adam7_deep_color_cross_product.py
python -B -m unittest .\labs\workshop_editor\test_png_apng_sidecar_decoder.py
python -B -m unittest .\labs\workshop_editor\test_png_apng_metadata_carrier_cross_product.py
python -B -m unittest .\labs\workshop_editor\test_png_apng_chunk_order_conformance.py
python -B -m unittest .\labs\workshop_editor\test_png_apng_partial_frame_playback.py
python -B -m unittest .\labs\workshop_editor\test_png_apng_filtered_frame_data.py
python -B -m unittest .\labs\workshop_editor\test_png_apng_color_type_frame_data.py
python -B -m unittest .\labs\workshop_editor\test_png_apng_bit_depth_frame_data.py
python -B -m unittest .\labs\workshop_editor\test_png_apng_partial_sample_frame_data.py
python -B -m unittest .\labs\workshop_editor\test_png_apng_adam7_frame_data.py
python -B -m unittest .\labs\workshop_editor\test_png_apng_partial_adam7_frame_data.py
python -B -m unittest .\labs\workshop_editor\test_png_apng_image_data_chunking.py
python -B -m unittest .\labs\workshop_editor\test_png_apng_zlib_compression_matrix.py
python -B -m unittest .\labs\workshop_editor\test_png_apng_zlib_header_policy.py
python -B -m unittest .\labs\workshop_editor\test_png_embedded_sidecar_writer.py
python -B -m unittest .\labs\workshop_editor\test_png_textual_metadata_policy.py
python -B -m unittest .\labs\workshop_editor\test_png_private_chunk_policy.py
python -B -m unittest .\labs\workshop_editor\test_png_private_chunk_preservation_matrix.py
python -B -m unittest .\labs\workshop_editor\test_project_native_metadata_writer.py
python -B -m unittest .\labs\workshop_editor\test_project_editor_rewrite_preservation.py
python -B -m unittest .\labs\workshop_editor\test_aseprite_user_data_chunk_writer.py
python -B -m unittest .\labs\workshop_editor\test_aseprite_tags_layers_semantics.py
python -B -m unittest .\labs\workshop_editor\test_aseprite_palette_slice_semantics.py
python -B -m unittest .\labs\workshop_editor\test_aseprite_linked_cel_semantics.py
python -B -m unittest .\labs\workshop_editor\test_aseprite_tilemap_tileset_semantics.py
python -B -m unittest .\labs\workshop_editor\test_aseprite_nested_timeline_semantics.py
python -B -m unittest .\labs\workshop_editor\test_aseprite_external_properties_semantics.py
python -B -m unittest .\labs\workshop_editor\test_aseprite_document_variant_resolution.py
python -B -m unittest .\labs\workshop_editor\test_aseprite_external_asset_resolver_matrix.py
python -B -m unittest .\labs\architecture\test_mecha_engine_runtime_boundary_gate.py
python -B -m unittest discover -s .\labs\slip_validator -p "test_*.py"
python -B -m unittest discover -s .\labs\workshop_editor -p "test_*.py"
Test-Path .\packages
rg -n "slip_profile_compatibility_matrix|research_slip_profile_compatibility_matrix_no_package_code|profile_compatibility_tests" .\research .\data
git diff --check
```

Existing lab reference checks:

```powershell
python -B -m unittest discover -s .\labs\grid_genome -p "test_*.py"
python -B -m unittest discover -s .\labs\workshop_editor -p "test_*.py"
```

Future package checks become valid only after package work starts:

```powershell
python -B -m unittest discover -s .\packages\mecha_engine\tests -p "test_*.py"
rg -n "from labs|import labs|labs/|labs\\|sys\.path" .\packages\mecha_engine
```

## Decision

Adopt this matrix as the Stage 0 SLIP compatibility test plan. Keep the current
SLIP validator as a narrow lab prototype. Treat the Stage 0 schema, failure
corpus, Pydantic lab model, and migration/dependency gate as the current
file-level profile contract. Treat the measured lifecycle/archive bridge,
runtime selection policy, and offspring lineage gate as Stage 0 lab-only
effect, elite-selection, child-selection, lineage-decision, and long-horizon
behavior probes, not as package runtime evolution. Treat the runtime boundary
gate as the current package/runtime handoff for those labs; it rejects lab
imports, missing dependency manifests, package promotion without a package root,
and profile-weighted evolution claims until package imports and manual
readability calibration exist. Treat the external JSON
sidecar strategy, static RGBA
PNG sidecar decoder, PNG variant sidecar decoder subset, fixed-grid horizontal
spritesheet sidecar decoder, spritesheet layout variant decoder subset, and
packed spritesheet runtime decoder subset as proven for Stage 0 metadata
preservation and playback sampling. Treat the PNG embedded sidecar writer as
proven for Stage 0 PNG `tEXt` chunk metadata preservation only. Treat the PNG
textual metadata policy as proven for the bounded `tEXt`/`zTXt`/`iTXt` carrier
subset only. Treat the PNG private chunk policy as proven for one app-private
`mgOT` carrier and carrier-selection inputs only, not as a final production
carrier decision. Treat the APNG metadata carrier cross-product as proven only
for bounded two-frame APNG files carrying `tEXt`, `zTXt`, `iTXt`, compressed
`iTXt`, and private `mgOT` sidecar metadata under the existing carrier
policies, not as full APNG/PNG conformance or a production carrier decision.
Treat the PNG/APNG chunk order conformance matrix as proof of the bounded
static RGBA, split-IDAT, indexed PLTE/tRNS, and APNG static-first-frame
chunk-order subset only, not full APNG/PNG image-data conformance.
Treat the APNG partial-frame playback matrix as proof of bounded 8-bit RGBA
partial-frame offsets, source/over blend operations, and background/previous
disposal only, not full APNG/PNG image-data conformance.
Treat the APNG filtered frame-data matrix as proof of bounded 8-bit RGBA
non-interlaced PNG filter-method-0 reconstruction and split-`fdAT`
concatenation only, not full APNG/PNG image-data conformance.
Treat the APNG color-type frame-data matrix as proof of bounded 8-bit
non-interlaced color types 0/2/3/4/6, PLTE/tRNS, and alpha-channel
reconstruction only, not full APNG/PNG image-data conformance.
Treat the APNG bit-depth frame-data matrix as proof of bounded non-interlaced
packed 1/2/4-bit and 16-bit samples, filter method 0 row reconstruction, and
split-`fdAT` reconstruction only, not full APNG/PNG image-data conformance.
Treat the APNG partial-sample frame-data matrix as proof of bounded
non-interlaced partial frame offsets for selected packed low-bit, indexed, and
16-bit sample models with source/over composition only, not full APNG/PNG
image-data conformance.
Treat the APNG Adam7 frame-data matrix as proof of bounded full-canvas Adam7
APNG frame reconstruction for selected packed low-bit, indexed, 8-bit, and
16-bit sample models with source/over composition only, not full APNG/PNG
image-data conformance.
Treat the APNG partial Adam7 frame-data matrix as proof of bounded non-zero
offset Adam7 APNG frame reconstruction for selected packed low-bit, indexed,
8-bit, and 16-bit sample models with source/over composition only, not full
APNG/PNG image-data conformance.
Treat the PNG/APNG image-data chunking matrix as proof of bounded IDAT and
fdAT chunk-boundary independence for selected static PNG and APNG frame-data
fixtures only, not full APNG/PNG image-data conformance.
Treat the PNG/APNG zlib compression matrix as proof of bounded zlib
compression-method-0/DEFLATE variant reconstruction for selected static PNG
and APNG frame-data fixtures only, not full APNG/PNG image-data conformance.
Treat the PNG/APNG zlib header policy matrix as proof of bounded zlib
CMF/FLG window handling and FDICT rejection for selected static PNG and APNG
frame-data fixtures only, not full APNG/PNG image-data conformance.
Treat the third-party project decoder
boundary as proof of sidecar binding for Piskel JSON, Pixelorama `.pxo`
ZIP/data.json, and Aseprite/LibreSprite header payloads, not as proof of broad
image/project interoperability. Treat the project native metadata writer as
proof of Piskel description and Pixelorama `data.json` metadata preservation
only, not as proof of live external editor rewrite validation or
Aseprite/LibreSprite coverage through that API. Treat the Aseprite User Data
Chunk writer as proof of the one-frame compressed RGBA cel subset only, and
treat the Aseprite tags/layers semantics lab as proof of the explicit
three-frame, three-layer, three-tag subset only. Treat the Aseprite
palette/slice semantics lab as proof of the explicit Palette Chunk `0x2019`
SLIP color subset and Slice Chunk `0x2022` organ-bounds subset only. Treat the
Aseprite linked-cel semantics lab as proof of the explicit Cel Chunk `0x2005`
linked cel type 1 frame-target subset only. Treat the Aseprite tilemap/tileset
semantics lab as proof of one Tilemap Layer type 2, one Tileset Chunk `0x2023`,
and compressed Tilemap Cel Chunk `0x2005` type 3 payloads only. Treat the
Aseprite nested timeline semantics lab as proof of the fixed group-layer,
tag-User-Data, and timeline loop-direction subset only. Treat the Aseprite
external properties semantics lab as proof of the fixed color-profile,
external-file-reference, User Data property-map, extension property-map, and
Cel Extra precise-bounds subset only. Treat the Aseprite document variant
resolution lab as proof of deterministic indexed 8 bpp, grayscale-alpha
16 bpp, RGBA 32 bpp, generated external asset resolution, and variant
hash-validation subsets only. Treat the Aseprite external asset resolver
matrix as proof of generated direct, relative-path, content-addressed, and
multi-root resolver policies only, not editor-authored arbitrary asset
resolution. Do not claim arbitrary Aseprite project schema coverage. Do not
claim full
profile-authoring compatibility until
runtime JSON Schema validation, declared dependency policy, package lifecycle
runtime integration, manual readability calibration, usability evidence, full
project-format coverage, live external editor rewrite validation, final PNG
production carrier selection, arbitrary Aseprite
project schemas, editor-authored Aseprite external asset resolution, editor-authored Aseprite
document variants, production renderer playback, and remaining APNG/PNG
conformance questions are proven or explicitly rejected.

Next research step:

```txt
Collect live external editor open-save fixtures, broaden remaining PNG/APNG
coverage beyond the bounded chunk-order, partial-frame playback, filtered
frame-data, color-type frame-data, bit-depth frame-data, partial-sample
frame-data, Adam7 frame-data, partial Adam7 frame-data, image-data chunking,
zlib compression, and zlib header-policy matrices through additional image-data conformance
fixtures, broaden Aseprite
chunk/schema coverage beyond
the fixed Stage 0 carrier subsets with editor-authored document variants and
editor-authored external asset resolution, collect 63 SLIP readability reviewer
rows, and start package implementation only when explicitly authorized before
claiming profile-weighted evolution.
```

## References

- `docs/01-brainstorming.md`
- `docs/02-research_plan.md`
- `data/slips/README.md`
- `data/slips/valid/slip_lcd_seed.json`
- `data/slips/valid/slip_gray_stable.json`
- `data/slips/valid/slip_amber_social.json`
- `data/slips/invalid/slip_invalid_bad_weight.json`
- `data/slips/invalid/slip_invalid_palette.json`
- `labs/grid_genome/slip.py`
- `labs/grid_genome/test_slip_constraints.py`
- `research/algorithm_cards/slip_schema_validator.md`
- `research/experiment_reports/2026-05-12-slip-constraint-baseline.md`
- `research/experiment_reports/2026-05-12-slip-multi-profile-generation-benchmark.md`
- `research/experiment_reports/2026-05-12-workshop-multi-profile-roundtrip.md`
- `research/experiment_reports/2026-05-12-slip-schema-failure-corpus.md`
- `research/slip/slip.schema.json`
- `research/slip/slip_examples/`
- `research/slip/slip_failure_cases.md`
- `data/slips/slip_schema_validation_stage0.json`
- `research/slip/pydantic_contract.md`
- `research/slip/slip_pydantic_model.schema.json`
- `data/slips/slip_pydantic_contract_stage0.json`
- `research/slip/schema_migration_dependency_gate.md`
- `data/slips/slip_schema_migration_dependency_gate_stage0.json`
- `research/experiment_reports/2026-05-12-slip-authoring-panel.md`
- `research/experiment_reports/2026-05-12-slip-behavior-mutation-preview-gate.md`
- `research/experiment_reports/2026-05-12-slip-lifecycle-archive-effects.md`
- `research/experiment_reports/2026-05-13-slip-runtime-selection-policy.md`
- `research/experiment_reports/2026-05-13-slip-offspring-lineage-gate.md`
- `research/experiment_reports/2026-05-13-slip-long-horizon-behavior-gate.md`
- `research/experiment_reports/2026-05-13-mecha-engine-runtime-boundary-gate.md`
- `research/experiment_reports/2026-05-12-external-metadata-sidecar-strategy.md`
- `research/experiment_reports/2026-05-12-standard-image-sidecar-decoder.md`
- `research/experiment_reports/2026-05-13-png-variant-sidecar-decoder.md`
- `research/experiment_reports/2026-05-14-png-deep-color-sidecar-decoder.md`
- `research/algorithm_cards/png_deep_color_sidecar_decoder.md`
- `research/experiment_reports/2026-05-14-png-adam7-deep-color-cross-product.md`
- `research/algorithm_cards/png_adam7_deep_color_cross_product.md`
- `research/experiment_reports/2026-05-14-apng-sidecar-decoder.md`
- `research/algorithm_cards/png_apng_sidecar_decoder.md`
- `research/experiment_reports/2026-05-14-apng-metadata-carrier-cross-product.md`
- `research/algorithm_cards/png_apng_metadata_carrier_cross_product.md`
- `research/experiment_reports/2026-05-14-png-apng-chunk-order-conformance.md`
- `research/algorithm_cards/png_apng_chunk_order_conformance.md`
- `research/experiment_reports/2026-05-14-apng-partial-frame-playback.md`
- `research/algorithm_cards/png_apng_partial_frame_playback.md`
- `research/experiment_reports/2026-05-14-apng-filtered-frame-data.md`
- `research/algorithm_cards/png_apng_filtered_frame_data.md`
- `research/experiment_reports/2026-05-14-apng-color-type-frame-data.md`
- `research/algorithm_cards/png_apng_color_type_frame_data.md`
- `research/experiment_reports/2026-05-14-apng-bit-depth-frame-data.md`
- `research/algorithm_cards/png_apng_bit_depth_frame_data.md`
- `research/experiment_reports/2026-05-14-apng-partial-sample-frame-data.md`
- `research/algorithm_cards/png_apng_partial_sample_frame_data.md`
- `research/experiment_reports/2026-05-14-apng-adam7-frame-data.md`
- `research/algorithm_cards/png_apng_adam7_frame_data.md`
- `research/experiment_reports/2026-05-14-apng-partial-adam7-frame-data.md`
- `research/algorithm_cards/png_apng_partial_adam7_frame_data.md`
- `research/experiment_reports/2026-05-14-png-apng-image-data-chunking.md`
- `research/algorithm_cards/png_apng_image_data_chunking.md`
- `research/experiment_reports/2026-05-14-png-apng-zlib-compression-matrix.md`
- `research/algorithm_cards/png_apng_zlib_compression_matrix.md`
- `research/experiment_reports/2026-05-14-png-apng-zlib-header-policy.md`
- `research/algorithm_cards/png_apng_zlib_header_policy.md`
- `research/experiment_reports/2026-05-13-png-embedded-sidecar-writer.md`
- `research/experiment_reports/2026-05-14-png-textual-metadata-policy.md`
- `research/experiment_reports/2026-05-14-png-private-chunk-policy.md`
- `research/experiment_reports/2026-05-14-png-private-chunk-preservation-matrix.md`
- `research/algorithm_cards/png_private_chunk_preservation_matrix.md`
- `research/experiment_reports/2026-05-12-spritesheet-sidecar-decoder.md`
- `research/experiment_reports/2026-05-13-spritesheet-layout-variant-decoder.md`
- `research/experiment_reports/2026-05-13-spritesheet-packed-runtime-decoder.md`
- `research/experiment_reports/2026-05-14-spritesheet-arbitrary-atlas-packer.md`
- `research/experiment_reports/2026-05-13-third-party-project-decoder-boundary.md`
- `research/experiment_reports/2026-05-13-project-editor-rewrite-preservation.md`
- `research/experiment_reports/2026-05-14-aseprite-user-data-chunk-writer.md`
- `research/experiment_reports/2026-05-14-aseprite-tags-layers-semantics.md`
- `research/experiment_reports/2026-05-14-aseprite-external-asset-resolver-matrix.md`
- `research/algorithm_cards/aseprite_external_asset_resolver_matrix.md`
- `labs/workshop_editor/slip_authoring_panel.py`
- `labs/workshop_editor/slip_preview_gates.py`
- `labs/workshop_editor/slip_lifecycle_archive_effects.py`
- `labs/workshop_editor/slip_runtime_selection_policy.py`
- `labs/workshop_editor/slip_offspring_lineage_gate.py`
- `labs/workshop_editor/slip_long_horizon_behavior_gate.py`
- `labs/workshop_editor/slip_multigeneration_lineage_runner.py`
- `labs/architecture/mecha_engine_runtime_boundary_gate.py`
- `labs/workshop_editor/external_metadata_sidecar.py`
- `labs/workshop_editor/standard_image_sidecar_decoder.py`
- `labs/workshop_editor/png_variant_sidecar_decoder.py`
- `labs/workshop_editor/png_adam7_interlace_decoder.py`
- `labs/workshop_editor/png_deep_color_sidecar_decoder.py`
- `labs/workshop_editor/png_adam7_deep_color_cross_product.py`
- `labs/workshop_editor/png_apng_sidecar_decoder.py`
- `labs/workshop_editor/png_apng_metadata_carrier_cross_product.py`
- `labs/workshop_editor/png_apng_chunk_order_conformance.py`
- `labs/workshop_editor/png_apng_partial_frame_playback.py`
- `labs/workshop_editor/png_apng_filtered_frame_data.py`
- `labs/workshop_editor/png_apng_color_type_frame_data.py`
- `labs/workshop_editor/png_apng_bit_depth_frame_data.py`
- `labs/workshop_editor/png_apng_partial_sample_frame_data.py`
- `labs/workshop_editor/png_apng_adam7_frame_data.py`
- `labs/workshop_editor/png_apng_partial_adam7_frame_data.py`
- `labs/workshop_editor/png_apng_image_data_chunking.py`
- `labs/workshop_editor/png_apng_zlib_compression_matrix.py`
- `labs/workshop_editor/png_apng_zlib_header_policy.py`
- `labs/workshop_editor/png_embedded_sidecar_writer.py`
- `labs/workshop_editor/png_textual_metadata_policy.py`
- `labs/workshop_editor/png_private_chunk_policy.py`
- `labs/workshop_editor/png_private_chunk_preservation_matrix.py`
- `labs/workshop_editor/spritesheet_sidecar_decoder.py`
- `labs/workshop_editor/spritesheet_layout_variant_decoder.py`
- `labs/workshop_editor/spritesheet_packed_runtime_decoder.py`
- `labs/workshop_editor/spritesheet_arbitrary_atlas_packer.py`
- `labs/workshop_editor/third_party_project_decoder.py`
- `labs/workshop_editor/project_native_metadata_writer.py`
- `labs/workshop_editor/project_editor_rewrite_preservation.py`
- `labs/workshop_editor/aseprite_user_data_chunk_writer.py`
- `labs/workshop_editor/aseprite_tags_layers_semantics.py`
- `labs/workshop_editor/aseprite_external_asset_resolver_matrix.py`
- `data/workshop_editor/slip_authoring_panel_stage0.json`
- `data/workshop_editor/slip_behavior_mutation_preview_stage0.json`
- `data/workshop_editor/slip_lifecycle_archive_effects_stage0.json`
- `data/workshop_editor/slip_runtime_selection_policy_stage0.json`
- `data/workshop_editor/slip_offspring_lineage_gate_stage0.json`
- `data/workshop_editor/slip_long_horizon_behavior_gate_stage0.json`
- `data/workshop_editor/slip_multigeneration_lineage_runner_stage0.json`
- `data/architecture/mecha_engine_runtime_boundary_gate_stage0.json`
- `data/workshop_editor/external_metadata_sidecar_stage0.json`
- `data/workshop_editor/standard_image_sidecar_decoder_stage0.json`
- `data/workshop_editor/png_variant_sidecar_decoder_stage0.json`
- `data/workshop_editor/png_adam7_interlace_decoder_stage0.json`
- `data/workshop_editor/png_deep_color_sidecar_decoder_stage0.json`
- `data/workshop_editor/png_adam7_deep_color_cross_product_stage0.json`
- `data/workshop_editor/apng_sidecar_decoder_stage0.json`
- `data/workshop_editor/apng_metadata_carrier_cross_product_stage0.json`
- `data/workshop_editor/png_apng_chunk_order_conformance_stage0.json`
- `data/workshop_editor/apng_partial_frame_playback_stage0.json`
- `data/workshop_editor/apng_filtered_frame_data_stage0.json`
- `data/workshop_editor/apng_color_type_frame_data_stage0.json`
- `data/workshop_editor/apng_bit_depth_frame_data_stage0.json`
- `data/workshop_editor/apng_partial_sample_frame_data_stage0.json`
- `data/workshop_editor/apng_adam7_frame_data_stage0.json`
- `data/workshop_editor/apng_partial_adam7_frame_data_stage0.json`
- `data/workshop_editor/png_apng_image_data_chunking_stage0.json`
- `data/workshop_editor/png_apng_zlib_compression_stage0.json`
- `data/workshop_editor/png_apng_zlib_header_policy_stage0.json`
- `data/workshop_editor/png_embedded_sidecar_writer_stage0.json`
- `data/workshop_editor/png_textual_metadata_policy_stage0.json`
- `data/workshop_editor/png_private_chunk_policy_stage0.json`
- `data/workshop_editor/png_private_chunk_preservation_matrix_stage0.json`
- `data/workshop_editor/spritesheet_sidecar_decoder_stage0.json`
- `data/workshop_editor/spritesheet_layout_variant_decoder_stage0.json`
- `data/workshop_editor/spritesheet_packed_runtime_decoder_stage0.json`
- `data/workshop_editor/spritesheet_arbitrary_atlas_packer_stage0.json`
- `data/workshop_editor/third_party_project_decoder_stage0.json`
- `data/workshop_editor/project_native_metadata_writer_stage0.json`
- `data/workshop_editor/project_editor_rewrite_preservation_stage0.json`
- `data/workshop_editor/aseprite_user_data_chunk_writer_stage0.json`
- `data/workshop_editor/aseprite_tags_layers_semantics_stage0.json`
- `data/workshop_editor/aseprite_external_asset_resolver_matrix_stage0.json`
- `data/workshop_editor/external_metadata_sidecar_stage0/`
- `data/workshop_editor/standard_image_sidecar_decoder_stage0/`
- `data/workshop_editor/png_variant_sidecar_decoder_stage0/`
- `data/workshop_editor/png_adam7_interlace_decoder_stage0/`
- `data/workshop_editor/png_deep_color_sidecar_decoder_stage0/`
- `data/workshop_editor/png_adam7_deep_color_cross_product_stage0/`
- `data/workshop_editor/apng_sidecar_decoder_stage0/`
- `data/workshop_editor/apng_metadata_carrier_cross_product_stage0/`
- `data/workshop_editor/png_apng_chunk_order_conformance_stage0/`
- `data/workshop_editor/apng_partial_frame_playback_stage0/`
- `data/workshop_editor/apng_filtered_frame_data_stage0/`
- `data/workshop_editor/apng_color_type_frame_data_stage0/`
- `data/workshop_editor/apng_bit_depth_frame_data_stage0/`
- `data/workshop_editor/apng_partial_sample_frame_data_stage0/`
- `data/workshop_editor/apng_partial_adam7_frame_data_stage0/`
- `data/workshop_editor/png_apng_image_data_chunking_stage0/`
- `data/workshop_editor/png_apng_zlib_compression_stage0/`
- `data/workshop_editor/png_apng_zlib_header_policy_stage0/`
- `data/workshop_editor/png_embedded_sidecar_writer_stage0/`
- `data/workshop_editor/png_textual_metadata_policy_stage0/`
- `data/workshop_editor/png_private_chunk_policy_stage0/`
- `data/workshop_editor/png_private_chunk_preservation_matrix_stage0/`
- `data/workshop_editor/spritesheet_sidecar_decoder_stage0/`
- `data/workshop_editor/spritesheet_layout_variant_decoder_stage0/`
- `data/workshop_editor/spritesheet_packed_runtime_decoder_stage0/`
- `data/workshop_editor/spritesheet_arbitrary_atlas_packer_stage0/`
- `data/workshop_editor/third_party_project_decoder_stage0/`
- `data/workshop_editor/project_native_metadata_writer_stage0/`
- `data/workshop_editor/project_editor_rewrite_preservation_stage0/`
- `data/workshop_editor/aseprite_user_data_chunk_writer_stage0/`
- `data/workshop_editor/aseprite_tags_layers_semantics_stage0/`
- `data/workshop_editor/aseprite_external_asset_resolver_matrix_stage0/`
- `data/workshop_editor/slip_authoring_panel_stage0/`
- `data/workshop_editor/slip_behavior_mutation_preview_stage0/`
- `data/workshop_editor/slip_lifecycle_archive_effects_stage0/`
- `data/workshop_editor/slip_runtime_selection_policy_stage0/`
- `data/workshop_editor/slip_offspring_lineage_gate_stage0/`
- `data/workshop_editor/slip_long_horizon_behavior_gate_stage0/`
- `data/workshop_editor/slip_multigeneration_lineage_runner_stage0/`
- `data/architecture/mecha_engine_runtime_boundary_gate_stage0/`
- `data/generated_grids/slip_lcd_seed_constrained/README.md`
- `data/slips/multi_profile_generation_stage0/slip_multi_profile_generation_stage0.json`
- `data/workshop_editor/multi_profile_roundtrip_stage0/workshop_multi_profile_roundtrip_stage0.json`
- [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12)
- [Pydantic JSON Schema docs](https://docs.pydantic.dev/latest/concepts/json_schema/)
- [Avida Digital Evolution Platform](https://avida.devosoft.org/)
- [JaxLife: An Open-Ended Agentic Simulator](https://arxiv.org/abs/2409.00853)
- [Reinforcement Learning: An Introduction](https://mitpress.mit.edu/9780262039246/reinforcement-learning/)
