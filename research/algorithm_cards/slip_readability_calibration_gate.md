# Algorithm Card: SLIP Readability Calibration Gate

## Purpose

Prepare the current SLIP long-horizon corpus for manual readability review and
block proxy-threshold calibration until real reviewer rows satisfy completeness,
agreement, and proxy-correlation checks.

## Mathematical Basis

For each sample:

```txt
proxy_readability_score = weighted_sum(validity, component_score,
body_mass_score, silhouette_score, symmetry_score, organ_detectability,
palette_contrast, animation_anchor_coverage)
```

Manual readiness requires:

```txt
complete = reviewers >= 3
        and rated_sample_count == sample_count
        and valid_rating_rows >= sample_count * 3
        and row_error_count == 0

ready = complete
     and inter_reviewer_mean_absolute_delta <= 1.0
     and proxy_human_spearman >= 0.25
```

## Inputs

- SLIP long-horizon behavior gate artifact
- Reconstructed selected offspring grids
- Held-out long-horizon candidate grids
- Existing readability proxy scorer
- Existing manual rating protocol and intake parser
- Optional filled reviewer CSV

## Outputs

- SLIP-specific readability benchmark
- CSV template for reviewers
- Reviewer packet
- Manual intake result
- Calibration readiness decision
- Closed and blocked state ledger

## Strengths

- Uses the exact corpus that passed the long-horizon behavior gate.
- Keeps proxy readability separate from human calibration.
- Requires complete coverage from at least three reviewers.
- Records reviewer agreement and proxy-human rank correlation separately.

## Weaknesses

- No bundled human ratings exist yet.
- Spearman correlation is descriptive and weak at small sample counts.
- The sample set covers current profiles, not community profile packs.
- The agreement check is a Stage 0 mean-absolute-delta proxy, not a final
  formal reliability model.

## Failure Modes

- Proxy scores can look stable while human reviewers disagree.
- Uniform human ratings make rank correlation undefined.
- Partial CSV rows can create a false sense of progress if only row count is
  inspected.
- Profile-weighted evolution can be overclaimed if packet readiness is treated
  as calibration readiness.

## Integration Risk

Medium.

## License Status

No external code selected.

## Prototype Result

Stage 0 SLIP readability packet completed on 2026-05-13.

```txt
sample_count: 21
selected_offspring_sample_count: 3
held_out_long_horizon_sample_count: 18
expected_completed_rating_rows: 63
mean_proxy_readability_score: 0.835645
rating_row_count: 0
reviewer_count: 0
proxy_human_spearman: null
inter_reviewer_mean_absolute_delta: null
manual_readability_calibration_ready: false
```

## Decision

Keep as active prototype. This closes the reviewer-packet and proxy-snapshot
step for the current SLIP long-horizon corpus, but does not close manual
readability calibration, profile-weighted evolution, package runtime
integration, or final descriptor thresholds.

## Go/No-Go Gate

Promote readability calibration only after a filled
`data/readability/slip_readability_calibration_ratings.csv` supplies 63 valid
reviewer rows, no row errors, acceptable inter-reviewer agreement, and positive
proxy-human rank correlation.
