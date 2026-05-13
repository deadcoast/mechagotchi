# SLIP Readability Calibration Reviewer Packet

Rate every row in `slip_readability_calibration_template.csv` before looking at proxy readability values. Use independent reviewer IDs and one row per sample per reviewer.

Protocol:

- Protocol ID: `readability_rating_v0_1`
- Rating scale: [1, 2, 3, 4, 5]
- Minimum reviewers: 3
- Sample count: 21
- Expected completed rows: 63
- Aggregation: median per question, then mean across questions

Questions:

- `silhouette`: Can the creature body be recognized from its outline alone?
- `organ_clarity`: Are sensors, expression cells, and body core easy to identify?
- `palette_contrast`: Does the palette separate body, organs, and background?
- `animation_readiness`: Is there a clear anchor or pose feature for simple motion?
- `companion_appeal`: Does the grid read as a plausible companion rather than noise?

Calibration remains blocked until the filled CSV has all expected reviewer rows, no row errors, acceptable inter-reviewer agreement, and a positive proxy-human rank correlation.
