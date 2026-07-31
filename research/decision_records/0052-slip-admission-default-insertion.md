# Decision Record 0052: The `slip_admission` Default Is `insertion` — DR 0047's Withholding Resolved, Its Prediction Confirmed

Date: 2026-07-28

## Status

**ACCEPTED** — `ADOPT_DEFAULT → insertion`, by the four gates
pre-registered in `labs/map_elites_archive/slip_admission_default.py`
before the run.

DR 0047 withheld this default and named exactly what would decide it.
That decider was built as named, and it **confirms DR 0047's
prediction**: `insertion`, not the old tie-break's `parents`.

## Context

L1 measured a flat **4,435-refusal tax** per run: the loop keeps drawing
parents that the covenant rejects, because SLIP-illegal bootstrap
creatures win niches on fitness and are then round-robined as parents
forever. M3 built three fixes and **all three take the tax to zero**.

M3's rule gated refusals and coverage, and named `parents` its winner.
**DR 0047 then refused to promote its own winner**, because `parents` is
the worst of the three on two dimensions the rule never asked about — it
lowers quality and leaves every illegal creature seated in the archive.
It recorded the decider precisely: *quality and archive legality
pre-registered as gates alongside coverage, over multiple seeds*, and
predicted `insertion` while insisting the prediction get its own gate.

## Pre-registered gates

Four, refusal first-class. **The pre-registration mattered more than
usual**: DR 0047 published a prediction, and a gate written after the
numbers arrive cannot refute the prediction it exists to test.

- **G1 — cause eliminated**: `refusals == 0`, structural (DR 0047's,
  unchanged), now required **on every seed** — a mean would let a clean
  seed hide a dirty one.
- **G2 — coverage preserved**: cost ≤ the **measured** seed-to-seed
  control (DR 0047's, unchanged in shape, wider in evidence). A gain is
  never penalised.
- **G3 — quality preserved** *(new)*: QD must not fall below the
  incumbent's by more than the **measured** seed-to-seed QD control.
  Same shape as G2; a gain is never penalised.
- **G4 — archive legality** *(new)*: zero SLIP-illegal elites on **every
  seed**. **Structural, exactly like G1**, on DR 0047's own reasoning: a
  covenant either holds over the archive it bred or it does not, and a
  percentage bar would be a number nobody derived.

**Tie-break: DR 0047's invasiveness order verbatim** (`parents` <
`insertion` < `bootstrap`), applied only among arms clearing all four.
That single change of *set* is the whole mechanism by which this record
overturns DR 0047's winner without touching its rule.

**The instrument was required to reproduce the study it decides for.**
The first seed is DR 0047's seed, so the incumbent must reproduce its
committed baseline exactly — coverage 0.898438, QD 404.618236, 4,435
refusals, 35 illegal elites, 460 niches. **All five reproduced.** The
configuration is read from DR 0047's *artifact*, never its prose, and a
mismatch is refused rather than run.

## Measured verdict

Controls (the incumbent's own seed-to-seed spread): coverage
**0.033204**, QD **16.560333**.

| arm | coverage cost | Δ QD | refusals | illegal elites | verdict |
| --- | --- | --- | --- | --- | --- |
| `bootstrap` | +0.029948 | −0.0353 | 0 / 0 / 0 | **0 / 0 / 0** | **ADOPTABLE** |
| `insertion` | +0.029948 | −0.1356 | 0 / 0 / 0 | **0 / 0 / 0** | **ADOPTABLE** |
| `parents` | +0.004558 | −2.5059 | 0 / 0 / 0 | **35 / 37 / 35** | **FAILS G4** |

**`parents` fails archive legality completely**, not marginally: 35, 37
and 35 illegal elites against the incumbent's 35, 37 and 33. It declines
to breed the illegal creatures and evicts none of them — exactly the
behaviour DR 0047 described and could not gate.

**`bootstrap` and `insertion` are indistinguishable on the gated
dimensions** — identical coverage on all three seeds, QD within 0.1 —
which is structural: both remove the same illegal bootstrap creatures,
differing only in whether those creatures are scored before exclusion.
So the tie-break decides between them on invasiveness alone, on an order
fixed before any of this was measured.

## Decision

**1. The adopted `slip_admission` default is `insertion`.** It clears
all four gates and is the least invasive arm that does.

**2. DR 0047's withholding is RESOLVED, not overturned.** Its rule was
correct for the questions it asked; its winner was correct under those
questions; and its refusal to promote that winner was the right call.
This record adds the two questions DR 0047 said were missing and reaches
the answer it predicted.

**3. The cost is stated, not softened.** `insertion` costs **0.029948
coverage — 90% of the measured control.** A pass, and a narrow one. What
it buys is 4,435 wasted evaluations per run removed and an archive that
is legal under the covenant that bred it. QD is untouched (−0.1356
against a control of 16.56).

**4. `parents` is dispositioned REJECTED as a default** — it remains a
runnable arm, but it cannot be the default, because an arm that leaves
the archive covenant-illegal does not fix the thing the covenant exists
to guarantee.

**5. The migration is scheduled, not assumed.** This record adopts the
default; it does not flip it. `run_evaluation_loop` still defaults to
`slip_admission="none"`, and changing that rewrites every artifact of
**at least six lab modules** that call the loop without naming an arm —
`evaluation_loop_scale`, `coverage_qd_gates`,
`elite_population_measures`, `family_ancestry`,
`generation_refusal_causes` and `lineage_dominance` — including
**DR 0042's headline coverage 0.8984** and **L1's entire subject** (its
4,435 refusals become 0). At ~380 s per loop run with a delta to explain
per artifact, that is its own task: **queued as N7 with this cost
measured**, not left floating.

## What this record does NOT do

1. **It does not change any committed number.** Coverage 0.8984, QD
   404.618236 and the 460 niches stand as the incumbent's, and DR 0042
   is untouched until the N7 migration explains each delta.
2. **It does not reach the promoted engine.** `slip_admission` appears
   nowhere in `packages/`; promoting the fix there is a separate step
   with its own spec and gate.
3. **It does not widen the evidence beyond one SLIP profile**
   (`slip_lcd_seed`) — DR 0047's own recorded limit, inherited. A wider
   palette rejects fewer bootstrap creatures and could move every cost.
4. **It does not measure eviction.** No arm removes an already-seated
   illegal elite; DR 0047's fourth candidate is still unmeasured.

## Process deviation, recorded

**The first run of this study used `population=512` — a parameter the
module invented rather than inherited — and it produced the wrong
answer.** M3 measured at 256 (also the loop's own documented default).
At 512 the incumbent did not reproduce DR 0047's baseline, and
`insertion` failed G2 by **0.000652** (2% of the control), leaving
`bootstrap` the sole passer. A hair's-width miss on the wrong
configuration would have refuted a correct prediction.

Caught by checking the discrepancy rather than accepting the verdict,
corrected, and re-run. Two guards now prevent silent recurrence:
`load_dr0047_baseline()` reads DR 0047's parameters from its artifact,
and `judge_configuration_match()` refuses a diverging run. Both pinned.
The 512 run is **not** offered as a robustness check; it was an error.

## Sources

- `research/experiment_reports/2026-07-28-slip-admission-default.md` (this record's study)
- `research/decision_records/0047-slip-admission-arms.md` (the withholding this resolves, and the prediction this confirms)
- `labs/map_elites_archive/slip_admission_default.py` (+ `test_slip_admission_default.py`, 36 pins) · `data/archives/slip_admission_default_stage0.json`
- `labs/map_elites_archive/slip_admission_arms.py` (the arms, imported never re-implemented) · `evaluation_loop_scale.py` (the loop and its `slip_admission` seam)
- `research/experiment_reports/2026-07-26-generation-refusal-causes.md` (L1), `2026-07-27-elite-population-measures.md` (M1), `2026-07-27-slip-admission-arms.md` (M3)
- `research/decision_records/0042-generation-layer-loop-revisit.md`, `0046-two-geometry-split.md`, `0028-dependency-and-license-policy.md`
- `data/archives/slip_admission_arms_stage0.json` (the committed baseline reproduced exactly)
- `audits/TODO.md` (cycle 24 N4; the N7 migration this record schedules)
