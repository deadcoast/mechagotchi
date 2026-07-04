# Workshop Editor Boundary Hardening

Date: 2026-07-04

Status: `research_workshop_editor_boundary_hardening_no_package_code`

## Purpose

Fix review findings M-02, M-03, M-04, L-07, and L-15 from
`docs/03-code_review/2026-07-04-code_review.md`, plus one regression
introduced by the same day's grid-validator schema alignment.

## What changed

1. **M-02** — `.pxo` zip reads in `third_party_project_decoder.py`,
   `project_native_metadata_writer.py`, and
   `project_editor_rewrite_preservation.py` now go through
   `_read_pxo_member`: a missing member named by attacker-controlled
   `data.json` raises typed `pxo_member_missing` (was raw `KeyError`), and
   members whose declared `file_size` exceeds `PXO_MEMBER_SIZE_CAP` (8 MiB)
   raise typed `*_member_too_large` before inflation. Negative tests added
   for both paths in all three modules.
2. **M-03** — `slip_preview_gates._profile_weight_effects_observed` computes
   over the actual profile set instead of hard-indexing the three default
   profile ids; custom `--profile` runs no longer crash with `KeyError`, and
   fewer than two profiles yields an explicit `insufficient_profiles` result.
   Default-run report values verified byte-identical.
3. **M-04** — `png_apng_sidecar_decoder.import_apng_with_sidecar` no longer
   catches `Exception`; it traps only the typed errors its decode path can
   raise (`APNGDecodeError`, `PNGEmbeddedSidecarError`, `PNGChunkError`), so
   programming bugs can no longer masquerade as malformed-input rejections.
   All invalid probes still reject with identical families.
4. **L-15** — the three remaining private `_read_png_chunks` copies
   (`png_apng_color_type_frame_data.py`, `png_apng_filtered_frame_data.py`,
   `png_apng_partial_frame_playback.py`) are now thin wrappers over the
   shared `png_chunk_reader.read_png_chunks`, adopting strict
   IEND/trailing-byte/ASCII-type behavior; per-module trailing-bytes negative
   tests added.
5. **L-07** — `symmetry_break_budget` is now `null` in the mutation preview
   (and `app.js` live preview): the preview model enumerates cell and organ
   candidates but has no symmetry-break candidate enumeration, so the old
   value merely echoed its own cap and made `caps_respected` trivially true
   on that axis.
6. **Regression fix** — the schema-alignment change earlier today
   (`05c7475`) enforced the `grid_id` pattern (max 64 chars); offspring ids
   in `slip_offspring_lineage_gate.py` compounded `_offspring_<variant>` per
   generation, so generation-2+ ids exceeded the limit and all four
   `slip_multigeneration_lineage_runner` tests errored (that commit's "all
   consuming lab suites green" claim missed workshop_editor, whose suite was
   in flight). `_offspring_grid_id` now compresses over-long ids
   deterministically (truncated prefix + sha256 suffix, ancestry preserved in
   `lineage.ancestor_ids`); a pinning test walks five generations and asserts
   schema conformance.

## Result

```powershell
python -B -m unittest discover -s labs/workshop_editor -p "test_*.py"
# Ran 267 tests in 4.079s
# OK  (was 259; +7 hardening tests, +1 regression pinning test)
```

Artifacts regenerated and validated: `slip_behavior_mutation_preview`
(symmetry budget `1 → null` only; metrics byte-identical),
`slip_lifecycle_archive_effects` / `slip_offspring_lineage_gate` /
`slip_multigeneration_lineage_runner` (budget nulls, compressed gen-2+ ids,
plus catching up `behavior_neediness` descriptor staleness from the H-03 fix
which had not regenerated these dependents), `apng_filtered_frame_data` (one
probe message string from the bounded-inflate adoption; family unchanged).
`third_party_project_decoder` artifacts were regenerated and reverted — the
diff was pure zip-timestamp noise (its `.pxo` encoder uses wall-clock
timestamps; the sibling modules use a stable-timestamp pattern — noted as
future alignment work).

## Decision

The workshop_editor import boundaries are now uniformly typed: missing/oversized
zip members, malformed metadata JSON, malformed PNG chunk streams, and
oversized zlib payloads all reject with family-tagged errors, and no import
path catches blind `Exception`. Offspring id generation is schema-bounded by
construction.

## Verification

```powershell
python -B -m unittest discover -s labs/workshop_editor -p "test_*.py"
python -B labs/workshop_editor/slip_offspring_lineage_gate.py
python -B labs/workshop_editor/slip_multigeneration_lineage_runner.py
python -m json.tool data/workshop_editor/slip_offspring_lineage_gate_stage0.json
```

## Sources

- `docs/03-code_review/2026-07-04-code_review.md`
- `labs/workshop_editor/third_party_project_decoder.py`
- `labs/workshop_editor/project_native_metadata_writer.py`
- `labs/workshop_editor/project_editor_rewrite_preservation.py`
- `labs/workshop_editor/slip_preview_gates.py`
- `labs/workshop_editor/png_apng_sidecar_decoder.py`
- `labs/workshop_editor/png_chunk_reader.py`
- `labs/workshop_editor/slip_offspring_lineage_gate.py`
- `research/experiment_reports/2026-07-04-grid-validator-schema-alignment.md`
- `research/experiment_reports/2026-07-04-workshop-editor-decoder-hardening.md`
- `data/workshop_editor/`
