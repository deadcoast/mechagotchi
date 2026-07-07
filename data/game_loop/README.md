# Game loop artifacts (Stage 0)

G2 (decision record 0021): one full Keeper session over the
promoted engine surfaces. `session_runner_stage0.json` is the
session lab report; `campaign_ledger.json` is the DR 0022
schema-v1 JSON-interim campaign ledger (campaigns/eras/elites/
founders/unlocks/replays with engine reports stored verbatim),
the future `storage` module's lossless migration source.

R5 (decision record 0023): `replay_recorder_stage0.json` is the
replay recorder lab report; `replay_sample.json` is one recorded
life in the `mechagotchi_replay_v1` format — birth/wound/repair
frames plus every episode tick, all engine truth verbatim — the
workshop preview scrubber's artifact.

Regenerate:

- `python -B labs/game_loop/session_runner.py`
- `python -B labs/game_loop/replay_recorder.py`
