# Decision Record 0026: The `render` Module — Disposition (D3)

Date: 2026-07-07

## Status

**Accepted** (cycle 04 D3). `render` has been a deferred
`mecha_engine` module target since the scaffold (DR 0004), with the
standing escape clause "if workshop slices need them promoted, each
takes its own decision record" (DR 0010; reaffirmed DR 0006, DR 0022).
This record applies the DR 0024 disposition method — supersede-or-
reject each candidate surface, with a named re-opener — and resolves
render: the renderer-neutral contract already ships in
`mecha_engine.genome`; a `mecha_engine.render` DRAWING module is
REJECTED-until-consumer.

## The render surfaces, field by field

| Candidate surface | Disposition | Where it lives now |
| --- | --- | --- |
| `render_packet_from_grid(grid, state=None) -> dict` | **SHIPPED verbatim** | `mecha_engine.genome.render` — the renderer-neutral packet (grid_id, grid_size, palette, cells, state); validated, deep-copied, JSON-serializable; explicitly "must not own frontend rendering" |
| `render_packet_v2(grid, lifecycle_state=None, *, animation=None)` | **SHIPPED verbatim** | `mecha_engine.genome.animation` (DR 0013 port of the T16 packet-v2; adds animation/mood/vocabulary keys) |
| the SLIP-vocab-gated `build_render_packet_v2(..., slip_profile=)` | **SUPERSEDED** (Decision 1) | an ANIMATION-SELECTION concern, not a drawing one — it lives in `labs/grid_genome/animation_states.py` with a package parity pin; its home is `genome`, not a render module (the workshop calls the lab version only for the covenant vocab gate) |
| a `mecha_engine.render` DRAWING/rasterizer module | **REJECTED-until-consumer** (Decision 2) | nowhere — the only pixel-drawing code is browser JS in the workshop HTML pages |

## Decision 1 — the packet contract is already promoted; no new module holds it

The renderer-neutral data boundary the og design wanted — a validated,
JSON-serializable packet every renderer consumes — ships inside
`mecha_engine.genome` (`render_packet_from_grid` + `render_packet_v2`),
consumed by the workshop server, `labs/runtime_integration`, and
`labs/game_loop/replay_recorder`. There is nothing a `mecha_engine.
render` module would hold that is not already promoted. The one genuine
gap (the workshop's live preview calls the LAB `build_render_packet_v2`
because only it carries the `visual_grammar.animation_vocab` gate) is an
animation-selection concern whose home is `genome` — closing it is a
`genome` follow-up (port the `slip_profile` gate into
`render_packet_v2`), NOT a render-module promotion.

## Decision 2 — a drawing module is REJECTED with a re-opener

The actual rendering — turning a packet into pixels — is entirely
browser-side JavaScript (`drawPacket` in `workshop/preview/preview.html`,
`drawReplayPacket` in `workshop/session/session.html`, `draw` in the
grid editor). That code is inherently non-portable to a Python package,
and there is NO Python consumer that needs to rasterize a packet. A
`mecha_engine.render` module today would be an empty target with no
verbatim-portable source and no caller — rejected under the same rule
DR 0011/0024 used for decorative surfaces: a promoted module must have a
real consumer and portable semantics, and render has neither.

**Designated re-opener**: a NON-workshop Python consumer needs to
rasterize a packet — e.g. server-side PNG/APNG export from the engine
without the browser, a headless renderer for automated visual
regression, or a `mechas` command that renders a creature to an image
file. At that point the drawing logic earns a portable Python home and a
`mecha_engine.render` decision record cites this one plus the task that
introduces the consumer. (The workshop's PNG/APNG export codecs already
live in `labs/workshop_editor/` and serve the workshop; they are not
that consumer until something outside the served-page stack needs them.)

## A recorded cleanup (workshop track, not this record)

The survey found the three canvas draw loops (`drawPacket`,
`drawReplayPacket`, the editor's `draw`) are DUPLICATED inline JS with
no shared asset. De-duplicating them into a shared workshop script is a
real, worthwhile workshop-track cleanup (DR 0010's stack) — recorded
here so it is not lost, but explicitly OUT of scope for the module
disposition.

## Consequences

- `render` stays a deferred module target, now with an explicit
  disposition and re-opener rather than a bare deferral; `slip` remains
  the other deferred target (its own future record).
- A `genome` follow-up is identified (the `slip_profile` animation-vocab
  gate into `render_packet_v2`) and a workshop-track cleanup (shared
  draw asset) is recorded — neither blocks anything.

## Sources

- `research/decision_records/0004-mecha-engine-package-scaffold.md` (the deferral)
- `research/decision_records/0010-start-mecha-workshop-build-track.md` (the escape clause)
- `research/decision_records/0013-port-slip-v2-and-packet-v2.md` (packet-v2 into `genome`)
- `research/decision_records/0024-grid-schema-animation-species-resolution.md` (the disposition method)
- `packages/mecha_engine/src/mecha_engine/genome/render.py` + `animation.py`
- `labs/grid_genome/animation_states.py` (+ the package parity pin)
- `workshop/preview/preview.html`, `workshop/session/session.html`, `workshop/grid_editor/grid_editor.html` (the JS draw loops)
- `research/package_specs/mecha_engine_genome_contract_gate.md`
