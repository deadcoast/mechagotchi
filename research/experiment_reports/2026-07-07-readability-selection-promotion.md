# Experiment Report: Readability Selection Promoted into `runtime.evolve` (C1) — The Legibility Currency Runs Live

Date: 2026-07-07

## WHY

Cycle 03 C1, named by the G2 report: DR 0021's legibility progression
axis cites `readability_selection.mean_learned_readability_by_
generation`, but that block only existed on the LAB loop — the promoted
`evolve` had no readability-aware parenting, so elite readability sat
below every earnable tier (0.16–0.24 vs the 0.25 floor) and the
currency was inert. The engine grows the number first (DR 0021's first
law); then the game shows it.

## WHAT

The DR 0020 promotion pattern, applied to the R3 seam (DR 0025):

- **The mirror** — `runtime/_readability.py`: verbatim private copies
  of `learned_readability_score` / `extract_readability_features` and
  the seven structural-feature helpers they call (copy-never-import;
  identical arithmetic, iteration order, rounding). Drift guard:
  `labs/readability_benchmark/test_package_readability_parity.py` pins
  mirror == lab authority across the whole corpus and edge cases.
- **The seam** — `evolve(readability_selection=None)` (keyword-only):
  blend of learned readability and min-max-normalized elite fitness
  steers parenting verbatim (`archive_elites_readability_blend`,
  precedence over `lineage_preferences`, per-generation candidate
  means in a rung-conditional report block). `None` byte-identical;
  weightless arms rejected.
- **The live consumer** — the session lab passes the arm on every era
  (`LEGIBILITY_BLEND = 0.7`) and the era digest carries the engine's
  own means.

## Verification

```powershell
PS> python -B -m unittest discover -s labs/readability_benchmark -p "test_package_readability_parity.py"
Ran 3 tests in 0.175s
OK

PS> python -B -m unittest discover -s labs/runtime_integration -p "test_readability_selection_parity.py"
Ran 5 tests in 5.857s
OK    # record-for-record lab parity, promoted-surface A/B (blend 0.7 > 0.0
      # post-founder), precedence pin, byte-identical default, rejection

PS> python -B -m unittest discover -s packages/mecha_engine/tests -p "test_*.py"
Ran 270 tests in 7.180s
OK

PS> python -B -m unittest discover -s labs/runtime_integration -p "test_*.py"
Ran 65 tests in 90.434s
OK    # every frozen pin unmodified

PS> python -B -m unittest discover -s labs/game_loop -p "test_*.py"
Ran 36 tests in 4.653s
OK
```

## Measurements — the currency is live, and it found something

Regenerated Stage-0 session (same seeds/config as G2, now steered):

| Era | Forecast | Elite learned readability | Engine means by generation | Unlocks |
| --- | --- | --- | --- | --- |
| 0 | calm | **0.401** (was 0.244) | 0.278, 0.207, 0.584 | legibility tiers 1+2 EARNED |
| 1 | stable_soup | 0.182 | 0.527, 0.002, 0.189 | — |
| 2 | storm | 0.014 | 0.007, 0.003, 0.011 | storm record 1 |

Eight unlock facts (was six) — the legibility axis is earnable live,
closing C1's goal. And the live currency immediately measured a real
ecosystem dynamic: **legibility drifts DOWN across chained eras**. The
feature vectors name the mechanism — era-0 vs era-2 elites: inverse
component count 0.875 → 0.567 (bodies fragment), symmetry 0.337 →
0.191, organ detectability 0.845 → 0.775. Chained founders (repaired,
renamed, re-admitted) breed structurally messier bodies, and the
learned score amplifies exactly the features it was trained to watch.
Recorded, not tuned away: this is what C4 (covenant budgets that could
counter drift) and C6 (the repair study) now have a measured target
for.

## Decision

Adopt (C1 developed to its description): the seam is promoted with the
full gate set green, and the game's legibility currency runs on the
engine's own recorded means. Next in queue: C2 (the `campaign_store`
lab, DR 0022).

## Sources

- `research/decision_records/0025-readability-selection-runtime-promotion.md`
- `research/decision_records/0019-learned-readability.md`
- `packages/mecha_engine/src/mecha_engine/runtime/_readability.py`
- `packages/mecha_engine/src/mecha_engine/runtime/evolve.py`
- `labs/readability_benchmark/test_package_readability_parity.py`
- `labs/runtime_integration/test_readability_selection_parity.py`
- `packages/mecha_engine/tests/test_runtime_contract.py` (+ driver)
- `labs/game_loop/session_runner.py`
- `data/game_loop/session_runner_stage0.json` + `data/game_loop/campaign_ledger.json`
- `research/package_specs/mecha_engine_runtime_interface_spec.md`
