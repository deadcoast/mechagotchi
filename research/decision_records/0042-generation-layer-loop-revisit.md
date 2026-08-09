# Decision Record 0042: The Generation Layer Revisited in the Loop — DR 0031's Clause Judged at Its Consumer

Date: 2026-07-21

## Status

**Accepted and ADOPTED on the measured verdict** (cycle 21 · Phase K ·
K2). The rule below was pre-registered BEFORE the comparison run (the
DR 0040 discipline: the "Measured verdict" section is filled only from
the committed artifact). The challenger cleared both bars decisively;
the loop's generation default is now `constrained`, DR 0031's
production-generator clause is superseded AT THE LOOP, and the E4
coverage/QD gates re-run under the adopted layer with the GA baseline
carried symmetrically.

## Context

DR 0031 (cycle 10 B3) adopted **WFC as the production generator for
rich-alphabet 16×16 generation** on the B2 bake-off's pre-registered
rule — and barred `constrained` from eligibility because the 5-token
path could not emit the rich alphabet. DR 0038/0039 (cycle 20) cured
exactly that blindness, and the REGENERATED bake-off flipped by the
original rule's own arithmetic: constrained now clears eligibility and
wins the ranking (descriptor novelty 0.26 vs 0.25, silhouette entropy
tied at 6.6439 bits, readability proxy 0.797 vs 0.685; validity 1.0
both) — the revisit evidence DR 0039 named.

But the bake-off is a ONE-SHOT instrument, and cycle 20's own
methodological finding (J3, DR 0040) is that **one-shot verdicts can
dissolve in the loop**: the coverage-vs-QD trade the occupancy
instrument measured vanished inside the full generational loop. The
WFC adoption's real consumer is that same loop — the E3 evolution
surface (`wfc_population`, the parent-conditioned path, running the
DR 0040 novelty-first default) whose truth the game's repertoire
inherits. The promoted era loop (`runtime.evolve`) already breeds
through the constrained path. So this record judges the revisit WHERE
THE ADOPTION IS CONSUMED: inside the full loop, at the matched
documented budget.

## Decision — the protocol and rule, pre-registered

1. **The loop gains an additive `generation` parameter**
   (`"wfc"` default | `"constrained"`), the DR 0040 arm pattern
   exactly: the WFC default is pinned byte-identical when asked for;
   the constrained arm is `constrained_population` — E2's recorded
   "promoted evolve inner loop, verbatim" (round-robin parents, the
   promoted `generate_candidate` under the loop's own SLIP profile,
   the generation model trained once on the seed corpus).
2. **Both arms run the loop as adopted**: novelty-first selection
   (DR 0040), population 256, the matched 20,480-evaluation scored
   budget, identical seeds and identical mixed bootstrap — one lever
   varies.
3. **The rule (DR 0040's bars, incumbent-favoring)**: `constrained`
   becomes the loop's generation default ONLY IF, against the WFC
   arm, coverage gain ≥ **+0.02** AND qd_score ≥ **0.95×**. Otherwise
   **WFC stands at its consumer** — DR 0031's clause survives where
   it is consumed, and the flipped bake-off is recorded as
   one-shot-only evidence (the J3 dissolution, mirrored). Ties favor
   the incumbent by construction.
4. **Scope either way**: both arms stay runnable; the promoted
   `mecha_engine.generation` WFC surface (additive seam,
   parity-pinned) and every instrument arm are untouched in BOTH
   outcomes; nothing is deleted. If adopted, DR 0031's
   production-generator clause is superseded AT THE LOOP by this
   record and the loop's committed artifact regenerates under the new
   default; if withheld, no committed artifact changes.
5. **Observation, not a gate**: per-arm elite role texture (which
   loop's elites carry the motion trio, and at what fraction) — the
   game-facing consequence of the choice, recorded from the loop's
   own elite grids.
6. **Run-once bound**: ≤ 1200 s per arm (the DR 0040 re-registered
   loop bound; an overage is cited with its cause, never silent).

## Measured verdict (filled from `data/archives/generation_arm_evolution_stage0.json`, run 2026-07-21)

| Axis | wfc (incumbent) | constrained (challenger) | Bar | Verdict |
| --- | --- | --- | --- | --- |
| coverage | 0.7852 (402/512) | **0.8984 (460/512)** | gain ≥ +0.02 | **+0.1133 — met, 5.7× the bar** |
| qd_score | 310.65 | **404.62** | ≥ 0.95× | **ratio 1.3025 — met** |
| mean elite fitness | 0.7728 | **0.8796** | (observation) | — |
| wall clock | 461.6 s | **272.1 s** | ≤ 1200 s each | both met |

> **Dated note, 2026-07-28 (cycle 25 O3 / DR 0056) — these numbers are
> NOT retracted, and they now need an arm named beside them.** They are
> what the loop achieves under `slip_admission="none"`, the incumbent
> arm, which is what this bake-off ran. DR 0052 later adopted
> `insertion` as the loop's default and DR 0053 flipped it. Restated at
> **this record's own seed and budget**, the adopted default gives
> **coverage 0.880859** (−0.017579), **QD 411.738214 (+7.119978)**, 451
> niches (−9), **0 refusals** (−4,435) and **0 SLIP-illegal elites**
> (−35). **Coverage does not fall for nothing — it buys quality**: nine
> niches and 0.0176 coverage buy +7.12 QD and an archive legal under the
> covenant that bred it. Both sets of numbers are correct and answer
> different questions; DR 0056's quoting rule is that any statement of
> the form *"the loop achieves X"* must say **which arm** it means. The
> documented E4 gates were re-judged under the adopted default and
> **hold** (`NO_REGRESSION`). See
> `research/experiment_reports/2026-07-28-adopted-default-restatement.md`.

**Verdict: `adopt:constrained`.** The J3 dissolution lesson ran in
REVERSE this time: the one-shot bake-off's flip did not dissolve in the
loop — it AMPLIFIED (one-shot novelty margin +0.01; loop coverage
margin +0.1133). The constrained loop reaches **460 occupied niches —
exactly the measured support ceiling the occupancy instrument named**
(J2's re-measure: support 460): the loop now fills everything its
candidate stream is known to reach.

**Recorded honestly, not hidden**: the constrained arm logged **4,435
generation failures** (~22% of attempts — the promoted
`generate_candidate` refuses invalid candidates loudly; WFC's bounded
restarts logged 0). The scored budget was matched by construction (the
loop's while-condition is the bar both arms cross), and the
budget-accounting pins evolved from exact-multiples to the
generator-agnostic invariant — bounded overshoot, per-generation scored
= produced — with WFC's exactness still pinned where it holds. Both
arms' elites span the full role palette with motion-trio elite fraction
1.0 (the observation gate-free, as registered).

> **CORRECTED BY MEASUREMENT, 2026-07-26 (cycle 22 L1 —
> `2026-07-26-generation-refusal-causes.md`).** The count above is
> exact and reproduces to the record; the two claims attached to it do
> not. **(a) The rate.** "~22% of attempts" divides 4,435 by the
> *scored budget* (20,480). Under the adopted novelty-first default the
> loop REQUESTS `population × pool_factor` per generation, so the real
> denominator is 61,440 attempts and the measured refusal rate is
> **7.2%**. **(b) The diagnosis.** `generate_candidate` refused
> **zero** invalid candidates in those 61,440 attempts: 100% of the
> refusals are `parent grid cannot satisfy SLIP constraints` — the
> PARENT rejected before any candidate is proposed. The failures are a
> selection fact, not a generator fact. Both corrections are measured,
> not argued; this paragraph stands as what K2 recorded, and the
> adoption it supports is unaffected (the scored budget both arms
> crossed is unchanged).

**Execution of the adoption**: the loop default flipped
(`generation="constrained"`, WFC runnable and byte-identical when asked
for); the loop's committed artifact regenerated under the new default;
the E4 coverage/QD gates lab gained the same `generation` parameter on
BOTH arms (its GA docstring's own symmetry law: "the SAME variation
operator") and its artifact regenerated — the DR 0032 standing clause
re-judged under the adopted layer: **coverage gate MET at mean 0.8865
(was 0.758); the GA-advantage clause REFUSED at +11.28% vs ≥ +25%**
(the refutation deepens monotonically as the generation layer improves
— +24.4% → +18.7% → +11.3% — because the GA-favorable history metric
saturates under a ~90%-reach candidate stream); best-fitness within
tolerance MET (0.9702 vs 0.9701). Neither DR 0032 re-opener triggers.

## Sources

- `research/decision_records/0031-wfc-generation-adoption.md` (the clause under revisit + its named re-opener), `0038`/`0039` (the cure that flipped the bake-off), `0040-novelty-first-evolution-surface.md` (the bars, the arm pattern, and the dissolution lesson)
- `data/wfc_grid/generation_bakeoff16_stage0.json` (the regenerated one-shot verdict: winner constrained)
- `labs/map_elites_archive/evaluation_loop_scale.py` (the consumer) + `labs/wfc_grid/wfc_population_throughput.py` (`constrained_population`, E2's verbatim arm)
- `labs/map_elites_archive/generation_arm_evolution.py` (the K2 study, this record's instrument)
