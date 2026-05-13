# Experiment Report: Manual Readability Rating Intake

Date: 2026-05-12

## Objective

Continue the post-v0.2 research sequence by creating the intake and aggregation
gate for real human readability ratings without fabricating reviewer data.

## Source Basis

PCG metric research shows that quantitative metrics should be compared with
human evaluation when they make qualitative claims. Inter-rater reliability
research reinforces that multiple reviewer judgments need agreement checks
before being treated as calibration truth.

Sources:

- https://arxiv.org/abs/2107.02457
- https://bmcmedresmethodol.biomedcentral.com/articles/10.1186/s12874-016-0200-9

## Scope

Included:

- CSV rating template for the existing held-out readability packet
- reviewer row loader
- 1-5 rating validation
- per-sample median question aggregation
- proxy/human Spearman rank comparison when ratings exist
- explicit blocked status when no ratings exist

Not included:

- fabricated human ratings
- UI for collecting ratings
- formal Krippendorff alpha implementation
- proxy weight recalibration
- package promotion

## Method

The intake rebuilds the existing held-out readability benchmark with 10 samples
per source, then emits one blank CSV row per sample. Reviewers fill
`reviewer_id`, five question scores, and optional notes.

When rows exist, the intake validates scores, aggregates median question ratings
per sample, computes a mean human rating, and compares proxy readability against
human ratings. When no rows exist, the report is deliberately blocked as
`awaiting_human_ratings`.

## Verification

RED command:

```powershell
python -B .\labs\readability_benchmark\test_manual_rating_intake.py
```

Initial result:

```txt
ModuleNotFoundError: No module named 'manual_rating_intake'
```

GREEN command:

```powershell
python -B .\labs\readability_benchmark\test_manual_rating_intake.py
```

Result:

```txt
Ran 5 tests in 0.029s
OK
```

Lab command:

```powershell
python -B .\labs\readability_benchmark\manual_rating_intake.py --output-dir .\data\readability --ratings .\data\readability\manual_ratings.csv --count-per-source 10 --rng-seed 20260512
```

Result summary:

```json
{
  "status": "awaiting_human_ratings",
  "template_row_count": 30,
  "rating_row_count": 0,
  "valid_rating_row_count": 0,
  "rated_sample_count": 0,
  "reviewer_count": 0,
  "mean_human_rating": null,
  "proxy_human_spearman": null,
  "inter_reviewer_mean_absolute_delta": null
}
```

## Findings

The manual-rating gate is now executable. It creates a 30-row template aligned
to the existing held-out benchmark and refuses to claim calibration without
reviewer rows.

The proxy readability benchmark therefore remains useful as a gate, but not as
final visual adoption evidence. Human calibration is blocked until at least
three reviewers submit ratings for the held-out packet.

## Decision

Prototype the rating intake and keep proxy calibration blocked. Do not adjust
readability weights or promote proxy scores as final evidence until real human
ratings are collected and agreement is measured.
