# Algorithm Card: PNG/APNG Zlib Compression Matrix

## Purpose

Define a bounded Stage 0 PNG/APNG image-data matrix for valid zlib-wrapped
DEFLATE variants in static PNG IDAT and APNG fdAT streams.

## Mathematical Basis

The lab treats PNG and APNG image data as zlib-compressed scanline streams:

```txt
raw = filtered_scanlines(pixels)
stream_variant_k = zlib_deflate(raw, strategy_k)
pixels_k = decode_scanlines(zlib_inflate(stream_variant_k))
```

For APNG second-frame data:

```txt
frame_stream_j = concat(fdAT_jk.frame_data by sequence_number)
frame_raw_j = zlib_inflate(frame_stream_j)
frame_pixels_j = decode_scanlines(frame_raw_j)
output = simulate_apng_playback(frame_pixels_j)
```

The invariant under test is:

```txt
hash(zlib_inflate(stream_variant_a)) == hash(zlib_inflate(stream_variant_b))
pixel_hash(decode(stream_variant_a)) == pixel_hash(decode(stream_variant_b))
```

## Inputs

- Valid SLIP profile
- Generated profile-aligned grid
- Static PNG 8-bit RGBA carrier from the existing deep-color decoder path
- APNG full-canvas second-frame carrier from the existing APNG frame-data path
- Six bounded IDAT/fdAT zlib compression cases

## Outputs

- PNG/APNG zlib compression report
- Generated PNG/APNG fixtures for each current valid profile
- Zlib header summaries, compressed stream hashes, raw scanline hashes, pixel
  hashes, APNG display hashes, final APNG output hashes, and invalid probe
  results

## External Anchors

The W3C PNG Third Edition specification anchors PNG compression method 0,
IDAT image data, APNG fdAT frame-data semantics, and APNG sequence-number
validation.

Source: <https://www.w3.org/TR/png-3/>

RFC 1950 anchors zlib stream structure, CM=8 deflate, FDICT, FLEVEL, and
Adler-32 validation.

Source: <https://www.rfc-editor.org/rfc/rfc1950>

RFC 1951 anchors stored, fixed-Huffman, dynamic-Huffman, and reserved DEFLATE
block types.

Source: <https://www.rfc-editor.org/rfc/rfc1951>

## Strengths

- Tests a concrete zlib/DEFLATE image-data surface not closed by previous
  color-type, bit-depth, Adam7, partial-frame, or chunking labs.
- Proves selected valid zlib streams with different compressor configurations
  preserve raw scanlines and decoded pixels.
- Covers both static PNG IDAT and APNG fdAT frame-data reconstruction.
- Records zlib CMF/FLG metadata and confirms CM=8 method use for all valid
  cases.
- Rejects unsupported PNG compression method, broken zlib header/trailer,
  truncated image data, and APNG sequence gaps.

## Weaknesses

- Uses selected 8-bit RGBA static PNG and APNG full-canvas frame-data carriers.
- Records compressor strategy used to create the stream; PNG decoders are not
  expected to recover the encoder strategy.
- Does not enumerate every possible DEFLATE block graph.
- Does not cover preset-dictionary rejection beyond the existing zlib decoder
  behavior.
- Does not cover gamma/color-management behavior, every ancillary chunk, or
  live editor preservation.
- Does not choose the final PNG/APNG production metadata carrier.

## Failure Modes

- Treating PNG IHDR compression method values other than 0 as supported.
- Accepting zlib streams with invalid CMF/FLG or Adler-32 values.
- Coupling decoder correctness to one encoder compression level or strategy.
- Treating APNG fdAT sequence errors as recoverable in the import path.
- Claiming full APNG/PNG conformance from selected zlib method-0 fixtures.

## Integration Risk

Medium. Zlib/DEFLATE handling is a low-level import/export correctness risk for
standard PNG/APNG carriers, but this proof remains a bounded lab subset.

## License Status

No external code selected. The W3C PNG specification and RFC 1950/1951 are used
as format anchors.

## Prototype Result

Stage 0 zlib compression matrix completed on 2026-05-14.

```txt
profile_count: 3
case_count: 18
case_success_count: 18
invalid_probe_count: 6
invalid_probe_rejected_count: 6
png_case_count: 9
apng_case_count: 9
ihdr_compression_method_0_count: 18
zlib_cm8_case_count: 18
split_fdat_case_count: 9
```

## Decision

Keep as a bounded PNG/APNG image-data proof. It closes only selected zlib
method-0/DEFLATE reconstruction and invalid probe rejection for deterministic
fixtures.

Full APNG/PNG conformance, live external editor validation, final carrier
selection, package runtime integration, manual readability calibration, and
profile-weighted evolution remain blocked.

## Go/No-Go Gate

Promote PNG/APNG image-data policy only after this zlib matrix is combined with
the other image-data fixtures and live editor open-save evidence.
