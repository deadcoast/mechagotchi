# Experiment Report: Mecha Engine Lifecycle Contract Gate

Date: 2026-05-12

## Objective

Define the acceptance contract for the future `mecha_engine.lifecycle` package
module before moving lifecycle code out of `labs/lifecycle_sim`.

## Method

1. Re-read the research plan's lifecycle, companion behavior, and evaluation
   sections.
2. Re-read the `mecha_engine` module interface spec.
3. Re-read the lifecycle simulator baseline, switchboard lifecycle feedback,
   and dynamic feedback stress reports.
4. Re-read the lifecycle simulator source and tests.
5. Checked current public references for artificial-life survival simulation,
   care-loop categories, and reward-from-interaction framing.
6. Wrote a prose gate and a machine-readable architecture artifact.

## Outputs

- `research/package_specs/mecha_engine_lifecycle_contract_gate.md`
- `data/architecture/mecha_engine_lifecycle_contract_gate_stage0.json`

## Findings

The lifecycle package boundary must preserve the mathematical shape of the lab
simulator without promoting the lab-only learner:

```txt
x(t + 1) = clamp(T(x(t), action(t), profile, grid))
```

The state vector is bounded over hunger, energy, stress, bond, and
grid-stability variables, while terminal behavior is represented by `alive`,
`age_ticks`, and explicit `death_cause`.

The Stage 0 comparator remains the acceptance evidence:

| Policy | Survival ticks | Alive | Need balance | Recovery events | Death cause |
| --- | ---: | --- | ---: | ---: | --- |
| switchboard | 72 | true | 0.789129 | 14 | none |
| idle | 11 | false | 0.121004 | 0 | starvation |
| random | 21 | false | 0.236001 | 2 | starvation |

The reward-feedback evidence does not justify promotion. Feedback updates are
mechanically active, but the dynamic stress suite produced mean need-balance
delta `-0.002226` and no survival improvement. That keeps online reward
shaping outside the lifecycle package gate.

Supersession note: SLIP runtime selection now consumes switchboard lifecycle
metrics for profile-specific archive elite selection in
`research/experiment_reports/2026-05-13-slip-runtime-selection-policy.md`.
SLIP offspring lifecycle checks are now covered by
`research/experiment_reports/2026-05-13-slip-offspring-lineage-gate.md`.
This still does not promote package runtime evolution or persistent
multigeneration lineage.

The required public surface is:

```python
from mecha_engine.lifecycle import (
    advance_tick,
    initial_state,
    reward_for_transition,
    run_episode,
)
```

## Decision

Adopt the lifecycle contract gate as the package acceptance checklist for the
future `mecha_engine.lifecycle` module. Do not create `packages/mecha_engine`
in this research step.

Status: `research_lifecycle_contract_gate_no_package_code`

## Verification Targets

These checks are valid after package implementation begins:

```powershell
python -B -m unittest discover -s .\packages\mecha_engine\tests -p "test_*.py"
python -c "from mecha_engine.lifecycle import initial_state, advance_tick, run_episode, reward_for_transition"
rg -n "from labs|import labs|labs/|labs\\|sys\\.path" .\packages\mecha_engine
python -B .\labs\package_promotion\package_promotion_gate.py --root . --output-dir .\data\package_promotion
```

This research step only verifies the new gate artifacts and existing lifecycle
lab evidence.

## Sources

- `research/package_specs/mecha_engine_module_interfaces.md`
- `research/algorithm_cards/lifecycle_simulator.md`
- `research/experiment_reports/2026-05-12-lifecycle-simulator-baseline.md`
- `research/experiment_reports/2026-05-12-switchboard-lifecycle-feedback.md`
- `research/experiment_reports/2026-05-12-switchboard-feedback-dynamic-stress.md`
- `research/experiment_reports/2026-05-13-slip-runtime-selection-policy.md`
- `data/lifecycle/lifecycle_stage0.json`
- `data/package_promotion/mecha_engine_package_promotion_gate_stage0.json`
- Tamagotchi Connection manual index:
  https://tamagotchi-official.com/manual/toy/connection/
- JaxLife artificial-life simulator paper:
  https://arxiv.org/abs/2409.00853
- Sutton and Barto, Reinforcement Learning: An Introduction:
  https://mitpress.mit.edu/9780262039246/reinforcement-learning/
- Contextual-bandit paper used by switchboard feedback research:
  https://arxiv.org/abs/1003.0146
