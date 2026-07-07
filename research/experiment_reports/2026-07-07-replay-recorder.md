# Experiment Report: The Replay Recorder and Scrubber (R5) — Engine Truth, Recorded

Date: 2026-07-07

## WHY

DR 0017 R5 (carried from cycle 01 as T12): "per-tick render packets
from live_cycle/episodes into a replay artifact; the preview gains a
scrubber (engine truth, recorded). The player's window." DR 0021's
Review step — the first thing a Keeper does each session — consumes
exactly this. The governing constraint is the game's first law: the
scrubber REPLAYS what happened; it never re-simulates, never invents a
frame.

## WHAT

Three layers (DR 0023):

1. **Engine seam** — `runtime.live_cycle(record_frames=False)`
   (keyword-only, default byte-identical — the DR 0016/0020 additive
   pattern). When on, each cycle carries `frames`: the wound's
   `removed_cells` verbatim from the damage observability contract, the
   `repaired_grid`, and the episode's full per-tick `history`. The
   engine grew the number first; the game only displays it.
2. **Recorder** — `labs/game_loop/replay_recorder.py` lays the life out
   as a `mechagotchi_replay_v1` timeline: `birth` packet → per cycle a
   `wound` frame (removed cells verbatim), a `repair` frame (the
   repaired body's validator-passed render packet, or the validator's
   errors when a repair is invalid — never a fake body), and one
   `episode_tick` frame per lifecycle history entry. The artifact
   embeds its reproducing parameters (seed included).
3. **Scrubber** — the preview page's replay panel (slider + play/pause;
   wounds overlay the current body; tick frames animate the lifecycle
   readout: action, need balance, death cause) fed by
   `POST /api/preview/replay`.

Recorded sample (`data/game_loop/replay_sample.json`): `mg_seed_001`
under `slip_lcd_seed`, 3 cycles × 48 ticks, seed 20260707 — 151 frames
(1 birth + 3 wounds + 3 repairs + 144 episode ticks; the creature
survived every episode fully).

## Verification

```powershell
PS> python -B -m unittest discover -s labs/game_loop -p "test_replay_recorder.py"
Ran 10 tests in 0.639s
OK

PS> python -B -m unittest discover -s packages/mecha_engine/tests -p "test_*.py"
Ran 269 tests in 7.423s
OK

PS> python -B -m unittest discover -s workshop/tests -p "test_*.py"
Ran 46 tests in 71.931s
OK

PS> python -B labs/game_loop/replay_recorder.py
{
  "artifact_id": "game_loop_replay_recorder_stage0",
  "decision": "replay_recorder_composed",
  "frame_count": 151,
  "tick_frame_count": 144,
  ...
}
```

The contract suite gained the `record_frames` probes (default has no
frames key; off equals stripped-on — the byte-identical pin; blocks
complete; wound counts match; histories match survival ticks; JSON
round-trip) and the signature/keyword-only pins. The workshop suite
gained the `/api/preview/replay` end-to-end + determinism test.

## Honest scope

- The scrubber consumes single recorded lives; era-scale replays (a
  whole evolve run) reuse the same seam creature-by-creature and are
  R6's `replay_100k_ticks` batching concern.
- The DR 0022 `replays` ledger table stays empty until the session
  runner records replays per era (a G4 wiring step); the format is now
  fixed.
- CTM deliberation fields ride the tick entries only when the covenant
  carries a `deliberation` block — the replay shows what the engine
  recorded, nothing more.

## Decision

`replay_recorder_composed` / adopt as lab + workshop evidence (R5
developed to its description: the recorder, the artifact, the
scrubber). Next: R6 (datasets, including `replay_100k_ticks` fed by
this recorder) and G4 (the Keeper's surface wiring replays per era).

## Sources

- `research/decision_records/0023-replay-recording.md`
- `research/decision_records/0021-game-loop.md`
- `packages/mecha_engine/src/mecha_engine/runtime/live.py`
- `packages/mecha_engine/tests/test_runtime_contract.py`
- `packages/mecha_engine/tests/helpers/runtime_contract_driver.py`
- `research/package_specs/mecha_engine_runtime_interface_spec.md`
- `labs/game_loop/replay_recorder.py`
- `labs/game_loop/test_replay_recorder.py`
- `workshop/server/workshop_server.py`
- `workshop/preview/preview.html`
- `workshop/tests/test_workshop_server.py`
- `data/game_loop/replay_recorder_stage0.json`
- `data/game_loop/replay_sample.json`
