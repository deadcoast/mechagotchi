# Experiment Report: The Transition Graph Holds at 98.8% (Cycle 11 · ENGINE · C2)

Date: 2026-07-08

## WHY

The dossier's animation gate: transition validity ≥80%. C1 gave clips
their frames and a measured intra-clip delta table; C2 defines which
clip may follow which and measures whether the cuts read as continuous.

## WHAT

`labs/animation_system/transition_graph.py` (RED-first; the animation
suite is now 16 tests): a hub-and-spoke graph — `idle` is the resting
hub, every state clip enters from and returns to it, `blink` is idle's
micro-interruption, and every clip carries a self-loop (a clip that
cannot loop cleanly cannot play). The validity metric was
PRE-REGISTERED: a transition a→b is valid for a creature when its
boundary delta (last frame of a → first frame of b, C1's exact
`_frame_delta`) is no larger than the jerkiest step already inside
either clip for that creature — the cut may not be jerkier than the
animation itself; near-static clips fall back to the corpus-wide
intra-max, never a free pass.

## FINDINGS (50 creatures × 13 edges = 650 measured transitions)

- **Transition validity 0.9877 ≥ 0.80** — the dossier bar holds with
  headroom. Eleven of thirteen edges are perfect (1.0).
- The only imperfect edges are `idle→ill` and `ill→idle` at **0.92**:
  illness onset and recovery are the jerkiest cuts (ill's shiver is the
  most violent clip, intra-max 0.967) — for four creatures the cut
  exceeds even that. Honest reading: sensible biology, recorded per
  edge, and exactly the kind of boundary a game client can soften with
  an interstitial idle frame if a polish pass ever wants to.
- Boundary deltas: p50 0.029 (most cuts are nearly seamless), p95
  0.841, max 0.967.

## Verification

```powershell
PS> python -B -m unittest discover -s labs/animation_system -p "test_*.py"
Ran 16 tests in 10.969s
OK
PS> python -B labs/animation_system/transition_graph.py
Transition validity 0.9877 against the >= 0.8 bar: the graph holds.
```

## Sources

- `labs/animation_system/transition_graph.py` (+ `test_transition_graph.py`)
- `data/animation_system/transition_graph_stage0.json`
- `labs/animation_system/clip_model.py` (C1, the delta metric and clips)
- `docs/project-research/deep-research/01/deep-research.md` (the ≥80% bar)
- `audits/TODO.md` (cycle 11 C2), `docs/gap-analysis.md` (Phase C)
