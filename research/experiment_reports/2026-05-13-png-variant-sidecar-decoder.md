# Experiment Report: PNG Variant Sidecar Decoder

Date: 2026-05-13

Status: `research_png_variant_sidecar_decoder_no_package_code`

## Question

Can Mechagotchi broaden the standard-image sidecar proof beyond static RGBA
filter-0 PNG while still preserving `SLIP` semantics through the sidecar rather
than inferring organs, mutation weights, or profile constraints from pixels?

## Plan Alignment

This continues the Stage 7 workshop/editor track in
`docs/02-research_plan.md`. The standard-image proof covered only static
non-interlaced 8-bit RGBA PNG using filter type 0. This experiment tests the
next narrower claim: explicit 8-bit, non-interlaced PNG variants across color
types and filter types. No `packages/` code was created.

## External Source Refresh

The decoder is anchored to the W3C PNG specification:
https://www.w3.org/TR/png-3/

The implementation treats PNG as a visual carrier and implements only the
subset tested here: 8-bit, compression method 0, filter method 0,
non-interlaced PNG using color types 0, 2, 3, and 6 plus scanline filter types
0 through 4. Adam7 interlace, APNG, 1/2/4/16-bit depths, grayscale-alpha, and
full PNG conformance remain outside this claim.

## Method

Added `labs/workshop_editor/png_variant_sidecar_decoder.py` with:

- `decode_png_variant`
- `export_png_variant_suite_with_sidecars`
- `import_png_variant_with_sidecar`
- `run_png_variant_sidecar_decoder_lab`
- `write_png_variant_sidecar_decoder_artifacts`

Added `labs/workshop_editor/test_png_variant_sidecar_decoder.py` first, watched
it fail on the missing module, then implemented the decoder.

The variant suite exports the first generated grid for each current valid
profile into five PNG carriers:

| Variant | Color type | Filter types |
| --- | ---: | --- |
| `rgba_filter_none` | 6 | 0 |
| `rgba_filter_cycle` | 6 | 0, 1, 2, 3, 4 |
| `rgb_truecolor_sub` | 2 | 1 |
| `grayscale_up` | 0 | 2 |
| `indexed_palette_average_paeth` | 3 | 3, 4 |

Every exported asset is bound to a Mechagotchi sidecar. Import validates PNG
signature/chunks/CRC/IDAT, unfilters scanlines, validates the sidecar binding,
validates the variant carrier hash, restores the semantic grid from sidecar
data, and checks grid validity, `SLIP` alignment, semantic fidelity, and visual
carrier fidelity.

Invalid probes cover Adam7 interlace rejection, indexed-color PNG without PLTE,
and variant carrier pixel-hash mismatch.

## Results

Machine-readable artifacts:

- `data/workshop_editor/png_variant_sidecar_decoder_stage0.json`
- `data/workshop_editor/png_variant_sidecar_decoder_stage0/png_variant_sidecar_decoder_stage0.json`
- `data/workshop_editor/png_variant_sidecar_decoder_stage0/*.png`
- `data/workshop_editor/png_variant_sidecar_decoder_stage0/*_sidecar.json`
- `data/workshop_editor/png_variant_sidecar_decoder_data.js`

Summary:

| Metric | Result |
| --- | ---: |
| Current valid profiles covered | 3 |
| Variants per profile | 5 |
| Variant round-trip successes | 15 |
| Invalid probes rejected | 3 |
| Variant round-trip success rate | 1.0 |
| Mean semantic fidelity | 1.0 |
| Mean pixel fidelity | 1.0 |
| Invalid probe rejection rate | 1.0 |

Closed states:

- `png_color_type_0_2_3_6_8bit_decoder`
- `png_filter_types_0_to_4_decoder`
- `png_plte_indexed_color_decoder`
- `png_variant_sidecar_export`
- `png_variant_sidecar_import`
- `png_variant_sidecar_semantic_restore`

Blocked states:

- `png_adam7_interlace_decoder`
- `apng_decoder`
- `png_color_type_4_grayscale_alpha_decoder`
- `png_bit_depth_1_2_4_16_decoder`
- `full_png_conformance`
- `spritesheet_packed_rotation_trim_decoder`
- `runtime_animation_playback`
- `full_project_format_coverage`
- `embedded_png_metadata_writer`
- `project_file_native_metadata_writer`
- `profile_weighted_evolution`

## Interpretation

The generic `png_variant_decoder_coverage` blocker is now too coarse and has
been replaced in current ledgers by the precise remaining PNG gaps above.

This is not a claim of full PNG conformance. It is a Stage 0 interoperability
proof for a deliberately small but broader PNG subset. The semantic contract
remains unchanged: Mechagotchi profile, organ, mutation, and lineage semantics
come from the sidecar, not from PNG pixels or PNG metadata.

Spritesheet vertical/matrix/padded/sparse layout coverage is now covered by
`research/experiment_reports/2026-05-13-spritesheet-layout-variant-decoder.md`.
Packed rotation/trim atlas handling and runtime animation playback remain
separate spritesheet gaps.

## Verification

RED command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_png_variant_sidecar_decoder.py
```

Initial result:

```txt
ModuleNotFoundError: No module named 'png_variant_sidecar_decoder'
```

GREEN command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_png_variant_sidecar_decoder.py
```

Result:

```txt
Ran 5 tests in 0.091s
OK
```

Artifact command:

```powershell
python -B .\labs\workshop_editor\png_variant_sidecar_decoder.py
```

## Decision

Adopt `png_variant_sidecar_decoder_stage0` as the Stage 0 proof for explicit
8-bit non-interlaced PNG variant sidecar import/export.

Runtime lifecycle/archive selection is now covered by
`research/experiment_reports/2026-05-13-slip-runtime-selection-policy.md`.
Next research should run held-out long-horizon behavior tests and manual
readability calibration before claiming profile-weighted evolution.
