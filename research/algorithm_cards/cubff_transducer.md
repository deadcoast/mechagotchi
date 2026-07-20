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

## Promotion Result (2026-07-07, R2.5 / DR 0020)

The Pipeline C seam is promoted into `mecha_engine.runtime.evolve`
(`cubff_pressure_source`, keyword-only, default None byte-identical).
`runtime/_cubff.py` mirrors the lab authority verbatim; drift is
caught by `labs/cubff_transducer/test_package_cubff_parity.py`.
Promoted-surface measurement matches R2 (chaotic 1.17x vs stable
0.90x at the same seed). Real-snapshot exercise remains honestly
blocked: the ingest gate still reports awaiting_real_cubff_snapshots.

## Real-Study Result (2026-07-12 G3 · 2026-07-20 I2)

The blocker above closed in cycle 17 G2 (real corpus, the gate
flipped 9/0/0). G3 ran the documented study over 400 real early-phase
states: preference 400/400, invalid 0/400 → KEEP — with the sweep's
degeneracy scrutinized (direct arm 0/400 valid, both instruments
saturated; "post-takeover states would un-saturate" recorded as the
remainder). Cycle 19 I2 re-ran the study over a fresh 20-run fleet at
the PROVEN takeover scale (400 states, 14 post-takeover; onset
stochastic — 4/20 seeds cross by epoch 6,144) and **REFUTED the
pre-registered break**: the direct arm is still 0-valid with flat
readability over post-takeover states. The saturation is a property
of the ARMS, not the soup's phase — the semantic transducer is the
only viable path from real soup to a displayable creature in ANY
phase. Un-saturating the comparison now requires a DIFFERENT direct
arm (a structured tape decoder), a new study design with its own
record. Evidence: `data/cubff_transducer/real_transducer_study_stage0.json`
(G3, frozen) + `real_transducer_study_i2_stage0.json` (I2).

Pressure-seam harshness over real soup (2026-07-20 I3): through the
checkpoint seam post-takeover soup measures MILDER than early (the
harshness channels are format-silent); through the CALLBACK path —
the upstream's pybind11 module built at the audited commit,
`eval_selfrep` lighting `replication_per_prog` (2 vs 129,211
replicators early/post) — the engine's multipliers rise to
1.021–1.048, harsher measured, still under the 1.17× synthetic
precedent on every path. `lineage_churn` stays silent everywhere
(no upstream lineage-event stream — named). Evidence:
`data/game_client/real_weather_harshness_stage0.json` +
`data/cubff_real_ingest/callback_states/callback_states_compact.json`
(self-verifying: consumers recompute the engine numbers live).
