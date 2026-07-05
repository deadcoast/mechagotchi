# SLIP Readability Calibration Reviewer Packet

Open `slip_readability_calibration_rating_tool.html` (this folder) in a browser — it renders every sample as pixel art, collects the five ratings per sample per reviewer, and exports the filled CSV. Rate before looking at proxy readability values; use independent reviewer IDs, one row per sample per reviewer. (The raw `slip_readability_calibration_template.csv` remains the canonical column contract if you prefer to fill it by hand.)

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
