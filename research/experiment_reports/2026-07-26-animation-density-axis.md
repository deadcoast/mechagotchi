# Experiment Report: `animation_density` — The Axis Earns Its Place, and Still Cannot Be Adopted (Cycle 22 · SHARED · L4)

Date: 2026-07-26

## WHY

The dossier's own worked archive entry (`deep-research.md:526-532`)
shows a **four**-axis descriptor:

```json
"descriptor": {
  "symmetry": 0.78, "visual_complexity": 0.41,
  "neediness": 0.29, "animation_density": 0.63
}
```

The engine carries three (baseline) / six (extended) and no animation
axis. `research.md:616-629` names ten intended niche axes; the Phase-K
gate's survey flagged the gap; and since Phase C/H built the clip
model, an animation measure is finally derivable from engine truth.
This is also the open half of **Evolution Q2** — *"Which behavior
descriptors make useful archive niches?"*

## WHAT

**The definition is CHOSEN, not documented — stated before anything
else.** `animation_density` appears in the documentation **exactly
once**: as a value in that JSON example. There is no formula, no range,
no threshold, anywhere. So this slice does not implement a documented
axis; it *proposes* one and asks whether it earns a place. Calling a
chosen definition a documented one would be the same class of error L1
caught in K2.

The proposal, grounded in the engine's own clip tables:

> `animation_density(grid)` = the fraction of live cells whose role the
> clip model animates.

The animating role set — `antenna`, `sensor`, `effect`, `limb`,
`joint`, `decoration` — is **read from `clip_model` at import**, never
copied, so a change to the engine's clip tables moves this axis with
it. A pin enforces that.

**The gates, pre-registered before the run, refusal first-class:**

- **A1 spread** — must support 8 octiles (7 *distinct* interior edges),
  the same `supports_full_bins` test every incumbent axis passes.
- **A2 independence** — `|Pearson r|` against every incumbent axis
  below **0.5**.
- **A3 discrimination** — among population pairs sharing the **same
  three-axis bin**, at least **0.2** must land in different animation
  octiles. This is the axis's entire purpose.
- **A4 coverage cost** — **reported, never gated**: a fourth axis takes
  the space from 8³ = 512 cells to 8⁴ = 4096.

**Which geometry would it join?** L3 found the repo runs two. This
candidate is judged against the **incumbent** (frozen train-derived)
geometry, because that is where coverage and QD are reported.

## FINDINGS

### The machine gates pass — decisively

| Gate | Bar | Measured | Verdict |
| --- | --- | --- | --- |
| A1 spread | supports 8 bins (7 distinct interior edges) | **7 distinct, `supports_full_bins: true`** | **pass** |
| A2 independence | \|r\| < 0.5 | **0.173** (max) | **pass** |
| A3 discrimination | ≥ 0.20 | **0.543** | **pass, 2.7× the bar** |

The axis spans 0.0112 → 0.600 with mean 0.1924 — real spread, not a
degenerate constant.

**It is very nearly orthogonal to everything the archive already
measures**: symmetry 0.173, visual complexity **0.068**, behavior
neediness 0.141. Whatever animation density captures, the incumbent
three axes are not already capturing it.

**And it does the job the axis exists for.** Among the 656 population
pairs that share the *same* three-axis bin — creatures the current
geometry cannot tell apart at all — **356 (54.3%) land in different
animation octiles**. More than half of the archive's current
indistinguishability is animation structure it has no coordinate for.

### The cost is real, and reported rather than buried

| | 3-axis | 4-axis |
| --- | --- | --- |
| cells | 512 | 4096 |
| occupied | 289 | **448** |
| coverage | **0.5645** | **0.1094** |

The fourth axis reveals **159 more distinguishable creature classes**
(+55% occupied cells) — and spreads the same population across eight
times the space, so coverage as a *fraction* falls five-fold. Both
numbers are true, and neither is the whole story: the trade is between
resolution and density, and it is exactly the kind of trade that must
be decided by a record rather than absorbed by an instrument.

### The verdict: `adoptable_pending_blocked_clause` — NOT adopted

Every machine-side gate passes, and adoption still cannot be claimed,
because the **documented** selection criterion is not a machine
measure. `deep-research.md:204` requires a descriptor set *"selected
with inter-rater interpretability ≥ 0.7"* — an inter-rater statistic,
which needs the owner-deferred human panel.

**No proxy is substituted for it.** The repo has been burned by exactly
that once already: the transducer study's "preference" number is a
readability proxy, and it is labelled as one everywhere it appears. A
machine-side correlation dressed up as interpretability would be the
same mistake, so the clause is **blocked explicitly** and named in the
artifact's `blocked_states`.

What this study can honestly conclude is narrower and still useful:
**the axis is worth the human panel's time.** It spreads, it is
independent, and it separates over half the creatures the current
geometry conflates. If a panel is ever scheduled, this is a descriptor
worth putting in front of it.

### An honest reading of the realised-motion observation

The axis measures *potential* animation. The realised figure — cells
that actually vacate their home position during `idle`, the one clip
with zero whole-body translation — comes out at **0.0417** against the
potential **0.1924**.

That gap is **mostly the clip schedule, not collision skips**, and
saying otherwise would misread it. `CLIP_LIMB_STEP["idle"]` and
`CLIP_JOINT_FLEX["idle"]` are `[0, 0, 0, 0]`: limbs and joints — by far
the largest animating-role populations in the corpus — **do not move
during idle at all**. Only sway (antenna/sensor), decoration bob, and
effect flicker are exercised. The realised number is therefore a
lower bound measured through one clip's schedule, not evidence that
three-quarters of animating cells are blocked.

## Verification

```powershell
PS> python -B -m unittest test_animation_density_axis   # (from labs/map_elites_archive)
ModuleNotFoundError: No module named 'animation_density_axis'   # RED
# after the axis + the study:
Ran 21 tests ... OK
PS> python -B labs/map_elites_archive/animation_density_axis.py
verdict: ADOPTABLE_PENDING_BLOCKED_CLAUSE
  A1 supports_full_bins : True
  A2 correlations       : {'symmetry': 0.173412, 'visual_complexity': 0.068047, 'behavior_neediness': 0.141292}
  A3 discrimination     : 0.542683 (356/656 same-bin pairs)
  A4 coverage cost      : 289/512 (0.564453) -> 448/4096 (0.109375)
  realised idle density : 0.041683 (potential - realised = 0.150755)
wrote data/archives/animation_density_axis_stage0.json
```

Two pins were adjusted during implementation, both recorded rather than
buried: a provenance assertion was case-sensitive against text that
opens with "CHOSEN", and the realised-motion invariant was moved off a
hand-built stub grid onto **real committed seed creatures**, because
the clip model consumes whole engine grids (the stub lacked `palette`).
The second change made the pin stronger, not weaker. No measured value
was affected.

## HONEST REMAINDER

1. **The documented interpretability clause stays BLOCKED.** Adoption
   is not available to any machine-side study, and this one does not
   pretend otherwise.
2. **Judged on the derivation population, not on the loop's elites.**
   Whether the axis discriminates as well among the creatures the
   archive is actually *filled* with is L3's open question wearing a
   different hat — and the L2 lineage seam already exposes the elite
   set, so it is cheap.

   > **Note added 2026-07-27 (cycle 23 M1 — this remainder was
   > UNDERSTATED; the wording above stands as what L4 expected).**
   > Carrying it out shows that two of the four gates above cannot be
   > re-measured on the elite population *at all* — not for want of
   > budget, but structurally. **The archive holds exactly one elite
   > per niche**, so no two elites can share a three-axis bin: **A3's
   > same-bin-pair denominator is zero**, and **A4 is degenerate**
   > (every elite already occupies a distinct 3-axis cell, so any
   > fourth axis maps it to a distinct 4-axis cell and
   > `occupied_4 == occupied_3` — for *any* fourth axis whatsoever).
   > A3 and A4 are properties of a **population**, not of an elite set.
   > A1 and A2 *are* defined on the elites and were re-measured.
   > What would genuinely answer A3/A4 on the filled population is the
   > loop's **scored candidate stream** — every creature evaluated, not
   > only the winners — which is a different seam and a different
   > slice. See `2026-07-27-elite-population-measures.md`. **L4's
   > verdict is untouched**: `adoptable_pending_blocked_clause` stands,
   > and the documented interpretability clause is still BLOCKED on the
   > owner-deferred human panel.
3. **The definition is one of several defensible ones.** Potential
   animation by role was chosen for being deterministic, engine-sourced
   and explainable; a realised-motion definition across all five clips
   (correcting for whole-body translation) is a different axis and
   would need its own comparison.
4. **The coverage trade is unresolved by design.** 289 → 448 occupied
   cells against a five-fold drop in coverage fraction is a decision
   for a record, not an instrument. Nothing here moves the geometry.

## Sources

- `audits/TODO.md` (cycle 22 L4) · `research/experiment_reports/2026-07-26-phase-k-gate.md` (the survey that named the gap) · `2026-07-26-geometry-consistency.md` (L3 — why the target geometry must be stated)
- `docs/project-research/deep-research/01/deep-research.md` (the four-axis descriptor at 526-532; the interpretability clause at 204) · `docs/project-research/research.md` (the ten intended niche axes, 616-629) · `research/questions.md` (Evolution Q2)
- `labs/map_elites_archive/animation_density_axis.py` (+ `test_animation_density_axis.py`, 21 pins)
- `labs/animation_system/clip_model.py` (the animating role tables, read at import) · `labs/map_elites_archive/niche_scale_archive.py` (the octile protocol)
- `data/archives/animation_density_axis_stage0.json` (the artifact) · `niche_scale_archive_stage0.json` (the incumbent geometry) · `data/animation_system/clip_model_stage0.json`
- `research/decision_records/0015-dormant-vocabulary-coverage.md`, `0029-16x16-default-grid-scale.md`, `0037-per-role-motion.md`
- `research/experiment_reports/2026-07-27-elite-population-measures.md` (cycle 23 M1 — the elite re-measure; the source of the dated note above, which corrects remainder 2 as understated: A1/A2 were re-measured on the elites, A3/A4 are structurally undefined there)
