# Experiment Report: Novelty-First at the Evolution Surface — Adopted on Both Axes (Cycle 20 · SHARED · J3)

Date: 2026-07-20

## WHY

I5b measured the novelty lever at the one-shot archive-insert
instrument (+0.078 coverage at a recorded QD cost) and handed
adoption to the surface that owns the trade. J3 judges it there: the
E3 evolution loop at the documented 20,480-evaluation budget, with
the decision rule PRE-REGISTERED in DR 0040 before the run — an arm
needs coverage gain ≥ +0.02 AND QD ≥ 0.95× baseline; the
highest-coverage adoptable arm wins; otherwise reject. For the game,
archive coverage is the variety the repertoire can ever surface and
QD is its quality — the trade belongs to a record.

## WHAT

**The arms live inside the loop** (`selection`, an additive
parameter; the historical baseline pinned byte-identical when asked
for): `novelty_first` collapses a 3× generation pool per generation —
generation is cheap, the SCORED budget is the bar — bins the pool
with the lifecycle-free descriptors, and scores first-of-unseen-niche
candidates first; `blend` alternates by generation parity.

**The measured verdict (matched budget, same seed): ADOPT
novelty_first — it wins on BOTH axes.**

| Arm | Coverage | QD | Wall |
| --- | --- | --- | --- |
| baseline | 0.763672 | 304.08 | 268 s |
| **novelty_first** | **0.785156 (+0.0215 ✓)** | **310.65 (1.0216 ✓)** | 774 s |
| blend | 0.769531 (+0.0059 ✗) | 311.02 (✓) | 464 s |

The one-shot instrument's trade DISSOLVES in the loop: first-reachers
claim niches early, and later generations refine them through elite
replacement — early coverage becomes lasting quality. Blend's
half-time novelty buys almost nothing: the lever wants every
generation.

**Adoption executed per the DR**: the loop's default `selection` is
`novelty_first`; the run-once wall-clock bound re-registers 600 →
1200 s (the overage is the 3× generation volume, never the scoring —
measured 774 s, cited, moved by the record, not silently); the loop's
own artifact regenerates under the adopted default; baseline and
blend stay runnable arms.

## Verification

```powershell
PS> python -B -m unittest discover -s labs/map_elites_archive -p "test_novelty_evolution.py"
ImportError: cannot import name ... from 'novelty_evolution'   # RED: the arms absent
# after the loop extension + comparison module:
Ran 8 tests ... OK
PS> python -B labs/map_elites_archive/novelty_evolution.py
# novelty_first: coverage_gain 0.021484, qd_ratio 1.021597, both bars MET
# blend: coverage_gain 0.005859 (bar NOT met)
# adopt:novelty_first
PS> python -B -m unittest discover -s labs/map_elites_archive -p "test_*.py"
Ran 127 tests ... OK              # the full archive lab under the adopted default
```

## HONEST REMAINDER

1. **The wall-clock cost is real and recorded**: the adopted default
   pays ~2.9× the baseline's generation volume (774 s vs 268 s at the
   documented budget) for +2.15pp coverage and +2.2% QD; the bound
   moved by the record.
2. **The game-side repertoire wiring** is the consumer's own
   increment — the repertoire inherits the richer loop truth when its
   consumer regenerates, never by smuggling.
3. **One seed at the documented budget** — the verdict is the
   protocol's, not a distribution; the arms stay runnable for any
   future re-judgment.

## Sources

- `audits/TODO.md` (cycle 20 J3), `research/decision_records/0040-novelty-first-evolution-surface.md` (the pre-registered rule + the filled decision)
- `labs/map_elites_archive/evaluation_loop_scale.py` (the arms), `novelty_evolution.py` (+ `test_novelty_evolution.py`)
- `data/archives/novelty_evolution_stage0.json` (the three-arm measurement), `evaluation_loop_scale_stage0.json` (regenerated under the adopted default)
- `research/experiment_reports/2026-07-20-occupancy-saturation.md` (I5b — the instrument this record judges in place)
