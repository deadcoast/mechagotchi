import argparse
import json
from pathlib import Path


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


def run_switchboard(state: dict) -> dict:
    threads = [
        recent_interaction_ewma(state),
        estimate_hidden_mood(state),
        action_preference_bandit(state),
        estimate_mutation_risk(state),
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
    parser.add_argument("--output", type=Path, default=Path("data/micro_learners/switchboard_stage0.json"))
    args = parser.parse_args()
    results = run_scenarios()
    write_scenarios(args.output, results)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
