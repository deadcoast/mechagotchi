# Algorithm Card: PNG/APNG Zlib Header Policy

## Purpose

Define a bounded Stage 0 PNG/APNG image-data matrix for valid zlib CMF/FLG
header-window variants and preset-dictionary rejection.

## Mathematical Basis

The lab treats the zlib wrapper as a constrained header plus deflate payload:

```txt
CMF = (CINFO << 4) | CM
CM = 8
FCHECK condition: (CMF * 256 + FLG) mod 31 == 0
FDICT(valid_png_apng_stage0) == false
raw = inflate(CMF, FLG, deflate_payload, adler32)
pixels = decode_scanlines(raw)
```

The valid-case invariant is:

```txt
hash(raw_window_512) == hash(raw_window_4096) == hash(raw_window_32768)
pixel_hash(window_i) == expected_pixel_hash
```

The invalid-case invariant is:

```txt
FDICT == true -> reject before semantic restore
bad FCHECK -> reject before semantic restore
CM != 8 or CINFO > 7 -> reject before semantic restore
```

## Inputs

- Valid SLIP profile
- Generated profile-aligned grid
- Static PNG 8-bit RGBA carrier from the existing deep-color decoder path
- APNG full-canvas second-frame carrier from the existing APNG frame-data path
- Six bounded IDAT/fdAT zlib header cases

## Outputs

- PNG/APNG zlib header policy report
- Generated PNG/APNG fixtures for each current valid profile
- Zlib header summaries, compressed stream hashes, raw scanline hashes, pixel
  hashes, APNG display hashes, final APNG output hashes, and invalid probe
  results

## External Anchors

The W3C PNG Third Edition specification anchors PNG compression method 0,
IDAT image data, APNG fdAT frame-data semantics, and APNG sequence-number
validation.

Source: <https://www.w3.org/TR/png-3/>

RFC 1950 anchors zlib CMF/FLG, CM=8, CINFO window-size field, FCHECK, FDICT,
FLEVEL, and Adler-32 validation.

Source: <https://www.rfc-editor.org/rfc/rfc1950>

RFC 1951 anchors the deflate payload interpreted by zlib method 8 streams.

Source: <https://www.rfc-editor.org/rfc/rfc1951>

## Strengths

- Tests legal zlib CINFO/window variants for both static PNG IDAT and APNG
  fdAT frame-data streams.
- Closes the explicit preset-dictionary rejection gap with real FDICT streams.
- Proves malformed CMF/FLG check values are rejected by the decoder path.
- Proves unsupported zlib compression method and too-large CINFO values are
  rejected before semantic restore.
- Reuses existing PNG/APNG decoders so the proof isolates zlib header policy.

## Weaknesses

- Uses selected 8-bit RGBA static PNG and APNG full-canvas frame-data carriers.
- Covers CINFO values 1, 4, and 7 only, not every legal window header.
- Does not enumerate every FLEVEL value.
- Does not enumerate every possible DEFLATE payload graph.
- Does not cover gamma/color-management behavior, every ancillary chunk, or
  live editor preservation.
- Does not choose the final PNG/APNG production metadata carrier.

## Failure Modes

- Accepting FDICT preset-dictionary streams and attempting semantic restore.
- Accepting zlib headers whose CMF/FLG bytes fail the modulo-31 check.
- Accepting unsupported zlib compression methods.
- Accepting CINFO values above the zlib maximum.
- Treating this bounded zlib header proof as full APNG/PNG conformance.

## Integration Risk

Medium. Header-policy handling is a low-level import/export correctness risk
for standard PNG/APNG carriers, but this proof remains a bounded lab subset.

## License Status

No external code selected. The W3C PNG specification and RFC 1950/1951 are used
as format anchors.

## Prototype Result

Stage 0 zlib header policy matrix completed on 2026-05-14.

```txt
profile_count: 3
case_count: 18
case_success_count: 18
invalid_probe_count: 6
invalid_probe_rejected_count: 6
png_case_count: 9
apng_case_count: 9
zlib_cinfo_values_covered: [1, 4, 7]
fdict_false_case_count: 18
cmf_flg_check_passed_case_count: 18
```

## Decision

Keep as a bounded PNG/APNG image-data proof. It closes selected zlib header
window reconstruction, FDICT rejection, and malformed zlib-header rejection
for deterministic fixtures.

Full APNG/PNG conformance, live external editor validation, final carrier
selection, package runtime integration, manual readability calibration, and
profile-weighted evolution remain blocked.

## Go/No-Go Gate

Promote PNG/APNG image-data policy only after this zlib header-policy matrix is
combined with the other image-data fixtures and live editor open-save evidence.
