# Experiment Report: Workshop Multi-Profile Round Trip

Date: 2026-05-12

Status: `research_workshop_multi_profile_roundtrip_no_package_code`

## Question

Can the native semantic workshop import and export generated grids across all
current valid SLIP profiles without losing semantic fidelity or breaking SLIP
alignment?

## Plan Alignment

This continues Stage 7 of the research plan. The plan recommends a
Mechagotchi-native semantic pixel editor because generic sprite editors cannot
represent organ roles, mutation weights, survival semantics, or SLIP
constraints without sidecar metadata.

This report directly follows the SLIP multi-profile generation benchmark and
uses its generated corpora as workshop input. No `packages/` implementation was
created.

## External Source Refresh

The external editor references still support the current research posture:

- Piskel remains useful as an Apache-2.0 browser editor reference:
  https://github.com/piskelapp/piskel
- Pixelorama remains useful for import/export and project-metadata workflow
  research: https://www.pixelorama.org/user_manual/Import/
- LibreSprite remains useful as an animation-workflow reference, but GPL-2.0
  licensing keeps embedded-code reuse out of scope:
  https://github.com/LibreSprite/LibreSprite

## Method

Added the following workshop benchmark functions:

- `run_workshop_multi_profile_roundtrip_suite`
- `write_workshop_multi_profile_roundtrip_artifacts`

The benchmark loads all generated grids from:

- `data/slips/multi_profile_generation_stage0/slip_lcd_seed/`
- `data/slips/multi_profile_generation_stage0/slip_gray_stable/`
- `data/slips/multi_profile_generation_stage0/slip_amber_social/`

Each grid is imported with its matching SLIP profile, exported through the
native workshop path, validated, checked for SLIP alignment, and compared
against the source grid for semantic fidelity.

## Results

| Profile | Candidates | Round-trip successes | Import valid | Export valid | SLIP aligned | Mean semantic fidelity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `slip_lcd_seed` | 50 | 50 | 50 | 50 | 50 | 1.0 |
| `slip_gray_stable` | 50 | 50 | 50 | 50 | 50 | 1.0 |
| `slip_amber_social` | 50 | 50 | 50 | 50 | 50 | 1.0 |
| **Total** | **150** | **150** | **150** | **150** | **150** | **1.0** |

Artifacts:

- `data/workshop_editor/multi_profile_roundtrip_stage0/workshop_multi_profile_roundtrip_stage0.json`
- `data/workshop_editor/multi_profile_roundtrip_stage0/slip_lcd_seed_roundtrips.json`
- `data/workshop_editor/multi_profile_roundtrip_stage0/slip_gray_stable_roundtrips.json`
- `data/workshop_editor/multi_profile_roundtrip_stage0/slip_amber_social_roundtrips.json`

## Interpretation

The previous workshop proof was one native JSON round trip under
`slip_lcd_seed`. The current proof covers 150 generated candidates across all
three valid Stage 0 profiles.

This proves native semantic JSON round-trip fidelity for the generated
multi-profile corpus. This report itself did not prove visual-image or
third-party project-file import/export. The
follow-up external metadata sidecar strategy now proves a Stage 0 semantic
preservation contract, and static RGBA PNG sidecar import/export now has a
Stage 0 decoder proof. Explicit 8-bit non-interlaced PNG color/filter variant
sidecar import/export and fixed horizontal-strip spritesheet PNG sidecar
import/export now also have Stage 0 decoder proofs. GIF, project-file
import/export, full PNG conformance, spritesheet variant layouts, and metadata
writer policies remain blocked until they are implemented against that
contract.

Supersession note: the minimal profile-authoring panel is now covered by
`research/experiment_reports/2026-05-12-slip-authoring-panel.md`. This
round-trip benchmark itself does not prove behavior preview or mutation
preview. The separate preview gate is now covered by
`research/experiment_reports/2026-05-12-slip-behavior-mutation-preview-gate.md`.
The external sidecar strategy is now covered by
`research/experiment_reports/2026-05-12-external-metadata-sidecar-strategy.md`.
The static RGBA PNG sidecar decoder is now covered by
`research/experiment_reports/2026-05-12-standard-image-sidecar-decoder.md`.
The fixed horizontal-strip spritesheet sidecar decoder is now covered by
`research/experiment_reports/2026-05-12-spritesheet-sidecar-decoder.md`.

## Verification

```powershell
python -B -m unittest discover -s labs\workshop_editor -p "test_workshop_editor.py"
python -B labs\workshop_editor\workshop_editor.py --multi-profile-root data\slips\multi_profile_generation_stage0 --multi-profile-output-dir data\workshop_editor\multi_profile_roundtrip_stage0
python -m json.tool data\workshop_editor\multi_profile_roundtrip_stage0\workshop_multi_profile_roundtrip_stage0.json
```

## Decision

Adopt `workshop_multi_profile_roundtrip_stage0` as the Stage 0 proof that the
native workshop can round-trip generated SLIP-constrained semantic grids across
the current valid profile corpus.

The follow-up versioned SLIP schema/failure corpus and minimal SLIP
profile-authoring panel are now complete. The deterministic behavior/mutation
preview gate is also complete. The external sidecar strategy and static RGBA
PNG sidecar decoder are complete, and fixed horizontal-strip spritesheet
sidecar decoding is complete for that exact layout. Broader spritesheet layout
coverage and project import remain premature until real decoders can bind
assets to that sidecar without losing semantic profile constraints.
