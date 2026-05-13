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
