# Lifecycle Simulator Stage 0

Deterministic lifecycle simulator output for the post-v0.1 research gate.
The artifact compares switchboard, idle, and random policies on survival ticks,
need balance, recovery events, final state, and per-tick history.

Primary artifact:

- `lifecycle_stage0.json`

Metric note:

- `need_balance` is scored over the full requested horizon.
- Missing ticks after death count as `0.0`.
- This prevents early death from being rewarded by a short high-average run.
