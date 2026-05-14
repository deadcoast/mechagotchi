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
- Invalid-probe rejection report

## Strengths

- Proves two JSON-friendly editor project carriers can keep Mechagotchi
  semantics inside the project file.
- Preserves the existing sidecar restore contract.
- Detects missing metadata, sidecar hash mismatch, canonical project hash
  mismatch, and unsupported native writer formats.
- Does not require embedding third-party editor code.

## Weaknesses

- Piskel uses a description-field envelope, which is workable but not a rich
  native custom-properties model.
- Pixelorama coverage is limited to the `.pxo` `data.json` metadata container.
- Editor rewrite preservation is not proven.
- Aseprite/LibreSprite User Data Chunk writing is not implemented.
- Tags, layers, cels, animation chunks, and full project semantics remain
  outside this proof.

## Failure Modes

- Missing native metadata must reject import.
- Tampered embedded sidecar must reject import.
- Project bytes changed outside the metadata envelope must reject import.
- Unsupported Aseprite/LibreSprite native writer attempts must stay blocked.
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
editor_rewrite_preservation_verified: false
```

## Decision

Keep as active prototype for the Piskel/Pixelorama native metadata subset. This
closes the Stage 0 project native metadata writer policy for JSON-friendly
project containers, but does not close Aseprite/LibreSprite User Data chunk
writing, editor rewrite preservation, tags/layers native semantics, full
project-format coverage, package runtime integration, manual readability
calibration, or profile-weighted evolution.

## Go/No-Go Gate

Promote only after editor rewrite preservation is tested and the
Aseprite/LibreSprite User Data chunk writer has a full chunk-model parser and
writer test surface.
