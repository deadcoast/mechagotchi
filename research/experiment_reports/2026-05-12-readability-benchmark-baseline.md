# Experiment Report: Readability Benchmark Baseline

Date: 2026-05-12

## Objective

Continue the post-v0.1 research sequence by adding a held-out readability
benchmark and a manual rating protocol.

## Source Basis

The v0.1 report identified readability as a remaining risk because previous
results used proxy metrics instead of human ratings. PCG evaluation literature
warns that procedural content evaluation lacks universal consensus and benefits
from structured, reusable methods. Pixel-art sprite generation work also mixes
quantitative image metrics with visual inspection, which supports keeping proxy
metrics and manual ratings as separate evidence streams.

Sources:

- https://arxiv.org/abs/2404.18657
- https://ojs.aaai.org/index.php/AIIDE/article/view/21951
- https://arxiv.org/abs/2208.06413

## Scope

Included:

- `labs/readability_benchmark/readability_benchmark.py`
- `labs/readability_benchmark/test_readability_benchmark.py`
- held-out sample assembly from seed, constrained, and Markov sources
- proxy metric scoring
- manual rating protocol with 1-5 scale and five questions
- artifacts under `data/readability/`

Not included:

- real human ratings
- reviewer UI
- blinding/randomized presentation order
- proxy/human agreement analysis
- display calibration

## Verification

RED command:

```powershell
python -B -m unittest discover -s labs\readability_benchmark -p 'test_*.py'
```

Initial result:

```txt
ModuleNotFoundError: No module named 'readability_benchmark'
```

GREEN command:

```powershell
python -B -m unittest discover -s labs\readability_benchmark -p 'test_*.py'
```

Result:

```txt
Ran 5 tests in 0.033s
OK
```

Lab command:

```powershell
python -B labs\readability_benchmark\readability_benchmark.py --output-dir data\readability --count-per-source 10 --rng-seed 20260512
```

## Metrics

Proxy score components:

- validity
- connected component score
- body mass score
- silhouette entropy score
- symmetry score
- organ detectability
- palette contrast
- animation anchor coverage

Manual protocol questions:

- silhouette
- organ clarity
- palette contrast
- animation readiness
- companion appeal

Human ratings are explicitly uncollected in Stage 0.

## Results

| Source | Samples | Valid | Mean proxy readability | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: |
| seed_holdout | 10 | 10 | 0.867316 | 0.825241 | 0.904102 |
| constrained_holdout | 10 | 10 | 0.830172 | 0.761579 | 0.897921 |
| markov_holdout | 10 | 0 | 0.374730 | 0.175000 | 0.538311 |

Overall mean proxy readability:

```txt
0.690739
```

## Findings

The held-out benchmark separates the current generator families. Hand-authored
seed holdouts score highest. Constrained holdouts remain close to seeds while
preserving full validity. Markov holdouts score much lower and have zero valid
samples in this Stage 0 packet.

This supports the existing research decision: raw Markov output should remain a
proposal source or local probability model, not a final visual generator.

The manual rating protocol is now defined but not executed. The next evidence
step is to collect ratings from at least three reviewers, then compare median
manual scores against proxy readability.

## Decision

Keep the readability benchmark as `prototype`.

Use the benchmark before extending MAP-Elites descriptors so archive fitness can
include a more explicit readability term instead of relying only on body mass,
sensor count, and symmetry.
