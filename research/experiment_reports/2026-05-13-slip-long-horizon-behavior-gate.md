# Experiment Report: SLIP Long-Horizon Behavior Gate

Date: 2026-05-13

Status: `research_slip_long_horizon_behavior_gate_no_package_code`

## Question

Can Mechagotchi run held-out long-horizon behavior tests for current
SLIP-selected offspring and generated candidates without claiming manual
readability calibration or profile-weighted evolution?

## Plan Alignment

This continues the research plan's lifecycle, artificial-life, quality-diversity
archive, and SLIP tracks. The previous offspring lineage gate produced bounded
children and lineage decisions; this experiment checks longer behavior survival
for those selected children plus held-out generated candidates. No `packages/`
code was created.

## External Source Refresh

Sources used:

- Avida Digital Evolution Platform: https://avida.devosoft.org/
- JaxLife: An Open-Ended Agentic Simulator: https://arxiv.org/abs/2409.00853
- Reinforcement Learning: An Introduction, MIT Press page: https://mitpress.mit.edu/9780262039246/reinforcement-learning/

Avida supports treating digital-evolution behavior work as explicit experiment
protocols over evolving computer artifacts. JaxLife supports measuring survival
and emergent behavior inside artificial-life simulation substrates. The
Sutton/Barto reference supports framing the switchboard-vs-idle contrast as
long-running agent-environment reward evidence rather than a one-step preview.

## Method

Added `labs/workshop_editor/slip_long_horizon_behavior_gate.py` with:

- `run_profile_long_horizon_probe`
- `run_slip_long_horizon_behavior_gate_lab`
- `write_slip_long_horizon_behavior_gate_artifacts`

Added `labs/workshop_editor/test_slip_long_horizon_behavior_gate.py` first and
watched it fail on the missing module before implementing the gate.

For each current valid profile, the lab:

1. reuses the offspring-lineage gate to select one bounded child from the
   runtime-selected parent;
2. reconstructs the selected child grid and validates it against the active
   profile;
3. runs 96-tick lifecycle probes under `switchboard` and `idle`;
4. evaluates held-out generated candidates after the parent-selection window;
5. records whether manual readability ratings exist before any evolution claim;
6. rejects unsupported-version and mismatched-profile probes before the
   long-horizon gate starts.

## Results

Machine-readable artifacts:

- `data/workshop_editor/slip_long_horizon_behavior_gate_stage0.json`
- `data/workshop_editor/slip_long_horizon_behavior_gate_stage0/slip_long_horizon_behavior_gate_stage0.json`
- `data/workshop_editor/slip_long_horizon_behavior_gate_stage0/*_long_horizon_behavior_gate.json`
- `data/workshop_editor/slip_long_horizon_behavior_gate_data.js`
- `research/algorithm_cards/slip_long_horizon_behavior_gate.md`

Summary:

| Metric | Result |
| --- | ---: |
| Current valid profiles covered | 3 |
| Long-horizon successes | 3 |
| Selected offspring full-survival probes | 3 |
| Held-out candidates | 18 |
| Held-out switchboard full-survival probes | 18 |
| Held-out idle deaths | 18 |
| Invalid probes rejected | 2 |
| Mean switchboard survival ratio | 1.0 |
| Mean idle survival ratio | 0.114583 |
| Mean switchboard need balance | 0.782108 |
| Mean idle need balance | 0.090432 |
| Mean need-balance delta vs idle | 0.691676 |
| Manual readability calibration ready | false |

Closed states:

- `held_out_long_horizon_behavior_tests`
- `offspring_long_horizon_survival_probe`
- `invalid_profile_rejected_before_long_horizon`

Blocked states:

- `profile_weighted_evolution`
- `package_runtime_lifecycle_integration`
- `manual_readability_calibration`

## Interpretation

The held-out long-horizon behavior-test gap is now specified and tested at
Stage 0. The active switchboard policy sustains selected offspring and held-out
generated candidates through the 96-tick horizon, while idle neglect fails for
every held-out probe.

This is still not profile-weighted evolution. There is no package runtime
integration and no collected human readability calibration. The follow-on
`slip_multigeneration_lineage_runner_stage0` now covers lab-only persistent
lineage depth. This gate proves behavior survival for the current lab corpus;
it does not prove final user-facing creature quality.

## Verification

RED command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_slip_long_horizon_behavior_gate.py
```

Initial result:

```txt
ModuleNotFoundError: No module named 'slip_long_horizon_behavior_gate'
```

GREEN command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_slip_long_horizon_behavior_gate.py
```

Result:

```txt
Ran 4 tests in 0.635s
OK
```

Artifact command:

```powershell
python -B .\labs\workshop_editor\slip_long_horizon_behavior_gate.py
```

## Decision

Adopt `slip_long_horizon_behavior_gate_stage0` as the Stage 0 proof for
held-out long-horizon behavior testing.

Next research should prepare the current long-horizon corpus for SLIP-specific
manual readability review, then collect reviewer rows and calibrate proxy
readability thresholds before claiming profile-weighted evolution.
