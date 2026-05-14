# Project Editor Rewrite Preservation

## Purpose

Test whether Stage 0 native project metadata survives deterministic editor-save
rewrite simulations for the current Piskel and Pixelorama project carriers.

## Mathematical Basis

The gate separates byte identity from visual-carrier identity:

```txt
canonical_project_hash = sha256(project after Mechagotchi metadata removal)
project_visual_hash = sha256(visual payload fields and image bytes)
sidecar_hash = sha256(canonical embedded sidecar JSON)
```

If a rewrite changes only editor-owned serialization details, the canonical
project hash may change, but the visual hash and sidecar hash must still match.
After validation, the sidecar binding is rebound to the rewritten canonical
project hash.

## Inputs

- Valid SLIP profile
- Generated profile-aligned grid
- Piskel or Pixelorama project with native Mechagotchi metadata
- Deterministic simulated editor rewrite

## Outputs

- Rewritten Piskel and Pixelorama project artifacts
- Rebound native sidecar import results
- Visual-hash preservation metrics
- Invalid-probe rejection report

## Strengths

- Proves deterministic rewrite tolerance for the current Piskel description and
  Pixelorama `data.json` metadata subset.
- Rejects missing metadata, tampered sidecar metadata, and visual-payload
  mutation before semantic restore.
- Keeps byte-level canonical hash checks strict unless the rewrite import path
  explicitly allows rebinding.

## Weaknesses

- This is a deterministic simulation, not a live Piskel or Pixelorama
  open-save capture.
- Aseprite/LibreSprite User Data Chunk writing remains unimplemented.
- Advanced tags/layers timeline variants and arbitrary project schemas remain
  outside this proof.

## Failure Modes

- Missing native metadata must reject import.
- Embedded sidecar hash mismatch must reject import.
- Visual carrier mutation must reject import even when rewrite rebinding is
  allowed.
- Treating simulated rewrite preservation as live external editor validation
  would overclaim the lab.

## Integration Risk

Medium-high.

## License Status

No external code selected. Piskel, Pixelorama, and Aseprite materials are used
as format and workflow anchors only.

## Prototype Result

Stage 0 deterministic editor rewrite preservation proof completed on
2026-05-13.

```txt
profile_count: 3
simulated_editor_format_count: 2
rewrite_roundtrip_success_count: 6
invalid_probe_rejected_count: 3
rewrite_roundtrip_success_rate: 1.0
mean_semantic_fidelity: 1.0
visual_hash_preservation_rate: 1.0
invalid_probe_rejection_rate: 1.0
live_external_editor_verified: false
```

## Decision

Keep as active prototype for deterministic Piskel/Pixelorama rewrite rebinding.
This closes only the simulated rewrite subset. It does not close live external
editor validation, Aseprite/LibreSprite User Data Chunk writing, full
project-format coverage, package runtime integration, manual readability
calibration, or profile-weighted evolution.

## Go/No-Go Gate

Promote only after collecting live external Piskel/Pixelorama open-save
fixtures and adding the Aseprite/LibreSprite User Data chunk writer with full
chunk-model tests.
