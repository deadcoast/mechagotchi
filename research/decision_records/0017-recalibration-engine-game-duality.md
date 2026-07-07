# Decision Record 0017: Recalibration — the Engine+Game Duality

Date: 2026-07-06

## Status

**Accepted** (owner FEEDBACK, 2026-07-06 — "recalibration, further
design and development; not deletion").

## The North Star, restated so it cannot drift

The application is a duality:

1. **The engine**: an innovative integration of the Google CuBFF
   experiment, the repository's mathematical research, and clever
   development, producing REAL, UNIQUE output — CuBFF-scale exponential
   growth, TRUE machine learning where applicable.
2. **The game**: an incremental progression, survival and simulation
   game that showcases the engine — a living ecosystem the PLAYER
   NOTICES adapting.

Neither survives alone: the engine needs the game to be exceptional or
no one discovers it; the game needs the engine to be exceptional or no
one plays it. Every future development choice traces to this duality,
and when a hard/unique feature competes with an easy/generic one, the
hard one wins — with the choice stated aloud.

## The honest drift finding

Verified against git history (deletion filter over the deep-track labs
is EMPTY): nothing was deleted. `labs/cubff_transducer/` (semantic
transducer + real-snapshot ingest), `labs/ctm_ticks/`, and the NCA labs
all stand with their tests. **The real failure is integration debt**:
the deep tracks were proven in labs and left there. The running engine
generates with a Markov hybrid, learns with a reward-mean bandit, and
scores readability against a proxy awaiting manual labels — while the
CuBFF lineage signals, CTM deliberation, and any learned model sit
unwired. From the owner's seat that is indistinguishable from removal.
This record converts that debt into the priority queue below.

A second inversion is corrected permanently: the manual readability
rating system is the **FALLBACK**, never the assignment. The assignment
is a learned/automatic readability mechanism; the rating system stays
exactly as built — a customizable QoL fallback and calibration check —
and "manual calibration deferred" is never again framed as a blocker.

## The corrective development queue (R-tasks, priority order)

| # | Task | The duality it serves |
| --- | --- | --- |
| R1 (=T8) | **CTM deliberation into the runtime switchboard**: confidence-gated extra thinking cycles, measured for decision quality and felt aliveness | the creature visibly *thinks* — game feel from engine math |
| R2 | **CuBFF live lineage pressure**: the transducer's Pipeline C (lineage dynamics → mutation weights) wired into the ACTUAL evolution loop, so real computational-life dynamics shape every generation | (a.1)+(a.3): CuBFF stops being a lab exhibit and becomes the engine's bloodstream |
| R3 | **Learned readability**: a model trained from engine-derived signals (proxy features, survival outcomes, structural metrics) — TRUE ML as the primary path, the manual rating system as its fallback/calibration | (a.4): no human hand-training as the design |
| R4 | **The game loop decision record**: incremental progression, survival sessions, persistence (unlocks the deferred `storage` module), what the player does and notices per session | (a.2)+(b.2): the showcase |
| R5 (=T12) | Replay recorder + workshop scrubber | the player's window into engine truth |
| R6 (=T11) | Dataset program completion (mechaseed_200, mutationbench_5000, replay_100k_ticks) | the ML tracks' fuel |
| R7 (=T7) | Grid-schema animation/species fields: implement or record the projection design as the superseding decision | closes the audit honestly |

## Consequences

- `audits/TODO.md` gains the R-queue; completed tasks are marked only
  when developed to their descriptions.
- A stale-language sweep removes every "blocked on manual calibration"
  framing from living docs.
- Memory records (owner-side) pin the duality, the fallback rule, and
  the `.depreciated/` scope so no future session re-drifts.

## Sources

- Owner FEEDBACK (2026-07-06), `.depreciated/01-design.md` [1] (the core disclaimer)
- `labs/cubff_transducer/`, `labs/ctm_ticks/`, `labs/cellular_automata/`
- `research/algorithm_cards/cubff_transducer.md`, `ctm_inspired_ticks.md`
- `audits/audit-devspec.md`, `audits/TODO.md`
