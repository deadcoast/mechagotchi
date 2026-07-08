# Mecha Engine Lifecycle Contract Gate

Date: 2026-05-12

## Status

Research acceptance gate. This document does not create or modify
`packages/mecha_engine`.

## Purpose

Define the package-level contract for the future `mecha_engine.lifecycle`
module before lifecycle code is moved out of `labs/lifecycle_sim`.

## Source Evidence

The Stage 0 lifecycle labs already prove:

- Switchboard policy survives the full 72-tick horizon on the LCD seed profile.
- Switchboard need balance is `0.789129`.
- Idle policy dies after 11 ticks with death cause `starvation`.
- Random policy dies after 21 ticks with death cause `starvation`.
- Switchboard recovers dangerous need states 14 times.
- Lifecycle reward feedback is mechanically wired, but reward shaping does not
  beat the frozen baseline under the current feedback tests.
- Dynamic feedback stress produces a mean need-balance delta of `-0.002226`,
  so online reward shaping must remain lab-only.
- SLIP runtime selection policy now consumes switchboard lifecycle metrics for
  3/3 current profile-specific archive elite choices with mean selected need
  balance `0.793865` and mean selected survival ratio `1.0`.
- SLIP offspring lineage gate now evaluates selected child lifecycle episodes
  with mean selected offspring need balance `0.793865` and survival ratio `1.0`.
- SLIP long-horizon behavior gate now records 3/3 selected offspring surviving
  the 96-tick switchboard horizon, 18/18 held-out switchboard full-survival
  probes, 18/18 idle-neglect deaths, and mean need-balance delta vs idle
  `0.691676`.
- SLIP multigeneration lineage runner records three-generation candidate
  lineages for 3/3 current profiles, but remains lab evidence.

The package lifecycle module may adopt the bounded simulator contract. It must
not promote online reward shaping as production behavior or treat the Stage 0
multigeneration runner as package runtime state.

## State Model

Lifecycle is a discrete-time bounded dynamical system:

```txt
x(t + 1) = clamp(T(x(t), action(t), profile, grid))
```

The first package state vector must include:

- `hunger`
- `energy`
- `stress`
- `bond`
- `grid_stability`
- `age_ticks`
- `alive`
- `death_cause`

All continuous state variables must remain in `[0, 1]` after every transition.
The simulator must preserve per-tick history so averages cannot hide unstable
oscillation or late collapse.

## Required Public Surface

```python
from mecha_engine.lifecycle import (
    advance_tick,
    initial_state,
    reward_for_transition,
    run_episode,
)
```

Required contracts:

- `initial_state(grid: dict, slip_profile: dict | None = None) -> dict`
- `advance_tick(state: dict, action: str) -> dict`
- `run_episode(grid: dict, slip_profile: dict | None = None, policy=None, actions=None, ticks=72, rng_seed=None) -> dict`
- `reward_for_transition(previous_state: dict, next_state: dict, action: str) -> float`

## Initial State Acceptance

`initial_state` must:

- reject invalid grids before simulation;
- reject grids that fail the supplied SLIP profile;
- preserve `grid_id` and `slip_profile_id`;
- initialize every continuous state variable inside `[0, 1]`;
- derive state from real grid stress, damage, and body mass;
- derive behavior priors from SLIP `neediness`, `sleepiness`, `curiosity`, and
  survival weights when supplied;
- avoid mutating the input grid or SLIP profile.

## Transition Acceptance

`advance_tick` must:

- accept only supported lifecycle actions;
- return a new state without mutating the prior state;
- increment `age_ticks` by exactly 1 for live states;
- clamp `hunger`, `energy`, `stress`, `bond`, and `grid_stability` into
  `[0, 1]`;
- update action counts;
- append one per-tick history entry;
- record recovered dangerous needs;
- set explicit terminal death causes for starvation, energy collapse, stress
  collapse, and grid collapse;
- leave already-dead states unchanged.

Required first action set:

- `feed`
- `sleep`
- `play`
- `idle`
- `mutate`

## Episode Acceptance

`run_episode` must:

- support a named policy or an explicit action stream;
- reject simultaneous ambiguous policy and action-stream requests;
- stop applying actions after terminal death;
- report `ticks_requested`, `survival_ticks`, `alive`, `death_cause`,
  `need_balance`, `recovery_events`, `action_counts`, `final_state`, and
  `history`;
- score `need_balance` across the full requested horizon;
- fill missing post-death ticks with `0.0` for the horizon score;
- preserve deterministic results for the same grid, profile, policy/actions,
  tick horizon, and RNG seed.

The package gate must reproduce the Stage 0 comparator result:

| Policy | Survival ticks | Alive | Need balance | Recovery events | Death cause |
| --- | ---: | --- | ---: | ---: | --- |
| switchboard | 72 | true | 0.789129 | 14 | none |
| idle | 11 | false | 0.121004 | 0 | starvation |
| random | 21 | false | 0.236001 | 2 | starvation |

## Reward Acceptance

`reward_for_transition` must:

- return a float in `[0, 1]`;
- reward full-state balance rather than a single action preference;
- include hunger recovery, energy recovery, stress reduction, and bond
  improvement signals;
- avoid writing into learner memory;
- remain deterministic for the same transition.

Online learner memory, contextual bandits, and reward-shaping updates are not
part of `mecha_engine.lifecycle` until a later research gate beats the frozen
baseline under dynamic stress.

## Negative Checks

The lifecycle package gate fails if:

- `packages/mecha_engine/src/mecha_engine/lifecycle` imports `labs`;
- package tests import `labs`;
- package tests mutate `sys.path` to reach `labs`;
- invalid grids can enter simulation;
- any continuous state variable leaves `[0, 1]`;
- death can happen without an explicit death cause;
- early death raises the average need-balance score by shortening the horizon;
- online reward shaping is promoted as package behavior;
- feedback learners are mixed into the lifecycle module instead of remaining a
  separate lab-only learning concern.

## Future Verification Commands

Run these after the scaffold and `lifecycle` implementation exist:

```powershell
python -B .\labs\lifecycle_sim\test_lifecycle_sim.py
python -B .\labs\grid_genome\test_switchboard_feedback.py
python -B -m unittest discover -s .\packages\mecha_engine\tests -p "test_*.py"
python -c "from mecha_engine.lifecycle import initial_state, advance_tick, run_episode, reward_for_transition"
rg -n "from labs|import labs|labs/|labs\\|sys\\.path" .\packages\mecha_engine
python -B .\labs\package_promotion\package_promotion_gate.py --root . --output-dir .\data\package_promotion
git diff --check
```

Expected implementation-stage result:

- Lab lifecycle tests still pass.
- Package lifecycle tests pass through `mecha_engine.lifecycle`.
- Package episodes reproduce the Stage 0 comparator metrics or explain an
  intentional metric revision in a new decision record.
- Invalid grids fail before simulation.
- State variables remain bounded across all tested transitions.
- Online reward shaping remains outside the lifecycle package.
- The package contains no runtime or test imports from `labs`.
- Package-promotion gate is rerun after package lifecycle tests exist.

## Non-Goals

- No package creation in this research step.
- No lifecycle implementation migration.
- No online reward-shaping promotion.
- No persistent learner state.
- No real user-trace model.
- No CA/NCA repair or local cell-stress propagation.
- No frontend care UI.

## Sources

- `research/package_specs/mecha_engine_module_interfaces.md`
- `research/algorithm_cards/lifecycle_simulator.md`
- `research/experiment_reports/2026-05-12-lifecycle-simulator-baseline.md`
- `research/experiment_reports/2026-05-12-switchboard-lifecycle-feedback.md`
- `research/experiment_reports/2026-05-12-switchboard-feedback-dynamic-stress.md`
- `research/experiment_reports/2026-05-13-slip-runtime-selection-policy.md`
- `research/experiment_reports/2026-05-13-slip-offspring-lineage-gate.md`
- `research/experiment_reports/2026-05-13-slip-long-horizon-behavior-gate.md`
- `data/lifecycle/lifecycle_stage0.json`
- `data/workshop_editor/slip_runtime_selection_policy_stage0.json`
- `data/workshop_editor/slip_offspring_lineage_gate_stage0.json`
- `data/workshop_editor/slip_long_horizon_behavior_gate_stage0.json`
- `data/package_promotion/mecha_engine_package_promotion_gate_stage0.json`
- Tamagotchi Connection manual index:
  https://tamagotchi-official.com/manual/toy/connection/
- JaxLife artificial-life simulator paper:
  https://arxiv.org/abs/2409.00853
- Sutton and Barto, Reinforcement Learning: An Introduction:
  https://mitpress.mit.edu/9780262039246/reinforcement-learning/
- Contextual-bandit paper used by switchboard feedback research:
  https://arxiv.org/abs/1003.0146

## Deliberation in history (F1, 2026-07-07 — the seen thought)

`advance_tick` accepts keyword-only `deliberation: dict | None = None`
and `choose_action` gains a companion `choose_action_detailed(policy,
state, rng) -> (action, record | None)`. Under a v0.2 covenant carrying
`deliberation`, ticks that actually reach the switchboard append the R1
record (`tick_count`, `max_ticks`, `confidence_threshold`) to their
history entry as a RUNG-CONDITIONAL key; reflex ticks (the quick-path
guards), the idle/random policies, explicit action streams, and every
no-covenant flow append the frozen entry byte-identically —
`choose_action` itself is unchanged. Verbatim across the lab authority
(`labs/lifecycle_sim/lifecycle_sim.py`) and the package, pinned by
`labs/lifecycle_sim/test_deliberation_history.py` (identical histories
on both sides) and the `deliberation_history` driver probe. This is how
DR 0021's notice 2 ("creatures visibly think") reaches the replay
scrubber: the tick frames carry the record, and the scrubber renders
"thought N ticks".

## Interactive surface (W1, 2026-07-07 - the living companion)

The contracted public surface widens from four names to six:
`choose_action_detailed` (F1's chooser, previously package-internal) and
`ACTIONS` (the action vocabulary) are exported so INTERACTIVE callers -
the living-companion surface first - can drive `advance_tick` one tick
at a time with either the player's choice (the buttons ARE the action
vocabulary) or the frozen switchboard's own choice, deliberation record
included. No behavior changed: both names bind the exact objects the
module already used internally, `run_episode` remains the episode
authority, and the no-learner-memory rule is untouched (the chooser is
stateless). Pinned by the surface probe (exact `__all__` equality).
