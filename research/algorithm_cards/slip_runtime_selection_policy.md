# Algorithm Card: SLIP Runtime Selection Policy

## Purpose

Specify how a valid `SLIP` profile can choose one existing archive elite using
runtime lifecycle measurements as the parent-selection step before bounded
offspring/lineage gates run.

## Mathematical Basis

Profile-conditioned elite selection over a quality-diversity archive:

```txt
candidate_score = weighted_mean(runtime_metrics, archive_metrics, SLIP_weights)
selected_elite = argmax(candidate_score)
```

The selector consumes switchboard lifecycle episodes and extended MAP-Elites
elite descriptors. Child mutation and lineage decisions now live in the
separate `slip_offspring_lineage_gate` card. Held-out long-horizon behavior
probes now live in `slip_long_horizon_behavior_gate`.

## Inputs

- Valid SLIP profile
- Generated SLIP-aligned candidate corpus
- Switchboard lifecycle episode metrics
- Extended MAP-Elites archive elites
- Profile behavior and survival weights

## Outputs

- Selected archive elite
- Selection score
- Component weights
- Runtime lifecycle summary
- Archive niche trace
- Rejection results for invalid version or mismatched candidate corpus

## Strengths

- Connects lifecycle and archive evidence through one auditable policy.
- Preserves MAP-Elites diversity by selecting from elites rather than scalar
  top-k candidates.
- Keeps profile weights explicit in the selection trace.
- Rejects invalid profiles before any runtime selection starts.

## Weaknesses

- Parent-selection episodes remain short-horizon synthetic lifecycle episodes;
  long-horizon behavior is checked by the follow-on behavior gate.
- Archive readability remains proxy-scored.
- No package runtime loop exists yet.

## Failure Modes

- Profile weights could over-favor stable but bland candidates.
- Sparse archive niches can make rarity noisy with small candidate pools.
- A selected elite can be useful as a parent without being sufficient proof of
  persistent evolution.

## Integration Risk

Medium.

## License Status

No external code selected.

## Prototype Result

Stage 0 runtime selection proof completed on 2026-05-13.

```txt
profile_count: 3
selection_success_count: 3
selected_elite_count: 3
distinct_selected_grid_ids: 3
distinct_selected_archive_niches: 3
mean_selected_selection_score: 0.955828
mean_selected_need_balance: 0.793865
mean_selected_survival_ratio: 1.0
invalid_probe_rejection_rate: 1.0
```

## Decision

Keep as active prototype. Use it as the Stage 0 bridge from SLIP weights to
runtime lifecycle/archive parent selection. Do not claim profile-weighted
evolution until manual readability calibration and package runtime integration
pass.

## Go/No-Go Gate

Promote only after manual readability calibration and package runtime
integration pass explicit gates.
