# Experiment Report: PNG Textual Metadata Policy

Date: 2026-05-14

Status: `research_png_textual_metadata_policy_no_package_code`

## Question

Can Mechagotchi round-trip embedded semantic sidecar metadata through standard
PNG textual chunks beyond the previous `tEXt`-only proof, while preserving
decoded pixels, SLIP alignment, and canonical hash validation?

## Plan Alignment

This continues the Stage 7 workshop/editor track in
`docs/02-research_plan.md`. The previous embedded PNG proof covered only an
ASCII JSON `tEXt` chunk. This experiment adds a bounded policy for `tEXt`,
`zTXt`, and `iTXt` variants without creating `packages/` code.

## External Anchor

Source used:

- [W3C PNG specification, Third Edition](https://www.w3.org/TR/png-3/)

The specification defines the textual chunk structures used here: `tEXt`
stores Latin-1 text, `zTXt` stores compressed Latin-1 text with compression
method `0`, and `iTXt` stores UTF-8 text with an optional compression flag.
The lab policy therefore keeps `tEXt` and `zTXt` JSON ASCII-only and allows
non-ASCII metadata only in `iTXt`.

## Method

Added `labs/workshop_editor/test_png_textual_metadata_policy.py` first and
watched it fail on the missing module. Then added
`labs/workshop_editor/png_textual_metadata_policy.py` with:

- `export_png_textual_metadata_bundle`
- `import_png_textual_metadata`
- `remove_png_textual_metadata_chunks`
- invalid-probe helpers for missing, duplicate, non-ASCII `tEXt`, unsupported
  `zTXt` method, corrupt `zTXt` stream, invalid `iTXt` UTF-8, and canonical
  hash mismatch cases
- `run_png_textual_metadata_policy_lab`
- `write_png_textual_metadata_policy_artifacts`

The exporter produces four variants for each current valid profile:

- `text_ascii`: `tEXt`, ASCII JSON inside a Latin-1 text chunk
- `ztxt_ascii`: `zTXt`, compressed ASCII JSON with method `0`
- `itxt_utf8`: uncompressed `iTXt`, UTF-8 JSON
- `itxt_utf8_compressed`: compressed `iTXt`, UTF-8 JSON

All variants embed the same sidecar model under keyword
`mechagotchi.sidecar.v1`. The canonical PNG hash excludes the Mechagotchi
textual metadata chunk, preserving the non-self-referential asset-binding rule
from the embedded sidecar writer.

## Results

Machine-readable artifacts:

- `data/workshop_editor/png_textual_metadata_policy_stage0.json`
- `data/workshop_editor/png_textual_metadata_policy_stage0/png_textual_metadata_policy_stage0.json`
- `data/workshop_editor/png_textual_metadata_policy_stage0/*.png`
- `data/workshop_editor/png_textual_metadata_policy_data.js`

Summary:

| Metric | Result |
| --- | ---: |
| Current valid profiles covered | 3 |
| Textual metadata variant round trips | 12 |
| Textual metadata variant successes | 12 |
| Invalid probes rejected | 7 |
| Textual metadata round-trip success rate | 1.0 |
| Mean semantic fidelity | 1.0 |
| Mean pixel fidelity | 1.0 |
| Invalid probe rejection rate | 1.0 |

Closed states:

- `png_textual_metadata_text_ascii_policy`
- `png_textual_metadata_ztxt_compressed_policy`
- `png_textual_metadata_itxt_utf8_policy`
- `png_textual_metadata_hash_validation`
- `png_textual_metadata_invalid_probe_rejection`

Blocked states:

- `live_external_editor_rewrite_validation`
- `Adam7/APNG/full PNG conformance`
- `arbitrary Aseprite project schema coverage`
- `full project-format coverage`
- `package_runtime_lifecycle_integration`
- `manual readability calibration`
- `profile_weighted_evolution`
- `community profile packs`

## Interpretation

The prior PNG embedded sidecar proof is now extended across the standard PNG
textual metadata families required by the current research gap. The result is
still bounded: it proves four controlled textual chunk encodings over the
current Stage 0 profile corpus, not arbitrary PNG metadata behavior or editor
open-save preservation.

The strict policy decision is deliberate. `tEXt` and `zTXt` can store Latin-1,
but this lab rejects non-ASCII JSON in those carriers so Unicode semantic
metadata has one unambiguous path: `iTXt`.

## Verification

RED command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_png_textual_metadata_policy.py
```

Initial result:

```txt
ModuleNotFoundError: No module named 'png_textual_metadata_policy'
```

GREEN command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_png_textual_metadata_policy.py
```

Result:

```txt
Ran 5 tests in 0.085s
OK
```

Artifact command:

```powershell
python -B .\labs\workshop_editor\png_textual_metadata_policy.py
```

## Decision

Adopt `png_textual_metadata_policy_stage0` as the Stage 0 proof for bounded
PNG `tEXt`/`zTXt`/`iTXt` semantic sidecar metadata policy.

Live external editor rewrite validation, Adam7/APNG/full PNG conformance,
package runtime lifecycle integration, manual readability calibration, and
profile-weighted evolution remain blocked until each has explicit fixtures and
authorization.
