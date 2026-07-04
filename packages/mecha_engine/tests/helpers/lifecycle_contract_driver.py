"""Lifecycle contract probe driver executed against the package surface.

Traceability: research/package_specs/mecha_engine_lifecycle_contract_gate.md
("Initial State Acceptance", "Transition Acceptance", "Episode Acceptance",
"Reward Acceptance", "Negative Checks"),
research/package_specs/mecha_engine_contract_traceability_matrix.md
("Lifecycle Test Obligations"), and
research/package_specs/mecha_engine_property_negative_test_strategy.md (P4,
invalid-grid rejection, bounded state, cross-module failure propagation).
``tests/test_lifecycle_contract.py`` launches this script in a subprocess
whose PYTHONPATH points at the package ``src`` directory (the same
documented import mechanics as ``tests/test_package_imports.py``), so every
probe exercises ``mecha_engine.lifecycle`` and rejects grids through
``mecha_engine.genome`` — never repository-root or research lab modules —
and the test module itself never touches the interpreter module search
path.

The driver prints a single JSON report on stdout; the unittest module
asserts on it. Fixtures are the frozen repository corpora fixed by the test
fixture manifest: ``data/seed_grids/mg_seed_001.json`` (the Stage 0
comparator grid), ``data/invalid_grids/*.json``, and the valid SLIP profile
``data/slips/valid/slip_lcd_seed.json``.
"""

from __future__ import annotations

import argparse
import inspect
import itertools
import json
import sys
from copy import deepcopy
from pathlib import Path
from statistics import mean

import mecha_engine.lifecycle as lifecycle_module
from mecha_engine.lifecycle import (
    advance_tick,
    initial_state,
    reward_for_transition,
    run_episode,
)


SUPPORTED_ACTIONS = ["feed", "sleep", "play", "idle", "mutate"]
CONTINUOUS_KEYS = ["hunger", "energy", "stress", "bond", "grid_stability"]
REQUIRED_EPISODE_FIELDS = [
    "ticks_requested",
    "survival_ticks",
    "alive",
    "death_cause",
    "need_balance",
    "recovery_events",
    "action_counts",
    "final_state",
    "history",
]
REQUIRED_HISTORY_ENTRY_FIELDS = [
    "tick",
    "action",
    "balance",
    "recoveries",
    "alive",
    "death_cause",
    "state",
]
LEARNER_SURFACE_TOKENS = ("feedback", "learner", "bandit", "memory", "shaping")


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _raised_message(callable_probe) -> str | None:
    try:
        callable_probe()
    except ValueError as error:
        return str(error)
    except Exception as error:  # unexpected exception type is trace-worthy
        return f"UNEXPECTED {type(error).__name__}: {error}"
    return None


def _bounded(state: dict) -> bool:
    return all(0.0 <= float(state[key]) <= 1.0 for key in CONTINUOUS_KEYS)


def probe_surface() -> dict:
    signature = inspect.signature(run_episode)
    defaults = {
        name: (
            parameter.default
            if parameter.default is not inspect.Parameter.empty
            else "REQUIRED"
        )
        for name, parameter in signature.parameters.items()
    }
    public_names = sorted(
        name for name in dir(lifecycle_module) if not name.startswith("_")
    )
    return {
        "public_all": sorted(lifecycle_module.__all__),
        "public_names": public_names,
        "learner_named_public_surface": [
            name
            for name in public_names
            if any(token in name.lower() for token in LEARNER_SURFACE_TOKENS)
        ],
        "run_episode_defaults": {
            "slip_profile": defaults.get("slip_profile"),
            "policy": defaults.get("policy"),
            "actions": defaults.get("actions"),
            "ticks": defaults.get("ticks"),
            "rng_seed": defaults.get("rng_seed"),
        },
    }


def probe_initial_state(grid: dict, profile: dict, invalid_grid: dict) -> dict:
    grid_pristine = deepcopy(grid)
    profile_pristine = deepcopy(profile)

    state = initial_state(grid, profile)
    state_without_profile = initial_state(grid)

    invalid_profile = deepcopy(profile)
    invalid_profile["behavior"]["curiosity"] = 1.2
    invalid_profile_raised = _raised_message(
        lambda: initial_state(grid, invalid_profile)
    )

    misaligned_profile = deepcopy(profile)
    misaligned_profile["grid"]["body_mass_min"] = 25
    misaligned_profile["grid"]["body_mass_max"] = 30
    misaligned_raised = _raised_message(
        lambda: initial_state(grid, misaligned_profile)
    )

    invalid_grid_raised = _raised_message(lambda: initial_state(invalid_grid))
    invalid_grid_with_profile_raised = _raised_message(
        lambda: initial_state(invalid_grid, profile)
    )
    non_dict_raised = _raised_message(lambda: initial_state("not a grid"))

    return {
        "grid_id_preserved": state["grid_id"] == grid_pristine["grid_id"],
        "slip_profile_id_preserved": state["slip_profile_id"]
        == profile_pristine["profile_id"],
        "no_profile_slip_id_none": state_without_profile["slip_profile_id"] is None,
        "alive": state["alive"] is True,
        "age_ticks_zero": state["age_ticks"] == 0,
        "death_cause_none": state["death_cause"] is None,
        "continuous_bounded": _bounded(state) and _bounded(state_without_profile),
        "history_empty": state["history"] == [],
        "recovery_events_zero": state["recovery_events"] == 0,
        "action_counts_zeroed": sorted(state["action_counts"]) == sorted(SUPPORTED_ACTIONS)
        and all(count == 0 for count in state["action_counts"].values()),
        "behavior_priors_from_profile": (
            state["neediness"] == profile_pristine["behavior"]["neediness"]
            and state["sleepiness"] == profile_pristine["behavior"]["sleepiness"]
            and state["curiosity"] == profile_pristine["behavior"]["curiosity"]
        ),
        "profile_changes_priors": state != state_without_profile,
        "grid_mutated": grid != grid_pristine,
        "profile_mutated": profile != profile_pristine,
        "invalid_grid_raised": invalid_grid_raised,
        "invalid_grid_with_profile_raised": invalid_grid_with_profile_raised,
        "non_dict_grid_raised": non_dict_raised,
        "invalid_profile_raised": invalid_profile_raised,
        "misaligned_grid_raised": misaligned_raised,
    }


def probe_transitions(grid: dict, profile: dict) -> dict:
    base = initial_state(grid, profile)
    base_pristine = deepcopy(base)

    ticked = advance_tick(base, "feed")
    unsupported_raised = _raised_message(lambda: advance_tick(base, "dance"))

    # Boundedness sweep: force every low/high corner of the continuous state
    # and apply every supported action (P4 bounded-state oracle).
    bounded_after_all = True
    explicit_death_causes = set()
    death_without_cause = False
    for corner in itertools.product([0.0, 1.0], repeat=len(CONTINUOUS_KEYS)):
        for action in SUPPORTED_ACTIONS:
            forced = deepcopy(base)
            forced.update(dict(zip(CONTINUOUS_KEYS, corner)))
            result = advance_tick(forced, action)
            if not _bounded(result):
                bounded_after_all = False
            if not result["alive"]:
                if result["death_cause"] is None:
                    death_without_cause = True
                else:
                    explicit_death_causes.add(result["death_cause"])

    # Targeted terminal transitions for each explicit death cause.
    death_probes = {}
    for cause, overrides in [
        ("starvation", {"hunger": 0.99}),
        ("energy_collapse", {"energy": 0.03}),
        ("stress_collapse", {"stress": 0.99}),
        ("grid_collapse", {"grid_stability": 0.05}),
    ]:
        forced = deepcopy(base)
        forced.update(overrides)
        result = advance_tick(forced, "idle")
        death_probes[cause] = {
            "alive": result["alive"],
            "death_cause": result["death_cause"],
            "tick_counted": result["age_ticks"] == 1
            and result["history"][-1]["tick"] == 1,
        }

    # Recovery accounting from a dangerous hunger state.
    hungry = deepcopy(base)
    hungry["hunger"] = 0.86
    hungry["energy"] = 0.44
    hungry["stress"] = 0.3
    recovered = advance_tick(hungry, "feed")

    # Dead states pass through unchanged.
    dead = advance_tick(deepcopy(base) | {"hunger": 0.99}, "idle")
    dead_pristine = deepcopy(dead)
    dead_after = advance_tick(dead, "feed")

    return {
        "unsupported_action_raised": unsupported_raised,
        "input_state_mutated": base != base_pristine,
        "age_ticks_incremented": ticked["age_ticks"] == base_pristine["age_ticks"] + 1,
        "action_count_updated": ticked["action_counts"]["feed"]
        == base_pristine["action_counts"]["feed"] + 1,
        "history_appended_once": len(ticked["history"])
        == len(base_pristine["history"]) + 1,
        "history_entry_fields": sorted(ticked["history"][-1]),
        "bounded_after_corner_sweep": bounded_after_all,
        "death_without_cause_seen": death_without_cause,
        "corner_sweep_death_causes_explicit": sorted(explicit_death_causes),
        "death_probes": death_probes,
        "hunger_recovery_recorded": "hunger" in recovered["history"][-1]["recoveries"]
        and recovered["recovery_events"] == hungry["recovery_events"] + 1,
        "dead_state_unchanged": dead_after == dead_pristine,
        "dead_state_history_not_grown": len(dead_after["history"])
        == len(dead_pristine["history"]),
    }


def probe_episodes(grid: dict, profile: dict, invalid_grid: dict) -> dict:
    grid_pristine = deepcopy(grid)
    profile_pristine = deepcopy(profile)

    comparator = {}
    for policy in ["switchboard", "idle", "random"]:
        result = run_episode(grid, profile, policy=policy, ticks=72, rng_seed=20260512)
        comparator[policy] = {
            "survival_ticks": result["survival_ticks"],
            "alive": result["alive"],
            "need_balance": result["need_balance"],
            "recovery_events": result["recovery_events"],
            "death_cause": result["death_cause"],
        }

    switchboard = run_episode(grid, profile, policy="switchboard", ticks=72, rng_seed=20260512)
    idle = run_episode(grid, profile, policy="idle", ticks=72, rng_seed=20260512)
    random_first = run_episode(grid, profile, policy="random", ticks=72, rng_seed=20260512)
    random_repeat = run_episode(grid, profile, policy="random", ticks=72, rng_seed=20260512)
    random_reseeded = run_episode(grid, profile, policy="random", ticks=72, rng_seed=99)
    default_call = run_episode(grid, profile)
    seed_none = run_episode(grid, profile, policy="random", ticks=72)

    episodes = [switchboard, idle, random_first]
    history_ok = True
    bounded_ok = True
    balances_bounded = True
    death_cause_explicit = True
    for episode in episodes:
        entries = episode["history"]
        if len(entries) != episode["survival_ticks"]:
            history_ok = False
        if [entry["tick"] for entry in entries] != list(
            range(1, episode["survival_ticks"] + 1)
        ):
            history_ok = False
        for entry in entries:
            if sorted(entry) != sorted(REQUIRED_HISTORY_ENTRY_FIELDS):
                history_ok = False
            if not _bounded(entry["state"]):
                bounded_ok = False
            if not 0.0 <= entry["balance"] <= 1.0:
                balances_bounded = False
            if not entry["alive"] and entry["death_cause"] is None:
                death_cause_explicit = False
        if not episode["alive"] and episode["death_cause"] is None:
            death_cause_explicit = False
        if not _bounded(episode["final_state"]):
            bounded_ok = False

    # Horizon scoring: dead episodes are scored over the full requested
    # horizon with 0.0 fill, so early death cannot inflate the average.
    idle_balances = [entry["balance"] for entry in idle["history"]]
    padded = idle_balances + [0.0] * (idle["ticks_requested"] - len(idle_balances))
    horizon_score_matches = idle["need_balance"] == round(mean(padded), 6)
    early_death_not_inflated = idle["need_balance"] < round(mean(idle_balances), 6)

    # Explicit action stream support.
    stream = ["feed", "sleep", "play", "idle"] * 3
    stream_episode = run_episode(grid, profile, actions=stream, ticks=12, rng_seed=1)
    ambiguous_raised = _raised_message(
        lambda: run_episode(grid, profile, policy="idle", actions=["idle"], ticks=1)
    )
    short_stream_raised = _raised_message(
        lambda: run_episode(grid, profile, actions=["feed"] * 5, ticks=12)
    )
    bad_stream_raised = _raised_message(
        lambda: run_episode(grid, profile, actions=["feed", "dance"], ticks=2)
    )
    bad_policy_raised = _raised_message(
        lambda: run_episode(grid, profile, policy="reward_shaping", ticks=4)
    )
    invalid_grid_raised = _raised_message(
        lambda: run_episode(invalid_grid, profile, policy="idle", ticks=4)
    )

    try:
        json_roundtrip = json.loads(json.dumps(switchboard)) == switchboard
    except (TypeError, ValueError):
        json_roundtrip = False

    return {
        "comparator": comparator,
        "required_fields_present": [
            field for field in REQUIRED_EPISODE_FIELDS if field in switchboard
        ],
        "default_ticks_requested": default_call["ticks_requested"],
        "default_policy_is_switchboard": default_call == switchboard,
        "seed_none_matches_stage0_seed": seed_none == random_first,
        "deterministic_repeat_identical": random_first == random_repeat,
        "reseeded_differs": random_reseeded != random_first,
        "history_ticks_sequential_and_complete": history_ok,
        "history_states_bounded": bounded_ok,
        "history_balances_bounded": balances_bounded,
        "death_causes_explicit": death_cause_explicit,
        "final_state_keys": sorted(switchboard["final_state"]),
        "action_counts_sum_matches_survival": all(
            sum(episode["action_counts"].values()) == episode["survival_ticks"]
            for episode in episodes
        ),
        "horizon_score_matches_zero_fill": horizon_score_matches,
        "early_death_not_inflated": early_death_not_inflated,
        "stream_policy_field_none": stream_episode["policy"] is None,
        "stream_ticks_requested": stream_episode["ticks_requested"],
        "stream_actions_followed": [
            entry["action"] for entry in stream_episode["history"]
        ]
        == stream[: stream_episode["survival_ticks"]],
        "ambiguous_request_raised": ambiguous_raised,
        "short_stream_raised": short_stream_raised,
        "bad_stream_action_raised": bad_stream_raised,
        "bad_policy_raised": bad_policy_raised,
        "invalid_grid_raised": invalid_grid_raised,
        "json_roundtrip": json_roundtrip,
        "grid_mutated": grid != grid_pristine,
        "profile_mutated": profile != profile_pristine,
    }


def probe_rewards(grid: dict, profile: dict) -> dict:
    episode = run_episode(grid, profile, policy="switchboard", ticks=72, rng_seed=20260512)
    entries = episode["history"]
    start = initial_state(grid, profile)

    rewards = []
    previous_snapshot = {key: start[key] for key in CONTINUOUS_KEYS}
    for entry in entries:
        rewards.append(
            reward_for_transition(previous_snapshot, entry["state"], entry["action"])
        )
        previous_snapshot = entry["state"]
    rewards_bounded = all(0.0 <= reward <= 1.0 for reward in rewards)

    previous = {
        "hunger": 0.8,
        "energy": 0.3,
        "stress": 0.5,
        "bond": 0.4,
        "grid_stability": 0.9,
    }
    improved = {
        "hunger": 0.5,
        "energy": 0.5,
        "stress": 0.3,
        "bond": 0.5,
        "grid_stability": 0.9,
    }
    previous_pristine = deepcopy(previous)
    improved_pristine = deepcopy(improved)
    improved_reward = reward_for_transition(previous, improved, "feed")
    flat_reward = reward_for_transition(improved, improved, "feed")
    repeat_reward = reward_for_transition(previous, improved, "feed")

    signal_deltas = {}
    for key, direction in [
        ("hunger", -0.1),
        ("energy", 0.1),
        ("stress", -0.1),
        ("bond", 0.1),
    ]:
        moved = deepcopy(improved)
        moved[key] = round(moved[key] + direction, 6)
        with_signal = reward_for_transition(improved, moved, "idle")
        without_signal = reward_for_transition(moved, moved, "idle")
        signal_deltas[key] = round(with_signal - without_signal, 6)

    unsupported_raised = _raised_message(
        lambda: reward_for_transition(previous, improved, "dance")
    )
    missing_key_raised = _raised_message(
        lambda: reward_for_transition({"hunger": 0.5}, improved, "feed")
    )

    return {
        "episode_rewards_bounded": rewards_bounded,
        "episode_reward_count": len(rewards),
        "reward_deterministic": improved_reward == repeat_reward,
        "improvement_bonus_positive": improved_reward > flat_reward,
        "recovery_signal_deltas": signal_deltas,
        "reward_in_unit_interval": 0.0 <= improved_reward <= 1.0
        and 0.0 <= flat_reward <= 1.0,
        "inputs_mutated": previous != previous_pristine
        or improved != improved_pristine,
        "unsupported_action_raised": unsupported_raised,
        "missing_state_key_raised": missing_key_raised,
    }


def probe_no_learner_memory(grid: dict, profile: dict) -> dict:
    """Assert lifecycle keeps no online learner memory (contract gate).

    Two probes: (1) identical requests reproduce identically even after
    interleaved episodes with other seeds/policies, so nothing observed in
    one episode can shape another; (2) the per-action reward observations
    live only inside the returned episode state as bounded ring buffers.
    """
    first = run_episode(grid, profile, policy="switchboard", ticks=48, rng_seed=11)
    for seed, policy in [(1, "random"), (2, "switchboard"), (3, "idle"), (4, "random")]:
        run_episode(grid, profile, policy=policy, ticks=48, rng_seed=seed)
    second = run_episode(grid, profile, policy="switchboard", ticks=48, rng_seed=11)

    # Inspect the bounded, episode-scoped reward observations.
    state = initial_state(grid, profile)
    for _ in range(20):
        state = advance_tick(state, "idle")
        if not state["alive"]:
            break
    ring_bounded = all(
        len(samples) <= 8 for samples in state["action_rewards"].values()
    )

    return {
        "cross_episode_results_identical": first == second,
        "action_reward_rings_bounded": ring_bounded,
    }


def probe_loaded_lab_modules() -> list[str]:
    lab_root = "la" "bs"
    return sorted(
        name
        for name in sys.modules
        if name == lab_root or name.startswith(lab_root + ".")
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()

    grid = _load(repo_root / "data" / "seed_grids" / "mg_seed_001.json")
    invalid_grid = _load(
        sorted((repo_root / "data" / "invalid_grids").glob("*.json"))[0]
    )
    profile = _load(repo_root / "data" / "slips" / "valid" / "slip_lcd_seed.json")
    grid_pristine = deepcopy(grid)
    profile_pristine = deepcopy(profile)

    report = {
        "surface": probe_surface(),
        "initial": probe_initial_state(grid, profile, invalid_grid),
        "transitions": probe_transitions(grid, profile),
        "episodes": probe_episodes(grid, profile, invalid_grid),
        "rewards": probe_rewards(grid, profile),
        "no_learner_memory": probe_no_learner_memory(grid, profile),
        "fixtures_mutated": grid != grid_pristine or profile != profile_pristine,
        "lab_modules_loaded": probe_loaded_lab_modules(),
    }
    json.dump(report, sys.stdout)


if __name__ == "__main__":
    main()
