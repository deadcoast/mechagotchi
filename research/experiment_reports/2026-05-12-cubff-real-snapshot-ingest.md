# Experiment Report: CuBFF Real Snapshot Ingest

Date: 2026-05-12

## Objective

Continue the post-v0.1 research plan by testing whether the CUBFF semantic
transducer can move from synthetic CUBFF-style fixtures toward real CuBFF
snapshot ingestion.

## Method

1. Re-read the CUBFF plan gate and existing synthetic transducer lab.
2. Checked primary sources with web search, GitHub MCP, and a local clone of
   `paradigms-of-intelligence/cubff`.
3. Audited upstream commit `f212e849027c98fcf4b242eccfb5fed435223e23`.
4. Wrote failing ingestion tests before implementation.
5. Added a parser/reporting layer for real-format CuBFF checkpoints and Python
   callback state exports.
6. Generated the stage-0 ingest report from the empty local snapshot drop zone.

## Source Findings

The official CuBFF repository provides the CUDA-capable implementation used by
the Computational Life paper. The repo documents `make` or `make CUDA=0` plus
`bin/main --lang bff_noheads` as the basic run path.

The source exposes runtime state through fields such as `soup`, `epoch`,
`brotli_size`, and `replication_per_prog`. The checkpoint writer stores three
native `size_t` values followed by `num_programs * 64` soup bytes.

The audited upstream tree contains metrics logs under `testdata/`, but no
committed soup/checkpoint snapshot artifacts. Metrics logs are not sufficient
for Mechagotchi semantic transducer ingestion.

Sources:

- https://github.com/paradigms-of-intelligence/cubff
- https://arxiv.org/abs/2406.19108
- https://github.com/paradigms-of-intelligence/cubff/blob/main/common_language.h
- https://github.com/paradigms-of-intelligence/cubff/blob/main/cubff_py.cc

## Artifacts

- `labs/cubff_transducer/real_snapshot_ingest.py`
- `labs/cubff_transducer/test_real_snapshot_ingest.py`
- `data/cubff_real_ingest/real_snapshot_ingest_stage0_report.json`
- `data/cubff_real_ingest/README.md`
- `data/cubff_real_ingest/source_snapshots/README.md`
- `research/algorithm_cards/cubff_real_snapshot_ingest.md`

## Results

From `data/cubff_real_ingest/real_snapshot_ingest_stage0_report.json`:

- Upstream audited files: 60
- Upstream committed snapshot artifacts: 0
- Upstream committed run logs: 13
- Local ingested real snapshots: 0
- Rejected files: 0
- Decision: `blocked_real_snapshot_absent`

## Interpretation

This gate did not produce real transducer evidence because no real snapshots
were available in the official repo or local drop zone. That is the correct
research result: synthetic CUBFF-style data remains non-adoption evidence.

The useful progress is that the project now has an executable ingest contract
for real CuBFF checkpoints and Python callback state exports. It also has an
audit trail preventing metrics-only logs from being mistaken for snapshots.

## Decision

Keep CUBFF as blocked for adoption. Do not revisit the CUBFF decision until a
real checkpoint or Python state export is placed in
`data/cubff_real_ingest/source_snapshots/` and compared against the existing
semantic transducer baseline.

## Next Input Required

Acquire at least one real CuBFF state source:

- a `.dat` checkpoint written by CuBFF `--checkpoint_dir`, or
- a JSON/JSONL Python callback state export containing `soup`, `epoch`, and
  optional `replication_per_prog`.

Then rerun:

```powershell
python -B labs\cubff_transducer\real_snapshot_ingest.py --input-dir data\cubff_real_ingest\source_snapshots --output-dir data\cubff_real_ingest --source-commit f212e849027c98fcf4b242eccfb5fed435223e23 --language bff_noheads --seed 0
```
