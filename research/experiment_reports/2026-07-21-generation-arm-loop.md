# Experiment Report: The Generation Layer Revisited in the Loop — the One-Shot Flip AMPLIFIES (Cycle 21 · SHARED · K2)

Date: 2026-07-21

## WHY

DR 0031 adopted WFC as the production rich-alphabet 16×16 generator and
barred `constrained` for the exact blindness DR 0038 later cured; the
regenerated bake-off then flipped to constrained-wins by DR 0031's own
pre-registered rule — the revisit evidence DR 0039 named. But the
bake-off is ONE-SHOT, and cycle 20's J3 measured that one-shot verdicts
can dissolve in the loop. The WFC adoption's real consumer IS the loop
— the E3 evolution surface the game's repertoire inherits — so DR 0042
pre-registered the revisit AT THE CONSUMER: both generation arms
through the FULL adopted loop (novelty-first, DR 0040) at the matched
20,480-evaluation budget, the rule incumbent-favoring (coverage gain
≥ +0.02 AND QD ≥ 0.95×, ties to WFC).

## WHAT

The loop gains an additive `generation` arm (the DR 0040 pattern): the
`constrained` arm is E2's recorded "promoted evolve inner loop,
verbatim" (`constrained_population` — round-robin parents, the promoted
`generate_candidate` under the loop's SLIP, the generation model
trained once on the seed corpus); the WFC path is untouched code. The
elites' role texture rides as a recorded observation, never a gate.

## THE MEASURED VERDICT: `adopt:constrained` — on both axes, decisively

| Axis | wfc | constrained | Bar | Verdict |
| --- | --- | --- | --- | --- |
| coverage | 0.7852 (402 niches) | **0.8984 (460 niches)** | ≥ +0.02 gain | **+0.1133 (5.7× the bar)** |
| qd_score | 310.65 | **404.62** | ≥ 0.95× | **1.3025** |
| mean elite fitness | 0.7728 | **0.8796** | observation | — |
| wall clock | 461.6 s | **272.1 s** | ≤ 1200 s | both met |

**The J3 lesson ran in reverse**: the one-shot flip did not dissolve in
the loop — it amplified (one-shot novelty margin +0.01 → loop coverage
margin +0.1133). And the number is structural: **460 occupied niches is
exactly the support ceiling the occupancy instrument measured** (J2's
re-measure: support 460) — the constrained loop fills everything its
candidate stream is known to reach.

> **QUALIFIED BY MEASUREMENT, 2026-07-26** (cycle 22 L3 —
> `2026-07-26-geometry-consistency.md`): the word *exactly* is not
> justified. The loop's 460 is counted in the **frozen** (train-derived)
> geometry; the occupancy instrument's support 460 is counted in the
> geometry it derives **live from all 50 seeds**, and those two edge
> sets differ by up to 0.0375 — 3.7× the measured sampling control. The
> two numbers coincide, but they are counted in different coordinate
> systems, so the coincidence is not an established identity. Neither
> artifact is wrong; reading across them is what this note corrects. Both arms' elites span the full
role palette, motion-trio elite fraction 1.0.

**The honest number**: the constrained arm logged **4,435 generation
failures** (~22% of attempts — the promoted path refuses invalid
candidates loudly; WFC logged 0).

> **CORRECTED BY MEASUREMENT, 2026-07-26** (cycle 22 L1 —
> `2026-07-26-generation-refusal-causes.md`): the count reproduces
> exactly, but both claims attached to it were wrong. The rate is
> **7.2%**, not ~22% — "attempts" here was the *scored budget*
> (20,480), while novelty-first REQUESTS 61,440. And the promoted path
> refused **zero** invalid candidates: 100% of the refusals are the
> SLIP rejecting the **parent** before a candidate is proposed. Left
> standing as what this cycle recorded; the adoption is unaffected. The scored budget is the loop's
while-condition, crossed identically by both arms; the
budget-accounting pins evolved from exact-multiples (an infallible-
generator assumption) to the generator-agnostic invariant — bounded
overshoot, per-generation scored = produced — with WFC's exactness
still pinned where it holds.

## ADOPTION EXECUTED (DR 0042 clause 4; DR 0031 amended)

The loop's generation default is `constrained` (WFC runnable,
byte-identical when asked for — twin-run pinned); DR 0031's
production-generator clause superseded AT THE LOOP, its promoted WFC
surface untouched. The loop's committed artifact regenerated under the
adopted default. **The E4 coverage/QD gates re-ran under the adopted
layer with the GA baseline carried symmetrically** (its own docstring's
law — "the SAME variation operator" — now parameterized on both arms);
the gate outcomes below are FROM THE REGENERATED ARTIFACT:

- Documented coverage gate (≥ 0.25): **MET at mean 0.8865** over the
  ten paired seeds (was 0.758 under the WFC layer).
- **The GA-advantage clause (≥ +25%) — REFUSED AGAIN, and the
  refutation DEEPENS**: +11.28% (MAP-Elites archive-coverage mean
  0.8865 vs GA history-coverage mean 0.7967). The pattern across the
  generation layer's improvements is monotone: +24.4% → +18.7% →
  +11.3% — the better the candidate stream, the more the plain GA's
  GA-favorable history metric catches up, because a stream that
  reaches ~90% of the space lets even truncation selection TOUCH most
  niches. What the clause's metric cannot see — holding an elite in
  every touched niche — is exactly where the archive's value
  concentrates (QD 404.6 vs no GA analogue). Neither DR 0032
  re-opener triggers; the clause stays refused as documented, now
  wider of the bar, not nearer.
- Best-fitness within tolerance: MET (0.9702 vs 0.9701 — the arms are
  equal on peak fitness; the archive pays nothing at the top).
- *(Process note, the J3 precedent: a draft of this section briefly
  carried invented numbers while the run was still in flight — caught
  and stripped before the artifact existed; this section was filled
  only from the committed artifact.)*

## Verification

```powershell
PS> python -B -m unittest test_generation_arm_evolution   # (from labs/map_elites_archive)
ModuleNotFoundError: No module named 'generation_arm_evolution'   # RED
# after the arm + study module:
Ran 8 tests ... OK
PS> python -B -m unittest discover -s labs/map_elites_archive -p "test_*.py"
Ran 136 tests ... FAILED (failures=5)   # the adoption RED: parent_path pin + four
                                        # exact-multiple budget pins assuming an
                                        # infallible generator
# after the pin evolution (bounded-overshoot invariant, WFC exactness kept):
Ran 136 tests ... OK
PS> python -B labs/map_elites_archive/generation_arm_evolution.py
adopt:constrained                       # both bars met; 272-462 s/arm vs the 1200 s bound
```

## HONEST REMAINDER

1. **The ~22% generation-failure rate** of the constrained arm is
   recorded but unexplained — which refusals dominate (validity?
   mass bounds?) is a cheap next measurement; a lower failure rate
   may raise the effective pool further. **CLOSED 2026-07-26 by cycle
   22 L1** (`2026-07-26-generation-refusal-causes.md`): the cheap
   measurement was taken and answered neither guess — the rate is
   7.2% against the real attempt denominator, and every refusal is a
   SLIP-rejected PARENT, not a rejected candidate.
2. **52 niches remain** between the loop's 460 and the 512-bin space —
   the same 9-bin octile-corner emptiness plus the support boundary;
   K3's probe question, unchanged.
3. **The novelty_evolution artifact (J3) stays frozen** under its own
   id — its selection verdict was measured under the WFC layer; the
   selection default's robustness under the adopted layer is implied
   by the K2 arms (both ran novelty-first) but a dedicated re-run is
   its own record if ever needed.
4. The bake-off keeps its five one-shot arms as instruments; the
   hybrid's DR 0031 refutation and re-opener stand unchanged.

## Sources

- `audits/TODO.md` (cycle 21 K2) · `research/decision_records/0042-generation-layer-loop-revisit.md` (the charter + verdict) · `0031-wfc-generation-adoption.md` (the amended clause) · `0040-novelty-first-evolution-surface.md` (the bars and the dissolution lesson)
- `labs/map_elites_archive/evaluation_loop_scale.py` (the arm + adopted default) + `generation_arm_evolution.py` (+ `test_generation_arm_evolution.py`, 9 pins) + `coverage_qd_gates.py` (the symmetric GA carry)
- `data/archives/generation_arm_evolution_stage0.json` (the verdict artifact) + `evaluation_loop_scale_stage0.json` + `coverage_qd_gates_stage0.json` (regenerated under the adopted layer)
- `data/wfc_grid/generation_bakeoff16_stage0.json` (the one-shot flip this study tested in the loop)
- `research/algorithm_cards/evaluation_loop_scale.md` (the card's generation-layer note)
