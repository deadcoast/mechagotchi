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

- Stage 0 handles native JSON only, not PNG, spritesheet, GIF, or project files.
- Round-trip sample set is still narrow.
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

## Decision

Keep as active prototype. Native semantic JSON should remain the canonical
workshop interchange format until pixel/image formats can preserve metadata.

## Go/No-Go Gate

Do not add broad external editor interoperability until native JSON round trips
pass across held-out grids, user-authored edits, and multiple SLIP profiles.
