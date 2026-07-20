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

## Layout (cycle 19 I1): one directory per real run

Each run directory holds the run's own `.dat` checkpoints, its
`metrics.csv` (the upstream binary's own epoch/brotli log, committed as
provenance and used by the ingest to label phases), and a `run.json`
manifest recording the exact parameters that reproduce the raw fleet.
The ingest joins each checkpoint's HEADER epoch (filename+1) to the
metrics row for that epoch and labels the state `early_phase` or
`post_takeover` by the measured compression ratio (threshold 0.5 — the
pre-registered midpoint between the two observed modes); states without
a measured row stay `unmeasured`. Nothing is recomputed or fabricated.

### `run_seed0_num8192/` — the cycle 17 G2 run (early-phase)

REAL checkpoints from one genuine upstream run — nothing synthetic,
nothing fabricated:

- Source: `paradigms-of-intelligence/cubff` at the AUDITED commit
  `f212e849027c98fcf4b242eccfb5fed435223e23` (the same commit the
  ingest record's upstream audit examined), built from source with
  `make CUDA=0` (g++ 13.3.0, OpenMP CPU path, libbrotli) on WSL2
  Ubuntu 24.04.
- Run: see `run.json` — nine `.dat` checkpoints (epochs 0 … 16384 by
  filename, each 524,312 bytes = 24-byte header + 8192 × 64 soup
  bytes, the documented writer format verbatim).
- Honest observation: over this window the soup stays EARLY-PHASE
  (brotli_size ≈ 482k of 524k raw at epoch 16384). A 262144-epoch
  probe of the same parameters (2026-07-19) also never crossed the
  takeover ratio — at this soup size takeover was never observed.
- Replication scores are not stored in checkpoints (the documented
  writer limitation); `mean_replication_score_count = 0` in the
  ingest report is the format's truth, not an omission.

### `run_seed0_num131072/` — the cycle 19 I1 run (through takeover)

The paper-scale soup (131,072 programs — the upstream default) run
past takeover to late epochs: the run's own metrics record the brotli
compression collapse crossing ratio 0.5 between epochs 2753 and 2817.
Curated checkpoints span both phases (each 8,388,632 bytes): epoch 1
(ratio 1.000), 2049 (0.943 — the last early save), 4097 (0.175 — the
first post-takeover save), 32769 (0.195 — the late state). The full
fleet reproduces from the recorded parameters in `run.json`;
uncommitted intermediate checkpoints are named there — curation is a
size decision, never a truth decision.

### `run_seed0_num8192_long/` — the cycle 19 I1 negative control

The G2 parameters driven 16× further (262,144 epochs): the takeover
ratio is NEVER crossed — minimum 0.675 at epoch 250,369, final 0.939
— all 4,096 metrics rows committed. The committed final checkpoint is
the deliberate contrast state: LATE-EPOCH yet EARLY-PHASE, because
soup age and soup phase are different axes.
