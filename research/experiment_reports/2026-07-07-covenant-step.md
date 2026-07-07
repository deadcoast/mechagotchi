# Experiment Report: The Covenant Step (C4) — Unlocks SPEND

Date: 2026-07-07

## WHY

DR 0021's core loop, step 2: "adjust the species SLIP within the
unlocked budget." G4 shipped the session and displayed the facts; C4
makes them SPENDABLE — the progression table stops being a scoreboard
and becomes the game's economy, with every budget line a pure function
of earned facts.

## WHAT

- **`covenant_budget`** (pure, tuning data): the DR 0021 table mapped
  to spendable budget — niche-mastery tiers unlock covenant palettes
  (`PALETTE_UNLOCK_ORDER`, one per tier); bloodline-depth tiers unlock
  `deliberation.max_ticks` (tier 1 = the authority's FLOOR of 2 ticks —
  found by the validator during development, "+1 per tier" rides on the
  real schema floor, not an imagined 1); quality-diversity tiers DOUBLE
  the population/generation caps against the campaign's snapshotted
  base; legibility tiers step the parenting blend (+0.05, capped 0.9).
  Deferred axes are NAMED in the budget (`organ_role_budget` awaits an
  `allowed_roles` SLIP field; `harsher_forecasts` await weather sources
  beyond the three shipped) — never silently dropped.
- **`apply_covenant_change`**: edits the ACTIVE campaign's covenant
  within budget — over-budget requests come back with named violations
  and NOTHING applies; the authority (`validate_slip`) judges the
  result exactly as it judges every covenant; deliberation spends bump
  the profile to v0.2. Past eras stay reproducible: the ledger stores
  each era's profile verbatim (DR 0022), so a mid-campaign covenant
  change never rewrites history.
- **The earned blend flows through `advance_campaign`** — computed from
  the campaign's own facts, so batch and incremental play remain the
  SAME code path (the G4 equality pin still passes untouched).
- **The surface**: `POST /api/session/covenant` (400 + violations on
  overspend); the Keeper page gains the covenant panel — palette
  checkboxes, deliberation/population/generation inputs, each labeled
  with the earned cap and the axis that grows it.

## Verification

```powershell
PS> python -B -m unittest discover -s labs/game_loop -p "test_*.py"
Ran 56 tests in 6.239s
OK    # budget-per-axis falsifiability, spend-reaches-the-next-era
      # (the era report's population reflects the spend), overspend
      # rejected with 3 named violations and nothing applied, earned
      # blend steps the engine's readability_selection block

PS> python -B -m unittest discover -s workshop/tests -p "test_*.py"
OK    # the session flow now exercises reject-then-accept covenant spends
```

Regenerated Stage-0 session: era 0 earns legibility tiers 1+2, so eras
1–2 run at the EARNED blend 0.8 — the first campaign where progression
mechanically changes the engine's behavior mid-bloodline.

## Honest scope

- The Keeper spends between eras; an unlock earned mid-era applies from
  the next era (era params snapshot at launch — the report is the
  record).
- Organ-role and harsher-forecast budgets stay deferred with named
  reasons in the budget payload itself.

## Decision

Adopt — C4 developed to its description. Cycle 03 remaining: C6 (the
repair-validity boundary study).

## Sources

- `research/decision_records/0021-game-loop.md` (the Covenant step, the table)
- `labs/game_loop/session_runner.py` (+ `test_session_runner.py`)
- `workshop/server/workshop_server.py`, `workshop/session/session.html`
- `workshop/tests/test_workshop_server.py`
- `data/game_loop/session_runner_stage0.json` (the earned-blend session)
