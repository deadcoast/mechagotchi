# Experiment Report: Ancestry Versus Morphology — Both Answers Are True at Once (Cycle 23 · SHARED · M4)

Date: 2026-07-27

## WHY

L2 named the question and never asked it: Phase E measured recurrent
**morphological** families by coarse-descriptor intersection; L2 measured
founder **lines** by recorded ancestry. Different objects — descriptor
similarity versus who descends from whom — and both are now exposed. Do
morphologically-recurrent families trace to common ancestors, or
**converge from different lines**?

It bears directly on **Evolution Q3**: *"Can lineage continuity be
measured independently from visual novelty?"*

**The question is askable now and was not in Phase E.** E5 chose
descriptor clustering over ancestry for a stated reason — *"the WFC
parent path retrains on the whole elite pool, so children carry no single
parent"*. Since **DR 0042** the loop's default is `constrained`, whose
`generate_candidate` preserves `lineage.ancestor_ids` on every candidate.
E5's blocker is **retired by the adopted layer**, not worked around.

## WHAT

**The question had to be reshaped before it could be answered.** Asking
whether families share ancestry *across runs* is **not well posed**:
every run builds its own bootstrap population, so a founder id in one run
is not the same object as a founder id in another — the ancestry spaces
are disjoint. Families recur **morphologically**; their ancestry *cannot*
recur, because there is no shared ancestor pool for it to recur in. The
answerable question, asked here:

> **Within a run, do elites sharing a coarse morphological family share a
> founder more often than chance?** — and is the answer consistent across
> independent runs?

**Pre-registered before the run:**

- **Statistic** — mean, over families with ≥2 members, of the family's
  largest-founder share. **Single-member families are excluded and
  counted**: their share is 1.0 by construction, and including them would
  manufacture common descent out of arithmetic.
- **The null is MEASURED by shuffling** — founder labels permuted across
  elites, preserving family sizes *and* founder-line sizes exactly, so
  the null differs from the observation only in the **pairing**.
- **Rule** — `common_descent` at ≥ 2.0 standard deviations above that
  null; `convergent` otherwise.
- **`convergent` is the NULL**, and the module says so: an absence of
  evidence for common descent, never positive proof of convergence. The
  positive evidence is reported separately as the **distinct-founder
  count**.

Family rule (`recurrent_families.family_key`) and founder rule
(`lineage_dominance.founder_of`) are **imported, never re-implemented**.

## FINDINGS

### The verdict: `common_descent`, consistently, and decisively

| seed | scorable families | share | null | z | verdict |
| --- | --- | --- | --- | --- | --- |
| 20260709 | 62 (1 single excluded) | 0.543184 | 0.341331 ± 0.009436 | **+21.39** | common_descent |
| 20260710 | 62 (2 excluded) | 0.608161 | 0.450059 ± 0.009906 | **+15.96** | common_descent |
| 20260711 | 64 (0 excluded) | 0.540681 | 0.343126 ± 0.011357 | **+17.39** | common_descent |

**Consistent across all three independent seeds.** Morphological families
are decisively more founder-homogeneous than chance: **the morphology
travels with the lineage.**

**Evolution Q3 has a measured answer, and it is NO.** Lineage continuity
cannot be measured independently from visual novelty in this archive —
they are coupled, at z ≈ +16 to +21 across seeds.

### But read the magnitude, not the z — both answers are true at once

**The z values are large because the null is TIGHT, not because the
effect is near-total.** Over 200 permutation rounds with ~62 families the
null's spread is ±0.009–0.011, so a moderate excess reads as a huge z.
Treating z as an effect size would be exactly the "beware the statistic"
error this repo has been burned by before.

The effect size is the share excess: **~0.16–0.20** on a 0–1 scale.
Rescaled — *computed after the run as an interpretive aid, not part of
the gate* — the observed concentration sits **29–31% of the way from
chance to pure lineage determination** (0.3065 / 0.2875 / 0.3008). Not
5%, and not 95%.

And the positive convergence evidence, reported beside the verdict and
deliberately outside it:

| seed | distinct founders per family | max in one family | founder lines | elites |
| --- | --- | --- | --- | --- |
| 20260709 | **3.19** | 7 | 38 | 460 |
| 20260710 | **2.84** | 7 | 33 | 458 |
| 20260711 | **3.30** | 7 | 36 | 464 |

**A typical morphological family contains about three distinct founder
lines, and some contain seven.** So the same coarse morphology *is*
reached from multiple independent lines — convergence is real and
common; it simply is not the whole story.

**The honest answer to L2's question is therefore both, and the study is
worth more for being able to say so:**

- Ancestry is **not** independent of morphology (decisively, z ≈ +18).
- Morphology is **not** lineage-determined either (~3 founder lines per
  family, up to 7; only ~30% of the way to determination).

A rule that could only return one of these would have hidden the other.
The gate returned `common_descent`; the distinct-founder count — which
was never allowed into the verdict — is what keeps the convergence half
visible.

### The stale count, found on the way in

**Every prose surface in `research/` says 52 recurrent families. The
committed artifact says 54**, with per-run counts 57–58 rather than
53–56.

Commit `f8c171b`'s own message records it — *"recurrent families 52 → 54
(gate MET)"* — when the DR 0038/0039 vocabulary regenerated E4's elite
rosters and this artifact regenerated with them. **The regeneration was
recorded; the prose was not updated**, so `52` propagated into the
Phase-E gate, DR 0032, the repertoire-browser report, L2's report, the
Phase-L gate, `audits/TODO.md` and `docs/gap-analysis.md`.

Nothing is retracted: the historical documents stay true of the
vocabulary they measured under, and **the gate verdict is unchanged —
met, by a wider margin**. Dated notes now sit beside the four primary
carriers (the E5 report, the E5 card, DR 0032, the Phase-E gate).

It surfaced because this module **reads the count from the artifact
rather than quoting prose**, which is a pinned property of the module
rather than a habit.

*(For scale: applying E5's recurrence rule to this study's three seeds
gives **63** families common to all three — higher than the ten-seed
intersection precisely because a strict intersection shrinks as runs are
added. It is not comparable to 54 and is not offered as a correction to
it.)*

## HONEST REMAINDERS

1. **A coarse family is a descriptor region, not a verified
   morphological type.** Whether members of one 4×4×4 cell look alike to
   a human is the owner-deferred survey's question, and **no proxy is
   offered**.
2. **Three seeds.** Consistent, but a distributional claim wants E4's
   ten-seed protocol.
3. **`common_descent` describes a tendency, not a mechanism.** *Why*
   families lean toward founders — inheritance of morphology, or
   founders occupying descriptor regions the loop then explores locally
   — is not separated here, and the two would need different
   instruments.
4. **The rescaled 29–31% is an interpretive aid computed after the
   run**, clearly outside the pre-registered gate. It is offered because
   the raw z invites over-reading, not as a measured bar.
5. **DR 0046's comparability rule applies**: these are
   incumbent-geometry addresses and may not be read against
   probe-geometry counts.

## Verification

RED — the pins written before the module existed:

```powershell
PS> python -B -m unittest test_family_ancestry   # (from labs/map_elites_archive)
ModuleNotFoundError: No module named 'family_ancestry'
----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (errors=1)
```

GREEN:

```powershell
PS> python -B -m unittest test_family_ancestry
Ran 19 tests in 1.845s

OK
```

The lab invocation that produced the artifact (three documented-budget
loops; wall clock **1070.396 s** against the **derived** 3600 s bound):

```powershell
PS> python -B labs/map_elites_archive/family_ancestry.py
E5 committed recurrent families: 54 (prose across research/ says 52)
  seed 20260709: 62 scorable families (1 single excluded), share 0.543184 vs null 0.341331±0.009436 (z +21.39) -> COMMON_DESCENT
      distinct founders per family: 3.1935 (max 7), 38 founder lines over 460 elites
  seed 20260710: 62 scorable families (2 single excluded), share 0.608161 vs null 0.450059±0.009906 (z +15.96) -> COMMON_DESCENT
      distinct founders per family: 2.8387 (max 7), 33 founder lines over 458 elites
  seed 20260711: 64 scorable families (0 single excluded), share 0.540681 vs null 0.343126±0.011357 (z +17.39) -> COMMON_DESCENT
      distinct founders per family: 3.2969 (max 7), 36 founder lines over 464 elites
VERDICT: COMMON_DESCENT (consistent across runs: True)
wrote data/archives/family_ancestry_stage0.json
```

**Two pin failures, corrected as pins and recorded rather than buried.**
The first was a stub: the recurrence helper was handed elite records with
empty `axis_values`, which is not what the instrument consumes — the real
axis values and fitness are now carried through, so the helper is
exercised on real records instead of a shape that merely satisfies it.

The second is worth stating precisely, because the fix changes a verdict
boundary. At exactly the bar, `(0.5 − 0.4) / 0.05` evaluates to
`1.9999999999999996` and **reports** as `2.0` — so judging the raw float
would have let a verdict contradict its own published number. The
judgement now runs on the **rounded** z, the same value the artifact
carries. That is float representation, not science, and it follows L2's
own precedent, where a pin asserting rounded shares summed to 1.0 failed
at 1.000003 and was replaced for asserting rounding rather than a
measurement. **No measured value changed.**

## Sources

- `audits/TODO.md` (cycle 23 M4) · `research/questions.md` (Evolution Q3)
- `research/experiment_reports/2026-07-26-lineage-dominance.md` (L2 — the question this asks and the founder rule it imports), `2026-07-09-recurrent-families.md` (E5 — the family rule it imports; now carrying a dated note), `2026-07-09-phase-e-gate.md` (dated note), `2026-07-27-elite-population-measures.md` (M1), `2026-07-27-geometry-decision.md` (M2 / DR 0046 — the comparability rule)
- `labs/map_elites_archive/family_ancestry.py` (+ `test_family_ancestry.py`, 19 pins) · `data/archives/family_ancestry_stage0.json`
- `labs/map_elites_archive/recurrent_families.py` (`family_key`, imported) · `lineage_dominance.py` (`founder_of`, imported) · `evaluation_loop_scale.py` (the `collect_lineage` seam)
- `data/archives/recurrent_families_stage0.json` (the count read rather than quoted), `lineage_dominance_stage0.json`, `coverage_qd_gates_stage0.json`
- `research/algorithm_cards/recurrent_families.md` (dated note) · `research/decision_records/0032-map-elites-ga-gate-disposition.md` (dated note), `0042-generation-layer-loop-revisit.md`, `0046-two-geometry-split.md`
