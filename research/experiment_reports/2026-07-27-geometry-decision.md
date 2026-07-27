# Experiment Report: The Geometry Split, Decided — and the Split Was Not the Disease (Cycle 23 · SHARED · M2)

Date: 2026-07-27

## WHY

L3 found the repo runs **two** scale geometries and deliberately did not
repair it — the loop and the E4 gates on frozen **train**-derived edges,
`reachability_probe` and `occupancy_saturation` on edges derived **live
from all 50 seeds**, differing by up to 0.0375 (3.7× L3's measured
sampling control). The consequence: `460/512 occupied` and `508/512
reachable` are counted in different coordinate systems and have been
read against each other in prose.

M2 is the gated record that decides it (**DR 0046**).

**Why L3's own measurement could not decide it.** L3 measured the split
in **edge distance**, which is diagnostic but is not the unit any ledger
number is expressed in: a reader cannot tell from *"the edges differ by
0.0375"* whether that moves one creature or four hundred. Deciding
needed the split measured in **addresses** — how often the same creature
lands in a different niche — because that is the unit `460/512` is
counted in.

## WHAT

**The rule, pre-registered in the module before the run**, both verdicts
first-class:

- **Statistic** — the **bin disagreement rate**: the fraction of one
  common population receiving a different descriptor address under the
  two geometries.
- **Bar** — **MEASURED, never a constant**: the same recipe derived at
  two different seeds, addressed over the same population, is how far a
  geometry disagrees *with itself*. Measured for **both** recipes with
  the **larger** taken, which makes `converge` harder to reach.
- **Rule** — `converge` at `>= 2.0 ×` the measured control,
  `freeze_split` otherwise. **Status-quo-favouring**: instruments are
  not rewired without measured cause.

**And the direction was fixed before the measurement.** The measurement
decides *whether* to converge; `CONVERGENCE_TARGET = "incumbent"` is a
pinned constant of the module with its reason, so the direction could
never be chosen to suit the number that came back. (Converging *onto*
the incumbent is the conservative direction: it leaves every committed
coverage/QD number untouched, and reachability is a claim *about* the
archive's coordinate system, so it has to be counted in the archive's
own coordinates or it does not bear on the archive at all.)

## FINDINGS

### The verdict: `freeze_split` — driven by an enormous control

| quantity | measured |
| --- | --- |
| bin disagreement, incumbent vs probe | **0.360000** |
| measured control (larger of the two recipes) | **0.310333** |
| ratio | **1.16** against the 2.0 bar |
| **verdict** | **`freeze_split`** |

Read the two numbers together, because the second is the finding:

| recipe | disagreement with ITSELF at another seed |
| --- | --- |
| incumbent | **0.200000** |
| probe | **0.310333** |

**Re-deriving the probe recipe at a different seed reassigns 31% of the
population to different niches.** The incumbent recipe reassigns 20%.
The gap between the two geometries — 36% — is barely larger than either
recipe's disagreement with a *resampled copy of itself*.

So the honest reading is not "the split is fine". It is:

> **The two geometries are not two principled coordinate systems. They
> are two draws from a noisy edge-derivation process.**

Converging them would have picked one draw over another and changed
nothing about the instability underneath. That is why the record refuses
convergence **on the measurement** rather than adopting it as
tidy-looking housekeeping — and it is a sharper reason than the one M2
was planned with.

### The mechanism, localised to one axis

| axis | address changes between geometries |
| --- | --- |
| symmetry | 0.053667 |
| **visual_complexity** | **0.264667** |
| behavior_neediness | 0.079000 |

One axis carries the split almost entirely. Its edges explain why:

```text
visual_complexity  incumbent = [0.860816, 0.871018, 0.877231, 0.883531, 0.889860, 0.896811, 0.906586]
                   probe     = [0.854783, 0.867710, 0.875275, 0.882224, 0.887879, 0.894817, 0.904185]
```

**All seven interior octile edges sit inside a band about 0.046 wide.**
An edge movement far inside sampling noise therefore reassigns a quarter
of the population.

This is **K3's measure-thinness and L3's own 0.046-wide
silhouette-entropy band — now measured in addresses rather than in edge
distance**, which ties the split directly to the quantization hypothesis
L3 hardened. The disease is not that the repo has two geometries. The
disease is that **`visual_complexity`'s octiles are not determined by a
600-creature derivation.**

### K2's cross-geometry claim, resolved rather than merely qualified

K2's headline: *"460 occupied niches is **exactly** the support ceiling
the occupancy instrument measured"*. Counted over **one** population
here:

| geometry | support ceiling |
| --- | --- |
| probe | **460** — reproduces the committed `occupancy_saturation` artifact exactly |
| incumbent | **456** |

The probe figure reproducing the committed artifact exactly is what
makes the comparison trustworthy: the instrument is reading the same
thing that artifact read.

L3 recorded that the identity was *not established*. This measurement
goes further: **the two numbers are not equal once either mismatch is
removed.** The match at 460 was a coincidence across **two** boundaries,
not one — a different geometry *and* a different population (the ceiling
is counted over a 3,000-creature evaluation population, the occupied 460
over the loop's 20,480 evaluations). A dated note now sits beside K2's
original wording; the original stands as what K2 measured.

### K3's blocking-axis re-run is correctly NOT triggered

The queue required re-running K3's blocking-axis instrument on the four
bounded bins *"if the geometry moves"*. The geometry does **not** move —
the verdict is `freeze_split` — so the trigger does not fire. Recording
that explicitly is part of the finding, so a later session does not read
the absence as an omission.

## HONEST REMAINDERS

1. **The probe's edges are not frozen, and that is now the strongest
   named follow-on** (DR 0046). The incumbent is protected from its own
   20% instability by being derived once and committed; the probe has no
   such protection. In practice it is deterministic (a fixed default
   seed), so **no committed probe number is wrong** — but its numbers
   are contingent on that draw in a way no artifact records, and a
   future run at a different seed or count would silently re-address
   31% of creatures.
2. **Whether `derivation_count = 600` determines the octile edges at
   all** is now an open question about E1's derivation protocol itself,
   not about which population feeds it. `visual_complexity` in
   particular looks under-determined at that size.
3. **The reachability numbers are untouched.** 508/512 and the four
   bins K3 bounded remain probe-geometry numbers; nothing here
   invalidates them, and the comparability rule governs how they may be
   quoted.
4. **The disagreement statistic counts an address change of any size.**
   A creature moving one octile on one axis counts the same as one
   moving three on all three. That is deliberate — a niche is a whole
   address — but it means the rate does not distinguish a small shift
   from a large one, and a distance-weighted variant would say something
   different.
5. **One population, one seed pair per recipe.** The controls bound the
   instability; a distributional claim about it needs its own protocol.

## Verification

RED — the pins written before the module existed:

```powershell
PS> python -B -m unittest test_geometry_decision   # (from labs/map_elites_archive)
ModuleNotFoundError: No module named 'geometry_decision'
----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (errors=1)
```

GREEN:

```powershell
PS> python -B -m unittest test_geometry_decision
Ran 20 tests in 2.828s

OK
```

The lab invocation that produced the artifact:

```powershell
PS> python -B labs/map_elites_archive/geometry_decision.py
bin disagreement 0.36 vs measured control 0.310333 (x1.160044) -> FREEZE_SPLIT
  per-axis: {'symmetry': 0.053667, 'visual_complexity': 0.264667, 'behavior_neediness': 0.079}
  controls: {'incumbent': 0.2, 'probe': 0.310333}
  support ceiling: incumbent 456 vs probe 460 (of 512)
wrote data/archives/geometry_decision_stage0.json
```

## Sources

- `audits/TODO.md` (cycle 23 M2) · `research/decision_records/0046-two-geometry-split.md` (the record this study produced)
- `research/experiment_reports/2026-07-26-geometry-consistency.md` (L3 — the diagnosis this decides), `2026-07-21-generation-arm-loop.md` (K2 — the cross-geometry claim, now carrying a dated note), `2026-07-21-reachability-escalation.md` (K3 — measure-thinness and the bounded bins), `2026-07-27-elite-population-measures.md` (M1 — the measured-control precedent)
- `labs/map_elites_archive/geometry_decision.py` (+ `test_geometry_decision.py`, 20 pins) · `data/archives/geometry_decision_stage0.json`
- `labs/map_elites_archive/niche_scale_archive.py` (the derivation protocol), `reachability_probe.py`, `occupancy_saturation.py` (probe-geometry consumers), `evaluation_loop_scale.py`, `coverage_qd_gates.py` (incumbent consumers) · `labs/wfc_grid/wfc_population_throughput.py` (`load_frozen_scale_edges`)
- `data/archives/occupancy_saturation_stage0.json`, `reachability_probe_stage0.json`, `reachability_escalation_stage0.json`, `niche_scale_archive_stage0.json`
- `research/decision_records/0029-16x16-default-grid-scale.md`, `0036-neediness-scale-recalibration.md`, `0042-generation-layer-loop-revisit.md`
