# Algorithm Card: PNG/APNG Chunk Order Conformance

## Purpose

Define a bounded Stage 0 conformance matrix for PNG/APNG chunk ordering,
cardinality, and APNG sequence-number rules used by Mechagotchi workshop
carriers.

## Mathematical Basis

The lab treats a PNG/APNG datastream as an ordered chunk sequence:

```txt
S = [IHDR, ancillary*, IDAT+, ancillary*, IEND]
```

It validates required partial orders and cardinalities rather than visual
semantics:

```txt
IHDR index = 0
IEND index = len(S) - 1
IDAT chunks are consecutive
PLTE index < first(IDAT)
tRNS index > PLTE and index < first(IDAT)
acTL index < first(IDAT)
APNG sequence numbers = 0..n with no gaps or duplicates
```

## Inputs

- Valid SLIP profile
- Generated profile-aligned grid
- Static RGBA PNG carrier
- Split-IDAT PNG carrier
- Indexed PLTE/tRNS PNG carrier
- APNG static-first-frame carrier

## Outputs

- Chunk-order conformance report
- Four valid PNG/APNG case families per profile
- Seven invalid order/cardinality probes
- Browser-readable data payload for workshop inspection

## External Anchor

The W3C PNG Third Edition specification anchors the rules for:

- PNG signature and chunk layout;
- required critical chunk order;
- PLTE, tRNS, and consecutive IDAT constraints;
- APNG acTL/fcTL/fdAT ordering and shared sequence numbers.

Source: <https://www.w3.org/TR/png-3/>

## Strengths

- Separates structural conformance from semantic sidecar restore.
- Exercises PNG critical chunk ordering across static, indexed, split-IDAT,
  and APNG carriers.
- Rejects misplaced IHDR/IEND/PLTE/tRNS/IDAT and APNG control-sequence
  violations before any production carrier claim.
- Uses generated current-profile fixtures instead of convenient one-off
  examples.

## Weaknesses

- Does not exhaust every PNG ancillary chunk, HDR chunk, interlace/deep-color
  image-data cross product, or compression edge case.
- Does not run live editor open-save preservation.
- Does not choose the final PNG/APNG production metadata carrier.
- Does not create package runtime code.

## Failure Modes

- Treating chunk-order success as full APNG/PNG conformance.
- Accepting APNG frames when `acTL`, `fcTL`, or `fdAT` sequence numbers are
  malformed.
- Allowing a nonconsecutive IDAT sequence to bypass later decoders.
- Allowing indexed transparency before the palette it depends on.

## Integration Risk

Medium. The rules are format-level gates that should sit before semantic
restore, but they do not replace full image-data decoder conformance or live
editor preservation evidence.

## License Status

No external code selected. The W3C PNG specification is used as the format
anchor.

## Prototype Result

Stage 0 chunk-order conformance matrix completed on 2026-05-14.

```txt
profile_count: 3
conformance_case_count: 12
conformance_case_success_count: 12
invalid_probe_count: 7
invalid_probe_rejected_count: 7
valid_case_family_count: 4
```

## Decision

Keep as a bounded PNG/APNG structural conformance proof. It closes only the
Stage 0 chunk-order matrix and keeps full APNG/PNG conformance, live external
editor validation, final carrier selection, package runtime integration,
manual readability calibration, and profile-weighted evolution blocked.

## Go/No-Go Gate

Promote PNG/APNG carrier policy only after this structural gate is combined
with remaining image-data conformance fixtures and live editor open-save
fixtures.
