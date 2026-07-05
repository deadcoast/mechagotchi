"""Learning contract probe driver executed against the package surface.

Traceability: research/package_specs/mecha_engine_learning_interface_spec.md
("Proposed public surface", "Hard gates for the port", "Non-goals"),
research/package_specs/mecha_engine_contract_traceability_matrix.md
("Cross-Cut Negative Tests"), and
research/decision_records/0009-create-mecha-engine-learning-target.md.
``tests/test_learning_contract.py`` launches this script in a subprocess
whose PYTHONPATH points at the package ``src`` directory (the same
documented import mechanics as ``tests/test_package_imports.py``), so
every probe exercises ``mecha_engine.learning`` and its promoted
dependencies (``genome``, ``lifecycle``) — never repository-root or
research lab modules — and the test module itself never touches the
interpreter module search path.

The driver prints a single JSON report on stdout; the unittest module
asserts on it. Fixtures are the frozen repository corpora:
``data/seed_grids/mg_seed_001.json`` (the sheltered measurement's seed
creature) and ``data/slips/valid/slip_lcd_seed.json``. The sheltered
need-balance pin is computed in-driver from the package surface: the
feedback and frozen 48-tick episodes on the seed fixture must reproduce
the recorded artifact values
(data/micro_learners/switchboard_lifecycle_feedback_stage0.json), and
their delta must equal exactly +0.03964 — a wellbeing pin, never a
survival claim (survival is morphology-decided; both arms survive all 48
ticks here, and the pinned survival delta is zero). The verbatim
reproduction of the lab episode records and the stress benchmark's
per-candidate arms is the lab-side parity pin
(``labs/grid_genome/test_package_learning_parity.py``); this suite proves
the package contract directly.
"""

from __future__ import annotations

import argparse
import inspect
import json
import sys
from copy import deepcopy
from pathlib import Path

import mecha_engine.learning as learning_module
from mecha_engine.learning import ACTIONS, decide, run_feedback_episode
from mecha_engine.lifecycle import initial_state


EPISODE_TICKS = 48


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _json_roundtrip(payload: object) -> bool:
    try:
        return json.loads(json.dumps(payload)) == payload
    except (TypeError, ValueError):
        return False


def probe_surface() -> dict:
    defaults: dict[str, dict] = {}
    keyword_only: dict[str, list[str]] = {}
    for name in learning_module.__all__:
        target = getattr(learning_module, name)
        if not callable(target):
            continue
        signature = inspect.signature(target)
        defaults[name] = {
            parameter_name: (
                repr(parameter.default)
                if parameter.default is not inspect.Parameter.empty
                else "REQUIRED"
            )
            for parameter_name, parameter in signature.parameters.items()
        }
        keyword_only[name] = [
            parameter_name
            for parameter_name, parameter in signature.parameters.items()
            if parameter.kind is inspect.Parameter.KEYWORD_ONLY
        ]
    return {
        "public_all": sorted(learning_module.__all__),
        "actions": list(ACTIONS),
        "signature_defaults": defaults,
        "keyword_only_parameters": keyword_only,
    }


def probe_decide(grid: dict, slip_profile: dict) -> dict:
    state = initial_state(grid, slip_profile)
    state_pristine = deepcopy(state)
    first = decide(state)
    second = decide(state)
    return {
        "deterministic_repeat_identical": first == second,
        "decision_json_roundtrip": _json_roundtrip(first),
        "decision_fields": sorted(first),
        "action_in_actions": first["action"] in ACTIONS,
        "utilities_cover_actions": sorted(first["utilities"]) == sorted(ACTIONS),
        "thread_count": len(first["threads"]),
        "confidence_in_unit_interval": 0.0 <= first["confidence"] <= 1.0,
        "state_mutated": state != state_pristine,
    }


def probe_episodes(grid: dict, slip_profile: dict) -> dict:
    feedback = run_feedback_episode(grid, slip_profile, ticks=EPISODE_TICKS)
    feedback_again = run_feedback_episode(grid, slip_profile, ticks=EPISODE_TICKS)
    frozen = run_feedback_episode(
        grid, slip_profile, ticks=EPISODE_TICKS, feedback_enabled=False
    )
    frozen_again = run_feedback_episode(
        grid, slip_profile, ticks=EPISODE_TICKS, feedback_enabled=False
    )
    return {
        "feedback_deterministic": feedback == feedback_again,
        "frozen_deterministic": frozen == frozen_again,
        "feedback_json_roundtrip": _json_roundtrip(feedback),
        "frozen_json_roundtrip": _json_roundtrip(frozen),
        "episode_fields": sorted(feedback),
        "history_entry_fields": sorted(feedback["history"][0]),
        "feedback_policy": feedback["policy"],
        "frozen_policy": frozen["policy"],
        "feedback_survival_ticks": feedback["survival_ticks"],
        "frozen_survival_ticks": frozen["survival_ticks"],
        "feedback_alive": feedback["alive"],
        "frozen_alive": frozen["alive"],
        "feedback_reward_update_count": feedback["reward_update_count"],
        "feedback_updates_equal_ticks_survived": feedback["reward_update_count"]
        == feedback["survival_ticks"],
        "frozen_reward_update_count": frozen["reward_update_count"],
        "feedback_need_balance": feedback["need_balance"],
        "frozen_need_balance": frozen["need_balance"],
        "need_balance_delta": round(
            feedback["need_balance"] - frozen["need_balance"], 6
        ),
        "feedback_recovery_events": feedback["recovery_events"],
        "frozen_recovery_events": frozen["recovery_events"],
        "frozen_final_means_equal_initial": frozen["final_action_reward_means"]
        == frozen["initial_action_reward_means"],
        "feedback_final_means_differ_from_initial": feedback[
            "final_action_reward_means"
        ]
        != feedback["initial_action_reward_means"],
        "history_length_equals_survival_ticks": len(feedback["history"])
        == feedback["survival_ticks"],
    }


def probe_miscalibrate_off(grid: dict, slip_profile: dict) -> dict:
    first = run_feedback_episode(
        grid, slip_profile, ticks=EPISODE_TICKS, miscalibrate=False
    )
    second = run_feedback_episode(
        grid, slip_profile, ticks=EPISODE_TICKS, miscalibrate=False
    )
    frozen = run_feedback_episode(
        grid,
        slip_profile,
        ticks=EPISODE_TICKS,
        feedback_enabled=False,
        miscalibrate=False,
    )
    return {
        "deterministic_repeat_identical": first == second,
        "episode_json_roundtrip": _json_roundtrip(first),
        "episode_fields": sorted(first),
        "feedback_updates_equal_ticks_survived": first["reward_update_count"]
        == first["survival_ticks"],
        "frozen_reward_update_count": frozen["reward_update_count"],
        # The delta without the miscalibrated start is recorded as an
        # observation only; the pinned learnable-gap measurements both
        # require miscalibrate=True (interface spec).
        "observed_need_balance_delta": round(
            first["need_balance"] - frozen["need_balance"], 6
        ),
    }


def probe_keyword_only_enforced(grid: dict, slip_profile: dict) -> dict:
    def _raised(callable_probe) -> str | None:
        try:
            callable_probe()
        except Exception as error:
            return f"{type(error).__name__}: {error}"
        return None

    return {
        "positional_ticks_raised": _raised(
            lambda: run_feedback_episode(grid, slip_profile, EPISODE_TICKS)
        ),
        "positional_flags_raised": _raised(
            lambda: run_feedback_episode(grid, slip_profile, EPISODE_TICKS, True, True)
        ),
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

    # mg_seed_001 is the frozen sheltered-measurement seed creature
    # (identical to the corpus builder's first seed grid).
    grid = _load(repo_root / "data" / "seed_grids" / "mg_seed_001.json")
    slip_profile = _load(
        repo_root / "data" / "slips" / "valid" / "slip_lcd_seed.json"
    )
    fixtures_pristine = deepcopy([grid, slip_profile])

    report = {
        "surface": probe_surface(),
        "decide": probe_decide(grid, slip_profile),
        "episodes": probe_episodes(grid, slip_profile),
        "miscalibrate_off": probe_miscalibrate_off(grid, slip_profile),
        "keyword_only": probe_keyword_only_enforced(grid, slip_profile),
        "fixtures_mutated": fixtures_pristine != [grid, slip_profile],
        "lab_modules_loaded": probe_loaded_lab_modules(),
    }
    json.dump(report, sys.stdout)


if __name__ == "__main__":
    main()
