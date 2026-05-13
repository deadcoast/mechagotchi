# Experiment Report: SLIP Runtime Selection Policy

Date: 2026-05-13

Status: `research_slip_runtime_selection_policy_no_package_code`

## Question

Can Mechagotchi specify a runtime lifecycle/archive selection policy that uses
current `SLIP` weights, switchboard lifecycle measurements, and extended
MAP-Elites elites without claiming full profile-weighted evolution?

## Plan Alignment

This continues the research plan's lifecycle, micro-learning, `SLIP`, and
`mecha_darwin` archive tracks. The previous lifecycle/archive bridge measured
profile effects but did not choose an archive elite. This experiment adds a
Stage 0 selector. No `packages/` code was created.

## External Source Refresh

Sources used:

- MAP-Elites paper: https://arxiv.org/abs/1504.04909
- Sutton and Barto, Reinforcement Learning: https://mitpress.mit.edu/9780262039246/reinforcement-learning/
- Contextual bandit paper: https://arxiv.org/abs/1003.0146
- JaxLife paper: https://arxiv.org/abs/2409.00853

MAP-Elites supports preserving diverse high-performing elites across selected
descriptor dimensions. Reinforcement-learning and contextual-bandit sources are
used only for reward/action-value vocabulary; this lab does not train an RL or
bandit policy. JaxLife keeps survival measurement framed as artificial-life
evaluation context.

## Method

Added `labs/workshop_editor/slip_runtime_selection_policy.py` with:

- `run_profile_runtime_selection_probe`
- `run_slip_runtime_selection_policy_lab`
- `write_slip_runtime_selection_policy_artifacts`

Added `labs/workshop_editor/test_slip_runtime_selection_policy.py` first and
watched it fail on the missing module before implementing the selector.

For each current valid profile, the lab:

1. validates the active profile and generated candidate corpus;
2. builds an extended MAP-Elites archive over the candidate set;
3. runs switchboard lifecycle episodes for archive elites;
4. scores each elite by weighted runtime/archive components:
   survival ratio, need balance, bond, mutation stability, archive niche rarity,
   readability, and `SLIP` alignment;
5. records the selected elite and full component-weight trace.

Invalid probes cover unsupported `SLIP` version and mismatched profile/candidate
corpus. Both must stop before selection starts.

## Results

Machine-readable artifacts:

- `data/workshop_editor/slip_runtime_selection_policy_stage0.json`
- `data/workshop_editor/slip_runtime_selection_policy_stage0/slip_runtime_selection_policy_stage0.json`
- `data/workshop_editor/slip_runtime_selection_policy_stage0/*_runtime_selection_policy.json`
- `data/workshop_editor/slip_runtime_selection_policy_data.js`
- `research/algorithm_cards/slip_runtime_selection_policy.md`

Summary:

| Metric | Result |
| --- | ---: |
| Current valid profiles covered | 3 |
| Selection successes | 3 |
| Selected archive elites | 3 |
| Invalid probes rejected | 2 |
| Distinct selected grid ids | 3 |
| Distinct selected archive niches | 3 |
| Mean selected selection score | 0.955828 |
| Mean selected need balance | 0.793865 |
| Mean selected survival ratio | 1.0 |

Selected elites:

| Profile | Selected grid | Archive niche | Selection score |
| --- | --- | --- | ---: |
| `slip_lcd_seed` | `slip_lcd_seed_constrained_011` | `1,1,2,4,4,4,1` | 0.955499 |
| `slip_gray_stable` | `slip_gray_stable_constrained_008` | `1,1,1,4,4,4,1` | 0.955179 |
| `slip_amber_social` | `slip_amber_social_constrained_004` | `2,0,2,4,4,4,2` | 0.956805 |

Closed states:

- `runtime_lifecycle_archive_selection_policy`
- `profile_weighted_archive_elite_selection_trace`
- `invalid_profile_rejected_before_runtime_selection`

Blocked states:

- `profile_weighted_evolution`
- `package_runtime_lifecycle_integration`
- `offspring_mutation_selection`
- `lineage_replacement_policy`
- `held_out_long_horizon_behavior_tests`
- `manual_readability_calibration`

## Interpretation

The broad runtime lifecycle/archive selection gap is now specified and tested at
Stage 0. The selector links `SLIP` weights, switchboard lifecycle metrics, and
extended archive elites through an auditable policy trace.

This is not profile-weighted evolution. The selected elite is an existing
candidate, not a generated child. No mutation, lineage replacement, package
runtime integration, or long-horizon held-out calibration is performed.

## Verification

RED command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_slip_runtime_selection_policy.py
```

Initial result:

```txt
ModuleNotFoundError: No module named 'slip_runtime_selection_policy'
```

GREEN command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_slip_runtime_selection_policy.py
```

Result:

```txt
Ran 4 tests in 0.202s
OK
```

Artifact command:

```powershell
python -B .\labs\workshop_editor\slip_runtime_selection_policy.py
```

## Decision

Adopt `slip_runtime_selection_policy_stage0` as the Stage 0 proof for lab-only
runtime lifecycle/archive elite selection.

Next research should define offspring mutation and lineage replacement gates
before claiming profile-weighted evolution.
