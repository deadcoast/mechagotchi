# Experiment Report: The Repair-Validity Boundary (C6) — A Mortal-Wound Gradient, Not an Edge

Date: 2026-07-07

## WHY

Building G2 surfaced (and the promotion-drift fix repaired) a crash:
wound-site repair can return a grid that is SLIP-ALIGNED yet
LIFECYCLE-INVALID, and the pre-fix engine ran an episode on it and
raised. The fix made the engine SKIP such a creature
(`archive_decision: skipped_invalid`). C6's job was the open QUESTION
that fix left: is the skip correct biology (a creature can be mortally
wounded), or should wound-site repair guarantee a connected core (an
engine-contract evolution)? Decide with evidence, not assertion.

## WHAT — and a methodology correction made mid-study

`labs/repair_boundary/repair_validity_boundary.py` measures the boundary
on the PRODUCTION surface (`runtime.evolve`) across a regime grid
(dropout {0.2…0.95} × cycles {1,2,4}) over 10 rng seeds, counting
`skipped_invalid` from each report's own per-creature
`archive_decision`; a cause diagnosis reproduces the mechanism
(deep candidate → `live_cycle` at heavy damage) and validates the
resulting bodies to NAME the failing invariant.

Two false starts, both recorded because they are the finding's spine:

1. A first reconstruction over pristine seeds accumulated `grid_id`
   suffixes each cycle and overflowed the schema's 64-char cap — the
   study was measuring its own harness bug (the `live_cycle` "known
   trap"), not biology. Fixed by reassigning the id per cycle.
2. The fixed reconstruction then found ZERO invalid repairs — because
   `lifecycle.initial_state` and the study both use the same
   `validate_grid`, so a grid the study calls valid never crashes the
   episode. The aligned-but-invalid body only emerges inside the
   multi-generation `evolve` loop, where candidates are bred from
   candidates and lineage deepens under sustained damage. The study was
   pivoted to measure the real production surface.

## FINDING — hypothesis refuted

| Regime (dropout × cycles) | skipped_invalid rate |
| --- | --- |
| 0.2 × 1 (mildest) | 0.025 |
| 0.2–0.4 × 1–2 (**session band**) | **0.0125** |
| 0.6 × 4 | 0.050 |
| 0.9 × 4 | 0.100 |
| 0.95 × 4 (harshest) | 0.0875 |

The pre-study hypothesis — that aligned-but-invalid repairs appear
ONLY at extreme damage — is **REFUTED**. The failure is present at the
mildest damage measured and rises roughly monotonically with it: a
**damage-scaled mortality gradient**, ~1.25% in the shipped session
band, climbing to ~10%. Almost every skip is `skipped_invalid` (aligned
but invalid), not `skipped_unaligned` (a normal death) — 2 unaligned
across the entire sweep. The cause diagnosis is unambiguous: the ONLY
invariant that fails is **"required body core is disconnected"** — a
creature whose core was shattered by repeated damage its repair could
not reconnect.

## VERDICT — the skip is retained as correct biology

A mortality curve that scales with damage is precisely what a survival
engine should produce; the shipped skip handles it gracefully (no
episode, `skipped_invalid`) and the game reads it as extinction
pressure (DR 0021's stakes). The alternative — a connected-core repair
CONTRACT — is REJECTED: forcing reconnection would flatten the
mortality curve to zero, manufacturing survival the physics did not
grant and breaking the game's first law. The low in-band rate keeps it
a rare event, not a common frustration. If a future difficulty curve
judges the rate too high, the repair MODEL's core-preservation (a
tuning lever, not a forced contract) is the recorded thing to study —
not this verdict reopened.

## Verification

```powershell
PS> python -B -m unittest discover -s labs/repair_boundary -p "test_*.py"
Ran 4 tests in 6.179s
OK

PS> python -B labs/repair_boundary/repair_validity_boundary.py
{
  "decision": "boundary_is_a_mortal_wound_gradient_skip_retained",
  "hypothesis": "REFUTED",
  "session_band_rate": 0.0125,
  "harshest_regime_rate": 0.0875,
  "cause": {"required body core is disconnected": 6}
}
```

## Decision

`boundary_is_a_mortal_wound_gradient_skip_retained` / adopt as
evidence. C6 developed to its description — the boundary is measured,
the invariant named, the hypothesis honestly refuted, the verdict
evidence-backed. This is cycle 03's final task; the TODO is exhausted.

## Sources

- `research/experiment_reports/2026-07-07-game-loop-session-runner.md` (the drift fix that raised the question)
- `research/algorithm_cards/repair_validity_boundary.md`
- `labs/repair_boundary/repair_validity_boundary.py` (+ `test_repair_validity_boundary.py`)
- `data/repair_boundary/repair_validity_boundary_stage0.json`
- `packages/mecha_engine/src/mecha_engine/runtime/evolve.py` (the `skipped_invalid` decision)
- `packages/mecha_engine/src/mecha_engine/genome/validation.py` (the body-core invariant)
- `research/decision_records/0021-game-loop.md` (extinction stakes)
