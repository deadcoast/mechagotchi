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

## Multi-Profile Round Trip

`multi_profile_roundtrip_stage0/` contains the native semantic JSON round-trip
benchmark across the generated Stage 0 SLIP profile corpora.

- Profiles: 3
- Candidates: 150
- Round-trip successes: 150
- Import-valid candidates: 150
- Export-valid candidates: 150
- SLIP-aligned exports: 150
- Mean semantic fidelity: 1.0

## SLIP Authoring Panel

`slip_authoring_panel_stage0/` contains the minimal Stage 0 profile-authoring
panel evidence for the current SLIP schema.

- Profiles: 3
- Valid drafts accepted: 3
- Invalid probes rejected: 3/3
- Profile authoring success rate: 1.0
- Invalid probe rejection rate: 1.0
- Decision: prototype_minimal_slip_authoring_panel

## SLIP Behavior and Mutation Preview

`slip_behavior_mutation_preview_stage0/` contains deterministic preview-gate
evidence for the current valid SLIP profiles.

- Profiles: 3
- Behavior previews: 3
- Mutation previews: 3
- Invalid probes rejected: 2/2
- Profile weight effects observed: True
- Mutation caps respected: True
- Decision: prototype_behavior_mutation_preview_gate
