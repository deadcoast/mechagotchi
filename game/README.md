# Mechagotchi — the Game Client

The second of the two builds (`docs/gap-analysis.md` §0): the playable
desktop client showcasing the Mechagotchi Computational Life Engine.
Technology decided by decision record 0033 (pygame-ce — the engine
imported in-process, packets consumed verbatim). The first law
(DR 0021): every number, event, and image shown is engine truth.

## Layout

- `src/mecha_game/` — the client package (no `sys.path` text; imports
  `mecha_engine`, never `labs`):
  - `packets.py` — the engine-truth packet source (adoption through
    `lifecycle.initial_state`; frames from `genome.render_packet_v2`)
  - `rasterize.py` — the pure, pygame-free compositor (the packet→pixel
    spec: palette raster, scanline, temporal `lcd_ghosting`)
  - `app.py` — the window (fixed-timestep pygame-ce loop)
- `tests/` — the F1 gates (headless; pygame cases skip unless the
  `game` group is provisioned)
- `evidence.py` — the stage-0 evidence harness
  (`data/game_client/front_end_skeleton_stage0.json`)
- `run_game.py` — the dev-checkout launcher
- `pyproject.toml` — the installable form (`mechagotchi` entry point;
  packaging is F5's rung)

## Run it (dev checkout)

```powershell
uv sync --group game
uv run python -B game/run_game.py            # play until ESC/close
uv run python -B game/run_game.py --ticks 24 # bounded verification run
```

## Test it

```powershell
uv run python -B -m unittest discover -s game/tests -p "test_*.py"
```

## Sources

- `research/decision_records/0033-game-front-end-technology.md`
- `research/experiment_reports/2026-07-12-front-end-client-skeleton.md`
- `research/decision_records/0021-game-loop.md` (the design input)
- `docs/gap-analysis.md` (Phase F)
