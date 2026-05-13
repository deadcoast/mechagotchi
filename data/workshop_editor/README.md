# Workshop Editor Stage 0

Minimal semantic editor artifacts for testing Mechagotchi grid authoring.

- Source grid: mg_seed_001
- SLIP profile: slip_lcd_seed
- Export valid: True
- Export SLIP aligned: True
- Decision: prototype


## Round Trip

- Round-trip success: 1
- Semantic fidelity: 1.0
- Changed cells: 0
- Missing cells: 0
- Added cells: 0

## Additional Stage 0 Evidence

- `png_variant_sidecar_decoder_stage0.json` records 15/15 PNG variant sidecar
  round trips across 3 profiles, color types 0/2/3/6, and filter types 0..4.
- `spritesheet_layout_variant_decoder_stage0.json` records 12/12
  layout-variant spritesheet sidecar round trips across vertical strips,
  row-major matrix sheets, padded/guttered grids, and sparse atlas rects.
- `slip_runtime_selection_policy_stage0.json` records 3/3 profile-weighted
  archive elite selections from switchboard lifecycle metrics, with 2/2 invalid
  selection probes rejected before selection.
