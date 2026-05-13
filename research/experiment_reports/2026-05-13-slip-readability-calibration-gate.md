# Experiment Report: SLIP Readability Calibration Gate

Date: 2026-05-13

Status: `slip_readability_packet_ready_human_ratings_required`

## Question

Can Mechagotchi bind the current SLIP long-horizon corpus to the manual
readability protocol and produce a reviewer packet without fabricating human
ratings or claiming profile-weighted evolution?

## Plan Alignment

This continues the research plan's readability, SLIP, lifecycle, and
quality-gate tracks. The previous long-horizon behavior gate closed the
behavior-survival proof for selected offspring and held-out candidates. This
experiment moves to the next blocker: human readability calibration. No
`packages/` code was created.

## External Source Refresh

Sources used:

- Comparing PCG metrics with Human Evaluation in Minecraft Settlement
  Generation: https://arxiv.org/abs/2107.02457
- A comprehensive guide to study the agreement and reliability of
  multi-observer ordinal data:
  https://link.springer.com/article/10.1186/s12874-024-02431-y

The PCG paper supports treating proxy metrics as hypotheses that must be
compared against human evaluations. The ordinal-data guide supports recording
agreement/reliability separately from proxy-human correlation when multiple
reviewers score ordinal samples.

## Method

Added `labs/readability_benchmark/slip_readability_calibration_gate.py` with:

- `build_slip_long_horizon_readability_benchmark`
- `run_slip_readability_calibration_gate_lab`
- `write_slip_readability_calibration_gate_artifacts`

Added `labs/readability_benchmark/test_slip_readability_calibration_gate.py`
first and watched it fail on the missing module before implementing the gate.

The lab:

1. loads `data/workshop_editor/slip_long_horizon_behavior_gate_stage0.json`;
2. reconstructs the 3 selected offspring used by the long-horizon gate;
3. loads the 18 held-out long-horizon candidate grids;
4. scores all 21 samples with the existing proxy readability metric;
5. emits a 21-row reviewer template;
6. requires 3 reviewers, for 63 completed reviewer rows;
7. keeps calibration blocked unless rows are complete, error-free, reliable,
   and positively rank-correlated with the proxy scores.

## Results

Machine-readable artifacts:

- `data/readability/slip_readability_calibration_gate_stage0.json`
- `data/readability/slip_readability_calibration_template.csv`
- `data/readability/slip_readability_calibration_reviewer_packet.md`
- `data/readability/slip_readability_calibration_README.md`
- `research/algorithm_cards/slip_readability_calibration_gate.md`

Summary:

| Metric | Result |
| --- | ---: |
| Samples | 21 |
| Selected offspring samples | 3 |
| Held-out long-horizon samples | 18 |
| Expected completed rating rows | 63 |
| Rating rows collected | 0 |
| Reviewers collected | 0 |
| Mean proxy readability score | 0.835645 |
| Proxy-human Spearman | null |
| Inter-reviewer mean absolute delta | null |
| Manual readability calibration ready | false |

Closed states:

- `slip_long_horizon_readability_packet`
- `manual_rating_template_for_slip_long_horizon_corpus`
- `proxy_readability_snapshot_for_slip_long_horizon_corpus`

Blocked states:

- `manual_readability_calibration`
- `proxy_human_readability_correlation_check`
- `inter_reviewer_reliability_check`
- `profile_weighted_evolution`
- `package_runtime_lifecycle_integration`

## Interpretation

This closes the packet/preparation step for manual readability review on the
current long-horizon SLIP corpus. It does not close manual readability
calibration because no filled reviewer CSV exists.

The proxy score snapshot is useful only as pre-calibration evidence. It must
not be used as final creature-quality evidence until human rows are collected
and the gate reruns with complete reviewer coverage.

## Verification

RED command:

```powershell
python -B -m unittest .\labs\readability_benchmark\test_slip_readability_calibration_gate.py
```

Initial result:

```txt
ModuleNotFoundError: No module named 'slip_readability_calibration_gate'
```

GREEN command:

```powershell
python -B -m unittest .\labs\readability_benchmark\test_slip_readability_calibration_gate.py
```

Result:

```txt
Ran 5 tests in 0.057s
OK
```

Artifact command:

```powershell
python -B .\labs\readability_benchmark\slip_readability_calibration_gate.py
```

Result:

```txt
sample_count: 21
expected_completed_rating_rows: 63
rating_row_count: 0
manual_readability_calibration_ready: false
```

## Decision

Adopt `slip_readability_calibration_gate_stage0` as the Stage 0 packet and
proxy-snapshot gate for the current SLIP long-horizon corpus.

Next research should collect 63 reviewer rows in
`data/readability/slip_readability_calibration_ratings.csv` and rerun this gate
before changing proxy readability thresholds or claiming profile-weighted
evolution.
