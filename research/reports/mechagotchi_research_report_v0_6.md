# Mechagotchi Research Report v0.6

Date: 2026-07-04

## Executive Summary

The post-v0.5 research continuation consolidates 46 experiment reports dated
2026-05-13 through 2026-07-04. It covers three large waves:

1. The SLIP evolution-gate wave: runtime lifecycle/archive elite selection,
   bounded offspring mutation and lineage replacement, held-out long-horizon
   behavior tests, persistent multigeneration lineage, the readability
   calibration reviewer packet, and the `mecha_engine` runtime boundary gate.
2. The workshop interoperability wave: third-party project-file boundaries and
   native metadata, spritesheet layout/packing/atlas coverage, bounded PNG
   conformance matrices, bounded APNG frame-data cross-products, and the
   Aseprite/LibreSprite chunk-semantics family.
3. The 2026-07-04 code-review remediation wave driven by
   `docs/03-code_review/2026-07-04-code_review.md`: environment-decoupled SLIP
   dependency gate tests, lab/authoritative SLIP validator alignment, and the
   MAP-Elites behavior-neediness descriptor fix.

The key conclusion remains conservative. Every proof in this window is a
Stage 0 lab proof over the current generated profile corpus. There is still no
`packages/mecha_engine` code, no package runtime lifecycle integration, no
manual readability calibration (0 of 63 reviewer rows collected), no live
external editor validation, and no profile-weighted evolution claim. The
code-review remediation is in progress; further remediation reports will be
consolidated in v0.7.

This report consolidates and links the underlying experiment reports; it does
not replace them.

## Research Scope

This report consolidates the post-v0.5 sequence:

1. Specify runtime lifecycle/archive selection, offspring lineage, long-horizon
   behavior, and multigeneration lineage gates for current SLIP profiles.
2. Prepare the SLIP long-horizon corpus for manual readability review and gate
   the `mecha_engine` runtime boundary without creating package code.
3. Decode third-party project-file boundaries and prove native metadata and
   simulated editor-rewrite preservation for the Piskel/Pixelorama subset.
4. Broaden spritesheet coverage to layout variants, packed trim/rotation,
   arbitrary rectangle atlases, and multi-page atlas bundles.
5. Broaden PNG coverage to textual/private metadata carriers, Adam7 interlace,
   deep color, and the Adam7/deep-color cross-product.
6. Prove bounded APNG frame-data behavior across blend/disposal, filters,
   color types, bit depths, partial regions, Adam7, chunk order, image-data
   chunking, and zlib compression/header policy.
7. Prove Aseprite/LibreSprite chunk-semantics subsets from User Data chunks to
   document variants and external asset resolver policies.
8. Remediate 2026-07-04 code-review findings H-01, H-02, H-03, M-05, M-06,
   M-15 (test surface), and the first half of L-01.

## Primary Artifacts

| Area | Artifact |
| --- | --- |
| SLIP runtime selection | `data/workshop_editor/slip_runtime_selection_policy_stage0.json` |
| SLIP offspring lineage | `data/workshop_editor/slip_offspring_lineage_gate_stage0.json` |
| SLIP long-horizon behavior | `data/workshop_editor/slip_long_horizon_behavior_gate_stage0.json` |
| SLIP multigeneration lineage | `data/workshop_editor/slip_multigeneration_lineage_runner_stage0.json` |
| Readability calibration packet | `data/readability/slip_readability_calibration_gate_stage0.json` |
| Runtime boundary gate | `data/architecture/mecha_engine_runtime_boundary_gate_stage0.json` |
| Third-party project boundary | `data/workshop_editor/third_party_project_decoder_stage0.json` |
| Aseprite resolver matrix | `data/workshop_editor/aseprite_external_asset_resolver_matrix_stage0.json` |
| PNG Adam7/deep-color cross | `data/workshop_editor/png_adam7_deep_color_cross_product_stage0.json` |
| APNG partial Adam7 frames | `data/workshop_editor/apng_partial_adam7_frame_data_stage0.json` |
| PNG/APNG zlib header policy | `data/workshop_editor/png_apng_zlib_header_policy_stage0.json` |
| Extended MAP-Elites archive (post-fix) | `data/archives/map_elites_extended_stage0.json` |

## Cluster Results

### 1. SLIP Evolution and Boundary Gates (2026-05-13, 6 reports)

| Gate | Evidence Anchor | Closed | Still Blocked |
| --- | ---: | --- | --- |
| Runtime selection policy | 3/3 profiles selected distinct archive elites; mean selection score `0.955828` | runtime lifecycle/archive selection trace | profile-weighted evolution |
| Offspring lineage gate | 3 lineage decisions (1 add-niche, 2 hold-parent); mean offspring score `0.928194` | offspring mutation selection, replacement policy | package runtime integration |
| Long-horizon behavior gate | 96-tick probes: switchboard survival `1.0` (21/21 probes), idle survival `0.114583` | held-out long-horizon behavior tests | manual readability calibration |
| Multigeneration lineage runner | 9 generation records, 9 continued children, max generation 4, no orphaned branches | persistent multigeneration lineage graph | profile-weighted evolution |
| Readability calibration gate | 21-sample packet, 63 reviewer rows expected, 0 collected; mean proxy score `0.835645` | reviewer packet + proxy snapshot | manual readability calibration itself |
| Runtime boundary gate | 5/5 contracts with source evidence; 5/5 negative probes rejected; package root absent | runtime boundary contracts as package-handoff layer | package scaffold, runtime JSON Schema validation |

Reports:
`research/experiment_reports/2026-05-13-slip-runtime-selection-policy.md`,
`research/experiment_reports/2026-05-13-slip-offspring-lineage-gate.md`,
`research/experiment_reports/2026-05-13-slip-long-horizon-behavior-gate.md`,
`research/experiment_reports/2026-05-13-slip-multigeneration-lineage-runner.md`,
`research/experiment_reports/2026-05-13-slip-readability-calibration-gate.md`,
`research/experiment_reports/2026-05-13-mecha-engine-runtime-boundary-gate.md`.

These gates deliberately stop short of profile-weighted evolution. The
selected elites are existing candidate parents, the corpus is lab-generated,
and every report keeps `profile_weighted_evolution`,
`package_runtime_lifecycle_integration`, and `manual_readability_calibration`
blocked.

### 2. Third-Party Project Boundary and Native Metadata (2026-05-13, 3 reports)

| Proof | Evidence Anchor | Boundary |
| --- | ---: | --- |
| Project decoder boundary | 3/3 Piskel/`.pxo`/Aseprite-header decodes; 3/3 sidecar restores; 3/3 invalid probes rejected | container/header decoding only, not full editor semantics |
| Native metadata writer | 6/6 Piskel/Pixelorama native metadata round trips; 4/4 invalid probes rejected | JSON-friendly carriers only; Aseprite routed to the User Data chunk lab |
| Editor rewrite preservation | 6/6 simulated rewrite round trips; visual hash preservation `1.0` | deterministic rewrite simulation only, not live editor open-save |

Reports:
`research/experiment_reports/2026-05-13-third-party-project-decoder-boundary.md`,
`research/experiment_reports/2026-05-13-project-native-metadata-writer.md`,
`research/experiment_reports/2026-05-13-project-editor-rewrite-preservation.md`.

`live_external_editor_rewrite_validation` and `full_project_format_coverage`
remain blocked because no live editor open-save fixtures exist.

### 3. Spritesheet Layout, Packing, and Atlas Family (4 reports)

| Proof | Evidence Anchor |
| --- | ---: |
| Layout variant decoder | 12/12 vertical/matrix/padded/sparse round trips; semantic fidelity `1.0` |
| Packed runtime decoder | 3/3 trim/rotation round trips; deterministic playback sampling fidelity `1.0` |
| Arbitrary atlas packer | 6/6 atlas round trips over 2 packing policies; mean occupancy `0.682598`; best policy `maxrects_best_short_side_fit` |
| Multi-page atlas | 3/3 bundle round trips; mean 3.0 pages / 7.0 frames; page-switch playback proven |

Reports:
`research/experiment_reports/2026-05-13-spritesheet-layout-variant-decoder.md`,
`research/experiment_reports/2026-05-13-spritesheet-packed-runtime-decoder.md`,
`research/experiment_reports/2026-05-14-spritesheet-arbitrary-atlas-packer.md`,
`research/experiment_reports/2026-05-14-spritesheet-multi-page-atlas.md`.

Editor-authored atlas fixtures and production renderer playback remain
blocked; the runtime proof is a deterministic sidecar playback model only.

### 4. PNG Conformance Family (8 reports)

| Proof | Evidence Anchor |
| --- | ---: |
| Variant sidecar decoder | 15/15 round trips over color types 0/2/3/6 and filter types 0-4 |
| Embedded `tEXt` sidecar writer | 3/3 embedded round trips; canonical hash excludes the metadata chunk |
| Textual metadata policy | 12/12 `tEXt`/`zTXt`/`iTXt` round trips; non-ASCII confined to `iTXt` |
| Private chunk policy (`mgOT`) | 3/3 round trips; 7/7 invalid probes rejected; carrier stays provisional |
| Private chunk preservation matrix | 18/18 expected outcomes matched across 6 simulated editor-save scenarios |
| Adam7 interlace decoder | 3/3 round trips through all 7 reduced-image passes |
| Deep color decoder | 33/33 variant round trips; color types 0/2/3/4/6, bit depths 1/2/4/8/16 |
| Adam7/deep-color cross-product | 33/33 variant round trips; 7/7 invalid probes rejected |

Reports:
`research/experiment_reports/2026-05-13-png-variant-sidecar-decoder.md`,
`research/experiment_reports/2026-05-13-png-embedded-sidecar-writer.md`,
`research/experiment_reports/2026-05-14-png-textual-metadata-policy.md`,
`research/experiment_reports/2026-05-14-png-private-chunk-policy.md`,
`research/experiment_reports/2026-05-14-png-private-chunk-preservation-matrix.md`,
`research/experiment_reports/2026-05-14-png-adam7-interlace-decoder.md`,
`research/experiment_reports/2026-05-14-png-deep-color-sidecar-decoder.md`,
`research/experiment_reports/2026-05-14-png-adam7-deep-color-cross-product.md`.

The private chunk labs record a deliberate provisional recommendation:
`textual_or_external_sidecar_preferred_until_editor_fixtures`. The
preservation matrix exposes a carrier-selection risk: the current canonical
hash rejects even unrelated ancillary chunk appends. Final production carrier
selection stays blocked until live editor fixtures exist.

### 5. APNG Frame-Data Cross-Products (13 reports)

| Proof | Evidence Anchor |
| --- | ---: |
| APNG sidecar decoder | 3/3 two-frame full-canvas round trips; `acTL`/`fcTL`/`fdAT` sequence validation |
| Metadata carrier cross-product | 15/15 round trips across 5 textual/private carriers without pixel change |
| Partial frame playback | 12/12 cases across offsets, source/over blend, none/background/previous disposal |
| Filtered frame data | 15/15 cases across filter types 0-4 with split-`fdAT` reconstruction |
| Color-type frame data | 15/15 cases across color types 0/2/3/4/6 with PLTE/tRNS |
| Bit-depth frame data | 30/30 cases across bit depths 1/2/4/16 |
| Partial sample frame data | 15/15 non-zero-offset partial-region cases at depths 1/4/16 |
| Adam7 frame data | 18/18 interlaced APNG cases through all 7 passes |
| Partial Adam7 frame data | 18/18 non-zero-offset interlaced cases |
| Chunk-order conformance | 12/12 valid cases; 7/7 malformed order/sequence probes rejected |
| Image-data chunking | 18/18 IDAT/fdAT boundary-split cases including zero-length data fields |
| Zlib compression matrix | 18/18 cases across stored/fixed-Huffman/strategy DEFLATE variants |
| Zlib header policy | 18/18 window-header cases (CINFO 1/4/7); FDICT preset-dictionary rejection proven |

Reports:
`research/experiment_reports/2026-05-14-apng-sidecar-decoder.md`,
`research/experiment_reports/2026-05-14-apng-metadata-carrier-cross-product.md`,
`research/experiment_reports/2026-05-14-apng-partial-frame-playback.md`,
`research/experiment_reports/2026-05-14-apng-filtered-frame-data.md`,
`research/experiment_reports/2026-05-14-apng-color-type-frame-data.md`,
`research/experiment_reports/2026-05-14-apng-bit-depth-frame-data.md`,
`research/experiment_reports/2026-05-14-apng-partial-sample-frame-data.md`,
`research/experiment_reports/2026-05-14-apng-adam7-frame-data.md`,
`research/experiment_reports/2026-05-14-apng-partial-adam7-frame-data.md`,
`research/experiment_reports/2026-05-14-png-apng-chunk-order-conformance.md`,
`research/experiment_reports/2026-05-14-png-apng-image-data-chunking.md`,
`research/experiment_reports/2026-05-14-png-apng-zlib-compression-matrix.md`,
`research/experiment_reports/2026-05-14-png-apng-zlib-header-policy.md`.

Every APNG report keeps `full_apng_png_conformance` blocked. Remaining gaps
named by the reports include gamma/color-management behavior, exhaustive
bit-depth/color-type combinations in partial and Adam7 regions, ancillary
chunk policy, and live editor open-save preservation.

### 6. Aseprite/LibreSprite Chunk Semantics Family (9 reports)

| Proof | Evidence Anchor |
| --- | ---: |
| User Data chunk writer | 3/3 one-frame User Data `0x2020` round trips with cel visual-hash preservation |
| Tags/layers semantics | 3/3 round trips; 3 layers, 3 tags, layer User Data roles; 4/4 invalid probes rejected |
| Palette/slice semantics | 3/3 round trips; Palette `0x2019` colors, Slice `0x2022` organ bounds; 5/5 probes rejected |
| Linked-cel semantics | 3/3 round trips; linked-cel target resolution rate `1.0`; 5/5 probes rejected |
| Tilemap/tileset semantics | 3/3 round trips; Tileset `0x2023`, tilemap cel type 3, tile-ID restore; 5/5 probes rejected |
| Nested timeline semantics | 3/3 round trips; group hierarchy, tag User Data, all 4 loop directions; 6/6 probes rejected |
| External properties semantics | 3/3 round trips; Color Profile `0x2007`, External Files `0x2008`, property maps, Cel Extra `0x2006`; 6/6 probes rejected |
| Document variant resolution | 9/9 round trips across 8/16/32 bpp document variants; 6/6 probes rejected |
| External asset resolver matrix | 36/36 round trips across 4 resolver policies and 3 document variants; 5/5 probes rejected |

Reports:
`research/experiment_reports/2026-05-14-aseprite-user-data-chunk-writer.md`,
`research/experiment_reports/2026-05-14-aseprite-tags-layers-semantics.md`,
`research/experiment_reports/2026-05-14-aseprite-palette-slice-semantics.md`,
`research/experiment_reports/2026-05-14-aseprite-linked-cel-semantics.md`,
`research/experiment_reports/2026-05-14-aseprite-tilemap-tileset-semantics.md`,
`research/experiment_reports/2026-05-14-aseprite-nested-timeline-semantics.md`,
`research/experiment_reports/2026-05-14-aseprite-external-properties-semantics.md`,
`research/experiment_reports/2026-05-14-aseprite-document-variant-resolution.md`,
`research/experiment_reports/2026-05-14-aseprite-external-asset-resolver-matrix.md`.

All nine labs record `live_external_editor_verified: false`. Everything is a
generated deterministic carrier subset. `arbitrary_aseprite_project_schema_coverage`,
`editor_authored_aseprite_document_variants`, and
`full_project_format_coverage` remain blocked.

### 7. 2026-07-04 Code-Review Remediation (3 reports)

Driver: `docs/03-code_review/2026-07-04-code_review.md`.

| Fix | Findings | Evidence Anchor |
| --- | --- | ---: |
| SLIP dependency gate environment decoupling | H-01, M-15 (test surface) | slip_validator suite 15 tests OK after decoupling `jsonschema_available` from a pinned value; artifacts byte-stable |
| SLIP lab validator alignment | H-02, M-05, M-06, L-01 (first half) | lab and authoritative validators now agree on all 3 valid + 12 failure + 3 example profiles; grid_genome suite 48 tests OK (was 42) |
| MAP-Elites behavior-neediness descriptor fix | H-03 | neediness axis now candidate-derived; occupied niches 33 (was 29), QD score `31.619138` (was `27.773545`); `descriptor_bin_spread` diagnostic added |

Reports:
`research/experiment_reports/2026-07-04-slip-dependency-gate-env-decoupling.md`,
`research/experiment_reports/2026-07-04-slip-lab-validator-alignment.md`,
`research/experiment_reports/2026-07-04-map-elites-neediness-descriptor-fix.md`.

The remediation is in progress. Open residuals recorded by the fix reports:
the dependency manifest decision (M-15) remains an explicit open decision, the
three-validator duplication remains tracked as L-04, and the
`lifecycle_survival` and `mutation_stability` descriptor axes are degenerate
(spread 1) on the current corpus (L-12). Further remediation reports will be
consolidated in the v0.7 research report.

## Decisions

### Adopt

- The Stage 0 SLIP evolution-gate chain (runtime selection, offspring lineage,
  long-horizon behavior, multigeneration lineage) as lab-only evidence, with
  the runtime boundary gate as the current package-handoff layer.
- The sidecar-first semantic contract for every image and project carrier:
  Mechagotchi semantics come from explicit metadata, never from pixels.
- The bounded PNG/APNG conformance matrices (chunk order, image-data chunking,
  zlib compression and header policy, Adam7/deep-color cross-products) as
  structural import/export evidence.
- The Aseprite chunk-subset lab family and the external asset resolver matrix
  as generated-fixture proofs only.
- The code-review remediation pattern: gate tests assert policy rather than
  environment observations; descriptor axes must be candidate-derived; lab
  validators must be agreement-pinned against the authoritative contract.

### Watch

- PNG private chunk carrier risk: strict ancillary-change rejection under the
  current canonical hash; provisional recommendation stays
  `textual_or_external_sidecar_preferred_until_editor_fixtures`.
- Degenerate `lifecycle_survival` and `mutation_stability` descriptor axes
  (spread 1) pending a harder lifecycle probe or mutation-varying generation.
- Three-validator SLIP duplication (`slip.py`, `slip_validator.py`,
  `pydantic_contract.py`), tracked as review finding L-04.
- The dependency manifest decision (M-15 residual): authoring a manifest flips
  `dependency_manifest_present` and triggers the migration-gate revisit.

### Blocked

- Profile-weighted evolution, because manual readability calibration and
  package runtime integration do not exist.
- Manual readability calibration, because 0 of 63 reviewer rows in
  `data/readability/slip_readability_calibration_template.csv` are collected.
- Package runtime lifecycle integration and package promotion, because
  `packages/mecha_engine` does not exist and package work is not authorized.
- Live external editor rewrite validation and editor-authored fixtures, for
  Piskel, Pixelorama, Aseprite/LibreSprite, and atlas tooling alike.
- Full APNG/PNG conformance and the final PNG production carrier selection.
- Arbitrary Aseprite project schema coverage and full project-format coverage.
- Community profile packs.

## Implementation Boundary

This report does not authorize implementation by itself. The first allowed
implementation step remains the empty `packages/mecha_engine` `src`-layout
scaffold defined by the v0.4/v0.5 reports and the scaffold verification gate,
and it may be taken only when the user explicitly starts package work. The
runtime boundary gate added in this window defines the contracts that scaffold
must satisfy; it does not create the scaffold.

## Next Research Sequence

1. Complete the 2026-07-04 code-review remediation and consolidate the
   remaining remediation reports in research report v0.7.
2. Collect 63 real SLIP readability reviewer rows and rerun the calibration
   gate before changing proxy thresholds or claiming profile-weighted
   evolution.
3. Collect live external editor open-save fixtures (Piskel, Pixelorama,
   Aseprite/LibreSprite) before removing editor-preservation blockers.
4. Decide the production metadata carrier only after editor fixtures exist.
5. Make the dependency manifest decision (M-15) explicit, then rerun the
   schema-migration and pydantic contract gates.
6. Keep package scaffold creation blocked until explicitly authorized.

## Publication Status

This is an internal research publication. It consolidates the post-v0.5
experiment evidence and records that the repository is still research-only:
all closed states in this window are Stage 0 lab proofs, and all package,
calibration, live-editor, and evolution claims remain blocked.

## External References

- W3C PNG specification, Third Edition: `https://www.w3.org/TR/png-3/`
- RFC 1950, ZLIB Compressed Data Format: `https://www.rfc-editor.org/rfc/rfc1950`
- RFC 1951, DEFLATE Compressed Data Format: `https://www.rfc-editor.org/rfc/rfc1951`
- Aseprite file-format specification:
  `https://github.com/aseprite/aseprite/blob/main/docs/ase-file-specs.md`
- Piskel serializer/deserializer sources:
  `https://github.com/piskelapp/piskel/blob/master/src/js/utils/serialization/Serializer.js`
- Pixelorama project documentation: `https://pixelorama.org/concepts/project/`
- Illuminating search spaces by mapping elites: `https://arxiv.org/abs/1504.04909`
- Avida Digital Evolution Platform: `https://avida.devosoft.org/`
- JaxLife, an open-ended agentic simulator: `https://arxiv.org/abs/2409.00853`
- Comparing PCG metrics with human evaluation in Minecraft settlement
  generation: `https://arxiv.org/abs/2107.02457`
- libGDX TexturePacker documentation: `https://libgdx.com/wiki/tools/texture-packer`

---
