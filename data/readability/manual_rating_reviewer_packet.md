# Manual Readability Reviewer Packet

Date: 2026-05-12

## Status

Collection packet prepared. Human ratings are still absent.

## Purpose

Collect real human readability ratings for the frozen Stage 0 held-out packet
without changing the sample set or fabricating reviewer data.

## Files

- Template to fill: `data/readability/manual_rating_template.csv`
- Completed file to create: `data/readability/manual_ratings.csv`
- Intake command:

```powershell
python -B .\labs\readability_benchmark\manual_rating_intake.py --output-dir .\data\readability --ratings .\data\readability\manual_ratings.csv --count-per-source 10 --rng-seed 20260512
```

## Reviewer Assignment

- Minimum reviewers: 3
- Samples per reviewer: 30
- Expected completed rows: 90
- Sources per reviewer:
  - `seed_holdout`: 10 rows
  - `constrained_holdout`: 10 rows
  - `markov_holdout`: 10 rows

Each reviewer should fill every row in `manual_rating_template.csv`. Combine
the reviewer rows into `manual_ratings.csv` with the same header.

## Required Columns

```txt
sample_id,grid_id,source,reviewer_id,silhouette,organ_clarity,palette_contrast,animation_readiness,companion_appeal,notes
```

The five score columns must be integers from 1 to 5:

- `silhouette`
- `organ_clarity`
- `palette_contrast`
- `animation_readiness`
- `companion_appeal`

## Rating Scale

- 1: unreadable or noisy
- 2: weakly readable
- 3: usable but ambiguous
- 4: clear
- 5: immediately legible

## Reviewer Instructions

- Rate each sample independently.
- Do not adjust scores after comparing generator sources.
- Use `3` when a sample is usable but ambiguous.
- Use `5` only when the creature is immediately legible.
- Do not reward novelty unless the creature remains recognizable.
- Notes are optional, but should be short and specific when used.

## Acceptance Gate

The rating packet is complete only when:

1. `data/readability/manual_ratings.csv` exists.
2. The file keeps the exact template header.
3. At least three unique `reviewer_id` values are present.
4. Each reviewer has one row for all 30 sample IDs.
5. All five score columns contain integers from 1 to 5.
6. The intake command reports `ratings_collected`.
7. Proxy/human agreement and reviewer agreement fields are populated.

Until those checks pass, readability calibration remains blocked.

## Source Basis

- PCG metric claims should be checked against human evaluation:
  https://arxiv.org/abs/2107.02457
- Inter-rater reliability should be measured before treating reviewer data as
  calibration truth:
  https://bmcmedresmethodol.biomedcentral.com/articles/10.1186/s12874-016-0200-9

