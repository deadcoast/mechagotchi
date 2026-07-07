# Experiment Report: Learned Readability (R3)

Date: 2026-07-06. Plan: decision record 0019.

## Objective

TRUE ML as the primary readability path (DR 0017 a.4): a model that
LEARNS readability from engine-derived signals with no human labels,
wired into the running evolution loop. The manual rating pipeline stays
exactly as built as the FALLBACK and calibration check.

## Method (per DR 0019)

Physics-supervised pairwise learning: the engine manufactures
provably-less-readable foils per grid (contrast collapse, organ
scatter, silhouette noise, anchor erosion) and every pair is admitted
only if its family's physical metric strictly decreased — verified,
never assumed. A Bradley-Terry/logistic pairwise ranker (stdlib SGD
from zero init) learns per-feature weights over raw measurables — never
the heuristic's blended score.

## RED findings that shaped the design (recorded, not hidden)

1. **Orthogonality**: with single-feature degradations, families don't
   overlap in feature space, so leave-one-family-out generalization is
   mathematically impossible for a linear model. Fix: composite pairs —
   a mild secondary perturbation from another family on half the pairs
   (real damage co-occurs).
2. **Sign-flipped physics**: an unverified secondary can accidentally
   RAISE its metric, feeding the trainer inverted labels. Fix: both
   perturbed metrics must verifiably decrease or the pure primary foil
   is kept.
3. **Sigmoid saturation**: a pairwise model only defines differences;
   the unanchored score was 1.0 for every healthy grid (measured — the
   first A/B was flat). Fix: scores anchored on the corpus mean feature
   vector.
4. **Schema surface**: organ features read the organs coordinate map,
   not per-cell tags — the physics verifier rejected an entire family
   until the degrader mutated both surfaces consistently.

## Results

Model (seed 20260706, 50 seed grids, 600 verified pairs, 80/20 split):

```txt
heldout accuracy                 1.0
leave-one-family-out             1.0 / 1.0 / 1.0 / 1.0  (all families)
learned weights (auditable)      organ_detectability 10.86,
                                 inverse_component_count 9.28,
                                 palette_contrast 6.97, anchors 5.89,
                                 symmetry 2.82, entropy -1.38,
                                 body_mass_ratio 0.00 (never perturbed
                                 -> honestly zero)
```

Live consumer — readability-aware parent selection (blend of learned
score and normalized archive fitness), A/B at the same seed where
blend 0.0 is the identical-machinery control:

```txt
mean candidate readability by generation
blend 0.7:  [0.362, 0.172, 0.412, 0.498]
blend 0.0:  [0.362, 0.172, 0.438, 0.199]
post-founder mean: 0.361 vs 0.270 (+34%); generation 3: 0.498 vs 0.199
trade-off recorded: 13 archive niches (blend 0.7) vs 15 (blend 0.0)
```

Creatures evolve to be easier to read because the engine learned what
readable means — the model steers parenting and the population's
candidate readability climbs where the control's collapses. The
diversity trade-off (2 fewer niches) is recorded for the blend
sensitivity study.

## Verification

RED -> GREEN: `labs/readability_benchmark/test_learned_readability.py`
(12 tests) and `labs/runtime_integration/test_readability_selection.py`
(4 tests, incl. the A/B and absent-arm byte-parity). Full lab sweep
(11 labs) + package suite green.

## Decision

Adopt the learned model as the primary readability signal;
`manual_calibration_check` stays in blocked_states as the FALLBACK
path's job when the owner schedules the human study — a quality check,
never a development blocker. Next per DR 0019: blend sensitivity at
scale, then promotion by its own record.

## Sources

- `research/decision_records/0019-learned-readability.md`
- `research/algorithm_cards/learned_readability.md`
- `labs/readability_benchmark/learned_readability.py`, `labs/readability_benchmark/test_learned_readability.py`
- `labs/runtime_integration/mecha_engine_runtime_loop.py`, `labs/runtime_integration/test_readability_selection.py`
- `data/readability_benchmark/learned_readability_stage0.json`
- `data/runtime_integration/mecha_engine_evolution_readability_selection_stage0.json`
