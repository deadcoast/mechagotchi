# Experiment Report: Project Native Metadata Writer

Date: 2026-05-13

Status: `research_project_native_metadata_writer_no_package_code`

## Question

Can Mechagotchi store and recover semantic sidecar metadata inside
third-party project-file metadata locations without pretending that broad
editor project semantics are solved?

## Plan Alignment

This continues the Stage 7 workshop/editor track in
`docs/02-research_plan.md`. The previous project decoder proved sidecar-bound
project container boundaries for Piskel, Pixelorama, and Aseprite/LibreSprite
headers. This experiment tests the next narrower claim: native project-file
metadata locations for formats whose current Stage 0 payloads are JSON-friendly.
No `packages/` code was created.

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

Piskel serializes and deserializes a project description string, so Stage 0 uses
a namespaced JSON envelope in `piskel.description`. Pixelorama documents `.pxo`
as a zip container whose `data.json` carries project metadata, so Stage 0 uses a
namespaced `mechagotchi_native_metadata` object there. Aseprite documents User
Data Chunk `0x2020`; that route is handled by the separate Stage 0
Aseprite/LibreSprite User Data Chunk writer lab, while this lab remains scoped
to JSON-friendly Piskel and Pixelorama project containers.

## Method

Added `labs/workshop_editor/test_project_native_metadata_writer.py` first and
watched it fail on the missing module. Then added
`labs/workshop_editor/project_native_metadata_writer.py` with:

- `write_project_native_metadata`
- `extract_project_native_metadata`
- `remove_project_native_metadata`
- `import_project_with_native_metadata`
- Piskel description-envelope writer/reader
- Pixelorama `.pxo` `data.json` writer/reader
- unsupported Aseprite/LibreSprite policy result
- invalid-probe helpers
- `run_project_native_metadata_writer_lab`
- `write_project_native_metadata_writer_artifacts`

The writer embeds the full Mechagotchi sidecar JSON plus a sidecar hash, a
canonical-project hash, and a project visual hash. The canonical hash is
computed over the project file after Mechagotchi metadata removal, avoiding
self-reference. The visual hash is used by the later rewrite-preservation gate
to distinguish editor-owned serialization changes from visual carrier changes.

## Results

Machine-readable artifacts:

- `data/workshop_editor/project_native_metadata_writer_stage0.json`
- `data/workshop_editor/project_native_metadata_writer_stage0/project_native_metadata_writer_stage0.json`
- `data/workshop_editor/project_native_metadata_writer_stage0/*_native_metadata.piskel`
- `data/workshop_editor/project_native_metadata_writer_stage0/*_native_metadata.pxo`
- `data/workshop_editor/project_native_metadata_writer_stage0/*_native_sidecar.json`
- `data/workshop_editor/project_native_metadata_writer_data.js`

Summary:

| Metric | Result |
| --- | ---: |
| Current valid profiles covered | 3 |
| Native writer formats covered | 2 |
| Native metadata round trips | 6 |
| Native metadata round-trip successes | 6 |
| Unsupported native writer policies | 1 |
| Invalid probes rejected | 4 |
| Native metadata round-trip success rate | 1.0 |
| Mean semantic fidelity | 1.0 |
| Invalid probe rejection rate | 1.0 |
| Live external editor rewrite validation verified | false |

Closed states:

- `project_file_native_metadata_writer_policy`
- `piskel_description_native_metadata_writer`
- `pixelorama_data_json_native_metadata_writer`
- `project_native_metadata_sidecar_semantic_restore`
- `project_native_metadata_hash_validation`

Blocked states:

- `full_project_format_coverage`
- `live_external_editor_rewrite_validation`
- `advanced_tags_layers_timeline_schema_coverage`
- `package_runtime_lifecycle_integration`
- `manual_readability_calibration`
- `profile_weighted_evolution`
- `community_profile_packs`

## Interpretation

The Stage 0 native metadata writer policy is now proven only for Piskel and
Pixelorama project carriers. It demonstrates that Mechagotchi can preserve and
recover semantic sidecar metadata inside two project-file metadata locations
while maintaining semantic fidelity.

This is not a broad editor compatibility claim. It does not prove live editor
open-save rewrite validation, arbitrary Piskel/Pixelorama project schemas,
cross-lab Aseprite dispatch through this API, advanced tags/layers timeline
schema coverage, or full project-format coverage.

## Verification

RED command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_project_native_metadata_writer.py
```

Initial result:

```txt
ModuleNotFoundError: No module named 'project_native_metadata_writer'
```

GREEN command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_project_native_metadata_writer.py
```

Result:

```txt
Ran 5 tests in 0.067s
OK
```

Artifact command:

```powershell
python -B .\labs\workshop_editor\project_native_metadata_writer.py
```

## Decision

Adopt `project_native_metadata_writer_stage0` as the Stage 0 proof for
Piskel/Pixelorama native project-file metadata preservation.

Next workshop metadata research should collect live external editor rewrite
validation and broaden Aseprite/LibreSprite chunk/schema coverage before
removing the remaining project-format blockers.
