# Manual Readability Rating Protocol

Protocol: `readability_rating_v0_1`

## Rating Scale

- 1: unreadable or noisy
- 2: weakly readable
- 3: usable but ambiguous
- 4: clear
- 5: immediately legible

## Questions

- `silhouette`: Can the creature body be recognized from its outline alone?
- `organ_clarity`: Are sensors, expression cells, and body core easy to identify?
- `palette_contrast`: Does the palette separate body, organs, and background?
- `animation_readiness`: Is there a clear anchor or pose feature for simple motion?
- `companion_appeal`: Does the grid read as a plausible companion rather than noise?

## Instructions

- Rate each sample independently before seeing generator source.
- Use 1 for unreadable/noisy, 3 for usable but ambiguous, and 5 for immediately legible.
- Do not treat novelty as readability unless the creature remains recognizable.
- Record reviewer id, timestamp, and optional notes separately from proxy metrics.

Minimum reviewers: 3
Aggregation: `median_per_question_then_mean`
