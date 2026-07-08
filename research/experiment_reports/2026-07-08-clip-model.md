# Experiment Report: The Clip Model — Animation Gains Time (Cycle 11 · ENGINE · C1)

Date: 2026-07-08

## WHY

The gap table's animation row: the documents specify clips with frames,
anchors, transition validity ≥80%, `animstate_300`, and a packet
carrying `clip`/`frame_index` — what exists is five single-frame color
projections and a pulse frame for APNG export. The animation SYSTEM did
not exist at any scale. Phase C builds it; C1 is the clip model.

## WHAT

`labs/animation_system/clip_model.py` (RED-first, 10 tests): five clips
grounded in the promoted state vocabulary (so SLIP `animation_vocab`
keeps bounding what a species may play), each frame composed as
state-projection → all-or-nothing whole-body motion → per-role motion
(antenna/sensor sway with collision/bounds skips, effect flicker — the
DR 0015 WATCH seam recorded per role; limb/joint/decoration motion is a
NAMED future increment). Frames mirror the render packet's cell shape
plus the dossier's `anchors` list. Hard rules pinned by test: a frame
is a valid render surface (in bounds, palette-clean, no invented cells,
no overlapping positions), the genome is NEVER mutated, idle frame 0 is
the exact identity, and every clip actually moves. Size-parametric:
proven at 16×16 and 8×8.

## FINDINGS (full 16×16 corpus, 50 × 5 clips × 19 frames = 950)

| Gate | Result |
| --- | --- |
| Frames in bounds | 1.0 |
| Frames palette-clean | 1.0 |
| Genome untouched | 1.0 |
| Clips that move (distinct frames) | 5/5 |

Intra-clip frame deltas (fraction of render positions changing between
consecutive frames — C2's transition baseline): idle 0.032, blink
0.045, beg 0.272, sleep 0.320, ill 0.768 (mean 0.305, max 0.967). The
ordering is sensible on its face: idling barely moves, illness is
violent — and C2's transition bar will judge BOUNDARY frames between
clips against exactly this kind of delta.

## Verification

```powershell
PS> python -B -m unittest discover -s labs/animation_system -p "test_*.py"
ModuleNotFoundError: No module named 'clip_model'   # RED
PS> python -B -m unittest discover -s labs/animation_system -p "test_*.py"
Ran 10 tests in 0.895s
OK
PS> python -B labs/animation_system/clip_model.py
"frames_rendered": 950, "frames_in_bounds_rate": 1.0,
"frames_palette_clean_rate": 1.0, "genome_untouched_rate": 1.0
```

## Sources

- `labs/animation_system/clip_model.py`, `labs/animation_system/test_clip_model.py`
- `data/animation_system/clip_model_stage0.json`
- `research/algorithm_cards/clip_model.md`
- `packages/mecha_engine/src/mecha_engine/genome/animation.py` (the promoted projections)
- `research/decision_records/0015` (the WATCH seam), `0024` (schema resolution)
- `audits/TODO.md` (cycle 11 C1), `docs/gap-analysis.md` (Phase C)
