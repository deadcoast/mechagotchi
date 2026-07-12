# Experiment Report: The Front-End Decision + the Launchable Client Skeleton (Cycle 14 · GAME · F1)

Date: 2026-07-12

## WHY

Cycle 14 opens the GAME track (Phase F): the build the engine exists to
showcase — a client a player launches and plays, NOT the dev-served
workshop pages (standing identity constraint). F1's charter
(`audits/TODO.md`): evaluate the documented bridge targets (web /
Godot / terminal / Pygame / desktop) against the engine's REAL contract
— JSON render packets, retro effects, deterministic replays,
installable releases with save files — choose by decision record, and
deliver a LAUNCHABLE hello-creature client rendering a real engine
packet end to end.

## WHAT

**Decision record 0033: the client is a pygame-ce desktop application.**
The deciding structure: the engine is a deterministic pure-Python
package, so the only front end that consumes packets *verbatim* — no
serialization boundary, no second implementation of any engine number,
no IPC process to package — is a Python client importing `mecha_engine`
in the same interpreter: the strongest form of the game's first law
(DR 0021) and the cheapest replay fidelity. Ecosystem facts checked
2026-07-12: pygame-ce 2.5.7 supports Python 3.10–3.14; upstream pygame
does not support 3.14 (this workspace runs 3.14.3). Web stays the
workshop's scale-path; Godot is a named re-opener at MVP 0.2/0.3 scale;
terminal cannot rasterize the effects contract in full; G4's
served-page delivery wording (DR 0021) is superseded for the game
build. Dependency declared per DR 0028 (root `game` group + the game's
own pyproject).

**The `game/` build** (a sibling of `workshop/`, src layout, boundary
law inherited from the engine — no `sys.path` text in `src/`, imports
`mecha_engine` never `labs`):

- `game/src/mecha_game/packets.py` — engine truth only: adoption via
  `lifecycle.initial_state` (the engine's own gate, errors relayed
  verbatim), every frame one `genome.render_packet_v2` driving the
  idle clip; the default hello pair (`mg_seed16_001_beetle` under
  `slip_lcd_seed`) is pinned by tests over the real fixtures, never
  assumed.
- `game/src/mecha_game/rasterize.py` — the PURE compositor (DR 0033
  decision 4): pygame-free packet→pixel math following the shared
  workshop drawer's canonical semantics, plus the first implementation
  of **`lcd_ghosting`** — the named Phase-C remainder #2 — as
  per-LCD-pixel persistence at grid resolution
  (`round(current·(1−alpha) + previous·alpha)`), the pre-scanline
  raster carried as temporal state. Declared-but-unimplemented effects
  are reported in `skipped`, never silently dropped.
- `game/src/mecha_game/app.py` — the window: fixed-timestep loop
  (default 8 fps, the LCD heartbeat), `--ticks` for bounded
  verification runs, ESC/close quits; pygame touches only this layer.
- `game/evidence.py` + `data/game_client/front_end_skeleton_stage0.json`
  — the measured evidence (below); `game/run_game.py` — the
  dev-checkout launcher; `game/pyproject.toml` — the installable form's
  manifest (`mechagotchi` entry point; packaging itself is F5).

**Measured (the stage-0 artifact):** twin-run frame checksums
byte-equal over a 32-tick session (deterministic composition); the
idle clip cycles exactly `tick % 4`; the always-on LCD identity
(`scanline` + `lcd_ghosting`) applied with nothing declared skipped;
ghosting yields 10 distinct frames from a 4-frame clip (the persistence
transient before the periodic steady state — temporal state is real,
not cosmetic). A real windowed launch on the dev machine ran 24 ticks
and exited 0.

## Verification

RED (before implementation — the F1 gates fail for want of the client):

```powershell
PS> uv run python -B -m unittest discover -s game/tests -p "test_*.py"
Ran 4 tests in 0.461s
FAILED (failures=1, errors=3)   # ModuleNotFoundError: mecha_game.*
```

GREEN (same command after implementation; 21 tests — packets,
compositor, evidence, headless launches):

```powershell
PS> uv run python -B -m unittest discover -s game/tests -p "test_*.py"
Ran 21 tests in 1.947s
OK
```

Lab/evidence + the real launch:

```powershell
PS> uv run python -B game/evidence.py
wrote C:\...\data\game_client\front_end_skeleton_stage0.json   # status: complete
PS> uv run python -B game/run_game.py --ticks 24
pygame-ce 2.5.7 (SDL 2.32.10, Python 3.13.9)
# window opened, 24 ticks at 8 fps, exit code 0
```

The closing sweep (2026-07-12):

```powershell
PS> # 19 lab suites under the system interpreter (the convention):
animation_system 33 · architecture 14 · asset_pipeline 22 ·
cellular_automata 37 · ctm_ticks 4 · cubff_transducer 17 · datasets 22 ·
game_loop 83 · grid_genome 209 · lifecycle_sim 24 · map_elites_archive 99 ·
micro_threads 85 · package_promotion 6 · readability_benchmark 42 ·
repair_boundary 4 · runtime_integration 65 · slip_validator 24 ·
wfc_grid 36 · workshop_editor 307 — all OK
package 291 OK · workshop 60 OK · CLI 21 OK · game 21 OK
```

**Interpreter observation recorded (not pinned, per the H-01 rule):**
`workshop_editor`'s foreign-fixture byte-equality pins are
zlib-BUILD-sensitive — they pass under the system CPython 3.14.3
(zlib-ng 1.3.1, which generated the committed fixtures) and fail 10
tests under uv's python-build-standalone 3.13.9 (classic zlib 1.3.1),
because the two builds emit different compressed bytes for the same
pixels. Run labs with the system `python -B` per convention; the uv
venv serves the dependency-group suites (lab/cli/game).

## HONEST REMAINDER

1. **The companion loop is F2** — the hello state is static engine
   truth (initial lifecycle state; the clip cycles, needs do not move).
   Tending, death, mutation, lineage land with MVP 0.1's loop over the
   W1 companion surfaces.
2. **`crt_bloom`/`glitch` rasterization is F3** — a calm hello creature
   declares neither; the compositor reports (never drops) declared
   effects it does not yet implement, pinned by test.
3. **The installable release is F5** — PyInstaller named in DR 0033,
   decided at its own rung; today's launch paths are the dev checkout
   (`run_game.py`, `python -m mecha_game`).
4. **Presentation cost is pure-Python** (~150k byte ops/frame at the
   default scale) — ample at 8 fps/16×16; a measured concern only if a
   future consumer demands more.

## Sources

- `research/decision_records/0033-game-front-end-technology.md` (the decision this report delivers)
- `audits/TODO.md` (cycle 14 F1), `docs/gap-analysis.md` (Phase F; §0)
- `research/experiment_reports/2026-07-08-phase-c-gate.md` (the packet contract; remainder #2 closed here for the live client)
- `workshop/shared/draw.js` (the canonical drawing semantics the compositor mirrors)
- `labs/game_loop/companion.py` (the W1 loop F2 productizes)
- `game/` (code + tests), `data/game_client/front_end_skeleton_stage0.json` (evidence)
