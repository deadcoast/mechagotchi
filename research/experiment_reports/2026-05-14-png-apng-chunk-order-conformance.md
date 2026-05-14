# Experiment Report: PNG/APNG Chunk Order Conformance

Date: 2026-05-14

Status: `research_png_apng_chunk_order_conformance_no_package_code`

## Question

Can the workshop PNG/APNG import path reject malformed chunk ordering and
APNG sequence-number structures before any broader full-conformance or
production-carrier claim?

## Plan Alignment

This continues the Stage 7 workshop/editor research path in
`docs/02-research_plan.md` and the active SLIP compatibility blocker for full
APNG/PNG conformance. It narrows the next repo-local proof to structural
chunk-order fixtures because live editor open-save validation and human
readability rows require external inputs.

## External Anchor

Source used:

- [W3C PNG specification, Third Edition](https://www.w3.org/TR/png-3/)

The specification defines the PNG signature, chunk layout, required critical
chunk ordering, PLTE/tRNS placement, IDAT consecutiveness, APNG control chunks,
and APNG sequence numbers. This lab implements deterministic fixtures against
those format rules.

## Method

Added `labs/workshop_editor/test_png_apng_chunk_order_conformance.py` first
and confirmed the missing-module RED failure. Then added
`labs/workshop_editor/png_apng_chunk_order_conformance.py` with:

- static RGBA single-IDAT PNG conformance case;
- static RGBA split-IDAT PNG conformance case;
- indexed-color PLTE/tRNS PNG conformance case;
- APNG static-first-frame conformance case;
- invalid duplicate-IHDR, post-IEND, PLTE-after-IDAT, tRNS-before-PLTE,
  nonconsecutive-IDAT, acTL-after-IDAT, and fcTL sequence-gap probes.

The lab records conformance summaries and generated PNG/APNG fixture files for
the three current valid SLIP profiles.

## Results

Machine-readable artifacts:

- `data/workshop_editor/png_apng_chunk_order_conformance_stage0.json`
- `data/workshop_editor/png_apng_chunk_order_conformance_stage0/png_apng_chunk_order_conformance_stage0.json`
- `data/workshop_editor/png_apng_chunk_order_conformance_stage0/cases/*.png`
- `data/workshop_editor/png_apng_chunk_order_conformance_data.js`

Summary:

| Metric | Result |
| --- | ---: |
| Current valid profiles covered | 3 |
| Valid conformance case families | 4 |
| Conformance cases | 12 |
| Conformance successes | 12 |
| Invalid probes | 7 |
| Invalid probes rejected | 7 |
| Conformance success rate | 1.0 |
| Invalid rejection rate | 1.0 |

Closed states:

- `png_critical_chunk_order_matrix`
- `png_palette_transparency_order_matrix`
- `png_consecutive_idat_matrix`
- `apng_control_chunk_order_matrix`
- `apng_sequence_number_matrix`

Blocked states:

- `full_apng_png_conformance`
- `live_external_editor_rewrite_validation`
- `production_import_export_carrier_selection_final_decision`
- `manual_readability_calibration`
- `package_runtime_lifecycle_integration`

## Interpretation

The new matrix improves APNG/PNG structural evidence without overclaiming. It
proves the current generated carriers can satisfy and enforce required chunk
ordering across static RGBA, indexed PLTE/tRNS, split-IDAT, and APNG
static-first-frame cases. It also fails closed on representative malformed
orders and APNG sequence gaps.

This still is not full APNG/PNG conformance. Remaining proof needs image-data
edge cases beyond the bounded current corpus, live external editor rewrite
fixtures, and a final metadata carrier decision.

## Verification

RED command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_png_apng_chunk_order_conformance.py
```

Initial result:

```txt
ModuleNotFoundError: No module named 'png_apng_chunk_order_conformance'
```

GREEN command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_png_apng_chunk_order_conformance.py
```

Result:

```txt
Ran 5 tests in 0.039s
OK
```

Artifact command:

```powershell
python -B .\labs\workshop_editor\png_apng_chunk_order_conformance.py
```

## Decision

Adopt `png_apng_chunk_order_conformance_stage0` as the bounded structural
chunk-order conformance proof.

Do not claim full APNG/PNG conformance, live external editor rewrite
validation, final production carrier selection, package runtime integration,
manual readability calibration, or profile-weighted evolution.
