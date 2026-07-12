# Experiment Report: Covenant Spending — the Progression Is Felt (Cycle 15 · GAME · F7)

Date: 2026-07-12

## WHY

DR 0021's Covenant step is the progression surface: unlock facts are
engine metrics, and spending them into the SLIP covenant is how the
Keeper's stewardship compounds — palettes, thinking depth, era scale.
The session lab proved the budget and the spend rule (G2/C4); MVP 0.1
shipped the EARNING (cycle 14's nine facts); F7 makes the facts
SPENDABLE in the client.

## WHAT

**`game/src/mecha_game/covenant.py`** — the lab's semantics mirrored
over engine publics (RED-first, 12 covenant tests): `covenant_budget`
is a PURE function of the campaign's BASE covenant, base engine
parameters, and the earned facts (palettes per niche tier in the
DR 0021 order; thinking per bloodline tier on the authority's real
2-tick floor; population/generation caps doubling per qd tier; the
legibility blend stepping; deferred axes NAMED — organ roles await
the SLIP field, harsher forecasts await new weather sources).
`apply_covenant_change` refuses over-budget requests with named
violations and applies NOTHING; every accepted covenant passes
`mecha_engine.slip.validate_slip` (the authority's refusals
verbatim). One-key spends (`spend_next_palette`,
`spend_deliberation_to_budget`, caps) power the client's covenant
mode. The campaign gained `base_profile`/`base_parameters` (spends
never compound against themselves) and in-memory unlock inheritance:
**a successor carries the unlock STATE but not the spends** — the
covenant and caps reset to base, the budget survives (roguelite,
mirroring the ledger's pointer-chain rule).

**The client**: **C** toggles the covenant mode — the footer shows
the budget verbatim (`palettes 1/2 · thinking 0/2 · pop 16/64 ·
gens 6/12`) and **1/2/3/4** spend palette/thinking/population/
generations; refusals display the named violations. Adopted elites
now live under the campaign's ACTIVE covenant — a spent thinking
budget makes the Keeper's companion visibly deliberate (W1's seen
thought, earned through play).

**Measured** (`data/game_client/covenant_spending_stage0.json`,
status complete, session scale, twin-run equal): one calm era earned
EIGHT facts (niche_mastery to tier 3, qd tier 2, legibility tier 2,
bloodline 1); the over-budget request (thinking beyond the earned
max) was REFUSED with nothing applied; palette (`amber_terminal`),
thinking (2 ticks), and population (cap 64 — qd tier 2 doubling
twice) all spent; **the era under the spent covenant ran at
population 64 and filled 93 niches** — the exponential progression
axis DR 0021 designed, observed working in the product.

## Verification

```powershell
PS> uv run python -B -m unittest discover -s game/tests -p "test_covenant.py"
Ran 1 test ... FAILED (errors=1)     # RED: no mecha_game.covenant
# after implementation:
Ran 12 tests ... OK
PS> uv run python -B -m unittest discover -s game/tests -p "test_*.py"
Ran 95 tests ... OK
PS> uv run python -B game/evidence.py   # covenant_spending_stage0: complete
PS> uv run python -B game/run_game.py --ticks 5 --keeper-dir <tmp>   # exit 0
```

## HONEST REMAINDER

1. **The deferred budget axes stay deferred and named** (the lab's own
   deferrals, mirrored): organ-role budgets await an `allowed_roles`
   SLIP field; storm_record tiers await weather beyond the three
   shipped forecasts.
2. **Spent-covenant persistence**: the ledger stores each ERA's
   profile verbatim (reproducibility holds), but the ACTIVE spent
   covenant itself is process-state — quitting mid-campaign re-earns
   the spends from the persisted facts. The campaign-resume rung
   (F11's hardening or 0.3's saves) owns it; named, not smuggled.
3. **The covenant UI is one-key presets** — a full palette
   picker/slider surface is 0.3-rung authoring polish.

## Sources

- `audits/TODO.md` (cycle 15 F7), `research/decision_records/0021-game-loop.md` (the Covenant step + progression table)
- `labs/game_loop/session_runner.py` (`covenant_budget`/`apply_covenant_change` — the mirrored source)
- `packages/mecha_engine/src/mecha_engine/slip/__init__.py` (the authority)
- `game/src/mecha_game/{covenant,campaign,app}.py` (+ `game/tests/test_covenant.py`)
- `data/game_client/covenant_spending_stage0.json` (evidence)
