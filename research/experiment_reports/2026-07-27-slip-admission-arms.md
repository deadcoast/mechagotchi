# Experiment Report: The Unbreedable Bootstrap Elites — Three Fixes That All Work, and the One the Rule Picked Is the Worst of Them (Cycle 23 · SHARED · M3)

Date: 2026-07-27

## WHY

L1 measured the mechanism exactly and deliberately did **not** fix it:
all **4,435** generation refusals are the SLIP rejecting the **parent**;
100% of those parents are **bootstrap** creatures, built by the corpus
generators without ever being handed the profile. They win niches on
fitness, hold them (only a fitter same-niche candidate displaces them),
and are round-robined as parents forever — a flat 38-per-generation tax
that never improves.

M1 sized the population: **48 of 460 elites (10.4%) are bootstrap
creatures.**

L1 refused to patch it for a stated reason: **the fix trades against
coverage.** A niche whose only occupant is SLIP-illegal goes **empty**
if that occupant is excluded, so "fixing" the refusals could lower the
**0.8984** coverage DR 0042 had just adopted. Three candidate changes
were named and are not equivalent. This slice measures each.

## WHAT

Three arms, each an additive `slip_admission` mode on the loop
(byte-identical when off, pinned):

- **`bootstrap`** — admit only SLIP-legal creatures into the bootstrap
  population. Changes what the archive is *seeded from*.
- **`insertion`** — admit only SLIP-legal creatures into the **archive**.
  A niche whose only occupant is illegal goes **empty**.
- **`parents`** — keep the archive exactly as it is, but breed only
  legal elites. Costs no niche by construction; costs parent diversity
  instead.

The SLIP predicate is the generation arm's own `is_grid_aligned`,
**imported and never re-implemented** — a second implementation could
admit a creature the generator would refuse, which would make every
arm's number a fiction.

### The rule, pre-registered before the run

- **G1 — the cause is eliminated**: `refusals == 0`. **Structural, not
  tuned**: L1 proved 100% of refusals are SLIP-illegal parents, so an
  arm that removes the cause must reach exactly zero. A
  percentage-reduction bar would be a number nobody derived.
- **G2 — coverage is preserved**: cost must not exceed the **MEASURED**
  control — the loop's own seed-to-seed coverage variation, from running
  the incumbent at two seeds. Never a constant; a coverage *gain* is
  never penalised.
- **Tie-break**, fixed in advance: **least invasive first** —
  `parents` < `insertion` < `bootstrap`.

## FINDINGS

### The population, measured directly

- The covenant admits only **49 of 256 bootstrap creatures — 19.1%**.
- Of the baseline's **48 bootstrap elites**, **35 are SLIP-illegal**
  (7.6% of the whole archive); 13 are legal. M1 measured the bootstrap
  share; this measures the *illegal* share directly, superseding L2's
  back-of-envelope "~23 unbreedable" inferred from L1's tax.

### All three arms eliminate the tax completely

Measured control: **0.033204** coverage.

| arm | coverage | cost | niches | refusals | SLIP-illegal elites | verdict |
| --- | --- | --- | --- | --- | --- | --- |
| baseline | 0.898438 | — | 460 | **4,435** | **35** | — |
| `bootstrap` | 0.880859 | +0.017579 | 451 (−9) | **0** | **0** | **adoptable** |
| `insertion` | 0.880859 | +0.017579 | 451 (−9) | **0** | **0** | **adoptable** |
| `parents` | 0.886719 | +0.011719 | 454 (−6) | **0** | **35** | **adoptable** |

**G1 passes for all three — the mechanism's own prediction, confirmed.**
L1 showed every refusal is a SLIP-illegal parent; remove those from the
parent pool by *any* route and the tax goes to zero. It did: 4,435 → 0
in every arm, with `parents` never once needing its fallback
(`parent_fallback_generations: 0`), so G1 is clean rather than rescued.

**G2 passes for all three.** Every cost sits below the measured control,
so on the pre-registered evidence **none of these fixes measurably costs
coverage** — which answers L1's stated worry directly: the trade it
declined to make turns out to be affordable.

**Tie-break → `parents`.**

### And then the ranking reverses on everything the rule did not gate

The rule gated **refusals** and **coverage**. It did not gate **archive
legality** or **quality**.

| arm | mean elite fitness | QD | archive covenant-legal? |
| --- | --- | --- | --- |
| baseline | 0.879605 | 404.618236 | no — 35 illegal |
| `bootstrap` | **0.913274** | **411.886553** | **yes — 0 illegal** |
| `insertion` | **0.912945** | **411.738214** | **yes — 0 illegal** |
| `parents` | 0.878754 | 398.954451 | no — **35 illegal** |

- **`parents` — the rule's winner — is the only arm that lowers
  quality.** QD 404.6 → 399.0; mean elite fitness 0.8796 → 0.8788.
- **`parents` leaves the archive covenant-illegal.** It stops the tax; it
  does not make the archive legal. All **35** illegal elites stay,
  because the arm evicts nobody — it only declines to breed them.
- **`bootstrap` and `insertion` raise mean elite fitness by 3.8%** and
  produce a **SLIP-clean archive**, for three more niches — still inside
  the control.

The mechanism is legible: the SLIP-illegal bootstrap elites were holding
niches at *below-average* fitness. Removing them from the archive raises
the mean; keeping them and merely declining to breed them keeps the dead
weight **and** narrows the parent pool.

**The bar was not widened to capture this.** The rule is what it was and
the winner is what the rule says. The reversal is reported beside the
verdict, in the L2/L4 tradition — which is also why it is worth
something: a rule that only ever confirms the answer you would have
picked is not a rule.

### `bootstrap` and `insertion` converge — structurally, not by coincidence

Both land on **451 niches, 14 bootstrap elites**, with QD within 0.15 of
each other, by different routes. That is expected once stated: both
remove exactly the same 207 SLIP-illegal bootstrap creatures from the
archive, and the only difference is whether those creatures are *scored*
before being excluded (`insertion` scores them; `bootstrap` never builds
them). The same 49 legal bootstrap creatures are available to both, and
14 of them end up holding niches in each.

## THE DECISION (DR 0047)

**All three arms ship as runnable arms, off by default. `parents` is
recorded as the rule's winner. The loop default is NOT changed.**

That withholding has a measured reason rather than caution behind it:
the gate weighed refusals and coverage, the arms are near-tied on both,
and they separate decisively on two dimensions the gate never looked at
— *in the opposite order*. Promoting the gate's winner to the default
would be letting a rule decide a question it did not ask.

What would decide the default is named rather than guessed: a re-run
with **quality and archive legality pre-registered as gates alongside
coverage**, over multiple seeds. On this evidence the likely winner is
`insertion`, not `parents` — which is precisely why it needs its own
gate.

## HONEST REMAINDERS

1. **QD was never gated, and it moved in both directions** (+1.8% for
   two arms, −1.4% for the third). That is a limitation of *this*
   pre-registration, recorded rather than repaired after the fact.
2. **One seed per arm** against a two-seed control. Every arm's cost is
   a single-seed measurement compared to a two-point noise floor; a
   distributional claim needs E4's ten-seed protocol.
3. **One SLIP profile.** All of this is measured under
   `slip_lcd_seed`. A wider palette would reject fewer bootstrap
   creatures and could change every cost here — these are **this
   covenant's** numbers, not the mechanism's in general. The 19.1%
   admission rate especially is a property of this profile.
4. **`parents` does not make the archive legal**, and no arm evicts an
   existing elite. An eviction arm — removing illegal elites already
   seated — was not built and is a fourth candidate nobody has measured.
5. **DR 0046's comparability rule applies**: every coverage and QD
   number here is an **incumbent-geometry** number and may not be read
   against reachability or support counts.

## Verification

RED — the pins written before the module existed:

```powershell
PS> python -B -m unittest test_slip_admission_arms   # (from labs/map_elites_archive)
ModuleNotFoundError: No module named 'slip_admission_arms'
----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (errors=1)
```

GREEN:

```powershell
PS> python -B -m unittest test_slip_admission_arms
Ran 25 tests in 17.688s

OK

PS> python -B -m unittest discover -s labs/map_elites_archive -p "test_*.py"
Ran 300 tests in 104.545s

OK
```

The lab invocation that produced the artifact (five documented-budget
loops; wall clock **1914.665 s** against the **derived** 6000 s bound —
`5 × PRE_REGISTERED_BOUND_S`, because the study runs the loop five
times):

```powershell
PS> python -B labs/map_elites_archive/slip_admission_arms.py
baseline: coverage 0.898438 (460 niches), 4435 refusals, 35 SLIP-illegal elites
measured coverage control: 0.033204
  bootstrap  coverage 0.880859 (cost +0.017579, +9 niches) refusals     0 -> ADOPTABLE
  insertion  coverage 0.880859 (cost +0.017579, +9 niches) refusals     0 -> ADOPTABLE
  parents    coverage 0.886719 (cost +0.011719, +6 niches) refusals     0 -> ADOPTABLE
ADOPTED ARM: parents
wrote data/archives/slip_admission_arms_stage0.json
```

> **CORRECTED BY REVIEW, 2026-07-27 (a claim in this report was
> wrong).** As first committed, the arm emitted `slip_admission` and
> `bootstrap_admitted` **unconditionally**, so the loop's returned
> dictionary changed for every existing caller even at
> `slip_admission="none"` — which contradicts the byte-identical-when-off
> claim made above and throughout this report. The pin could not catch
> it, because it compared two calls to the *new* implementation and both
> had gained the keys; "byte-identical when off" means identical to what
> the loop returned **before the arm existed**. Both keys are now
> **rung-conditional**, and the off-mode key set is **pinned against a
> frozen list** so a future unconditional key fails the suite. A second
> defect found in the same review: under the `bootstrap` arm the
> population was filtered without recomputing `bootstrap_composition`,
> so the result reported a mix summing to the *unfiltered* population
> beside an admitted count that did not — the composition is now
> recomputed by measured membership, and pinned. **No measured value in
> the artifact changed**: `bootstrap_admitted` for the incumbent is the
> population by construction either way, and the composition was never
> carried into this study's artifact.

**A pin that failed and was corrected as a pin, not as code** — recorded
rather than buried. An early pin asserted the insertion arm ends on the
same `evaluations_total` as the incumbent (measured 64 against 76). It
does not, and legitimately so: the loop overshoots by whatever the final
generation adds, and the number of generations depends on how many
candidates each generation produced, which the refusal count changes.
The invariant actually intended — *a refused insertion still spends its
evaluation* — is now pinned directly: the incumbent's `candidate_count`
equals its evaluations, while the insertion arm's is strictly less. A
second pin was added at the same time to stop the legality check passing
vacuously: the **incumbent archive really does hold SLIP-illegal
elites**, which is the arm's reason to exist. No measured value changed.

## Sources

- `audits/TODO.md` (cycle 23 M3) · `research/decision_records/0047-slip-admission-arms.md` (the record this study produced)
- `research/experiment_reports/2026-07-26-generation-refusal-causes.md` (L1 — the mechanism and the named fix), `2026-07-27-elite-population-measures.md` (M1 — the 48-of-460 denominator), `2026-07-26-lineage-dominance.md` (L2), `2026-07-21-generation-arm-loop.md` (K2 / DR 0042 — the coverage this trades against), `2026-07-27-geometry-decision.md` (M2 / DR 0046 — the comparability rule)
- `labs/map_elites_archive/slip_admission_arms.py` (+ `test_slip_admission_arms.py`, 25 pins) · `evaluation_loop_scale.py` (the additive `slip_admission` arm) · `data/archives/slip_admission_arms_stage0.json`
- `labs/grid_genome/slip.py` (`is_grid_aligned`, the shared predicate) · `labs/grid_genome/constrained_generator.py` (`_acceptable`) · `labs/wfc_grid/wfc_population_throughput.py` (`parents_from_archive`)
- `data/slips/valid/slip_lcd_seed.json` (the one profile these numbers belong to)
- `research/decision_records/0040-novelty-first-evolution-surface.md`, `0042-generation-layer-loop-revisit.md`, `0046-two-geometry-split.md`
