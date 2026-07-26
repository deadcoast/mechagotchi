# Experiment Report: The Refusal-Cause Histogram — What the Constrained Arm's ~22% Actually Refuses (Cycle 22 · SHARED · L1)

Date: 2026-07-26

## WHY

K2 (DR 0042) adopted the constrained generation arm at its consumer and
recorded, honestly, a number it could not explain. From that report,
verbatim:

> **The honest number**: the constrained arm logged **4,435 generation
> failures** (~22% of attempts — the promoted path refuses invalid
> candidates loudly; WFC logged 0).

Two things are true about that sentence. The count is measured and
solid. The *diagnosis* attached to it — "refuses invalid candidates" —
was never measured at all; it was the natural reading of a raise site,
not a reading of the data. And the data was never far away: the
generation arms have always built one record per refusal carrying
`{parent_grid_id, error}`, but the loop kept only `len(failures)`, so
every refusal's own words were discarded one line after they were
created.

L1 is the cheapest instrument in the Phase-L queue and the one whose
absence was least defensible: look at the strings.

## WHAT

**The loop's refusal seam** (`run_evaluation_loop(...,
collect_refusals=False)`): additive, gated, and **byte-identical when
off — pinned**, because an instrument that perturbs the run it observes
is not an instrument. When on, the loop adds exactly ONE key
(`refusal_collection`) carrying the records verbatim plus the attempt
denominator only the loop can compute (the novelty path requests
`population × pool_factor` per generation, so the denominator is not
reconstructible from outside without duplicating the loop's own
arithmetic). Each record also carries the refused parent's **origin**,
measured by membership in the bootstrap population the loop itself
built — never inferred from lineage depth, for the reason the process
note below records — with lineage depth kept as its own separate field
because it answers a different question.

**The classifier** (`classify_refusal`): the promoted generator has
five distinct *refusal* sites, and they are five different diagnoses —
pooling them is exactly what hid the answer. (A sixth `raise` guards
against misuse — an object that is not a trained generation model —
and is deliberately left unclassified: it is a programming error, not
a refusal.) A refused **parent**
(`parent grid cannot satisfy SLIP constraints`) means the loop offered
a breeding partner the profile forbids: the attempt dies *before any
candidate is proposed*, and the fact is about SELECTION. An invalid
**candidate** (`constrained generation produced an invalid candidate`)
means the generator itself missed: the fact is about GENERATION. The
raise-site prefixes are **mirrored as text, never imported across the
package boundary** (the house rule).

Each refusal is then split into its individual reasons — a single
`ValueError` joins the authority's errors with `"; "`, so counting the
message once undercounts the reasons — and each reason is normalized to
a class that groups across variable values (`palette crt_blue not
allowed by SLIP` → `palette not allowed by SLIP`) while keeping the
authority's own words. One measured detail shaped the parser: the
reason `required organ role missing for SLIP: expression` carries a
colon *inside* it, so the family split takes only the first separator
after the recognized prefix.

**Three honesty rules are built into the instrument, not bolted on:**
an unrecognized message is `unclassified` and reported verbatim, so a
future generator change cannot quietly vanish from the histogram; a
recognized family carrying an unrecognized reason keeps that reason's
verbatim text as its own class and is listed under
`unnormalized_reasons`, so nothing is merged into a neighbouring class
to make the table tidy; and the refusal total is cross-checked against
the loop's own independently counted `collapse_failures` **and**
against the committed K2 artifact's total — at K2's parameters the
instrument reproduces 4,435 or the instrument is wrong.

**Pre-registered before the run**: this is an **INSTRUMENT, never a
gate**. It reports whatever the histogram says, *including a result
that contradicts K2's reading of its own number*. No generation change
rides on this artifact; any fix it motivates is its own record with its
own gates.

## FINDINGS

### The instrument reproduces the record exactly

At K2's own parameters the instrument measured **4,435 refusals** —
identical to the committed K2 artifact's `collapse_failures_total`, and
identical again on a second independent run. The loop's own separately
counted `collapse_failures` agrees. Whatever follows is a reading of
the same 4,435 events K2 recorded, not of a different run.

### K2's rate was wrong: 7.2%, not ~22%

| Quantity | Value |
| --- | --- |
| generation attempts (measured) | **61,440** |
| refusals | 4,435 |
| **refusal rate** | **0.0722** |

The ~22% figure is `4435 / 20480` — the **scored budget** used as if it
were the attempt count. Under the adopted novelty-first default the
loop *requests* `population × pool_factor` every generation: 256 × 3 ×
80 generations = **61,440**, exactly what the loop reports. The scored
budget is one third of the attempts by construction, so the failure
rate was overstated threefold. This is the house's own standing warning
— *beware the statistic, not just the data* — landing on the house.

### K2's diagnosis was wrong: nothing refused a candidate

| Refusal family | Count | Share |
| --- | --- | --- |
| `parent_slip_misaligned` | **4,435** | **100%** |
| `candidate_invalid` | **0** | 0% |
| `candidate_slip_misaligned` | **0** | 0% |
| `parent_invalid` | 0 | 0% |
| `slip_profile_invalid` | 0 | 0% |
| unclassified | 0 | 0% |

K2 wrote that "the promoted path refuses invalid candidates loudly."
In 61,440 attempts it refused **zero**. Every one of the 4,435 events
is `parent grid cannot satisfy SLIP constraints` — the profile
rejecting the **parent**, before a candidate is ever proposed. The
generator did not miss once. **The loss is a selection fact, not a
generator fact**, and the two have completely different fixes.

The reasons decompose cleanly (a refusal may carry several, joined by
`"; "` — 5,024 reasons across 4,435 refusals):

| Reason class | Count |
| --- | --- |
| `palette not allowed by SLIP` | 4,411 |
| `required organ role missing for SLIP` | 613 |

which resolves to 3,822 palette-only, 589 carrying both, and 24
organ-role-only. **Palette is the dominant blocker by an order of
magnitude** — the covenant's palette clause, not its morphology
clauses, is what makes an elite unbreedable.

### The refusals have a hard structural signature

Refusals per generation collapse and then stop moving:

| Generation | 1 | 2 | 3 | 5 | 10 | 41–80 |
| --- | --- | --- | --- | --- | --- | --- |
| refusals | **567** | 294 | 171 | 100 | 52 | **38, every generation** |

Generation 1 refuses **73.8% of its 768 requests** — the bootstrap
population is overwhelmingly unbreedable under the covenant. The curve
then decays and locks: **exactly 38 refusals per generation, unbroken
for the last 40 generations — half the run** — a flat 4.95% tax that
never improves. That is not noise. It is the signature of a *fixed set*
of SLIP-illegal elites holding niches permanently and being
round-robined as parents forever, refused every single time.

Consistent with that: **131 distinct parents** were refused across the
run, and the most-refused single parent accounts for only **3.7%** of
refusals — the burden is spread across many elites, not caused by a
handful of pathological ones. Read against the next finding, that
number says something concrete about the archive: since every refused
parent turns out to be a bootstrap creature, **at least 131 distinct
SLIP-illegal creatures occupied elite slots** at some point during the
run, out of a bootstrap population of 256.

### Where the unbreedable elites come from — and why it closes

The mechanism makes a falsifiable prediction *from the code, before the
measurement*. `generate_candidate` accepts a proposal only if
`_acceptable` passes, and `_acceptable` requires **both** validator
legality **and** `is_grid_aligned(grid, slip)`. So every candidate the
loop's own generation emits is SLIP-aligned by construction, and a loop
offspring can therefore *never* be refused as a parent. If the
prediction holds, 100% of refused parents must have entered the archive
from the **bootstrap** population — which `build_population` builds
with the corpus generators, and which is never handed the SLIP.

Measured, by membership in the bootstrap population the loop actually
built:

| Refused parent origin | Count | Share |
| --- | --- | --- |
| `bootstrap` | **4,435** | **100%** |
| `loop_offspring` | **0** | 0% |

The prediction holds exactly. Splitting the same 4,435 by lineage depth
shows why this had to be measured by membership and not inferred: 824
sit at depth 0 (raw seed-corpus grids) and **3,611 at depth 1** —
bootstrap creatures generated *from* a seed, one step down, and
therefore indistinguishable from loop offspring to any depth-based
test. That is the exact trap the process note below records falling
into.

**So the whole finding closes on itself.** The bootstrap seeds the
archive with creatures the covenant forbids as breeding partners; they
win niches on fitness (the archive does not ask about SLIP alignment
when it inserts); they hold those niches, because only a fitter
candidate in the same niche displaces them; and they are round-robined
as parents every generation thereafter, refused every time. That is the
73.8% opening cost, the decay as SLIP-legal offspring claim the rest of
the space, and the permanent flat 38-per-generation tax — one
mechanism, measured end to end.

## Verification

```powershell
PS> python -B -m unittest test_generation_refusal_causes   # (from labs/map_elites_archive)
ModuleNotFoundError: No module named 'generation_refusal_causes'   # RED
# after the loop seam + the instrument:
Ran 22 tests ... OK
PS> python -B -m unittest discover -s labs/map_elites_archive -p "test_*.py"
Ran 164 tests ... OK                    # 142 + the 22 L1 pins; the K2/K3 pins untouched
PS> python -B labs/map_elites_archive/generation_refusal_causes.py
refusals 4435 / attempts 61440 (rate 0.072184)
  parent_slip_misaligned         4435  1.0000
k2 self-verification: {'applicable': True, 'committed_total': 4435, 'measured_total': 4435, 'match': True}
wrote data/archives/generation_refusal_causes_stage0.json
# 273.8 s vs the loop's registered 1200 s bound
```

**The additivity proof, at the byte level.** Regenerating the loop's
own committed artifact under the seam-carrying code:

```powershell
PS> python -B labs/map_elites_archive/evaluation_loop_scale.py
The loop ran 20681 stress-probed lifecycle evaluations over 80 generations of
population 256: 460 of 512 niches occupied (coverage 0.898438), QD score
404.618236, best fitness 0.971513 — deterministic under seed 20260709.
PS> git diff data/archives/evaluation_loop_scale_stage0.json
-      "mean_ms_per_evaluation": 7.4406      +      "mean_ms_per_evaluation": 7.5635
-      "evaluations_20k_s": 148.81,          +      "evaluations_20k_s": 151.27,
-      "evaluations_50k_s": 372.03,          +      "evaluations_50k_s": 378.18,
-      "wall_clock_s": 313.54,               +      "wall_clock_s": 276.18,
```

**Four changed lines, all four of them per-run wall-clock
observations** — every measured value the artifact exists to record
(20,681 evaluations, 80 generations, 460/512 niches, coverage
0.898438, QD 404.618236, best fitness 0.971513) is identical. Timings
cannot be byte-stable by construction, so the artifact was restored
with `git checkout` rather than committed with timing churn — the
H-01 treatment for per-run environment observations.

## HONEST REMAINDER

1. **The fix is deliberately NOT taken here**, and the obvious ones are
   not equivalent. Filtering the bootstrap through the SLIP, refusing
   SLIP-illegal candidates at archive insertion, or selecting parents
   only among breedable elites are three different changes with three
   different consequences — and at least one of them **trades against
   coverage**: a niche whose only occupant is SLIP-illegal goes *empty*
   if that occupant is excluded, so "fixing" the 7.2% could lower the
   0.8984 the loop just adopted. That trade needs a pre-registered
   gate, not a patch, and it belongs to its own record. It also touches
   L2 and L3 directly: an archive that permanently holds elites which
   cannot breed is a lineage-structure fact (L2) measured against a
   geometry calibrated before any of this was known (L3).
2. **Only one refusal family ever occurred**, so the classifier's other
   four are pinned against verbatim-shaped samples but have never met
   real data. This is a limitation, not a hole: `unclassified` catches
   any unrecognized shape and reports it verbatim, so the moment a
   generator change starts refusing candidates the histogram will say
   so instead of silently absorbing it.
3. **One seed, one parameter set.** These are the K2 run's numbers
   reproduced exactly — which is the point — but they are not a
   distribution. Anything distributional needs E4's ten-seed protocol
   and is its own measurement.
4. **Reasons split on `"; "`.** An individual authority error
   containing that separator would be over-split. Unobserved in 5,024
   reasons; recorded as a known limitation rather than assumed away.
5. **The WFC arm is not diagnosed.** It logged zero refusals in the run
   K2 measured, so its histogram would be empty by construction; the
   seam is pinned to work on that arm regardless, and its refusal count
   is deliberately left as an observation, never a pinned constant.
6. **A documentation gap found in passing, named not absorbed**:
   `data/archives/README.md` — the folder's own index — has not been
   updated since cycle 13, so six committed artifacts
   (`novelty_evolution`, `occupancy_saturation`, `reachability_probe`,
   `reachability_escalation`, `generation_arm_evolution`,
   `neediness_scale16`) are unlisted there. Unrelated to this slice's
   science and not folded into it; recorded here so the backfill is a
   scoped change of its own rather than a silent rider.

### Process note, recorded not hidden

The first version of the origin measurement was **wrong, and shipped
nothing**. It derived a refused parent's origin from its
`lineage.generation` depth — depth 0 read as "bootstrap founder",
depth > 0 as "evolved descendant" — and reported that 81% of refused
parents were evolved descendants. That reading was caught before the
report was written by cross-checking it against the most-refused parent
IDs, which were all `mg_constrained_*` and `mg_wfc_*`: bootstrap
names. The cause is that a bootstrap creature is itself generated *from*
a seed, so its lineage depth is already 1 — depth measures ancestry,
not provenance, and using one for the other mislabeled every bootstrap
creature. The instrument now measures origin by **membership in the
bootstrap population the loop actually built**, keeps lineage depth as
its own separately-named field, and carries a pin for each. The
mislabeled figure never left the working tree; it is recorded here
because catching it was the same discipline that produced the finding.

## Sources

- `audits/TODO.md` (cycle 22 L1) · `research/experiment_reports/2026-07-26-phase-k-gate.md` (the remainder this closes)
- `research/experiment_reports/2026-07-21-generation-arm-loop.md` + `research/decision_records/0042-generation-layer-loop-revisit.md` (K2 — both now carry the correction note this report produced)
- `labs/map_elites_archive/generation_refusal_causes.py` (+ `test_generation_refusal_causes.py`, 22 pins) · `labs/map_elites_archive/evaluation_loop_scale.py` (the `collect_refusals` seam)
- `labs/wfc_grid/wfc_population_throughput.py` (`constrained_population` — the failure records, untouched by this slice)
- `packages/mecha_engine/src/mecha_engine/generation/generate.py` (the refusal sites, mirrored as text and never imported across the boundary)
- `data/archives/generation_refusal_causes_stage0.json` (the artifact) · `data/archives/generation_arm_evolution_stage0.json` (the self-verification target) · `data/archives/evaluation_loop_scale_stage0.json` (the additivity proof)
- `research/algorithm_cards/evaluation_loop_scale.md` (the card's L1 evolution entry)
