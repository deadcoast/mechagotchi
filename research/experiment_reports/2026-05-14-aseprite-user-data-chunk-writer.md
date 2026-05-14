# Aseprite User Data Chunk Writer

Date: 2026-05-14

Status: `research_aseprite_user_data_chunk_writer_no_package_code`

## Question

Can Mechagotchi embed and recover SLIP-aligned semantic sidecar metadata inside
an Aseprite/LibreSprite User Data Chunk without claiming full editor-native
project coverage?

## Plan Alignment

This continues the Stage 7 workshop/editor track in
`docs/02-research_plan.md`. Earlier project-file labs decoded Aseprite header
boundaries and used external sidecars, while Piskel/Pixelorama gained native
metadata and deterministic rewrite-simulation gates. This experiment addresses
the remaining executable Aseprite/LibreSprite metadata blocker by writing a
minimal binary chunk model. No `packages/` code was created.

## External Source Refresh

Sources used:

- Aseprite file-format specification:
  https://github.com/aseprite/aseprite/blob/main/docs/ase-file-specs.md
- LibreSprite GitHub:
  https://github.com/LibreSprite/LibreSprite

The Aseprite specification anchors the little-endian header, frame header,
Layer Chunk `0x2004`, Cel Chunk `0x2005`, and User Data Chunk `0x2020`. The
lab uses the format information only; it does not embed editor code.

## Method

Added `labs/workshop_editor/test_aseprite_user_data_chunk_writer.py` first and
watched it fail on the missing module. Then added
`labs/workshop_editor/aseprite_user_data_chunk_writer.py` with:

- `export_aseprite_user_data_project`
- `decode_aseprite_user_data_project`
- `extract_aseprite_user_data_sidecar`
- `import_aseprite_user_data_project`
- `strip_aseprite_user_data_chunks`
- User Data and visual-payload tamper helpers
- `run_aseprite_user_data_chunk_writer_lab`
- `write_aseprite_user_data_chunk_writer_artifacts`

The writer creates a one-frame, one-layer, 32-bit RGBA `.aseprite` carrier with
Layer Chunk `0x2004`, text User Data Chunk `0x2020`, and compressed image Cel
Chunk `0x2005`. The sidecar binds to the canonical project bytes after User
Data removal, while `cel_visual_hash` binds to the decompressed RGBA cel bytes.

## Results

Machine-readable artifacts:

- `data/workshop_editor/aseprite_user_data_chunk_writer_stage0.json`
- `data/workshop_editor/aseprite_user_data_chunk_writer_stage0/aseprite_user_data_chunk_writer_stage0.json`
- `data/workshop_editor/aseprite_user_data_chunk_writer_stage0/*_user_data.aseprite`
- `data/workshop_editor/aseprite_user_data_chunk_writer_data.js`

Summary:

| Metric | Result |
| --- | ---: |
| Current valid profiles covered | 3 |
| User Data round trips | 3 |
| User Data round-trip successes | 3 |
| Invalid probes rejected | 3 |
| User Data round-trip success rate | 1.0 |
| Mean semantic fidelity | 1.0 |
| Cel visual hash preservation rate | 1.0 |
| Invalid probe rejection rate | 1.0 |
| Live external editor verified | false |

Closed states:

- `aseprite_libresprite_user_data_chunk_writer`
- `aseprite_layer_chunk_writer_subset`
- `aseprite_compressed_rgba_cel_chunk_writer_subset`
- `aseprite_user_data_sidecar_semantic_restore`
- `aseprite_user_data_hash_validation`

Blocked states:

- `live_external_editor_rewrite_validation`
- `full_project_format_coverage`
- `advanced_tags_layers_timeline_schema_coverage`
- `arbitrary_aseprite_project_schema_coverage`
- `package_runtime_lifecycle_integration`
- `manual_readability_calibration`
- `profile_weighted_evolution`
- `community_profile_packs`

## Interpretation

The Stage 0 Aseprite/LibreSprite User Data Chunk writer subset is now proven
for the current profile corpus. It demonstrates binary chunk emission and
parsing, semantic sidecar restore, and visual-payload tamper rejection for the
one-frame compressed RGBA cel subset.

This is not full editor compatibility. It does not prove live external
Aseprite/LibreSprite open-save behavior, arbitrary project schemas, advanced
multi-layer/tag timeline variants, palette/timeline coverage, package runtime
integration, or full project-format coverage.

## Verification

RED command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_aseprite_user_data_chunk_writer.py
```

Initial result:

```txt
ModuleNotFoundError: No module named 'aseprite_user_data_chunk_writer'
```

GREEN command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_aseprite_user_data_chunk_writer.py
```

Result:

```txt
Ran 5 tests in 0.033s
OK
```

Artifact command:

```powershell
python -B .\labs\workshop_editor\aseprite_user_data_chunk_writer.py
```

## Decision

Adopt `aseprite_user_data_chunk_writer_stage0` as the Stage 0 proof for the
Aseprite/LibreSprite one-frame User Data Chunk subset only.

Next workshop metadata research should collect live external editor open-save
fixtures and broaden the chunk/schema fixture corpus before removing full
project-format blockers.
