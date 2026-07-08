# Experiment Report: The Phase-C Gate — the Animation System Exists (Cycle 11 · ENGINE · C6)

Date: 2026-07-08

## WHY

The gap table's animation row: the documents specify clips with frames,
anchors, transition validity ≥80%, `animstate_300`, the packet's
`clip`/`frame_index` contract, and the retro effects pipeline — what
existed was five single-frame color projections and a pulse frame for
APNG export. Phase C's charter: build the animation SYSTEM, the
render-bridge contract Phase F's game client will consume.

## THE GATE

| Task | Result | Evidence |
| --- | --- | --- |
| **C1 · the clip model** | Clips as bounded frame sequences over the promoted projections (state track → all-or-nothing body motion → per-role motion, the DR 0015 seam recorded per role). 950/950 corpus frames in-bounds, palette-clean, genome-untouched; every clip moves; idle frame 0 is the identity; proven at both ratified scales | `2026-07-08-clip-model.md` |
| **C2 · transitions** | Hub-and-spoke graph with mandatory self-loops; PRE-REGISTERED metric (a cut may not be jerkier than the animation itself). **Validity 0.9877 ≥ 0.80** over 650 transitions; only idle↔ill imperfect at 0.92 (illness is the jerkiest cut — sensible biology, per-edge recorded) | `2026-07-08-transition-graph.md` |
| **C3 · the dataset** | `animstate_950`: 950 labeled (grid, palette, clip, state, frame) samples, full coverage, named by its real size with the documented `animstate_300` recorded as superseded (og kept as history) | `2026-07-08-animstate-950.md` |
| **C4 · the packet contract** | The clip model promoted verbatim into `mecha_engine.genome` (frame-for-frame parity); `render_packet_v2` carries the dossier's `animation` block as a DR 0013 additive rung (`clip=None` byte-identical, proven by the untouched parity suite); the workshop scrubs a real clip end-to-end | `2026-07-08-packet-clip-contract.md` |
| **C5 · effects + ui_hints** | The documented effects list + deterministic `effect_parameters` (glitch amplitude IS the engine's stress; bloom rides beg; scanline/ghosting the LCD identity) + threshold-mirroring `ui_hints`, on every v2 packet in verbatim twins; the shared drawer rasterizes the declared effects | `2026-07-08-effects-contract.md` |
| **C6 · sweep** | 18 labs green (animation_system 33 joined), package 291, workshop 60, CLI 21 | this report |

## HONEST REMAINDER

1. **Per-role motion for limb/joint/decoration** — the DR 0015 seam's
   named next increment (antenna/sensor/effect move today).
2. **`lcd_ghosting` rasterization** needs temporal state — a live-player
   concern for Phase F's client; declared in every packet, honestly
   skipped by the static drawer.
3. **Live clip DRIVING**: the transition graph exists and the packet
   carries clips, but the companion/session tick still selects single
   STATES — the client-side play loop that walks the graph frame by
   frame is Phase F's consumption of this contract.
4. **The animation-preference learner** consuming `animstate_950` is
   Phase D's charter (the documented bandit).
5. **APNG/spritesheet exports** still emit the historical pulse frame,
   not clip frames — a workshop-track increment when the authoring
   surface wants it, named not smuggled.

## VERDICT

**Phase C is green.** Creatures have clips, transitions measured above
the documented bar, a real dataset, and a packet contract with effects
that any client can rasterize — the render bridge Phase F consumes.
Cycle 11 is complete; cycle 12 opens Phase D from the gap analysis:
the intelligence threads — the owner's core ML thesis, ~2 of ~11
threads existing today — with the synthetic user models, the
100k-tick × 500-lifecycle harness, and the documented ablation gates.

## Verification

```powershell
PS> # the closing sweep (2026-07-08)
animation_system 33 · architecture 14 · asset_pipeline 22 ·
cellular_automata 37 · ctm_ticks 4 · cubff_transducer 17 · datasets 22 ·
game_loop 83 · grid_genome 209 · lifecycle_sim 24 · map_elites_archive 35 ·
package_promotion 6 · readability_benchmark 42 · repair_boundary 4 ·
runtime_integration 65 · slip_validator 24 · wfc_grid 20 ·
workshop_editor 307 — all OK
package 291 OK · workshop 60 OK · CLI 21 OK
```

## Sources

- `docs/gap-analysis.md` (Phase C), `audits/TODO.md` (cycle 11)
- The five C-task reports (2026-07-08): `clip-model`, `transition-graph`, `animstate-950`, `packet-clip-contract`, `effects-contract`
- `labs/animation_system/`, `packages/mecha_engine/src/mecha_engine/genome/animation.py`, `workshop/shared/draw.js`
- `data/animation_system/`
