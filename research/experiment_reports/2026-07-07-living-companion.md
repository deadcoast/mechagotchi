# Experiment Report: The Living Companion (W1) — The Tamagotchi Heart, on the Engine's Tick

Date: 2026-07-07

## WHY

Cycle 08's charter (the owner's course correction): the mechanisms are
proven but the application is not coherent — and the biggest missing
piece is the og fantasy itself. Every surface showed the ecosystem from
above (eras, archives, replays); nothing showed A COMPANION: one
creature, alive on screen, that the player tends. The engine has
carried everything needed for this since Stage 0 — `initial_state`,
`advance_tick`, the frozen switchboard, packet v2 — it had simply never
been composed into the experience.

## WHAT

- **One lifecycle export** — `choose_action_detailed` (F1's chooser)
  and `ACTIONS` join the contracted public surface (gate doc
  "Interactive surface" amendment; the exact-`__all__` pin updated
  four → six; no behavior changed — both names bind objects the module
  already used internally).
- **The companion lab** (`labs/game_loop/companion.py`): adopt =
  `initial_state`'s own gate (invalid bodies and covenant mismatches
  refused with the engine's verbatim errors); tend = the player's
  buttons ARE the action vocabulary, one `advance_tick` each; live =
  `choose_action_detailed` plays the idle moments (the same frozen
  switchboard that plays every era, deliberation record included —
  a thinking covenant makes the companion visibly think, live); appear
  = every frame is `render_packet_v2(grid, state, slip_profile=...)`
  (mood + animation from the live state, bounded by the species'
  grammar); die = honestly, cause named, tending the dead REFUSED
  (never no-opped), succession the only way on. Persisted as play
  state (`keeper/companion.json`, gitignored, backup-before-overwrite).
- **The surface** — `/companion` (needs bars with worry coloring, the
  action buttons, "let it live" auto-tick, the thought line, recent
  moments, honest death screen, adopt panel with creature + covenant
  pickers reusing the existing list endpoints); server endpoints
  `GET /api/companion`, `POST /api/companion/adopt|act|tick`; nav links
  from session and preview; `mechas session --companion` serves and
  opens it.
- **12 lab gates + 3 endpoint tests**, including: feeding feeds;
  neglect starves at the measured bistability tick; a
  deliberation covenant produces bounded thoughts in the log;
  autonomous ticks are deterministic given the state; the E1 vocab
  gate bounds a hungry companion's expression to its species' grammar
  (displayed idle, mood honestly hungry); the wrong-species successor
  is REFUSED by the same gate that admitted the first (mg_seed_002 is
  gameboy_gray under an lcd covenant — caught live during testing, the
  gate doing exactly its job).

## Verification

```powershell
PS> python -B -m unittest discover -s labs/game_loop -p "test_companion.py"
Ran 12 tests ... OK
PS> workshop (55) OK · package (290, surface pin updated) OK ·
    game_loop (81) OK · lifecycle_sim (24) OK ·
    runtime_integration (65) OK · cli (21, --companion) OK
```

## Decision

Adopt — W1 developed to its description. The application now has its
heart: a creature you adopt through the engine's gate, tend with the
engine's actions, watch think with the engine's deliberation, and lose
to the engine's honest mortality. Zero new engine numbers were invented;
one existing seam was made public.

## Sources

- `audits/TODO.md` (cycle 08 W1 — the owner's course correction)
- `labs/game_loop/companion.py` + `test_companion.py`
- `packages/mecha_engine/src/mecha_engine/lifecycle/__init__.py`
- `research/package_specs/mecha_engine_lifecycle_contract_gate.md` (§ Interactive surface)
- `workshop/companion/companion.html`, `workshop/server/workshop_server.py`
- `workshop/tests/test_workshop_server.py` (CompanionEndpointTests)
- `tools/mechas_cli/src/mechas_cli/workflows/session.py` (`--companion`)
