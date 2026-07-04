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

`manifest.json` describes every fixture: features, dimensions,
frame count, reference pixel hashes computed by the writer's own
reference model, and the expected outcome (decode or typed
rejection family) per workshop decoder.

Regenerate with:

```
python labs/workshop_editor/foreign_fixture_writer.py
```

- Fixtures: 17
- Corpus id: foreign_fixture_corpus_v1
