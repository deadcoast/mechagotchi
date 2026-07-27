# Decision Record 0049: The Derivation Protocol Is Sampling-Limited, Not Structurally Indeterminate — and E1's 600 Is Not Raised, Because What It Would Fix Is Not What Was Broken

Date: 2026-07-27

## Status

**ACCEPTED** — by the two gates pre-registered in
`labs/map_elites_archive/derivation_size_stability.py` before the run.

E1's `derivation_count = 600` **stays**. Raising it was available, is
cheap, and measurably improves address stability — and it is declined
**on the measurement**, because the quantity every ledger number is
counted in was already at its measurement floor at 600 and no affordable
derivation size moves it.

## Context

DR 0046 froze the two-geometry split and, in its own consequences, named
a defect larger than the question it had been asked:

> **Testing whether `derivation_count = 600` determines the octile edges
> at all.** The instability measured here suggests it may not, for
> `visual_complexity` in particular. That is a question about the
> derivation protocol itself (E1's), not about which population feeds it.

E1 derives the whole scale geometry from a 600-candidate population.
Every coverage, QD and E4 number in the ledger is counted against the
edges that derivation produced. If 600 does not determine them, the
defect sits underneath all of it.

DR 0046's prose also carried a diagnosis that turns out to fuse two
different things: *"the disease is that `visual_complexity`'s octiles are
not determined by a 600-creature derivation"*, offered alongside the
observation that its seven interior edges sit inside a band about 0.046
wide. Those are separable claims, and they have different answers.

## Pre-registered gates

Written into the module before the run, every verdict first-class. The
statistic is DR 0046's own — the **re-addressing rate** R(N), the
fraction of one common evaluation population landing in a different
niche under two independent derivations of size N — because a niche is a
whole address and edge distance is not the unit any ledger number is
expressed in.

- **Gate 1 (mechanism)** — fit `log R` against `log N`. Empirical
  quantile estimates converge at N^-1/2, so ordinary sampling error
  gives a slope of **-0.5**. Judged against the **MEASURED** spread of
  four independent per-track slopes at 2.0×, never against a threshold:
  `sampling_limited` if theory lies inside the measured band,
  `structurally_indeterminate` if the curve is materially flatter,
  `faster_than_sampling` if steeper.
- **Gate 2 (practical)** — derivation-induced movement in
  **occupied-niche count**, against a **MEASURED** floor: the movement
  that same count shows when the edges are held fixed and only the
  evaluation population is resampled. `determined_at` is the smallest
  ladder size reaching it; `not_determined_within_reach` is first-class.

Ladder 75 · 150 · 300 · 600 · 1200 · 2400 · 4800, over both recipes,
four disjoint seed pairs per rung.

**The instrument was required to reproduce committed numbers first** —
DR 0046's incumbent control (0.2) and probe control (0.310333) at N=600
on M2's own seed pair. Both **reproduced exactly**, as did the committed
frozen `visual_complexity` edges.

## Measured verdict

### Gate 1 — `sampling_limited` on both recipes

| recipe | slope | measured spread | consistent band | verdict |
| --- | --- | --- | --- | --- |
| incumbent | **-0.418611** | 0.096942 | [-0.612495, -0.224727] | `sampling_limited` |
| probe | **-0.399656** | 0.065990 | [-0.531636, -0.267676] | `sampling_limited` |

**The structural-indeterminacy reading is refuted.** Re-addressing falls
monotonically down the whole ladder — incumbent 0.7268 at N=75 to
**0.1278** at N=4800 — at a rate consistent with sampling theory. The
edges are not beyond the reach of a derivation population; they are
under-sampled at 600.

Both point estimates run *flatter* than -0.5 and the probe's band clears
theory by only 0.032, so this is "consistent with sampling", not "equal
to it".

### Gate 2 — the gates disagree, and the disagreement is the finding

| recipe | verdict | determined_at | movement at N=600 |
| --- | --- | --- | --- |
| incumbent | `determined` | **600** | **4.000** (floor 4) |
| probe | `not_determined_within_reach` | — | 5.750 |

At N = 600 the incumbent re-addresses **31.7% of individual creatures**
while its **occupied-niche count moves exactly the measured floor** —
indistinguishable from resampling the evaluation population and never
touching the derivation at all.

**And more budget does not help the aggregate.** At N = 4800
re-addressing has improved 2.5× to 12.8% while ceiling movement is
**7.75**, *higher* than at 600. What limits the aggregate is not the
derivation.

So the question has two true answers: **600 creatures do not determine
the octile edges — and neither do 4,800 — but they do determine the
numbers the ledger quotes, as far as this instrument can resolve, and
they already did.**

## Decision

**1. E1's `derivation_count` stays at 600.** Not from caution: raising it
demonstrably buys address stability (31.7% → 12.8% at 8× budget, ~13
minutes of wall clock). It is declined because **the thing it would fix
is not the thing that was broken**. Every committed coverage, QD and E4
number is an occupied-count statistic, and Gate 2 measures those as
already at their floor. Changing the derivation size would re-address a
third of the population, invalidate the frozen edge artifact, and move no
number anyone quotes.

**2. The protocol is recorded as SOUND, so it is not re-opened as
unknowable.** A future session reading DR 0046's *"may not determine them
at all"* would be reading a hypothesis this record has tested. The
instability is sampling error with a measured convergence rate, and a
consumer who needs address-level stability can buy it — this record names
the price rather than leaving it as folklore.

**3. Measure-thinness and edge placement are DIFFERENT PROPERTIES, and
prose must stop fusing them.** The `visual_complexity` edge band is
**essentially constant across a 64× range of derivation sizes**
(incumbent 0.043993 at N=75, 0.045196 at N=4800):

> The ~0.045-wide band is a permanent property of the silhouette-entropy
> distribution and **no derivation budget narrows it**. What sampling
> buys is *where the seven edges sit inside that fixed band*. K3's
> measure-thin windows are therefore structural and are not a
> small-sample artifact.

This sharpens rather than contradicts DR 0046: the axis carries the
instability because its band is thin, and the thinness is not going away.
`visual_complexity` is also the **slowest-converging** axis rather than
merely the noisiest — at N=75 it is the *smallest* per-axis contributor
on the incumbent and by N=4800 it carries **49%** of all axis movement,
the other two having converged out from under it.

**4. DR 0046's controls are CORRECTED as understated, by dated notes
beside the originals.** They were single draws; the four-pair means at
the same size are **0.316917** (incumbent, against 0.200000 recorded) and
**0.371583** (probe, against 0.310333). M2 drew the most favourable
incumbent pair on the ladder.

**DR 0046's verdict is unchanged and strengthened.** Its ratio of 1.16
becomes **0.360000 / 0.371583 = 0.969** against the same 2.0 bar: the two
geometries differ by *less* than the probe recipe differs from a
resampled copy of itself. `freeze_split` holds by a wider margin and
DR 0046's central sentence — *"two draws from a noisy edge-derivation
process"* — is more true than when it was written. Nothing is retracted.

**5. No geometry moves and no number is retracted.** DR 0046's
comparability rule stands unchanged.

## A limitation of this record's own pre-registration

Gate 2's rule says *"the smallest ladder size whose movement falls at or
below the floor"*, which assumes monotone convergence. **The movement is
not monotone** — incumbent `10.0, 15.5, 9.75, 4.0, 4.75, 7.5, 7.75`.

The verdict stands as the rule produced it; re-scoring after seeing the
numbers is what this repo forbids. But `determined_at = 600` is **a noisy
statistic crossing a threshold, not a located stability point**. The
honest reading is that ceiling movement plateaus near the floor from
N ≈ 600 and jitters around it. Two further reasons to hold it loosely:
the incumbent passes by an **exact tie** (4.000 against a floor of 4)
with pair movements spanning `[0, 6, 1, 9]`, and the floor itself is
measured from **three pairs** (`[2, 6, 4]`) — too coarse to resolve 4.0
from 5.75, which is the whole distance between the two recipes' Gate-2
verdicts. **They should not be read as a real difference between the
recipes.**

Decision 1 does not rest on `determined_at`. It rests on the direction
the ladder establishes over 64×: the aggregate does not improve with
derivation size while addresses do.

## Consequences

**What this record settles:**

- E1's derivation size is decided, with its reason measured rather than
  assumed, and the price of the alternative recorded.
- The protocol is sound; "the edges may be indeterminate" is closed.
- Measure-thinness is structural; edge placement is sampled. Prose that
  fuses them is now wrong by this record.
- DR 0046's controls carry dated corrections that strengthen its verdict.

**What this record deliberately does NOT do:**

1. **Freeze the probe's edges.** That is N2's charter and needs its own
   gate. This record does give N2 its size guidance: the probe's
   aggregate never reaches the floor within reach and its re-addressing
   at N=4800 (0.129333) is level with the incumbent's, so **freezing at
   a larger derivation size buys address stability but not aggregate
   stability** — and freezing at E1's 600 keeps the two recipes
   comparable in size, which is worth more than a marginal rung.
2. **Locate the knee.** Gate 2's floor is too coarse. A study that wanted
   to *place* rather than bound it needs many more evaluation pairs and a
   distance-weighted movement statistic.
3. **Establish the exponent.** Four tracks per recipe bound the slope's
   spread; they do not prove -0.5, and both point estimates run flatter.
4. **Re-run any consumer.** No reachability, coverage or QD number is
   recomputed here, and none needed to be.

## Sources

- `research/experiment_reports/2026-07-27-derivation-size-stability.md` (this record's study)
- `labs/map_elites_archive/derivation_size_stability.py` (+ `test_derivation_size_stability.py`, 43 pins) · `data/archives/derivation_size_stability_stage0.json`
- `research/decision_records/0046-two-geometry-split.md` (the record whose remainder this answers, and whose controls this corrects by dated note)
- `research/experiment_reports/2026-07-27-geometry-decision.md` (M2), `2026-07-26-geometry-consistency.md` (L3), `2026-07-21-reachability-escalation.md` (K3 — measure-thinness), `2026-07-09-niche-scale-archive.md` (E1 — the protocol)
- `labs/map_elites_archive/niche_scale_archive.py` (`derive_scale_bin_edges`, `build_population`) · `labs/wfc_grid/wfc_population_throughput.py` (`load_frozen_scale_edges`)
- `research/algorithm_cards/niche_scale_archive.md`
- `research/decision_records/0029-16x16-default-grid-scale.md`, `0036-neediness-scale-recalibration.md`, `0028-dependency-and-license-policy.md`
- `audits/TODO.md` (cycle 24 N1)
