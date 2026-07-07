# Algorithm Card: Game-Loop Session Runner (era chain over the promoted engine)

- **Name**: Keeper session runner — deterministic era chain composing
  `mecha_engine.runtime.evolve` with founder re-admission, forecast
  weather, threshold-data unlocks, and pointer-chain succession.
- **Purpose**: G2 (decision record 0021) — the executable proof that
  "Eras of the Soup" runs end to end over PROMOTED surfaces only: the
  game loop is engine truth, not invented UI.
- **Mathematical basis**: iterated MAP-Elites evolution with
  re-seeding — era N's founder pool is era N−1's elite set E(N−1)
  ordered by niche key, re-admitted through the engine's own
  validity/alignment gates; unlock facts are monotone threshold
  predicates `metric(era) >= t` over report metrics (thresholds are
  data); extinction is the engine's measured empty-archive fixed point
  (generations ran < requested, or E = ∅); succession resolves unlock
  state as the union over the predecessor pointer chain (no copying).
- **Inputs**: seed corpus, SLIP profile (the covenant), weather
  schedule (forecast names → CuBFF snapshot sets; `calm` = None, the
  byte-identical default), base seed, evolve parameters, the R3 learned
  readability model (legibility currency), package trainers' models.
- **Outputs**: campaign record (eras with VERBATIM evolve reports +
  derived metrics, each derived value pinned to engine truth), unlock
  facts citing resolvable metric paths, the DR 0022 schema-v1 JSON
  ledger (campaigns/eras/elites/founders/unlocks/replays), stage-0
  report.
- **Strengths**: every mechanic maps to a shipped engine mechanism
  (DR 0021's first law); deterministic end to end; ledger migration to
  the SQLite storage module is lossless by construction; thresholds
  falsifiable on fixtures both directions.
- **Weaknesses**: one SLIP covenant per campaign (mid-campaign covenant
  adjustment is the C4 slice). The legibility-currency weakness closed
  2026-07-07: DR 0025 promoted readability selection into
  `runtime.evolve`, the session steers every era at blend 0.7, and the
  axis is earnable live — which immediately measured legibility
  DRIFTING DOWN across chained eras (0.401 → 0.014), a real dynamic
  queued for C4/C6.
- **Failure modes**: live extinction unobserved at Stage-0 scale (the
  repair guard holds alignment through 0.95 probe dropout) — detection
  is contract-based and succession fixture-proven, not live-measured;
  building G2 exposed the aligned-but-invalid promotion drift in
  `runtime.live_cycle` (episodes crashed lifecycle simulation at the
  measured boundary — fixed, RED-first, verbatim lab-semantics sync).
- **Integration risk**: low — pure composition over public promoted
  surfaces; no engine state mutated; weather seam upgrades to real
  CuBFF exports with zero session-runner changes.
- **License status**: original stdlib implementation.
- **Prototype result**: three-era live session — 10/10 and 9/9 founders
  admitted across the chain; stable soup measurably shields (58 removed
  cells at 0.90x vs calm's 65) while the storm's 1.17x earns the
  storm-record unlock; 6 unlock facts earned, every metric path
  resolving in its cited era record; 19/19 lab tests green.
- **Decision**: adopt (lab evidence for the game-loop track); the
  readability-selection promotion seam and the storage lab
  (`campaign_store`, DR 0022) are the identified successors.
- **Go-No-Go gate**: deterministic session equality; chained-era
  founder ids equal to prior elites with engine-verbatim admission;
  storm > stable measured damage at a fixed seed; unlock fixtures pass
  met-must-unlock AND unmet-must-not; ledger derived columns equal
  their blob fields; absent weather byte-identical.

## Sources

- `research/decision_records/0021-game-loop.md`
- `research/decision_records/0022-storage-module.md`
- `research/experiment_reports/2026-07-07-game-loop-session-runner.md`
- `labs/game_loop/session_runner.py` (+ `test_session_runner.py`)
- `data/game_loop/session_runner_stage0.json`
- `data/game_loop/campaign_ledger.json`
- `packages/mecha_engine/src/mecha_engine/runtime/evolve.py`
