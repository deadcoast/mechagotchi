# Experiment Report: The Real Documented Bake-off — WFC Wins, the Hybrid Is Refuted (Cycle 10 · ENGINE · B2)

Date: 2026-07-08

## WHY

The dossier's stage-two protocol compares generator arms on named
metrics with hard thresholds (validity ≥85–95%, ≤250 ms per candidate
at 16×16) — and the historical bake-off ran without the documented WFC
field. With B1's lab in place, this is the first bake-off with all five
arms. The adoption rule was PRE-REGISTERED in code before the run:
validity bar ≥0.85, rich-alphabet emission REQUIRED (Phase A's named
remainder is the reason this phase exists), then descriptor novelty,
silhouette entropy, readability proxy.

## PROTOCOL (adaptations recorded)

30/10/10 stratified split (the dossier's 72/24/24 over the real
50-creature corpus); batches of 100 per arm at one fixed seed; organ-
presence F1 against the train corpus's modal role set; silhouette
entropy as Shannon bits over the batch's silhouette distribution;
descriptor novelty as unique baseline archive descriptors per candidate;
readability proxy labeled 8×8-calibrated; human pairwise preference NOT
collected (owner-deferred survey, recorded); generation time measured
wall-clock in a machine-flagged section.

## THE TABLE

| Arm | Validity | Connected | Organ F1 | Symmetry | Entropy (bits) | Novelty | Readability* | Copies | Rich | ms/cand† |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :-: | ---: |
| random | 0.46 | 1.00 | 0.90 | 0.83 | 5.92 | 0.14 | 0.73 | **0.53** | yes | 0.2 |
| markov | **0.02** | 0.13 | 0.63 | 0.14 | 6.62 | 0.29 | 0.36 | 0.00 | no | 0.2 |
| constrained | 1.00 | 1.00 | 0.73 | 0.81 | 6.45 | **0.32** | **0.84** | 0.00 | **no** | 2.3 |
| **wfc** | **1.00** | **1.00** | **0.96** | 0.40 | **6.64** | 0.25 | 0.69 | 0.00 | **yes** | 6.3 |
| hybrid | 1.00 | 1.00 | 0.97 | 0.40 | 6.64 | 0.22 | 0.70 | 0.00 | yes | 6.2 |

\* 8×8-calibrated proxy. † machine-dependent measured section; all arms
pass the ≤250 ms gate with ~40× headroom.

## VERDICT

- **Eligible**: wfc, hybrid (validity ≥0.85 AND rich alphabet).
  `constrained` clears validity with the best readability and novelty
  but CANNOT emit the rich alphabet — barred by the requirement this
  phase exists to satisfy, not by quality. `markov` at 16×16 is 2%
  valid (the same global-connectivity blindness B1 measured) — raw
  Markov is a proposal source, never a production path, exactly as the
  engine's own negative check has always said. `random` is 46% valid
  and 53% training copies — the honest floor.
- **Winner: wfc** (novelty 0.25 vs hybrid's 0.22; all 100 silhouettes
  unique). **The documented hybrid is REFUTED at this scale** — a
  first-class finding: its added stages over WFC are the
  mutation-temperature jitter and a validator gate, but the jitter
  varies only the mutation VECTOR (invisible to the baseline descriptor
  axes) and the gate never fires because the collapse already emits
  valid creatures. The documented pipeline's Markov stage is likewise
  already inside WFC — the collapse's proposal distribution IS the
  learned local statistic. Honest caveat: the jitter's value lives on
  the extended archive's mutation_stability axis, and the promoted
  `evolve` path applies its own jitter regardless — so nothing is lost
  by adopting the simpler arm.

## Verification

```powershell
PS> python -B -m unittest discover -s labs/wfc_grid -p "test_*.py"
Ran 16 tests in 4.503s
OK
PS> python -B -m unittest discover -s labs/grid_genome -p "test_*.py"
Ran 209 tests in 5.486s
OK   # markov_grid gained the size-derivation fix; all 8x8 pins intact
PS> python -B labs/wfc_grid/generation_bakeoff16.py
"winner": "wfc", "hybrid_won": false, "hybrid_refuted": true
```

## Sources

- `labs/wfc_grid/generation_bakeoff16.py` (+ `test_generation_bakeoff16.py`)
- `data/wfc_grid/generation_bakeoff16_stage0.json`
- `labs/wfc_grid/wfc_grid.py`, `labs/grid_genome/markov_grid.py` (size fix)
- `research/experiment_reports/2026-07-08-wfc-grid-lab.md`
- `docs/project-research/deep-research/01/deep-research.md` (the protocol and thresholds)
- `audits/TODO.md` (cycle 10 B2), `docs/gap-analysis.md` (Phase B)
