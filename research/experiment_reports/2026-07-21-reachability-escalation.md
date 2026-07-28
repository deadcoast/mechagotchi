# Experiment Report: The Last Nine Bins — Five Reached, Four Bounded by Measure-Thin Windows (Cycle 21 · SHARED · K3)

Date: 2026-07-21

## WHY

J1 proved 417/512 descriptor bins reachable under the engine's own
move set; DR 0038's vocabulary cure leapt the probe to 503/512,
leaving **nine bins unreached within budget 200** — every one, the
committed artifact shows, at best_distance 1 (one octile step away on
one axis). K3 escalates the probe under the FULL post-DR-0038 move
set: budget 200 → 2000 per bin, the DR 0038 resample-temperature rider
on an attempt-indexed ladder over its full legal range
(None, 0.5, 1.0, 1.5, 2.0), elite depth 4 → 8 — protocol
pre-registered in the module before the run, targets the committed
artifact's bins VERBATIM, the move set still `generate_candidate` only
(no hand-painted exceptions; the descent's distance-to-target
selection subsumes novelty-first for a single-target probe). New this
slice: the **blocking-axis instrument** — for every bin that stays
unreached, the required octile interval from the frozen edges and the
best raw value attained on the blocking axis CONDITIONED on the other
two axes sitting on-target, so a bound names its gap in numbers.

## THE VERDICTS (126 s vs the registered 900 s bound)

**Five reached — 508/512 now proven reachable**, every witness
validator-passing and bin-recomputed (committed in the artifact):

| Bin | Attempts | Witness temperature |
| --- | --- | --- |
| [3, 0, 5] | 924 | **1.5 — the rider's win** |
| [4, 0, 7] | 105 | **2.0 — the rider's win** |
| [7, 2, 0] | 391 | None (budget + depth) |
| [7, 4, 4] | 86 | None |
| [7, 6, 2] | 691 | None |

Two of the five fell ONLY on high-temperature attempts — the DR 0038
mutation-temperature knob paying off at exactly the surface its record
chartered it for. Three extreme-symmetry bins (7,·,·) fell to budget
and elite depth alone: J1's octile-corner "structured emptiness" was,
for these, a budget artifact.

**Four bounded sharper** (2000 attempts each, still best_distance 1) —
and the instrument converts the structural hypothesis into measured
mechanism: **the remaining emptiness is measure-thinness, not
distance**:

- **[1, 0, 2]**: needs visual_complexity octile 0 (< 0.8548); with the
  other axes on-target the attained minimum is 0.8562 — a gap of
  **0.0014**. The symmetry direction misses by 0.05 (attained ≤ 0.271
  vs required ≥ 0.3226).
- **[6, 6, 2]** and **[7, 5, 2]**: the complexity octiles 5–6 are
  razor-thin under the frozen derivation edges (windows 0.0069 and
  0.0094 wide); conditional attempts straddle the window from both
  sides without landing in it, jointly with a symmetry requirement the
  conditional attainment tops out below (0.849 vs ≥ 0.9212; 0.9296 vs
  ≥ 0.9543).
- **[4, 7, 4]**: the sharpest finding — **875 conditional candidates
  SPAN the required behavior_neediness interval [0.3825, 0.3975)
  without one landing inside it** (attained 0.2825–0.605). The
  neediness axis is quantized by integer cell counts; an octile window
  0.015 wide can fall between attainable levels for the morphology
  class that satisfies the other two axes. Octile emptiness by
  QUANTIZATION is a different phenomenon than octile emptiness by
  range, and the instrument distinguishes them.

Per the standing rule: these four stay **bounds, not impossibility
proofs** — but each bound now carries its measured gap, so any future
generator increment (or an analytical emptiness proof for the
quantization case) charters against numbers, not vibes.

## Verification

```powershell
PS> python -B -m unittest test_reachability_escalation test_reachability_probe   # (from labs/map_elites_archive)
Ran 12 tests ... OK      # 6 new escalation pins + the J1 pins untouched
PS> python -B -m unittest discover -s labs/map_elites_archive -p "test_*.py"
Ran 142 tests ... OK
PS> python -B labs/map_elites_archive/reachability_probe.py --escalate
5 reached ... 4 bounded SHARPER ...   # 126 s vs the 900 s bound
```

Process note, recorded not hidden: this slice ran
**implementation-first** — the escalation function was written minutes
before its pins, inverting the RED-first order the house discipline
prescribes. No pin was staged retroactively to fake a RED; the
deviation is named here as the honest record.

## HONEST REMAINDER

1. **Four bins stand bounded** with measured gaps: one at 0.0014 from
   the boundary (a hair the move set may close by chance at higher
   budget), two behind razor-thin joint windows, one behind suspected
   quantization emptiness — the last is the candidate for an
   ANALYTICAL emptiness argument (its own record if attempted; a
   proof, never a fiat).
2. **The J1 base artifact stays the budget-200 truth** under its own
   parameters; prose citing "9 unreached" now cites this escalation's
   5/4 split.
3. The thin-window mechanism implicates the FROZEN derivation edges
   (octiles over a 600-candidate derivation) — whether the geometry
   itself should re-derive under the DR 0042 generation layer is a
   named question for the archive's own records, not smuggled here.
   **ANSWERED 2026-07-26 by cycle 22 L3**
   (`2026-07-26-geometry-consistency.md`): the geometry is **not
   stale** — E1's protocol re-run under today's code reproduces the
   committed edges exactly, against a measured sampling control of
   0.0102, because the frozen artifact was already regenerated at the
   DR 0038 commit. So these thin windows are a real property of the
   distribution and the quantization hypothesis HARDENS. Note also
   that this escalation's edges are **derived live from all 50 seeds**,
   not the frozen train-derived set the evolution loop uses — the two
   differ by up to 0.0375, so this report's bin intervals (e.g.
   neediness `[0.3825, 0.3975)`) belong to the probe's geometry, and
   its `508/512` is not directly comparable to the loop's `460/512`.

   > **Dated note, 2026-07-28 (cycle 24 N2 / DR 0050) — "derived live"
   > is no longer true, and this report's own wording is why it
   > mattered.** The blocking-axis instrument above describes its bounds
   > as *"the required octile interval from the **frozen** edges"*, but
   > this escalation derived them live and recorded none of them in its
   > artifact. The probe geometry is now genuinely frozen and committed
   > (`data/archives/probe_edge_freeze_stage0.json`), loaded through one
   > shared loader, and pinned against a live re-derivation. **No number
   > in this report changes** — the frozen set reproduces the draw these
   > bounds were computed under exactly (N2's G1), which is what makes
   > the intervals above still correct. The comparability point in this
   > paragraph is unchanged and is now DR 0046's standing rule.

## Sources

- `audits/TODO.md` (cycle 21 K3) · `research/experiment_reports/2026-07-20-reachability-probe.md` (J1) + `2026-07-20-vocabulary-alphabet.md` (the DR 0038 leap + the rider)
- `labs/map_elites_archive/reachability_probe.py` (the escalation protocol + `--escalate`) + `test_reachability_escalation.py` (6 pins)
- `data/archives/reachability_escalation_stage0.json` (verdicts, witnesses, blocking instrument) + `reachability_probe_stage0.json` (the committed targets, verbatim)
- `packages/mecha_engine/src/mecha_engine/generation/generate.py` (`resample_temperature`, DR 0038)
