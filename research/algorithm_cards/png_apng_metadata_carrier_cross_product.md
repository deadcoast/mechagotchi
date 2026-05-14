# Algorithm Card: APNG Metadata Carrier Cross Product

## Purpose

Prove that bounded APNG sidecar semantics can survive the existing
Mechagotchi PNG textual and private metadata carrier policies.

## Mathematical Basis

The carrier proof separates canonical APNG bytes from metadata-bearing APNG
bytes:

```txt
canonical_apng_hash = sha256(APNG bytes without Mechagotchi carrier chunks)
sidecar_hash = sha256(sidecar JSON)
frame_pixel_hash[i] = sha256(decoded RGBA frame i)
```

Import succeeds only if the carrier metadata hash matches the canonical APNG,
the embedded sidecar hash matches, decoded frame hashes are unchanged after
carrier removal, and the canonical APNG sidecar import restores a valid
SLIP-aligned grid.

## Inputs

- Valid SLIP profile
- Generated profile-aligned grid
- Bounded two-frame full-canvas APNG asset
- Mechagotchi semantic sidecar
- One of the existing carrier policies: `tEXt`, `zTXt`, `iTXt`,
  compressed `iTXt`, or app-private `mgOT`

## Outputs

- APNG files with textual/private metadata carriers
- Restored semantic grid
- Carrier policy manifest
- Invalid-probe rejection report

## External Anchor

The W3C PNG specification anchors APNG chunks, textual chunks, private chunk
naming, and safe-to-copy policy.

Source: <https://www.w3.org/TR/png-3/>

## Strengths

- Reuses existing PNG textual and private carrier policies instead of creating
  a second APNG-specific metadata model.
- Proves metadata-bearing APNG files preserve frame pixel hashes.
- Covers all current profiles across five carrier variants.
- Rejects missing carriers, duplicate textual carriers, corrupt compressed
  text, private canonical-hash mismatch, and APNG sequence tampering.

## Weaknesses

- Inherits the bounded APNG decoder policy: two full-canvas 8-bit RGBA source
  frames only.
- Does not test live external editor open-save preservation.
- Does not decide the final production PNG/APNG metadata carrier.
- Does not prove partial-frame APNG blend/disposal behavior or arbitrary APNGs.

## Failure Modes

- Missing textual/private carrier must reject import.
- Duplicate textual carrier must reject import.
- Corrupt `zTXt` stream must reject import.
- Private carrier canonical-hash mismatch must reject import.
- APNG sequence-number tampering must reject before semantic restore.

## Integration Risk

Medium-high.

## License Status

No external code selected. The W3C PNG specification is used as the format
anchor.

## Prototype Result

Stage 0 APNG metadata carrier cross-product proof completed on 2026-05-14.

```txt
profile_count: 3
metadata_carrier_roundtrip_success_count: 15
invalid_probe_rejected_count: 6
metadata_carrier_roundtrip_success_rate: 1.0
mean_semantic_fidelity: 1.0
mean_frame_pixel_fidelity: 1.0
invalid_probe_rejection_rate: 1.0
```

## Decision

Keep as a bounded prototype. This closes only the APNG textual/private
metadata-carrier cross-product for the current two-frame APNG policy. Full
APNG/PNG conformance, partial-frame APNG playback, live external editor
rewrite validation, final PNG production carrier selection, package runtime
integration, manual readability calibration, and profile-weighted evolution
remain blocked.

## Go/No-Go Gate

Promote only after live editor fixtures and broader APNG conformance fixtures
confirm the same carrier behavior outside this generated Stage 0 corpus.
