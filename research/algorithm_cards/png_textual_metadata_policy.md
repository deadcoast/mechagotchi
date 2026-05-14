# Algorithm Card: PNG Textual Metadata Policy

## Purpose

Define and test a bounded PNG textual metadata carrier policy for Mechagotchi
semantic sidecars across `tEXt`, `zTXt`, and `iTXt` chunks.

## Mathematical Basis

Each exported PNG variant carries the same sidecar identity:

```txt
canonical_png_hash = sha256(PNG without Mechagotchi textual metadata chunks)
sidecar_hash = sha256(canonical sidecar JSON)
variant_png_hash = sha256(PNG with one textual metadata chunk)
```

The canonical hash excludes the metadata chunk to avoid self-referential
hashing. Pixel identity is checked by decoding the variant PNG and the
canonical PNG and comparing decoded RGBA tuples.

## Inputs

- Valid SLIP profile
- Generated profile-aligned grid
- Static PNG carrier from the standard image sidecar decoder
- Mechagotchi semantic sidecar JSON

## Outputs

- One `tEXt` ASCII JSON variant
- One `zTXt` compressed ASCII JSON variant
- One uncompressed `iTXt` UTF-8 JSON variant
- One compressed `iTXt` UTF-8 JSON variant
- Import report with semantic fidelity, pixel fidelity, and invalid-probe
  rejection results

## External Anchor

The W3C PNG specification anchors the chunk structures and encoding rules:
`tEXt` and `zTXt` use Latin-1 text, `zTXt` uses compression method `0`, and
`iTXt` carries UTF-8 text with optional compression.

Source: <https://www.w3.org/TR/png-3/>

## Strengths

- Proves that the embedded sidecar design can use all three standard textual
  metadata chunk families in a bounded policy.
- Keeps `tEXt` and `zTXt` JSON ASCII-only to avoid silent Latin-1 ambiguity.
- Allows non-ASCII JSON only in `iTXt`, where UTF-8 is the defined text
  encoding.
- Rejects missing, duplicate, malformed, unsupported-compression, invalid
  UTF-8, and canonical-hash mismatch cases before semantic restore.

## Weaknesses

- Does not prove Adam7, APNG, 16-bit color, arbitrary ancillary chunks, or full
  PNG conformance.
- Does not prove live external editor open-save preservation.
- Does not decide whether production metadata should prefer textual chunks,
  private chunks, external sidecars, or a hybrid. The private chunk branch is
  separately covered by `png_private_chunk_policy`, but the final production
  carrier decision remains blocked.
- Does not create package runtime code.

## Failure Modes

- Missing Mechagotchi textual metadata chunk must reject import.
- Duplicate Mechagotchi textual metadata chunks are unsupported.
- Non-ASCII `tEXt`/`zTXt` metadata JSON must reject under this policy.
- Unsupported `zTXt` compression methods and corrupt `zTXt` streams must reject.
- Invalid `iTXt` UTF-8 must reject.
- Canonical PNG hash mismatch must reject.

## Integration Risk

Medium.

## License Status

No external code selected. The W3C PNG specification is used as the format
anchor.

## Prototype Result

Stage 0 PNG textual metadata policy proof completed on 2026-05-14.

```txt
profile_count: 3
textual_metadata_roundtrip_success_count: 12
invalid_probe_rejected_count: 7
textual_metadata_roundtrip_success_rate: 1.0
mean_semantic_fidelity: 1.0
mean_pixel_fidelity: 1.0
invalid_probe_rejection_rate: 1.0
```

## Decision

Keep as active prototype. This closes the bounded Stage 0 `tEXt`/`zTXt`/`iTXt`
textual metadata policy subset, but does not close live external editor rewrite
validation, Adam7/APNG/full PNG conformance, arbitrary project-format coverage,
package runtime integration, manual readability calibration, or
profile-weighted evolution.

## Go/No-Go Gate

Promote only after production import/export policy chooses the metadata carrier
strategy and after real editor open-save fixtures verify preservation behavior.
