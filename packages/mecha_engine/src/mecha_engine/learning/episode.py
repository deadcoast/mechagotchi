"""Feedback-vs-frozen learning episode for mecha_engine.learning.

Contract sources:

- research/package_specs/mecha_engine_learning_interface_spec.md
  ("Proposed public surface", "Hard gates for the port", "Non-goals")
- research/decision_records/0009-create-mecha-engine-learning-target.md

Verbatim semantic port of the episode mechanics shared by the grid_genome
switchboard-feedback research lab and the runtime_integration stress
learning benchmark's ``_policy_episode``: the deliberate stale
idle-favoring reward miscalibration, the tick loop that lets ``decide``
pick the action and the lifecycle transition observe the reward, the
frozen arm's per-tick reset of ``action_rewards`` back to the episode's
initial histories, and the need-balance padding of missing post-death
ticks with ``0.0`` across the full requested horizon. The episode drives
``mecha_engine.lifecycle`` exclusively through its public surface
(``initial_state``, ``advance_tick``); reward-shaping state (the
feedback/frozen switch and the update count) lives here in the episode
loop and never inside lifecycle, per the lifecycle module's contract.

Parity scope — which lab report fields are included and why: the episode
report mirrors the lab shape field-for-field where the semantics are
scenario-free — ``policy``, ``ticks_requested``, ``episode_deterministic``,
``survival_ticks``, ``alive``, ``death_cause``, ``need_balance``,
``recovery_events``, ``action_counts``, ``reward_update_count``,
``initial_action_reward_means``, ``final_action_reward_means``, and the
per-tick ``history`` entries (tick, action, decision_confidence,
observed_reward, need_balance, reward_means_before/after, alive,
death_cause). Excluded lab fields: ``scenario_id`` and ``events_applied``
(the scenario/event machinery stays lab-only per the interface spec's
non-goals) and ``rng_seed`` (the lab records it for interface parity only;
the episode is fully deterministic, no code path consumes a seed, and this
signature deliberately has no seed parameter). The lab-side parity test
(``labs/grid_genome/test_package_learning_parity.py``) pins every included
field equal to the lab episode and to the stress benchmark's
``_policy_episode`` outputs for both arms.

Single-episode learning only: nothing persists at module level or across
episodes, matching the evidence bounds of decision record 0009.
"""

from __future__ import annotations

from copy import deepcopy
from statistics import mean

from mecha_engine.lifecycle import advance_tick, initial_state

from ._switchboard import ACTIONS, decide


def run_feedback_episode(
    grid: dict,
    slip_profile: dict,
    *,
    ticks: int = 48,
    feedback_enabled: bool = True,
    miscalibrate: bool = True,
) -> dict:
    """Run one deterministic feedback (or frozen-comparator) episode.

    ``feedback_enabled=True`` lets the rewards observed from lifecycle
    transitions accumulate in the state's ``action_rewards`` histories, so
    ``decide``'s preference thread learns online within the episode;
    ``feedback_enabled=False`` resets those histories to the episode's
    initial values after every tick — the frozen comparator, identical in
    every other respect. ``miscalibrate=True`` installs the research labs'
    deliberate stale idle-favoring reward memory before the first tick (the
    learnable-gap premise both recorded measurements share);
    ``miscalibrate=False`` starts from the lifecycle initial state's own
    reward histories. Neither input is mutated; the report is
    JSON-serializable and identical across repeated calls.
    """
    state = initial_state(grid, slip_profile)
    if miscalibrate:
        state = _miscalibrate_rewards(state)
    initial_rewards = deepcopy(state["action_rewards"])
    initial_means = _reward_means(initial_rewards)
    history: list[dict] = []
    reward_update_count = 0

    for _ in range(ticks):
        if not state["alive"]:
            break
        decision = decide(state)
        action = decision["action"]
        before_means = _reward_means(state["action_rewards"])
        next_state = advance_tick(state, action)
        observed_reward = next_state["action_rewards"][action][-1]

        if feedback_enabled:
            reward_update_count += 1
            after_means = _reward_means(next_state["action_rewards"])
        else:
            next_state["action_rewards"] = deepcopy(initial_rewards)
            after_means = _reward_means(next_state["action_rewards"])

        history.append(
            {
                "tick": next_state["age_ticks"],
                "action": action,
                "decision_confidence": decision["confidence"],
                "observed_reward": observed_reward,
                "need_balance": next_state["history"][-1]["balance"],
                "reward_means_before": before_means,
                "reward_means_after": after_means,
                "alive": next_state["alive"],
                "death_cause": next_state["death_cause"],
            }
        )
        state = next_state

    balances = [entry["need_balance"] for entry in history]
    if balances and len(balances) < ticks:
        balances = balances + [0.0] * (ticks - len(balances))

    return {
        "policy": "feedback_switchboard" if feedback_enabled else "frozen_switchboard",
        "ticks_requested": ticks,
        "episode_deterministic": True,
        "survival_ticks": state["age_ticks"],
        "alive": state["alive"],
        "death_cause": state["death_cause"],
        "need_balance": round(mean(balances), 6) if balances else 0.0,
        "recovery_events": state["recovery_events"],
        "action_counts": state["action_counts"],
        "reward_update_count": reward_update_count,
        "initial_action_reward_means": initial_means,
        "final_action_reward_means": _reward_means(state["action_rewards"]),
        "history": history,
    }


def _miscalibrate_rewards(state: dict) -> dict:
    """Install the labs' stale, behaviorally harmful action-reward memory.

    Verbatim port of the switchboard-feedback research lab's helper: the
    memory claims idling is the most rewarding action (as if calibrated
    during an earlier quiet phase) while the other actions carry flat,
    uninformative reward means. In the curious-mood band only the bandit
    thread separates idle from active care, so a frozen switchboard acting
    on this memory locks into idle, while the feedback switchboard corrects
    the idle mean from observed lifecycle rewards and re-engages. Both
    recorded measurements (sheltered and stress) start from exactly this
    memory — changing it would break the learnable-gap premise they share.
    """
    updated = deepcopy(state)
    updated["hunger"] = 0.35
    updated["energy"] = 0.45
    updated["stress"] = 0.12
    updated["bond"] = 0.6
    updated["grid_stability"] = 0.85
    updated["recent_interactions"] = [1, 0, 0, 1, 0]
    updated["action_rewards"] = {
        "feed": [0.5],
        "play": [0.5],
        "sleep": [0.5],
        "idle": [0.95, 0.94, 0.96],
        "mutate": [0.5],
    }
    return updated


def _reward_means(rewards: dict) -> dict[str, float]:
    means: dict[str, float] = {}
    for action in ACTIONS:
        samples = list(rewards.get(action, []))
        means[action] = round(mean(samples), 6) if samples else 0.0
    return means
