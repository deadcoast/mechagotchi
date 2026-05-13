# Experiment Report: SLIP Authoring Panel

Date: 2026-05-12

Status: `research_slip_authoring_panel_no_package_code`

## Question

Can the workshop expose a minimal SLIP profile-authoring panel that drafts
current `0.1.0` profiles against the Stage 0 schema, Pydantic contract, and
migration policy without creating package code or a dependency manifest?

## Plan Alignment

This continues Stage 6 of `docs/02-research_plan.md`: SLIP profile creator
research. The panel is intentionally narrow. It covers metadata, palette
constraints, body-mass bounds, required organ roles, mutation caps, behavior
weights, survival weights, profile JSON export, schema validation feedback, and
the current no-migration version gate.

No `packages/` implementation was created.

## External Source Refresh

The static browser panel uses standard form surfaces rather than a framework.
MDN's FormData documentation anchors the form-draft extraction path, and MDN's
HTML input documentation anchors the browser-side `required`, `pattern`,
`min`, `max`, and `step` control constraints.

Sources:

- https://developer.mozilla.org/docs/Web/API/FormData
- https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input

## Method

Added `labs/workshop_editor/slip_authoring_panel.py` with:

- `build_authoring_state`
- `apply_authoring_patch`
- `validate_authoring_draft`
- `run_slip_authoring_panel_lab`
- `write_slip_authoring_panel_artifacts`

The lab consumes the existing dependency-free validator, Pydantic contract, and
schema migration gate. It does not create a separate profile truth source.

The static workshop app now exposes a SLIP panel in:

- `labs/workshop_editor/index.html`
- `labs/workshop_editor/app.js`
- `labs/workshop_editor/styles.css`

## Results

Machine-readable artifacts:

- `data/workshop_editor/slip_authoring_panel_stage0.json`
- `data/workshop_editor/slip_authoring_panel_stage0/slip_authoring_panel_stage0.json`
- `data/workshop_editor/slip_authoring_panel_stage0/slip_lcd_seed_authoring_state.json`
- `data/workshop_editor/slip_authoring_panel_stage0/slip_gray_stable_authoring_state.json`
- `data/workshop_editor/slip_authoring_panel_stage0/slip_amber_social_authoring_state.json`
- `data/workshop_editor/slip_authoring_panel_data.js`

Summary:

| Metric | Result |
| --- | ---: |
| Current valid profiles covered | 3 |
| Valid draft patches accepted | 3 |
| Invalid probes rejected | 3 |
| Authoring success rate | 1.0 |
| Invalid probe rejection rate | 1.0 |

Invalid probes covered:

- unsupported `slip_version`;
- unknown palette;
- mutation cap outside `[0, 1]`.

## Interpretation

This closes the minimal profile-authoring panel gap for the current Stage 0
schema. It does not prove behavior preview, mutation preview UI,
profile-weighted evolution, community profile packs, runtime JSON Schema
dependency selection, or a human usability pilot.

## Verification

```powershell
python -B -m unittest discover -s labs\workshop_editor -p "test_*.py"
python -B labs\workshop_editor\slip_authoring_panel.py --output-dir data\workshop_editor\slip_authoring_panel_stage0
python -m json.tool data\workshop_editor\slip_authoring_panel_stage0.json
python -m json.tool data\workshop_editor\slip_authoring_panel_stage0\slip_authoring_panel_stage0.json
```

## Decision

Adopt `slip_authoring_panel_stage0` as the current minimal workshop-side SLIP
authoring proof. At original authoring time, the next SLIP/workshop research
was behavior and mutation preview gates or the external metadata sidecar
strategy.

Follow-up: the behavior and mutation preview gate is now recorded in
`research/experiment_reports/2026-05-12-slip-behavior-mutation-preview-gate.md`.
