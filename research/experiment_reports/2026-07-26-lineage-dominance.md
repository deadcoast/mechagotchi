# Experiment Report: The Lineage-Dominance Clause, Judged at Last (Cycle 22 · SHARED · L2)

Date: 2026-07-26

## WHY

The documented MAP-Elites evaluation gate has two halves. From
`docs/project-research/deep-research/01/deep-research.md:205`, verbatim:

> archive coverage ≥ 25% on a 576-cell repertoire after 20k
> evaluations; **no single lineage > 40% of occupied cells**

The first half is one of the most-judged numbers in the repository: the
Phase-E gate measured it, DR 0032 dispositioned the GA-advantage clause
beside it, and K2 re-ran it symmetrically under the adopted generation
layer (coverage MET at mean 0.8865). **The second half has never been
measured — not once, in the project's entire history.**

It was never blocked, either. The promoted `generate_candidate`
preserves `lineage.ancestor_ids` on every candidate it emits, composing
them oldest-first, so every elite's founder has been recoverable for as
long as the archive has existed. The clause was simply never looked at
— the same shape of omission L1 found one task earlier, and the reason
the Phase-K gate's survey named it the sharpest unmet documented item
in the repo.

It matters beyond bookkeeping. The clause is the **quantitative form of
Evolution Q1** (`research/questions.md`: *"Can MAP-Elites preserve
multiple companion families instead of one dominant optimum?"*) — the
question the whole archive exists to answer. Phase E answered it
qualitatively, with 52 recurrent morphological families across ten
seeds. Nobody had ever asked whether those families trace back to one
ancestor.

## WHAT

**The loop's lineage seam** (`run_evaluation_loop(...,
collect_lineage=False)`): additive, gated, **byte-identical when off —
pinned**, adding exactly one key. When on it emits the engine's own
recorded ancestry for each occupied niche's elite, verbatim and nothing
more. The loop **collects**; it does not derive — the founder rule
lives in exactly one pinned place so the two cannot drift apart.

**The pre-registered rule**, written into the module before any run,
with both outcomes first-class:

- A **lineage** is a founder line. An elite's founder is
  `lineage.ancestor_ids[0]` where ancestry is recorded — the promoted
  generator composes `[*parent_ancestors, parent_grid_id]`, so the list
  is oldest-first and element 0 is the origin of the line — and the
  elite's own `grid_id` where no ancestry is recorded. An ancestor is
  never invented.
- `max_founder_share` is the largest share of **occupied** cells held
  by any single founder line.
- **pass** if `max_founder_share ≤ 0.40`; **refuse** otherwise. The
  documented wording is "> 40%", so exactly 40% is not a violation —
  the boundary belongs to the rule and is pinned as such.

**One divergence is declared, not silently substituted.** The
documented clause pairs with a **576-cell** repertoire; this repo's
proven geometry is the **512-cell** 8×8×8 octile archive (DR 0029, E1)
— the same population every coverage judgement has used. A dominance
*share* is a fraction of occupied cells and is well-defined under
either, but quietly judging one document's bar against another
population is precisely the statistic error L1 caught in K2 one task
ago. The artifact therefore carries both numbers and the module refuses
to pretend they are the same.

**Reported beside the verdict, deliberately outside it**: the clause
judges a *single* lineage, and a clause about one lineage cannot see a
cartel of three. The instrument also reports how many founder lines it
takes to hold half the archive — an observation, never part of the
documented bar.

## FINDINGS

### The verdict: PASS — measured, first time in the project's history

| Quantity | Value |
| --- | --- |
| occupied cells | 460 of 512 |
| distinct founder lines | 38 |
| **largest single lineage** | **0.2848** (131 of 460 cells) |
| documented bar | ≤ 0.40 |
| **verdict** | **`pass`** |

The documented clause is **met**, with margin. After more than twenty
cycles of citing this gate, its second half has an answer.

### But the archive is far from evenly ancestral, and that is the finding

A pass is not the whole picture, and the instrument was built to say so
without moving the bar. Uniform occupancy across 38 founder lines would
put each at 2.6%; the largest holds **28.5%**, and:

| Founder line | Cells | Share |
| --- | --- | --- |
| `mg_wfc_037` | 131 | 0.2848 |
| `mg_wfc_046` | 50 | 0.1087 |
| `mg_seed16_013_sprout` | 34 | 0.0739 |
| `mg_wfc_045` | 28 | 0.0609 |
| `mg_seed16_019_bat` | 28 | 0.0609 |
| `mg_seed16_037_crane` | 24 | 0.0522 |

**Four founder lines hold half the archive.** The documented clause
cannot see that — it asks about one lineage, and one lineage is at
0.2848. Reported as an observation, deliberately outside the verdict:
widening a documented bar because the measurement came out interesting
is precisely what the pre-registration discipline forbids.

### The dominant lines were founded by the *losing* generator

The two largest lines — 39.4% of the archive between them — are founded
by **`mg_wfc_*` creatures**: the WFC half of the bootstrap population.
Across the 25 reported lines, WFC-founded lines hold 283 cells against
160 for seed-corpus-founded lines. The loop's adopted generation layer
is `constrained` (DR 0042), and every one of those 460 elites was bred
by it — but the *ancestry* of the space is dominated by lines the WFC
bootstrap started. Generation layer and founder stock are independent
facts, and this is the first measurement that separates them.

### Depth, and a cross-check with L1

Elite lineage depth spans **0 to 18** generations of descent (modal
depths 5, 1, 4, 9, 3), so these are genuinely deep lines, not shallow
mutations of the bootstrap. Exactly **one** elite has no recorded
ancestry at all.

That last number cross-checks L1 neatly. Depth-1 elites (47 of them)
are creatures generated directly from a seed — the constrained half of
the bootstrap — and together with the single self-founded WFC creature
that leaves roughly 48 bootstrap creatures still holding niches at
generation 80. L1 measured a permanent tax of exactly 38 refusals per
generation from SLIP-illegal bootstrap parents, which at the loop's
round-robin rate (768 requests over 460 parents ≈ 1.67 uses each)
implies on the order of 23 unbreedable elites. Two instruments built
for different questions, agreeing on the same residual bootstrap
population.

## Verification

```powershell
PS> python -B -m unittest test_lineage_dominance   # (from labs/map_elites_archive)
ModuleNotFoundError: No module named 'lineage_dominance'   # RED
# after the loop seam + the instrument:
Ran 17 tests ... OK
PS> python -B -m unittest discover -s labs/map_elites_archive -p "test_*.py"
Ran 181 tests ... OK                    # 164 + the 17 L2 pins; L1/K2/K3 untouched
PS> python -B labs/map_elites_archive/lineage_dominance.py
occupied 460 / 512 cells; 38 founder lines
max founder share 0.284783 vs bar 0.4 -> PASS
founders holding half the archive: 4
   131  mg_wfc_037
    50  mg_wfc_046
    34  mg_seed16_013_sprout
wrote data/archives/lineage_dominance_stage0.json
# 279.4 s vs the loop's registered 1200 s bound
```

One pin was relaxed during implementation and the reason is recorded
rather than buried: an initial assertion that the per-founder shares
sum to exactly 1.0 at six decimal places failed at 1.000003 — the
artifact rounds each share independently, so that pin was asserting
float rounding rather than the science. It was replaced with the exact
structural invariant (one share per founder line, `distinct_founders`
of them) plus a tolerance-appropriate sum check. No measured value
changed.

## HONEST REMAINDER

1. **The clause judges a SINGLE lineage.** A bar on one founder line
   cannot see a cartel of three, so concentration across several lines
   rides in the artifact as an observation
   (`founders_holding_half_the_archive`) and is deliberately **not**
   part of the verdict. Whether the documented clause is the right
   shape of question is a documentation matter, not something this
   slice may quietly widen.
2. **A founder line is not an E5 recurrent family.** One is ancestry,
   the other is descriptor similarity — Phase E's 52 families were
   measured by coarse-descriptor intersection across seeds, not by
   who descends from whom. The two are not compared here, and
   comparing them (do morphologically-recurrent families share
   ancestry, or converge from different lines?) is a genuinely
   interesting question that belongs to its own record.
3. **One seed, one parameter set** — the documented budget, run once.
   Anything distributional needs E4's ten-seed protocol.
4. **The 576-vs-512 divergence stands declared but unresolved.** This
   slice refuses to equate them; deciding what the documented
   repertoire size *should* be now that the geometry is proven at 512
   is a question for the records that own the geometry — and L3 is
   about to re-derive that geometry's edges.

## Sources

- `audits/TODO.md` (cycle 22 L2) · `research/experiment_reports/2026-07-26-phase-k-gate.md` (the survey that named this the sharpest unmet documented item)
- `docs/project-research/deep-research/01/deep-research.md` (the gate clause at line 205) · `research/questions.md` (Evolution Q1, the qualitative form)
- `labs/map_elites_archive/lineage_dominance.py` (+ `test_lineage_dominance.py`) · `labs/map_elites_archive/evaluation_loop_scale.py` (the `collect_lineage` seam)
- `packages/mecha_engine/src/mecha_engine/generation/generate.py` (`ancestor_ids` composed oldest-first — the ancestry the founder rule reads)
- `data/archives/lineage_dominance_stage0.json` (the artifact) · `data/archives/recurrent_families_stage0.json` (Phase E's 52 families — the qualitative answer this clause quantifies) · `data/archives/coverage_qd_gates_stage0.json` (the clause's other half)
- `research/decision_records/0029-16x16-default-grid-scale.md`, `0032-map-elites-ga-gate-disposition.md`, `0040-novelty-first-evolution-surface.md`, `0042-generation-layer-loop-revisit.md`
- `research/algorithm_cards/evaluation_loop_scale.md` (the card's L2 evolution entry)
