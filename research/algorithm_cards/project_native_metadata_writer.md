# Algorithm Card: Project Native Metadata Writer

## Purpose

Embed Mechagotchi sidecar JSON into editor project-file metadata locations,
extract it back, and restore a valid `SLIP`-aligned semantic grid without a
separate external sidecar file.

## Mathematical Basis

The writer avoids self-referential hashing by validating two byte identities:

```txt
canonical_project_hash = sha256(project file after Mechagotchi metadata removal)
embedded_project_hash = sha256(project file with Mechagotchi metadata)
project_visual_hash = sha256(visual payload fields and image bytes)
sidecar_hash = sha256(canonical sidecar JSON)
```

The embedded sidecar binds to the canonical project bytes, not the bytes that
contain the embedded sidecar itself.

## Inputs

- Valid SLIP profile
- Generated profile-aligned grid
- Third-party project boundary payload
- Mechagotchi sidecar JSON

## Outputs

- Piskel project JSON with metadata in `piskel.description`
- Pixelorama `.pxo` archive with metadata in `data.json`
- Extracted sidecar JSON
- Restored semantic grid
- Project visual hash
- Invalid-probe rejection report

## Strengths

- Proves two JSON-friendly editor project carriers can keep Mechagotchi
  semantics inside the project file.
- Preserves the existing sidecar restore contract.
- Detects missing metadata, sidecar hash mismatch, canonical project hash
  mismatch, visual payload hash mismatch, and unsupported native writer
  formats.
- Does not require embedding third-party editor code.

## Weaknesses

- Piskel uses a description-field envelope, which is workable but not a rich
  native custom-properties model.
- Pixelorama coverage is limited to the `.pxo` `data.json` metadata container.
- Live external editor rewrite validation is not proven by this lab.
- Aseprite/LibreSprite User Data Chunk writing is handled by the separate
  Stage 0 User Data Chunk writer lab, not this JSON-friendly writer.
- Tags, layers, cels, animation chunks, and full project semantics remain
  outside this proof.

## Failure Modes

- Missing native metadata must reject import.
- Tampered embedded sidecar must reject import.
- Project bytes changed outside the metadata envelope must reject import.
- Visual payload changes must reject import in strict and rewrite-aware paths.
- Unsupported Aseprite/LibreSprite calls to this JSON-friendly writer must
  route to the dedicated User Data Chunk writer path if promoted.
- Treating this as full project-format coverage would overclaim the lab.

## Integration Risk

Medium-high.

## License Status

No external code selected. Piskel, Pixelorama, and Aseprite sources are used as
format and workflow anchors only.

## Prototype Result

Stage 0 project native metadata writer proof completed on 2026-05-13.

```txt
profile_count: 3
native_writer_format_count: 2
native_metadata_roundtrip_success_count: 6
unsupported_native_writer_policy_count: 1
invalid_probe_rejected_count: 4
native_metadata_roundtrip_success_rate: 1.0
mean_semantic_fidelity: 1.0
invalid_probe_rejection_rate: 1.0
live_external_editor_rewrite_validation_verified: false
```

## Decision

Keep as active prototype for the Piskel/Pixelorama native metadata subset. This
closes the Stage 0 project native metadata writer policy for JSON-friendly
project containers, but does not close cross-lab Aseprite dispatch, live
external editor rewrite validation, advanced tags/layers timeline schema
coverage, full project-format coverage, package runtime integration, manual
readability calibration, or profile-weighted evolution.

## Go/No-Go Gate

Promote only after live external editor rewrite validation is collected and the
dedicated Aseprite/LibreSprite User Data Chunk writer is integrated, if the
generic native metadata API is promoted beyond Piskel/Pixelorama.
