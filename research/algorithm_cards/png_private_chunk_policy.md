# Algorithm Card: PNG Private Chunk Policy

## Purpose

Define and test a bounded app-private PNG ancillary chunk carrier for
Mechagotchi semantic sidecars.

## Mathematical Basis

Each private-chunk PNG stores a hash-bound sidecar payload:

```txt
canonical_png_hash = sha256(PNG without Mechagotchi private metadata chunks)
sidecar_hash = sha256(canonical sidecar JSON)
private_png_hash = sha256(PNG with one mgOT private metadata chunk)
```

Decoded pixel identity is checked by comparing the private-chunk PNG and its
canonical PNG after removing the app-private chunk.

## Inputs

- Valid SLIP profile
- Generated profile-aligned grid
- Static PNG carrier from the standard image sidecar decoder
- Mechagotchi semantic sidecar JSON

## Outputs

- PNG with one `mgOT` ancillary private unsafe-to-copy metadata chunk
- Magic-prefixed UTF-8 JSON private chunk payload
- Restored semantic grid
- Invalid-probe rejection report
- Carrier-selection input matrix comparing external sidecars, textual PNG
  chunks, and private PNG chunks

## External Anchor

The W3C PNG specification anchors the policy:

- chunk type property bits are encoded through letter case;
- private chunks use a lowercase second letter;
- private chunks should not be used merely for human textual information;
- app-specific identifying data should appear at the start of private chunk
  data;
- ancillary chunks are preferred for private information that is not essential
  to display the image.

Source: <https://www.w3.org/TR/png-3/>

## Strengths

- Tests an app-native PNG carrier without overloading standard textual
  metadata chunks.
- Uses an ancillary private chunk so standard decoders can ignore it.
- Uses an uppercase fourth byte, making the chunk unsafe-to-copy because the
  metadata is bound to the canonical image bytes.
- Stores a magic prefix before the JSON payload to reduce collision risk.
- Rejects missing, duplicate, wrong type-bit, wrong magic, invalid JSON,
  canonical-hash, and sidecar-hash failures.

## Weaknesses

- Does not prove live external editor preservation.
- Does not prove Adam7, APNG, 16-bit color, or full PNG conformance.
- Does not choose a final production metadata carrier.
- Private chunks are a weaker fit for human textual metadata than `iTXt`.
- Does not create package runtime code.

## Failure Modes

- Missing `mgOT` chunk must reject import.
- Duplicate private chunks are unsupported.
- A safe-to-copy variant of the chunk type must reject under this policy.
- Missing or mismatched magic prefix must reject import.
- Invalid JSON must reject import.
- Canonical PNG hash mismatch must reject import.
- Sidecar hash mismatch must reject import.

## Integration Risk

Medium-high.

## License Status

No external code selected. The W3C PNG specification is used as the format
anchor.

## Prototype Result

Stage 0 PNG private chunk policy proof completed on 2026-05-14.

```txt
profile_count: 3
private_chunk_roundtrip_success_count: 3
invalid_probe_rejected_count: 7
private_chunk_roundtrip_success_rate: 1.0
mean_semantic_fidelity: 1.0
mean_pixel_fidelity: 1.0
invalid_probe_rejection_rate: 1.0
```

## Decision

Keep as active prototype. This closes only the bounded `mgOT` private ancillary
chunk policy subset and carrier-selection input matrix. It does not close the
final production import/export carrier decision, live external editor rewrite
validation, Adam7/APNG/full PNG conformance, package runtime integration,
manual readability calibration, or profile-weighted evolution.

## Go/No-Go Gate

Promote only after real editor open-save fixtures show preservation behavior
and the production import/export policy chooses between external sidecars,
textual PNG chunks, private PNG chunks, or a hybrid.
