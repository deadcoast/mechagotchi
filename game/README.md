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
  - `session.py` — the companion loop (F2, MVP 0.1): W1 semantics +
    the documented beg-mediated interaction model (the companion begs,
    only the keeper feeds), death → the engine's child, the
    `keeper_lineage_v1` file of verbatim engine blocks
  - `hud.py` — pure engine-truth bars (hunger/energy) + `ui_hints` icons
  - `app.py` — the playable window (fixed-timestep pygame-ce loop)
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

Controls: **F** feed · **P** play · **S** sleep (queued for the next
lifecycle tick) · **ENTER** adopt the successor when the companion
dies · **E** run an evolution era (**1/2/3** pick the weather) ·
**A** adopt the era's best elite as your companion · **C** covenant
mode (**1/2/3/4** spend earned unlocks: palette / thinking /
population / generations) · **H** hatch a new founder under your
covenant and adopt it (its origin trace shows) · **R** release your
companion's genome as a founder for the next era · **W** gather the
workshop's released creatures for the next era (the engine admits or
rejects them — the verdict shows) · **V** review the last era's best
elite living one recorded life (SPACE play/pause, **.** step, **,**
back) · **B** browse the repertoire — your bloodline's whole archive,
niche by niche (**.**/**,** page, **[**/**]** switch eras, **A**
adopt the one you're looking at) · **L** read your bloodline's story,
life by life (origins, death causes, the growing ancestor chain) ·
**X** export your covenant as a shareable SLIP file / **I** import
one from `keeper/covenants/covenant_import.json` (the engine's
authority judges it; an import is a new species contract) · **K**
import a community pack from `keeper/packs/pack_import.json`
(covenants and creatures staged into the inboxes, verdicts shown;
`data/packs/mechagotchi_starter_pack.json` is the committed example) ·
**ESC**/close quit. Saves land in
`keeper/` (gitignored) — quit and come back, the client resumes. The
companion begs when it wants food — only you can feed it; neglect
starves it (measured: ~10 ticks).

## Install it (F5)

```powershell
uv run python -B game/build_release.py
.\game\dist\Mechagotchi\Mechagotchi.exe        # install-free bundle: launch and play
```

Quit and come back: the client auto-resumes your companion from the
save file (`--new` starts a fresh one). Saves live in `keeper/` in a
checkout, `~/.mechagotchi` for the installed build.

## Test it

```powershell
uv run python -B -m unittest discover -s game/tests -p "test_*.py"
```

## Sources

- `research/decision_records/0033-game-front-end-technology.md`
- `research/experiment_reports/2026-07-12-front-end-client-skeleton.md`
- `research/decision_records/0021-game-loop.md` (the design input)
- `docs/gap-analysis.md` (Phase F)

## Covenant-authored cleaning (Q2, 2026-10-04)

A v0.2 covenant can opt into cleanliness with
`"mechanics": {"cleanliness": true}`. The game shows the engine's value in
the footer and **G** queues a clean action for the next lifecycle tick.
Cleaning takes a tick; it does not feed the companion. The default covenant
stays unchanged. Opt-in survives quitting, resuming, and succession.

Try the authored example in a separate save directory:

```powershell
uv sync --locked --group lab --group cli --group game
uv run --no-sync python -B game/run_game.py --new --slip data/slips/valid/slip_v2_cleanliness.json --keeper-dir keeper/cleanliness-example
# Resume that same companion (omit --new):
uv run --no-sync python -B game/run_game.py --keeper-dir keeper/cleanliness-example
```

`--new` replaces the companion in the selected keeper directory. The example
directory separates this trial from ordinary `keeper/` play. For code consumers,
`CompanionSession(..., mechanics=None)` inherits the covenant; an explicit
`mechanics=()` disables it, and that override survives save/load/succession.

## Sources for Q2

- `research/decision_records/0063-covenant-mechanics-authorship.md`
- `game/tests/test_slip_mechanics.py`
- `data/slips/valid/slip_v2_cleanliness.json`

## 2026-10-04: New default companions can be cleaned (DR 0064)

New lives now use the measured v0.2 cleanliness covenant. **G** cleans on the
next lifecycle tick; the footer shows the engine's value. Feeding, playing and
sleeping still matter; cleaning takes time and does not feed the companion.
Existing saves and existing campaigns retain their own covenants.

The normal launcher now supports authored profiles and separate save homes:

```powershell
mechas game --play
mechas game --play --new --slip data/slips/valid/slip_v2_cleanliness.json --keeper-dir keeper/cleanliness-example
mechas game --play --keeper-dir keeper/cleanliness-example
```

The last command resumes that example. A supplied --slip applies to a new
companion; if that directory already contains a save, choose --new explicitly
or a separate directory. A new evolution campaign starts under that companion's
covenant. A resumed campaign keeps its saved, possibly earned/spent covenant.
The earlier Q2 default note above describes the state before this gated flip.

## Sources for Q3

- `research/decision_records/0064-default-covenant-cleanliness.md`
- `research/experiment_reports/2026-10-04-default-covenant-gate.md`
- `data/game_client/default_covenant_gate_stage0.json`, `default_covenant_release_stage0.json`
