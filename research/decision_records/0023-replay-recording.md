# Decision Record 0023: Replay Recording (R5) — The Player's Window

Date: 2026-07-07

## Status

**Accepted** (DR 0017 R5 = cycle-01 T12, carried; DR 0021's Review step
names this its window). Replay is RECORDED engine truth: the scrubber
replays what happened, it never re-simulates and never invents a frame.

## Decision

Three layers, each honest about what it is:

1. **The engine seam** — `mecha_engine.runtime.live_cycle` gains
   keyword-only `record_frames: bool = False`. When true, each cycle
   dict carries a `frames` block: `removed_cells` (the damage event's
   own observability record, verbatim), `repaired_grid`, and the full
   per-tick `episode_history`. Default `False` is byte-identical (the
   DR 0016/0020 additive-keyword pattern; contract probe + frozen pins
   unmodified). This is DR 0021's first law in action: the game needed
   per-tick truth the engine did not expose, so the engine grew the
   number first.
2. **The recorder** — `labs/game_loop/replay_recorder.py` lays a
   recorded life out as a scrubber timeline
   (`mechagotchi_replay_v1`): a `birth` packet, then per cycle a
   `wound` frame (removed cells verbatim), a `repair` frame (the
   repaired body's validator-passed render packet — or the validator's
   errors when a repair comes back invalid; never a fake body), and one
   `episode_tick` frame per lifecycle history entry (action, balance,
   recoveries, alive/death, full state snapshot — R1 deliberation
   fields ride along when the covenant carries them). An unaligned
   cycle ends the recording where the engine ended the life. The
   artifact embeds the parameters (seed included) that reproduce it.
3. **The scrubber** — the workshop preview page gains a replay panel
   (slider + play/pause over the frame timeline; wounds overlay the
   current body; tick frames animate the lifecycle readout) fed by
   `POST /api/preview/replay` on the workshop server (DR 0010's
   delivery stack; the workshop layer may import labs and the package).

## Gates

- Contract: `record_frames` defaults off byte-identical; blocks
  complete; wound counts match; histories match survival ticks; JSON
  round-trip (driver probes + `test_runtime_contract.py`).
- Lab: deterministic replay; timeline shape (birth, wound+repair per
  cycle, tick frames equal to survived ticks); wound/repair frames pin
  their cycle digests; invalid bodies carry validator errors and no
  packet; artifacts round-trip (`test_replay_recorder.py`).
- Workshop: `/api/preview/replay` returns a deterministic
  `mechagotchi_replay_v1` artifact end to end
  (`test_workshop_server.py`).

## Consequences

- DR 0021's Review step has its window; the campaign ledger's `replays`
  table (DR 0022) has its artifact format.
- R6's `replay_100k_ticks` dataset is this recorder batched over the
  corpus.

## Sources

- `research/decision_records/0017-recalibration-engine-game-duality.md` (R5)
- `research/decision_records/0021-game-loop.md` (the Review step)
- `research/decision_records/0022-storage-module.md` (the replays table)
- `packages/mecha_engine/src/mecha_engine/runtime/live.py`
- `labs/game_loop/replay_recorder.py` (+ `test_replay_recorder.py`)
- `workshop/server/workshop_server.py`, `workshop/preview/preview.html`
- `research/package_specs/mecha_engine_runtime_interface_spec.md` ("record_frames")
