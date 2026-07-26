# Decision Record 0044: The Covenant's Earned Budget Gains Its Workshop Face — Advisory, Never Authority

Date: 2026-07-21

## Status

**Accepted** (cycle 21 · Phase K · K5). H4's named cross-surface
decision ("budget-aware covenant editing in the workshop would need
the workshop to read campaign state — a DR, not a drift"), decided:
**ADOPT, with the boundary pinned**.

## Context

The slip creator authors 0.2.0 covenants blind to the campaign: the
deliberation panel will author `max_ticks 8` with no hint that the
active campaign's EARNED cap is lower, and the palette toggles show no
earned unlocks. Meanwhile the boundary question was already half
settled by precedent this record now makes explicit: the workshop's
SESSION surface (G4/C4) already drives the keeper loop through the
session lab — `load_keeper_state`, `apply_covenant_change` — under the
server's own law, "every number the page shows comes from the session
lab's own read model over verbatim engine reports; the server never
recomputes game logic." What H4's remainder actually asks for is the
AUTHORING page seeing what the session page already governs.

## Decisions

1. **The session lab owns the read model**: `state_covenant_budget
   (state)` — the state→budget composition extracted VERBATIM from
   the lab's own `apply_covenant_change` (which now calls it; the
   existing covenant suite pins the refactor's identity). Budgets
   remain a pure function of RECORDED campaign facts; nobody
   recomputes game logic outside the lab that owns it.
2. **The workshop server gains ONE read-only endpoint**:
   `GET /api/covenant/budget` — loads the keeper state the server
   already knows how to find; **no session → `available: false` with
   the reason named** (an honest answer, never an error, never a
   fabricated budget: the workshop does not pretend to know unlock
   facts it doesn't have); a session → the active campaign id and its
   earned budget from the lab's read model, verbatim.
3. **The slip creator gains the advisory strip**: beside the
   deliberation panel and the palette toggles, the earned caps of the
   active campaign — and when the authored profile EXCEEDS them, an
   AMBER advisory naming the gap. **Advisory, never authority**: the
   SLIP validity verdict is untouched, saving stays gated on the
   authority alone, and nothing the panel shows can refuse a profile
   — a species definition legal under the schema is legal regardless
   of any one campaign's progression (the game's `apply_covenant_
   change` remains the only budget ENFORCER, exactly as before).
4. **The boundary, pinned by tests**: the endpoint is GET-only and
   writes nothing; absent state answers `available: false`; the
   served budget equals the session lab's own function over the same
   state (self-verifying); an over-budget profile still validates and
   saves (the advisory never gates).

## Consequences

- The Keeper authoring a species sees the campaign truth beside the
  sliders — the covenant's authoring face and its earned-budget
  governance finally share a pane of glass, without the workshop
  gaining any authority it shouldn't have.
- Engine parameters in the budget (population/generation caps) are
  NOT slip-creator concerns and stay on the session page; the
  advisory strip shows only the SLIP-shaped caps (palettes,
  deliberation ticks) — scope named, not drifted.

## Sources

- `research/experiment_reports/2026-07-19-behavior-editor.md` (H4's named remainder)
- `labs/game_loop/session_runner.py` (`covenant_budget`, `apply_covenant_change` — the lab authority; `state_covenant_budget` the extracted read model)
- `workshop/server/workshop_server.py` (the session precedent + the new endpoint) + `workshop/slip_creator/slip_creator.html` (the advisory strip)
- `game/src/mecha_game/covenant.py` (the game's mirror — untouched; still the only spender in the game build)
- `research/decision_records/0021-game-loop.md` (the covenant progression), `0007` (the workshop's serving discipline)
