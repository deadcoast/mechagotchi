# Project Editor Rewrite Preservation

Date: 2026-05-13

Status: `research_project_editor_rewrite_preservation_no_package_code`

## Question

Can the Stage 0 Piskel and Pixelorama native metadata subset survive editor-save
style project rewrites without losing Mechagotchi semantic sidecar data?

## Plan Alignment

This continues the Stage 7 workshop/editor track in
`docs/02-research_plan.md`. The prior native metadata writer proved embedded
metadata round trips for Piskel description metadata and Pixelorama `.pxo`
`data.json` metadata. This experiment narrows the next claim to deterministic
rewrite simulation and keeps live external editor validation blocked. No
`packages/` code was created.

## External Source Refresh

Sources used:

- Piskel serializer:
  https://github.com/piskelapp/piskel/blob/master/src/js/utils/serialization/Serializer.js
- Piskel deserializer:
  https://github.com/piskelapp/piskel/blob/master/src/js/utils/serialization/Deserializer.js
- Pixelorama project documentation:
  https://pixelorama.org/concepts/project/
- Aseprite file-format specification:
  https://github.com/aseprite/aseprite/blob/main/docs/ase-file-specs.md

Piskel exposes a serialized project description field, so the deterministic
rewrite simulation preserves that envelope while reserializing project and
layer JSON. Pixelorama `.pxo` uses a zip container with `data.json` and
`image_data/`, so the simulation rewrites `data.json` while preserving image
members. Aseprite/LibreSprite User Data Chunk writing remains a separate
full chunk-model target.

## Method

Added `labs/workshop_editor/test_project_editor_rewrite_preservation.py` first
and watched it fail on the missing module. Then added
`labs/workshop_editor/project_editor_rewrite_preservation.py` with:

- `simulate_editor_rewrite`
- `import_project_after_editor_rewrite`
- `tamper_project_visual_payload`
- `run_project_editor_rewrite_preservation_lab`
- `write_project_editor_rewrite_preservation_artifacts`
- deterministic Piskel and Pixelorama rewrite helpers
- missing metadata, sidecar tamper, and visual tamper invalid probes

The native metadata writer was extended with `project_visual_hash` and an
explicit rewrite import path. Strict imports still reject canonical project
hash changes. Rewrite imports allow canonical hash rebinding only when the
embedded sidecar hash and visual payload hash remain intact.

## Results

Machine-readable artifacts:

- `data/workshop_editor/project_editor_rewrite_preservation_stage0.json`
- `data/workshop_editor/project_editor_rewrite_preservation_stage0/project_editor_rewrite_preservation_stage0.json`
- `data/workshop_editor/project_editor_rewrite_preservation_stage0/*_rewritten.piskel`
- `data/workshop_editor/project_editor_rewrite_preservation_stage0/*_rewritten.pxo`
- `data/workshop_editor/project_editor_rewrite_preservation_data.js`

Summary:

| Metric | Result |
| --- | ---: |
| Current valid profiles covered | 3 |
| Simulated editor formats covered | 2 |
| Rewrite round trips | 6 |
| Rewrite round-trip successes | 6 |
| Invalid probes rejected | 3 |
| Rewrite round-trip success rate | 1.0 |
| Mean semantic fidelity | 1.0 |
| Visual hash preservation rate | 1.0 |
| Invalid probe rejection rate | 1.0 |
| Live external editor verified | false |

Closed states:

- `project_editor_rewrite_preservation_simulated`
- `piskel_description_rewrite_preservation_simulated`
- `pixelorama_data_json_rewrite_preservation_simulated`
- `project_visual_hash_preservation_gate`
- `project_rewrite_sidecar_rebind_policy`

Blocked states:

- `live_external_editor_rewrite_validation`
- `arbitrary_aseprite_project_schema_coverage`
- `full_project_format_coverage`
- `advanced_tags_layers_timeline_schema_coverage`
- `package_runtime_lifecycle_integration`
- `manual_readability_calibration`
- `profile_weighted_evolution`
- `community_profile_packs`

## Interpretation

The Stage 0 deterministic rewrite subset is proven for current Piskel and
Pixelorama payloads. The proof shows that Mechagotchi can detect editor-owned
serialization changes, preserve the visual carrier hash, and rebind the
embedded sidecar to the rewritten canonical project hash.

This is not a live editor compatibility claim. It does not prove actual
Piskel/Pixelorama open-save behavior, arbitrary project schemas,
Aseprite/LibreSprite User Data Chunk writing, advanced tags/layers timeline
schema coverage, or full project-format coverage.

## Verification

RED command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_project_editor_rewrite_preservation.py
```

Initial result:

```txt
ModuleNotFoundError: No module named 'project_editor_rewrite_preservation'
```

GREEN command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_project_editor_rewrite_preservation.py
```

Result:

```txt
Ran 5 tests in 0.066s
OK
```

Artifact command:

```powershell
python -B .\labs\workshop_editor\project_editor_rewrite_preservation.py
```

## Decision

Adopt `project_editor_rewrite_preservation_stage0` as the Stage 0 proof for
deterministic Piskel/Pixelorama rewrite rebinding only.

Next workshop metadata research should collect live external Piskel/Pixelorama
open-save fixtures and build the Aseprite/LibreSprite User Data chunk writer
before removing the remaining project-format blockers.
