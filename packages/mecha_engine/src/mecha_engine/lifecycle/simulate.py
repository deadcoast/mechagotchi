"""Bounded lifecycle simulation for mecha_engine.

Contract sources:

- research/package_specs/mecha_engine_lifecycle_contract_gate.md
  ("State Model", "Initial State Acceptance", "Transition Acceptance",
  "Episode Acceptance", "Reward Acceptance", "Negative Checks")
- research/package_specs/mecha_engine_module_interfaces.md ("lifecycle")

Self-contained semantic port of the Stage 0 research lifecycle simulator
(the lifecycle_sim research lab): identical need-decay drift, action
effects, recovery counting, death causes, per-tick history entries, and the
pinned survival_ticks arithmetic, so package episodes reproduce the Stage 0
switchboard/idle/random comparator byte-for-byte. Grids are rejected through
``mecha_engine.genome.validate_grid`` before any state exists; supplied SLIP
profiles are validated and alignment-checked (private ``_slip`` port) before
profile-weighted state creation.

Determinism: only the ``random`` policy consumes RNG, seeded from the
caller-supplied ``rng_seed``; ``rng_seed=None`` uses the pinned Stage 0 seed
``20260512`` so unspecified episodes stay deterministic and reproduce the
comparator artifact (data/lifecycle/lifecycle_stage0.json).

No online learner memory: the only reward traces are the bounded (last 8),
episode-scoped ``action_rewards`` ring buffers carried inside the state that
each transition returns; nothing persists at module level or across
episodes, and reward-shaping updates remain lab-only (the grid_genome
switchboard-feedback research lab) per the contract gate.

Inputs are never mutated: not the grid, not the SLIP profile, and not the
prior state passed to ``advance_tick`` or ``reward_for_transition``.
"""

from __future__ import annotations

import random
from copy import deepcopy
from statistics import mean

from mecha_engine.genome import validate_grid

from ._policy import ACTIONS, SUPPORTED_POLICIES, choose_action
from ._slip import is_grid_aligned, validate_slip

# Stage 0 homeostasis targets and danger thresholds (research values).
TARGETS: dict[str, float] = {
    "hunger": 0.34,
    "energy": 0.68,
    "stress": 0.18,
    "bond": 0.72,
    "grid_stability": 0.92,
}

DANGER_THRESHOLDS: dict[str, float] = {
    "hunger": 0.75,
    "energy": 0.25,
    "stress": 0.65,
    "bond": 0.25,
    "grid_stability": 0.35,
}

ACTION_EFFECTS: dict[str, dict[str, float]] = {
    "feed": {
        "hunger": -0.32,
        "energy": 0.01,
        "stress": -0.03,
        "bond": 0.02,
        "grid_stability": 0.0,
    },
    "sleep": {
        "hunger": 0.025,
        "energy": 0.34,
        "stress": -0.12,
        "bond": -0.003,
        "grid_stability": 0.01,
    },
    "play": {
        "hunger": 0.035,
        "energy": -0.07,
        "stress": -0.045,
        "bond": 0.065,
        "grid_stability": 0.0,
    },
    "idle": {
        "hunger": 0.02,
        "energy": -0.012,
        "stress": 0.018,
        "bond": -0.012,
        "grid_stability": -0.002,
    },
    "mutate": {
        "hunger": 0.02,
        "energy": -0.045,
        "stress": 0.05,
        "bond": 0.015,
        "grid_stability": -0.055,
    },
}

DEFAULT_TICKS = 72
DEFAULT_POLICY = "switchboard"
# Pinned Stage 0 comparator seed; rng_seed=None resolves here so episodes
# without an explicit seed stay deterministic (episode acceptance).
DEFAULT_RNG_SEED = 20260512


def initial_state(grid: dict, slip_profile: dict | None = None) -> dict:
    """Build a bounded lifecycle state from a valid grid and optional SLIP.

    Invalid grids fail through ``mecha_engine.genome.validate_grid`` before
    any simulation state exists; a supplied SLIP profile is validated and
    the grid must be aligned with it before profile-weighted state creation.
    Neither input is mutated.

    SLIP v0.2 profiles (decision record 0013) additionally stash
    ``risk_tolerance_mutation`` and ``learning_switches`` into the state,
    exactly as the lab lifecycle simulator does; v0.1 states stay
    byte-identical to the frozen baseline.
    """
    validation = validate_grid(grid) if isinstance(grid, dict) else None
    if validation is None or not validation.ok:
        errors = validation.errors if validation is not None else ["not an object"]
        raise ValueError(
            "invalid grid for lifecycle simulation: " + "; ".join(errors)
        )
    if slip_profile is not None:
        profile_result = validate_slip(slip_profile)
        if not profile_result.ok:
            raise ValueError(
                "SLIP profile is invalid: " + "; ".join(profile_result.errors)
            )
        alignment = is_grid_aligned(grid, slip_profile)
        if not alignment.ok:
            raise ValueError(
                "grid is not aligned with SLIP: " + "; ".join(alignment.errors)
            )

    cells = grid.get("cells", [])
    cell_stress = mean([float(cell.get("stress", 0)) for cell in cells]) if cells else 0.0
    cell_damage = mean([float(cell.get("damage", 0)) for cell in cells]) if cells else 0.0
    body_mass = sum(1 for cell in cells if cell.get("organ") == "core")

    risk_tolerances = (slip_profile or {}).get("risk_tolerances")
    learning_switches = (slip_profile or {}).get("learning_switches")
    behavior = (slip_profile or {}).get("behavior", {})
    survival_weights = (slip_profile or {}).get("survival_weights", {})
    neediness = _clamp(behavior.get("neediness", 0.45))
    sleepiness = _clamp(behavior.get("sleepiness", 0.5))
    curiosity = _clamp(behavior.get("curiosity", 0.5))
    stability_weight = _clamp(survival_weights.get("stability", 0.5))
    bond_weight = _clamp(survival_weights.get("bond", 0.25))

    state = {
        "grid_id": grid.get("grid_id", "unknown_grid"),
        "slip_profile_id": (slip_profile or {}).get("profile_id"),
        "alive": True,
        "age_ticks": 0,
        "hunger": round(_clamp(0.32 + neediness * 0.12), 6),
        "energy": round(_clamp(0.74 - sleepiness * 0.12), 6),
        "stress": round(_clamp(0.18 + cell_stress * 0.5), 6),
        "bond": round(_clamp(0.48 + bond_weight * 0.35 + curiosity * 0.08), 6),
        "grid_stability": round(
            _clamp(0.93 + stability_weight * 0.06 - cell_stress * 0.4 - cell_damage * 0.5),
            6,
        ),
        "body_mass": body_mass,
        "neediness": neediness,
        "sleepiness": sleepiness,
        "curiosity": curiosity,
        "recent_interactions": [1, 0, 1],
        "action_rewards": {
            "feed": [0.56 + neediness * 0.16],
            "play": [0.5 + curiosity * 0.24],
            "sleep": [0.52 + sleepiness * 0.2],
            "idle": [0.42],
            "mutate": [0.35],
        },
        "action_counts": {action: 0 for action in ACTIONS},
        "recovery_events": 0,
        "death_cause": None,
        "history": [],
    }
    # SLIP ladder rung T3.2 (decision records 0012/0013): v0.2 profiles
    # carry a mutation risk tolerance the switchboard consumes; absent
    # (every v0.1 profile) the state is byte-identical to the frozen
    # baseline. Identical stashing to the lab lifecycle simulator.
    if isinstance(risk_tolerances, dict) and "mutation" in risk_tolerances:
        state["risk_tolerance_mutation"] = _clamp(
            float(risk_tolerances["mutation"])
        )
    # Rung T3.3: profile-authored thread gates for the switchboard.
    if isinstance(learning_switches, dict) and learning_switches:
        state["learning_switches"] = dict(learning_switches)
    return state


def advance_tick(state: dict, action: str) -> dict:
    """Apply one supported action to a live state and return a new state.

    The prior state is never mutated. Live states age by exactly one tick,
    stay clamped inside ``[0, 1]`` on every continuous variable, gain one
    per-tick history entry (with recovered dangerous needs), and receive an
    explicit death cause when a terminal threshold is crossed. Already-dead
    states are returned unchanged.
    """
    if action not in ACTION_EFFECTS:
        raise ValueError(f"unsupported lifecycle action: {action}")
    next_state = deepcopy(state)
    if not next_state.get("alive", False):
        return next_state

    previous = _snapshot(next_state)
    neediness = _clamp(next_state.get("neediness", 0.45))
    sleepiness = _clamp(next_state.get("sleepiness", 0.5))
    curiosity = _clamp(next_state.get("curiosity", 0.5))

    drift = {
        "hunger": 0.032 + neediness * 0.018,
        "energy": -(0.022 + sleepiness * 0.012),
        "stress": 0.009 + next_state["hunger"] * 0.01,
        "bond": -0.004,
        "grid_stability": -0.001,
    }
    effects = ACTION_EFFECTS[action]
    for key in TARGETS:
        next_state[key] = round(
            _clamp(float(next_state[key]) + drift[key] + effects[key]),
            6,
        )

    if action == "play":
        next_state["bond"] = round(_clamp(next_state["bond"] + curiosity * 0.015), 6)
    elif action == "feed":
        next_state["stress"] = round(_clamp(next_state["stress"] - neediness * 0.01), 6)
    elif action == "sleep":
        next_state["stress"] = round(_clamp(next_state["stress"] - sleepiness * 0.015), 6)

    next_state["age_ticks"] = int(next_state.get("age_ticks", 0)) + 1
    next_state["action_counts"][action] = next_state["action_counts"].get(action, 0) + 1

    interaction = 1 if action in {"feed", "play"} else 0
    next_state["recent_interactions"] = (
        list(next_state.get("recent_interactions", [])) + [interaction]
    )[-5:]

    balance = _need_balance(_snapshot(next_state))
    reward = _reward_for_action(previous, _snapshot(next_state), balance)
    rewards = next_state.setdefault("action_rewards", {})
    rewards[action] = (list(rewards.get(action, [])) + [reward])[-8:]

    recoveries = _recovered_needs(previous, _snapshot(next_state))
    next_state["recovery_events"] = int(next_state.get("recovery_events", 0)) + len(
        recoveries
    )
    next_state["alive"], next_state["death_cause"] = _life_status(next_state)
    next_state["history"].append(
        {
            "tick": next_state["age_ticks"],
            "action": action,
            "balance": balance,
            "recoveries": recoveries,
            "alive": next_state["alive"],
            "death_cause": next_state["death_cause"],
            "state": _snapshot(next_state),
        }
    )
    return next_state


def run_episode(
    grid: dict,
    slip_profile: dict | None = None,
    policy: str | None = None,
    actions: list[str] | None = None,
    ticks: int = DEFAULT_TICKS,
    rng_seed: int | None = None,
) -> dict:
    """Run a deterministic bounded episode from a valid grid.

    Exactly one action source drives the episode: a named policy
    (``switchboard``, ``idle``, or ``random``) or an explicit action
    stream; supplying both is rejected as ambiguous, and supplying neither
    uses the Stage 0 default policy ``switchboard``. An explicit action
    stream must cover the requested tick horizon (death may consume fewer
    actions). ``rng_seed=None`` resolves to the pinned Stage 0 seed
    ``20260512`` so unspecified episodes stay deterministic.

    ``need_balance`` is scored across the full requested horizon with
    missing post-death ticks counted as ``0.0``, so early death can never
    inflate the score by shortening the horizon.
    """
    if policy is not None and actions is not None:
        raise ValueError(
            "ambiguous episode request: supply either a named policy or an "
            "explicit action stream, not both"
        )
    if isinstance(ticks, bool) or not isinstance(ticks, int) or ticks < 0:
        raise ValueError(f"ticks must be a non-negative integer: {ticks}")

    action_stream: list[str] | None = None
    if actions is not None:
        action_stream = list(actions)
        for action in action_stream:
            if action not in ACTION_EFFECTS:
                raise ValueError(f"unsupported lifecycle action: {action}")
        if len(action_stream) < ticks:
            raise ValueError(
                "action stream must cover the requested tick horizon: "
                f"{len(action_stream)} actions for {ticks} ticks"
            )
        effective_policy = None
    else:
        effective_policy = DEFAULT_POLICY if policy is None else policy
        if effective_policy not in SUPPORTED_POLICIES:
            raise ValueError(f"unsupported lifecycle policy: {effective_policy}")

    rng = random.Random(DEFAULT_RNG_SEED if rng_seed is None else rng_seed)
    state = initial_state(grid, slip_profile)
    for index in range(ticks):
        if not state["alive"]:
            break
        if action_stream is not None:
            action = action_stream[index]
        else:
            action = choose_action(effective_policy, state, rng)
        state = advance_tick(state, action)

    balances = [entry["balance"] for entry in state["history"]]
    if balances and len(balances) < ticks:
        balances = balances + [0.0] * (ticks - len(balances))
    need_balance = round(mean(balances), 6) if balances else _need_balance(_snapshot(state))
    return {
        "policy": effective_policy,
        "ticks_requested": ticks,
        # survival_ticks counts ticks entered, including the tick on which
        # death occurs: advance_tick increments age_ticks and sets alive=False
        # in the same call, so a pet that dies on tick N reports
        # survival_ticks == N (not N - 1). Downstream artifacts and metrics
        # depend on this arithmetic; do not change it.
        "survival_ticks": state["age_ticks"],
        "alive": state["alive"],
        "death_cause": state["death_cause"],
        "need_balance": need_balance,
        "recovery_events": state["recovery_events"],
        "action_counts": state["action_counts"],
        "final_state": _snapshot(state),
        "history": state["history"],
    }


def reward_for_transition(previous_state: dict, next_state: dict, action: str) -> float:
    """Return the deterministic bounded reward for one state transition.

    The reward is the full-state need balance of ``next_state`` plus the
    Stage 0 recovery bonuses (hunger recovery, energy recovery, stress
    reduction, bond improvement), clamped into ``[0, 1]``. It is a pure
    function of its arguments: no learner memory is read or written, and
    neither state is mutated. The value equals the per-action reward the
    simulator records inside episode state for the same transition.
    """
    if action not in ACTION_EFFECTS:
        raise ValueError(f"unsupported lifecycle action: {action}")
    previous = _checked_snapshot(previous_state, "previous_state")
    current = _checked_snapshot(next_state, "next_state")
    return _reward_for_action(previous, current, _need_balance(current))


def _need_balance(state: dict) -> float:
    distances = []
    for key, target in TARGETS.items():
        distances.append(abs(float(state[key]) - target))
    return round(_clamp(1 - mean(distances)), 6)


def _reward_for_action(previous: dict, current: dict, balance: float) -> float:
    reward = balance
    if current["hunger"] < previous["hunger"]:
        reward += 0.03
    if current["energy"] > previous["energy"]:
        reward += 0.03
    if current["stress"] < previous["stress"]:
        reward += 0.03
    if current["bond"] > previous["bond"]:
        reward += 0.02
    return round(_clamp(reward), 6)


def _recovered_needs(previous: dict, current: dict) -> list[str]:
    recovered = []
    if previous["hunger"] >= DANGER_THRESHOLDS["hunger"] and current["hunger"] < previous["hunger"]:
        recovered.append("hunger")
    if previous["energy"] <= DANGER_THRESHOLDS["energy"] and current["energy"] > previous["energy"]:
        recovered.append("energy")
    if previous["stress"] >= DANGER_THRESHOLDS["stress"] and current["stress"] < previous["stress"]:
        recovered.append("stress")
    if previous["bond"] <= DANGER_THRESHOLDS["bond"] and current["bond"] > previous["bond"]:
        recovered.append("bond")
    if (
        previous["grid_stability"] <= DANGER_THRESHOLDS["grid_stability"]
        and current["grid_stability"] > previous["grid_stability"]
    ):
        recovered.append("grid_stability")
    return recovered


def _life_status(state: dict) -> tuple[bool, str | None]:
    if state["hunger"] >= 0.995:
        return False, "starvation"
    if state["energy"] <= 0.02:
        return False, "energy_collapse"
    if state["stress"] >= 0.995:
        return False, "stress_collapse"
    if state["grid_stability"] <= 0.05:
        return False, "grid_collapse"
    return True, None


def _snapshot(state: dict) -> dict:
    return {
        "hunger": round(float(state["hunger"]), 6),
        "energy": round(float(state["energy"]), 6),
        "stress": round(float(state["stress"]), 6),
        "bond": round(float(state["bond"]), 6),
        "grid_stability": round(float(state["grid_stability"]), 6),
    }


def _checked_snapshot(state: dict, name: str) -> dict:
    if not isinstance(state, dict):
        raise ValueError(f"{name} must be a lifecycle state object")
    missing = sorted(key for key in TARGETS if key not in state)
    if missing:
        raise ValueError(
            f"{name} is missing lifecycle state variables: " + ", ".join(missing)
        )
    return _snapshot(state)


def _clamp(value: object) -> float:
    try:
        number = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        number = 0.0
    return max(0.0, min(1.0, number))
