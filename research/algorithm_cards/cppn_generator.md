# Algorithm Card: CPPN Generator (Indirect Encoding)

## Purpose

Disposition the dossier's *Indirect encoding* row (*"CPPN,
HyperNEAT-style regularity"*) at its documented role — *"Keep as a late
exploratory generator"*, *"optional late-stage"* — which had never been
dispositioned: no card, no prototype, no verdict (cycle 25 O4).

## Mathematical Basis

- **Compositional pattern-producing network**: the body is a function of
  position. Per cell, inputs (x_n, y_n) ∈ [−1, 1], radial distance
  r = √(x_n² + y_n²), and the bilateral-symmetry channel s = |x_n| feed
  six seeded hidden nodes drawn from {sin, cos, gauss, sigmoid, abs};
  one tanh output channel per generator token; the cell takes the
  argmax. Symmetry and repeated motifs come free of the corpus — the
  network never sees a training grid.
- **Two declared design choices, part of the generator**: the empty
  channel gains a centered radial bias (`gain · (r − 0.5)`: empty
  penalized in the canvas middle, favored at the rim — the same prior
  the WFC lab learns from its corpus), and the center cell is a germ
  cell. One anchor is anointed at the strongest body activation,
  mirroring the promoted generator's one-anchor semantics.
- Deterministic per (rng_seed, size); stdlib-only.

## Inputs

- An integer seed and a grid size; no corpus (a true de-novo arm)

## Outputs

- Deterministic rich-alphabet candidates; measured by the B2 bake-off's
  own `measure_arm` in `data/wfc_grid/stage2_generator_arms_stage0.json`

## Strengths

- **symmetry_mean 0.475226** — above the WFC family (wfc 0.3973, hybrid
  0.395171); the dossier's regularity claim shows up in the measurement
- 100/100 unique silhouettes, training-copy rate 0.0, silhouette
  entropy at the batch maximum; emits the full rich alphabet including
  `sensor`, a role the committed wfc row lacks

## Weaknesses

- **Validity 0.12** against the 0.85 dossier bar — and the mechanism is
  mass, not incoherence: 79 of 88 invalid bodies are connected cores
  below the DR 0029 18-cell floor (only 9 disconnect)
- readability_proxy_mean 0.446945 vs the adopted layer's 0.79663

## Failure Modes

- Activation blobs scale with the network's random weights, not with the
  documented mass floor — the encoding has no notion of cardinality, so
  most bodies compose too small (the dossier's *"hard integration with
  semantic pixels"* risk, measured as a mass shortfall)

## Integration Risk

High (the dossier's own rating). Nothing is integrated.

## License Status

Original stdlib-only code, Apache-2.0.

## Prototype Result

At the committed B2 protocol (batch 100, seed 1030), judged against the
adopted constrained layer's committed row under a pre-registered rule:
validity 0.12 (bar 0.85) → the first gate, nothing offsets it.
Prediction (recorded first) confirmed, with one refinement it did not
contain: the failure is the mass floor specifically.

## Decision

**REJECT** as a generator (DR 0057). The recorded path back — a
re-opener, not a task: the arm's documented selling point is regularity
**under mutation**, which a generator-only bake-off cannot see
(`cppn_under_evolutionary_mutation_not_measured` in the artifact's
blocked states). Any return also owes the mass-floor mechanism an
answer before it owes anything else.

## Sources

- `labs/wfc_grid/stage2_generator_arms.py` (+ `test_stage2_generator_arms.py`)
- `data/wfc_grid/stage2_generator_arms_stage0.json`
- `research/experiment_reports/2026-08-08-stage2-generator-arms.md`
- `research/decision_records/0057-stage2-generator-arms-dispositioned.md`
- `docs/project-research/deep-research/01/deep-research.md` (the indirect-encoding row; the method matrix's CPPN row)
- `data/wfc_grid/generation_bakeoff16_stage0.json` (the committed baseline)
