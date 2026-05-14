# Algorithm Card: Workshop Round-Trip I/O

## Purpose

Prove that the Mechagotchi workshop can import a semantic grid genome, rebuild
editor state, export it again, and preserve semantic fidelity.

## Mathematical Basis

Lossless semantic serialization over a bounded 8x8 grid. Fidelity is measured by
normalizing source and exported cells to semantic signatures and comparing
coordinates, roles, organs, materials, animation anchors, and lock state.

## Inputs

- Valid grid genome
- Active SLIP profile
- Editor state
- Export grid id

## Outputs

- Imported editor state
- Round-trip exported grid
- Import validation
- Export validation
- SLIP alignment result
- Semantic diff
- Fidelity metrics

## Strengths

- Tests workshop interoperability without embedding third-party editor code.
- Preserves Mechagotchi-specific semantics instead of flattening to pixels.
- Produces machine-readable diff output for CI and future UI checks.
- Keeps import/export fidelity separate from visual editor polish.

## Weaknesses

- Stage 0 native round trips handle semantic JSON, and the current image path
  handles static non-interlaced 8-bit RGBA PNG, an explicit 8-bit
  non-interlaced PNG color/filter variant subset, and fixed equal-size
  horizontal spritesheet PNGs.
- External metadata sidecar strategy, static PNG sidecar decoding,
  PNG variant sidecar decoding, fixed-grid horizontal spritesheet sidecar
  decoding, layout-variant spritesheet sidecar decoding for vertical/matrix/
  padded/sparse layouts, PNG `tEXt` embedded sidecar writing, packed
  trim/rotation runtime sidecar decoding, and the project-file boundary decoder
  are proven, but arbitrary atlas packing, tags/layers, production renderer
  playback, full project-format coverage, Aseprite/LibreSprite User Data chunk
  writing, live external editor rewrite validation, and full PNG conformance are not
  implemented.
- Static UI import uses paste-and-parse rather than a file picker.
- No browser automation assertion has been added for the import button yet.

## Failure Modes

- Imported grids outside the active SLIP profile are rejected.
- Semantic fields can drift if future exporters rename roles or organs.
- Pixel-only formats would lose mutation and organ metadata unless sidecar data exists.
- Round-trip fidelity can pass while visual preview styling still needs work.

## Integration Risk

Medium.

## License Status

No external code selected.

## Prototype Result

First workshop round-trip prototype completed on 2026-05-12.

```txt
roundtrip_success: 1
semantic_fidelity: 1.0
schema_error_rate: 0
changed_cell_count: 0
missing_cell_count: 0
added_cell_count: 0
```

Follow-up generated-corpus and sidecar strategy results:

```txt
multi_profile_roundtrip_profiles: 3
multi_profile_roundtrip_candidates: 150
multi_profile_roundtrip_success: 150
multi_profile_mean_semantic_fidelity: 1.0
external_sidecar_profiles: 3
external_sidecar_roundtrip_success: 3
external_sidecar_invalid_probes_rejected: 2
external_sidecar_adapter_formats_requiring_sidecar: 5
standard_image_png_profiles: 3
standard_image_png_roundtrip_success: 3
standard_image_png_mean_semantic_fidelity: 1.0
standard_image_png_mean_pixel_fidelity: 1.0
png_variant_profiles: 3
png_variant_roundtrip_success: 15
png_variant_supported_color_types: 0, 2, 3, 6
png_variant_supported_filter_types: 0, 1, 2, 3, 4
png_variant_mean_semantic_fidelity: 1.0
png_variant_mean_pixel_fidelity: 1.0
png_embedded_sidecar_profiles: 3
png_embedded_sidecar_roundtrip_success: 3
png_embedded_sidecar_invalid_probes_rejected: 3
png_embedded_sidecar_mean_semantic_fidelity: 1.0
png_embedded_sidecar_mean_pixel_fidelity: 1.0
spritesheet_profiles: 3
spritesheet_roundtrip_success: 3
spritesheet_mean_semantic_fidelity: 1.0
spritesheet_mean_frame_pixel_fidelity: 1.0
spritesheet_layout_variant_profiles: 3
spritesheet_layout_variant_roundtrip_success: 12
spritesheet_layout_variant_mean_semantic_fidelity: 1.0
spritesheet_layout_variant_mean_frame_pixel_fidelity: 1.0
spritesheet_packed_runtime_profiles: 3
spritesheet_packed_runtime_roundtrip_success: 3
spritesheet_packed_runtime_invalid_probes_rejected: 4
spritesheet_packed_runtime_mean_semantic_fidelity: 1.0
spritesheet_packed_runtime_mean_reconstructed_frame_fidelity: 1.0
spritesheet_packed_runtime_mean_runtime_frame_fidelity: 1.0
third_party_project_profiles: 3
third_party_project_decoder_success: 3
third_party_project_sidecar_restore_success: 3
third_party_project_mean_semantic_fidelity: 1.0
```

## Decision

Keep as active prototype. Native semantic JSON remains the canonical workshop
interchange format. The external JSON sidecar strategy, static RGBA PNG
sidecar decoder, and explicit 8-bit non-interlaced PNG variant sidecar decoder
are accepted for Stage 0 metadata preservation. The PNG embedded sidecar writer
is accepted for Stage 0 `tEXt` chunk metadata preservation only. The fixed-grid
horizontal spritesheet sidecar decoder is accepted for its fixed horizontal layout, and
the layout-variant spritesheet sidecar decoder is accepted for vertical strips,
row-major matrix sheets, padded/guttered grids, and sparse atlas rects. The
packed runtime spritesheet decoder is accepted for Stage 0 sidecar-described
trim, 90-degree rotation, canonical frame reconstruction, and deterministic
playback sampling. The third-party project decoder boundary is accepted for
Piskel JSON, Pixelorama `.pxo` ZIP/data.json, and Aseprite/LibreSprite header
binding only. These are not substitutes for arbitrary atlas packing,
tags/layers, production renderer playback, full editor-native project
coverage, live external editor rewrite validation, Aseprite/LibreSprite User Data chunk
writing, or full PNG conformance.

## Go/No-Go Gate

Do not add broad external editor interoperability until arbitrary atlas
packing, tags/layers, production renderer playback, full project-format
coverage, live external editor rewrite validation, Aseprite/LibreSprite User Data chunk
writing, and remaining full-PNG-conformance questions prove they can preserve
SLIP organ, mutation, and profile metadata without depending on lossy
editor-native fields.
