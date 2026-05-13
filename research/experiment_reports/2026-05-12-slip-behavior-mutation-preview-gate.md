# Experiment Report: SLIP Behavior and Mutation Preview Gate

Date: 2026-05-12

Status: `research_slip_behavior_mutation_preview_no_package_code`

## Question

Can current `SLIP` profiles drive deterministic workshop previews for behavior
and mutation while still rejecting invalid profiles before preview activation?

## Plan Alignment

This continues Stage 6 of `docs/02-research_plan.md`: a user-created `SLIP`
must be able to preview behavior and mutation. The gate remains a workshop lab
artifact. It does not create package code, train a policy, mutate offspring, or
prove profile-weighted evolution.

## External Source Refresh

The preview uses conservative browser and research anchors:

- PCG literature frames mutation as bounded candidate generation, not random
  unconstrained change: https://www.pcgbook.com/
- Sutton and Barto's reinforcement-learning text is treated as background for
  action-value thinking only; this lab uses a deterministic proxy, not RL:
  https://mitpress.mit.edu/9780262039246/reinforcement-learning/
- MDN's `<output>` element documentation anchors the static browser surface for
  calculated preview results:
  https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/output

## Method

Added `labs/workshop_editor/slip_preview_gates.py` with:

- `validate_preview_request`
- `build_behavior_preview`
- `build_mutation_preview`
- `run_slip_preview_gate_lab`
- `write_slip_preview_gate_artifacts`

The behavior preview derives deterministic profile signals from the current
behavior and survival weights:

- social pull
- exploration pull
- rest pull
- mutation pressure
- mutation caution

The mutation preview reads the generated profile-aligned grid corpus and
projects bounded candidate counts from the active mutation caps. It does not
change grid cells.

The static workshop app now exposes preview panels in:

- `labs/workshop_editor/index.html`
- `labs/workshop_editor/app.js`
- `labs/workshop_editor/styles.css`

## Results

Machine-readable artifacts:

- `data/workshop_editor/slip_behavior_mutation_preview_stage0.json`
- `data/workshop_editor/slip_behavior_mutation_preview_stage0/slip_behavior_mutation_preview_stage0.json`
- `data/workshop_editor/slip_behavior_mutation_preview_stage0/slip_lcd_seed_preview_gate.json`
- `data/workshop_editor/slip_behavior_mutation_preview_stage0/slip_gray_stable_preview_gate.json`
- `data/workshop_editor/slip_behavior_mutation_preview_stage0/slip_amber_social_preview_gate.json`
- `data/workshop_editor/slip_preview_gate_data.js`

Summary:

| Metric | Result |
| --- | ---: |
| Current valid profiles covered | 3 |
| Behavior previews produced | 3 |
| Mutation previews produced | 3 |
| Invalid probes rejected | 2 |
| Preview gate success rate | 1.0 |
| Profile-weight effects observed | true |
| Mutation caps respected | true |

Observed profile effects:

- `slip_amber_social` has the highest social pull.
- `slip_gray_stable` has the highest rest pull and mutation caution.
- all current single-palette profiles block palette-shift preview.

## Interpretation

This closes the Stage 0 behavior and mutation preview gate for current valid
profiles. The result is intentionally narrow: it proves previewability and cap
respect, not actual lifecycle outcomes, archive scoring effects, offspring
validity, or profile-weighted evolution.

## Verification

```powershell
python -B -m unittest labs\workshop_editor\test_slip_preview_gates.py
python -B labs\workshop_editor\slip_preview_gates.py --output-dir data\workshop_editor\slip_behavior_mutation_preview_stage0
python -m json.tool data\workshop_editor\slip_behavior_mutation_preview_stage0.json
python -m json.tool data\workshop_editor\slip_behavior_mutation_preview_stage0\slip_behavior_mutation_preview_stage0.json
node --check labs\workshop_editor\app.js
```

## Decision

Adopt `slip_behavior_mutation_preview_stage0` as the current deterministic
preview gate. Keep `profile_weighted_evolution`, lifecycle behavior
integration, usability pilot, runtime JSON Schema, and declared dependency
policy open. The external metadata sidecar strategy is now covered separately in
`research/experiment_reports/2026-05-12-external-metadata-sidecar-strategy.md`;
static RGBA PNG sidecar decoding is now covered in
`research/experiment_reports/2026-05-12-standard-image-sidecar-decoder.md`.
Fixed horizontal-strip spritesheet sidecar decoding is now covered in
`research/experiment_reports/2026-05-12-spritesheet-sidecar-decoder.md`.
The measured lifecycle/archive bridge is now covered in
`research/experiment_reports/2026-05-12-slip-lifecycle-archive-effects.md`.
Packed rotation/trim atlas handling, runtime animation playback, full
project-format coverage, full PNG conformance, runtime profile-weighted
evolution, and metadata writers remain open. The explicit PNG color/filter
variant subset is now covered by
`research/experiment_reports/2026-05-13-png-variant-sidecar-decoder.md`.
Spritesheet vertical/matrix/padded/sparse layout coverage is now covered by
`research/experiment_reports/2026-05-13-spritesheet-layout-variant-decoder.md`.
