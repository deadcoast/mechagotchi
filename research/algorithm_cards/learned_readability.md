# Algorithm Card: Learned Readability (physics-supervised pairwise ranker)

- **Name**: Learned readability — Bradley-Terry/logistic pairwise ranker
  over raw structural features, trained on physics-verified degradation
  pairs.
- **Purpose**: TRUE ML as the PRIMARY readability path (R3, decision
  record 0019) — replace the hand-designed heuristic mix as the
  authority while the manual rating pipeline remains the fallback and
  calibration check.
- **Mathematical basis**: Bradley-Terry preference model,
  `P(a > b) = sigmoid(w . (f(a) - f(b)))`, weights learned from zero
  init by stochastic gradient ascent with L2 (stdlib math). Absolute
  scores anchored on the corpus mean feature vector (a pairwise model
  only defines differences; unanchored sigmoids saturate at 1.0 for
  healthy grids and cannot discriminate — measured before fixing).
- **Inputs**: grids; degradation pair corpus (contrast collapse / organ
  scatter / silhouette noise / anchor erosion, each pair VERIFIED
  against its family's physical metric — WCAG luminance, connected
  components, organ geometry, anchor coverage; composite secondaries
  also verified so the trainer never receives sign-flipped physics).
- **Outputs**: learned per-feature weights (auditable), anchored score
  in [0,1], stage-0 report with heldout + leave-one-family-out metrics.
- **Strengths**: no human in the training loop; labels checked, never
  assumed; weights inspectable; deterministic.
- **Weaknesses**: linear ceiling unmeasured; readability defined by the
  degradation families chosen (corpus design is the model's worldview).
- **Failure modes**: orthogonal single-feature degradations make
  cross-family generalization mathematically impossible for a linear
  model (found in RED — fixed by composite degradations, mirroring how
  real damage co-occurs); unverified secondary perturbations flip
  training signs (found in RED — fixed by verifying both metrics).
- **Integration risk**: low — optional `readability_selection` arm in
  the evolution loop; absent = byte-identical.
- **License status**: original stdlib implementation.
- **Prototype result**: heldout accuracy 1.0; leave-one-family-out 1.0
  on all four families; learned weights rank organ_detectability
  (10.86) and inverse_component_count (9.28) highest, never-perturbed
  body_mass_ratio honestly 0.0. Live A/B (same seed, blend 0.7 vs 0.0):
  post-founder mean candidate readability 0.361 vs 0.270 (+34%), gen-3
  0.498 vs 0.199; trade-off recorded (13 vs 15 archive niches).
- **Decision**: adopt (primary readability signal); nonlinear model
  only if the linear ceiling is measured and found wanting.
- **Go-No-Go gate**: heldout AND every leave-one-family-out accuracy
  above chance; A/B shows the arm measurably raising candidate
  readability at a fixed seed; absent-arm parity pins green.

## Sources

- `research/decision_records/0019-learned-readability.md`
- `labs/readability_benchmark/learned_readability.py` (+ tests)
- `labs/runtime_integration/mecha_engine_runtime_loop.py` (+ test_readability_selection.py)
- `data/readability_benchmark/learned_readability_stage0.json`
- `data/runtime_integration/mecha_engine_evolution_readability_selection_stage0.json`
