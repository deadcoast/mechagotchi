# Experiment Report: APNG Metadata Carrier Cross Product

Date: 2026-05-14

Status: `research_apng_metadata_carrier_cross_product_no_package_code`

## Question

Can the bounded APNG sidecar decoder round-trip semantic metadata through the
existing PNG textual and private metadata carriers without changing APNG frame
pixels or claiming full APNG/PNG conformance?

## Plan Alignment

This continues the Stage 7 workshop/editor track in
`docs/02-research_plan.md`. The compatibility matrix kept APNG metadata
carrier cross-products open after the first APNG sidecar proof. This
experiment closes only that bounded cross-product for the current generated
profile corpus.

## External Anchor

Source used:

- [W3C PNG specification, Third Edition](https://www.w3.org/TR/png-3/)

The specification anchors APNG chunk ordering, textual chunks, private chunks,
and the safe-to-copy bit policy used by the `mgOT` carrier.

## Method

Added `labs/workshop_editor/test_png_apng_metadata_carrier_cross_product.py`
first and watched it fail on the missing module. Then added
`labs/workshop_editor/png_apng_metadata_carrier_cross_product.py`.

The lab builds one canonical bounded APNG per current profile with
`png_apng_sidecar_decoder.py`, then inserts carrier metadata using the existing
PNG carrier policies:

- `tEXt` ASCII JSON
- `zTXt` compressed ASCII JSON
- uncompressed `iTXt` UTF-8 JSON
- compressed `iTXt` UTF-8 JSON
- private unsafe-to-copy `mgOT` JSON with magic prefix

Each carrier stores a canonical APNG hash, sidecar hash, and sidecar payload.
Import removes the carrier, verifies the canonical APNG hash and frame hashes,
then restores semantics through the canonical APNG sidecar decoder.

## Results

Machine-readable artifacts:

- `data/workshop_editor/apng_metadata_carrier_cross_product_stage0.json`
- `data/workshop_editor/apng_metadata_carrier_cross_product_stage0/apng_metadata_carrier_cross_product_stage0.json`
- `data/workshop_editor/apng_metadata_carrier_cross_product_stage0/*.png`
- `data/workshop_editor/apng_metadata_carrier_cross_product_data.js`

Summary:

| Metric | Result |
| --- | ---: |
| Current valid profiles covered | 3 |
| Carrier variants per profile | 5 |
| Metadata carrier round trips | 15 |
| Metadata carrier round-trip successes | 15 |
| Invalid probes rejected | 6 |
| Metadata carrier round-trip success rate | 1.0 |
| Mean semantic fidelity | 1.0 |
| Mean frame-pixel fidelity | 1.0 |
| Invalid probe rejection rate | 1.0 |

Closed states:

- `apng_textual_metadata_carrier_cross_product`
- `apng_private_metadata_carrier_cross_product`
- `apng_metadata_canonical_hash_validation`
- `apng_metadata_frame_hash_preservation`
- `apng_metadata_invalid_probe_rejection`

Blocked states:

- `full_apng_png_conformance`
- `partial_frame_blend_over_disposal_variants`
- `live_external_editor_rewrite_validation`
- `final_png_production_carrier_selection`
- `package_runtime_lifecycle_integration`
- `manual_readability_calibration`
- `profile_weighted_evolution`

## Interpretation

The APNG sidecar path now has a bounded metadata-carrier cross-product across
the current textual and private carrier policies. This does not make the APNG
decoder generally conformant: it still supports only two full-canvas 8-bit
RGBA source frames, no blend-over, no disposal variants, and no partial-frame
composition.

The result is useful as carrier evidence, not as a production carrier
decision. Live editor preservation and final carrier selection remain blocked
until editor-authored/open-save fixtures exist.

## Verification

RED command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_png_apng_metadata_carrier_cross_product.py
```

Initial result:

```txt
ModuleNotFoundError: No module named 'png_apng_metadata_carrier_cross_product'
```

GREEN command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_png_apng_metadata_carrier_cross_product.py
```

Result:

```txt
Ran 4 tests in 0.098s
OK
```

Artifact command:

```powershell
python -B .\labs\workshop_editor\png_apng_metadata_carrier_cross_product.py
```

## Decision

Adopt `apng_metadata_carrier_cross_product_stage0` as a bounded APNG carrier
proof. Do not claim full APNG/PNG conformance, live external editor rewrite
validation, final PNG production carrier selection, package runtime
integration, manual readability calibration, or profile-weighted evolution.
