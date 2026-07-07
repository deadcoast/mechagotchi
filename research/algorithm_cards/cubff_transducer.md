# Algorithm Card: CUBFF Semantic Transducer

## Purpose

Test whether computational-life dynamics can contribute hidden hereditary
signals to Mechagotchi without directly generating unreadable pixels.

## Mathematical Basis

Self-modifying program soups and emergent self-replication in simple
computational substrates.

## Inputs

- CUBFF simulation snapshots
- Tape or program statistics
- Replication events
- Entropy and motif counts
- Lineage churn

## Outputs

- Trait vector
- Mutation pressure
- Temperament modifiers
- Instability score
- Optional archive descriptor features

## Strengths

- High novelty
- Direct artificial-life relevance
- Can supply hidden lineage pressure separate from hand-authored rules

## Weaknesses

- Raw outputs are not human-legible companion bodies.
- CUDA path adds tooling complexity.
- It can distract from the baseline engine if promoted too early.

## Failure Modes

- Direct tape-to-pixel mapping creates noise
- Interesting dynamics with no measurable gameplay value
- Hidden signals become arbitrary constants
- Tooling cost exceeds research value

## Integration Risk

High.

## License Status

CUBFF is Apache-2.0 licensed. Confirm dependency and build implications before
any code reuse.

Sources:

- [Computational-Life-arXiv](https://arxiv.org/abs/2406.19108)
- [cubff-github](https://github.com/paradigms-of-intelligence/cubff)

## Prototype Result

First synthetic CUBFF-style semantic transducer lab completed on 2026-05-12.

Artifacts:

- `labs/cubff_transducer/cubff_transducer.py`
- `data/cubff_transducer/synthetic_snapshots.json`
- `data/cubff_transducer/cubff_transducer_stage0_report.json`
- `research/experiment_reports/2026-05-12-cubff-semantic-transducer-baseline.md`

Measured result:

- Direct tape-to-pixels baseline: 0/12 valid, 0/12 SLIP aligned, mean
  readability 0.0.
- Hybrid semantic compiler: 12/12 valid, 12/12 SLIP aligned, mean readability
  1.0.

Caveat: this was a synthetic CUBFF-style snapshot lab, not a CUDA CuBFF
simulation run.

Real snapshot ingest follow-up completed on 2026-05-12:

- `labs/cubff_transducer/real_snapshot_ingest.py`
- `data/cubff_real_ingest/real_snapshot_ingest_stage0_report.json`
- `research/experiment_reports/2026-05-12-cubff-real-snapshot-ingest.md`

Result: the official upstream tree at
`f212e849027c98fcf4b242eccfb5fed435223e23` contains metrics logs and
checkpoint-writing code, but no committed soup/checkpoint snapshot artifacts.
Local real snapshot ingestion remains at 0 records.

## Decision

Watch and lab-only. The transducer interface is worth preserving, but CUBFF
must not become a core dependency until real CuBFF snapshots beat the existing
baselines on readability plus either novelty, survival, or lineage value.

## Go/No-Go Gate

Adopt only if semantic transduction beats direct visual mapping and baseline
procedural mutation on readability plus either novelty or survival.

## Live Integration Result (2026-07-06, R2 / DR 0018)

Pipeline C is wired into the running evolution loop: per generation,
`extract_cubff_features -> mutation_pressure` scales damage severity.
Measured (same seed): a chaotic CuBFF soup drives a 1.17x multiplier
and 111 cells destroyed vs a stable soup's 0.90x and 88 — real
computational-life dynamics visibly moving the ecosystem. Only
scalars cross the boundary (never tape->tokens). Absent source
byte-identical; the runtime.evolve promotion is the next plan.
