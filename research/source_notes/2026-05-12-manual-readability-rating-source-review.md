# Manual Readability Rating Source Review - 2026-05-12

## Primary Sources

- https://arxiv.org/abs/2107.02457
- https://bmcmedresmethodol.biomedcentral.com/articles/10.1186/s12874-016-0200-9

## Confirmed Facts

- PCG metrics can make qualitative claims that should be compared against human
  evaluation rather than accepted as self-validating.
- Human rating studies need an explicit reusable methodology and recorded
  reviewer data.
- Inter-rater reliability matters when multiple people judge the same content;
  agreement should be measured before treating ratings as calibration truth.

## Mechagotchi Interpretation

Mechagotchi should not tune proxy readability weights from invented ratings.
The correct Stage 0 step is to freeze the held-out sample packet, emit a blank
rating template, and define the intake analysis that will run after reviewers
submit rows.

The current intake therefore reports `awaiting_human_ratings` until a reviewer
CSV is supplied. Once supplied, it aggregates median question ratings per sample
and compares human ratings against proxy scores with a Spearman rank check.
