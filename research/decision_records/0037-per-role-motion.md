# Decision Record 0037: Per-Role Motion — Limb, Joint, Decoration

Date: 2026-07-20

## Status

**Accepted** (cycle 19 · Phase I, task I4). Executes DR 0015's WATCH
item ("per-role animation … a future T4 increment, recorded not
improvised") for the three roles the clip model did not yet move.

## Context

The clip model (C1, promoted through the C4/H3 packet and export
rungs) moves antennae/sensors (sway) and effects (flicker); DR 0015's
exemplar corpus proves limb/joint/decoration cells exist and render,
but they only ever moved with the whole body. The clip lab's own
blocked state named the gap:
`per_role_motion_for_limb_joint_decoration_unrecorded`.

## Decision

Three recorded per-clip offset tables, mirrored verbatim at both
parity sites (`labs/animation_system/clip_model.py` and
`mecha_engine.genome.animation`), applied after body motion and sway,
before flicker, each per-cell with the standard collision/bounds skip:

- **Limbs step VERTICALLY** (`CLIP_LIMB_STEP`) with the
  **column-parity sign rule** — even column `+offset`, odd column
  `−offset`: opposite legs alternate, the gait read of the
  locomotion vocabulary (DR 0011).
- **Joints flex HORIZONTALLY** (`CLIP_JOINT_FLEX`) with the same
  parity rule — left/right pivots counter-flex.
- **Decoration bobs vertically in unison** (`CLIP_DECOR_BOB`) — no
  parity flip; ornaments shimmer together.

Amplitudes are the LCD unit step (1px) at EVERY canvas — the same
size-parametric grammar as the whole-body bob (proven over the 8×8
exemplar and both seed corpora); frame 0 of every table is 0 (frame
zero stays the identity). Idle gains decoration bob only (the still
body keeps its stillness; the ornament gives idle life). The
increment is ADDITIVE: grids without the three roles produce
byte-identical frames (pinned).

## Consequences

- The clip lab's named remainder closes; the sharper remainder is
  per-clip CHOREOGRAPHY beyond the recorded tables (a future engine
  DR when a consumer asks).
- The C2/C3 artifacts regenerate under the richer frames (transition
  validity holds at 0.98 vs the 0.8 bar); the workshop's H3 timeline,
  onion skin, and clip exports consume the new motion UNTOUCHED
  (workshop 83 green) — authoring a limb/joint/decoration cell and
  scrubbing the timeline now shows the engine's own gait/flex/bob.
- For the game: the same clip frames are the game's sprites — 
  creatures with the DR 0011 locomotion vocabulary now visibly walk,
  flex, and shimmer wherever clips play (hatchery, eras, exports).

## Sources

- `research/decision_records/0015-dormant-vocabulary-coverage.md` (the WATCH charter), `0011-run-one-run-two-reconciliation.md`
- `labs/animation_system/clip_model.py` (+ `test_clip_model.py`, `test_package_clip_parity.py`)
- `packages/mecha_engine/src/mecha_engine/genome/animation.py`
- `data/animation_system/clip_model_stage0.json`, `data/vocabulary_exemplars/`
- `research/experiment_reports/2026-07-20-per-role-motion.md`
