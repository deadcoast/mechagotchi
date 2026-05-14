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
- `png_embedded_sidecar_writer_stage0.json` records 3/3 embedded PNG `tEXt`
  sidecar round trips, decoded pixel preservation, and 3/3 invalid embedded
  metadata probes rejected before semantic restore.
- `spritesheet_layout_variant_decoder_stage0.json` records 12/12
  layout-variant spritesheet sidecar round trips across vertical strips,
  row-major matrix sheets, padded/guttered grids, and sparse atlas rects.
- `spritesheet_packed_runtime_decoder_stage0.json` records 3/3 packed
  trim/rotation spritesheet sidecar round trips, 3 runtime playback timelines,
  and 4/4 invalid packed/runtime probes rejected before semantic restore.
- `project_native_metadata_writer_stage0.json` records 6/6 Piskel and
  Pixelorama native project metadata round trips across the 3 current profiles,
  4/4 invalid native metadata probes rejected, and one explicit unsupported
  Aseprite/LibreSprite User Data chunk writer policy.
- `slip_runtime_selection_policy_stage0.json` records 3/3 profile-weighted
  archive elite selections from switchboard lifecycle metrics, with 2/2 invalid
  selection probes rejected before selection.
- `slip_offspring_lineage_gate_stage0.json` records 3/3 bounded offspring
  selections from runtime-selected parents, 3 lineage decisions, and 2/2
  invalid offspring probes rejected before the gate starts.
- `slip_long_horizon_behavior_gate_stage0.json` records 3/3 selected
  offspring surviving the 96-tick switchboard horizon, 18/18 held-out
  switchboard full-survival probes, 18/18 idle-neglect deaths, and 2/2 invalid
  long-horizon probes rejected before the gate starts.
- `slip_multigeneration_lineage_runner_stage0.json` records 3/3 current
  profiles persisting three-generation candidate lineages, 9/9 selected
  offspring continuing as qualified lineage frontiers, max generation 4, and
  2/2 invalid multigeneration probes rejected before the runner starts.
