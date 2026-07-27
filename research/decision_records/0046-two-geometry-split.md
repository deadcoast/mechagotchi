# Decision Record 0046: The Two-Geometry Split — Frozen, Not Converged, Because Converging Would Not Have Fixed It

Date: 2026-07-27

## Status

**ACCEPTED** — `freeze_split`, by the rule pre-registered in
`labs/map_elites_archive/geometry_decision.py` before the run.

The split is frozen **explicitly**, with its reason and a comparability
rule. Convergence was available and is **refused on the measurement**:
it would have changed which coordinate system the probe-side surfaces
use without touching the thing that actually makes their numbers
unstable.

## Context

L3 (cycle 22) found the repo runs **two** scale geometries and
deliberately did not repair it:

- **`incumbent`** — `build_population(600, seed, TRAIN, wfc_model)`,
  **frozen and committed**. `evaluation_loop_scale` and
  `coverage_qd_gates` consume it via `load_frozen_scale_edges`. Every
  coverage, QD and E4 number in the ledger lives here.
- **`probe`** — `build_population(600, seed, ALL 50 SEEDS, wfc_model)`,
  **re-derived live on every run**. `reachability_probe` and
  `occupancy_saturation` use it. Every reachability and support number
  lives here.

The edge sets differ by up to 0.0375, which L3 measured at **3.7× its
own sampling control**. So `460/512 occupied` and `508/512 reachable`
are counted in different coordinate systems and have been read against
each other in prose.

### Why L3's measurement could not decide it

L3 measured the split in **edge distance**. That is diagnostic, but it
is not the unit any ledger number is expressed in: a reader cannot tell
from *"the edges differ by 0.0375"* whether that moves one creature or
four hundred. Deciding needed the split measured in **addresses** — how
often the same creature lands in a different niche — because that is
the unit `460/512` is counted in.

## Decision

**1. The split is FROZEN, explicitly.** The two geometries stay as they
are, each named, each documented as to what it is for.

**2. The comparability rule, which is the operative part of this
record:**

> A descriptor bin index means nothing except relative to the edges that
> produced it. **Numbers measured in different geometries may not be
> read against each other.** Any claim that compares them must be
> re-measured in one geometry before it is restated.

Concretely: coverage, QD and the E4 gate means are **incumbent**
numbers; reachability counts and support ceilings are **probe** numbers.
`460/512 occupied` and `508/512 reachable` are **not** two readings of
one scale.

**3. No historical number is retracted.** Every artifact stays true
under the edges it was measured with. Coverage 0.8984, QD 404.618236
and the 460 occupied niches remain exactly what they were. What changes
is what may be *compared* with what.

**4. The direction of convergence was fixed before the measurement** —
`CONVERGENCE_TARGET = "incumbent"`, pinned in the module — so that the
measurement could decide *whether* to converge without being able to
decide *which way*. It was not triggered; the constant and its reason
stay recorded for whoever revisits this.

## Pre-registered gates

Written into the module before the run, both verdicts first-class:

- **Statistic** — the **bin disagreement rate**: the fraction of one
  common population that receives a different descriptor address under
  the two geometries.
- **Bar** — **MEASURED, never a constant**: the same recipe derived at
  two different seeds, addressed over the same population, is how far a
  geometry disagrees *with itself*. Measured for **both** recipes, with
  the **larger** taken — which makes `converge` harder to reach.
- **Rule** — `converge` at `>= 2.0 ×` the measured control;
  `freeze_split` otherwise. **Status-quo-favouring**: instruments are
  not rewired without measured cause.

## Measured verdict: FREEZE_SPLIT — and the reason is not the one expected

| quantity | measured |
| --- | --- |
| bin disagreement, incumbent vs probe | **0.360000** |
| measured control (larger of the two recipes) | **0.310333** |
| ratio | **1.16** vs the 2.0 bar |
| verdict | **`freeze_split`** |

**The verdict is driven by an enormous control, not by a small
disagreement — and that is the finding.**

| recipe | disagreement with ITSELF at another seed |
| --- | --- |
| incumbent | **0.200000** |
| probe | **0.310333** |

Re-deriving the *probe* recipe at a different seed reassigns **31% of
the population** to different niches. Re-deriving the *incumbent* recipe
reassigns **20%**. The gap between the two geometries (36%) is barely
larger than either recipe's disagreement with a resampled copy of
itself.

> **Dated note, 2026-07-27 (cycle 24 N1 / DR 0049) — these two controls
> are UNDERSTATED, and correcting them STRENGTHENS this record.** Both
> numbers above are **single draws**. N1 measured the same statistic at
> the same derivation size over **four disjoint seed pairs**: the
> incumbent mean is **0.316917** (pairs `[0.200, 0.386, 0.363, 0.319]`
> — M2 happened to draw the most favourable pair on the ladder) and the
> probe mean is **0.371583** (pairs `[0.310, 0.523, 0.349, 0.303]`).
> Re-running this record's own rule against the four-pair control gives
> **0.360000 / 0.371583 = 0.969** against the 2.0 bar, so `freeze_split`
> holds by a **wider** margin than 1.16 — the two geometries differ by
> *less* than the probe recipe differs from a resampled copy of itself.
> The sentence above is more true than when it was written. Nothing is
> retracted; the originals stand as what M2 measured. See
> `research/experiment_reports/2026-07-27-derivation-size-stability.md`.

**So the two geometries are not two principled coordinate systems. They
are two draws from a noisy edge-derivation process.** Converging them
would have picked one draw over another and changed nothing about the
instability underneath — which is precisely why convergence is refused
here rather than adopted as tidy-looking housekeeping.

### The mechanism, localised

| axis | address changes between geometries |
| --- | --- |
| symmetry | 0.053667 |
| **visual_complexity** | **0.264667** |
| behavior_neediness | 0.079000 |

One axis carries the split almost entirely. Its incumbent edges are
`[0.860816 … 0.906586]` and its probe edges `[0.854783 … 0.904185]` —
**all seven interior octile edges packed inside a band about 0.046
wide**. An edge movement far inside sampling noise therefore reassigns a
quarter of the population.

This is **K3's measure-thinness and L3's own 0.046-wide silhouette-entropy
band, now measured in addresses rather than in edge distance** — and it
ties the split directly to the quantization hypothesis L3 hardened. The
disease is not that the repo has two geometries. The disease is that
`visual_complexity`'s octiles are not determined by a 600-creature
derivation.

### The cross-geometry claim L3 named, now resolved

K2's headline was that *"460 occupied niches is **exactly** the support
ceiling the occupancy instrument measured"*. Counted over one population
here:

| geometry | support ceiling |
| --- | --- |
| probe | **460** (reproduces the committed `occupancy_saturation` artifact exactly) |
| incumbent | **456** |

L3 recorded that the identity was *not established*. This record goes
further: **the two numbers are not equal once either mismatch is
removed.** The match at 460 was a coincidence across **two** boundaries,
not one — a different geometry *and* a different population (the ceiling
is counted over a 3,000-creature evaluation population, the occupied 460
over the loop's 20,480 evaluations). A dated note now sits beside K2's
original wording, which stands as what K2 measured.

## Consequences

**What this record settles:**

- The split stands, named and documented, with the comparability rule
  above as law for future prose.
- **K3's blocking-axis instrument is NOT re-run.** The queue required
  that re-run *"if the geometry moves"*; the geometry does not move, so
  the trigger is correctly not fired. Saying so explicitly is part of
  the record.
- Convergence is refused **with its measured reason**, so a future
  session does not re-open it as unfinished tidying.

**What this record deliberately does NOT do** — each needs its own
pre-registered gate, and none is smuggled in here:

1. **Freezing the probe's edges to a committed artifact.** The
   incumbent is protected from its own 20% instability by being frozen
   once and committed; the probe has no such protection and is
   re-derived live. In practice it is deterministic (a fixed default
   seed), but its numbers are contingent on that draw in a way no
   artifact records, and a future run at a different seed or count would
   silently re-address 31% of creatures. **This is the strongest
   follow-on this record names.**
2. **Testing whether `derivation_count = 600` determines the octile
   edges at all.** The instability measured here suggests it may not,
   for `visual_complexity` in particular. That is a question about the
   derivation protocol itself (E1's), not about which population feeds
   it.

   > **Dated note, 2026-07-27 — ANSWERED by cycle 24 N1 (DR 0049), and
   > the answer splits in two.** The protocol is **`sampling_limited`,
   > not structurally indeterminate**: re-addressing falls monotonically
   > from 0.7268 at N=75 to 0.1278 at N=4800 at a log-log slope of
   > -0.4186, consistent with sampling theory's -0.5 against a measured
   > spread. So 600 does **not** determine the edges — and neither does
   > 4,800 — but the edges are reachable, not unknowable. Meanwhile the
   > **occupied-niche count** every ledger number is quoted in was
   > already at its measured floor at 600 and does **not** improve with
   > derivation size. E1's 600 therefore stays, on the measurement.
   > This record's guess above ("suggests it may not") was right about
   > the addresses and would have been wrong about the consequence.
   > **And the `~0.046-wide band` and the edge placement are separable:**
   > the band is essentially constant across a 64× range of derivation
   > sizes, so measure-thinness is **structural and permanent** while
   > only the placement inside it is sampled.
3. **Re-running the reachability numbers.** 508/512 and the four bins
   bounded by K3 stay probe-geometry numbers. Nothing here invalidates
   them; the comparability rule governs how they may be quoted.

## Sources

- `research/experiment_reports/2026-07-27-geometry-decision.md` (this record's study)
- `research/experiment_reports/2026-07-27-derivation-size-stability.md` + `research/decision_records/0049-derivation-size-and-octile-determinacy.md` (cycle 24 N1 — answers this record's second named follow-on, and corrects its two controls by dated note)
- `labs/map_elites_archive/geometry_decision.py` (+ `test_geometry_decision.py`, 20 pins) · `data/archives/geometry_decision_stage0.json`
- `research/experiment_reports/2026-07-26-geometry-consistency.md` (L3 — the diagnosis this record decides), `2026-07-21-generation-arm-loop.md` (K2 — the cross-geometry claim, now carrying a dated note), `2026-07-21-reachability-escalation.md` (K3 — measure-thinness), `2026-07-27-elite-population-measures.md` (M1 — the measured-control precedent this study follows)
- `labs/map_elites_archive/niche_scale_archive.py` (the derivation protocol), `reachability_probe.py`, `occupancy_saturation.py` (the probe-geometry consumers), `evaluation_loop_scale.py`, `coverage_qd_gates.py` (the incumbent consumers) · `labs/wfc_grid/wfc_population_throughput.py` (`load_frozen_scale_edges`)
- `data/archives/occupancy_saturation_stage0.json`, `reachability_probe_stage0.json`, `reachability_escalation_stage0.json`, `niche_scale_archive_stage0.json`
- `research/decision_records/0029-16x16-default-grid-scale.md`, `0036-neediness-scale-recalibration.md`, `0042-generation-layer-loop-revisit.md`
- `audits/TODO.md` (cycle 23 M2)
