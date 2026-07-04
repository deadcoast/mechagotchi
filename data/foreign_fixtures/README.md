# Foreign Fixture Corpus

Spec-derived PNG/APNG conformance fixtures for the workshop_editor
decoders. Every file is generated in-repo by
`labs/workshop_editor/foreign_fixture_writer.py`, an independent
encoder written directly from the W3C PNG specification, Third
Edition (https://www.w3.org/TR/png-3/), including the APNG chapter. The corpus is
license-clean: it contains no third-party image data, only
deterministic synthetic pixel patterns.

The writer deliberately shares no code with the lab encoders so
encoder bugs cannot cancel decoder bugs. Features covered:
multi-IDAT streams split at arbitrary byte boundaries (including a
zero-length IDAT chunk), scanline filters 0-4 (uniform and mixed
per row), interleaved ancillary chunks (gAMA, pHYs, tEXt) at legal
positions, Adam7 interlace from an independent pass extraction,
APNG dispose ops none/background/previous, blend op over,
sub-canvas frame regions, a default image excluded from the
animation, and fdAT payloads split across chunks with consecutive
sequence numbers.

Grayscale and deep-color coverage: 8-bit grayscale (color type 0),
16-bit grayscale, and 16-bit RGBA fixtures, including 16-bit
multi-IDAT streams with non-zero filters (byte-oriented filtering
with bpp 2 for gray16 and bpp 8 for rgba16) and one 16-bit RGBA
Adam7 fixture for the Adam7/deep-color cross-product decoder.
16-bit references record the specification's sample-depth
rescaling to RGBA8 (round(sample * 255 / 65535)) plus a hash of
the raw big-endian samples. Still out of scope (see the manifest
coverage_notes): indexed color type 3, truecolor color type 2,
grayscale-alpha color type 4, low-bit grayscale (1/2/4), and
grayscale/16-bit APNG frame data (no APNG decoder in the sweep
claims frame data beyond 8-bit RGBA).

`manifest.json` describes every fixture: features, dimensions,
frame count, reference pixel hashes computed by the writer's own
reference model, and the expected outcome (decode or typed
rejection family) per workshop decoder.

Regenerate with:

```
python labs/workshop_editor/foreign_fixture_writer.py
```

- Fixtures: 22
- Corpus id: foreign_fixture_corpus_v1
