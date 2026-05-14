# Experiment Report: APNG Sidecar Decoder

Date: 2026-05-14

Status: `research_apng_sidecar_decoder_no_package_code`

## Question

Can Mechagotchi bind a real APNG animation carrier to a semantic sidecar,
validate APNG frame control and frame hashes, and restore a SLIP-aligned grid
without claiming full APNG or PNG conformance?

## Plan Alignment

This continues the Stage 7 workshop/editor track in
`docs/02-research_plan.md`. The current compatibility matrix called for
remaining PNG work through APNG/full-conformance fixtures. This experiment
adds a bounded APNG sidecar decoder for two full-canvas 8-bit RGBA source
frames.

## External Anchor

Source used:

- [W3C PNG specification, Third Edition](https://www.w3.org/TR/png-3/)

The specification defines APNG through `acTL`, `fcTL`, and `fdAT` chunks,
including sequence numbers, frame rectangles, frame delays, disposal, and
blend operations.

## Method

Added `labs/workshop_editor/test_png_apng_sidecar_decoder.py` first and
watched it fail on the missing module. Then added
`labs/workshop_editor/png_apng_sidecar_decoder.py` with:

- `export_apng_with_sidecar`
- `decode_apng_frames`
- `import_apng_with_sidecar`
- invalid-probe helpers for missing `acTL`, bad sequence numbers, unsupported
  blend mode, frame hash mismatch, and asset hash mismatch
- `run_apng_sidecar_decoder_lab`
- `write_apng_sidecar_decoder_artifacts`

The bounded policy supports exactly two full-canvas 8-bit RGBA frames. Frame
0 is encoded with `IDAT`; frame 1 is encoded with `fdAT`. Both frames use
`APNG_BLEND_OP_SOURCE`, `APNG_DISPOSE_OP_NONE`, zero offsets, and equal canvas
dimensions.

## Results

Machine-readable artifacts:

- `data/workshop_editor/apng_sidecar_decoder_stage0.json`
- `data/workshop_editor/apng_sidecar_decoder_stage0/apng_sidecar_decoder_stage0.json`
- `data/workshop_editor/apng_sidecar_decoder_stage0/*.png`
- `data/workshop_editor/apng_sidecar_decoder_data.js`

Summary:

| Metric | Result |
| --- | ---: |
| Current valid profiles covered | 3 |
| APNG round trips | 3 |
| APNG round-trip successes | 3 |
| Invalid probes rejected | 5 |
| APNG round-trip success rate | 1.0 |
| Mean semantic fidelity | 1.0 |
| Mean frame-pixel fidelity | 1.0 |
| Invalid probe rejection rate | 1.0 |

Closed states:

- `apng_full_canvas_source_frame_decoder`
- `apng_actl_fctl_fdat_sequence_validation`
- `apng_sidecar_semantic_restore`
- `apng_frame_hash_validation`
- `apng_invalid_probe_rejection`

Blocked states:

- `full_apng_png_conformance`
- `partial_frame_blend_over_disposal_variants`
- `APNG_textual_private_metadata_carrier_cross_product`
- `live_external_editor_rewrite_validation`
- `final_png_production_carrier_selection`
- `package_runtime_lifecycle_integration`
- `manual_readability_calibration`
- `profile_weighted_evolution`

## Interpretation

The APNG carrier can be used as a bounded animation-sidecar format for the
current profile corpus. The proof is intentionally narrower than full APNG:
it validates a known-safe full-canvas source-frame policy and rejects
unsupported blend, disposal, sequence, and hash cases before semantic restore.

This closes the local `apng_decoder` gap only for a Stage 0 bounded subset.
It does not close full APNG/PNG conformance, metadata carrier cross-products,
live editor preservation, or production carrier selection.

## Verification

RED command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_png_apng_sidecar_decoder.py
```

Initial result:

```txt
ModuleNotFoundError: No module named 'png_apng_sidecar_decoder'
```

GREEN command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_png_apng_sidecar_decoder.py
```

Result:

```txt
Ran 5 tests in 0.037s
OK
```

Artifact command:

```powershell
python -B .\labs\workshop_editor\png_apng_sidecar_decoder.py
```

## Decision

Adopt `apng_sidecar_decoder_stage0` as the bounded APNG sidecar proof.

Do not claim full APNG/PNG conformance, live external editor rewrite
validation, final PNG production carrier selection, package runtime
integration, manual readability calibration, or profile-weighted evolution.
