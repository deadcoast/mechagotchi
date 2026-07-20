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
- Phase labels (`early_phase` / `post_takeover` / `unmeasured`) joined from the
  run's own `metrics.csv` on the checkpoint header epoch (filename+1), with
  `compression_ratio` and the pre-registered `TAKEOVER_COMPRESSION_RATIO = 0.5`
  midpoint; `run.json` reproduction manifests attached as
  `provenance.run_parameters` (cycle 19 I1)
- Report-level `phase_summary` and `corpus_truth`
  (`early_and_post_takeover` only when both phases are really present)
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

Implemented on 2026-05-12; the gate flipped on real data in cycle 17 G2
(2026-07-12); phase labeling added in cycle 19 I1 (2026-07-20).

Artifacts:

- `labs/cubff_transducer/real_snapshot_ingest.py`
- `labs/cubff_transducer/test_real_snapshot_ingest.py`
- `data/cubff_real_ingest/real_snapshot_ingest_stage0_report.json`
- `data/cubff_real_ingest/source_snapshots/README.md` (+ per-run `run.json`)
- `research/experiment_reports/2026-05-12-cubff-real-snapshot-ingest.md`
- `research/experiment_reports/2026-07-12-real-cubff-corpus.md` (G2)
- `research/experiment_reports/2026-07-20-post-takeover-corpus.md` (I1)

Measured result (2026-05-12 audit): upstream audited files 60, committed
upstream snapshot artifacts 0, committed upstream metrics logs 13 — the
original blocker. Measured result (G2/I1): real checkpoints from genuine
upstream runs ingested with 0 rejections; the paper-scale run's own metrics
cross the takeover ratio between epochs 2753 and 2817; the committed corpus
truth is `early_and_post_takeover` (counts in the stage-0 report).

## Decision

Adopted as the corpus gate (never a core dependency — the adoption note
stands): real snapshots flow through this ingest, phase-labeled by the run's
own instruments. The transducer comparison over post-takeover states is the
I2 study's charter.

## Go/No-Go Gate

Go only when real CuBFF snapshots are ingested and the semantic transducer beats
the existing baseline on readability plus either novelty, survival, or lineage
value.
