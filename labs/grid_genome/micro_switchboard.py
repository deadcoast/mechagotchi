import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


ACTIONS = ["feed", "play", "sleep", "idle", "mutate"]


def recent_interaction_ewma(state: dict) -> dict:
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


def estimate_hidden_mood(state: dict) -> dict:
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


def action_preference_bandit(state: dict) -> dict:
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


def estimate_mutation_risk(state: dict) -> dict:
    stress = _clamp(state.get("stress", 0.0))
    stability = _clamp(state.get("grid_stability", 0.5))
    risk = _clamp(stress * 0.65 + (1 - stability) * 0.35)
    # SLIP ladder rung T3.2 (decision record 0012): the profile's mutation
    # risk tolerance is the risk level at which mutation utility flips
    # negative. Absent (every v0.1 flow) the historical constant 0.35 is
    # the baseline tolerance, bit-for-bit.
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


# Census-facing alias (research/micro_learners/thread_census.md).
mutation_risk_scorer = estimate_mutation_risk

# SLIP ladder rung T3.3 (decision record 0012): the og learning toggles.
# Order matters — it is the frozen execution order of run_switchboard.
SWITCHBOARD_THREADS = [
    ("recent_interaction_ewma", recent_interaction_ewma),
    ("hidden_mood_estimator", estimate_hidden_mood),
    ("action_preference_bandit", action_preference_bandit),
    ("mutation_risk_scorer", estimate_mutation_risk),
]
SWITCHBOARD_THREAD_NAMES = [name for name, _ in SWITCHBOARD_THREADS]


def run_switchboard(state: dict) -> dict:
    # SLIP ladder rung T3.3: profile-authored learning switches gate which
    # threads run (absent key or True = on). No v0.1 flow ever sets the
    # key, so the frozen baseline runs all four threads bit-for-bit.
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


def run_scenarios() -> dict:
    scenarios = {
        "hungry_recent_attention": {
            "hunger": 0.78,
            "energy": 0.46,
            "bond": 0.5,
            "stress": 0.24,
            "grid_stability": 0.86,
            "recent_interactions": [1, 1, 0, 1, 1],
            "action_rewards": {
                "feed": [0.8, 0.7],
                "play": [0.6, 0.6],
                "sleep": [0.3],
                "idle": [0.2],
            },
        },
        "low_energy": {
            "hunger": 0.18,
            "energy": 0.08,
            "bond": 0.45,
            "stress": 0.3,
            "grid_stability": 0.8,
            "recent_interactions": [0, 0, 1, 0, 0],
            "action_rewards": {
                "feed": [0.3],
                "play": [0.2],
                "sleep": [0.9, 0.8],
                "idle": [0.5],
            },
        },
        "stable_curious": {
            "hunger": 0.3,
            "energy": 0.7,
            "bond": 0.7,
            "stress": 0.12,
            "grid_stability": 0.96,
            "recent_interactions": [1, 0, 1, 1, 1],
            "action_rewards": {
                "feed": [0.3],
                "play": [0.8, 0.75],
                "sleep": [0.2],
                "idle": [0.4],
                "mutate": [0.65],
            },
        },
    }
    decisions = {name: run_switchboard(state) for name, state in scenarios.items()}
    action_counts: dict[str, int] = {}
    for decision in decisions.values():
        action_counts[decision["action"]] = action_counts.get(decision["action"], 0) + 1
    return {"scenario_count": len(scenarios), "action_counts": action_counts, "decisions": decisions}


def write_scenarios(path: Path, results: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")


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
        number = float(value)
    except (TypeError, ValueError):
        number = 0.0
    return max(0.0, min(1.0, number))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "data/micro_learners/switchboard_stage0.json")
    args = parser.parse_args()
    results = run_scenarios()
    write_scenarios(args.output, results)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
