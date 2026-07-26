# Experiment Report: The Scale Geometry Is Not Stale — It Is Split (Cycle 22 · SHARED · L3)

Date: 2026-07-26

## WHY

K3 bounded four descriptor bins and named their mechanism: measure-thin
windows in the frozen octile edges — one bin missing its boundary by
0.0014, two behind windows 0.0069 and 0.0094 wide, one behind a
suspected quantization gap. Its remainder asked whether the geometry
itself should re-derive under the adopted generation layer, and the
cycle-22 plan carried that forward on a stated premise:

> Its octile edges were calibrated empirically over a 600-candidate
> population produced by the *pre-DR-0038* generation layer.

That premise is testable, so L3 tested it before anything else. **It is
false**, and the correction matters more than the original question,
because testing it surfaced something nobody had written down.

## WHAT

**The staleness test.** E1's derivation protocol, re-run verbatim under
today's code, compared to the committed frozen edges.

**The bar is measured, never assumed.** Octile edges move on their own
between samples, so "unchanged" is meaningless without a noise floor.
The control is the *same recipe derived twice at different seeds* —
whatever the edges do on their own is the bar. The pre-registered,
incumbent-favouring rule: the frozen geometry stands unless the drift
reaches **2× that measured control**.

**The recipe survey.** The repo does not have one scale geometry; it
has several derivation *recipes*, and this module names the three in
live use:

| Recipe | Derivation population | Who consumes it |
| --- | --- | --- |
| `incumbent` | `build_population(600, seed, **train**, wfc)` | the committed frozen edges → `evaluation_loop_scale`, `coverage_qd_gates`, E2 |
| `probe` | `build_population(600, seed, **all seeds**, wfc)` | `reachability_probe` (J1, K3) and `occupancy_saturation`, derived **live every run** |
| `loop_stream` | `constrained_population` via the promoted `generate_candidate` under the SLIP | what the archive is actually **filled from** since DR 0042 |

A descriptor bin index means nothing except relative to the edges that
produced it, so two numbers derived under different recipes are not
comparable — the same class of error L1 caught in K2's failure rate one
task earlier.

**This instrument never moves the geometry.** Re-deriving the edges
would silently change the meaning of every coverage number in the
ledger; that is a gated change with its own record.

## FINDINGS

### 1. The geometry is NOT stale — the premise is refuted by measurement

| Quantity | Value |
| --- | --- |
| frozen vs re-derived incumbent | **0.0** on all three axes |
| measured sampling control | **0.010206** (symmetry; 0.008125 neediness, 0.001289 complexity) |
| ratio | **0.0** |
| **verdict** | **`withhold_regeneration`** |

E1's own protocol reproduces the committed edges **exactly** — not
"within tolerance", byte-identically — while the control shows edges
genuinely do move about 0.01 between samples on their own. So the zero
is informative, not trivial.

The reason is in the history, and it corrects the plan I wrote: the
`niche_scale_archive_stage0.json` artifact was **regenerated at
`f8c171b`, the DR 0038/0039 commit itself**. The frozen edges were
never pre-vocabulary. They are already post-DR-0038, and the derivation
population today carries the full ratified vocabulary (100% of its 600
grids carry the motion trio, spanning all ten roles).

**So K3's measure-thin windows are not a stale-calibration artifact.**
They are a real property of the silhouette-entropy distribution, which
packs six of its eight octiles into a 0.046-wide band. The quantization
hypothesis for `[4, 7, 4]` **hardens**, exactly as the cycle plan said
it would if the windows survived.

### 2. The real finding: the repo runs TWO scale geometries at once

Nothing in the ledger says so, but the surfaces disagree about where
the edges are:

| Comparison | Max edge move | vs the 0.0102 control |
| --- | --- | --- |
| `incumbent` vs `probe` | **0.0375** (behavior_neediness) | **3.7×** |
| `incumbent` vs `loop_stream` | 0.4844 (symmetry) | 47× *(see the caveat below)* |

The `incumbent`/`probe` split is **beyond sampling noise by the
module's own pre-registered factor** — the difference is real, and its
cause is mundane: the frozen edges derive from the corpus **train**
split (~30 grids), while the probe and the occupancy instrument derive
from **all 50 seeds**. Same protocol, different calibration population,
different geometry.

The consequence is that these numbers live in different coordinate
systems:

- **`460/512` occupied, coverage `0.8984`, QD `404.6`, the E4 gate mean
  `0.8865`** — all measured in the **incumbent** geometry.
- **`508/512` proven reachable** (J1 → K3) and the **support ceiling
  `460`** — both measured in the **probe** geometry.

And they have been compared to each other in prose. K2's headline reads
that *"460 occupied niches is **exactly** the support ceiling the
occupancy instrument measured"* — a claim of exact identity between a
number counted in the incumbent geometry and a number counted in the
probe geometry. The two may well be close; what is not justified is the
word *exactly*. The coincidence is real, the identity is not
established, and nothing forces the two geometries to stay near each
other.

This is a latent hazard rather than a present error: each instrument is
internally consistent, and no artifact contains a wrong number. What is
wrong is reading across them.

### 3. How the frozen geometry splits each population

Octile edges are *defined* so their own calibration population lands
1/8 per bin. Measuring the others against the frozen edges shows how
far each sits from the geometry every coverage number is reported in:

| Recipe | symmetry TVD | complexity TVD | neediness TVD | empty octiles |
| --- | --- | --- | --- | --- |
| `incumbent` (its own calibration) | 0.0100 | **0.0000** | 0.0317 | 0 |
| `probe` | 0.0283 | 0.0583 | 0.0717 | 0 |
| `loop_stream` | 0.4500 | 0.4750 | 0.3083 | **4** |

**The caveat on `loop_stream` is large and stated first**: only **120
of 600** requested candidates were produced — 480 refused — because its
parents here are the raw seed corpus, which L1 showed is largely
SLIP-illegal. That sample is small and biased, and it is *not* the
loop's steady-state stream (whose parents are elites). The row bounds
the question; it does not settle it. What it does suggest, and only
suggests, is that the distribution the archive is filled from may sit
well away from the distribution its geometry was calibrated on — with
four octiles that population never reaches at all.

## Verification

```powershell
PS> python -B -m unittest test_geometry_consistency   # (from labs/map_elites_archive)
ModuleNotFoundError: No module named 'geometry_consistency'   # RED
# after the instrument:
Ran 17 tests ... OK
PS> python -B labs/map_elites_archive/geometry_consistency.py
staleness drift 0.0 vs measured control 0.010206 (ratio 0.0) -> WITHHOLD_REGENERATION
  incumbent_vs_probe           max edge move 0.0375  {'behavior_neediness': 0.0375, ...}
  incumbent_vs_loop_stream     max edge move 0.484413 {'symmetry': 0.484413, ...}
wrote data/archives/geometry_consistency_stage0.json
```

The premise correction was verified from history, not inferred:

```powershell
PS> git log --oneline --follow -- data/archives/niche_scale_archive_stage0.json
f8c171b DR 0038 + DR 0039 implemented: the vocabulary-complete generation alphabet …
```

## HONEST REMAINDER

1. **The split is diagnosed, not repaired.** Making the surfaces agree
   means choosing one calibration population and re-deriving — which
   changes what every historical coverage number means. That is a gated
   record of its own, and it must state plainly that prior artifacts
   remain true under the edges they were measured with.
2. **The `loop_stream` row is a bound, not a verdict.** Measuring the
   distribution the archive is actually filled from needs the loop's
   steady-state elites as parents, not seeds. The L2 lineage seam
   already exposes the elite set, so this is cheap — and it is the
   question that decides whether the geometry is calibrated on the
   right population at all.
3. **K3's blocking-axis windows are not re-measured here.** Confirming
   that they survive in numbers (rather than by the staleness argument
   above) needs the probe re-run, which is its own slice.
4. **Prose across the repo compares the two geometries.** K2's report,
   the Phase-J and Phase-K gates, and the cycle-22 plan all read
   reachability counts against coverage counts. Each is corrected with
   a dated note pointing here; none of the underlying artifacts is
   wrong, and none was rewritten.

## Sources

- `audits/TODO.md` (cycle 22 L3) · `research/experiment_reports/2026-07-21-reachability-escalation.md` (K3's named question) · `2026-07-26-phase-k-gate.md`
- `labs/map_elites_archive/geometry_consistency.py` (+ `test_geometry_consistency.py`, 17 pins)
- `labs/map_elites_archive/niche_scale_archive.py` (the derivation protocol) · `reachability_probe.py` + `occupancy_saturation.py` (the live-deriving surfaces) · `evaluation_loop_scale.py` + `coverage_qd_gates.py` (the frozen-edge consumers)
- `data/archives/geometry_consistency_stage0.json` (the artifact) · `niche_scale_archive_stage0.json` (the frozen edges, regenerated at `f8c171b`) · `reachability_escalation_stage0.json` · `occupancy_saturation_stage0.json`
- `research/decision_records/0029-16x16-default-grid-scale.md`, `0038-vocabulary-complete-generation-alphabet.md`, `0042-generation-layer-loop-revisit.md`
