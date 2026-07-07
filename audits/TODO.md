# Development TODO — Cycle 05: consumers and cleanups, the seams cycle 04 named

Source: the follow-ups cycle 04 recorded (DR 0026's genome + workshop
notes), the last deferred module target, and the R6 datasets that were
built as "the ML tracks' fuel" but nothing burns yet. Cycle 04 is
archived complete at `audits/complete/04/` (D2 mortal-wound signal, D3
render disposition, D5 campaign soak; D1/D4 closed by owner decision —
synthetic weather is the shipped answer, no external dependency).
Governing rule unchanged: deep integrations over breadth — the
ENGINE+GAME duality (DR 0017); hard/unique features win over
easy/generic ones, said aloud. A task is complete when developed to its
description, then marked. Development proceeds continuously through this
TODO's tasks; planning is triggered ONLY when the TODO is exhausted of
its tasks and confirmed COMPLETE — then the next cycle is planned.
(Decision records remain the design documentation for tasks that need
them; they do not pause the queue.)

- [ ] **E1 · Port the SLIP animation-vocab gate into
  `genome.render_packet_v2`.** (DR 0026's identified `genome`
  follow-up.) The workshop's live preview still calls the LAB
  `build_render_packet_v2` because only it carries the
  `visual_grammar.animation_vocab` gate (packet selection outside the
  species' vocabulary falls back to a displayed idle while mood stays
  honest). Port that `slip_profile` gate into the promoted
  `mecha_engine.genome.render_packet_v2` verbatim (additive keyword,
  default byte-identical), add the contract test + lab-side parity
  pin/drift guard, then switch the workshop server to the package
  version — closing the last place a shipped surface depends on a lab.
- [ ] **E2 · Shared workshop draw asset.** (DR 0026/0010's workshop
  cleanup.) The three canvas draw loops (`drawPacket` in preview,
  `drawReplayPacket` in session, the editor's `draw`) are duplicated
  inline JS. Extract one shared, served `.js` drawing helper the pages
  import — de-duplication only, pixel output byte-identical, an
  endpoint/DOM test proving each page still renders.
- [ ] **E3 · The datasets become ML fuel (R6's consumers).** R6 built
  `mechaseed_200`, `mutationbench_5000`, `replay_100k_ticks` as "the ML
  tracks' fuel" — nothing consumes them yet. Wire real consumers: (a)
  evaluate the R3 learned-readability model on `mutationbench_5000`'s
  REAL generated offspring (does a model trained on synthetic
  degradation pairs rank real mutation outcomes? measured, honest
  either way); (b) a behaviour/switchboard evaluation over
  `replay_100k_ticks`. Deep integration — the fuel finally burns.
  Triad; verdict recorded, not asserted.
- [ ] **E4 · `slip` module disposition.** (The last deferred module
  target; DR 0004's list, now that `render` is dispositioned by DR
  0026.) Apply the DR 0024/0026 method: the SLIP validators, the
  schema ladder, and `visual_grammar` ship as lab + package `_slip`
  mirrors across four surfaces — decide whether a promoted
  `mecha_engine.slip` earns its target now (a real consumer, verbatim-
  portable) or stays deferred with a named re-opener.
- [ ] **E5 · The five player-NOTICES audit (DR 0021 a.4).** DR 0021
  named five felt phenomena, each mapped to a shipped mechanism
  (weather changes the world; creatures visibly think; the species
  becomes easier to read; your creature's blood persists; absence
  hurts). Audit each against what actually ships NOW after cycles
  02–04 — is every notice reachable and player-visible at a real
  surface? Close any gap found, or record it honestly as the next
  cycle's seed. The living-ecosystem claim, verified end to end.

## Standing note

The identity constraint and DR 0017 govern: the engine is the
application, the game is its showcase. The rating system is the
fallback; `.depreciated/` is the owner's archive (ignore unless
linked). Real-CuBFF ingest is closed by owner decision (cycle 04):
the synthetic weather is the shipped answer, nothing external is
required, and the real-export ingest stays an optional drop-in seam.
`slip` is the last deferred module target (E4); `render` was
dispositioned by DR 0026.

## Sources

- `audits/complete/04/TODO.md` (cycle 04, complete)
- `research/decision_records/0017-recalibration-engine-game-duality.md`
- `research/decision_records/0026-render-module-disposition.md` (E1/E2 named)
- `research/decision_records/0013-port-slip-v2-and-packet-v2.md` (the packet-v2 port pattern for E1)
- `research/experiment_reports/2026-07-07-dataset-program.md` (E3's fuel)
- `research/decision_records/0019-learned-readability.md` (E3's model)
- `research/decision_records/0024-grid-schema-animation-species-resolution.md` (E4's disposition method)
- `research/decision_records/0021-game-loop.md` (E5's five notices)
