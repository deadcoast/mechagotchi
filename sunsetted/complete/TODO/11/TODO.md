# Development TODO — Cycle 11: ENGINE track · Phase C — the animation system

**Build track: THE ENGINE** (of the two builds — engine and game — per
`docs/gap-analysis.md` §0; the engine completes before the game's
playable front end is built, and no feature in this cycle is "the
application").

Source: `docs/gap-analysis.md` (Phase C), opened by the Phase-B gate
(`research/experiment_reports/2026-07-08-phase-b-gate.md`, cycle 10).
The gap table's animation row: the documents specify animation CLIPS
with frames, anchors, transition validity ≥80%, an `animstate_300`
dataset, and a render packet carrying `clip`/`frame_index` (the
dossier's packet example: `"animation": {"clip": "idle_blink",
"frame_index": 2, "anchors": [...]}`) plus the retro effects pipeline
(scanline, lcd_ghosting, crt_bloom, glitch) and `ui_hints`. What exists
is a single state name and a pulse frame for APNG export — the
animation SYSTEM does not exist at any scale. This is the render-BRIDGE
contract the game's client (Phase F) will consume; DR 0024 governs the
schema side, DR 0015's WATCH verdict on per-role animation is the
recorded seam, and DR 0026's render disposition (packet contract yes,
Python rasterizer no) still stands.

- [x] **C1 · The clip model, proven in a lab.** A deterministic
  clip/frame representation over the 16×16 grid: named clips (idle,
  blink, sleep, eat, hurt — grounded in the animation-state vocabulary
  the engine already gates), each a bounded sequence of frames, each
  frame a deterministic transform of the base grid anchored at the
  animation anchor (per-role motion enters here — DR 0015's WATCH seam:
  antenna twitch, effect pulse — recorded per role, never improvised).
  Hard rule: a frame is a valid render surface, never a mutated genome
  (engine truth — frames are presentation, the genome is untouched).
  Triad + RED-first.
- [x] **C2 · Transition validity ≥80%.** The documented gate: a
  transition graph between clips (which clip may follow which, on what
  state change), with measured transition validity — every
  transition's boundary frames within a bounded cell-delta so motion
  reads as continuous. Measure over the 16×16 corpus; the ≥80% bar is
  the dossier's, the metric operationalization is recorded before the
  run.
- [x] **C3 · `animstate_300` at documented scale.** The dataset the
  documents name: ≥300 labeled (grid, state, clip, frame) samples
  across the corpus and the clip vocabulary — a data product with its
  own README and gates, consumable by Phase D's animation-preference
  learner.
- [x] **C4 · The packet carries the contract.** `render_packet_v2`
  gains the documented `animation` block (`clip`, `frame_index`,
  `anchors`) as an additive rung — byte-identical when no clip is
  requested (DR 0013's rung pattern, DR 0024's resolution); the SLIP
  `animation_vocab` gate keeps bounding what a species may play. The
  workshop preview scrubs a real clip end-to-end.
- [x] **C5 · The retro effects pipeline, contract-side.** The
  documented effects (scanline, lcd_ghosting, crt_bloom, glitch) as
  PACKET-LEVEL declarations with deterministic parameters (the
  renderer-neutral contract — DR 0026: consumers rasterize, the engine
  never does) plus `ui_hints` (need icons, attention ping) driven by
  engine state. One consumer proof in the workshop's canvas drawer.
- [x] **C6 · Phase-C gate + report.** One consolidated report:
  transition-validity table, dataset stats, packet contract proof,
  honest remainder list. Gap-analysis Phase C checked off only when
  this gate is green.

## Standing note

`docs/gap-analysis.md` governs cycle planning until retired (Phase G
alpha). The engine-truth law (DR 0021), the identity constraint, and
the triad discipline are unchanged. CuBFF real ingest is REQUIRED
late-stage (Phase G). Apache-2.0; dependencies permitted with
justification (DR 0028). Size-parametric, never size-replacing (DR
0029). Named Phase-B remainders (evolve's inner loop on WFC; the hybrid
re-opener) wait for their own evidence — do not smuggle them into this
cycle.

## Sources

- `docs/gap-analysis.md` (Phase C)
- `research/experiment_reports/2026-07-08-phase-b-gate.md` (the opener)
- `docs/project-research/deep-research/01/deep-research.md` (the packet example, `animstate_300`, the ≥80% bar)
- `research/decision_records/0013` (rung pattern), `0015` (per-role WATCH seam), `0024` (schema resolution), `0026` (render disposition)
- `labs/grid_genome/animation_states.py` (the vocabulary gate that exists)
