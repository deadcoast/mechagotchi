"""Frozen episode action policies for mecha_engine.lifecycle.

Contract sources:

- research/package_specs/mecha_engine_lifecycle_contract_gate.md
  ("Episode Acceptance": support a named policy or an explicit action
  stream; reproduce the Stage 0 switchboard/idle/random comparator)
- research/package_specs/mecha_engine_module_interfaces.md ("lifecycle":
  inputs include "Policy or explicit action stream")

Scope note (documented factoring): the interface spec keeps learning
lab-only ("online reward shaping remains lab-only until it beats the frozen
baseline") and the scaffold verification gate defers a ``learning`` module,
so lifecycle carries only the *frozen* switchboard decision function needed
to reproduce the pinned Stage 0 comparator: a semantic port of the research
micro-switchboard (the grid_genome research lab, identical thread math and
tie-break ordering) plus the Stage 0 pre-policy safety overrides.
Nothing here learns: every function is a pure read of the caller's episode
state; the only reward observations the switchboard consults are the
bounded, episode-scoped ``action_rewards`` ring buffers that the simulator
itself maintains inside the state it returns. There is no module-level
learner memory, no persistence across episodes, and no reward-shaping
update path (that remains the grid_genome switchboard-feedback research
lab).

Parity note (decision record 0013): the switchboard here stays in sync
with the lab micro-switchboard's current semantics — the thread registry
with profile-authored ``learning_switches`` gating (absent key or True =
on) and the ``risk_tolerance_mutation`` flip point in the mutation-risk
thread (absent key = the historical 0.35 constant). No v0.1 flow ever
sets either state key, so the frozen baseline runs all four threads
bit-for-bit; ``initial_state`` stashes both keys only for v0.2 SLIP
profiles, exactly as the lab lifecycle does. The lab-side parity pin is
``labs/lifecycle_sim/test_package_lifecycle_v2_parity.py``.
"""

from __future__ import annotations

import random
from collections.abc import Callable

# Stage 0 first action set. Order is load-bearing: the switchboard utility
# table and the bandit-thread means iterate in this order, so deterministic
# max() tie-breaks depend on it (identical to the research lab constant).
ACTIONS: list[str] = ["feed", "play", "sleep", "idle", "mutate"]

SUPPORTED_POLICIES: tuple[str, ...] = ("switchboard", "idle", "random")


def choose_action(policy: str, state: dict, rng: random.Random) -> str:
    """Choose the next action for a named policy (Stage 0 semantics)."""
    return choose_action_detailed(policy, state, rng)[0]


def choose_action_detailed(
    policy: str, state: dict, rng: random.Random,
    *, decision_function: Callable[[dict], dict] | None = None,
) -> tuple[str, dict | None]:
    """(action, deliberation record | None) — F1, the seen thought.

    Verbatim lab semantics (labs/lifecycle_sim/_choose_action_detailed):
    the record is the switchboard decision's own R1 ``deliberation``
    block, present only when the covenant carries the field AND the tick
    actually reached the switchboard — reflexes (the quick-path guards)
    and the idle/random policies don't think, and no-covenant flows
    never produce the key, so every frozen path stays byte-identical."""
    if policy == "idle":
        return "idle", None
    if policy == "random":
        return rng.choice(ACTIONS), None
    if policy != "switchboard":
        raise ValueError(f"unsupported lifecycle policy: {policy}")

    if state["energy"] < 0.18:
        return "sleep", None
    if state["hunger"] > 0.7:
        return "feed", None
    if state["stress"] > 0.72:
        return "idle", None
    # An explicit evaluator lets a consumer use promoted learning without
    # changing the frozen comparator or bypassing its engine-owned reflexes.
    decision = (decision_function or run_switchboard)(state)
    thought = decision.get("deliberation")
    if "qtable_consumer" in decision:
        thought = {**(thought or {}), "qtable_consumer": decision["qtable_consumer"]}
    return decision["action"], thought


def _ctm_state_pressure(state: dict) -> dict[str, float]:
    """Mirrored verbatim from labs/ctm_ticks/ctm_inspired_ticks.py
    (_state_pressure) — pinned by the R1 live-vs-lab parity test."""
    hunger = _clamp(state.get("hunger", 0.5))
    energy = _clamp(state.get("energy", 0.5))
    bond = _clamp(state.get("bond", 0.5))
    stress = _clamp(state.get("stress", 0.0))
    stability = _clamp(state.get("grid_stability", 0.5))
    interaction = 0.0
    for event in state.get("recent_interactions", []):
        interaction = 0.45 * _clamp(event) + 0.55 * interaction
    interaction = round(interaction, 6)
    return {
        "feed": round(hunger * 0.22, 6),
        "sleep": round((1 - energy) * 0.22, 6),
        "play": round(bond * 0.12 + interaction * 0.18 + (1 - stress) * 0.05, 6),
        "idle": round(stress * 0.14 + (1 - interaction) * 0.05, 6),
        "mutate": round((stability - stress) * 0.12, 6),
    }


def _ctm_decision_from_utilities(utilities: dict[str, float], tick: int) -> dict:
    """Mirrored verbatim from labs/ctm_ticks (_decision_from_utilities)."""
    sorted_actions = sorted(utilities.items(), key=lambda item: item[1], reverse=True)
    action, top_score = sorted_actions[0]
    next_score = sorted_actions[1][1] if len(sorted_actions) > 1 else 0.0
    margin = top_score - next_score
    return {
        "action": action,
        "confidence": round(_clamp(0.5 + margin), 6),
        "utilities": {key: round(value, 6) for key, value in sorted(utilities.items())},
        "explanation": (
            f"Selected {action} after {tick} confidence-gated internal ticks."
        ),
    }


def run_switchboard(state: dict) -> dict:
    """Frozen micro-switchboard decision over additive thread utilities."""
    # SLIP ladder rung T3.3 (decision records 0012/0013): profile-authored
    # learning switches gate which threads run (absent key or True = on).
    # No v0.1 flow ever sets the key, so the frozen baseline runs all four
    # threads bit-for-bit. Identical to the lab micro-switchboard.
    switches = state.get("learning_switches") or {}
    threads = [
        run(state)
        for name, run in SWITCHBOARD_THREADS
        if switches.get(name, True)
    ]
    utilities = {action: 0.0 for action in ACTIONS}
    utilities["idle"] = 0.05
    for thread in threads:
        for action, effect in thread["effects"].items():
            utilities[action] = utilities.get(action, 0.0) + effect * thread["confidence"]

    action = max(utilities, key=utilities.get)
    sorted_scores = sorted(utilities.values(), reverse=True)
    margin = sorted_scores[0] - sorted_scores[1] if len(sorted_scores) > 1 else sorted_scores[0]
    confidence = _clamp(0.5 + margin)
    decision = {
        "action": action,
        "confidence": round(confidence, 6),
        "utilities": {key: round(value, 6) for key, value in sorted(utilities.items())},
        "threads": threads,
        "explanation": f"Selected {action} from additive micro-learner utilities.",
    }

    # R1 (DR 0017): CTM-inspired confidence-gated deliberation — the og
    # "thinking over ticks". Opt-in via SLIP-stashed state keys; no v0.1
    # flow ever sets them, so the frozen path is bit-for-bit. Semantics
    # mirror labs/ctm_ticks exactly (pinned by parity test).
    max_ticks = state.get("deliberation_max_ticks")
    if not max_ticks:
        return decision
    threshold = _clamp(state.get("deliberation_confidence_threshold", 0.72))
    aggregate = {name: float(decision["utilities"].get(name, 0.0)) for name in ACTIONS}
    final_decision = decision
    tick_count = 1
    for tick in range(2, max(1, int(max_ticks)) + 1):
        if final_decision["confidence"] >= threshold:
            break
        pressure = _ctm_state_pressure(state)
        gain = round(0.55 / tick, 6)
        for name, value in pressure.items():
            aggregate[name] = aggregate.get(name, 0.0) + value * gain
        final_decision = _ctm_decision_from_utilities(aggregate, tick)
        tick_count = tick
    return {
        "action": final_decision["action"],
        "confidence": final_decision["confidence"],
        "utilities": final_decision["utilities"],
        "threads": threads,
        "explanation": final_decision.get(
            "explanation", decision["explanation"]
        ),
        "deliberation": {
            "tick_count": tick_count,
            "max_ticks": int(max_ticks),
            "confidence_threshold": threshold,
        },
    }


def _recent_interaction_ewma(state: dict) -> dict:
    interactions = state.get("recent_interactions", [])
    value = 0.0
    alpha = 0.45
    for event in interactions:
        value = alpha * float(event) + (1 - alpha) * value
    confidence = min(1.0, len(interactions) / 5)
    effects = {
        "play": round(value * 0.25, 6),
        "idle": round((1 - value) * 0.15, 6),
    }
    return _thread(
        "recent_interaction_ewma",
        {"recent_interactions": interactions},
        round(value, 6),
        confidence,
        "Recent user attention raises play utility; low attention raises idle utility.",
        effects,
    )


def _estimate_hidden_mood(state: dict) -> dict:
    hunger = _clamp(state.get("hunger", 0.5))
    energy = _clamp(state.get("energy", 0.5))
    stress = _clamp(state.get("stress", 0.0))
    if energy < 0.2:
        mood = "tired"
        effects = {"sleep": 0.55, "play": -0.25, "mutate": -0.2}
        confidence = 0.9
    elif hunger > 0.65:
        mood = "hungry"
        effects = {"feed": 0.5, "play": -0.1}
        confidence = 0.85
    elif stress > 0.65:
        mood = "stressed"
        effects = {"idle": 0.35, "mutate": -0.35}
        confidence = 0.8
    else:
        mood = "curious"
        effects = {"play": 0.25, "idle": 0.05}
        confidence = 0.65
    return _thread(
        "hidden_mood_estimator",
        {"hunger": hunger, "energy": energy, "stress": stress},
        mood,
        confidence,
        f"Rule-based latent mood estimate is {mood}.",
        effects,
    )


def _action_preference_thread(state: dict) -> dict:
    """Read-only preference over the episode-scoped action-reward ring.

    Frozen form of the Stage 0 ``action_preference_bandit`` thread: it only
    averages the bounded per-action reward samples already present in the
    caller's episode state. It never writes those samples (the simulator
    transition owns them) and holds no memory of its own.
    """
    rewards = state.get("action_rewards", {})
    means = {}
    for action in ACTIONS:
        samples = rewards.get(action, [])
        means[action] = sum(samples) / len(samples) if samples else 0.35
    best_action = max(means, key=means.get)
    confidence = min(1.0, sum(len(rewards.get(action, [])) for action in ACTIONS) / 10)
    effects = {action: round((mean - 0.5) * 0.25, 6) for action, mean in means.items()}
    return _thread(
        "action_preference_bandit",
        {"action_rewards": rewards},
        {"best_action": best_action, "means": {k: round(v, 6) for k, v in means.items()}},
        confidence,
        f"Historical reward average favors {best_action}.",
        effects,
    )


def _estimate_mutation_risk(state: dict) -> dict:
    stress = _clamp(state.get("stress", 0.0))
    stability = _clamp(state.get("grid_stability", 0.5))
    risk = _clamp(stress * 0.65 + (1 - stability) * 0.35)
    # SLIP ladder rung T3.2 (decision records 0012/0013): the profile's
    # mutation risk tolerance is the risk level at which mutation utility
    # flips negative. Absent (every v0.1 flow) the historical constant
    # 0.35 is the baseline tolerance, bit-for-bit.
    tolerance = state.get("risk_tolerance_mutation")
    inputs = {"stress": stress, "grid_stability": stability}
    if tolerance is None:
        tolerance = 0.35
        explanation = "High stress or low grid stability suppresses mutation."
    else:
        tolerance = _clamp(tolerance)
        inputs["risk_tolerance_mutation"] = tolerance
        explanation = (
            "High stress or low grid stability suppresses mutation; the "
            f"SLIP risk tolerance {tolerance} sets the flip point."
        )
    effects = {
        "mutate": round((tolerance - risk) * 0.6, 6),
        "idle": round(risk * 0.2, 6),
    }
    return _thread(
        "mutation_risk_scorer",
        inputs,
        round(risk, 6),
        0.8,
        explanation,
        effects,
    )


# The frozen execution order of run_switchboard; names match the lab
# micro-switchboard registry (and the SLIP ``learning_switches`` schema).
SWITCHBOARD_THREADS = [
    ("recent_interaction_ewma", _recent_interaction_ewma),
    ("hidden_mood_estimator", _estimate_hidden_mood),
    ("action_preference_bandit", _action_preference_thread),
    ("mutation_risk_scorer", _estimate_mutation_risk),
]


def _thread(
    name: str,
    inputs: dict,
    output: object,
    confidence: float,
    explanation: str,
    effects: dict[str, float],
) -> dict:
    return {
        "name": name,
        "input": inputs,
        "output": output,
        "confidence": round(_clamp(confidence), 6),
        "explanation": explanation,
        "effects": effects,
    }


def _clamp(value: object) -> float:
    try:
        number = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        number = 0.0
    return max(0.0, min(1.0, number))
