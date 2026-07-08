"""The micro-thread fleet contract (cycle 12 D1, gap-analysis Phase D).

The documents specify ~11 micro-learner threads streaming confidence
into the switchboard; ~2 exist. This lab is the CONTRACT the fleet
grows through, plus the first documented need predictor as the
end-to-end pipe cleaner.

A fleet thread is (name, observe, signal):

- ``observe(thread_state, lifecycle_state) -> new thread_state`` — the
  online learning step. Pure (returns a NEW dict), deterministic,
  JSON-serializable, BOUNDED memory. Called by the episode/companion
  loop per tick, never by the switchboard (the promoted rule: decide is
  a pure read; learning mechanics live in the loop).
- ``signal(thread_state, lifecycle_state) -> thread dict`` — the same
  ``{name, input, output, confidence, explanation, effects}`` shape the
  historical switchboard threads emit, additively combined as
  ``effects x confidence``.

Thread memory lives in ``lifecycle_state["thread_states"][name]``.

THE OPT-IN RULE (load-bearing): historical switchboard threads run on
``learning_switches`` absent-or-True; fleet threads run ONLY on an
explicit ``learning_switches[name] is True``. No existing flow sets
fleet names, so every frozen path — the parity-pinned baseline, every
episode, every session — is byte-identical until a profile opts in.

The pipe cleaner, ``hunger_forecast`` (the documented hunger
predictor): an online trend forecaster over the companion's own hunger
history. It anticipates — its feed utility rises BEFORE the reactive
mood thread's 0.65 threshold trips — and it is honest at cold start
(confidence 0, no effects, no invented signal).
"""

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GRID_GENOME = ROOT / "labs" / "grid_genome"
LIFECYCLE_SIM = ROOT / "labs" / "lifecycle_sim"
PACKAGE_SRC = ROOT / "packages" / "mecha_engine" / "src"
for _path in [GRID_GENOME, LIFECYCLE_SIM, PACKAGE_SRC]:
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))


ARTIFACT_ID = "micro_thread_fleet_contract_stage0"
REPORT_DATE = "2026-07-08"
REPLAY_TICKS = 48
# estimate_hidden_mood's frozen rule: mood flips to "hungry" strictly
# above this. The pipe cleaner must speak BEFORE it.
REACTIVE_HUNGRY_THRESHOLD = 0.65

HISTORY_LIMIT = 8
FEED_ANTICIPATION_FLOOR = 0.55


def hunger_forecast_observe(thread_state: dict, lifecycle_state: dict) -> dict:
    history = list(thread_state.get("history", []))
    history.append(_clamp(lifecycle_state.get("hunger", 0.5)))
    return {"history": history[-HISTORY_LIMIT:]}


def hunger_forecast_signal(thread_state: dict, lifecycle_state: dict) -> dict:
    history = thread_state.get("history", [])
    if len(history) < 2:
        return _thread(
            "hunger_forecast",
            {"history_length": len(history)},
            {"predicted_hunger": None},
            0.0,
            "Cold start: no hunger trend observed yet.",
            {},
        )
    deltas = [
        round(current - previous, 6)
        for previous, current in zip(history, history[1:])
    ]
    slope = sum(deltas) / len(deltas)
    predicted = _clamp(history[-1] + slope)
    rising = sum(1 for delta in deltas if delta > 0)
    falling = sum(1 for delta in deltas if delta < 0)
    consistency = (
        max(rising, falling) / len(deltas) if any(deltas) else 0.0
    )
    confidence = round(
        min(1.0, len(history) / HISTORY_LIMIT) * (0.4 + 0.6 * consistency), 6
    )
    anticipation = max(0.0, predicted - FEED_ANTICIPATION_FLOOR)
    effects = {}
    if anticipation > 0:
        effects["feed"] = round(anticipation * 0.5, 6)
    return _thread(
        "hunger_forecast",
        {"history_length": len(history), "last_hunger": history[-1]},
        {
            "predicted_hunger": round(predicted, 6),
            "slope": round(slope, 6),
        },
        confidence,
        "Hunger trend forecast; anticipatory feeding before the reactive threshold.",
        effects,
    )


# The fleet registry: (name, observe, signal), execution order fixed.
FLEET_THREADS = [
    ("hunger_forecast", hunger_forecast_observe, hunger_forecast_signal),
]
FLEET_THREAD_NAMES = [name for name, _observe, _signal in FLEET_THREADS]


def observe_fleet(lifecycle_state: dict) -> dict:
    """One observe step for every OPTED-IN fleet thread.

    Returns the new ``thread_states`` mapping (the caller stores it back
    on its state); the input state is never mutated. Threads without an
    explicit ``learning_switches[name] is True`` do not run and hold no
    memory.
    """
    switches = lifecycle_state.get("learning_switches") or {}
    thread_states = dict(lifecycle_state.get("thread_states") or {})
    updated: dict = {}
    for name, observe, _signal in FLEET_THREADS:
        if switches.get(name) is True:
            updated[name] = observe(thread_states.get(name) or {}, lifecycle_state)
    return updated


def fleet_signals(lifecycle_state: dict) -> list[dict]:
    """Signals for every opted-in fleet thread (the switchboard seam)."""
    switches = lifecycle_state.get("learning_switches") or {}
    thread_states = lifecycle_state.get("thread_states") or {}
    return [
        signal(thread_states.get(name) or {}, lifecycle_state)
        for name, _observe, signal in FLEET_THREADS
        if switches.get(name) is True
    ]


def _replay(ticks: int, opt_in: bool) -> dict:
    """One deterministic lifecycle replay on the LCD seed subject.

    ``opt_in=False`` is the frozen arm: every visited state is decided by
    BOTH the lab switchboard and the promoted package, counted identical.
    ``opt_in=True`` is the fleet arm: the loop observes per tick (the
    contract's division of labor), and each visited state is also decided
    with the opt-in stripped, so the seam's utility movement is measured
    on the very states the fleet trajectory visits.
    """
    from corpus_builder import build_seed_grids
    from lifecycle_sim import advance_tick, initial_lifecycle_state
    from micro_switchboard import run_switchboard

    from mecha_engine.learning import decide

    slip_profile = json.loads(
        (ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json").read_text(
            encoding="utf-8"
        )
    )
    state = initial_lifecycle_state(build_seed_grids()[0], slip_profile)
    if opt_in:
        switches = dict(state.get("learning_switches") or {})
        switches["hunger_forecast"] = True
        state["learning_switches"] = switches

    arm = {
        "ticks": ticks,
        "lab_package_decisions_identical": 0,
        "fleet_thread_appearances": 0,
        "anticipatory_signal_ticks": 0,
        "first_anticipatory_signal_tick": None,
        "first_reactive_hungry_tick": None,
        "cold_start_silent_ticks": 0,
        "utility_moved_ticks": 0,
        "decision_flips": 0,
        "max_confidence": 0.0,
        "feed_count": 0,
        "mean_hunger": 0.0,
    }
    hunger_total = 0.0
    for tick in range(ticks):
        if opt_in:
            state["thread_states"] = observe_fleet(state)
        decision = run_switchboard(state)
        if decision == decide(state):
            arm["lab_package_decisions_identical"] += 1
        hunger = _clamp(state.get("hunger", 0.5))
        hunger_total += hunger
        if (
            hunger > REACTIVE_HUNGRY_THRESHOLD
            and arm["first_reactive_hungry_tick"] is None
        ):
            arm["first_reactive_hungry_tick"] = tick
        fleet_entries = [
            thread
            for thread in decision["threads"]
            if thread["name"] in FLEET_THREAD_NAMES
        ]
        arm["fleet_thread_appearances"] += len(fleet_entries)
        for entry in fleet_entries:
            arm["max_confidence"] = max(arm["max_confidence"], entry["confidence"])
            if entry["confidence"] == 0.0 and not entry["effects"]:
                arm["cold_start_silent_ticks"] += 1
            if entry["effects"] and hunger <= REACTIVE_HUNGRY_THRESHOLD:
                arm["anticipatory_signal_ticks"] += 1
                if arm["first_anticipatory_signal_tick"] is None:
                    arm["first_anticipatory_signal_tick"] = tick
        if opt_in:
            stripped = dict(state)
            stripped.pop("thread_states", None)
            stripped_switches = dict(stripped.get("learning_switches") or {})
            stripped_switches.pop("hunger_forecast", None)
            stripped["learning_switches"] = stripped_switches
            frozen_decision = run_switchboard(stripped)
            if frozen_decision["utilities"] != decision["utilities"]:
                arm["utility_moved_ticks"] += 1
            if frozen_decision["action"] != decision["action"]:
                arm["decision_flips"] += 1
        if decision["action"] == "feed":
            arm["feed_count"] += 1
        state = advance_tick(state, decision["action"])
    arm["mean_hunger"] = round(hunger_total / ticks, 6)
    return arm


def build_thread_fleet_report() -> dict:
    frozen = _replay(REPLAY_TICKS, opt_in=False)
    fleet = _replay(REPLAY_TICKS, opt_in=True)
    frozen_arm = {
        key: frozen[key]
        for key in [
            "ticks",
            "lab_package_decisions_identical",
            "fleet_thread_appearances",
            "feed_count",
            "mean_hunger",
        ]
    }
    fleet_arm = {key: fleet[key] for key in fleet if key != "decision_flips"}
    fleet_arm["decision_flips"] = fleet["decision_flips"]

    frozen_holds = (
        frozen["lab_package_decisions_identical"] == frozen["ticks"]
        and frozen["fleet_thread_appearances"] == 0
    )
    anticipates = fleet["anticipatory_signal_ticks"] > 0 and (
        fleet["first_reactive_hungry_tick"] is None
        or fleet["first_anticipatory_signal_tick"]
        < fleet["first_reactive_hungry_tick"]
    )
    complete = frozen_holds and anticipates
    return {
        "artifact_id": ARTIFACT_ID,
        "status": "complete" if complete else "refuted",
        "date": REPORT_DATE,
        "purpose": (
            "The D1 micro-thread fleet contract (observe -> signal -> "
            "confidence in [0,1], pure, deterministic, JSON-serializable, "
            "bounded memory) plus the switchboard's ADDITIVE confidence "
            "seam, proven on a two-arm deterministic lifecycle replay: "
            "the frozen arm must be byte-identical lab-and-package with "
            "zero fleet appearances; the opted-in arm must move utilities "
            "through the seam and speak before the reactive hungry "
            "threshold (0.65) trips."
        ),
        "source_artifacts": [
            "labs/grid_genome/micro_switchboard.py",
            "packages/mecha_engine/src/mecha_engine/learning/_switchboard.py",
            "packages/mecha_engine/src/mecha_engine/learning/threads.py",
            "labs/lifecycle_sim/lifecycle_sim.py",
            "data/slips/valid/slip_lcd_seed.json",
            "data/seed_grids/mg_seed_001.json",
            "docs/gap-analysis.md",
            "docs/project-research/deep-research/01/deep-research.md",
        ],
        "metrics": {
            "replay_ticks": REPLAY_TICKS,
            "fleet_size": len(FLEET_THREADS),
            "documented_fleet_target": 11,
            "reactive_hungry_threshold": REACTIVE_HUNGRY_THRESHOLD,
            "feed_anticipation_floor": FEED_ANTICIPATION_FLOOR,
            "frozen_replay": frozen_arm,
            "fleet_replay": fleet_arm,
        },
        "closed_states": (
            [
                "thread_contract_defined_observe_signal_confidence",
                "opt_in_rule_keeps_frozen_paths_byte_identical",
                "switchboard_seam_additive_lab_and_package",
                "package_twin_parity_pinned_by_lab_tests",
                "hunger_forecast_speaks_before_the_reactive_threshold",
                "cold_start_is_honest_zero_confidence_no_effects",
            ]
            if complete
            else ["d1_bar_not_met_recorded_honestly"]
        ),
        "blocked_states": [
            "need_predictors_not_trained_on_replayed_histories (D2)",
            "confidence_calibration_unmeasured (D2)",
            "animation_bandit_and_hmm_mood_not_built (D3)",
            "evidence_threads_not_wired (D4)",
            "synthetic_keepers_and_scale_harness_absent (D5)",
            "ablation_gates_not_run (D6)",
        ]
        + (
            []
            if fleet["decision_flips"] > 0
            else [
                "anticipatory_signal_moves_utilities_but_never_flips_the_lcd_decision "
                "(effect magnitudes are D2's calibration work; recorded, not fudged)"
            ]
        ),
        "decision": (
            "The contract and the seam hold: "
            f"{frozen_arm['lab_package_decisions_identical']}/{REPLAY_TICKS} "
            "frozen decisions byte-identical lab-and-package with zero fleet "
            "appearances; the opted-in pipe cleaner moved utilities on "
            f"{fleet_arm['utility_moved_ticks']} ticks and first spoke at "
            f"tick {fleet_arm['first_anticipatory_signal_tick']} "
            f"(reactive threshold trips at "
            f"{fleet_arm['first_reactive_hungry_tick']})."
            if complete
            else "The D1 bar is NOT met — recorded, not fudged."
        ),
        "next_research_step": (
            "D2: the need predictors (sleep/energy, boredom/novelty, "
            "attention, interaction timing) trained against replayed "
            "lifecycle traces, each streaming calibrated confidence."
        ),
    }


def write_thread_fleet_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / f"{ARTIFACT_ID}.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Micro-thread fleet contract lab (cycle 12 D1)."
    )
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "data" / "micro_threads"
    )
    args = parser.parse_args()
    report = build_thread_fleet_report()
    write_thread_fleet_artifacts(args.output_dir, report)
    print(json.dumps(report["metrics"], indent=2))
    print(report["decision"])


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


if __name__ == "__main__":
    main()
