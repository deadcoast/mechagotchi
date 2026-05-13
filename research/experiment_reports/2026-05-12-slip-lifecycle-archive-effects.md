# Experiment Report: SLIP Lifecycle and Archive Effects

Date: 2026-05-12

Status: `research_slip_lifecycle_archive_effects_no_package_code`

## Question

Can current deterministic `SLIP` preview signals be connected to measured
lifecycle and extended archive effects without claiming full profile-weighted
evolution?

## Plan Alignment

This continues the research plan's `SLIP`, lifecycle, micro-learning, and
`mecha_darwin` archive tracks. The result is a Stage 0 bridge from workshop
previewability to measured lab effects. It does not create package code, adopt
an online learner, mutate offspring, or integrate a runtime archive selection
policy.

## External Source Refresh

- Sutton and Barto's official online draft is used only as action-value and
  bandit vocabulary background; this lab does not train RL:
  http://incompleteideas.net/book/the-book-2nd.html
- MAP-Elites remains the quality-diversity archive reference for preserving
  high-performing elites across behavior descriptors:
  https://arxiv.org/abs/1504.04909
- Contextual bandits remain future personalization context; this lab records
  deterministic profile effects before online learning:
  https://arxiv.org/abs/1003.0146

## Method

Added `labs/workshop_editor/slip_lifecycle_archive_effects.py` and focused
tests in `labs/workshop_editor/test_slip_lifecycle_archive_effects.py`.

For each current valid profile, the lab:

- validates the profile/grid request through the existing preview gate;
- builds deterministic behavior and mutation previews;
- runs a 24-tick switchboard lifecycle probe on the first aligned grid;
- builds a 12-candidate extended MAP-Elites archive for that profile;
- records preview, lifecycle, and archive effect fingerprints;
- rejects unsupported-version and mismatched-profile/grid probes before effects
  start.

## Results

Machine-readable artifacts:

- `data/workshop_editor/slip_lifecycle_archive_effects_stage0.json`
- `data/workshop_editor/slip_lifecycle_archive_effects_stage0/slip_lifecycle_archive_effects_stage0.json`
- `data/workshop_editor/slip_lifecycle_archive_effects_stage0/slip_lcd_seed_lifecycle_archive_effects.json`
- `data/workshop_editor/slip_lifecycle_archive_effects_stage0/slip_gray_stable_lifecycle_archive_effects.json`
- `data/workshop_editor/slip_lifecycle_archive_effects_stage0/slip_amber_social_lifecycle_archive_effects.json`
- `data/workshop_editor/slip_lifecycle_archive_effects_data.js`

Summary:

| Metric | Result |
| --- | ---: |
| Current valid profiles covered | 3 |
| Valid preview requests | 3 |
| Lifecycle effects measured | 3 |
| Archive effects measured | 3 |
| Invalid probes rejected | 2 |
| Distinct preview fingerprints | 3 |
| Distinct lifecycle fingerprints | 3 |
| Distinct archive fingerprints | 3 |
| Mean lifecycle need balance | 0.793865 |
| Mean lifecycle survival ratio | 1.0 |
| Mean archive QD score | 7.671145 |

## Interpretation

This closes the narrow gap between deterministic preview output and measurable
Stage 0 lab effects. The bridge proves that the three current valid profiles
produce distinct preview, lifecycle, and archive fingerprints under the current
short-horizon simulator and descriptor archive.

The result still does not prove profile-weighted evolution. Runtime
lifecycle/archive elite selection is now covered by
`research/experiment_reports/2026-05-13-slip-runtime-selection-policy.md`.
Evolution remains blocked until offspring mutation/selection, lineage
replacement, held-out long-horizon tests, and package-level contracts are
specified and tested.

## Verification

```powershell
python -B -m unittest labs\workshop_editor\test_slip_lifecycle_archive_effects.py
python -B labs\workshop_editor\slip_lifecycle_archive_effects.py --generated-root data\slips\multi_profile_generation_stage0 --output-dir data\workshop_editor\slip_lifecycle_archive_effects_stage0
python -m json.tool data\workshop_editor\slip_lifecycle_archive_effects_stage0.json
python -m json.tool data\workshop_editor\slip_lifecycle_archive_effects_stage0\slip_lifecycle_archive_effects_stage0.json
```

## Decision

Adopt `slip_lifecycle_archive_effects_stage0` as the measured Stage 0 bridge
from preview signals to lifecycle/archive effects. Keep `profile_weighted_evolution`,
package runtime lifecycle integration, offspring mutation selection, lineage
replacement policy, runtime JSON Schema, declared dependency policy, usability
pilot, community profile packs, packed rotation/trim atlas handling, runtime
animation playback, full project-format coverage, and metadata writers open.

Supersession note: third-party project boundary decoding is now covered by
`research/experiment_reports/2026-05-13-third-party-project-decoder-boundary.md`;
this does not close full editor-native project coverage or native metadata
writer policy.
PNG color/filter variants are now covered by
`research/experiment_reports/2026-05-13-png-variant-sidecar-decoder.md`, and
spritesheet vertical/matrix/padded/sparse layout coverage is now covered by
`research/experiment_reports/2026-05-13-spritesheet-layout-variant-decoder.md`.
