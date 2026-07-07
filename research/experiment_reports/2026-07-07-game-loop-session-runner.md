# Experiment Report: The Game-Loop Session Runner (G2) — One Full Keeper Session over the Promoted Engine

Date: 2026-07-07

## WHY

DR 0021 ("Eras of the Soup") fixed the game's design: an era is one
`runtime.evolve` run, a campaign is the chain of eras persisted through
`founder_grids`, weather is a CuBFF pressure source, progression
currencies are report metrics verbatim, and everything shown is engine
truth. Build gate G2 demands the executable proof: one full Keeper
session running over the PROMOTED surfaces only — era-chaining, weather
selection, unlock evaluation, extinction and succession — deterministic,
triad convention, JSON-artifact persistence interim until the `storage`
module (DR 0022) lands.

## WHAT

`labs/game_loop/session_runner.py` (+ `test_session_runner.py`, 19
tests) composes `mecha_engine.runtime.evolve` with the package trainers
and runs a three-era campaign:

- **Era-chaining** — era N submits era N−1's archive elites (niche-key
  order, the same ordering evolve uses for elite parents) as
  `founder_grids`; the engine's own gates re-admit them (DR 0016
  admission/rejection recorded verbatim). Live session: era 1 admitted
  10/10, era 2 admitted 9/9; both chained eras report
  `parent_source: founders_plus_seed_pool`.
- **Weather** — forecasts `calm` (no source, byte-identical default),
  `stable_soup`, `storm` map to synthetic CuBFF snapshot sets; the
  engine's `cubff_pressure` block is the weather record, snapshot
  provenance included. Real exports stay honestly blocked
  (`awaiting_real_cubff_snapshots`) and drop into the same seam with no
  session-runner change.
- **Unlocks** — facts computed from era-record metrics against
  threshold DATA (`UNLOCK_THRESHOLDS`; DR 0021: tuning, not
  architecture), each citing the metric path and value that earned it.
  Falsifiability is pinned both ways on fixture era records (met must
  unlock; unmet must not; earned never re-earns) and every live fact's
  path is asserted to resolve in its cited era record.
- **Extinction & succession** — extinction is detected on the report
  contract (the engine's measured empty-archive early end, or an era
  with zero elites); an extinct campaign's successor carries ONLY the
  Keeper's unlock facts, resolved through the predecessor pointer
  without copying (DR 0022's succession rule), and starts a fresh
  bloodline from seeds.
- **Persistence interim** — `build_campaign_ledger` emits the DR 0022
  schema-v1 vocabulary (campaigns/eras/elites/founders/unlocks/replays)
  with every engine report stored verbatim and derived columns pinned
  equal to their blob fields by test — the future
  `ingest_session_artifacts` migration source.

## Live session measurements (`data/game_loop/session_runner_stage0.json`)

| Era | Forecast | Removed cells | Max multiplier survived | Founders admitted | Filled niches | QD | Elite learned readability |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | calm | 65 | — | — (seed pool) | 10 | 9.194 | 0.244 |
| 1 | stable_soup | 58 | 0.8998 | 10/10 | 9 | 8.181 | 0.177 |
| 2 | storm | 65 | 1.1702 | 9/9 | 10 | 9.030 | 0.165 |

The weather physics read correctly from engine truth: a stable soup
(multiplier ≈0.90) SHIELDS the ecosystem relative to calm (58 vs 65
cells removed at the same base dropout), while the storm's 1.17x
multiplier earns the storm-record unlock. Six unlock facts were earned
live (niche_mastery 1–2, bloodline_depth 1, quality_diversity 1–2,
storm_record 1); the **legibility axis earned nothing, honestly** —
elite mean learned readability at the promoted surface (0.16–0.24)
sits below the earnable tiers because R3's readability-aware parent
selection is a LAB-loop consumer not yet promoted into
`runtime.evolve`; promoting that seam is the identified path to a
live legibility currency (a natural successor task, not claimed here).

## FINDING — promotion drift: the missing validity gate (fixed)

Building G2 crashed the promoted engine at ordinary session parameters:

```text
ValueError: invalid grid for lifecycle simulation: required body core is disconnected
```

Root cause: since T1 (commit d382805) the LAB evolution loop gates
cycle episodes on `valid AND aligned` — an aligned-but-invalid repair
(heavy damage leaving a disconnected core after wound-site repair)
carries no episode, the creature records
`archive_decision: skipped_invalid`, and scoring requires
`all_cycles_valid`. The promoted `runtime.live_cycle`/`evolve` were
ported BEFORE that gate existed and were never synced: `live_cycle` ran
episodes for any aligned repair and crashed lifecycle simulation. No
frozen parity pin caught it because no pinned seed produces an invalid
repair (probe 2026-07-07: 8 of 60 scanned seeds hit the boundary at
dropout 0.95 with 4 cycles; the session's storm era hit it at
0.2 × 1.6-band multipliers).

Fix (verbatim lab-semantics sync, RED first):
`packages/mecha_engine/src/mecha_engine/runtime/live.py` episode gate
`if aligned` → `if valid and aligned`;
`evolve.py` scoring gate gains `all_cycles_valid` and the
`skipped_invalid` decision. Spec amended
(`mecha_engine_runtime_interface_spec.md`, "Validity gate on
episodes"). Pinned-seed parity artifacts are byte-identical — all 60
runtime-integration tests (including every frozen pin) and all
package contract tests pass unmodified.

### Verification — RED

```powershell
PS> python -B -m unittest discover -s labs/runtime_integration -p "test_invalid_repair_semantics.py"
ValueError: invalid grid for lifecycle simulation: required body core is disconnected
Ran 4 tests in 1.357s
FAILED (errors=4)
```

### Verification — GREEN

```powershell
PS> python -B -m unittest discover -s labs/runtime_integration -p "test_invalid_repair_semantics.py"
Ran 4 tests in 1.391s
OK

PS> python -B -m unittest discover -s labs/runtime_integration -p "test_*.py"
Ran 60 tests in 56.853s
OK

PS> python -B -m unittest discover -s packages/mecha_engine/tests -p "test_*.py"
Ran 267 tests in 4.231s
OK
```

(The package suite now includes the `invalid_repair_boundary` contract
probe — 268 tests after this report's suite extension; the lab-side
boundary parity pin is `test_invalid_repair_semantics.py`, which also
asserts lab and package reports agree record-for-record at the
boundary seed.)

### Verification — Lab

```powershell
PS> python -B -m unittest discover -s labs/game_loop -p "test_*.py"
Ran 19 tests in 2.184s
OK

PS> python -B labs/game_loop/session_runner.py
{
  "artifact_id": "game_loop_session_runner_stage0",
  "decision": "session_loop_composed",
  "era_count": 3,
  "unlock_fact_count": 6,
  "output_dir": "...\\data\\game_loop"
}
```

## Honest scope

- **Extinction did not occur live at Stage-0 scale**: the repair guard
  holds SLIP alignment through probe dropout up to 0.95; detection and
  succession are contract-implemented and fixture-proven (the DR 0021
  falsifiability pattern). Beyond ~0.9 dropout with 4+ cycles lies the
  aligned-but-invalid boundary above — now a skip, never a crash.
- **Real CuBFF weather** remains blocked on the ingest gate
  (`awaiting_real_cubff_snapshots`); synthetic forecasts carry the
  measured low/high pressure signatures.
- **SQLite persistence** waits on the `storage` module's own lab and
  promotion gates (DR 0022); the JSON ledger interim carries the full
  schema-v1 vocabulary so the migration is lossless.
- Era 1's engine decision is `evolution_loop_gaps_measured` (one
  creature fell short of a module contract mid-loop) — recorded as the
  engine reports it; the session loop does not require all-green eras.

## Decision

`session_loop_composed` / adopt as lab evidence (gate G2 developed to
its description). Next: G4 (the Keeper's surface), R5 (replay — the
Review step's window), the storage lab (`campaign_store`, DR 0022), and
the identified readability-selection promotion seam.

## Sources

- `research/decision_records/0021-game-loop.md`
- `research/decision_records/0022-storage-module.md`
- `research/decision_records/0016-evolve-founder-grids.md`
- `research/decision_records/0018-cubff-live-lineage-pressure.md`
- `research/decision_records/0019-learned-readability.md`
- `research/decision_records/0020-cubff-pressure-runtime-promotion.md`
- `labs/game_loop/session_runner.py`
- `labs/game_loop/test_session_runner.py`
- `labs/runtime_integration/test_invalid_repair_semantics.py`
- `packages/mecha_engine/src/mecha_engine/runtime/live.py`
- `packages/mecha_engine/src/mecha_engine/runtime/evolve.py`
- `packages/mecha_engine/tests/test_runtime_contract.py`
- `packages/mecha_engine/tests/helpers/runtime_contract_driver.py`
- `research/package_specs/mecha_engine_runtime_interface_spec.md`
- `data/game_loop/session_runner_stage0.json`
- `data/game_loop/campaign_ledger.json`
