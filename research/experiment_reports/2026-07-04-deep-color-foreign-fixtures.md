# Deep-Color Foreign Fixtures

Date: 2026-07-04

Status: `research_deep_color_foreign_fixtures_no_package_code`

## Purpose

Close the coverage gap recorded by
`research/experiment_reports/2026-07-04-foreign-fixture-conformance.md`: the
foreign-fixture corpus had no grayscale or deep-color fixtures, leaving
`png_deep_color_sidecar_decoder`'s claimed 16-bit scope unexercised by
independently-encoded input.

## What changed

`labs/workshop_editor/foreign_fixture_writer.py` gained independent
grayscale/deep-color serialization (per-pixel byte encoding, byte-oriented
filtering at bpp 1/2/8, generalized Adam7 pass extraction, spec sample-depth
rescaling `round(v*255/65535)`). Five fixtures added (corpus 17 → 22; the
existing 17 PNGs are byte-identical):

- `gray8_multi_idat_mixed_filters` — color type 0, 8-bit, filters 0–4, 2 IDATs
- `gray16_multi_idat_mixed_filters` — 16-bit gray, filters 0–4 incl. Paeth,
  3 IDATs, samples varying in both bytes
- `rgba16_basic` — 16-bit RGBA baseline
- `rgba16_paeth_sub_multi_idat` — 16-bit RGBA, Sub/Paeth/Up/Average, 3 IDATs
  (filter bpp 8)
- `rgba16_adam7_mixed_filters_multi_idat` — 16-bit RGBA Adam7, mixed filters
  per reduced row, non-power-of-two 6×7 canvas

The manifest records per-fixture color type/bit depth and raw-sample hashes,
plus a `coverage_notes` block replacing the old gap note.

## Result

Conformance outcomes (all pixel-verified or typed; sweep now 22 fixtures ×
10 decoders, zero raw exceptions, `known_deficiencies` still empty):

- `png_deep_color_sidecar_decoder` — all four non-interlaced new fixtures
  decode pixel-exact (filter bpp 1/2/8 all exercised); Adam7 16-bit rejects
  typed `png_interlace_unsupported` per its non-interlaced scope.
- `png_adam7_deep_color_cross_product` — the Adam7 16-bit fixture decodes
  pixel-exact; non-interlaced input rejects typed.
- 8-bit-RGBA-only decoders (standard, Adam7-8bit, the APNG family, textual
  metadata) — all five fixtures reject with their documented typed families.
- `chunk_order_validator` — all five spec-valid.

```powershell
python -B -m unittest discover -s labs/workshop_editor -p "test_foreign_fixture_conformance.py"
# Ran 40 tests - OK  (was 29)
```

No decoder bugs found; no decoder modules modified.

## Decision

The grayscale/deep-color gap is closed. Remaining out-of-scope, recorded in
the manifest `coverage_notes`: indexed color (type 3) and truecolor/gray-alpha
(types 2/4) — claimed by the deep-color decoder but not yet foreign-covered —
low-bit grayscale (1/2/4), and grayscale/16-bit APNG frame data (no APNG
decoder claims beyond 8-bit RGBA).

## Verification

```powershell
python -B -m unittest discover -s labs/workshop_editor -p "test_foreign_fixture_conformance.py"
python -B labs/workshop_editor/foreign_fixture_writer.py
python -m json.tool data/foreign_fixtures/manifest.json
```

## Sources

- `research/experiment_reports/2026-07-04-foreign-fixture-conformance.md`
- `labs/workshop_editor/foreign_fixture_writer.py`
- `labs/workshop_editor/test_foreign_fixture_conformance.py`
- `labs/workshop_editor/png_deep_color_sidecar_decoder.py`
- `labs/workshop_editor/png_adam7_deep_color_cross_product.py`
- `data/foreign_fixtures/manifest.json`
