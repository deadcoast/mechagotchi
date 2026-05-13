# Algorithm Card: CuBFF Real Snapshot Ingest

## Purpose

Gate CUBFF adoption on actual CuBFF soup/state exports instead of synthetic
CUBFF-style fixtures or metrics-only logs.

## Mathematical Basis

No new generative math is introduced. This is a provenance and normalization
layer for computational-life state snapshots.

## Inputs

- CuBFF `.dat` checkpoint files written by `--checkpoint_dir`
- JSON or JSONL Python callback state exports containing `soup`
- Source repo, source commit, language, seed, and capture method provenance

## Outputs

- Normalized real-CuBFF snapshot records
- First-program 64-byte `tape` vectors compatible with the semantic transducer
- Soup size, program count, soup hash, epoch, and optional replication scores
- Ingest report and upstream source audit

## Strengths

- Prevents synthetic data from being promoted into an adoption decision
- Separates real snapshots from metrics logs
- Captures enough provenance to rerun or reject questionable source data
- Supports both binary checkpoints and Python callback state dumps

## Weaknesses

- Binary checkpoints do not include replication scores
- Endianness/word-size assumptions come from the official writer
- No real snapshot can be produced without running CuBFF or obtaining saved
  state exports

## Failure Modes

- Treating `testdata/*.txt` metrics logs as snapshots
- Ingesting synthetic fixtures into the real snapshot drop zone
- Losing source commit or seed metadata
- Reusing checkpoint data from an incompatible CuBFF build without documenting
  the build

## Integration Risk

Medium. The parser is small, but any CuBFF runtime dependency remains high-risk
until real snapshots beat the existing baselines.

## License Status

CuBFF is Apache-2.0 licensed. This lab does not vendor CuBFF code or data; it
records source-derived format facts and local ingest code.

Sources:

- [paradigms-of-intelligence](https://github.com/paradigms-of-intelligence/cubff)
- [Computational-Life-arXiv](https://arxiv.org/abs/2406.19108)

## Prototype Result

Implemented on 2026-05-12.

Artifacts:

- `labs/cubff_transducer/real_snapshot_ingest.py`
- `labs/cubff_transducer/test_real_snapshot_ingest.py`
- `data/cubff_real_ingest/real_snapshot_ingest_stage0_report.json`
- `data/cubff_real_ingest/source_snapshots/README.md`
- `research/experiment_reports/2026-05-12-cubff-real-snapshot-ingest.md`

Measured result:

- Upstream audited files: 60
- Committed upstream snapshot artifacts: 0
- Committed upstream metrics logs: 13
- Local real snapshots ingested: 0

## Decision

Blocked on real snapshot availability. Do not revisit CUBFF adoption from the
synthetic transducer result. The parser and report gate are ready, but the
transducer comparison cannot run until real CuBFF checkpoint or Python callback
state exports exist.

## Go/No-Go Gate

Go only when real CuBFF snapshots are ingested and the semantic transducer beats
the existing baseline on readability plus either novelty, survival, or lineage
value.
