# Experiment Report: The Companion Loop as a Product — MVP 0.1 Lives (Cycle 14 · GAME · F2)

Date: 2026-07-12

## WHY

MVP 0.1 is the rung that "proves the entire thesis" (validity §1.34):
a 16×16 creature generated from a genome, visible needs, expression by
state, logged interactions, death → mutation → child carrying parent
traits, a lineage file. F1 delivered the launchable skeleton; F2 makes
the client PLAY the documented loop — under the game's documented
interaction model, not the sheltered simulator: D5 measured the honest
zero (a self-feeding switchboard saturates welfare), D6 operationalized
the keeper-dependent answer, and DR 0021 names it — **the companion
begs, the keeper feeds.**

## WHAT

**`game/src/mecha_game/session.py`** — the product loop, engine
surfaces only (mirrors the proven W1 lab without importing it —
boundary law): adoption via `lifecycle.initial_state` (refusals
verbatim), keeper actions via `advance_tick` over `ACTIONS`, autonomy
via `choose_action_detailed("switchboard", ...)` with thoughts riding
history. **Beg mediation exactly as D6 ran the gates**: an autonomous
"feed" decision becomes a beg display executed as `idle` (the tick's
deliberation record still rides — the thought was real; the game
mediated the act), and only the keeper's feed fills hunger. Death is
refusal-not-noop; **succession is `generation.generate_candidate`**
from the dead parent under the same covenant (deterministic seed
chain), lineage blocks recorded VERBATIM into
`keeper_lineage_v1` (grid_id, parent_grid_id, the engine's lineage
block, born/died ticks, cause). History trimmed to a 32-entry window
(the D5-measured deepcopy hotspot) — **pinned by test to change no
decision** against the untrimmed engine loop.

**`game/src/mecha_game/hud.py`** — pure engine-truth pixels: hunger
and energy bars from the state's own numbers, icons mirroring the
packet's `ui_hints` verbatim (the C5 threshold contract — the HUD
never re-derives a threshold). **`app.py`** — the playable window:
LCD panel + HUD strip (composed pure, scanlined) + a footer of
mood/age/generation from the packet and the state; F/P/S queue the
keeper's action for the NEXT lifecycle tick (answering the tick, not
accelerating time), ENTER adopts the successor at the death screen,
the lineage file saves on death and on quit (`keeper/` at the repo
root, gitignored — a live pet is not evidence; `~/.mechagotchi`
outside a checkout).

**Measured** (`data/game_client/companion_loop_stage0.json`, status
complete): the loop has REAL stakes from the engine's own dynamics —
**neglect starves the companion at age 10** (4 begs unanswered,
death_cause `starvation`); **the attentive keeper's feeding keeps it
alive through the full 400-tick budget** (79 feeds answered begs).
Twin runs byte-equal (the only nondeterminism is the player).
Succession holds: `mg_seed16_001_beetle → gen_d42be33dc5a7bfa7`,
child's `parent_grid_id` = the parent, engine lineage carried, two
records in the lineage document. The full unattended loop
(beg → starve → die → auto-succeed → two-life lineage file) runs
headless end to end in the launch tests, and a real window played
8 lifecycle ticks on the dev machine, exit 0.

## Verification

RED (the F2 gates fail for want of the modules):

```powershell
PS> uv run python -B -m unittest discover -s game/tests -p "test_session.py"
Ran 1 test in 0.000s
FAILED (errors=1)   # ModuleNotFoundError: mecha_game.session
PS> uv run python -B -m unittest discover -s game/tests -p "test_hud.py"
Ran 1 test in 0.000s
FAILED (errors=1)   # ModuleNotFoundError: mecha_game.hud
```

GREEN (the whole game suite — packets, compositor, session, HUD,
evidence, launches):

```powershell
PS> uv run python -B -m unittest discover -s game/tests -p "test_*.py"
Ran 42 tests in 1.906s
OK
```

Evidence + the real launch:

```powershell
PS> uv run python -B game/evidence.py
wrote ...\data\game_client\front_end_skeleton_stage0.json
wrote ...\data\game_client\companion_loop_stage0.json   # status: complete
PS> uv run python -B game/run_game.py --ticks 8 --keeper-dir <tmp>
pygame-ce 2.5.7 (SDL 2.32.10, Python 3.13.9)
# window: creature + bars + footer, 8 ticks played, exit code 0
```

## HONEST REMAINDER

1. **F3 owns the full bridge**: transition-graph clip DRIVING (today:
   state-selected clip via the engine's own probe packet, beg
   override, frame cycling), `crt_bloom`/`glitch` rasterization, and
   the D6-kept threads' game-side consumers (beg timing, clip choice,
   mood display).
2. **The lineage file is the only persistence** — session resume,
   eras, and unlocks are F4/F5 (DR 0021 G1's storage schema remains
   queued for its consumer).
3. **Mood/age text renders via pygame's default font** — casing
   chrome, not LCD truth; the numbers themselves are packet/state
   fields. A deterministic LCD micro-font is a candidate F3+ polish.
4. **Death pacing is real**: at the default 1.5 s/tick cadence an
   unattended companion starves in ~15 s of wall clock. Cadence is a
   presentation mapping (`--tick-frames`), the engine untouched;
   product tuning belongs to F4's era/session design.

## Sources

- `audits/TODO.md` (cycle 14 F2), `docs/project-research/validity-research.md` (§1.22, §1.34)
- `research/decision_records/0021-game-loop.md` (the interaction model), `0033-game-front-end-technology.md` (the skeleton this builds on)
- `labs/game_loop/companion.py` (W1 — the proven loop semantics mirrored)
- `labs/micro_threads/ablation_gates.py` (D6 — the beg-mediation semantics mirrored)
- `research/experiment_reports/2026-07-08-synthetic-keepers.md` (D5 — the honest zero that forced the model)
- `game/src/mecha_game/{session,hud,app}.py` (+ tests), `data/game_client/companion_loop_stage0.json`
