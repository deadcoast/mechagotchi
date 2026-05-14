# Experiment Report: PNG Private Chunk Policy

Date: 2026-05-14

Status: `research_png_private_chunk_policy_no_package_code`

## Question

Can Mechagotchi store and recover semantic sidecar metadata in a bounded
app-private PNG ancillary chunk while preserving decoded pixels, SLIP
alignment, canonical image binding, and clear carrier-selection limits?

## Plan Alignment

This continues the Stage 7 workshop/editor track in
`docs/02-research_plan.md`. Previous PNG metadata proofs covered external
sidecars, standard image sidecars, color/filter variants, embedded `tEXt`, and
bounded `tEXt`/`zTXt`/`iTXt` textual metadata. This experiment tests one
private ancillary chunk policy without creating `packages/` code and without
claiming a final production carrier decision.

## External Anchor

Source used:

- [W3C PNG specification, Third Edition](https://www.w3.org/TR/png-3/)

The specification defines chunk type property bits by case, including the
ancillary bit, private bit, reserved bit, and safe-to-copy bit. It also gives
guidance for private chunks: use app-specific identifying information at the
start of the chunk data, do not use private chunks merely for text metadata
that standard text chunks can carry, and use ancillary chunks when private
information is not essential for image display.

## Method

Added `labs/workshop_editor/test_png_private_chunk_policy.py` first and
watched it fail on the missing module. Then added
`labs/workshop_editor/png_private_chunk_policy.py` with:

- `export_png_private_chunk_bundle`
- `import_png_private_chunk`
- `remove_png_private_chunks`
- invalid-probe helpers for missing chunk, duplicate chunk, safe-to-copy type
  mutation, magic mismatch, invalid JSON, canonical hash mismatch, and sidecar
  hash mismatch
- `run_png_private_chunk_policy_lab`
- `write_png_private_chunk_policy_artifacts`

The lab uses private chunk type `mgOT`:

```txt
m = ancillary
g = private
O = reserved bit valid
T = unsafe-to-copy
```

The payload begins with `mechagotchi.private_chunk.v1\0`, followed by UTF-8
JSON metadata. The chunk is unsafe-to-copy because the metadata is bound to the
canonical PNG bytes. If an editor rewrites image data, preserving the chunk
without rewriting hashes must fail import.

## Results

Machine-readable artifacts:

- `data/workshop_editor/png_private_chunk_policy_stage0.json`
- `data/workshop_editor/png_private_chunk_policy_stage0/png_private_chunk_policy_stage0.json`
- `data/workshop_editor/png_private_chunk_policy_stage0/*.png`
- `data/workshop_editor/png_private_chunk_policy_data.js`

Summary:

| Metric | Result |
| --- | ---: |
| Current valid profiles covered | 3 |
| Private chunk round trips | 3 |
| Private chunk round-trip successes | 3 |
| Invalid probes rejected | 7 |
| Private chunk round-trip success rate | 1.0 |
| Mean semantic fidelity | 1.0 |
| Mean pixel fidelity | 1.0 |
| Invalid probe rejection rate | 1.0 |

Closed states:

- `png_private_chunk_type_bits_policy`
- `png_private_chunk_magic_prefix_policy`
- `png_private_chunk_hash_validation`
- `png_private_chunk_invalid_probe_rejection`
- `png_metadata_carrier_selection_inputs`

Blocked states:

- `production_import_export_carrier_selection_final_decision`
- `live_external_editor_rewrite_validation`
- `Adam7/APNG/full PNG conformance`
- `private_chunk_editor_preservation_matrix`
- `package_runtime_lifecycle_integration`
- `manual readability calibration`
- `profile_weighted_evolution`

## Interpretation

The private chunk path works for a controlled app-native PNG metadata carrier,
but it should not be promoted as the default production carrier yet. The lab
records a provisional recommendation:

```txt
textual_or_external_sidecar_preferred_until_editor_fixtures
```

That recommendation is deliberately conservative. `iTXt` is the better
standard route for non-ASCII textual metadata, external sidecars remain the
most editor-compatible route when metadata preservation is unknown, and private
chunks remain useful only if live editor fixtures show preservation behavior
that justifies the app-native carrier.

## Verification

RED command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_png_private_chunk_policy.py
```

Initial result:

```txt
ModuleNotFoundError: No module named 'png_private_chunk_policy'
```

GREEN command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_png_private_chunk_policy.py
```

Result:

```txt
Ran 5 tests in 0.035s
OK
```

Artifact command:

```powershell
python -B .\labs\workshop_editor\png_private_chunk_policy.py
```

## Decision

Adopt `png_private_chunk_policy_stage0` as the bounded Stage 0 proof for a
single app-private PNG metadata carrier and metadata-carrier selection inputs.

Do not claim a final production import/export carrier decision, live external
editor preservation, Adam7/APNG/full PNG conformance, package runtime
integration, manual readability calibration, or profile-weighted evolution.
