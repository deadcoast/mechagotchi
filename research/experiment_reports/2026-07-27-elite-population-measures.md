# Experiment Report: The Archive Measured on Its Own Inhabitants (Cycle 23 · SHARED · M1)

Date: 2026-07-27

## WHY

Phase L produced one finding it never planned for, and it arrived four
separate times without anyone looking for it:

> **Every instrument measures a different population from the one the
> archive is actually filled with.**

- **L1** — the elites that hold niches forever are SLIP-illegal
  *bootstrap* creatures.
- **L2** — the dominant founder lines are *bootstrap*-founded, not
  seed-founded, though every elite was bred by the adopted layer.
- **L3** — the geometry is calibrated on `build_population` while the
  archive is filled by `generate_candidate`; the one attempt to measure
  that stream produced 120 of 600 requested, a bound only.
- **L4** — the candidate axis was judged on the derivation population,
  *because that is what every instrument uses*, and said so in its own
  remainder.

Four instruments, four different questions, one convergent answer. M1 is
that finding acted on: the instruments turned around to face the
creatures that are actually in the archive.

This is an **INSTRUMENT** slice. It changes no geometry, moves no bar,
and adopts nothing.

## WHAT

Three things the ledger reports from the derivation/bootstrap
population, re-measured on the loop's **steady-state elites**:

1. the **descriptor distribution** — where each population falls in the
   frozen (incumbent) octile geometry, per axis;
2. **octile occupancy** — how many octiles carry weight, and how far
   each shape sits from the uniform 1/8 split the geometry is *defined*
   to produce on its calibration population;
3. **L4's `animation_density` candidate** — as far as it can honestly be
   carried (see *The undefined gates*, which is this slice's sharpest
   result).

**The loop gains a third observation seam.** L2's `collect_lineage`
emits ancestry; a morphological re-measure needs the cells themselves,
so `collect_elite_grids` emits a deep **copy** of each occupied niche's
elite grid, plus its origin measured by **membership** in the loop's
bootstrap population — never inferred from lineage depth, which is L1's
recorded process error pinned so it cannot recur. Additive, exactly one
gated key, and **byte-identical when off** (pinned, both alone and
composed with the L2 seam).

### The rule, pre-registered before the run

The queue's own warning is the design constraint: *"pre-register what
counts as a material difference before running, so 'the elites look
different' cannot become a conclusion in search of a bar."*

- **The statistic** is the **total variation distance** between two
  octile histograms — a comparison of *shapes*, because the elite set
  and the derivation population differ in size by construction and
  comparing counts would report a large difference between two
  identical distributions.
- **The bar is MEASURED, never a constant** (L3's precedent). The same
  population *type* is drawn twice at different seeds; the statistic
  between those two draws is how far it moves for reasons that are not
  the population type. **Two controls are measured, one per type** — a
  derivation control and an elite control (**a second full
  documented-budget loop**) — and the bar takes the **larger**. The
  elite set is an extreme-value selection from a stochastic process, so
  assuming it is no more variable than a plain draw would understate the
  control and make "material" too easy to claim.
- A difference is **material** only at `>= 2.0 ×` the measured control,
  and **`within_sampling_noise`** otherwise. Both verdicts are
  first-class: *"the elites are indistinguishable from the derivation
  population"* is a real outcome of this study, not a failure of it.
- **The wall-clock bound is derived, not picked**: measuring an elite
  control means running the loop twice, so the bound is
  `2 × PRE_REGISTERED_BOUND_S` — two of the loop's own registered bound
  (DR 0028 discipline).

## FINDINGS

### The verdict: `within_sampling_noise` on every statistic

| statistic | derivation vs elite (TVD) | measured control | ratio | verdict |
| --- | --- | --- | --- | --- |
| symmetry | 0.084783 | 0.050000 | **1.70** | within_sampling_noise |
| visual_complexity | 0.013043 | 0.046667 | 0.28 | within_sampling_noise |
| behavior_neediness | 0.065870 | 0.055000 | 1.20 | within_sampling_noise |
| animation_density | 0.205435 | 0.242256 | 0.85 | within_sampling_noise |

Bar: `>= 2.0 ×` the measured control. The highest ratio is **1.70**.

**The gate could have fired and did not.** Read carefully, this says:
at the documented budget and one seed pair, the elites' descriptor
distribution is **not distinguishable** from the derivation
population's by this instrument. It does **not** say they are the same —
it says the difference is smaller than the measurement's own
run-to-run variation.

That is a partial deflation of this cycle's own framing, and it is
recorded as such. Phase L's convergent finding — *every instrument
measures a different population from the one the archive is filled
with* — is true in kind, and the queue was planned expecting the
difference to be large. For the **three incumbent descriptor axes it is
not**, at this power. (L3 tested its own cycle's stated premise first
and refuted it; the same discipline applies here to the premise M1 was
planned on.)

### The method finding: the elite control prevented a false positive

This is the strongest result in the slice, and it is measured rather
than argued.

The rule pre-registered **two** controls — a cheap derivation control
and an expensive elite control (a second full documented-budget loop) —
and takes the **larger**, on the stated reasoning that *"the elite set
is an extreme-value selection from a stochastic process, so assuming it
is no more variable than a plain draw would understate the control and
make 'material' too easy to claim."* That sentence was written before
the run. Then:

| `animation_density` judged against | control | ratio | verdict |
| --- | --- | --- | --- |
| the derivation control alone | 0.040000 | **5.14** | *material* |
| the elite control (the rule) | 0.242256 | **0.85** | within_sampling_noise |

A study that had measured only the obvious cheap control — the natural
design, and the one L3 used for its own different question — would have
reported `animation_density` as a **decisive material difference at 5×
the bar**. The second loop refuted it. The elite control is **6.1× the
derivation control** on this axis (0.242256 vs 0.040000): the axis that
*looks* most different is the one whose difference is **least
trustworthy**, because its distribution is the most seed-unstable of the
four.

**The premise was right where it mattered and harmlessly wrong
elsewhere**, which is worth saying plainly rather than claiming a clean
win: for the three incumbent axes the **derivation** control is the
larger one (0.050 vs 0.030; 0.047 vs 0.015; 0.055 vs 0.042). Elites are
more variable than a plain draw on exactly one of four axes — the
candidate one, which is the one the false positive would have landed on.

### Where the elites *do* sit differently — beside the verdict, outside it

Reported under L2's precedent: name the interesting shape, and do **not**
widen the bar to capture it.

- **symmetry** — the derivation population is flat by construction
  (`[75, 70, 80, 75, 75, 75, 74, 76]`); the elites are
  `[64, 57, 71, 64, 64, 64, 48, 28]`. **The top two octiles are
  depleted** — 48 and 28 against a flat expectation near 57. The
  archive's inhabitants are under-represented at the highest symmetry.
  This is the largest ratio of the four (1.70) and still short of the
  pre-registered bar: **suggestive, not established.**
- **behavior_neediness** — `[52, 58, 46, 38, 76, 71, 54, 65]`: octile 3
  depleted, octiles 4–5 enriched.
- **visual_complexity** — essentially identical (ratio 0.28). The elites
  track the derivation population on this axis.
- **No empty octiles** in either population, on any axis.

### The archive's own inhabitants, counted: 48 of 460 are bootstrap

Measured by **membership** in the loop's bootstrap population (L1's
discipline), never inferred: **48 bootstrap / 412 loop offspring =
10.4%**. The control run agrees in kind: **51 / 443 = 11.5%**.

L2 *inferred* "~48" from lineage depth, and the two agree — but calling
that independent corroboration would overstate it, so it is not
claimed. A loop offspring's depth is its parent's + 1 and every parent
is an elite, so offspring sit at depth ≥ 2 while bootstrap creatures sit
at depth ≤ 1: **depth and membership must agree here by construction.**
What M1 adds is that the count is now **measured rather than inferred**,
and it sharpens L1's process note — depth is not provenance in general
(L1's recorded error), but `depth >= 2 ⟺ loop offspring` *does* hold for
elites specifically, because of how the loop composes lineage.

**This is M3's denominator.** M3 must decide the unbreedable bootstrap
elites, and the fix trades against coverage. The population at stake is
now sized exactly: **48 of 460 occupied cells (10.4%)** are held by
bootstrap creatures, of which L2's reading of L1's flat
38-refusals-per-generation tax implies roughly half are SLIP-illegal. A
worst-case exclusion empties about a tenth of the archive.

### L4's gates on the elites: A1 holds, A2 weakens by half, A3/A4 undefined

- **A1 spread — PASS.** `supports_full_bins: true`; range 0.0111–0.4889
  (derivation 0.0112–0.600), mean 0.180 (derivation 0.192).
- **A2 independence — PASS, with half the margin.** Max |Pearson r|
  **0.350208** on the elites against **0.173412** on the derivation
  population: the correlation with symmetry roughly **doubles**
  (0.173 → 0.350), while `behavior_neediness` collapses to about zero
  (0.141 → **−0.009**). The gate still passes its 0.5 bar — and the
  axis is **less independent among the creatures the archive actually
  holds** than the derivation population indicated. Recorded because
  independence was one of L4's headline strengths.
- **A3 discrimination / A4 coverage cost — STRUCTURALLY UNDEFINED**,
  and measured to be so: same-three-axis-bin pairs among elites = **0**.
  Not "0.0 discrimination" — undefined. **No number is substituted for
  either.** See *the undefined gates* above; a dated note now sits
  beside L4's remainder, which called this measurement "cheap" when it
  is in that form impossible.

### The loop reproduced its own committed numbers exactly

**460 niches, coverage 0.898438, QD 404.618236, 80 generations** —
identical to the figures DR 0042 and L2 committed. The new seam did not
perturb the loop, *measured* as well as pinned byte-identical-when-off.
The candidate axis's reference edges reproduce L4's committed edges
exactly (`[0.097222, 0.133333, 0.157895, 0.180556, 0.2, 0.235294,
0.274402]`), so this study reads the axis against precisely L4's
reference.

Wall clock **773.482 s** against the derived **2400 s** bound (two
loops at `2 × PRE_REGISTERED_BOUND_S`) — well within. The full study was
run **twice** and every measured value is identical; the two runs differ
only in the per-run wall-clock observations, by construction.

## HONEST REMAINDERS

1. **Total variation distance carries a finite-sample bias** that grows
   as sample size falls. Both controls are size-matched within their
   type, but the derivation-vs-elite comparison mixes sizes (600 vs
   460), so part of every elite-involving distance is bias rather than
   shape. A size-matched control — subsampling the derivation to the
   elite count — would separate the two. **Deliberately not done here**:
   changing the statistic after seeing the numbers is re-scoring, which
   this repo forbids. It is named for whoever runs this next, and it
   cuts toward *smaller* true differences, so it does not threaten the
   `within_sampling_noise` verdict.
2. **"Within sampling noise" is not "the same".** The instrument bounds
   the difference; it does not establish equality. The symmetry
   depletion at the top octiles is visible and unestablished, and it is
   the obvious target for a higher-powered re-run.
3. **One seed pair.** Two loops bound the elite control; any
   distributional claim needs E4's ten-seed protocol.
4. **A3/A4 need the loop's SCORED CANDIDATE STREAM** — every creature
   evaluated, not only the winners. That is a different seam and a
   different slice, named rather than smuggled in.
5. **The candidate axis's octiles are derivation-derived** (L4's
   reference). Deriving them from the elites would compare a population
   against edges defined by itself — the degenerate in-sample case
   `occupancy_saturation` already names.
6. **The documented interpretability clause stays BLOCKED** on the
   owner-deferred human panel. **L4's verdict is untouched**:
   `adoptable_pending_blocked_clause` stands, and nothing here moves the
   axis toward adoption. A2's halved margin is a reason for the panel to
   look harder, not a machine substitute for it.

## Verification

RED — the pins written before the module existed:

```powershell
PS> python -B -m unittest test_elite_population_measures   # (from labs/map_elites_archive)
  File "...\test_elite_population_measures.py", line 38, in <module>
    from elite_population_measures import (  # noqa: E402
ModuleNotFoundError: No module named 'elite_population_measures'
----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (errors=1)
```

GREEN — the module, the seam and the study:

```powershell
PS> python -B -m unittest test_elite_population_measures
Ran 36 tests in 13.385s

OK

PS> python -B -m unittest discover -s labs/map_elites_archive -p "test_*.py"
Ran 255 tests in 79.286s

OK
```

The lab invocation that produced the artifact:

```powershell
PS> python -B labs/map_elites_archive/elite_population_measures.py
elites 460 (coverage 0.898438) vs derivation 600
  elite origin: {'bootstrap': 48, 'loop_offspring': 412} (bootstrap share 0.104348)
  symmetry             tvd 0.084783 vs control 0.050000 (x1.70) -> within_sampling_noise
  visual_complexity    tvd 0.013043 vs control 0.046667 (x0.28) -> within_sampling_noise
  behavior_neediness   tvd 0.065870 vs control 0.055000 (x1.20) -> within_sampling_noise
  animation_density    tvd 0.205435 vs control 0.242256 (x0.85) -> within_sampling_noise
  A1 supports_full_bins : True
  A2 max |r|            : 0.350208
  A3/A4                 : UNDEFINED on elites (same-bin pairs = 0)
VERDICT: WITHIN_SAMPLING_NOISE (driven by symmetry)
wrote data/archives/elite_population_measures_stage0.json
```

A recording change made **after** the first run and recorded rather than
buried: the artifact did not carry the edges its histograms were binned
against, so `frozen_edges` and `animation_density_reference_edges` were
added with a pin, and the whole study re-run. **No measured value
changed** — the re-run reproduced every number exactly, which is also
the full-scale determinism check — and the added reference is what lets
the L4 edge cross-check above be verified from the artifact alone.

## Sources

- `audits/TODO.md` (cycle 23 M1) · `research/experiment_reports/2026-07-26-phase-l-gate.md` (the convergent finding this slice acts on)
- `research/experiment_reports/2026-07-26-generation-refusal-causes.md` (L1 — origin by membership, the bootstrap elites), `2026-07-26-lineage-dominance.md` (L2 — the seam this one follows), `2026-07-26-geometry-consistency.md` (L3 — the measured-control precedent and the two geometries), `2026-07-26-animation-density-axis.md` (L4 — the gates re-measured here, and the remainder this slice corrects)
- `labs/map_elites_archive/elite_population_measures.py` (+ `test_elite_population_measures.py`) · `evaluation_loop_scale.py` (the additive `collect_elite_grids` seam)
- `data/archives/elite_population_measures_stage0.json` (the artifact) · `animation_density_axis_stage0.json`, `lineage_dominance_stage0.json`, `geometry_consistency_stage0.json`, `evaluation_loop_scale_stage0.json`, `niche_scale_archive_stage0.json`
- `docs/project-research/deep-research/01/deep-research.md` (the four-axis descriptor at 526-532; the interpretability clause at 204) · `research/questions.md` (Evolution Q2)
- `research/decision_records/0028-dependency-and-license-policy.md`, `0029-16x16-default-grid-scale.md`, `0040-novelty-first-evolution-surface.md`, `0042-generation-layer-loop-revisit.md`
