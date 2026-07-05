# Experiment Report: Mecha Engine Evolution Loop

Date: 2026-07-05

## Objective

Extend the runtime integration loop to multi-generation evolution: archive
elites become parents, and every creature survives repeated damage/repair
cycles with full lifecycle episodes between regenerations. This is the
composed engine doing what the research plan built it for — variation,
selection through MAP-Elites niche fitness, regeneration, and inheritance —
and the final evidence input for the `mecha_engine.runtime` target
proposal (decision record 0008).

## Design

- Generation 0 parents: the profile-aligned seed pool (18/50 seeds for
  the LCD profile). Generations 1+: the archive's elites, sorted by niche
  key for determinism, round-robin.
- Per creature: generate → validate → `damage_cycles` × (seeded damage
  event → SLIP-aware wound-site repair → full episode) → final episode →
  score → insert into the archive. Grid ids are reassigned per cycle
  (the 64-char cap trap).
- Fitness and archive trajectories are reported as measurements; the
  decision gates only on contract-holding (validity, alignment,
  position restoration, everything archived, elites actually reproduced).

## Verification

RED (functions did not exist):

```powershell
python -B -m unittest discover -s labs/runtime_integration -p "test_*.py"
# ImportError -> FAILED (errors=1)
```

GREEN (9 tests: single-gen loop + evolution loop, determinism pinned):

```txt
Ran 9 tests in 18.243s
OK
```

Test-honesty note: an early assertion required every damage event to
remove at least one cell; a stochastic event can legitimately remove zero
(≈5% at dropout 0.2 on ~14 live cells), making repair a no-op. The test
now asserts the position guarantee per cycle and nonzero damage across
the run.

Lab command (4 generations × 8 creatures × 3 damage cycles, 72-tick
episodes, ~3 minutes):

```powershell
python -B .\labs\runtime_integration\mecha_engine_runtime_loop.py --mode evolution
```

```txt
"creature_count": 32, "total_damage_events": 96,
"candidate_valid_rate": 1.0, "slip_alignment_retention_rate": 1.0,
"mean_position_restoration": 1.0, "mean_token_restoration": 0.975259,
"guard_substitution_total": 12, "archived_creature_count": 32,
"mean_fitness_by_generation": [0.932076, 0.920086, 0.926957, 0.920902],
"archive": {"filled_niches": 15, "qd_score": 13.92259}
"decision": "evolution_loop_composed"
```

## Findings

1. **Elites reproduce and the engine holds.** All 32 creatures across 4
   generations validate, stay SLIP-aligned through 96 damage events
   (retention 1.0), restore their exact silhouettes (position 1.0, token
   0.9753), and score back into the archive — which grows 10 → 15 niches
   (QD 9.29 → 13.92) as offspring of elites discover new niches.
2. **The SLIP-aware guard earns its keep under repetition**: 12
   substitutions across the run (vs 1 in the single-cycle loop) — repeated
   damage hits profile-required organs regularly, and every hit was
   repaired into a simulatable creature.
3. **Fitness is flat, honestly reported** (≈0.92–0.93 per generation):
   with survival saturated at 1.0 and readability an uncalibrated proxy,
   the fitness surface currently has little gradient for selection to
   climb — a measurement, not a gate. Expect selection pressure to mean
   something once calibrated readability and harder survival regimes
   exist.
4. **Lineage-counter nuance**: `max_lineage_generation` reads 2 despite
   4 generations because repair reconstruction (`grid_from_matrix`)
   resets the numeric lineage counter; true ancestry is the parent-id
   chain, which deepens correctly. Accumulating the counter through
   repair would change promoted-module output semantics (parity
   implications) — recorded as future work, not patched silently.

## Decision

Status: `evolution_loop_composed`. The composed engine runs
multi-generation evolution with regeneration under contract. Evidence
basis for decision record 0008 (the `mecha_engine.runtime` target
proposal) is complete. Follow-ups, value order: (a) owner review of DR
0008; (b) lineage-counter accumulation through repair (parity-reviewed);
(c) longer-horizon evolution studies once calibrated readability exists
(owner-deferred data, not chased).

## Sources

- `labs/runtime_integration/mecha_engine_runtime_loop.py`
- `labs/runtime_integration/test_mecha_engine_runtime_loop.py`
- `data/runtime_integration/mecha_engine_evolution_loop_stage0.json`
- `data/runtime_integration/mecha_engine_runtime_loop_stage0.json`
- `research/experiment_reports/2026-07-05-mecha-engine-runtime-loop.md`
- `research/experiment_reports/2026-07-05-slip-aware-repair-guard.md`
- `research/algorithm_cards/mecha_engine_runtime_loop.md`
- `research/decision_records/0008-propose-mecha-engine-runtime-target.md`
