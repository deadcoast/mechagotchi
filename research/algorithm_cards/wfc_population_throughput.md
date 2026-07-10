# Algorithm Card: WFC Population Throughput (the elite parent path)

## Purpose

Measure the engine's promoted generation surfaces at the documented
population scale (~256 per generation) with parents drawn from archive
elites per the promoted evolve semantics — the WFC parent path
(per-generation model retraining on the elite pool) against the
constrained inner-loop path from the same parents — producing the
DR 0031 standing remainder's evidence (gap-analysis Phase E, E2).

## Mathematical basis

- WFC overlapping-pattern collapse (the adopted DR 0031 generator):
  position-conditioned token priors + right/down adjacency constraints,
  bounded restarts on wave contradictions.
- The evolve parent semantics: elites ordered by sorted niche key,
  round-robin assignment `parents[index % len(parents)]`, per-candidate
  seed `rng_seed + generation × 100000 + index` (verbatim from
  `runtime.evolve`'s default branch).
- MAP-Elites refresh: generated candidates scored (calibrated Stage 0
  fitness over a 24-tick stress-probed lifecycle) and inserted through
  E1's package-parity mechanics under the frozen empirical octile
  edges.

## Inputs

- The E1 scale archive bootstrapped from a 400-candidate mixed
  population (E1's proven surfaces, frozen edges).
- The 16×16 seed corpus (constrained generation model trained once, as
  evolve receives it; WFC model retrained per generation on parents).

## Outputs

- Per-generation, per-arm: validity rate, unique-signature rate,
  parent-copy rate, unique scale descriptors, failure counts.
- Archive growth under the WFC parent path (occupancy/coverage/QD).
- `measured`: per-candidate wall-clock vs the documented 250 ms bar
  (WFC retraining counted; constrained one-time training excluded).

## Strengths

- Measures the PROMOTED package surfaces, not lab twins.
- Both arms share identical parents and seed schemes — a controlled
  comparison.
- Failures (wave contradictions, parent rejections) recorded, never
  hidden.

## Weaknesses

- SLIP alignment deliberately out of scope (E3's loop owns it).
- The WFC arm retrains on elites without weighting by fitness — the
  elite pool is treated as a uniform corpus (matching how
  `train_wfc_model` consumes grids).

## Failure modes

- A narrow elite pool could over-constrain the WFC wave (contradiction
  storms) — bounded restarts + recorded failure counts guard the
  reading; observed failures at full scale: zero.
- Elite grids from mixed generators could carry token patterns the
  collapse cannot reconcile — same guard.

## Integration risk

Low for measurement; the inner-loop adoption itself is a
`runtime.evolve` change (additive, byte-identical off) belonging to
E3/a decision record.

## License status

Repo Apache-2.0 (DR 0028); stdlib only.

## Prototype result

Population 256 × 3 generations from 171-elite parents: validity 1.0 on
BOTH arms; WFC unique-signature rate 1.0 (constrained 0.996); WFC
7.04 ms per candidate including retraining, constrained 2.51 ms — both
under the 250 ms bar with ~35×/~100× headroom; archive 171 → 233
occupied niches (coverage 0.455) under the WFC parent path.

## Decision

**adopt** (as Phase E's population-scale generation evidence; the
evolve inner-loop switch stays a named decision for E3, now with its
evidence in hand).

## Go-No-Go gate

GO for E3: both arms meet the documented validity and time bars at
population scale and the WFC parent path sustains archive growth.
NO-GO triggers: collapse-failure storms on narrower elite pools, or the
alignment-gated loop (E3) refuting the unconstrained reading.

## Sources

- `labs/wfc_grid/wfc_population_throughput.py` (+ `test_wfc_population_throughput.py`)
- `data/wfc_grid/wfc_population_throughput_stage0.json`
- `research/experiment_reports/2026-07-09-wfc-population-throughput.md`
- `research/decision_records/0031-wfc-generation-adoption.md`
- `packages/mecha_engine/src/mecha_engine/generation/`
- `packages/mecha_engine/src/mecha_engine/runtime/evolve.py`
