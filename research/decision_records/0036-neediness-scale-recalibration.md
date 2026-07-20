# Decision Record 0036: The behavior_neediness Reference-Canvas Recalibration

Date: 2026-07-20

## Status

**Accepted** (cycle 19 · Phase I, task I5). Authorizes the ONE
formula change at both parity sites — the lab's extended descriptors
and the promoted package's archive metrics — under the measured
evidence of `labs/map_elites_archive/neediness_scale16.py`.

## Context

The Phase-E gate (2026-07-09) named the remainder honestly:
**behavior_neediness is mass-dominated at 16×16** — "a recalibration
candidate with its own evidence." The formula

```text
neediness = clamp(0.35 + sensor_count * 0.08 - body_mass * 0.01 [+ SLIP prior shift])
```

was calibrated against 8×8 masses (~6–16 core cells). 16×16 masses
are ~4× larger, so the mass term swamps the sensor signal: the
descriptor axis stops measuring behavior and starts mirroring mass —
the same failure shape cycle 09 A4 fixed for the mass BIN EDGES with
reference-canvas scaling (an exact identity at 8×8).

The measurement (both committed seed corpora, the engine's own
numbers — `data/archives/neediness_scale16_stage0.json`):

| | 8×8 (reference) | 16×16 original | 16×16 recalibrated |
| --- | --- | --- | --- |
| pearson(neediness, mass) | −0.703 | **−0.726** | −0.407 |
| pearson(neediness, sensors) | +0.870 | +0.530 | **+0.904** |
| value floor | 0.37 | **0.00 (clamp floor)** | 0.298 |
| distinct values | 5 | 18 | 37 |

At the reference canvas the sensor signal LEADS (|0.870| > |0.703|);
unscaled at 16×16 that inverts (mass dominates); recalibrated, the
reference structure returns.

## Decision

Scale the mass term to the 8×8 reference canvas at BOTH parity sites:

```text
neediness = clamp(0.35 + sensor_count * 0.08 - body_mass * 0.01 * (64 / area) [+ prior shift])
```

- `labs/map_elites_archive/extended_descriptors.py` (`_behavior_neediness`)
- `packages/mecha_engine/src/mecha_engine/archive/_metrics.py` (`behavior_neediness`)

Pre-registered gates, all MET: **identity_8x8** (max abs diff 0.0
over the 8×8 corpus — every historical 8×8 artifact and pin
untouched, verified byte-identical on regeneration of
`map_elites_extended_stage0.json`), **mass_domination_reduced**
(|−0.407| < |−0.726|), **sensor_signal_present** (+0.904 > 0). The
measurement lab freezes the ORIGINAL formula verbatim so the evidence
keeps meaning what it measured, and self-checks that both live sites
carry the recalibration.

## Consequences

- **The 512-niche geometry un-degenerates**: regenerating
  `niche_scale_archive_stage0.json` moves distinct neediness octile
  edges 6 → 7 of 7 (`supports_full_bins: true` — 8 bins need exactly
  7 edges, so the axis now supports the FULL documented geometry) and
  REMOVES the recorded degeneracy note.
- **Measured coverage effect**: 274 → 319 of 512 niches occupied
  (0.535 → 0.623) over the same 3,000 candidates — the Phase-E
  occupancy plateau was partly the collapsed axis wasting a
  descriptor dimension. The occupancy-saturation remainder is
  NARROWED, not closed: the plateau question (what bounds coverage
  past ~62%) stays open with its named candidates (novelty pressure,
  re-derived edges, mutation-heavy arms).
- 16×16-dependent archive artifacts regenerate with this record;
  8×8-era artifacts are unchanged by the identity.
- The game's evolution surfaces consume the archive through the
  package — richer niche coverage at 16×16 is player-visible variety
  (more distinct creatures survive archiving), which is the
  engine+game duality's point (DR 0017).

## Sources

- `labs/map_elites_archive/neediness_scale16.py` (+ `test_neediness_scale16.py`)
- `data/archives/neediness_scale16_stage0.json` (the measurement)
- `data/archives/niche_scale_archive_stage0.json` (the regenerated geometry)
- `research/experiment_reports/2026-07-09-phase-e-gate.md` (the named remainder)
- `research/decision_records/0029-16x16-default-grid-scale.md`, `0030-slip-size-relative-mass-bounds.md` (the cycle 09 reference-canvas precedent)
