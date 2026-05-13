# Algorithm Card: SLIP Multigeneration Lineage Runner

## Purpose

Persist a lab-only multigeneration SLIP lineage by repeatedly mutating a
qualified frontier child, recording archive decisions, and verifying lineage
graph continuity.

## Mathematical Basis

For each generation:

```txt
offspring_score = weighted_mean(validity, alignment, runtime, archive, novelty)
lineage_action = replace_parent | add_archive_niche | hold_parent
continue_child = valid and aligned and caps_respected and survival_ratio == 1.0
```

The archive action and continuation frontier are deliberately separate:

```txt
archive_state updates only from lineage_action
frontier_parent updates when continue_child is true
```

This lets the lab stress-test descendant continuity without pretending every
continued child displaced an archive elite.

## Inputs

- Valid SLIP profile
- Profile-specific generated candidate corpus
- Runtime selection policy
- Bounded offspring mutation policy
- Lifecycle simulator
- Extended MAP-Elites descriptor scorer
- Lineage graph builder

## Outputs

- Per-generation selected child records
- Archive update records
- Continuation frontier records
- Lineage graph edges and orphan checks
- Invalid-probe rejections
- Closed and blocked state ledger

## Strengths

- Runs actual multigeneration child production instead of a one-step lineage
  decision.
- Uses the existing runtime selector, mutation caps, lifecycle scoring, and
  extended archive metrics.
- Preserves archive semantics by separating archive update actions from
  candidate-lineage continuation.
- Rejects invalid profiles before generation starts.

## Weaknesses

- Stage 0 still runs inside labs, not package runtime state.
- The frontier policy is deterministic and synthetic.
- Readability remains proxy-scored.
- The current corpus covers only three authored profiles.

## Failure Modes

- A child can continue as a frontier candidate without becoming an archive
  elite.
- Conservative mutations can produce many hold-parent archive decisions.
- Small profile corpora can understate longer-run extinction or dominance
  risks.
- Treating this lab as package runtime evolution would overclaim the result.

## Integration Risk

Medium.

## License Status

No external code selected.

## Prototype Result

Stage 0 multigeneration lineage proof completed on 2026-05-13.

```txt
profile_count: 3
multigeneration_success_count: 3
total_generation_records: 9
total_selected_offspring: 9
continued_child_count: 9
replace_parent_count: 0
add_archive_niche_count: 2
hold_parent_count: 7
invalid_probe_rejection_rate: 1.0
max_generation_reached: 4
mean_selected_offspring_score: 0.925309
mean_selected_runtime_survival_ratio: 1.0
mean_dominant_lineage_share: 0.333333
```

## Decision

Keep as active prototype. This closes the Stage 0 persistent multigeneration
lineage-runner gap for the lab, but does not close manual readability
calibration, package runtime integration, final descriptor thresholds, or
profile-weighted evolution.

## Go/No-Go Gate

Promote only after package/runtime lifecycle integration exists and manual
readability calibration locks descriptor thresholds.
