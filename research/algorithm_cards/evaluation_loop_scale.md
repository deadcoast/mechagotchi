# Algorithm Card: Evaluation Loop at Documented Scale

## Purpose

The full generational MAP-Elites evolve loop at the documented budget
(20k–50k stress-probed lifecycle evaluations, populations ~256) over
the E1 scale geometry with the E2-evidenced WFC parent path — the
Phase-E scale proof with the wall-clock measured against a
pre-registered bound and determinism pinned under seeds (gap-analysis
Phase E, E3).

## Mathematical basis

- MAP-Elites generational illumination: elites parent the next
  population; insertion by strictly-higher-fitness per niche (E1's
  package-parity mechanics, frozen empirical octile edges).
- The promoted evolve semantics: sorted-niche elite ordering,
  per-candidate seed `rng_seed + generation × 100000 + index`.
- The calibrated Stage 0 fitness over the 24-tick stress-probed
  lifecycle (the documented evaluation unit since D5/E1).

## Inputs

- The 16×16 seed corpus (bootstrap: constrained + WFC halves).
- E1's frozen edges; E2's parent-path evidence; a single rng seed.

## Outputs

- Per-generation trajectory (occupancy, coverage, QD, best fitness,
  replacements, collapse failures).
- The final archive summary + lean elite records (descriptor, axis
  values, signature hash — E5's clustering inputs).
- `measured`: pilot ms/evaluation, 20k/50k projections, and the full
  run's wall-clock against the pre-registered 600 s bound.

## Strengths

- The documented budget actually runs — 20,480 evaluations, one seed,
  ~3 minutes, zero failures.
- DR 0028 executed in the honest order: pilot → pre-registered bound →
  measured run.
- Deterministic end to end; the artifact carries the full replay
  protocol.

## Weaknesses

- One seed per artifact run (E5 runs independent seeds for family
  recurrence; the loop function takes any seed).
- Coverage saturates near 55% under the pure WFC parent path —
  late-run generations refine fitness instead of discovering niches.

## Failure modes

- Elite-pool convergence: WFC retrained on a stable elite pool
  regenerates similar bodies; occupancy plateaus (observed ~gen 50).
  Recorded honestly; novelty pressure is a named candidate follow-up,
  never an unrecorded tweak.
- Working-set growth: only current elites' grids are retained between
  generations (memory stays bounded at ~hundreds of grids).

## Integration risk

Low: lab-side over promoted generation surfaces; the engine archive's
scale-geometry seam remains the named promotion for the Phase-E gate.

## License status

Repo Apache-2.0 (DR 0028); stdlib only — and the measurement says
stdlib HOLDS at this scale (no NumPy record required).

## Prototype result

20,480 evaluations / 79 generations / population 256: 281/512 niches
(coverage 0.549), QD 222.1, best 0.9836, 682 replacements, 0 collapse
failures; 174.12 s measured vs the 600 s pre-registered bound; 50k
projection 323 s also inside the bound; determinism test-pinned.

## Decision

**adopt** (as Phase E's scale evidence; E4 judges the documented gates
on this instrument).

## Go-No-Go gate

GO for E4/E5: budget reached, bound met, determinism pinned. NO-GO
triggers: the E4 GA-baseline comparison refuting the ≥25%-over-GA
documented gate, or determinism drift under the pinned seeds.

## Evolution

- **DR 0040 (2026-07-20)**: `selection` became an arm; novelty_first
  adopted on both axes (coverage 0.7637 → 0.7852, QD ratio 1.0216) at
  the matched budget.
- **DR 0042 (2026-07-21)**: `generation` became an arm; the
  constrained path (the promoted evolve inner loop, vocabulary-complete
  since DR 0038) beat the WFC incumbent on BOTH pre-registered bars in
  the full loop — coverage 0.7852 → **0.8984** (+0.1133 vs the +0.02
  bar; 460 niches = the measured support ceiling), QD ratio **1.3025**
  — and is the adopted generation default; WFC stays a runnable arm.
  The constrained arm's ~22% recorded generation-failure rate is a
  named observation (**corrected by L1 below**); budget pins evolved to
  the generator-agnostic bounded-overshoot invariant with WFC exactness
  kept.
- **Cycle 22 L1 (2026-07-26)**: the loop gained the additive
  `collect_refusals` seam — byte-identical when off (pinned), adding
  exactly one key when on, carrying each refusal's verbatim error, its
  generation index, and its parent's lineage depth. The instrument it
  feeds **corrected DR 0042's own reading of its own number**: the
  4,435 count is exact, but the rate is **7.2%** (the ~22% figure used
  the SCORED budget, 20,480, where novelty-first REQUESTS 61,440), and
  the promoted path refused **zero** invalid candidates — 100% of the
  refusals are SLIP-rejected PARENTS, so the loss is a selection fact,
  not a generator fact. An instrument only: no generation behaviour
  changed.
- **Cycle 22 L2 (2026-07-26)**: the loop gained the additive
  `collect_lineage` seam (byte-identical when off, one gated key,
  emitting the engine's own recorded ancestry per occupied niche), and
  **the documented gate's second clause was judged for the first
  time** — `deep-research.md:205`, *"no single lineage > 40% of
  occupied cells"*. **PASS at 0.2848** (131 of 460 cells) over 38
  founder lines. Reported beside the verdict and deliberately outside
  it: **four founder lines hold half the archive**, and the two
  largest (39.4% between them) are founded by WFC *bootstrap*
  creatures even though the adopted generation layer is `constrained`
  — generation layer and founder stock are independent facts. Elite
  lineage depth spans 0–18.
- **Cycle 22 L3 (2026-07-26)**: the geometry this loop measures in was
  tested for staleness and is **not stale** — E1's protocol re-run
  today reproduces the committed edges exactly (drift 0.0 against a
  measured 0.0102 sampling control), verdict `withhold_regeneration`.
  But the survey found the repo runs **two** geometries: this loop
  (and `coverage_qd_gates`) consume the frozen **train**-derived edges
  via `load_frozen_scale_edges`, while `reachability_probe` and
  `occupancy_saturation` derive **live from all 50 seeds** — edge sets
  differing by up to 0.0375, 3.7× the control. **Coverage and QD
  numbers from this loop are therefore not directly comparable to
  reachability or support counts.**
- **Cycle 22 L4 (2026-07-26)**: a fourth descriptor axis
  (`animation_density`, the documented four-axis descriptor's missing
  member) was proposed and judged as a CANDIDATE against **this loop's
  incumbent geometry**. All machine gates pass — spread, independence
  (max |r| 0.173), and discrimination (54.3% of same-three-axis-bin
  pairs separated) — with the coverage cost reported: occupied 289 →
  448 while coverage falls 0.5645 → 0.1094 (512 → 4096 cells).
  **Not adopted**: the documented selection criterion needs the
  owner-deferred human panel and no proxy was substituted. The loop's
  geometry is unchanged.
- **Cycle 23 M1 (2026-07-27)**: the loop gained its third additive
  observation seam, `collect_elite_grids` — byte-identical when off
  (pinned alone *and* composed with `collect_lineage`), one gated key,
  emitting a deep COPY of each occupied niche's elite grid plus its
  origin measured by MEMBERSHIP in the bootstrap population. Phase L's
  convergent finding was then tested: **the elites' descriptor
  distribution is NOT distinguishable from the derivation population's**
  — `within_sampling_noise` on all four statistics against a bar of 2×
  a MEASURED control, highest ratio 1.70 (symmetry). The control is two
  population types each drawn twice, **larger taken** — and that choice
  is what prevented a false positive: `animation_density` reads
  **5.14× → "material"** against the cheap derivation control alone and
  **0.85 → within noise** against the elite control (a second full
  loop), which is 6.1× larger on that axis. Measured beside the
  verdict: **48 of 460 elites (10.4%) are bootstrap creatures**
  (M3's denominator, now exact), the top two symmetry octiles are
  depleted (48 and 28 vs ~57 flat) without reaching the bar, and L4's
  **A2 independence weakens by half on the elites** (max |r| 0.173 →
  **0.350**, still under its 0.5 bar). L4's **A3 and A4 are
  STRUCTURALLY UNDEFINED** on this population — one elite per niche
  means zero same-bin pairs and `occupied_4 == occupied_3` for any
  fourth axis — and no number was substituted. The loop reproduced its
  committed 460 / 0.898438 / 404.618236 exactly, so the seam perturbs
  nothing by measurement as well as by pin. An INSTRUMENT: no geometry
  moved, nothing adopted, L4's verdict untouched.
- **Cycle 23 M3 (2026-07-27, DR 0047)**: the loop gained the additive
  `slip_admission` ARM set — `bootstrap` / `insertion` / `parents`,
  byte-identical at `"none"` (pinned), the SLIP predicate being the
  generation arm's own `is_grid_aligned` imported rather than
  re-implemented. Measured: the covenant admits only **49 of 256**
  bootstrap creatures (19.1%), and **35 of the 48 bootstrap elites are
  SLIP-illegal**. **All three arms drive the 4,435-refusal tax to
  ZERO** (G1, a structural bar), and **every coverage cost lands below
  the measured 0.033204 control** — so L1's declined trade is
  affordable. Tie-break (least invasive) → `parents`. **And the ranking
  reverses on what the rule did not gate**: `parents` is the **only arm
  that lowers quality** (QD 404.618236 → 398.954451) and **leaves all
  35 illegal elites seated**, while `bootstrap` / `insertion` raise mean
  elite fitness 3.8% (0.8796 → 0.913) and produce a SLIP-clean archive
  for three more niches. **The loop default is NOT changed** — withheld
  with the reason measured, because the gate weighed two dimensions and
  the arms separate on two others in the opposite order. The incumbent
  configuration's 460 / 0.898438 / 404.618236 stands untouched.

## Sources

- `labs/map_elites_archive/evaluation_loop_scale.py` (+ `test_evaluation_loop_scale.py`)
- `data/archives/evaluation_loop_scale_stage0.json`
- `data/archives/generation_arm_evolution_stage0.json` (the DR 0042 verdict)
- `labs/map_elites_archive/generation_refusal_causes.py` (+ `test_generation_refusal_causes.py`) · `data/archives/generation_refusal_causes_stage0.json` (the L1 instrument)
- `labs/map_elites_archive/lineage_dominance.py` (+ `test_lineage_dominance.py`) · `data/archives/lineage_dominance_stage0.json` (the L2 instrument)
- `labs/map_elites_archive/geometry_consistency.py` (+ `test_geometry_consistency.py`) · `data/archives/geometry_consistency_stage0.json` (the L3 instrument) · `research/experiment_reports/2026-07-26-geometry-consistency.md`
- `labs/map_elites_archive/animation_density_axis.py` (+ `test_animation_density_axis.py`) · `data/archives/animation_density_axis_stage0.json` (the L4 candidate axis) · `research/experiment_reports/2026-07-26-animation-density-axis.md`
- `labs/map_elites_archive/elite_population_measures.py` (+ `test_elite_population_measures.py`, 36 pins) · `data/archives/elite_population_measures_stage0.json` (the M1 instrument) · `research/experiment_reports/2026-07-27-elite-population-measures.md`
- `labs/map_elites_archive/slip_admission_arms.py` (+ `test_slip_admission_arms.py`, 25 pins) · `data/archives/slip_admission_arms_stage0.json` (the M3 arms) · `research/experiment_reports/2026-07-27-slip-admission-arms.md` · `research/decision_records/0047-slip-admission-arms.md`
- `labs/grid_genome/slip.py` (`is_grid_aligned` — the M3 arms' shared predicate, imported never re-implemented)
- `research/experiment_reports/2026-07-09-evaluation-loop-scale.md`, `2026-07-21-generation-arm-loop.md`, `2026-07-26-generation-refusal-causes.md`, `2026-07-26-lineage-dominance.md`
- `research/decision_records/0040-novelty-first-evolution-surface.md`, `0042-generation-layer-loop-revisit.md`
- `docs/project-research/deep-research/01/deep-research.md`
