# Decision Record 0040: Novelty-First at the Evolution Surface

Date: 2026-07-20

## Status

**Accepted — decision pending the measured run** (cycle 20 · Phase J,
task J3). This record pre-registers the arms and the decision rule
BEFORE the full-scale comparison runs; the decision section below is
filled by the numbers, adopt/blend/reject all first-class.

## Context

I5b measured novelty-first selection at the archive-insert instrument
(+0.078 coverage at a recorded QD cost, 235.84 → 223.85) and left
adoption to the surface that owns the trade. That surface is the E3
evolution loop (`labs/map_elites_archive/evaluation_loop_scale.py` —
the documented 20,480-evaluation generational loop, the lab truth the
game's repertoire consumer ultimately surfaces). DR 0038 moved the
landscape (baseline archive coverage 0.887 at the one-shot
instrument; the evolve loop's regenerated trajectory reaches
391/512 = 0.764) — the lever is re-judged HERE, in the loop, at the
documented budget, not extrapolated from the one-shot instrument.

For the game: archive coverage is the creature variety the repertoire
browser can ever surface; QD score is the quality of that repertoire.
The trade belongs to a record, not a hunch.

## The arms (matched scored budget, same seeds)

1. **baseline** — the loop verbatim (`selection="baseline"`,
   byte-identical to the committed artifact's path).
2. **novelty_first** — per generation the WFC path collapses
   `pool_factor × population` candidates (generation is cheap;
   SCORED evaluation is the budget, unchanged); descriptors bin the
   pool (no lifecycle spent), and the scored `population` is drawn
   novelty-first: candidates landing in niches EMPTY in the live
   archive first (within-batch first-of-bin first), then generation
   order. `pool_factor = 3` (the I5b instrument's factor).
3. **blend** — novelty-first on even generations, baseline on odd
   (the cheapest half-measure worth a number).

## Pre-registered decision rule

Judged at the matched final budget, against the baseline arm's final
`coverage` and `qd_score`:

- An arm's **coverage gain** must be ≥ **+0.02** to matter (the I5b
  bar, unchanged).
- An arm's **QD cost** must be ≤ **5%** relative
  (`qd_score ≥ 0.95 × baseline_qd`) to be adoptable.
- **ADOPT** the highest-coverage arm meeting both bars.
- **REJECT** all arms if none meets both (the lever stays a recorded
  instrument finding; the loop keeps its baseline).
- Wall-clock stays under the loop's PRE_REGISTERED_BOUND_S per arm
  (DR 0028 discipline) or the overage is recorded with the verdict.

Adoption scope on ADOPT: the E3 lab loop's default `selection`
switches to the winning arm; the game-side repertoire consumer's
wiring is the consumer's own increment (named, not smuggled here).

## Decision

**ADOPT novelty_first — by the pre-registered rule, on the measured
numbers** (2026-07-20, `data/archives/novelty_evolution_stage0.json`,
matched 20,480-evaluation budget, seed 20260709):

| Arm | Coverage | QD score | vs the bars |
| --- | --- | --- | --- |
| baseline | 0.763672 | 304.08 | — |
| **novelty_first** | **0.785156 (+0.021484)** | **310.65 (ratio 1.0216)** | **both MET** |
| blend | 0.769531 (+0.005859) | 311.02 (ratio 1.0228) | gain bar NOT met |

The trade the one-shot instrument measured (coverage at a QD cost)
DISSOLVES inside the loop: first-reachers claim niches early and the
loop's later generations refine them through elite replacement, so
novelty-first wins on BOTH axes. The E3 loop's default `selection` is
now `novelty_first`; baseline and blend stay runnable arms.

**Recorded overage**: the adopted arm's wall-clock is 774 s at the
documented budget — over the loop's original 600 s run-once bound.
The overage is the 3× generation volume (never the scoring), stdlib
holds, and this record RE-REGISTERS the loop bound at 1200 s for the
adopted default (DR 0028 discipline: the measurement cited, the bound
moved by a record, not silently).

## HONEST REMAINDER

1. `selection` stays an explicit loop parameter (the arms remain
   runnable; a landscape shift re-runs this record's rule).
2. The game-side repertoire wiring is the consumer's own increment —
   named, never smuggled here (the game's repertoire artifact builds
   from archive evidence and inherits the richer loop truth when its
   consumer regenerates).
3. Blend's near-baseline gain at full QD is recorded — half-time
   novelty buys little; the lever wants every generation.

## Sources

- `audits/TODO.md` (cycle 20 J3), `research/experiment_reports/2026-07-20-occupancy-saturation.md` (I5b — the lever's instrument)
- `labs/map_elites_archive/evaluation_loop_scale.py` (+ `novelty_evolution.py`, `test_novelty_evolution.py`)
- `data/archives/novelty_evolution_stage0.json` (the three-arm measurement)
- `research/decision_records/0032-map-elites-ga-gate-disposition.md`, `0038-vocabulary-complete-generation-alphabet.md`
