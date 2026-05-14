# Algorithm Card: PNG/APNG Image Data Chunking

## Purpose

Define a bounded Stage 0 PNG/APNG image-data matrix for IDAT and fdAT chunk
boundary independence.

## Mathematical Basis

The lab treats PNG and APNG image data as compressed datastream concatenation:

```txt
png_stream = concat(IDAT_i.data)
png_raw = zlib_decompress(png_stream)
png_pixels = decode_scanlines(png_raw)

apng_frame_stream_j = concat(fdAT_jk.frame_data by sequence_number)
apng_raw_j = zlib_decompress(apng_frame_stream_j)
apng_frame_pixels_j = decode_scanlines(apng_raw_j)
output = simulate_apng_playback(apng_frame_pixels_j)
```

It validates that chunk boundaries are transport segmentation only:

```txt
concat([empty, stream]) == stream
concat([stream[0:1], stream[1:]]) == stream
concat([stream[0:1], stream[1:2], stream[2:-4], stream[-4:-2], stream[-2:]]) == stream
```

## Inputs

- Valid SLIP profile
- Generated profile-aligned grid
- Static PNG 8-bit RGBA carrier from the existing deep-color decoder path
- APNG filtered frame-data carrier from the existing APNG frame-data path
- Six bounded IDAT/fdAT chunking cases

## Outputs

- PNG/APNG image-data chunking report
- Generated PNG/APNG fixtures for each current valid profile
- IDAT data lengths, fdAT frame_data lengths, data chunk counts, pixel hashes,
  APNG display hashes, final APNG output hashes, and invalid probe results

## External Anchor

The W3C PNG Third Edition specification anchors the rules for:

- IDAT image-data chunk concatenation;
- fdAT `frame_data` concatenation in sequence-number order;
- zlib compression method 0;
- scanline filter bytes in decompressed image data;
- zero-length APNG fdAT `frame_data` fields.

Source: <https://www.w3.org/TR/png-3/>

## Strengths

- Tests a concrete PNG/APNG conformance surface not closed by previous
  color-type, bit-depth, Adam7, or partial-frame labs.
- Proves zero-length IDAT data fields and zero-length fdAT `frame_data` fields
  in bounded fixtures.
- Splits the zlib header and Adler-32 trailer across chunk boundaries.
- Reuses existing decoders so the proof isolates chunk-boundary behavior.
- Rejects nonconsecutive IDAT, corrupt IDAT/fdAT streams, missing data chunks,
  and APNG sequence gaps.

## Weaknesses

- Uses selected 8-bit RGBA static PNG and APNG filtered frame-data carriers.
- Does not broaden color-type, bit-depth, interlace, or APNG playback coverage
  beyond the source decoders.
- Does not cover gamma/color-management behavior, every ancillary chunk, or
  live editor preservation.
- Does not choose the final PNG/APNG production metadata carrier.

## Failure Modes

- Treating IDAT chunk boundaries as scanline or compression-block boundaries.
- Treating APNG fdAT chunk boundaries as frame boundaries.
- Dropping zero-length IDAT data fields before concatenation.
- Rejecting legal empty fdAT `frame_data` fields.
- Accepting nonconsecutive IDAT chunks or fdAT sequence gaps.

## Integration Risk

Medium. Image-data chunking is a low-level import/export correctness risk for
standard PNG/APNG carriers, but this proof remains a bounded lab subset.

## License Status

No external code selected. The W3C PNG specification is used as the format
anchor.

## Prototype Result

Stage 0 image-data chunking matrix completed on 2026-05-14.

```txt
profile_count: 3
case_count: 18
case_success_count: 18
invalid_probe_count: 6
invalid_probe_rejected_count: 6
png_case_count: 9
apng_case_count: 9
zero_length_data_chunk_case_count: 6
zlib_header_split_case_count: 6
adler32_split_case_count: 6
```

## Decision

Keep as a bounded PNG/APNG image-data proof. It closes only selected static PNG
IDAT and APNG fdAT chunk-boundary reconstruction, plus invalid probe rejection
for deterministic fixtures.

Full APNG/PNG conformance, live external editor validation, final carrier
selection, package runtime integration, manual readability calibration, and
profile-weighted evolution remain blocked.

## Go/No-Go Gate

Promote PNG/APNG image-data policy only after this chunking matrix is combined
with the other image-data fixtures and live editor open-save evidence.
