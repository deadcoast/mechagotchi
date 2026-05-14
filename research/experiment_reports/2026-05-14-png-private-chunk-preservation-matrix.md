# Experiment Report: PNG Private Chunk Preservation Matrix

Date: 2026-05-14

Status: `research_png_private_chunk_preservation_matrix_no_package_code`

## Question

How does the Stage 0 `mgOT` private PNG metadata carrier behave across bounded
editor-save behaviors: exact preservation, metadata stripping, ancillary-only
changes, lossless IDAT reencoding, stale unsafe-copy preservation, and
Mechagotchi-aware rebinding?

## Plan Alignment

This continues the Stage 7 workshop/editor research path in
`docs/02-research_plan.md`. It follows the private chunk policy lab and turns
the previously blocked `private chunk editor preservation matrix` item into a
bounded simulated matrix. It does not claim live external editor validation or
a final production carrier decision.

## External Anchor

Source used:

- [W3C PNG specification, Third Edition](https://www.w3.org/TR/png-3/)

The specification defines PNG editor behavior, private chunk guidance, and
safe-to-copy semantics. This lab applies those rules to deterministic fixtures
without assuming any specific external editor preserves unknown chunks.

## Method

Added `labs/workshop_editor/test_png_private_chunk_preservation_matrix.py`
first and watched it fail on the missing module. Then added
`labs/workshop_editor/png_private_chunk_preservation_matrix.py` with:

- six scenario policies;
- exact byte-preservation simulation;
- unknown-editor private chunk stripping;
- ancillary-only chunk append while preserving `mgOT`;
- lossless IDAT reencoding with stale private chunk preservation;
- lossless IDAT reencoding with private chunk stripping;
- Mechagotchi-aware canonical hash and sidecar rebinding after reencoding.

The lab imports each transformed PNG through the existing private chunk policy
decoder and records expected-vs-actual outcomes.

## Results

Machine-readable artifacts:

- `data/workshop_editor/png_private_chunk_preservation_matrix_stage0.json`
- `data/workshop_editor/png_private_chunk_preservation_matrix_stage0/png_private_chunk_preservation_matrix_stage0.json`
- `data/workshop_editor/png_private_chunk_preservation_matrix_stage0/*.png`
- `data/workshop_editor/png_private_chunk_preservation_matrix_data.js`

Summary:

| Metric | Result |
| --- | ---: |
| Current valid profiles covered | 3 |
| Scenario policies | 6 |
| Matrix results | 18 |
| Expected outcomes matched | 18 |
| Recoverable imports | 6 |
| Missing metadata outcomes | 6 |
| Stale private chunk rejections | 6 |
| Strict ancillary-change rejections | 3 |
| Recoverable semantic fidelity mean | 1.0 |
| Recoverable pixel fidelity mean | 1.0 |
| Live external editor verified | false |

Closed states:

- `png_private_chunk_editor_preservation_matrix_simulated`
- `png_private_chunk_exact_preservation_gate`
- `png_private_chunk_stale_unsafe_copy_rejection_gate`
- `png_private_chunk_metadata_loss_detection_gate`
- `png_private_chunk_mechagotchi_rebind_gate`

Blocked states:

- `live_external_editor_rewrite_validation`
- `final_png_production_carrier_selection`
- `APNG/full PNG conformance`
- `package_runtime_lifecycle_integration`
- `manual_readability_calibration`
- `profile_weighted_evolution`

## Interpretation

The private chunk path is viable only under strict conditions. Exact
preservation works. Metadata stripping fails closed. Stale unsafe-copy
preservation after critical image rewrite fails closed. A Mechagotchi-aware
rebind path can recover after lossless reencoding when pixels and semantic
overlay still match.

The most important risk exposed by the matrix is strict ancillary-change
rejection: the current `canonical_png_hash` covers the whole PNG after removing
`mgOT`, so even an unrelated ancillary chunk append invalidates the carrier.
That may be acceptable for a conservative Stage 0 proof, but it is a
carrier-selection risk and should remain visible before choosing production
metadata strategy.

## Verification

RED command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_png_private_chunk_preservation_matrix.py
```

Initial result:

```txt
ModuleNotFoundError: No module named 'png_private_chunk_preservation_matrix'
```

GREEN command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_png_private_chunk_preservation_matrix.py
```

Result:

```txt
Ran 5 tests in 0.043s
OK
```

Artifact command:

```powershell
python -B .\labs\workshop_editor\png_private_chunk_preservation_matrix.py
```

## Decision

Adopt `png_private_chunk_preservation_matrix_stage0` as the bounded simulated
private chunk preservation matrix and carrier-selection evidence.

Do not claim live external editor rewrite validation, APNG/full PNG
conformance, final PNG production carrier selection, package runtime
integration, manual readability calibration, or profile-weighted evolution.
