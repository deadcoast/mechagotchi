# Experiment Report: The Covenant's Earned Budget Gains Its Workshop Face — Advisory, Never Authority (Cycle 21 · SHARED · K5)

Date: 2026-07-21

## WHY

H4 named it and refused to drift into it: "budget-aware covenant
editing in the workshop (showing a campaign's earned caps beside the
sliders) would need the workshop to read campaign state — a
cross-surface decision for a DR." The survey for K5 found the boundary
half-crossed already, by recorded precedent: the workshop's SESSION
surface has driven the keeper loop through the session lab since the
G-phase (`load_keeper_state`, `apply_covenant_change`) under the
server's own law — "the server never recomputes game logic." What H4's
remainder actually asks is for the AUTHORING page to see what the
session page already governs. DR 0044 decides: **adopt, boundary
pinned**.

## WHAT

**The session lab owns the read model** (DR 0044 clause 1):
`state_covenant_budget(state)` — the state→budget composition
extracted VERBATIM from the lab's own `apply_covenant_change`, which
now calls it. The refactor's identity is pinned: the read model over a
fresh state equals `covenant_budget` over the state's recorded facts,
AND an over-spend rejection carries the identical budget dict.

**One read-only endpoint** (clause 2): `GET /api/covenant/budget` — an
absent session answers `available: false` with the reason named (the
workshop never fabricates unlock facts); a session answers the active
campaign id plus the lab's read model verbatim. Pinned read-only: the
GET leaves the state file byte-identical.

**The advisory strip** (clause 3): the slip creator's verdict column
gains the covenant-budget panel — the active campaign's earned
deliberation cap and palette set beside the very sliders that author
those fields, re-rendered on every live validation. Authoring beyond
the caps turns the strip AMBER with the gap named ("deliberation 8
exceeds the earned cap 3 — the game's covenant step would refuse this
spend"); within them, the accent confirmation. **Advisory, never
authority — pinned**: a schema-legal profile beyond any campaign's
earned caps still validates and saves exactly as before; the SLIP
verdict, the save gate, and the game's `apply_covenant_change` (the
only spender) are all untouched.

## Verification

```powershell
PS> python -B -m unittest test_workshop_server -k CovenantBudgetAdvisoryTests   # (from workshop/tests)
HTTP Error 404: File not found        # RED: no endpoint, no strip
# after the lab read model + endpoint + strip:
Ran 4 tests ... OK
PS> python -B -m unittest test_session_runner -k covenant   # (from labs/game_loop)
Ran 5 tests ... OK                    # incl. the extraction-identity pin
PS> node --check <extracted slip creator script>
JS SYNTAX OK                          # 551 lines
PS> python -B -m unittest discover -s workshop/tests -p "test_*.py"
Ran 92 tests in 158.215s ... OK       # 88 + the 4 advisory pins
PS> python -B -m unittest discover -s labs/game_loop -p "test_*.py"
Ran 84 tests in 5.418s ... OK         # incl. the extraction-identity pin
```

*(Process note: a draft of this block briefly carried predicted
full-suite counts before those runs completed — stripped and refilled
from the measured output; the numbers happened to match, which changes
nothing about the rule.)*

## HONEST REMAINDER

1. **The strip shows the SLIP-shaped caps only** (palettes,
   deliberation ticks); population/generation caps are engine
   parameters and stay on the session page — scope named in the DR.
2. **Server-verified, not click-tested** — the H5 standing gate, as
   with every H/J/K authoring face.
3. The advisory reads ONE session (the project's keeper state file);
   multi-campaign browsing is not a named need and enters only by its
   own record.

## Sources

- `audits/TODO.md` (cycle 21 K5) · `research/decision_records/0044-covenant-budget-workshop-face.md` (the charter) · `2026-07-19-behavior-editor.md` (H4's named remainder)
- `labs/game_loop/session_runner.py` (`state_covenant_budget`) + `test_session_runner.py` (the identity pin)
- `workshop/server/workshop_server.py` (`/api/covenant/budget`) + `workshop/slip_creator/slip_creator.html` (the advisory strip) + `workshop/tests/test_workshop_server.py` (CovenantBudgetAdvisoryTests)
- `game/src/mecha_game/covenant.py` (the game's spender — untouched)
