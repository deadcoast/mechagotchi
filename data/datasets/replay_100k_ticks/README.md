# replay_100k_ticks

`replay_100k_ticks@2026-07-07` — behaviour/switchboard
evaluation: 100004 per-tick lifecycle logs across
2501 episodes (50
seed creatures x switchboard/idle/random x deterministic rng
rounds). Rows are the episode's own history entries VERBATIM
(tick, action, need balance, recoveries, alive/death, full state
snapshot) — the same entries the R5 replay recorder frames.
Gzipped JSONL (stdlib `gzip`, mtime=0 for byte determinism);
`replay_sample_first_200.jsonl` is an uncompressed sample.

Read: `import gzip, json; rows = [json.loads(l) for l in gzip.open(path, 'rt', encoding='utf-8')]`

Regenerate: `python -B labs/datasets/dataset_program.py`
