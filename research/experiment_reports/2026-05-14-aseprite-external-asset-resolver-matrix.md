# Experiment Report: Aseprite External Asset Resolver Matrix

Date: 2026-05-14

Status: `research_aseprite_external_asset_resolver_matrix_no_package_code`

## Question

Can Mechagotchi resolve Aseprite/LibreSprite External Files Chunk assets
through multiple hash-checked resolver policies before semantic restore,
without claiming live editor validation or arbitrary project schema coverage?

## Plan Alignment

This continues the Stage 7 workshop/editor track in
`docs/02-research_plan.md`. The compatibility matrix kept arbitrary external
asset resolution and editor-authored document variants blocked after the
document-variant lab. This experiment adds a bounded resolver matrix for the
current generated document-variant corpus.

## External Anchor

Source used:

- [Aseprite file-format specification](https://github.com/aseprite/aseprite/blob/main/docs/ase-file-specs.md)

The specification anchors External Files Chunk `0x2008`. This lab does not
embed Aseprite or LibreSprite code.

## Method

Added `labs/workshop_editor/test_aseprite_external_asset_resolver_matrix.py`
first and watched it fail on the missing module. Then added
`labs/workshop_editor/aseprite_external_asset_resolver_matrix.py`.

The lab reuses the existing Aseprite document-variant project generator and
tests each current profile across:

- indexed 8 bpp document variant;
- grayscale-alpha 16 bpp document variant;
- RGBA 32 bpp document variant;
- direct manifest resolver;
- relative file-map resolver;
- content-addressed pool resolver;
- multi-root priority resolver.

Invalid probes cover missing assets, tampered payloads, ambiguous candidates,
path traversal, and unsupported resolver policy IDs.

## Results

Machine-readable artifacts:

- `data/workshop_editor/aseprite_external_asset_resolver_matrix_stage0.json`
- `data/workshop_editor/aseprite_external_asset_resolver_matrix_stage0/aseprite_external_asset_resolver_matrix_stage0.json`
- `data/workshop_editor/aseprite_external_asset_resolver_matrix_stage0/projects/*.aseprite`
- `data/workshop_editor/aseprite_external_asset_resolver_matrix_stage0/resolver_sources/`
- `data/workshop_editor/aseprite_external_asset_resolver_matrix_data.js`

Summary:

| Metric | Result |
| --- | ---: |
| Current valid profiles covered | 3 |
| Document variants per profile | 3 |
| Resolver policies | 4 |
| Resolver round trips | 36 |
| Resolver round-trip successes | 36 |
| Invalid probes rejected | 5 |
| Resolver round-trip success rate | 1.0 |
| Mean semantic fidelity | 1.0 |
| External asset resolution rate | 1.0 |
| Invalid probe rejection rate | 1.0 |

Closed states:

- `aseprite_direct_manifest_asset_resolver_subset`
- `aseprite_relative_file_asset_resolver_subset`
- `aseprite_content_addressed_asset_resolver_subset`
- `aseprite_multi_root_asset_resolver_subset`
- `aseprite_external_asset_resolver_invalid_probe_rejection`

Blocked states:

- `live_external_editor_rewrite_validation`
- `editor_authored_aseprite_document_variants`
- `arbitrary_aseprite_project_schema_coverage`
- `full_project_format_coverage`
- `package_runtime_lifecycle_integration`
- `manual_readability_calibration`
- `profile_weighted_evolution`

## Interpretation

The resolver matrix broadens the external-asset proof beyond a direct generated
asset list. It adds path-safety, ambiguity, and content-hash checks before the
document-variant importer can restore semantics.

This is still not arbitrary external asset resolution in the full product
sense. The assets and projects are generated Stage 0 fixtures. Live
editor-authored Aseprite/LibreSprite files, arbitrary project schemas, and
open-save preservation remain blocked.

## Verification

RED command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_aseprite_external_asset_resolver_matrix.py
```

Initial result:

```txt
ModuleNotFoundError: No module named 'aseprite_external_asset_resolver_matrix'
```

GREEN command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_aseprite_external_asset_resolver_matrix.py
```

Result:

```txt
Ran 5 tests in 0.117s
OK
```

Artifact command:

```powershell
python -B .\labs\workshop_editor\aseprite_external_asset_resolver_matrix.py
```

## Decision

Adopt `aseprite_external_asset_resolver_matrix_stage0` as a bounded generated
resolver proof. Do not claim live editor validation, editor-authored Aseprite
document variants, arbitrary Aseprite project schemas, package runtime
integration, manual readability calibration, or profile-weighted evolution.
