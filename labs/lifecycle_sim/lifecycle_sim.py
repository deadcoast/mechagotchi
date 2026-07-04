import argparse
import json
import random
import sys
from copy import deepcopy
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parents[2]
GRID_GENOME = ROOT / "labs" / "grid_genome"
if str(GRID_GENOME) not in sys.path:
    sys.path.insert(0, str(GRID_GENOME))

from corpus_builder import build_seed_grids
from micro_switchboard import ACTIONS, run_switchboard
from slip import is_grid_aligned
from validator import validate_grid


TARGETS = {
    "hunger": 0.34,
    "energy": 0.68,
    "stress": 0.18,
    "bond": 0.72,
    "grid_stability": 0.92,
}

DANGER_THRESHOLDS = {
    "hunger": 0.75,
    "energy": 0.25,
    "stress": 0.65,
    "bond": 0.25,
    "grid_stability": 0.35,
}

ACTION_EFFECTS = {
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


def initial_lifecycle_state(grid: dict, slip_profile: dict | None = None) -> dict:
    validation = validate_grid(grid)
    if not validation.ok:
        raise ValueError(f"invalid grid for lifecycle simulation: {validation.errors}")
    if slip_profile is not None:
        alignment = is_grid_aligned(grid, slip_profile)
        if not alignment.ok:
            raise ValueError(f"grid is not aligned with SLIP: {alignment.errors}")

    cells = grid.get("cells", [])
    cell_stress = mean([float(cell.get("stress", 0)) for cell in cells]) if cells else 0.0
    cell_damage = mean([float(cell.get("damage", 0)) for cell in cells]) if cells else 0.0
    body_mass = sum(1 for cell in cells if cell.get("organ") == "core")

    behavior = (slip_profile or {}).get("behavior", {})
    survival_weights = (slip_profile or {}).get("survival_weights", {})
    neediness = _clamp(behavior.get("neediness", 0.45))
    sleepiness = _clamp(behavior.get("sleepiness", 0.5))
    curiosity = _clamp(behavior.get("curiosity", 0.5))
    stability_weight = _clamp(survival_weights.get("stability", 0.5))
    bond_weight = _clamp(survival_weights.get("bond", 0.25))

    return {
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


def advance_tick(state: dict, action: str) -> dict:
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


def run_lifecycle_simulation(
    grid: dict,
    slip_profile: dict | None = None,
    *,
    ticks: int = 72,
    policy: str = "switchboard",
    rng_seed: int = 20260512,
) -> dict:
    rng = random.Random(rng_seed)
    state = initial_lifecycle_state(grid, slip_profile)
    for _ in range(ticks):
        if not state["alive"]:
            break
        action = _choose_action(policy, state, rng)
        state = advance_tick(state, action)

    balances = [entry["balance"] for entry in state["history"]]
    if balances and len(balances) < ticks:
        balances = balances + [0.0] * (ticks - len(balances))
    need_balance = round(mean(balances), 6) if balances else _need_balance(_snapshot(state))
    return {
        "policy": policy,
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


def run_lifecycle_lab(*, ticks: int = 72, rng_seed: int = 20260512) -> dict:
    grid = build_seed_grids()[0]
    slip_profile = _load_default_slip()
    policies = {
        policy: run_lifecycle_simulation(
            grid,
            slip_profile,
            ticks=ticks,
            policy=policy,
            rng_seed=rng_seed,
        )
        for policy in ["switchboard", "idle", "random"]
    }
    ranked = sorted(
        policies.values(),
        key=lambda result: (result["alive"], result["survival_ticks"], result["need_balance"]),
        reverse=True,
    )
    return {
        "lab_id": "lifecycle_sim_stage0",
        "date": "2026-05-12",
        "source_grid_id": grid["grid_id"],
        "slip_profile_id": slip_profile["profile_id"],
        "ticks_requested": ticks,
        "rng_seed": rng_seed,
        "research_questions": [
            "Can the companion survive a fixed tick horizon?",
            "Does an active policy improve need balance over neglect?",
            "Can recovery from hunger, energy, stress, or bond risk be counted?",
        ],
        "policies": policies,
        "summary": {
            "best_policy": ranked[0]["policy"],
            "switchboard_beats_idle_on_need_balance": (
                policies["switchboard"]["need_balance"] > policies["idle"]["need_balance"]
            ),
            "switchboard_survival_delta_vs_idle": (
                policies["switchboard"]["survival_ticks"]
                - policies["idle"]["survival_ticks"]
            ),
            "switchboard_recovery_delta_vs_idle": (
                policies["switchboard"]["recovery_events"]
                - policies["idle"]["recovery_events"]
            ),
        },
        "decision": "prototype",
        "limitations": [
            "Stage 0 uses deterministic synthetic care actions rather than player traces.",
            "Need balance is still a proxy metric and needs held-out user validation.",
            "Grid repair and cellular stress propagation are not active yet.",
        ],
        "source_refs": [
            {
                "name": "Tamagotchi Connection official manual",
                "url": "https://tamagotchi-official.com/manual/toy/connection/connection_web_manual_IS_EN.pdf",
                "use": "Reference for care-loop categories such as feeding, sleep, and attention.",
            },
            {
                "name": "JaxLife",
                "url": "https://arxiv.org/abs/2409.00853",
                "use": "Reference for measuring survival and behavior in artificial-life substrates.",
            },
        ],
    }


def write_lifecycle_artifacts(output_path: Path, report: dict) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    readme_path = output_path.parent / "README.md"
    readme_path.write_text(
        "# Lifecycle Simulator Stage 0\n\n"
        "Deterministic lifecycle simulator output for the post-v0.1 research gate.\n"
        "The artifact compares switchboard, idle, and random policies on survival ticks,\n"
        "need balance, recovery events, final state, and per-tick history.\n\n"
        "Primary artifact:\n\n"
        "- `lifecycle_stage0.json`\n\n"
        "Metric note:\n\n"
        "- `need_balance` is scored over the full requested horizon.\n"
        "- Missing ticks after death count as `0.0`.\n"
        "- This prevents early death from being rewarded by a short high-average run.\n",
        encoding="utf-8",
    )


def _choose_action(policy: str, state: dict, rng: random.Random) -> str:
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


def _load_default_slip() -> dict:
    path = ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _clamp(value: object) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = 0.0
    return max(0.0, min(1.0, number))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("data/lifecycle/lifecycle_stage0.json"))
    parser.add_argument("--ticks", type=int, default=72)
    parser.add_argument("--rng-seed", type=int, default=20260512)
    args = parser.parse_args()
    report = run_lifecycle_lab(ticks=args.ticks, rng_seed=args.rng_seed)
    write_lifecycle_artifacts(args.output, report)
    print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    main()
