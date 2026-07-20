# Experiment Report: Per-Role Motion — the DR 0015 WATCH Seam's Named Increment Lands (Cycle 19 · SHARED · I4)

Date: 2026-07-20

## WHY

DR 0015 recorded the WATCH item: per-role animation for the ratified
vocabulary's motion roles is "a future T4 increment, recorded not
improvised." The clip model moved antennae/sensors (sway) and effects
(flicker); limb, joint, and decoration cells — the locomotion and
ornament vocabulary DR 0011 ratified and the exemplar corpus proves —
only ever moved with the whole body. The clip lab's own blocked state
named it: `per_role_motion_for_limb_joint_decoration_unrecorded`.

The game stake is direct: the engine's clip frames ARE the game's
sprites (the same grid truth renders the pixel assets). Creatures
with legs that never stepped read as stickers; after this increment
the locomotion vocabulary visibly walks, flexes, and shimmers
wherever clips play — hatchery, eras, the workshop timeline, APNG and
spritesheet exports.

## WHAT

**The recorded semantics (DR 0037), both parity sites verbatim:**
limbs step VERTICALLY and joints flex HORIZONTALLY under the
column-parity sign rule (even column +, odd column − — opposite legs
alternate; left/right pivots counter-flex); decoration bobs
vertically in unison. Amplitudes are the LCD unit step (1px) at every
canvas; frame 0 stays the identity; every offset keeps the standard
collision/bounds skip; application order body → sway → limb → joint →
decoration → flicker. ADDITIVE: role-free grids produce byte-identical
frames (pinned on the drone seed).

**The pins make the honesty visible on the exemplar's own geometry**:
the boxed upper limbs and the shell-blocked step SKIP (pinned
exactly — only the free limb steps); the blocked decoration bob on
idle frame 3 skips while frame 1's free bob lands; relocated joints
flex crisply in open space.

**Gates over the full corpus** (`clip_model_stage0.json`
regenerated): frames in-bounds **1.0**, palette-clean **1.0**, genome
untouched **1.0**; every clip still moves (ill delta 0.79, beg 0.29,
idle 0.064 — the idle life now includes the decoration shimmer). The
C2 transition graph holds at **0.9831 vs the 0.8 bar** over the
richer frames; animstate_950 regenerates as the frames' current
truth. **Workshop 83 green untouched** — the H3 timeline, onion skin,
and clip exports consume the new motion with zero workshop changes
(the additive promise honored at the consuming surface).

## Verification

```powershell
PS> python -B -m unittest discover -s labs/animation_system -p "test_clip_model.py"
ImportError: cannot import name 'CLIP_DECOR_BOB' from 'clip_model'
FAILED (errors=1)                          # RED: the tables absent
# after the lab implementation:
Ran 15 tests ... OK
# the parity discipline working — the package not yet mirrored:
PS> python -B -m unittest discover -s labs/animation_system -p "test_package_clip_parity.py"
Ran 7 tests ... FAILED (failures=60)
# after the verbatim package mirror:
PS> python -B -m unittest discover -s labs/animation_system -p "test_*.py"
Ran 38 tests ... OK
PS> python -B -m unittest discover -s packages/mecha_engine/tests -p "test_*.py"
Ran 295 tests ... OK
PS> python -B -m unittest discover -s workshop/tests -p "test_*.py"
Ran 83 tests ... OK
```

## HONEST REMAINDER

1. **Per-clip choreography beyond the recorded tables** is the
   sharper named remainder (the clip lab's new blocked state): five
   clips × three tables is the recorded vocabulary; richer
   choreography (per-species gaits, walk cycles as their own clips)
   is an engine DR when a consumer asks.
2. **The exemplar is the only committed grid exercising all three
   roles together** — the drift guard
   (`test_vocabulary_exemplars.py`) keeps the vocabulary alive, and
   the generation surfaces still rarely emit limbs/joints (the I5b
   descriptor-range finding is the same fact from the archive side).
3. **Two boxed exemplar limbs never move** (their step targets are
   shell/limb-occupied) — the collision skip working as recorded, and
   a fact for any future exemplar authoring.

## Sources

- `audits/TODO.md` (cycle 19 I4)
- `research/decision_records/0037-per-role-motion.md` (the recorded semantics), `0015-dormant-vocabulary-coverage.md` (the WATCH charter)
- `labs/animation_system/clip_model.py` (+ `test_clip_model.py`, `test_package_clip_parity.py`)
- `packages/mecha_engine/src/mecha_engine/genome/animation.py` (the parity mirror)
- `data/animation_system/clip_model_stage0.json`, `transition_graph_stage0.json`, `animstate_950.json` (regenerated)
- `research/experiment_reports/2026-07-08-clip-model.md` (C1 — the model this extends)
