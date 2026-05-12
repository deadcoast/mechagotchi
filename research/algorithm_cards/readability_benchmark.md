# Algorithm Card: Readability Benchmark

## Purpose

Evaluate whether generated grid genomes are visually legible before they are
used for archive fitness, lifecycle experiments, or workshop presentation.

## Mathematical Basis

Weighted proxy scoring over semantic grid metrics:

- validation status
- connected component score
- body mass target score
- silhouette entropy target score
- bilateral symmetry score
- organ detectability
- palette contrast
- animation anchor coverage

The benchmark also defines a manual rating protocol so human ratings can later
calibrate or replace the proxy weights.

## Inputs

- Valid and invalid grid-genome samples
- Generator source label
- Rating protocol version
- Optional future human ratings

## Outputs

- Per-sample proxy readability score
- Metric breakdown
- Source-level summary
- Manual rating packet
- Human rating status

## Strengths

- Creates a held-out benchmark separate from generator implementation.
- Penalizes invalid grids while still exposing partial visual metrics.
- Produces enough separation to compare strong and weak generators.
- Avoids inventing human ratings before review actually happens.

## Weaknesses

- Proxy weights are hand-set.
- The current sample set is small.
- Human ratings are protocol-defined but not collected.
- Palette contrast is scalar and does not yet model display context.

## Failure Modes

- Proxy score can reward symmetry even when the creature is bland.
- Entropy can favor noisy silhouettes without human calibration.
- A valid but unappealing grid can score higher than a readable but unusual one.
- Reviewer-facing samples need blinding before formal rating.

## Integration Risk

Medium.

## License Status

No external code selected.

## Prototype Result

First held-out readability benchmark completed on 2026-05-12.

```txt
source                 samples  valid  mean_proxy_readability
seed_holdout           10       10     0.867316
constrained_holdout    10       10     0.830172
markov_holdout         10        0     0.374730
```

## Decision

Keep as active prototype. Use this benchmark as the readability gate before
expanding MAP-Elites descriptors or promoting visual generators.

## Go/No-Go Gate

Do not treat proxy readability as final adoption evidence until at least three
manual reviewers rate the held-out packet and proxy/human agreement is measured.
