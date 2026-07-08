"""The need-predictor evaluation harness (cycle 12 D2, gap-analysis Phase D).

D2's bar: every fleet predictor is proven against REPLAYED lifecycle
traces — the engine's own recorded histories
(`data/datasets/replay_100k_ticks`, 100k per-tick rows across 2501
episodes, switchboard/idle/random policies), never invented data — and
streams CALIBRATED confidence.

Per episode the harness reconstructs the exact lifecycle state stream
the engine produced (the recorded per-tick state snapshots, plus
`recent_interactions` and `action_counts` rebuilt verbatim from the
recorded actions through the same 5-window/append rules
`lifecycle_sim.advance_tick` applies), feeds it tick-by-tick through
each thread's ``observe``, and scores every one-step-ahead prediction
against the recorded next tick:

- ``hunger_forecast`` / ``energy_forecast``: MAE of the predicted next
  need value vs the PERSISTENCE baseline (predict no change).
- ``boredom_novelty``: Brier score of the predicted repeat probability
  (next action == the last action) vs the episode's RUNNING repeat
  base rate.
- ``attention_forecast``: Brier score of the predicted next-tick
  interaction probability vs the episode's RUNNING interaction rate.
- ``interaction_timing``: MAE of the predicted next interaction gap vs
  LAST-GAP persistence.

Calibration: every scored prediction carries the thread's own
confidence; predictions are quartile-binned by confidence and the top
bin's mean error must be no worse than the bottom bin's — confidence
has to MEAN something before D5's harness weighs signals by it.
"""

import argparse
import gzip
import json
from pathlib import Path

from thread_fleet import (
    attention_forecast_observe,
    attention_forecast_signal,
    boredom_novelty_observe,
    boredom_novelty_signal,
    energy_forecast_observe,
    energy_forecast_signal,
    hunger_forecast_observe,
    hunger_forecast_signal,
    interaction_timing_observe,
    interaction_timing_signal,
)


ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = (
    ROOT / "data" / "datasets" / "replay_100k_ticks" / "replay_100k_ticks.jsonl.gz"
)

ARTIFACT_ID = "need_predictors_stage0"
REPORT_DATE = "2026-07-08"
PREDICTOR_KEYS = [
    "hunger_forecast",
    "energy_forecast",
    "boredom_novelty",
    "attention_forecast",
    "interaction_timing",
]
ERROR_METRICS = {
    "hunger_forecast": "mae",
    "energy_forecast": "mae",
    "boredom_novelty": "brier",
    "attention_forecast": "brier",
    "interaction_timing": "gap_mae_ticks",
}
BASELINES = {
    "hunger_forecast": "persistence",
    "energy_forecast": "persistence",
    "boredom_novelty": "running_repeat_rate",
    "attention_forecast": "running_interaction_rate",
    "interaction_timing": "last_gap_persistence",
}
CALIBRATION_BINS = 4
INTERACTION_ACTIONS = {"feed", "play"}
# lifecycle_sim seeds every state with this window before tick 1.
INITIAL_INTERACTION_WINDOW = [1, 0, 1]
INTERACTION_WINDOW_LIMIT = 5


def _load_episodes(path: Path) -> list[list[dict]]:
    opener = gzip.open if path.suffix == ".gz" else open
    grouped: dict[str, list[dict]] = {}
    with opener(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            grouped.setdefault(row["episode_id"], []).append(row)
    episodes = []
    for episode_id in sorted(grouped):
        rows = sorted(grouped[episode_id], key=lambda row: row["tick"])
        episodes.append(rows)
    return episodes


def _reconstruct_states(rows: list[dict]) -> list[dict]:
    """The engine's own state stream, verbatim: recorded snapshots plus
    recent_interactions/action_counts rebuilt through advance_tick's rules."""
    counts: dict[str, int] = {}
    window = list(INITIAL_INTERACTION_WINDOW)
    states = []
    for row in rows:
        action = row["action"]
        counts[action] = counts.get(action, 0) + 1
        interaction = 1 if action in INTERACTION_ACTIONS else 0
        window = (window + [interaction])[-INTERACTION_WINDOW_LIMIT:]
        state = dict(row["state"])
        state["action_counts"] = dict(counts)
        state["recent_interactions"] = list(window)
        states.append(state)
    return states


def _evaluate_episode(rows: list[dict], samples: dict[str, list]) -> None:
    states = _reconstruct_states(rows)
    thread_states: dict[str, dict] = {key: {} for key in PREDICTOR_KEYS}

    repeat_events = 0
    repeat_hits = 0
    interaction_events = 0
    interaction_hits = 0
    pending_gap: tuple[float, float, float] | None = None
    previous_gap: float | None = None
    last_interaction_index: int | None = None

    for index, (state, row) in enumerate(zip(states, rows)):
        if not row["alive"]:
            break
        thread_states["hunger_forecast"] = hunger_forecast_observe(
            thread_states["hunger_forecast"], state
        )
        thread_states["energy_forecast"] = energy_forecast_observe(
            thread_states["energy_forecast"], state
        )
        thread_states["boredom_novelty"] = boredom_novelty_observe(
            thread_states["boredom_novelty"], state
        )
        thread_states["attention_forecast"] = attention_forecast_observe(
            thread_states["attention_forecast"], state
        )
        thread_states["interaction_timing"] = interaction_timing_observe(
            thread_states["interaction_timing"], state
        )

        # -- interaction_timing scores on completed gaps ------------------
        interaction = 1 if rows[index]["action"] in INTERACTION_ACTIONS else 0
        if interaction:
            if last_interaction_index is not None:
                gap = float(index - last_interaction_index)
                if pending_gap is not None:
                    estimate, confidence, baseline_gap = pending_gap
                    samples["interaction_timing"].append(
                        (
                            confidence,
                            abs(estimate - gap),
                            abs(baseline_gap - gap),
                        )
                    )
                    pending_gap = None
                signal = interaction_timing_signal(
                    thread_states["interaction_timing"], state
                )
                estimate = signal["output"]["mean_gap_ticks"]
                if estimate is not None:
                    pending_gap = (estimate, signal["confidence"], gap)
                previous_gap = gap
            last_interaction_index = index

        next_row = rows[index + 1] if index + 1 < len(rows) else None
        if next_row is None:
            break
        next_action = next_row["action"]
        next_interaction = 1 if next_action in INTERACTION_ACTIONS else 0

        # -- hunger / energy one-step forecasts ---------------------------
        for key, field in [
            ("hunger_forecast", "hunger"),
            ("energy_forecast", "energy"),
        ]:
            signal = (
                hunger_forecast_signal(thread_states[key], state)
                if key == "hunger_forecast"
                else energy_forecast_signal(thread_states[key], state)
            )
            predicted = signal["output"][f"predicted_{field}"]
            if predicted is not None:
                actual = float(next_row["state"][field])
                samples[key].append(
                    (
                        signal["confidence"],
                        abs(predicted - actual),
                        abs(float(state[field]) - actual),
                    )
                )

        # -- boredom_novelty: next action repeats the last one -------------
        signal = boredom_novelty_signal(thread_states["boredom_novelty"], state)
        predicted_repeat = signal["output"]["predicted_repeat_probability"]
        if predicted_repeat is not None:
            outcome = 1 if next_action == signal["input"]["last_action"] else 0
            base_rate = (
                repeat_hits / repeat_events if repeat_events else 0.5
            )
            samples["boredom_novelty"].append(
                (
                    signal["confidence"],
                    (predicted_repeat - outcome) ** 2,
                    (base_rate - outcome) ** 2,
                )
            )
            repeat_events += 1
            repeat_hits += outcome

        # -- attention_forecast: next-tick interaction ---------------------
        signal = attention_forecast_signal(
            thread_states["attention_forecast"], state
        )
        predicted_attention = signal["output"][
            "predicted_interaction_probability"
        ]
        if predicted_attention is not None:
            base_rate = (
                interaction_hits / interaction_events
                if interaction_events
                else 0.5
            )
            samples["attention_forecast"].append(
                (
                    signal["confidence"],
                    (predicted_attention - next_interaction) ** 2,
                    (base_rate - next_interaction) ** 2,
                )
            )
        interaction_events += 1
        interaction_hits += 1 if interaction else 0


def _calibration(sample_rows: list[tuple[float, float, float]]) -> dict:
    ordered = sorted(sample_rows, key=lambda item: item[0])
    count = len(ordered)
    bins = []
    for index in range(CALIBRATION_BINS):
        start = index * count // CALIBRATION_BINS
        stop = (index + 1) * count // CALIBRATION_BINS
        chunk = ordered[start:stop]
        if not chunk:
            bins.append({"count": 0, "mean_confidence": None, "error": None})
            continue
        bins.append(
            {
                "count": len(chunk),
                "mean_confidence": round(
                    sum(item[0] for item in chunk) / len(chunk), 6
                ),
                "error": round(
                    sum(item[1] for item in chunk) / len(chunk), 6
                ),
            }
        )
    top_no_worse = bool(
        bins
        and bins[0]["error"] is not None
        and bins[-1]["error"] is not None
        and bins[-1]["error"] <= bins[0]["error"]
    )
    return {"bins": bins, "top_bin_no_worse_than_bottom": top_no_worse}


def evaluate_replay_dataset(
    path: str | Path, max_episodes: int | None = None
) -> dict:
    episodes = _load_episodes(Path(path))
    if max_episodes is not None:
        episodes = episodes[:max_episodes]
    samples: dict[str, list] = {key: [] for key in PREDICTOR_KEYS}
    rows_scored = 0
    for rows in episodes:
        rows_scored += len(rows)
        _evaluate_episode(rows, samples)
    predictors = {}
    for key in PREDICTOR_KEYS:
        rows = samples[key]
        predictor_error = (
            sum(item[1] for item in rows) / len(rows) if rows else None
        )
        baseline_error = (
            sum(item[2] for item in rows) / len(rows) if rows else None
        )
        predictors[key] = {
            "predictions": len(rows),
            "error_metric": ERROR_METRICS[key],
            "baseline": BASELINES[key],
            "predictor_error": (
                round(predictor_error, 6) if predictor_error is not None else None
            ),
            "baseline_error": (
                round(baseline_error, 6) if baseline_error is not None else None
            ),
            "beats_baseline": bool(
                predictor_error is not None
                and baseline_error is not None
                and predictor_error < baseline_error
            ),
            "calibration": _calibration(rows),
        }
    return {
        "episodes": len(episodes),
        "rows": rows_scored,
        "predictors": predictors,
    }


def build_need_predictor_report() -> dict:
    evaluation = evaluate_replay_dataset(DATASET_PATH)
    predictors = evaluation["predictors"]
    all_beat = all(
        predictors[key]["beats_baseline"] for key in PREDICTOR_KEYS
    )
    all_calibrated = all(
        predictors[key]["calibration"]["top_bin_no_worse_than_bottom"]
        for key in PREDICTOR_KEYS
    )
    complete = all_beat and all_calibrated
    return {
        "artifact_id": ARTIFACT_ID,
        "status": "complete" if complete else "refuted",
        "date": REPORT_DATE,
        "purpose": (
            "D2: the documented need predictors (hunger, sleep/energy, "
            "boredom/novelty, attention) and the interaction-timing "
            "predictor, each an online per-companion fleet thread through "
            "the D1 contract, proven one-step-ahead against the engine's "
            "own replayed histories (replay_100k_ticks, 2501 episodes) "
            "with quartile-binned confidence calibration. Bars: every "
            "predictor beats its documented online baseline; every "
            "predictor's top-confidence quartile errs no worse than its "
            "bottom quartile."
        ),
        "source_artifacts": [
            "labs/micro_threads/thread_fleet.py",
            "data/datasets/replay_100k_ticks/replay_100k_ticks.jsonl.gz",
            "data/micro_threads/micro_thread_fleet_contract_stage0.json",
            "labs/lifecycle_sim/lifecycle_sim.py",
            "docs/gap-analysis.md",
            "docs/project-research/deep-research/01/deep-research.md",
        ],
        "metrics": evaluation,
        "closed_states": (
            [
                "five_need_and_timing_predictors_stream_through_the_d1_contract",
                "every_predictor_beats_its_online_baseline_on_replayed_traces",
                "confidence_is_calibrated_top_quartile_no_worse_than_bottom",
                "no_invented_data_the_traces_are_the_engines_own_histories",
            ]
            if complete
            else ["d2_bar_not_met_recorded_honestly"]
        ),
        "blocked_states": [
            "animation_bandit_and_hmm_mood_not_built (D3)",
            "evidence_threads_not_wired (D4)",
            "welfare_impact_of_thread_effects_unmeasured (D5 benchmark; "
            "prediction skill is proven here, utility-effect wiring is "
            "judged by the ablation gates)",
            "ablation_gates_not_run (D6)",
        ],
        "decision": (
            "All five predictors beat their baselines with calibrated "
            "confidence on the engine's own replayed histories."
            if complete
            else "The D2 bar is NOT met — recorded, not fudged."
        ),
        "next_research_step": (
            "D3: the animation-preference bandit over animstate_950 and "
            "the HMM mood thread, both deterministic under seeds."
        ),
    }


def write_need_predictor_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / f"{ARTIFACT_ID}.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Need-predictor replay evaluation lab (cycle 12 D2)."
    )
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "data" / "micro_threads"
    )
    args = parser.parse_args()
    report = build_need_predictor_report()
    write_need_predictor_artifacts(args.output_dir, report)
    print(json.dumps(report["metrics"]["predictors"], indent=2))
    print(report["decision"])


if __name__ == "__main__":
    main()
