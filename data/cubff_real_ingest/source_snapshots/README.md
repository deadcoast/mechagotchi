# Real CuBFF Snapshot Drop Zone

Place real CuBFF checkpoint or Python callback state exports here before
running `labs/cubff_transducer/real_snapshot_ingest.py`.

Accepted inputs:

- `.dat` checkpoint files written by CuBFF `--checkpoint_dir`.
- `.json` or `.jsonl` Python callback state exports containing `soup`,
  `epoch`, and optional `replication_per_prog` fields.

Do not place synthetic CUBFF-style fixtures here. Metrics logs are useful
provenance, but they are not snapshots and will not be treated as transducer
inputs.

## The committed corpus (cycle 17 G2, 2026-07-12)

REAL checkpoints from one genuine upstream run — nothing synthetic,
nothing fabricated:

- Source: `paradigms-of-intelligence/cubff` at the AUDITED commit
  `f212e849027c98fcf4b242eccfb5fed435223e23` (the same commit the
  ingest record's upstream audit examined), built from source with
  `make CUDA=0` (g++ 13.3.0, OpenMP CPU path, libbrotli) on WSL2
  Ubuntu 24.04.
- Run: `bin/main --lang bff_noheads --seed 0 --num 8192
  --max_epochs 16384 --save_interval 2048 --checkpoint_dir …
  --log …/metrics.csv --disable_output` — nine `.dat` checkpoints
  (epochs 0 … 16384, each 524,312 bytes = 24-byte header +
  8192 × 64 soup bytes, the documented writer format verbatim).
- `metrics.csv` is the run's own epoch/brotli_size/soup_size log —
  committed as PROVENANCE (the ingest gate correctly ignores it as a
  non-snapshot).
- Honest observation: over this window the soup stays EARLY-PHASE
  (brotli_size ≈ 482k of 524k raw at epoch 16384 — no compression
  collapse/takeover yet at this soup size). Longer/larger runs for
  emergent states are the transducer study's protocol territory (G3),
  never retrofitted here.
- Replication scores are not stored in checkpoints (the documented
  writer limitation); `mean_replication_score_count = 0` in the
  ingest report is the format's truth, not an omission.
