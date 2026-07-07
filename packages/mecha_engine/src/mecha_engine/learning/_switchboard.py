"""Micro-switchboard decision function for mecha_engine.learning.

Contract sources:

- research/package_specs/mecha_engine_learning_interface_spec.md
  ("Proposed public surface": ``decide`` is a verbatim port of the
  research micro-switchboard's ``run_switchboard``)
- research/decision_records/0009-create-mecha-engine-learning-target.md

Verbatim semantic port of the grid_genome research lab's micro-switchboard:
identical thread math (interaction EWMA, rule-based mood estimate,
action-preference reward means, mutation-risk score), identical additive
utility combination with the 0.05 idle prior, identical deterministic
``max()`` tie-breaks over the load-bearing ``ACTIONS`` order, and the
identical decision dict (action, confidence, per-action utilities, the four
per-learner signal threads, explanation). The lab-side parity test
(``labs/grid_genome/test_package_learning_parity.py``) pins ``decide``
equal to the lab ``run_switchboard`` over every state visited by a full
feedback episode.

``decide`` is a pure read of the caller's lifecycle state: the only reward
observations it consults are the bounded, episode-scoped ``action_rewards``
ring buffers inside that state. It never writes them and holds no memory of
its own — reward-feedback mechanics live in ``mecha_engine.learning.episode``,
never here and never inside ``mecha_engine.lifecycle``.

Parity note (decision record 0013): the port stays in sync with the lab
switchboard's current semantics — the ``SWITCHBOARD_THREADS`` registry
with profile-authored ``learning_switches`` gating (absent key or True =
on) and the ``risk_tolerance_mutation`` flip point in the mutation-risk
thread (absent key = the historical 0.35 constant). No v0.1 flow ever
sets either state key, so the frozen baseline runs all four threads
bit-for-bit. The lab-side v0.2 parity pin is
``labs/grid_genome/test_package_switchboard_v2_parity.py``.
"""

from __future__ import annotations

# Stage 0 first action set. Order is load-bearing: the switchboard utility
# table and the bandit-thread means iterate in this order, so deterministic
# max() tie-breaks depend on it (identical to the research lab constant).
ACTIONS: list[str] = ["feed", "play", "sleep", "idle", "mutate"]


def decide(state: dict) -> dict:
    """Return the micro-switchboard decision for one lifecycle state.

    Verbatim port of the research lab's ``run_switchboard``: the decision
    dict carries the chosen ``action``, a margin-derived ``confidence``, the
    per-learner signal ``threads``, the per-action ``utilities``, and the
    ``explanation`` string, all rounded exactly as the lab rounds them.
    The input state is never mutated.
    """
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


def _action_preference_bandit(state: dict) -> dict:
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


# SLIP ladder rung T3.3 (decision record 0012): the og learning toggles.
# Order matters — it is the frozen execution order of ``decide``; names
# match the lab registry (and the SLIP ``learning_switches`` schema).
SWITCHBOARD_THREADS = [
    ("recent_interaction_ewma", _recent_interaction_ewma),
    ("hidden_mood_estimator", _estimate_hidden_mood),
    ("action_preference_bandit", _action_preference_bandit),
    ("mutation_risk_scorer", _estimate_mutation_risk),
]
SWITCHBOARD_THREAD_NAMES = [name for name, _ in SWITCHBOARD_THREADS]


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
