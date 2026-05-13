# Algorithm Card: SLIP Offspring Lineage Gate

## Purpose

Specify how a runtime-selected `SLIP` parent can produce bounded offspring
candidates and a lineage decision without claiming persistent evolution.

## Mathematical Basis

Profile-conditioned survivor gate over a parent/offspring set:

```txt
offspring_score = weighted_mean(validity, alignment, runtime, archive, novelty)
lineage_action = replace_parent | add_archive_niche | hold_parent
```

The gate separates parent selection, offspring mutation, and lineage
replacement. This follows the research plan requirement that mutation and
archive replacement remain explicit, testable operators.

## Inputs

- Valid SLIP profile
- Runtime-selected archive parent
- Parent grid genome and lineage metadata
- SLIP mutation caps
- Switchboard lifecycle metrics
- Extended MAP-Elites descriptor and fitness metrics

## Outputs

- Bounded offspring candidates
- Selected offspring
- Mutation-cap compliance record
- Runtime episode summary for the selected child
- Archive niche trace
- Lineage action and reason
- Invalid-probe rejections

## Strengths

- Produces actual child grid records rather than prose-only mutation plans.
- Enforces SLIP mutation caps and alignment before lineage decisions.
- Keeps archive niche addition separate from parent replacement.
- Preserves the parent unless the child beats a replacement threshold or opens
  a qualified archive niche.

## Weaknesses

- Stage 0 mutations are deliberately conservative.
- Multigeneration persistence now lives in the separate
  `slip_multigeneration_lineage_runner`.
- Runtime episodes in this gate remain short horizon; the separate
  `slip_long_horizon_behavior_gate` now covers held-out 96-tick behavior
  probes.
- Readability is still proxy-scored.

## Failure Modes

- Conservative mutation can over-hold parents.
- New archive niches can be sparse with small profile corpora.
- Proxy readability may accept children that need human calibration.

## Integration Risk

Medium.

## License Status

No external code selected.

## Prototype Result

Stage 0 offspring/lineage proof completed on 2026-05-13.

```txt
profile_count: 3
offspring_gate_success_count: 3
lineage_decision_count: 3
invalid_probe_rejected_count: 2
mean_selected_offspring_score: 0.928194
mean_selected_offspring_need_balance: 0.793865
mean_selected_offspring_survival_ratio: 1.0
distinct_selected_offspring_ids: 3
distinct_selected_offspring_niches: 3
replace_parent_count: 0
add_archive_niche_count: 1
hold_parent_count: 2
```

## Decision

Keep as active prototype. This closes the Stage 0 offspring mutation selection
and lineage replacement policy gap, and the follow-on long-horizon behavior
gate closes the held-out behavior-test gap. The follow-on multigeneration
runner closes lab lineage depth. This still does not close profile-weighted
evolution.

## Go/No-Go Gate

Promote only after manual readability calibration and package runtime
integration pass explicit gates.
