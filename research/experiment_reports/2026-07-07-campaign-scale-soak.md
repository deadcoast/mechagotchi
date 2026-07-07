# Experiment Report: Campaign-Scale Session Soak (D5) — The Spine Holds Under Load

Date: 2026-07-07

## WHY

C2/C3/C5 proved the persistence spine — the DR 0022 ledger, the promoted
`mecha_engine.storage` module, per-era replay — on short campaigns. D5
soaks it: a long chained campaign (12 eras) run deterministically over
the promoted surfaces and persisted through the promoted storage module,
with every contract verified over the FULL chain rather than one era.

## WHAT

`labs/game_loop/session_soak.py` (+ `test_session_soak.py`, 5 tests)
runs a 12-era campaign (four cycles of calm/stable/storm) and verifies:

- **determinism at scale** — the whole campaign, run twice, is equal;
- **ledger integrity** — every era ingests; each stored `report_json`
  re-canonicalizes byte-identical;
- **deterministic replay of EVERY stored era** — the DR 0022 gate 4
  exercised over all 12 eras, not one: each stored era's
  `(rng_seed, profile, weather, founder pool, earned blend)` re-run
  reproduces its stored report;
- **replay directory** — one artifact per era, each file's sha256
  matching its ledger `replays` row (C5 at scale);
- **founder-chain continuity** — every post-founder era's admitted
  founders equal the prior era's stored elites;
- **unlock-chain monotonicity** — the fact count never shrinks era over
  era ([6,6,7,7,7,7,7,7,7,8,8,8] on the shipped run).

Result: **`soak_spine_holds_at_campaign_scale`**, spine all-green,
12 eras / 67 elites / 62 founders / 8 unlocks / 12 replays ingested.

## FINDINGS — two harness faithfulness bugs, and a non-extinction

The soak first reported a spine GAP (deterministic-replay failing), and
the gap was in the study's own replay harness both times — recorded
because chasing them is the finding:

1. **The earned blend must be replayed, not defaulted.** C4 makes later
   eras run at a stepped legibility blend once a legibility tier is
   earned; the replay initially used the base 0.7. Fixed by reading the
   actual blend from the stored report (`readability_selection.blend`).
2. **`None` ≠ `[]` for `founder_grids`.** Era 0 originally ran with
   `founder_grids=None` (the DR 0016 byte-identical default — no
   founders block); the replay loaded an EMPTY pool `[]`, which is a
   legitimate but DIFFERENT input (wire ran, admitted nobody → an empty
   block). The engine contract is intentional and unchanged; the replay
   now reproduces the original `None` for the first era.

Both are the same lesson as C6: a faithful replay must reproduce the
original INPUTS exactly, and the engine's input distinctions are real.

**Non-extinction at Stage-0 scale** (extending G2): even under sustained
storm at dropout 0.9 with strict covenants, the archive never empties —
live extinction is unreachable here, so succession stays fixture-proven
(`test_campaign_store` gate 6, `test_session_runner` succession). This
soak proves the SURVIVING spine at load and records the non-extinction
as a first-class blocked state.

## Verification

```powershell
PS> python -B -m unittest discover -s labs/game_loop -p "test_session_soak.py"
Ran 5 tests in 3.614s
OK

PS> python -B labs/game_loop/session_soak.py
{
  "decision": "soak_spine_holds_at_campaign_scale",
  "era_count": 12,
  "spine_all_green": true
}
```

## Decision

`soak_spine_holds_at_campaign_scale` / adopt as lab evidence. D5
developed to its description: the C2/C3/C5 spine is load-verified over a
long chain through the promoted storage module.

## Sources

- `research/decision_records/0022-storage-module.md`
- `research/experiment_reports/2026-07-07-storage-module-promotion.md` (C3)
- `research/experiment_reports/2026-07-07-per-era-replay.md` (C5)
- `research/experiment_reports/2026-07-07-repair-validity-boundary.md` (the non-extinction finding)
- `labs/game_loop/session_soak.py` (+ `test_session_soak.py`)
- `data/game_loop/session_soak_stage0.json`
