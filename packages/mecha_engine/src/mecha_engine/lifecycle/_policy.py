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
"""

from __future__ import annotations

import random

# Stage 0 first action set. Order is load-bearing: the switchboard utility
# table and the bandit-thread means iterate in this order, so deterministic
# max() tie-breaks depend on it (identical to the research lab constant).
ACTIONS: list[str] = ["feed", "play", "sleep", "idle", "mutate"]

SUPPORTED_POLICIES: tuple[str, ...] = ("switchboard", "idle", "random")


def choose_action(policy: str, state: dict, rng: random.Random) -> str:
    """Choose the next action for a named policy (Stage 0 semantics)."""
    if policy == "idle":
        return "idle"
    if policy == "random":
        return rng.choice(ACTIONS)
    if policy != "switchboard":
        raise ValueError(f"unsupported lifecycle policy: {policy}")

    if state["energy"] < 0.18:
        return "sleep"
    if state["hunger"] > 0.7:
        return "feed"
    if state["stress"] > 0.72:
        return "idle"
    return run_switchboard(state)["action"]


def run_switchboard(state: dict) -> dict:
    """Frozen micro-switchboard decision over additive thread utilities."""
    threads = [
        _recent_interaction_ewma(state),
        _estimate_hidden_mood(state),
        _action_preference_thread(state),
        _estimate_mutation_risk(state),
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
    return {
        "action": action,
        "confidence": round(confidence, 6),
        "utilities": {key: round(value, 6) for key, value in sorted(utilities.items())},
        "threads": threads,
        "explanation": f"Selected {action} from additive micro-learner utilities.",
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
    effects = {
        "mutate": round((0.35 - risk) * 0.6, 6),
        "idle": round(risk * 0.2, 6),
    }
    return _thread(
        "mutation_risk_scorer",
        {"stress": stress, "grid_stability": stability},
        round(risk, 6),
        0.8,
        "High stress or low grid stability suppresses mutation.",
        effects,
    )


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
