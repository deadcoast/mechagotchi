# 0032 — MAP-Elites disposition after the documented GA-advantage gate refutation

- Status: accepted
- Date: 2026-07-09
- Cycle: 13 (ENGINE · Phase E · E4)

## Context

The dossier's MAP-Elites archive test decision gate: *"Keep MAP-Elites
if it yields at least 25% greater archive coverage than GA at the same
budget while keeping best-fitness within 10% of the strongest
comparator, and if the resulting archive is visually and behaviorally
diverse enough that a human evaluator can reliably distinguish at
least five recurrent families."*

E4 ran the comparison at the documented protocol — the documented 20k
evaluation budget, the documented ten paired seeds per comparator,
identical bootstraps, the shared winning WFC generator (the dossier's
own inputs spec), GA coverage read over its full evaluation history
(the GA-favorable reading), the rule pre-registered:

- Coverage gate: **MET** — MAP-Elites mean coverage 0.549 vs the ≥0.25
  gate (2.2×).
- Best-fitness clause: **MET** — identical means (0.9785) both arms.
- **GA-advantage gate: REFUTED** — +22.6% mean coverage over the GA vs
  the documented ≥25%, converged across sample sizes (three seeds:
  +22.9%; ten seeds: +22.6%). Not noise; a real miss by ~2.4 points.
- Family clause: **MET tenfold** (E5) — 52 recurrent morphological
  families across all ten independent seeded runs vs the documented
  ≥5.

  > **Count superseded by regeneration, noted 2026-07-27** (cycle 23 M4):
  > the committed artifact now reads **54**, the count having moved when
  > the DR 0038 vocabulary regenerated E4's rosters (commit `f8c171b`).
  > The clause's disposition is **unchanged and MET by a wider margin**;
  > only the figure quoted here is stale. See
  > `research/experiment_reports/2026-07-27-family-ancestry.md`.

## Why the advantage gate under-shoots, on the evidence

Both comparators consume the winning WFC generator per the dossier's
shared-inputs design. WFC retrained on ANY parent pool — even the GA's
scalar-selected top half — emits morphologically diverse candidates,
so the operator itself is the dominant illuminator and the GA's
history coverage lands high (0.448). The archive mechanism adds its
+22.6% on top of an operator that already explores. The gate's 25%
figure was written before the generator bake-off chose WFC; under a
weaker operator the archive's relative advantage would read higher by
construction. The measured trade is: +22.6% coverage, identical best
fitness, plus everything only the archive provides.

## Decision

**MAP-Elites remains adopted.** The refuted clause is recorded as a
first-class negative result (the Phase-B hybrid-refutation precedent),
not overridden and not hidden. The grounds, in order:

1. **The documented architecture requires the repertoire.** The
   founding documents define the engine as evolving through
   "quality-diversity survival archives" (validity-research §1.35);
   species memory is a core thesis, and a plain GA produces no
   repertoire to ship. Un-adopting the archive would shrink the
   documented scope — ruled out by the owner (2026-07-07): the
   documentation defines the scope.
2. **Three of the gate's four clauses hold**, one at 2.2× and one at
   10× their bars, at the full documented protocol.
3. **The refuted clause costs nothing measurable**: best fitness is
   identical, wall-clock is equivalent, and the +22.6% coverage is a
   strict improvement — the clause failed as a *threshold*, not as a
   *direction*.

## Re-opener (named, honest)

This disposition reopens if EITHER: (a) a future documented-scale
evaluation shows the archive mechanism costing welfare, fitness, or
wall-clock relative to scalar selection (direction reversal, not
threshold shortfall); or (b) the family/diversity clause fails at a
future scale (E5's 52-of-≥5 would have to collapse). The 25% threshold
itself may be re-litigated only against a documented re-derivation of
the gate under the WFC-operator regime — never silently relaxed.

## Sources

- `data/archives/coverage_qd_gates_stage0.json` (the ten-seed verdict)
- `data/archives/recurrent_families_stage0.json` (the family clause)
- `research/experiment_reports/2026-07-09-coverage-qd-gates.md`
- `research/experiment_reports/2026-07-09-recurrent-families.md`
- `docs/project-research/deep-research/01/deep-research.md` (the gate)
- `docs/project-research/validity-research.md` (§1.35)
- `research/decision_records/0031-wfc-generation-adoption.md`
- owner course correction, 2026-07-07 (scope is the documentation)
