# Experiment Report: Do 600 Creatures Determine the Octile Edges? — No for the Edges, Yes for the Number the Ledger Quotes (Cycle 24 · SHARED · N1)

Date: 2026-07-27

## WHY

M2 (DR 0046) was sent to decide L3's two-geometry split and came back
with something bigger than the question it was asked. Its *control* —
re-deriving the same recipe at a different seed — reassigned **20%** of a
population under the incumbent recipe and **31%** under the probe. The
two geometries differed by 36%, barely more than either differed from a
resampled copy of itself, so the split was frozen and convergence
refused. DR 0046 then named the real defect in its own consequences:

> **Whether `derivation_count = 600` determines the octile edges at all**
> is an open question about E1's derivation protocol itself.

That sits *underneath every coverage number in the ledger*: E1 derives
the scale geometry from a 600-candidate population, and every coverage,
QD and E4 figure is counted against the edges that derivation produced.

N1 measures the protocol. **It moves no geometry and retracts no
number** — it asks whether the process that produces them determines
them, and both answers are real findings.

## WHAT

**The rule, pre-registered in the module before the run**
(`labs/map_elites_archive/derivation_size_stability.py`), every verdict
first-class.

**The statistic** is the **re-addressing rate** R(N): the fraction of one
common, fixed evaluation population that receives a **different
descriptor address** under two independent derivations of size N. This is
DR 0046's control statistic as a function of derivation size, and
deliberately DR 0046's unit — a niche is a whole address, and edge
distance is not the unit any ledger number is expressed in.

Measured over **four disjoint seed pairs** per rung, so every rate
carries a measured spread rather than a single draw.

**Gate 1 — the mechanism. Is the instability curable by spending
derivation budget?** Empirical quantile estimates converge at N^-1/2, so
if the re-addressing is ordinary sampling error, R(N) falls with a
log-log slope of **-0.5**. Judged against the **MEASURED** spread of four
independent per-track slopes at 2.0× (the repo's control factor applied
to a measured spread, never to a threshold):

- `sampling_limited` — theory lies inside the measured band; the
  protocol is sound and 600 is merely small.
- `structurally_indeterminate` — the curve is materially **flatter**; no
  affordable population determines the edges. **This is what K3's
  measure-thinness and L3's 0.046-wide band predict.**
- `faster_than_sampling` — steeper than theory.

**Gate 2 — the practical question. Is 600 enough for what the edges are
USED for?** The ledger does not quote individual addresses; it quotes
occupied-niche counts. So the second gate is measured in that unit
against a **measured floor**: hold the edges fixed and resample only the
**evaluation** population, and the occupied count moves by an amount that
has nothing to do with derivation size. `determined_at` is the smallest
ladder size reaching that floor; `not_determined_within_reach` is
first-class.

**The two gates were pre-registered as able to disagree**, and the module
docstring says why that would matter: addresses can be wildly unstable
while the aggregate they feed is not, and reporting only one of them
would be the kind of sentence Phase M kept catching.

**Ladder**: 75 · 150 · 300 · 600 · 1200 · 2400 · 4800 — bracketing E1's
own 600 on both sides and spanning 64×, over **both** recipes L3 named
(the incumbent draws from TRAIN, the probe from all 50 seeds), because N2
must choose a size to freeze the probe **at**.

### The instrument validates itself against committed numbers first

Two checks, both passed before any rung was read:

| check | committed | measured |
| --- | --- | --- |
| DR 0046 incumbent control at N=600, M2's seed pair | 0.2 | **0.2** |
| DR 0046 probe control at N=600, M2's seed pair | 0.310333 | **0.310333** |

The replicate seeds begin at `DEFAULT_RNG_SEED` on the repo's existing
disjoint-stream stride, so **pair 0 IS M2's pair** by construction rather
than by a special case. The first replicate's `visual_complexity` edges
at N=600 also reproduce the committed frozen set verbatim
(`[0.860816 … 0.906586]`). Without these, no rung on the ladder would be
interpretable.

## FINDINGS

### Gate 1: `sampling_limited` on both recipes — the instability is ordinary sampling error

| recipe | slope | measured spread | consistent band | verdict |
| --- | --- | --- | --- | --- |
| incumbent | **-0.418611** | 0.096942 | [-0.612495, -0.224727] | **`sampling_limited`** |
| probe | **-0.399656** | 0.065990 | [-0.531636, -0.267676] | **`sampling_limited`** |

The theory slope of -0.5 lies inside both measured bands. Per-track
slopes: incumbent `[-0.4096, -0.2977, -0.5339, -0.4332]`, probe
`[-0.3147, -0.3914, -0.4729, -0.4197]`.

**So the structural-indeterminacy reading is REFUTED.** The edges are not
beyond the reach of a derivation population — they are simply
under-sampled at 600. Re-addressing falls monotonically all the way down
the ladder:

| N | incumbent R(N) | probe R(N) |
| --- | --- | --- |
| 75 | 0.726833 | 0.670167 |
| 150 | 0.559750 | 0.596167 |
| 300 | 0.413917 | 0.530250 |
| **600** | **0.316917** | **0.371583** |
| 1200 | 0.258500 | 0.261916 |
| 2400 | 0.169333 | 0.205500 |
| 4800 | **0.127833** | **0.129333** |

**Read honestly**: both point estimates sit *flatter* than -0.5
(-0.419, -0.400), and the probe's band clears theory by only 0.032. The
verdict is "consistent with sampling", not "equal to sampling" — if the
true slope is genuinely flatter, convergence is slower than theory and
every size below buys less than N^-1/2 would promise. Bounded, not
established.

### Gate 2: the two gates disagree — and the disagreement IS the answer

| recipe | verdict | determined_at | movement at N=600 |
| --- | --- | --- | --- |
| incumbent | **`determined`** | **600** | **4.000** (floor = 4) |
| probe | **`not_determined_within_reach`** | — | 5.750 (minimum 4.250 at N=2400) |

The floor is measured, not assumed: the committed frozen edges held
fixed while the evaluation population is resampled move the occupied
count by `[2, 6, 4]` niches across three disjoint pairs → **4**.

Now put the two gates side by side at E1's own size:

> At N = 600 the incumbent re-addresses **31.7% of individual
> creatures** — and its **occupied-niche count moves 4 niches, exactly
> the floor**, which is to say indistinguishable from resampling the
> evaluation population and never touching the derivation at all.

**And spending more does not help the aggregate.** At N = 4800
re-addressing has fallen to 12.8% — a 2.5× improvement in address
stability — while ceiling movement is **7.75**, *higher* than at 600. The
aggregate was already at its measurement floor at 600 and no affordable
derivation size improves it, because what limits it is not the
derivation at all.

So the title question has two different true answers:

- **Do 600 creatures determine the octile edges?** **No.** Nor do 4,800:
  a third of creatures change niche at 600 and an eighth still do at
  4,800.
- **Do 600 creatures determine the numbers the ledger quotes?**
  **Yes — as far as this instrument can resolve**, and they already did.

### A limitation of THIS study's own pre-registration, recorded not repaired

Gate 2's rule says *"the smallest ladder size whose movement falls at or
below the floor"*. That wording assumes the movement converges
monotonically. **It does not.** Incumbent ceiling movement across the
ladder runs `10.0, 15.5, 9.75, 4.0, 4.75, 7.5, 7.75` — it falls to the
floor at 600 and then rises again.

The verdict stands as the rule produced it, because re-scoring a gate
after seeing its numbers is exactly what this repo forbids. But the
honest reading of the curve is **not** "600 is the size at which the
geometry stops moving". It is that **ceiling movement plateaus at
roughly the floor from N ≈ 600 onward and then jitters around it**, and
`determined_at = 600` is a noisy statistic crossing a threshold rather
than a located stability point.

Two further reasons to hold it loosely, both visible in the numbers:

1. **The incumbent's verdict turns on an exact tie** — movement 4.000
   against a floor of 4, passing by `<=`. Its four pair movements are
   `[0, 6, 1, 9]`, a spread far wider than the floor itself.
2. **The floor is measured from three pairs** (`[2, 6, 4]`). A floor
   that coarse cannot resolve the difference between 4.0 and 5.75, which
   is the entire distance between the incumbent's `determined` and the
   probe's `not_determined_within_reach`. **The two recipes' Gate-2
   verdicts should not be read as a real difference between them.**

### The mechanism: measure-thinness is STRUCTURAL, edge placement is SAMPLED — and M2 fused them

M2 localised the split to `visual_complexity`, whose seven interior
octile edges sit inside a band about 0.046 wide, and concluded *"the
disease is that `visual_complexity`'s octiles are not determined by a
600-creature derivation"*. The ladder separates two things that sentence
runs together. The band width does **not** narrow with data:

| N | incumbent vc band | probe vc band |
| --- | --- | --- |
| 75 | 0.043993 | 0.048585 |
| 600 | 0.045185 | 0.048260 |
| 4800 | 0.045196 | 0.047415 |

**Essentially constant across a 64× range.** The thinness is a property
of the silhouette-entropy distribution itself — permanent, and no
derivation budget touches it. What sampling buys is *where the seven
edges sit inside that fixed band*, and that is what converges.

The per-axis rates show `visual_complexity` is the **slowest-converging**
axis rather than simply the noisiest. At N=75 it is the *smallest*
contributor on the incumbent (vc 0.2388 against neediness 0.4630); by
N=600 it leads (0.1465); by N=4800 it leads by more, carrying **49%** of
all axis movement (vc 0.0624, neediness 0.0420, symmetry 0.0287). The
other two axes converge out from under it. That is exactly what a thin
band predicts — the same edge displacement re-addresses more creatures
where the density is highest — and it makes K3's and L3's measure-thin
windows a permanent feature of the axis, not a small-sample artifact.

### CORRECTED (DR 0046's controls, understated — a dated note, nothing retracted)

DR 0046's controls are **single draws**. Measured over four disjoint
pairs at the same size:

| recipe | DR 0046 (pair 0) | N1 four-pair mean | pair spread |
| --- | --- | --- | --- |
| incumbent | 0.200000 | **0.316917** | `[0.200, 0.386, 0.363, 0.319]` |
| probe | 0.310333 | **0.371583** | `[0.310, 0.523, 0.349, 0.303]` |

M2 happened to draw the **most favourable incumbent pair on the ladder**
(0.200 against a mean of 0.317). Both controls were therefore understated.

**M2's verdict is unchanged and strengthened.** Its rule compared a
disagreement of 0.360000 against the larger control (0.310333) for a
ratio of 1.16 against a 2.0 bar. Against the four-pair control the larger
is 0.371583, giving **0.360000 / 0.371583 = 0.969** — the two geometries
now differ by *less* than the probe recipe differs from a resampled copy
of itself. `freeze_split` holds by a wider margin, and DR 0046's central
sentence — *"they are two draws from a noisy edge-derivation process"* —
is more true than when it was written, not less.

Dated notes sit beside DR 0046 and its experiment report. No number is
retracted; the originals stand as what M2 measured.

### What did NOT confound this

**The generator is not saturating.** Distinct-grid fraction stays at
1.0000 through N=600 and falls only to **0.9935** (incumbent) and
**0.9938** (probe) at N=4800. A derivation population that had stopped
producing new creatures would show as a geometry that had stopped
moving; it does not, and the ladder measures this rather than assuming
it. Saturation *is* beginning, so a ladder beyond 4,800 would need to
watch it harder.

## HONEST REMAINDERS

1. **This study moves no geometry and freezes nothing.** Acting on it is
   N2's charter. Whether E1's `derivation_count` should be raised is a
   consumer's decision, and DR 0049 records why it is not raised here.
2. **Gate 2's floor is too coarse to locate a size** (three pairs, and a
   verdict turning on an exact tie). A study that wanted to *place* the
   knee rather than bound it needs a floor measured over many more
   evaluation pairs, and a distance-weighted movement statistic.
3. **The evaluation population shares an rng seed with the second
   derivation replicate**, inherited from M2's construction so DR 0046
   reproduces exactly. The draws differ in size and source corpus, so
   they are not identical — but they are not formally independent
   either. Recorded rather than silently re-seeded, because re-seeding
   would have cost the reproduction check that makes the ladder
   interpretable.
4. **The re-addressing statistic counts an address change of any size**
   — DR 0046's own remainder, inherited unchanged. A creature moving one
   octile counts the same as one moving three on all three axes.
5. **One common evaluation population carries every rung**, so the
   ladder measures derivation instability against a fixed ruler and says
   nothing about how R(N) would move on a different evaluation draw.
6. **The slopes are consistent with -0.5, not equal to it**, and both
   point estimates run flatter. Four tracks per recipe bound the spread;
   they do not establish the exponent.

## Verification

RED — the pins, written before the module existed:

```powershell
PS> python -B -m unittest test_derivation_size_stability   # (from labs/map_elites_archive)
E
======================================================================
ERROR: test_derivation_size_stability (unittest.loader._FailedTest.test_derivation_size_stability)
----------------------------------------------------------------------
ImportError: Failed to import test module: test_derivation_size_stability
Traceback (most recent call last):
  File "C:\Python314\Lib\unittest\loader.py", line 137, in loadTestsFromName
    module = __import__(module_name)
  File "labs\map_elites_archive\test_derivation_size_stability.py", line 26, in <module>
    from derivation_size_stability import (  # noqa: E402
    ...<18 lines>...
    )
ModuleNotFoundError: No module named 'derivation_size_stability'


----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (errors=1)
```

GREEN:

```powershell
PS> python -B -m unittest test_derivation_size_stability
----------------------------------------------------------------------
Ran 43 tests in 40.980s

OK
```

The lab invocation that produced the artifact (the DR 0028 wall-clock
pilot runs FIRST, and its projection of 752.15 s is what the 826.247 s
ladder was budgeted against):

```powershell
PS> python -B labs/map_elites_archive/derivation_size_stability.py
{
  "context": "stage-0 dev machine; excludes one-time seed/model setup; one unit is mixed constrained+WFC generation of one candidate plus its three scale-axis measurements (no lifecycle scoring - a derivation population is never scored)",
  "derivation_unit": {
    "sample_count": 200,
    "build_ms_total": 923.79,
    "axis_ms_total": 63.29,
    "mean_ms_per_grid": 4.9354
  },
  "projections": {
    "ladder_grid_total": 152400,
    "full_ladder_s": 752.15
  }
}

evaluation-resampling floor: 4 niches

[incumbent]
  N=75    re-address 0.726833 (+/-0.139100)  ceiling move 10.000  vc band 0.043993  distinct 1.0000
  N=150   re-address 0.559750 (+/-0.118866)  ceiling move 15.500  vc band 0.045923  distinct 1.0000
  N=300   re-address 0.413917 (+/-0.063634)  ceiling move 9.750  vc band 0.045486  distinct 1.0000
  N=600   re-address 0.316917 (+/-0.082654)  ceiling move 4.000  vc band 0.045185  distinct 0.9983
  N=1200  re-address 0.258500 (+/-0.132783)  ceiling move 4.750  vc band 0.045102  distinct 0.9975
  N=2400  re-address 0.169333 (+/-0.026504)  ceiling move 7.500  vc band 0.044938  distinct 0.9950
  N=4800  re-address 0.127833 (+/-0.019676)  ceiling move 7.750  vc band 0.045196  distinct 0.9935
  GATE 1 slope -0.418611 (spread 0.096942) -> SAMPLING_LIMITED
  GATE 2 determined_at 600 (floor 4) -> DETERMINED
  DR 0046 control: committed 0.2, measured 0.2 -> REPRODUCED

[probe]
  N=75    re-address 0.670167 (+/-0.091171)  ceiling move 15.500  vc band 0.048585  distinct 1.0000
  N=150   re-address 0.596167 (+/-0.130751)  ceiling move 30.500  vc band 0.048584  distinct 1.0000
  N=300   re-address 0.530250 (+/-0.085389)  ceiling move 17.000  vc band 0.048489  distinct 1.0000
  N=600   re-address 0.371583 (+/-0.103171)  ceiling move 5.750  vc band 0.048260  distinct 1.0000
  N=1200  re-address 0.261916 (+/-0.032707)  ceiling move 5.500  vc band 0.048084  distinct 0.9983
  N=2400  re-address 0.205500 (+/-0.039257)  ceiling move 4.250  vc band 0.047336  distinct 0.9958
  N=4800  re-address 0.129333 (+/-0.019197)  ceiling move 5.500  vc band 0.047415  distinct 0.9938
  GATE 1 slope -0.399656 (spread 0.06599) -> SAMPLING_LIMITED
  GATE 2 determined_at None (floor 4) -> NOT_DETERMINED_WITHIN_REACH
  DR 0046 control: committed 0.310333, measured 0.310333 -> REPRODUCED

wrote data/archives/derivation_size_stability_stage0.json
```

The archive lab, and the full sweep. The baseline is **measured, not
quoted**: the Phase-M gate records 319, but `ce6b063` (the PR-review
round, landed after that report was written) added 3 pins to
`test_slip_admission_arms.py`, so the pre-N1 count is **322** and
`319 + 43` would not have reconciled. Quoting the gate figure would have
propagated a stale number exactly the way the 52-vs-54 family count did.

```powershell
PS> python -B -m unittest discover -s labs/map_elites_archive -p "test_*.py"
----------------------------------------------------------------------
Ran 365 tests in 105.238s

OK

PS> python -B tools/ci/run_sweep.py
lab:animation_system             OK  OK  [10.0s]
lab:architecture                 OK  OK  [15.8s]
lab:asset_pipeline               OK  OK  [0.4s]
lab:cellular_automata            OK  OK  [34.5s]
lab:ctm_ticks                    OK  OK  [0.1s]
lab:cubff_transducer             OK  OK  [0.5s]
lab:datasets                     OK  OK  [2.6s]
lab:game_loop                    OK  OK  [6.6s]
lab:grid_genome                  OK  OK  [7.0s]
lab:lifecycle_sim                OK  OK  [0.4s]
lab:map_elites_archive           OK  OK  [110.8s]
lab:micro_threads                OK  OK  [8.0s]
lab:package_promotion            OK  OK  [0.1s]
lab:readability_benchmark        OK  OK  [2.7s]
lab:repair_boundary              OK  OK  [3.3s]
lab:runtime_integration          OK  OK  [80.8s]
lab:slip_validator               OK  OK  [0.6s]
lab:wfc_grid                     OK  OK  [6.0s]
lab:workshop_editor              OK  OK  [6.2s]
package                          OK  OK  [7.2s]
cli                              OK  OK (skipped=15)  [3.7s]
game                             OK  OK (skipped=5)  [12.3s]
workshop                         OK  <sys>:0: ResourceWarning: unclosed <socket.socket fd=428, family=2, type=1, proto=0, laddr=('127.0.0.1', 3957)>  [179.8s]
data artifacts                   OK  2241 JSON artifacts valid  [0.5s]

SWEEP GREEN
```

## Sources

- `audits/TODO.md` (cycle 24 N1) · `research/decision_records/0049-derivation-size-and-octile-determinacy.md` (the record this study produced)
- `research/experiment_reports/2026-07-27-geometry-decision.md` (M2 — the study whose remainder this answers, and whose controls now carry a dated note), `2026-07-26-geometry-consistency.md` (L3 — the split's diagnosis), `2026-07-21-reachability-escalation.md` (K3 — measure-thinness), `2026-07-09-niche-scale-archive.md` (E1 — the derivation protocol measured here)
- `research/decision_records/0046-two-geometry-split.md` (the comparability rule and the controls corrected here), `0029-16x16-default-grid-scale.md`, `0036-neediness-scale-recalibration.md`, `0028-dependency-and-license-policy.md` (the wall-clock-first discipline)
- `labs/map_elites_archive/derivation_size_stability.py` (+ `test_derivation_size_stability.py`, 43 pins) · `data/archives/derivation_size_stability_stage0.json`
- `labs/map_elites_archive/niche_scale_archive.py` (`derive_scale_bin_edges`, `build_population`, `scale_axis_values`) · `labs/wfc_grid/wfc_population_throughput.py` (`load_frozen_scale_edges`)
- `research/algorithm_cards/niche_scale_archive.md` (the protocol's card, updated with this finding)
- `data/archives/geometry_decision_stage0.json`, `niche_scale_archive_stage0.json`, `occupancy_saturation_stage0.json`, `reachability_probe_stage0.json`
