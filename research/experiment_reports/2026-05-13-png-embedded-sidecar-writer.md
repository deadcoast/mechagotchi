# Experiment Report: PNG Embedded Sidecar Writer

Date: 2026-05-13

Status: `research_png_embedded_sidecar_writer_no_package_code`

## Question

Can Mechagotchi store and recover semantic sidecar metadata inside a PNG file
without losing decoded pixels, `SLIP` alignment, or the external sidecar
contract?

## Plan Alignment

This continues the Stage 7 workshop/editor track in
`docs/02-research_plan.md`. Prior PNG proofs used external JSON sidecars only.
This experiment tests a Stage 0 embedded PNG metadata writer/reader using a
PNG `tEXt` ancillary chunk. No `packages/` code was created.

## External Anchor

Source used:

- W3C PNG specification: https://www.w3.org/TR/png-3/

The PNG specification permits ancillary chunks and allows decoders to ignore
unknown ancillary chunks while still displaying the image. It also defines
chunk ordering and editor-copy constraints. This experiment uses a standard
`tEXt` chunk as a conservative metadata carrier and keeps Mechagotchi semantics
inside the sidecar JSON.

## Method

Added `labs/workshop_editor/test_png_embedded_sidecar_writer.py` first and
watched it fail on the missing module. Then added
`labs/workshop_editor/png_embedded_sidecar_writer.py` with:

- `export_png_with_embedded_sidecar`
- `embed_sidecar_in_png_text_chunk`
- `extract_embedded_sidecar_from_png`
- `import_png_with_embedded_sidecar`
- `remove_embedded_sidecar_chunks`
- invalid-probe helpers for missing metadata, invalid JSON, and canonical hash
  mismatch
- `run_png_embedded_sidecar_writer_lab`
- `write_png_embedded_sidecar_writer_artifacts`

The writer embeds a JSON payload under keyword
`mechagotchi.sidecar.v1`. The embedded payload stores:

- the metadata model;
- the canonical PNG hash;
- the sidecar hash;
- the Mechagotchi sidecar JSON;
- a hash note explaining that the canonical PNG hash excludes the metadata
  chunk.

The canonical-hash rule avoids self-referential hashing. The sidecar still
binds to the visual PNG without the embedded metadata chunk, while the report
also records the full embedded PNG hash.

## Results

Machine-readable artifacts:

- `data/workshop_editor/png_embedded_sidecar_writer_stage0.json`
- `data/workshop_editor/png_embedded_sidecar_writer_stage0/png_embedded_sidecar_writer_stage0.json`
- `data/workshop_editor/png_embedded_sidecar_writer_stage0/*.png`
- `data/workshop_editor/png_embedded_sidecar_writer_stage0/*_sidecar.json`
- `data/workshop_editor/png_embedded_sidecar_writer_data.js`

Summary:

| Metric | Result |
| --- | ---: |
| Current valid profiles covered | 3 |
| Embedded PNG round-trip successes | 3 |
| Invalid probes rejected | 3 |
| Embedded round-trip success rate | 1.0 |
| Mean semantic fidelity | 1.0 |
| Mean pixel fidelity | 1.0 |
| Invalid probe rejection rate | 1.0 |

Closed states:

- `embedded_png_metadata_writer_text_chunk`
- `embedded_png_metadata_reader_text_chunk`
- `embedded_png_sidecar_semantic_restore`
- `embedded_png_sidecar_hash_validation`

Blocked states:

- `Adam7/APNG/full PNG conformance`
- `project-file native metadata writer`
- `full project-format coverage`
- `arbitrary atlas packing`
- `tags/layers`
- `production renderer playback`
- `package runtime lifecycle integration`
- `manual readability calibration`
- `profile-weighted evolution`
- `community profile packs`

## Interpretation

The embedded PNG metadata writer is now proven only for the Stage 0 `tEXt`
chunk subset. It demonstrates that Mechagotchi can ship PNG pixels and semantic
sidecar metadata in the same PNG carrier while preserving decoded pixels and
semantic restore fidelity.

This is not a full PNG conformance claim. It does not cover Adam7, APNG,
`iTXt`, `zTXt`, non-ASCII metadata policy, editor rewrite preservation, or
third-party project-file native metadata.

## Verification

RED command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_png_embedded_sidecar_writer.py
```

Initial result:

```txt
ModuleNotFoundError: No module named 'png_embedded_sidecar_writer'
```

GREEN command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_png_embedded_sidecar_writer.py
```

Result:

```txt
Ran 6 tests in 0.035s
OK
```

Artifact command:

```powershell
python -B .\labs\workshop_editor\png_embedded_sidecar_writer.py
```

## Decision

Adopt `png_embedded_sidecar_writer_stage0` as the Stage 0 proof for PNG `tEXt`
chunk sidecar embedding and extraction.

Next workshop metadata research should address project-file native metadata
writers separately. Full PNG conformance and editor rewrite preservation remain
blocked until each has its own explicit test surface.
