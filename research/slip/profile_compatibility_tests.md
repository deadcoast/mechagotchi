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
| PNG embedded sidecar writer | `data/workshop_editor/png_embedded_sidecar_writer_stage0.json` | 1 | 3 embedded PNG `tEXt` sidecar round trips, decoded pixels preserved, 3 invalid embedded metadata probes rejected |
| PNG textual metadata policy | `data/workshop_editor/png_textual_metadata_policy_stage0.json` | 1 | 12 bounded PNG textual metadata round trips across `tEXt`, `zTXt`, uncompressed `iTXt`, and compressed `iTXt`; 7 invalid metadata policy probes rejected |
| PNG private chunk policy | `data/workshop_editor/png_private_chunk_policy_stage0.json` | 1 | 3 app-private PNG `mgOT` ancillary chunk round trips; 7 invalid private chunk probes rejected; carrier-selection inputs recorded without final production decision |
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
| Standard image sidecar decoder | 3/3 current profile grids export to real static RGBA PNG, decode with PNG signature/chunk/CRC/IDAT checks, restore SLIP-aligned semantic grids from sidecars, and reject 2/2 corrupt PNG or hash-mismatch probes | proven static non-interlaced 8-bit RGBA PNG only; superseded for broader color/filter variants by PNG variant sidecar decoder | Adam7/APNG/full PNG conformance remains separate |
| PNG variant sidecar decoder | 15/15 current profile PNG variants export/import with sidecars across 8-bit non-interlaced color types 0, 2, 3, and 6; filter types 0 through 4; PLTE indexed-color decoding; 3/3 invalid interlace/PLTE/carrier-hash probes rejected | proven Stage 0 PNG variant subset only | Adam7 interlace, APNG, grayscale-alpha, 1/2/4/16-bit depths, and full PNG conformance |
| PNG embedded sidecar writer | 3/3 current profile PNG files embed Mechagotchi sidecar JSON in a PNG `tEXt` ancillary chunk, preserve decoded pixels, restore SLIP-aligned semantic grids, and reject 3/3 missing metadata, invalid JSON, or canonical-hash mismatch probes | proven Stage 0 embedded PNG text-chunk sidecar subset; textual variant policy is superseded by PNG textual metadata policy | live external editor rewrite validation, Adam7/APNG/full PNG conformance, and project-file native metadata beyond Piskel/Pixelorama |
| PNG textual metadata policy | 12/12 current profile PNG textual metadata variants round-trip sidecar semantics across `tEXt` ASCII JSON, `zTXt` compressed ASCII JSON, uncompressed `iTXt` UTF-8 JSON, and compressed `iTXt` UTF-8 JSON; 7/7 invalid missing, duplicate, non-ASCII text-policy, compression, UTF-8, and canonical-hash probes rejected | proven Stage 0 bounded textual metadata carrier policy only; private chunk policy is handled separately | live external editor rewrite validation, Adam7/APNG/full PNG conformance, and production import/export carrier selection |
| PNG private chunk policy | 3/3 current profile PNG files round-trip sidecar semantics through one `mgOT` ancillary private unsafe-to-copy chunk with a magic-prefixed UTF-8 JSON payload; 7/7 invalid missing, duplicate, safe-to-copy type, magic, JSON, canonical-hash, and sidecar-hash probes rejected; carrier-selection inputs recorded | proven Stage 0 bounded private ancillary chunk policy and carrier-selection input matrix only | live external editor rewrite validation, private chunk editor preservation matrix, Adam7/APNG/full PNG conformance, and final production import/export carrier selection |
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
  import/export, fixed horizontal-strip spritesheet PNG import/export, and
  vertical/matrix/padded/sparse spritesheet layout import/export, packed
  trim/rotation reconstruction, arbitrary atlas packing, and generated
  multi-page atlas page/frame binding are proven against
  the sidecar contract, and Piskel JSON, Pixelorama `.pxo`, and
  Aseprite/LibreSprite header project boundaries are proven against the same
  sidecar contract;
- Adam7/APNG/full PNG conformance, full project-file
  coverage, production renderer playback, arbitrary Aseprite/LibreSprite
  project schema coverage, and live external editor rewrite validation remain
  blocked.

Current proof is 150 native JSON round trips across the generated three-profile
SLIP corpus. External sidecar strategy is proven for metadata preservation,
static RGBA PNG sidecar import/export is proven, the PNG variant sidecar decoder
is proven for the explicit 8-bit non-interlaced color/filter subset, fixed
horizontal-strip spritesheet PNG sidecar import/export is proven, the PNG
embedded sidecar writer is proven for the `tEXt` chunk subset, the bounded PNG
textual metadata policy is proven for `tEXt`/`zTXt`/`iTXt` carriers, the
bounded PNG private chunk policy is proven for one app-private `mgOT` carrier,
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
Adam7/APNG/full PNG conformance, production
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
- Adam7/APNG/full PNG conformance, because the PNG variant proof covers only
  8-bit non-interlaced color types 0/2/3/6 and filter types 0..4;
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
  document-variant subsets, not arbitrary editor-authored project schemas or
  arbitrary external asset resolution;
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
python -m json.tool .\data\workshop_editor\png_embedded_sidecar_writer_stage0.json
python -m json.tool .\data\workshop_editor\png_textual_metadata_policy_stage0.json
python -m json.tool .\data\workshop_editor\png_private_chunk_policy_stage0.json
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
python -m json.tool .\data\workshop_editor\spritesheet_sidecar_decoder_stage0.json
python -m json.tool .\data\workshop_editor\spritesheet_layout_variant_decoder_stage0.json
python -m json.tool .\data\workshop_editor\spritesheet_packed_runtime_decoder_stage0.json
python -m json.tool .\data\workshop_editor\spritesheet_arbitrary_atlas_packer_stage0.json
python -m json.tool .\data\workshop_editor\spritesheet_multi_page_atlas_stage0.json
python -m json.tool .\data\workshop_editor\third_party_project_decoder_stage0.json
python -B -m unittest .\labs\workshop_editor\test_spritesheet_packed_runtime_decoder.py
python -B -m unittest .\labs\workshop_editor\test_spritesheet_arbitrary_atlas_packer.py
python -B -m unittest .\labs\workshop_editor\test_spritesheet_multi_page_atlas.py
python -B -m unittest .\labs\workshop_editor\test_png_embedded_sidecar_writer.py
python -B -m unittest .\labs\workshop_editor\test_png_textual_metadata_policy.py
python -B -m unittest .\labs\workshop_editor\test_png_private_chunk_policy.py
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
carrier decision. Treat the third-party project decoder
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
hash-validation subsets only. Do not claim arbitrary Aseprite project schema
coverage. Do not claim full
profile-authoring compatibility until
runtime JSON Schema validation, declared dependency policy, package lifecycle
runtime integration, manual readability calibration, usability evidence, full
project-format coverage, live external editor rewrite validation, final PNG
production carrier selection, arbitrary Aseprite
project schemas, arbitrary external asset resolution, editor-authored Aseprite
document variants, production renderer playback, and full PNG conformance
questions are proven or explicitly rejected.

Next research step:

```txt
Collect live external editor open-save fixtures, broaden Aseprite chunk/schema
coverage beyond the fixed Stage 0 carrier subsets with editor-authored
document variants and arbitrary external asset resolution, collect 63 SLIP
readability reviewer rows, and start package implementation only when
explicitly authorized before claiming profile-weighted evolution.
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
- `research/experiment_reports/2026-05-13-png-embedded-sidecar-writer.md`
- `research/experiment_reports/2026-05-14-png-textual-metadata-policy.md`
- `research/experiment_reports/2026-05-14-png-private-chunk-policy.md`
- `research/experiment_reports/2026-05-12-spritesheet-sidecar-decoder.md`
- `research/experiment_reports/2026-05-13-spritesheet-layout-variant-decoder.md`
- `research/experiment_reports/2026-05-13-spritesheet-packed-runtime-decoder.md`
- `research/experiment_reports/2026-05-14-spritesheet-arbitrary-atlas-packer.md`
- `research/experiment_reports/2026-05-13-third-party-project-decoder-boundary.md`
- `research/experiment_reports/2026-05-13-project-editor-rewrite-preservation.md`
- `research/experiment_reports/2026-05-14-aseprite-user-data-chunk-writer.md`
- `research/experiment_reports/2026-05-14-aseprite-tags-layers-semantics.md`
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
- `labs/workshop_editor/png_embedded_sidecar_writer.py`
- `labs/workshop_editor/png_textual_metadata_policy.py`
- `labs/workshop_editor/png_private_chunk_policy.py`
- `labs/workshop_editor/spritesheet_sidecar_decoder.py`
- `labs/workshop_editor/spritesheet_layout_variant_decoder.py`
- `labs/workshop_editor/spritesheet_packed_runtime_decoder.py`
- `labs/workshop_editor/spritesheet_arbitrary_atlas_packer.py`
- `labs/workshop_editor/third_party_project_decoder.py`
- `labs/workshop_editor/project_native_metadata_writer.py`
- `labs/workshop_editor/project_editor_rewrite_preservation.py`
- `labs/workshop_editor/aseprite_user_data_chunk_writer.py`
- `labs/workshop_editor/aseprite_tags_layers_semantics.py`
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
- `data/workshop_editor/png_embedded_sidecar_writer_stage0.json`
- `data/workshop_editor/png_textual_metadata_policy_stage0.json`
- `data/workshop_editor/png_private_chunk_policy_stage0.json`
- `data/workshop_editor/spritesheet_sidecar_decoder_stage0.json`
- `data/workshop_editor/spritesheet_layout_variant_decoder_stage0.json`
- `data/workshop_editor/spritesheet_packed_runtime_decoder_stage0.json`
- `data/workshop_editor/spritesheet_arbitrary_atlas_packer_stage0.json`
- `data/workshop_editor/third_party_project_decoder_stage0.json`
- `data/workshop_editor/project_native_metadata_writer_stage0.json`
- `data/workshop_editor/project_editor_rewrite_preservation_stage0.json`
- `data/workshop_editor/aseprite_user_data_chunk_writer_stage0.json`
- `data/workshop_editor/aseprite_tags_layers_semantics_stage0.json`
- `data/workshop_editor/external_metadata_sidecar_stage0/`
- `data/workshop_editor/standard_image_sidecar_decoder_stage0/`
- `data/workshop_editor/png_variant_sidecar_decoder_stage0/`
- `data/workshop_editor/png_embedded_sidecar_writer_stage0/`
- `data/workshop_editor/png_textual_metadata_policy_stage0/`
- `data/workshop_editor/png_private_chunk_policy_stage0/`
- `data/workshop_editor/spritesheet_sidecar_decoder_stage0/`
- `data/workshop_editor/spritesheet_layout_variant_decoder_stage0/`
- `data/workshop_editor/spritesheet_packed_runtime_decoder_stage0/`
- `data/workshop_editor/spritesheet_arbitrary_atlas_packer_stage0/`
- `data/workshop_editor/third_party_project_decoder_stage0/`
- `data/workshop_editor/project_native_metadata_writer_stage0/`
- `data/workshop_editor/project_editor_rewrite_preservation_stage0/`
- `data/workshop_editor/aseprite_user_data_chunk_writer_stage0/`
- `data/workshop_editor/aseprite_tags_layers_semantics_stage0/`
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
- JSON Schema Draft 2020-12: https://json-schema.org/draft/2020-12
- Pydantic JSON Schema docs: https://docs.pydantic.dev/latest/concepts/json_schema/
- Avida Digital Evolution Platform: https://avida.devosoft.org/
- JaxLife: An Open-Ended Agentic Simulator: https://arxiv.org/abs/2409.00853
- Reinforcement Learning: An Introduction: https://mitpress.mit.edu/9780262039246/reinforcement-learning/
