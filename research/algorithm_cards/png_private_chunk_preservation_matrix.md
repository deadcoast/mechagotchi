# Algorithm Card: PNG Private Chunk Preservation Matrix

## Purpose

Define a deterministic editor-behavior matrix for the Stage 0 `mgOT` PNG
private chunk carrier.

## Mathematical Basis

The matrix separates byte preservation, metadata preservation, critical-image
rewrite, and Mechagotchi-aware rebinding:

```txt
canonical_png_hash = sha256(PNG without mgOT private chunks)
sidecar_hash = sha256(canonical sidecar JSON)
actual_outcome = import(private-chunk PNG after simulated editor behavior)
```

Unsafe-to-copy private chunks are valid only while the bound canonical PNG
hash remains current. If a simulated editor rewrites image data and copies the
old `mgOT` chunk unchanged, import must reject the stale metadata.

## Inputs

- Valid SLIP profile
- Generated profile-aligned grid
- `png_private_chunk_policy_stage0` carrier
- Six deterministic editor-behavior scenarios

## Outputs

- Simulated editor preservation matrix
- Rewritten PNG fixtures for each profile/scenario pair
- Expected-vs-actual outcome report
- Carrier-selection risk notes

## External Anchor

The W3C PNG specification anchors the editor and private-chunk policy:

- private chunks may be defined for app-specific data;
- ancillary chunks should be used when the data is not essential to display;
- private chunk data should begin with app-identifying information;
- safe-to-copy behavior matters when editors modify image data.

Source: <https://www.w3.org/TR/png-3/>

## Strengths

- Distinguishes exact preservation from metadata stripping.
- Rejects stale unsafe private chunks after lossless IDAT reencoding.
- Exposes the current policy's strict behavior when an editor appends unrelated
  ancillary metadata while preserving `mgOT`.
- Demonstrates a Mechagotchi-aware rebind path after lossless reencoding.
- Keeps live external editor validation explicitly out of scope.

## Weaknesses

- Uses deterministic simulations, not live Piskel, Pixelorama, Aseprite,
  LibreSprite, ImageMagick, browser-canvas, or OS preview open-save captures.
- Does not choose the final production metadata carrier.
- Does not broaden APNG/full PNG conformance.
- Does not create package runtime code.

## Failure Modes

- Unknown-editor metadata stripping loses embedded semantics.
- Unmodified stale private chunks after critical image rewrites reject import.
- Strict canonical hashing rejects ancillary-only additions, even when decoded
  pixels are unchanged.
- Treating this matrix as live editor validation would overclaim the evidence.

## Integration Risk

Medium-high.

## License Status

No external code selected. The W3C PNG specification is used as the format and
editor-behavior anchor.

## Prototype Result

Stage 0 simulated preservation matrix completed on 2026-05-14.

```txt
profile_count: 3
scenario_count: 6
matrix_result_count: 18
expected_outcome_match_count: 18
recoverable_import_count: 6
missing_metadata_count: 6
stale_private_chunk_rejection_count: 6
strict_ancillary_rejection_count: 3
recoverable_semantic_fidelity_mean: 1.0
recoverable_pixel_fidelity_mean: 1.0
live_external_editor_verified: false
```

## Decision

Keep as a carrier-selection input. This closes the simulated private-chunk
preservation matrix only. It does not close live external editor rewrite
validation, APNG/full PNG conformance, final PNG production carrier selection,
package runtime integration, manual readability calibration, or
profile-weighted evolution.

## Go/No-Go Gate

Promote the private chunk carrier only after real editor open-save fixtures
show acceptable preservation or after a Mechagotchi-aware rebind path exists in
the production import/export pipeline.
