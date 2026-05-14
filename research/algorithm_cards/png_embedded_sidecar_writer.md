# Algorithm Card: PNG Embedded Sidecar Writer

## Purpose

Embed Mechagotchi sidecar JSON inside a PNG carrier, extract it back, and use
it to restore a valid `SLIP`-aligned semantic grid.

## Mathematical Basis

The embedded file carries two byte identities:

```txt
canonical_png_hash = sha256(PNG without Mechagotchi tEXt chunk)
embedded_png_hash = sha256(PNG with Mechagotchi tEXt chunk)
sidecar_hash = sha256(canonical sidecar JSON)
```

The canonical hash avoids the impossible self-reference of hashing a PNG that
contains a sidecar whose asset binding contains that same full PNG hash.

## Inputs

- Valid SLIP profile
- Generated profile-aligned grid
- Static RGBA PNG encoder output
- Mechagotchi sidecar JSON

## Outputs

- Embedded PNG with one `mechagotchi.sidecar.v1` `tEXt` chunk
- Extracted sidecar JSON
- Canonical PNG bytes with embedded sidecar removed
- Restored semantic grid
- Invalid-probe rejection report

## Strengths

- Keeps PNG pixels and Mechagotchi metadata together for simple file transfer.
- Preserves the existing sidecar restore contract.
- Detects missing metadata, malformed metadata JSON, and canonical image hash
  mismatches.
- Does not require third-party editor code.

## Weaknesses

- Covers only PNG `tEXt` chunks and ASCII JSON payloads.
- Does not prove `iTXt`, `zTXt`, non-ASCII metadata, editor rewrite
  preservation, Adam7, APNG, or full PNG conformance.
- Does not solve editor-native project metadata writers.
- Larger sidecars make small PNG test fixtures much bigger.

## Failure Modes

- Missing embedded sidecar chunk must reject import.
- Invalid embedded JSON must reject import.
- Canonical PNG hash mismatch must reject import.
- Duplicate embedded sidecar chunks are unsupported.
- Treating this as full PNG metadata policy would overclaim the lab.

## Integration Risk

Medium.

## License Status

No external code selected. The W3C PNG specification is used as the format
anchor.

## Prototype Result

Stage 0 PNG embedded sidecar proof completed on 2026-05-13.

```txt
profile_count: 3
embedded_roundtrip_success_count: 3
invalid_probe_rejected_count: 3
embedded_roundtrip_success_rate: 1.0
mean_semantic_fidelity: 1.0
mean_pixel_fidelity: 1.0
invalid_probe_rejection_rate: 1.0
```

## Decision

Keep as active prototype. This closes the Stage 0 embedded PNG metadata writer
gap for the `tEXt` sidecar subset, but does not close full PNG conformance,
editor rewrite preservation, project-file native metadata writers, package
runtime integration, manual readability calibration, or profile-weighted
evolution.

## Go/No-Go Gate

Promote only after production import/export policy decides whether PNG
metadata should use `tEXt`, `iTXt`, private chunks, external sidecars, or a
combination, and after editor rewrite preservation is tested.
