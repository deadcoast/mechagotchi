# Experiment Report: The Review Step — a Recorded Life Plays Back (Cycle 15 · GAME · F10)

Date: 2026-07-12

## WHY

DR 0021's core loop opens with Review: "the last era's report and
replay: who survived, what the storms did" — and names R5's scrubber
as the window. The recorder shipped lab-side (R5, DR 0023:
`live_cycle(record_frames=True)` is the engine seam); the client's
Review showed summary metrics only. F10 brings the replay itself to
the player.

## WHAT

**`game/src/mecha_game/replay.py`** (RED-first, 10 tests): the R5
recorder's frame construction mirrored verbatim over engine publics —
one recorded `live_cycle` becomes birth / per-cycle wound (the damage
event's own `removed_cells`) / repair (restoration fidelity, the
validator's verdicts) / every episode tick. **The replay never
invents a displayable body**: packets only for validator-passing
states, errors verbatim otherwise. `ReplayPlayer` is the
scrubber-lite (step/back clamped, engine-truth captions), with the
shared drawer's invariant — the body at frame i is the latest
packet-bearing frame ≤ i — and `overlay_wounds` renders the wound
frames with the drawer's fill as arithmetic.

**`KeeperCampaign.record_review_replay()`**: the era's best elite
lives one recorded life at the ERA'S OWN seed and parameters, with
the lab's honest label riding the artifact ("a real recorded life of
a real era creature, replayed post-era" — the in-era lives ran
without frame recording; threading `record_frames` through `evolve`
remains the engine's named future seam).

**The client**: **V** opens the review (the companion's time stands
still while the Keeper looks away); **SPACE** plays/pauses, **.**
steps, **,** steps back; the panel shows the recorded body raw and
honestly effect-free (v1 packets declare no effects), wounds overlaid
in the drawer's red; the footer shows the caption and the honest
label.

**A finding the tests forced (recorded, not smoothed):** raw SEEDS
under the weak test-scale repair model hit the G2-measured
aligned-but-invalid boundary — their recorded lives truncate honestly
with zero episode ticks (pinned by test). The Review path replays
ELITES — gate survivors — whose lives record in full. **Measured**
(`data/game_client/review_replay_stage0.json`, status complete,
session scale): the best elite's replay at the era seed carries the
full phase vocabulary (birth 1 / wound 2 / repair 2 / episode_tick
32), the scrubber invariant holds at EVERY frame, twin runs
byte-equal.

## Verification

```powershell
PS> uv run python -B -m unittest discover -s game/tests -p "test_replay.py"
Ran 1 test ... FAILED (errors=1)   # RED: no mecha_game.replay
# after implementation (and the truncated-life finding):
Ran 10 tests ... OK
PS> uv run python -B -m unittest discover -s game/tests -p "test_*.py"
Ran 116 tests ... OK
PS> uv run python -B game/evidence.py   # review_replay_stage0: complete
PS> uv run python -B game/run_game.py --ticks 5 --keeper-dir <tmp>   # exit 0
```

## HONEST REMAINDER

1. **In-era lives are not frame-recorded** — the replay is a real
   recorded life at the era's seed, post-era (the lab's honest note;
   the evolve seam stays named engine-side).
2. **Replays are recorded on demand and not persisted** — the
   ledger's `record_replay` surface exists; persistence is a 0.3
   saves rung.
3. **Truncated lives display honestly** — an unaligned repair ends
   the recording where the engine ended it.

## Sources

- `audits/TODO.md` (cycle 15 F10), `research/decision_records/0021-game-loop.md` (Review), `0023-replay-recording.md` (the engine seam)
- `labs/game_loop/replay_recorder.py` (the mirrored recorder), `workshop/shared/draw.js` (bodyPacketAt + woundOverlay, the mirrored consumers)
- `game/src/mecha_game/{replay,campaign,app}.py` (+ `game/tests/test_replay.py`)
- `data/game_client/review_replay_stage0.json` (evidence)
