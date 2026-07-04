# Foreign Fixture Conformance Corpus

Date: 2026-07-04

Status: `research_foreign_fixture_conformance_no_package_code`

## Purpose

Fix review finding L-06 from `docs/03-code_review/2026-07-04-code_review.md`:
all workshop_editor tests were self-referential — decoders were only ever fed
their own encoders' output (or tampered versions of it), so spec-valid
PNG/APNG features the lab encoders never produce were unexercised.

## What changed

1. **`labs/workshop_editor/foreign_fixture_writer.py`** — an independent
   spec-derived PNG/APNG encoder sharing no code with the lab encoders: its
   own chunk writer and CRC, its own filter 0–4 implementations, its own
   Adam7 pass extraction, its own acTL/fcTL/fdAT serialization, and an
   exact-arithmetic (Fraction) APNG playback reference model covering blend
   source/over and dispose none/background/previous. Fully deterministic.
2. **`data/foreign_fixtures/`** — 17 committed fixtures + `manifest.json`
   (features, dimensions, reference hashes, per-decoder expected outcomes) +
   README. Features the lab encoders cannot produce: multi-IDAT (even and
   ragged splits including a zero-length chunk), per-row filters 0–4,
   interleaved ancillary chunks (gAMA/pHYs/tEXt), independent Adam7 output,
   split fdAT with correct sequence numbers, non-animated default images,
   dispose background/previous, blend over, sub-canvas frame regions.
3. **`labs/workshop_editor/test_foreign_fixture_conformance.py`** — 29 tests
   sweeping every fixture × decoder pair: each outcome must be either a
   pixel-exact decode (verified against the writer's independent reference)
   or a documented typed rejection; any raw exception is a decoder bug.

## Bug found and fixed

`png_apng_filtered_frame_data.py:392` (`_validate_frame_control`) accepted
dispose_op 1/2 and blend_op 1 while its playback simulation silently ignored
disposal and blending — **wrong pixels, not a rejection** — for spec-valid
files using those ops (propagating into `png_apng_image_data_chunking`). Now
typed rejections `apng_dispose_op_unsupported` / `apng_blend_op_unsupported`
matching the module's documented source-playback-only scope, with a
regression test. Both modules' stage0 artifacts regenerate with zero diff
(their own probes never used those ops — which is exactly why only a foreign
corpus could catch this).

## Result

Conformance outcomes (all pixel-verified or typed):

- `decode_png_rgba` — multi-IDAT joiner correct (including zero-length
  chunks); ancillary chunks ignored correctly; filters 1–4 and Adam7
  rejected typed.
- `decode_png_adam7_rgba` — decodes independent Adam7 output pixel-exact,
  including mixed filters + multi-IDAT.
- `decode_apng_frames` — split-fdAT/split-IDAT decodes pixel-exact;
  everything outside its bounded scope rejects typed; no crashes.
- `decode_apng_partial_frame_playback` — dispose background/previous, blend
  over, and sub-canvas playback match the independent spec model's hashes
  exactly.
- `validate_png_apng_chunk_order` — all 17 fixtures validate.
- Manifest `known_deficiencies` is empty: no wrong-pixel behavior remains.

```powershell
python -B -m unittest discover -s labs/workshop_editor -p "test_*.py"
# Ran 296 tests - OK  (was 267; +29 conformance tests)
```

Determinism pinned by test (double-generation byte-compare); committed
corpus byte-matches regeneration.

## Decision

The self-referential-fixture limitation recorded in the decoder-hardening
report is closed for the features this corpus covers. New decoder claims
should add fixtures here rather than relying on encoder round-trips; the
`known_deficiencies` list in the manifest is the honest place for any future
wrong-pixel finding that cannot be fixed immediately. Remaining honest gap:
grayscale/deep-color foreign fixtures (current decoders under test claim
8-bit RGBA scope).

## Verification

```powershell
python -B -m unittest discover -s labs/workshop_editor -p "test_*.py"
python -B labs/workshop_editor/foreign_fixture_writer.py
python -m json.tool data/foreign_fixtures/manifest.json
```

## Sources

- `docs/03-code_review/2026-07-04-code_review.md`
- `labs/workshop_editor/foreign_fixture_writer.py`
- `labs/workshop_editor/test_foreign_fixture_conformance.py`
- `labs/workshop_editor/png_apng_filtered_frame_data.py`
- `labs/workshop_editor/png_apng_image_data_chunking.py`
- `data/foreign_fixtures/manifest.json`
- `research/experiment_reports/2026-07-04-workshop-editor-decoder-hardening.md`
