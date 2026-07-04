# Workshop Editor Decoder Hardening

Date: 2026-07-04

Status: `research_workshop_editor_decoder_hardening_no_package_code`

## Purpose

Fix review findings H-04, H-05, and M-01 from
`docs/03-code_review/2026-07-04-code_review.md`: three systemic robustness
gaps in the `labs/workshop_editor/` decoder family, each a consequence of
per-module copies of shared binary-format helpers drifting apart.

## What changed

### H-04 — typed errors for malformed aseprite metadata JSON

Seven aseprite decoders (`tags_layers`, `tilemap_tileset`, `palette_slice`,
`linked_cel`, `nested_timeline`, `external_properties`,
`document_variant_resolution`) called `json.loads` on User Data chunk text
after only a prefix check, so a chunk carrying the Mechagotchi prefix with
malformed JSON crashed `import_*` with an untyped `json.JSONDecodeError`. Each
site now wraps the parse into the module's `AsepriteUserDataError` using its
existing `<prefix>_json_invalid` family, and each module gains a
`tamper_*_metadata_json` probe builder registered in `_invalid_probe_results`
(probe counts 4→5 / 5→6 / 6→7 per module), plus a direct unit test.

### H-05 — one shared strict PNG chunk reader

`_read_png_chunks` existed in five divergent copies. The
`png_embedded_sidecar_writer.py` variant — which `png_apng_sidecar_decoder.py`
imports — silently accepted trailing bytes after `IEND` and raised a raw
`UnicodeDecodeError` on non-ASCII chunk types. New module
`labs/workshop_editor/png_chunk_reader.py` provides `read_png_chunks`
(signature, CRC, truncation, ASCII-type, and trailing-byte enforcement,
raising `PNGChunkError(family, message)`); all five variants are now thin
wrappers that map `PNGChunkError` into their local typed families, so every
public error surface is unchanged except the two fixed defects. New negative
tests cover trailing garbage after IEND (`png_trailing_bytes`) and a
non-ASCII chunk type (`png_chunk_type_invalid`) on both the embedded-writer
and APNG paths.

Three further `_read_png_chunks` copies of a different shape remain in
`png_apng_color_type_frame_data.py`, `png_apng_filtered_frame_data.py`, and
`png_apng_partial_frame_playback.py` — tracked as review finding L-15, not
changed here.

### M-01 — bounded zlib inflation

Every decode-path `zlib.decompress` inflated fully before any size check, a
decompression-bomb surface. `png_chunk_reader.bounded_decompress(data,
max_length)` inflates through `zlib.decompressobj` with the expected output
size as a hard cap (`zlib_output_overflow` on excess, `zlib_stream_invalid`
on corrupt or truncated streams, and a guard rejecting non-positive declared
sizes because zlib treats `max_length=0` as unlimited). Nineteen decode-path
sites across the PNG, APNG frame-data, and aseprite cel decoders now use it;
text chunks (`zTXt`/`iTXt`) cap at `MAX_DECOMPRESSED_TEXT_BYTES = 1 MiB`.
Lab-internal helpers that inflate streams the lab itself just compressed were
deliberately left on plain `zlib.decompress`.

## Result

RED (before, commit `08699fb`): a prefixed-but-malformed User Data chunk
crashed seven importers with `json.JSONDecodeError`; PNGs with post-IEND
garbage were silently accepted on the embedded/APNG path; non-ASCII chunk
types raised `UnicodeDecodeError`; a small crafted IDAT/fdAT/cel stream could
inflate without bound.

GREEN (after):

```powershell
python -B -m unittest discover -s labs/workshop_editor -p "test_*.py"
# Ran 259 tests in 3.882s
# OK  (was 249 before this change)
python -B -m unittest discover -s labs/grid_genome -p "test_*.py"
# Ran 48 tests in 0.531s
# OK
```

Stage 0 artifacts regenerated for the seven aseprite modules and the seven
PNG-family modules; all changed JSON validated with `python -m json.tool`.
Artifact deltas are exactly the new rejected probes (e.g.
`invalid_probe_rejected_count` 4→5 with family
`aseprite_tags_layers_json_invalid`) and the `zlib stream invalid:` message
prefix.

## Decision

Adopt `png_chunk_reader` as the single chunk-read/inflate path for workshop
labs; new decoders must not copy a private `_read_png_chunks` or call
unbounded `zlib.decompress` on external data. The self-referential-fixture
limitation (review finding L-06) still holds: these tests exercise
tampered self-output, not foreign-produced files.

## Verification

```powershell
python -B -m unittest discover -s labs/workshop_editor -p "test_*.py"
python -B -m unittest discover -s labs/grid_genome -p "test_*.py"
python -B labs/workshop_editor/aseprite_tags_layers_semantics.py
python -m json.tool data/workshop_editor/aseprite_tags_layers_semantics_stage0.json
```

## Sources

- `docs/03-code_review/2026-07-04-code_review.md`
- `labs/workshop_editor/png_chunk_reader.py`
- `labs/workshop_editor/png_embedded_sidecar_writer.py`
- `labs/workshop_editor/png_apng_sidecar_decoder.py`
- `labs/workshop_editor/standard_image_sidecar_decoder.py`
- `labs/workshop_editor/png_adam7_interlace_decoder.py`
- `labs/workshop_editor/png_deep_color_sidecar_decoder.py`
- `labs/workshop_editor/png_variant_sidecar_decoder.py`
- `labs/workshop_editor/png_textual_metadata_policy.py`
- `labs/workshop_editor/aseprite_tags_layers_semantics.py` (and the six
  sibling aseprite semantics modules)
- `data/workshop_editor/`
