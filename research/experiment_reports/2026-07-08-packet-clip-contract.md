# Experiment Report: The Packet Carries the Clip Contract (Cycle 11 · ENGINE · C4)

Date: 2026-07-08

## WHY

The dossier's render-packet example carries
`"animation": {"clip": "idle_blink", "frame_index": 2, "anchors": [...]}`
— the contract the game's client (Phase F) will consume. The packet's
`animation` field was a state STRING; the clip system (C1–C3) existed
only lab-side.

## WHAT

RED-first (7 new pins in `test_package_clip_parity.py`):

1. **The clip model promoted** into `mecha_engine.genome.animation` — a
   verbatim port of the lab (tables, motion rules, error strings),
   pinned frame-for-frame over corpus samples; new genome publics
   `CLIP_STATES`, `clip_names`, `clip_frame_count`, `clip_frame`.
2. **`render_packet_v2` gains `clip`/`frame_index`** as a DR 0013
   additive rung: when a clip is requested the packet's `animation`
   field becomes the documented BLOCK
   (`clip`/`frame_index`/`frame_count`/`anchors`) and the packet's
   cells are the clip FRAME's cells. Validation stays on the projected
   grid (positions preserved); the moved frame is presentation applied
   after the v1 gate. Clip names are the state names, so the SLIP
   `animation_vocab` gate bounds clips exactly as it bounds states —
   an out-of-vocab clip displays the idle clip while mood stays honest.
   `clip=None` is byte-identical to the pre-C4 contract — proven by the
   pre-existing animation parity suite passing unmodified.
3. **The workshop scrubs a real clip end-to-end**: `POST
   /api/preview/clip` returns every frame of a clip through the
   promoted rung; the test scrubs the beetle's `ill` clip (four frames,
   each carrying the documented block, visibly moving) and pins the
   loud rejection of unknown clips.

## Verification

```powershell
PS> python -B -m unittest discover -s labs/animation_system -p "test_*.py"
Ran 28 tests in 9.673s
OK
PS> python -B -m unittest discover -s labs/grid_genome -p "test_package_animation_parity.py"
Ran 11 tests in 0.036s
OK   # the clip=None byte-identity proof
PS> python -B -m unittest discover -s packages/mecha_engine/tests -p "test_*.py"
Ran 291 tests in 8.771s
OK
PS> python -B -m unittest discover -s workshop/tests -p "test_*.py"
Ran 59 tests in 107.258s
OK
```

## Sources

- `packages/mecha_engine/src/mecha_engine/genome/animation.py` (+ `__init__.py`)
- `labs/animation_system/test_package_clip_parity.py` (the parity + rung pins)
- `workshop/server/workshop_server.py` (+ `workshop/tests/test_workshop_server.py`)
- `labs/animation_system/clip_model.py` (the verbatim source)
- `research/decision_records/0013` (the rung pattern), `0024`
- `docs/project-research/deep-research/01/deep-research.md` (the packet example)
- `audits/TODO.md` (cycle 11 C4), `docs/gap-analysis.md` (Phase C)
