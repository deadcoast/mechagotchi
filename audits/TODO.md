# Development TODO — Standby: the queue is honestly empty

Cycle 07 (the v1.0 consolidation) is archived complete at
`audits/complete/07/`. Seven cycles are archived in full (01–07); the
realization-wave report (`research/reports/
mechagotchi_research_report_v1_0.md`) consolidates the state: ten of
ten og module targets realized, "Eras of the Soup" live end to end with
all five DR 0021 player-notices, the dataset→consumer→adopted-model
chain closed, 1,210 tests green.

**Per the planning rule, this queue was exhausted and confirmed
COMPLETE — and the honest plan is that NO agent-actionable task
remains.** Everything left is either an owner decision or a named
re-opener waiting on a condition. Manufacturing tasks to fill a queue
would violate the governing rule (deep integrations over breadth;
hard/unique features win — and nothing hard or unique is currently
unbuilt against the ratified designs).

## The owner-decision menu (not tasks; act only on owner direction)

1. **The repo-wide license grant** — pending since T21; SPDX plumbing
   and the REUSE layout are ready.
2. **The `[project]` dependencies policy** — deliberately blocked;
   unblocking is a policy choice, not a need (everything ships
   stdlib-only).
3. **Manual readability calibration** — pipeline ready
   (`mechas rate --creatures --autoexport`, 0/63 rows); resume when
   the sample set stabilizes. The learned model remains primary; this
   is its calibration check.
4. **Real CuBFF export ingest** — the optional drop-in seam (cycle 04
   decision): drop real simulator exports into
   `data/cubff_real_ingest/source_snapshots/` and run the ingest lab;
   zero code changes needed.
5. **Publishing/pushing** — commits are local; push on direction.
6. **New game/engine direction** — the next era of the project is a
   design conversation, not a backlog item.

## Named re-openers (each fires on its condition, citing its record)

- `mecha_engine.render` — when a non-workshop Python consumer needs to
  rasterize a packet (DR 0026).
- Repair core-preservation tuning — if the mortal-wound rate is ever
  judged too high for the difficulty curve (C6's verdict).
- Grid-level `species_class` — when mixed-species soups make
  per-creature species load-bearing (DR 0024).
- Extinction-at-scale soak — if a future regime makes live extinction
  reachable, re-run the D5 soak to exercise succession under load.

## Standing note

The identity constraint and DR 0017 govern: the engine is the
application, the game is its showcase. The rating system is the
fallback; `.depreciated/` is the owner's archive (ignore unless
linked).

## Sources

- `audits/complete/01/`–`audits/complete/07/` (every cycle, archived)
- `research/reports/mechagotchi_research_report_v1_0.md` (+ manifest)
- `research/decision_records/0017-recalibration-engine-game-duality.md`
- `docs/agent-standards.md` (refreshed to this state, cycle 07 V2)
