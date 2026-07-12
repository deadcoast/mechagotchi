# Decision Record 0033: The Game Front End — a pygame-ce Desktop Client (F1)

Date: 2026-07-12

## Status

**Accepted** (cycle 14 · GAME track · Phase F, task F1). Governed by
`docs/gap-analysis.md` Phase F and the two-builds frame (§0); design
input DR 0021 (the Keeper/era loop); dependency authority DR 0028.
This record chooses the technology for the playable client — the build
the engine exists to showcase — and names where it lives.

## Context — the engine's REAL contract, measured

The documented bridge targets are web, Godot, terminal, Pygame, and
desktop (gap-analysis §3 "Rendering"; validity-research §1.20 names the
stack "Python first" with "TypeScript + Canvas" as the *editor* path and
"later you can port the runtime core to Rust, TypeScript, or Godot if
needed"). The client must be judged against what the engine actually
ships, not against taste:

1. **The render bridge is a JSON packet, renderer-neutral by law.**
   `mecha_engine.genome.render_packet_v2` emits cells + palette at the
   ratified 16×16 scale, the dossier's `animation` block
   (`clip`/`frame_index`/`frame_count`/`anchors`), `mood`, the effects
   declaration (`scanline` + `lcd_ghosting` always on — the LCD
   identity; `crt_bloom` riding beg; `glitch` with amplitude equal to
   the engine's own stress), deterministic `effect_parameters`, and
   threshold-mirroring `ui_hints`. DR 0026's disposition stands:
   **consumers rasterize; the engine never does.**
2. **`lcd_ghosting` requires temporal state.** The Phase-C gate's named
   remainder #2: a static drawer honestly skips it; only a live client
   holding frame history can rasterize it. The chosen front end must
   composite frames over time.
3. **The companion loop is Python, in-process.** Adoption is
   `lifecycle.initial_state` (the engine's own gate), tending is
   `advance_tick` over `ACTIONS`, autonomy is the frozen switchboard
   via `choose_action_detailed`, eras are `runtime.evolve` — all
   deterministic under seeds; the only nondeterminism in a companion's
   life is the player (the W1 companion lab pins this end to end).
4. **Deterministic replays are an input-fidelity discipline** (DR 0023;
   a faithful replay reproduces INPUTS exactly). Any boundary that
   serializes engine state to a second runtime is a place replay
   fidelity can silently drift.
5. **F5 requires an installable release with save files** — install,
   launch, play, quit, resume.

One supersession to record explicitly: DR 0021's build gate G4 named
"the workshop server pattern (stdlib server + served page)" for the
Keeper's surface. The owner's recalibration (gap-analysis §0; the
cycle-14 charter) rules that **dev-served pages are NOT the game's
front end**. G4's *content* (a session surface, `mechas` session
commands) stands; its served-page *delivery* is superseded by this
record for the game build. The workshop keeps its ratified stack.

## The candidates, judged against that contract

| Candidate | Packets | Effects (incl. temporal ghosting) | Determinism/replay | Installable + saves | Verdict |
| --- | --- | --- | --- | --- | --- |
| Web (served page / TS+React) | via HTTP bridge or an engine PORT | canvas: yes | serialization seam or a second engine implementation | needs Electron/Tauri on top | **Rejected** for the game; TS+React remains the documented WORKSHOP scale-path |
| Godot | via IPC to a Python subprocess, or a GDScript port | shaders: excellent | two-process seam; port violates engine truth | excellent | **Rejected for MVP 0.1; named re-opener** at 0.2/0.3 scale |
| Terminal | in-process | cannot rasterize bloom/alpha-ghosting/sub-cell glitch with fidelity | trivially | yes | **Rejected** (F3 must consume the effects contract IN FULL) |
| Desktop GUI (tkinter/Qt) | in-process | no game loop idiom; per-pixel compositing slow (tkinter) or a heavyweight dependency (Qt) | trivially | Qt heavy for a 16×16 LCD toy | **Rejected** |
| **pygame-ce** | **in-process, verbatim** | **SDL2 surfaces composite all four documented effects, including temporal ghosting** | **same interpreter, same seeds — preserved by construction** | **cross-platform; PyInstaller path for F5** | **ADOPTED** |

The deciding structure: the engine is a deterministic pure-Python
package, so the only front end that consumes packets *verbatim* — no
serialization boundary, no second implementation of any engine number,
no IPC process to package — is a Python client importing
`mecha_engine` in the same interpreter. That is the strongest possible
form of the game's first law (every pixel is engine truth) and the
cheapest possible replay fidelity. A fixed-timestep pygame loop is
also exactly the live clip-driving consumer the Phase-C remainder
names for F3, and SDL surface compositing implements the documented
effects deterministically.

Ecosystem facts checked 2026-07-12: **pygame-ce 2.5.7** (released
2026-03-02) supports Python 3.10–3.14; **upstream pygame does not
support Python 3.14** (pygame/pygame#4810), and this workspace runs
3.14.3. pygame-ce is the actively maintained community fork and is
what downstream ecosystems are migrating to. The dependency is
therefore `pygame-ce`, not `pygame` — they are import-compatible
(`import pygame`).

## Decision

1. **The playable client is a pygame-ce desktop application** —
   product title *Mechagotchi*, package `mecha_game`.
2. **Home: `game/`** — a sibling build to `workshop/`, per the
   two-builds frame: src layout `game/src/mecha_game/`, tests in
   `game/tests/`, its own `pyproject.toml`. The root pyproject gains a
   `game` dependency group (`pygame-ce>=2.5.7`) for in-repo
   development and test runs, mirroring the `cli` group's pattern.
3. **Boundary law, inherited from the engine:** `game/src/mecha_game/`
   imports `mecha_engine` and never `labs`; no `sys.path` text inside
   `src/`; the dev launcher and the tests own the path bootstrap
   (the installable form resolves real dependencies instead).
4. **The rasterizer core stays pure Python (pygame-free).** Packet →
   pixel-buffer compositing (palette mapping, scanline, temporal
   ghosting, later bloom/glitch) is deterministic stdlib math with
   headless unit tests; pygame touches only the window/present layer.
   Consequence: a future Godot/web client reuses the same compositing
   spec, and the render bridge stays front-end agnostic in fact, not
   just in name.
5. **F1's deliverable:** the launchable hello-creature client — a real
   16×16 corpus creature (`data/seed_grids_16x16/`) under an aligned
   SLIP through `lifecycle.initial_state` → `render_packet_v2` driving
   the idle clip frame by frame → the always-on LCD identity effects
   composited live. `crt_bloom`/`glitch` rasterization lands at F3
   with the full bridge consumption (a calm hello creature never
   declares them — honest scope, not a skipped contract).
6. **F5's packaging is NAMED here (PyInstaller), decided there** — at
   its own rung, with evidence, per this repo's discipline.

## Consequences

- The GAME track has a concrete, launchable delivery form; F2–F5 build
  on this skeleton.
- The first third-party runtime dependency of a shipped build enters
  under DR 0028, justified above (the list stays otherwise unchanged).
- DR 0021 G4's served-page delivery wording is superseded for the game
  build; everything else in DR 0021 stands as the design input.
- Named re-openers: a Godot client if MVP 0.2/0.3 rendering scale
  demands it (the packet contract is the seam it would consume
  unchanged); a web showcase build; a terminal auxiliary view.

## Sources

- `docs/gap-analysis.md` (§0 the two builds; §3 rendering/tech-stack rows; Phase F)
- `audits/TODO.md` (cycle 14, F1)
- `docs/project-research/validity-research.md` (§1.20 tech stack, §1.22 MVP 0.1)
- `research/decision_records/0021-game-loop.md` (design input; G4 supersession recorded above)
- `research/decision_records/0026-render-module-disposition.md` (consumers rasterize)
- `research/decision_records/0028-license-and-dependency-policy.md` (dependency authority)
- `research/experiment_reports/2026-07-08-phase-c-gate.md` (the packet contract; remainders #2/#3)
- `packages/mecha_engine/src/mecha_engine/genome/animation.py` (`render_packet_v2`, `packet_effects`)
- `labs/game_loop/companion.py` (the W1 companion loop this client will productize)
- pygame-ce 2.5.7 (PyPI, 2026-03-02; Python 3.10–3.14); pygame/pygame#4810 (no upstream 3.14 support)
