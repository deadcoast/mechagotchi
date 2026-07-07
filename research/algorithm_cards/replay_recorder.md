# Algorithm Card: Replay Recorder (a recorded life for the scrubber)

- **Name**: Replay recorder — `live_cycle(record_frames=True)` laid out
  as a deterministic scrubber timeline (`mechagotchi_replay_v1`).
- **Purpose**: R5 (DR 0017/0021/0023) — the player's window: a
  creature's whole life (birth, wounds, repairs, every episode tick) as
  RECORDED engine truth the preview scrubber replays without ever
  re-simulating.
- **Mathematical basis**: none needed — the recorder is a pure layout
  function over engine outputs. Frame identity: the timeline is
  `[birth] + Σ_cycles ([wound_c, repair_c] + [tick_{c,t} for t in
  episode_history_c])`; body-at-frame-i is the latest packet-bearing
  frame ≤ i (scrubber invariant); tick count equals the lifecycle's own
  `survival_ticks` per cycle (pinned).
- **Inputs**: a valid grid, SLIP profile, repair model, live-cycle
  parameters (cycles, ticks, dropout, seed).
- **Outputs**: the replay artifact — frames (packets for validator-
  passed bodies; the validator's errors verbatim for invalid repairs;
  the damage events' `removed_cells` verbatim for wounds; lifecycle
  history entries verbatim for ticks), the live digests, and the
  reproducing parameters.
- **Strengths**: first-law clean (no synthesized frame anywhere);
  deterministic and reproducible from its embedded parameters; the
  engine seam is additive and byte-identical off; consumable by both
  the workshop scrubber and R6's dataset batching.
- **Weaknesses**: single lives only (era-scale replay is recorder
  batching, R6/G4); frame payloads duplicate the body per repair frame
  (acceptable at 8x8 Stage-0 scale; compression is a dataset concern).
- **Failure modes**: a repair that comes back invalid yields a
  packet-less frame with the validator's errors — the scrubber shows
  the last valid body plus the failure, never a fake; an unaligned
  cycle ends the recording exactly where the engine ended the life.
- **Integration risk**: low — one opt-in keyword on `live_cycle`
  (contract-pinned byte-identical default), a lab, one server endpoint,
  one page panel.
- **License status**: original stdlib implementation.
- **Prototype result**: `mg_seed_001` under `slip_lcd_seed` (3×48,
  seed 20260707): 151 frames — 1 birth, 3 wounds, 3 repairs, 144
  episode ticks, full survival; 10/10 lab tests, 269 package contract
  tests, 46 workshop tests green; `/api/preview/replay` deterministic
  end to end.
- **Decision**: adopt (R5 developed to its description); era-scale
  wiring belongs to G4, dataset batching to R6.
- **Go-No-Go gate**: `record_frames` default byte-identical (contract
  probe); deterministic replay equality; timeline shape and tick-count
  pins; invalid bodies carry errors and no packet; endpoint round-trip
  deterministic.

## Sources

- `research/decision_records/0023-replay-recording.md`
- `research/experiment_reports/2026-07-07-replay-recorder.md`
- `labs/game_loop/replay_recorder.py` (+ `test_replay_recorder.py`)
- `packages/mecha_engine/src/mecha_engine/runtime/live.py`
- `workshop/server/workshop_server.py`, `workshop/preview/preview.html`
- `data/game_loop/replay_sample.json`
