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

- [x] **E1 · Port the SLIP animation-vocab gate into
  `genome.render_packet_v2`.** (2026-07-07: the T3.5
  `visual_grammar.animation_vocab` gate promoted verbatim as a
  keyword-only `slip_profile` on `genome.render_packet_v2` (species
  vocab bounds the packet; unsupported states fall to a DISPLAYED idle
  with honest mood; `None` byte-identical). Parity carve-out closed
  (`SlipVocabGateParityTests`), contract probe added; the workshop
  `/api/preview/render` switched to the promoted surface — nocturne
  renders vocab `[idle,sleep]` end-to-end. The last shipped-surface
  dependency on a lab for packet building is closed; the lab
  `build_render_packet_v2` import is gone from the server.)
- [x] **E2 · Shared workshop draw asset.** (2026-07-07:
  `workshop/shared/draw.js` — one `MechaDraw` with the packet loop
  (damage stroke as an option pinning each page's historical pixels),
  the wound overlay, and the scrubber body-resolution helper; preview
  + session import it, inline duplicates deleted, endpoint tests pin
  the asset + imports + absence of duplicates. Scope correction
  recorded honestly: the grid editor's `draw()` is NOT a duplicate —
  it renders the editing MATRIX (tokens/anchor dot/mouth bar/
  overlays), a distinct authoring surface that stays local, pinned by
  test.)
- [x] **E3 · The datasets become ML fuel (R6's consumers).**
  (2026-07-07, two findings: (a) R3's synthetic-trained model
  GENERALIZES to real mutations — 0.9406 pairwise accuracy on 2,880
  physics-labeled real pairs (0.983 degraded / 0.849 improved; 57.6%
  coverage with the unlabeled remainder reported; all 5,000 signatures
  re-verified in passing). (b) A survivorship-bias catch: the naive
  per-lived-tick mean ranked switchboard LAST; the engine-faithful
  full-horizon statistic (run_episode's own padding rule) flips it —
  switchboard 0.789 at survival 1.00 vs idle 0.121 at survival 0.00,
  all idle creatures starving by tick ~11; both statistics reported,
  the padding math pinned by a hand-computed crafted-corpus test. 10
  new tests; verdicts are the numbers.)
- [x] **E4 · `slip` module disposition.** (DR 0027, 2026-07-07: the
  DR 0024/0026 method applied — and unlike render, slip EARNS its
  target: four package-internal `_slip.py` mirrors (~80 KB
  quadruplicated, sync held only by parity pins) plus the workshop
  server whose docstring already promises the switch. The tenth module
  target is AUTHORIZED; the port is its own queued task under the
  DR 0022 authorize-then-gate pattern, with mirror reconciliation as
  gate 1 (the four mirrors hash differently — prove behavioral
  identity over the zoo + fuzz corpora before collapsing). The
  pydantic/jsonschema cross-check stays lab-side by design —
  independence is its value. The deferred-target list is now EMPTY.)
- [x] **E5 · The five player-NOTICES audit (DR 0021 a.4).**
  (2026-07-07: every notice audited at its real surface. (1) weather —
  SHIPPED+VISIBLE, provenance display closed here (snapshot count +
  tooltip on era cards). (2) creatures think — MECHANISM SHIPPED,
  trace NOT visible: `choose_action` discards the deliberation record
  before episode history; seeded for next cycle with the exact path
  named. (3) legibility — SHIPPED+VISIBLE, direction corrected by C1's
  measurement (drifts DOWN across chained eras — real, watched). (4)
  blood persists — GAP FOUND AND CLOSED: the Contribute step wired
  into the Keeper session (releases LEAD the founder pool, admissions/
  rejections verbatim, server passes its real released dir, CLI
  --released-dir; pinned incl. rejection + byte-identical-when-absent;
  the flow test founds a storm era with a released creature). (5)
  absence hurts — SHIPPED with the honest reading (persistence +
  replays; "simmering" is framing, no background sim exists or
  should). Four of five fully live; the fifth thinks but can't yet be
  seen thinking.)

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
