# Experiment Report: The Phase-E Gate — Evolution at Documented Scale (Cycle 13 · ENGINE · E1–E6)

Date: 2026-07-09

## WHY

The gap table's evolution row was ~3 orders of magnitude under the
documented regime: population 4, 3 generations, a handful of niches,
against a specification of ~576 niches, populations ~256, 20k–50k
evaluations, and the coverage/QD/family gates. Phase E (gap-analysis)
closes when evolution runs at the documented scale with the documented
gates judged. Cycle 13 ran E1–E5 end to end; this is the consolidated
gate.

## THE EVIDENCE, TASK BY TASK

- **E1 — the archive at documented niche scale**
  (`2026-07-09-niche-scale-archive.md`): the dossier's first-pass
  8×8×8 geometry (symmetry, silhouette-entropy visual complexity,
  behavior neediness) derived with EMPIRICAL octile edges from a
  measured population; mechanics parity-pinned byte-equal to
  `mecha_engine.archive`; 274/512 niches on a disjoint 3,000-candidate
  population; the evaluation unit measured FIRST (6.29 ms).
- **E2 — generation throughput at population scale**
  (`2026-07-09-wfc-population-throughput.md`): the PROMOTED surfaces
  at 256×3 from 171 archive-elite parents per the promoted evolve
  semantics; validity 1.0 both arms; WFC 7.04 ms/candidate WITH
  retraining vs the 250 ms bar (~35× headroom); the DR 0031 standing
  remainder's evidence delivered.
- **E3 — the evaluation loop at documented scale**
  (`2026-07-09-evaluation-loop-scale.md`): 20,480 stress-probed
  lifecycle evaluations over 79 generations of population 256,
  deterministic under seeds byte-for-byte; **stdlib HOLDS — 174 s
  measured vs the 600 s pre-registered bound** (the strongest NumPy
  trigger yet did not fire; 50k projects to 323 s, also inside).
- **E4 — the documented gates + the GA baseline**
  (`2026-07-09-coverage-qd-gates.md`), at the DOCUMENTED ten-seed
  protocol (twenty full-scale runs): **coverage gate MET** (0.549 vs
  ≥0.25, 2.2×); **best-fitness clause MET** (identical means across
  arms); **the GA-advantage gate REFUTED — +22.6% vs the documented
  ≥25%, converged** (+22.9% at three seeds → +22.6% at ten). Recorded,
  not fudged; dispositioned by **DR 0032** (MAP-Elites remains adopted
  — the documented architecture requires the repertoire; the clause
  failed as a threshold, not a direction; named re-openers).
- **E5 — the recurrent families**
  (`2026-07-09-recurrent-families.md`): **52 recurrent morphological
  families across ALL TEN independent seeded runs vs the documented
  ≥5** — the strict intersection, nothing curated; per-run family
  counts stable at 53–56. Species memory, measured.

  > **Count superseded by regeneration, noted 2026-07-27** (cycle 23 M4):
  > the committed artifact reads **54**, per-run counts **57–58**. The
  > figures here are the pre-DR-0038 vocabulary's and stay true of it;
  > the artifact regenerated with E4's rosters at commit `f8c171b`
  > (*"recurrent families 52 → 54"*) and the prose was never updated.
  > The gate verdict is unchanged. See
  > `research/experiment_reports/2026-07-27-family-ancestry.md`.

Full sweep at the gate: 19 lab suites, the 291-test package suite, the
workshop suite, and the CLI suite — all green.

## THE GATE — GREEN

Evolution now runs at the documented regime: hundreds of niches
(281–283 occupied of 512 per run), populations in the hundreds (256),
the documented evaluation budget (20,480 per run; twenty such runs for
the gate), the documented gates judged at the documented protocol, and
recurrence proven across ten independent runs. The one refuted clause
is a first-class negative finding with a decision record — exactly how
Phase B handled the hybrid refutation.

## HONEST REMAINDERS (named, standing)

1. **The GA-advantage refutation** (+22.6% vs ≥25%) and DR 0032's
   re-openers: direction reversal, or family collapse.
2. **Occupancy saturation**: the WFC parent path plateaus ~55%
   coverage by ~generation 50; coverage beyond that needs novelty
   pressure, re-derived edges, or mutation-heavy arms — a named
   candidate, only with its own evidence.
3. **behavior_neediness is mass-dominated at 16×16** (6 distinct
   octile edges; 7 of 8 fine bins) — a recalibration candidate with
   its own evidence.
4. **The package scale-geometry seam is NOT promoted**: the engine
   archive still exposes baseline/extended modes; the 512-niche
   geometry lives lab-side. Promotion is a gated package change for
   whichever consumer demands it (likely the game's evolution surface,
   Phase F).
5. **SLIP alignment not enforced** in the Phase-E harnesses
   (generation measured without profile constraints; the ecosystem
   loop owns alignment).
6. **The 512-vs-576 documented figure discrepancy** stays recorded
   verbatim.
7. **The 50k upper budget** was projected (323 s), not run; artifacts
   ran the documented 20k lower bound.
8. **QDax stays untaken** (optional per the dossier) — stdlib measured
   holding at every Phase-E scale.
9. **Human distinguishability of families** stays owner-deferred
   (survey territory, never a blocker); its material is prepared.
10. **Evolve's inner loop on WFC**: E2's evidence is recorded; the
    `runtime.evolve` package change remains a named decision for when
    an engine consumer demands the scale loop.

## VERIFICATION

```powershell
PS> python -B -m unittest discover -s labs/map_elites_archive -p "test_*.py"
Ran 99 tests in 7.905s

OK
PS> python -B -m unittest discover -s packages/mecha_engine/tests -p "test_*.py"
Ran 291 tests in 6.520s

OK
# full sweep: 19/19 lab suites OK; workshop 60 OK; CLI OK
```

## CONSEQUENCE

Phase E is checked off in `docs/gap-analysis.md`. Cycle 13 archives to
`audits/complete/13/`. Cycle 14 opens **Phase F — the playable game:
the GAME track begins** (the engine track A–E is complete; the fleet's
welfare value, the render bridge, and the evolution repertoire all
cash out at the game's consumers, exactly as the Phase-C/D gates
named).

## Sources

- `research/experiment_reports/2026-07-09-niche-scale-archive.md` (E1)
- `research/experiment_reports/2026-07-09-wfc-population-throughput.md` (E2)
- `research/experiment_reports/2026-07-09-evaluation-loop-scale.md` (E3)
- `research/experiment_reports/2026-07-09-coverage-qd-gates.md` (E4)
- `research/experiment_reports/2026-07-09-recurrent-families.md` (E5)
- `research/decision_records/0032-map-elites-ga-gate-disposition.md`
- `docs/gap-analysis.md` (Phase E)
- `audits/TODO.md` (cycle 13, archived to `audits/complete/13/`)
