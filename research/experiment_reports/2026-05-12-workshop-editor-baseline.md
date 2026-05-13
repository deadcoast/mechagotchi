# Experiment Report: Workshop Editor Baseline

Date: 2026-05-12

## Objective

Continue the research plan by building the first minimal Mechagotchi workshop
editor and testing whether semantic authoring can export a valid grid genome
under an active SLIP profile.

## Source Basis

The research plan recommends studying existing pixel editors for workflow
patterns while building a Mechagotchi-native semantic editor. The useful
distinction is that normal sprite editors manipulate pixels, while this workshop
must manipulate body cells, sensor cells, expression cells, animation anchors,
mutation metadata, and SLIP constraints.

Sources:

- https://github.com/piskelapp/piskel
- https://github.com/Orama-Interactive/Pixelorama
- https://github.com/LibreSprite/LibreSprite

## Scope

Included:

- `labs/workshop_editor/workshop_editor.py`
- `labs/workshop_editor/index.html`
- `labs/workshop_editor/styles.css`
- `labs/workshop_editor/app.js`
- semantic brush toolbar: body, anchor, sensor, expression, erase
- 8x8 semantic grid surface
- cell metadata inspector
- local validator panel
- JSON export panel
- app payload and exported sample under `data/workshop_editor/`

Not included:

- image import/export
- animation timeline
- onion skinning
- layers
- palette editing
- user-authored SLIP creator UI
- round-trip file picker
- full browser automation test suite

## Verification

RED command:

```powershell
python -m unittest discover -s labs\workshop_editor -p 'test_*.py'
```

Initial result:

```txt
ModuleNotFoundError: No module named 'workshop_editor'
```

GREEN command:

```powershell
python -m unittest discover -s labs\workshop_editor -p 'test_*.py'
```

Result:

```txt
Ran 6 tests in 0.020s
OK
```

Lab command:

```powershell
python labs\workshop_editor\workshop_editor.py --output-dir data\workshop_editor --slip data\slips\valid\slip_lcd_seed.json --seed-index 0
```

## Results

Machine-readable report:

```json
{
  "lab_id": "workshop_editor_stage0",
  "source_grid_id": "mg_seed_001",
  "slip_profile_id": "slip_lcd_seed",
  "metrics": {
    "profile_creation_success": 1,
    "validator_clarity": 1,
    "schema_error_rate": 0,
    "custom_profile_survival_rate": 1
  },
  "export_validation": {
    "valid": true,
    "slip_aligned": true
  }
}
```

Export artifact:

- `data/workshop_editor/workshop_export_stage0.json`

The exported genome validates with the existing grid validator and aligns with
`slip_lcd_seed`.

## Findings

The first workshop proof supports the research plan's recommendation: build a
Mechagotchi-native semantic editor rather than embedding a general sprite
editor. The minimum viable surface is not a canvas alone; it needs semantic
brushes, metadata inspection, validator feedback, and export preview.

The static app is intentionally narrow but operational. It can be opened as a
local HTML file and uses the generated `workshop_app_data.js` payload to render
the seed grid and live export JSON.

Supersession note: the minimal SLIP authoring panel is now covered by
`research/experiment_reports/2026-05-12-slip-authoring-panel.md`.

## Decision

Keep the workshop editor direction as `prototype`.

The next workshop research step should add import/export round trips and a
minimal SLIP authoring panel before any animation timeline, layers, or external
asset workflow. Both follow-up surfaces now have Stage 0 lab evidence; behavior
and mutation previews remain open.
