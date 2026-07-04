# Mechagotchi Research Report v0.8

Date: 2026-07-04

## Executive Summary

The post-v0.7 close-out consolidates the three remediation reports that
resolved the items v0.7 explicitly left open: the dependency-manifest
decision (M-15 remainder), the grayscale/deep-color foreign-fixture coverage
gap, and the degenerate descriptor axes (L-12). With this wave, every
finding in `docs/03-code_review/2026-07-04-code_review.md` is resolved or
closed-verified; the full sweep is 474 tests across 12 labs, all green.

Three results of independent interest:

1. **Decision record 0005** declares a pyproject `lab` dependency group
   (pydantic, jsonschema) while keeping the *package* dependency policy
   blocked — and the architecture runtime-boundary gate now measures that
   distinction from real pyproject inspection instead of assuming it.
   Lab-level runtime JSON Schema validation is unblocked with parity
   evidence: 17/18 corpus agreements, the single divergence being the
   documented body-mass semantic gap that layered validation retains.
2. **The deep-color decoders survived independent input.** Five foreign
   fixtures (gray 8/16-bit, RGBA 16-bit, incl. multi-IDAT non-zero-filter
   and Adam7 16-bit) decode pixel-exact against an independent spec-derived
   encoder; the 22 × 10 fixture/decoder sweep produced zero raw exceptions
   and zero wrong-pixel outcomes.
3. **All seven descriptor axes now differentiate niches** (spread ≥ 2):
   per-candidate mutation temperature within SLIP caps (spread 5) and a
   morphology-derived lifecycle stress probe (spread 2). The archive grew
   from 33 to 83 occupied niches (QD 31.62 → 72.07). The honest finding
   behind the survival axis: the switchboard lifecycle is bistable (stress
   ≤ 0.94 stabilizes forever; ≥ 0.95 collapses at tick 12–14), so
   intermediate survival bins await a harsher lifecycle model — recorded,
   not forced past.

Every proof remains a Stage 0 lab proof. There is still no
`packages/mecha_engine` code, no package dependency policy, no manual
readability calibration, and no profile-weighted evolution claim.

This report consolidates and links the underlying experiment reports; it
does not replace them.

## Consolidated Reports

1. `research/experiment_reports/2026-07-04-lab-dependency-manifest-and-jsonschema-parity.md`
   — decision record 0005; `pyproject.toml` lab group; parity lab
   (`labs/slip_validator/jsonschema_runtime_parity.py`); gates re-scoped to
   lab vs package; stale `declared_dependency_manifest` blockers retired.
2. `research/experiment_reports/2026-07-04-deep-color-foreign-fixtures.md`
   — corpus 17 → 22 fixtures; conformance module 29 → 40 tests; remaining
   out-of-scope recorded in the manifest `coverage_notes` (indexed/type-2/
   type-4 color, low-bit gray, 16-bit APNG frame data).
3. `research/experiment_reports/2026-07-04-descriptor-axis-calibration.md`
   — mutation temperature + cap-normalized stability; lifecycle stress
   probe; 550 grids regenerated deterministically, all validating and
   SLIP-aligned; downstream workshop SLIP gate artifacts rebuilt.

## Decisions

- Adopt layered runtime schema validation for labs (schema layer +
  retained semantic checks); package-level validation stays blocked and is
  now measured.
- Adopt the calibrated descriptor set; any future axis must show
  `descriptor_bin_spread` ≥ 2 before its niche contribution is claimed.
- Keep the foreign-fixture corpus as the conformance bar for new decoder
  claims; extend it rather than relying on encoder round-trips.

## Blocked / Open

- Package dependency policy, package import surface, package runtime
  lifecycle integration (unchanged; awaiting `packages/`).
- Manual readability calibration (0 of 63 reviewer rows collected).
- Harsher lifecycle model for intermediate survival bins (bistability
  finding).
- Foreign-fixture out-of-scope list per the corpus manifest.

## Publication Status

Published internally as the v0.8 wrap-up of the 2026-07-04 code-review
remediation. Sources and metrics in
`research/reports/research_report_v0_8_manifest.json`.

## Sources

- `docs/03-code_review/2026-07-04-code_review.md`
- `research/reports/mechagotchi_research_report_v0_7.md`
- `research/reports/research_report_v0_7_manifest.json`
- `research/decision_records/0005-declare-lab-dependency-manifest.md`
- `research/experiment_reports/2026-07-04-lab-dependency-manifest-and-jsonschema-parity.md`
- `research/experiment_reports/2026-07-04-deep-color-foreign-fixtures.md`
- `research/experiment_reports/2026-07-04-descriptor-axis-calibration.md`
