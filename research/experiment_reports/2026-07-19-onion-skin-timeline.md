# Experiment Report: Onion Skin + the Animation Timeline — Clip-Frame Authoring and Exports (Cycle 18 · WORKSHOP · H3)

Date: 2026-07-19

## WHY

The gap table's Workshop row names onion skin and the animation
timeline in the documented editor depth, and the Phase-C gate carried
the named remainder: *"APNG/spritesheet exports still emit the
historical pulse frame, not clip frames — a workshop-track increment
when the authoring surface wants it, named not smuggled."* This is
that increment, named. The design constraint is unchanged: frames are
the ENGINE's projections — derived, never stored; the grid stays the
single truth (DR 0021).

## WHAT

**The timeline scrubs the UNSAVED draft.** `POST /api/preview/clip`
accepts an inline `matrix` (+ `palette_id`, + the trait editor's
`cell_overrides`): the engine judges the draft first (an invalid draft
gets the validator's words, never frames), then every frame comes back
through the promoted `render_packet_v2` rung exactly as the saved-
creature path has since C4. Overrides riding the scrub is the
authoring loop for the motion choices the clip model exposes — paint
an anchor or set an antenna/effect role, Sync, and the engine's own
sway/flicker/anchor answers move in the timeline.

**Exports carry clip frames as an additive rung** (the DR 0013 shape:
no clip, no change). `POST /api/export/{apng,spritesheet}` takes an
optional `clip`; the server projects every frame through
`render_packet_v2` (unknown clips rejected with the engine's verbatim
`unknown clip: …`; a clip on a single-frame kind is refused loudly)
and hands the cells + animation blocks to the codecs. Without `clip`,
the two-frame pulse APNG and the 3-frame spritesheet proof are
untouched (pinned).

**The codec labs gain the carrier**, named not smuggled:
`export_apng_with_sidecar(..., clip_frames=)` and
`export_spritesheet_with_sidecar(..., clip_frames=)` render each
frame's cells full-canvas; the sidecar binding gains
`frame_source: {kind: "clip_frames", clip}` and a per-frame
`animation` block (the dossier's `clip`/`frame_index`/`frame_count`/
`anchors`). The APNG decoder's frame bound relaxes from exactly-two to
**2..16** (`MAX_APNG_FRAMES` — headroom over the documented ≤4-frame
clips, decode still bounded). Consequence handled honestly: the
`apng_dispose_previous` foreign fixture now reaches the per-frame gate
and rejects as `apng_frame_control_unsupported` instead of
`apng_frame_count_unsupported` — the writer's expectation, the
conformance pin, and `data/foreign_fixtures` regenerated; the decoder
limitations text and both algorithm cards updated; the historical
pulse artifacts regenerated with the corrected bound wording.

**The editor grows the animation panel**: clip selector (populated
from the engine's `clips` answer), a frame scrubber, onion skin
(previous frame ghosted 0.25, next 0.12), the engine's anchors drawn
per frame, a stale mark whenever the draft mutates after a sync
(paint / trait edit / resize / load), and an "exports carry this clip"
toggle that adds `clip` to the APNG/spritesheet export payloads.
Clip frames are never persisted — no sidecar change; a release stays
the grid, pinned (H2's law).

## Verification

```powershell
PS> python -B -m unittest test_workshop_server.ClipAuthoringTests   # (from workshop/tests)
Ran 8 tests ... FAILED (failures=6)   # RED: 404 no inline draft, pulse-only exports
PS> python -B -m unittest discover -s labs/workshop_editor -p "test_png_apng_sidecar_decoder.py"
FAILED (errors=3)   # RED: unexpected keyword 'clip_frames'
# after implementation:
PS> python -B -m unittest test_workshop_server.ClipAuthoringTests
Ran 9 tests ... OK
PS> python -B -m unittest discover -s labs/workshop_editor -p "test_*.py"
OK                                     # full codec lab suite incl. conformance
PS> python -B labs/workshop_editor/foreign_fixture_writer.py   # fixtures regenerated
PS> node --check <extracted editor script>
JS SYNTAX OK                           # 850 lines
```

## HONEST REMAINDER

1. **The clip vocabulary is the engine's** — five clips over fixed
   motion tables. The per-creature authorable choices are anchors and
   motion roles (the DR 0015 vocabulary), which the timeline now
   round-trips; per-clip choreography would be an engine increment
   with its own DR, not a workshop drift.
2. **The browser panel is syntax-checked and server-verified, not
   click-tested** — the human-driven session is H5's gate; every
   behavior the panel depends on (inline scrub, overrides, exports)
   is pinned server-side.
3. **PNG/Aseprite stay single-frame** and refuse a clip loudly; an
   Aseprite multi-frame carrier would be its own named increment.
4. The production clip driver takes its frame counts from the
   engine's `clip_frame_count` (app.py); the driver test's injected
   table is arbitrary by design — checked, no discrepancy in truth.

## Sources

- `audits/TODO.md` (cycle 18 H3), the gap table's Workshop row, `research/experiment_reports/2026-07-08-phase-c-gate.md` (remainder 5)
- `workshop/server/workshop_server.py` (`_preview` inline clip path, `_export` clip rung) + `workshop/tests/test_workshop_server.py` (ClipAuthoringTests)
- `labs/workshop_editor/png_apng_sidecar_decoder.py` (`MAX_APNG_FRAMES`, `clip_frames`), `labs/workshop_editor/spritesheet_sidecar_decoder.py` (`clip_frames`, `frame_labels`) + their test files
- `labs/workshop_editor/foreign_fixture_writer.py` + `labs/workshop_editor/test_foreign_fixture_conformance.py` (the dispose-previous family shift) + `data/foreign_fixtures/`
- `workshop/grid_editor/grid_editor.html` (the animation panel)
- `research/algorithm_cards/png_apng_sidecar_decoder.md`, `research/algorithm_cards/png_apng_metadata_carrier_cross_product.md` (bound wording)
- `packages/mecha_engine/src/mecha_engine/genome/animation.py` (the promoted clip model, untouched)
