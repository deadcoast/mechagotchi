# Algorithm Card: Clip Model

## Purpose

The animation SYSTEM's first layer (gap-analysis Phase C): animation
CLIPS — bounded frame sequences with anchors — over the promoted
single-frame state projections, extending the proven thesis (a frame is
a deterministic, visual-only projection; the genome is never touched)
into time.

## Mathematical Basis

`frame(clip, i) = per-role motion(whole-body motion(state_projection(grid, CLIP_STATES[clip][i])))`

- State track per clip (blink = [idle, blink, idle]; sleep sleeps
  throughout) — reusing the promoted `project_animation_state`.
- Whole-body (dx, dy) per frame, ALL-OR-NOTHING: skipped for the frame
  if any cell would leave the canvas (edge creatures breathe in place;
  no deformation, deterministic per creature).
- Per-role motion (the DR 0015 WATCH seam, recorded per role): antenna/
  sensor sway with per-cell collision/bounds skip; effect flicker on
  odd frames. Limb/joint/decoration motion is a NAMED future increment,
  not improvised.
- Frame packets mirror the render packet's cell shape plus the
  dossier's `anchors` list.

## Inputs

- Any valid grid (size-parametric: proven at 16×16 and 8×8)
- The clip vocabulary (one clip per promoted animation state, so SLIP
  `animation_vocab` keeps bounding what a species may play)

## Outputs

- Deterministic frame packets; `data/animation_system/clip_model_stage0.json`

## Strengths

- 950/950 corpus frames in bounds, palette-clean, genome untouched;
  every clip demonstrably moves; idle frame 0 is the exact identity
- The intra-clip delta table (idle 0.032 → ill 0.768) is a measured
  baseline for C2's transition-validity bar

## Weaknesses

- Motion is table-driven and species-uniform — per-species motion
  personality is Phase D territory (the animation-preference learner)
- Frames may hide cells (blink, flicker) but never invent them — glow
  trails, particles, and overlays are renderer-side effects (C5)

## Failure Modes

- A clip whose body motion is always skipped (a canvas-filling
  creature) degrades to its state track — legal, measured by the delta
  table

## Integration Risk

Low until C4 (the packet rung); the lab is presentation-side only.

## License Status

Original stdlib-only code, Apache-2.0.

## Prototype Result

10 tests green; 50 creatures × 5 clips × 19 frames: in-bounds 1.0,
palette-clean 1.0, genome-untouched 1.0, per-clip mean deltas
idle 0.032 / blink 0.045 / beg 0.272 / sleep 0.320 / ill 0.768.

## Decision

**Prototype → transition graph** (C2). Go gate: the dossier's ≥80%
transition validity, operationalized before the run.

## Sources

- `labs/animation_system/clip_model.py` (+ `test_clip_model.py`)
- `data/animation_system/clip_model_stage0.json`
- `research/experiment_reports/2026-07-08-clip-model.md`
- `packages/mecha_engine/src/mecha_engine/genome/animation.py`
- `research/decision_records/0015` (WATCH seam), `0024`
- `audits/TODO.md` (cycle 11 C1), `docs/gap-analysis.md` (Phase C)
