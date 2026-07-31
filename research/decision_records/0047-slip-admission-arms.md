# Decision Record 0047: SLIP Admission — Three Arms That All Pass, and Why the Loop Default Still Does Not Move

Date: 2026-07-27

## Status

**ACCEPTED as ARMS. The loop default is NOT changed — WITHHELD, with the
reason measured.**

By the rule pre-registered in
`labs/map_elites_archive/slip_admission_arms.py` before the run, **all
three arms are adoptable** and the tie-break names **`parents`**. That
verdict stands exactly as the rule produced it. It is *not* promoted to
the loop's default, because the arms differ in the **opposite
direction** on two dimensions the pre-registered rule did not weigh —
and choosing a default requires gating those.

## Context

L1 measured the mechanism and deliberately did not fix it: all **4,435**
generation refusals are the SLIP rejecting the **parent**; 100% of those
parents are **bootstrap** creatures, built by the corpus generators
without ever being handed the profile. They win niches on fitness, hold
them (only a fitter same-niche candidate displaces them), and are
round-robined as parents forever — a flat 38-per-generation tax that
never improves.

M1 sized the population: **48 of 460 elites (10.4%) are bootstrap
creatures.** This study sharpens that by direct measurement: **35 of
those 48 are SLIP-illegal** (7.6% of the archive), and the covenant
admits only **49 of 256 bootstrap creatures — 19.1%**.

L1 refused to patch it because **the fix trades against coverage**: a
niche whose only occupant is SLIP-illegal goes **empty** if that
occupant is excluded, so "fixing" the refusals could lower the
**0.8984** coverage DR 0042 had just adopted. The three candidate
changes are not equivalent, so they are measured separately and never
blended.

## Pre-registered gates

- **G1 — the cause is eliminated**: `refusals == 0`. **Structural, not
  tuned**: L1 proved 100% of refusals are SLIP-illegal parents, so an
  arm removing the cause must reach exactly zero. A percentage-reduction
  bar would be a number nobody derived.
- **G2 — coverage is preserved**: the arm's coverage cost must not
  exceed the **MEASURED** control — the loop's own seed-to-seed coverage
  variation, measured by running the incumbent at two seeds. Never a
  constant; a coverage *gain* is never penalised.
- **Tie-break**, fixed before the run: **least invasive first** —
  `parents` < `insertion` < `bootstrap`.
- The SLIP predicate is the generation arm's own `is_grid_aligned`,
  imported and never re-implemented, so no arm can admit a creature the
  generator would refuse.

## Measured verdict

Measured control: **0.033204** coverage.

| arm | coverage | cost | niches | refusals | SLIP-illegal elites | verdict |
| --- | --- | --- | --- | --- | --- | --- |
| baseline (incumbent) | 0.898438 | — | 460 | **4,435** | **35** | — |
| `bootstrap` | 0.880859 | +0.017579 | 451 (−9) | **0** | **0** | **adoptable** |
| `insertion` | 0.880859 | +0.017579 | 451 (−9) | **0** | **0** | **adoptable** |
| `parents` | 0.886719 | +0.011719 | 454 (−6) | **0** | **35** | **adoptable** |

**G1 passes for all three, exactly as the mechanism predicted.** L1
showed every refusal is a SLIP-illegal parent; remove those from the
parent pool by *any* of the three routes and the tax goes to zero. It
did — 4,435 → 0 in every arm, with `parents` never once needing its
fallback (`parent_fallback_generations: 0`), so G1 is clean rather than
rescued.

**G2 passes for all three**: every cost is below the measured control,
so on the pre-registered evidence none of these fixes measurably costs
coverage.

**Tie-break → `parents`**, the least invasive.

## The finding beside the verdict, deliberately outside it

The rule gated **refusals** and **coverage**. It did not gate **archive
legality** or **quality** — and on both, the ranking **reverses**.

| arm | mean elite fitness | QD | archive covenant-legal? |
| --- | --- | --- | --- |
| baseline | 0.879605 | 404.618236 | no — 35 illegal |
| `bootstrap` | **0.913274** | **411.886553** | **yes — 0 illegal** |
| `insertion` | **0.912945** | **411.738214** | **yes — 0 illegal** |
| `parents` | 0.878754 | 398.954451 | no — **35 illegal** |

- **`parents` is the only arm that lowers quality.** QD falls 404.6 →
  399.0 and mean elite fitness 0.8796 → 0.8788.
- **`parents` leaves the archive covenant-illegal.** It stops the tax; it
  does **not** make the archive legal. All 35 SLIP-illegal elites remain
  in place, because the arm evicts nobody — it only declines to breed
  them.
- **`bootstrap` and `insertion` raise mean elite fitness by 3.8%** and
  produce a **SLIP-clean archive**, for three more niches (still inside
  the control).

The mechanism is legible: the SLIP-illegal bootstrap elites were holding
niches with *below-average* fitness. Removing them from the archive
raises the mean; keeping them and merely declining to breed them keeps
the dead weight **and** narrows the parent pool.

**`bootstrap` and `insertion` converge on nearly the same archive** —
451 niches, 14 bootstrap elites, QD within 0.15 of each other — by
different routes. That is structural rather than coincidental: both
remove exactly the same 207 SLIP-illegal bootstrap creatures from the
archive, and the only difference is whether those creatures are scored
before being excluded (`insertion` scores them, `bootstrap` never builds
them).

**The bar was not widened to capture any of this.** The rule is what it
was, the winner is what the rule says, and the reversal is reported
beside the verdict.

## Decision

1. **All three arms ship as runnable arms**, off by default. The
   incumbent stays byte-identical when `slip_admission="none"` (pinned).
2. **`parents` is recorded as the pre-registered rule's winner.**
3. **The loop default is NOT changed.** This is a withholding with a
   measured reason, not caution: the gate weighed refusals and coverage,
   the arms are near-tied on both, and they separate decisively on two
   dimensions the gate never looked at — *in the opposite order*.
   Promoting the gate's winner to the default would be letting a rule
   decide a question it did not ask.
4. **What would decide the default** is named rather than guessed: a
   re-run with **quality and archive legality pre-registered as gates
   alongside coverage**, over multiple seeds. On this evidence the
   likely winner is `insertion`, not `parents` — and that is exactly why
   it needs its own gate rather than a paragraph here.

   > **Dated note, 2026-07-28 — DONE by cycle 24 N4 (DR 0052), and this
   > prediction is CONFIRMED.** The decider was built exactly as named:
   > G3 quality and G4 archive legality added as gates beside G1/G2,
   > over three seeds, with this record's invasiveness tie-break carried
   > verbatim and applied only to arms clearing all four. **`parents`
   > fails G4 completely** — 35/37/35 illegal elites against the
   > incumbent's 35/37/33, evicting none — while **`bootstrap` and
   > `insertion` both clear all four**, and the tie-break picks
   > **`insertion`**. This record's withholding is therefore *resolved,
   > not overturned*: the rule was right for the questions it asked, the
   > winner was right under those questions, and refusing to promote it
   > was the right call. The incumbent reproduced this record's
   > committed baseline exactly at the shared seed (0.898438 /
   > 404.618236 / 4,435 / 35 / 460). Cost stated plainly: `insertion`
   > spends **0.029948 coverage, 90% of the measured control** — a
   > narrow pass. See
   > `research/experiment_reports/2026-07-28-slip-admission-default.md`.

## Consequences

- The 4,435-refusal tax is now **solved in principle** — three ways,
  each measured, none of them costing coverage beyond the noise floor.
  What remains is which cost the project wants to pay, not whether one
  must be paid.
- **DR 0042 is untouched.** Coverage 0.8984 and QD 404.618236 remain the
  adopted configuration's numbers; nothing here retracts them.
- **DR 0046's comparability rule applies**: every coverage and QD number
  here is an **incumbent-geometry** number and may not be read against
  reachability or support counts.
- Honest limits, recorded: **one seed per arm** against a two-seed
  control; and the arms are measured under **one SLIP profile**
  (`slip_lcd_seed`) — a wider palette would reject fewer bootstrap
  creatures and could change every cost here, so these are this
  covenant's numbers, not the mechanism's in general.

## Sources

- `research/experiment_reports/2026-07-27-slip-admission-arms.md` (this record's study)
- `research/experiment_reports/2026-07-28-slip-admission-default.md` + `research/decision_records/0052-slip-admission-default-insertion.md` (cycle 24 N4 — the decider this record named; the default is `insertion` and this record's prediction is confirmed)
- `labs/map_elites_archive/slip_admission_arms.py` (+ `test_slip_admission_arms.py`, 25 pins) · `evaluation_loop_scale.py` (the additive `slip_admission` arm) · `data/archives/slip_admission_arms_stage0.json`
- `research/experiment_reports/2026-07-26-generation-refusal-causes.md` (L1 — the mechanism and the named fix), `2026-07-27-elite-population-measures.md` (M1 — the 48-of-460 denominator), `2026-07-26-lineage-dominance.md` (L2), `2026-07-21-generation-arm-loop.md` (K2 / DR 0042 — the coverage this trades against)
- `labs/grid_genome/slip.py` (`is_grid_aligned`, the shared predicate) · `labs/grid_genome/constrained_generator.py` (`_acceptable`) · `labs/wfc_grid/wfc_population_throughput.py`
- `research/decision_records/0040-novelty-first-evolution-surface.md`, `0042-generation-layer-loop-revisit.md`, `0046-two-geometry-split.md`
- `audits/TODO.md` (cycle 23 M3)
