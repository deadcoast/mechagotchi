# Experiment Report: Workshop Import/Export Round Trip

Date: 2026-05-12

## Objective

Continue the post-v0.1 research sequence by adding import/export round trips to
the workshop editor.

## Source Basis

The research plan recommends studying existing pixel editors without embedding
them prematurely. Piskel remains a useful browser-editor reference because it is
built with JavaScript, HTML, and CSS. Pixelorama is especially relevant to this
gate because it supports import/export formats and project metadata. LibreSprite
remains a UX reference for animation workflows, but its GPL status keeps it out
of embedded code paths.

Sources:

- https://github.com/piskelapp/piskel
- https://github.com/Orama-Interactive/Pixelorama
- https://github.com/LibreSprite/LibreSprite

## Scope

Included:

- `import_grid`
- `roundtrip_grid`
- `compare_semantic_grid_fidelity`
- `run_workshop_roundtrip_lab`
- `write_workshop_roundtrip_artifacts`
- static app import textarea, import button, and round-trip diff panel
- artifacts under `data/workshop_editor/`

Not included:

- PNG import/export
- spritesheet import/export
- GIF import/export
- third-party project file import
- file picker
- browser automation for the import button
- multi-profile round-trip corpus

Supersession note: the multi-profile round-trip corpus is now covered by
`research/experiment_reports/2026-05-12-workshop-multi-profile-roundtrip.md`,
and the minimal SLIP authoring panel is covered by
`research/experiment_reports/2026-05-12-slip-authoring-panel.md`.

## Verification

RED command:

```powershell
python -B -m unittest discover -s labs\workshop_editor -p 'test_*.py'
```

Initial result:

```txt
ImportError: cannot import name 'import_grid' from 'workshop_editor'
```

GREEN command:

```powershell
python -B -m unittest discover -s labs\workshop_editor -p 'test_*.py'
```

Result:

```txt
Ran 10 tests in 0.032s
OK
```

Lab command:

```powershell
python -B labs\workshop_editor\workshop_editor.py --output-dir data\workshop_editor --slip data\slips\valid\slip_lcd_seed.json --seed-index 0
```

## Metric Definition

Semantic fidelity compares source and exported cells after normalizing each cell
to:

- coordinate
- role
- organ
- material
- animation anchor
- lock state

Fidelity is:

```txt
1 - diff_count / source_cell_count
```

where `diff_count` includes changed, missing, and added cells.

## Results

Machine-readable report:

```json
{
  "lab_id": "workshop_roundtrip_stage0",
  "source_grid_id": "mg_seed_001",
  "slip_profile_id": "slip_lcd_seed",
  "metrics": {
    "roundtrip_success": 1,
    "semantic_fidelity": 1.0,
    "schema_error_rate": 0,
    "changed_cell_count": 0,
    "missing_cell_count": 0,
    "added_cell_count": 0,
    "import_export_fidelity": 1.0,
    "preview_accuracy": 1.0
  }
}
```

Artifacts:

- `data/workshop_editor/workshop_roundtrip_stage0_report.json`
- `data/workshop_editor/workshop_roundtrip_imported_state.json`
- `data/workshop_editor/workshop_roundtrip_export.json`
- `data/workshop_editor/workshop_app_data.js`

## Findings

The workshop can now round-trip the native semantic grid format without losing
organ roles, animation anchor state, material, lock state, or coordinates. This
supports the research plan's position that Mechagotchi should keep its own
semantic metadata instead of flattening authoring data into generic pixel
formats too early.

This is still a native JSON proof. Standard image/spritesheet formats need a
sidecar or project metadata strategy before they can preserve mutation weights,
organs, survival semantics, and SLIP constraints.

## Decision

Keep native workshop JSON round trips as `prototype`.

The round-trip corpus has now been broadened in
`research/experiment_reports/2026-05-12-workshop-multi-profile-roundtrip.md`,
and the minimal SLIP authoring panel has been added. Next workshop research
should define behavior/mutation preview gates or the external metadata sidecar
strategy before external image/project import paths.
