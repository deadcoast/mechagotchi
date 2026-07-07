"""Dataset consumers (E3) — the R6 fuel finally burns.

R6 built the corpora as "the ML tracks' fuel"; nothing consumed them.
This lab wires the first two real consumers, each answering a question
the datasets were built for — measured, honest either way:

**(a) Learned readability on REAL mutations** (`mutationbench_5000`).
R3's model was trained on physics-verified SYNTHETIC degradation pairs.
Does it rank REAL mutation outcomes? Method: R3's own verification
transplanted — for each bench case, regenerate the candidate
deterministically (verifying the dataset's `grid_signature` in
passing), compute the four physics metrics R3's families verified
against (palette contrast, organ detectability, inverse component
count, anchor coverage) for parent and child, and admit the case as
*physics-degraded* only when at least one metric STRICTLY decreased
and none increased (monotone — the same strictness the training pairs
had; mirrored for *physics-improved*). The measurement: on those
physics-labeled real pairs, how often does the learned score agree
(child < parent on degraded; child > parent on improved)? Coverage is
reported first-class — real mutations are rarely monotone, and the
unlabeled remainder is named, not hidden.

**(b) Switchboard evaluation from stored ticks** (`replay_100k_ticks`).
The og table built this corpus for "behaviour and switchboard
evaluation". Consume it AS DATA: stream the gzipped JSONL and compute
per-policy outcomes (mean need balance, survival rate, mean survival
ticks, death causes) across every episode — an at-scale, simulation-free
read of whether the switchboard beats idle/random, from the stored
corpus alone.

Deterministic; stdlib + the package surfaces + the R3 lab authority.
"""

from __future__ import annotations

import argparse
import gzip
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GRID_GENOME = ROOT / "labs" / "grid_genome"
READABILITY = ROOT / "labs" / "readability_benchmark"
PACKAGE_SRC = ROOT / "packages" / "mecha_engine" / "src"
for path in [GRID_GENOME, READABILITY, PACKAGE_SRC]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from corpus_builder import build_seed_grids  # noqa: E402
from learned_readability import (  # noqa: E402
    build_learned_readability_report,
    extract_readability_features,
    learned_readability_score,
)

from mecha_engine.generation import (  # noqa: E402
    generate_candidate,
    train_generation_model,
)
from mecha_engine.genome import grid_signature  # noqa: E402

ARTIFACT_ID = "dataset_consumers_stage0"
REPORT_DATE = "2026-07-07"
DEFAULT_OUTPUT_DIR = ROOT / "data" / "datasets"
BENCH_PATH = (
    ROOT / "data" / "datasets" / "mutationbench_5000" / "mutationbench_5000.jsonl"
)
REPLAY_PATH = (
    ROOT
    / "data"
    / "datasets"
    / "replay_100k_ticks"
    / "replay_100k_ticks.jsonl.gz"
)
CORPUS_PROFILE_PATH = ROOT / "data" / "datasets" / "slip_corpus_r6.json"

# The four metrics R3's degradation families were VERIFIED against —
# the physics ground truth (learned_readability.DEGRADATION_FAMILIES).
PHYSICS_METRICS = (
    "palette_contrast",
    "organ_detectability",
    "inverse_component_count",
    "animation_anchor_coverage",
)


def load_bench_rows(path: str | Path = BENCH_PATH) -> list[dict]:
    return [
        json.loads(line)
        for line in Path(path).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _physics_label(parent_features: dict, child_features: dict) -> str:
    """R3's admission strictness on real mutations: monotone across the
    four verified physics metrics, at least one strict move."""
    decreased = increased = False
    for metric in PHYSICS_METRICS:
        delta = child_features[metric] - parent_features[metric]
        if delta < 0:
            decreased = True
        elif delta > 0:
            increased = True
    if decreased and not increased:
        return "physics_degraded"
    if increased and not decreased:
        return "physics_improved"
    return "unlabeled"


def evaluate_learned_on_mutationbench(
    rows: list[dict],
    seeds_by_id: dict[str, dict],
    generation_model: dict,
    slip_profile: dict,
    model: dict,
) -> dict:
    """(a): pairwise accuracy of the learned model on physics-labeled
    REAL mutation pairs, with dataset-integrity verification riding
    along (every regenerated candidate must match its stored
    signature)."""
    signature_mismatches = 0
    labels = {"physics_degraded": 0, "physics_improved": 0, "unlabeled": 0}
    agree = {"physics_degraded": 0, "physics_improved": 0}
    ties_by_label = {"physics_degraded": 0, "physics_improved": 0}
    for row in rows:
        parent = seeds_by_id[row["parent_grid_id"]]
        child = generate_candidate(
            parent, generation_model, slip_profile, rng_seed=row["rng_seed"]
        )
        if grid_signature(child) != row["candidate_signature"]:
            signature_mismatches += 1
            continue
        label = _physics_label(
            extract_readability_features(parent),
            extract_readability_features(child),
        )
        labels[label] += 1
        if label == "unlabeled":
            continue
        parent_score = learned_readability_score(parent, model)
        child_score = learned_readability_score(child, model)
        if child_score == parent_score:
            ties_by_label[label] += 1
            continue
        if label == "physics_degraded" and child_score < parent_score:
            agree["physics_degraded"] += 1
        elif label == "physics_improved" and child_score > parent_score:
            agree["physics_improved"] += 1
    labeled = labels["physics_degraded"] + labels["physics_improved"]
    agreed = agree["physics_degraded"] + agree["physics_improved"]
    ties = ties_by_label["physics_degraded"] + ties_by_label["physics_improved"]
    scored = labeled - ties
    return {
        "case_count": len(rows),
        "signature_mismatches": signature_mismatches,
        "labels": labels,
        "labeled_count": labeled,
        "coverage": round(labeled / len(rows), 6) if rows else 0.0,
        "score_ties": ties,
        "agreements": agree,
        "pairwise_accuracy": round(agreed / scored, 6) if scored else None,
        "accuracy_by_label": {
            label: (
                round(agree[label] / scored_label, 6)
                if (scored_label := labels[label] - ties_by_label[label])
                else None
            )
            for label in ("physics_degraded", "physics_improved")
        },
    }


def evaluate_replay_corpus(path: str | Path = REPLAY_PATH) -> dict:
    """(b): per-policy behaviour outcomes streamed from the stored
    corpus — no simulation, the dataset IS the evidence."""
    per_policy: dict[str, dict] = {}
    episodes: dict[str, dict] = {}
    tick_count = 0
    with gzip.open(Path(path), "rt", encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            tick_count += 1
            policy = row["policy"]
            stats = per_policy.setdefault(
                policy, {"ticks": 0, "balance_sum": 0.0}
            )
            stats["ticks"] += 1
            stats["balance_sum"] += row["balance"]
            episode = episodes.setdefault(
                row["episode_id"],
                {
                    "policy": policy,
                    "last_tick": 0,
                    "alive": True,
                    "death_cause": None,
                    "balance_sum": 0.0,
                    "horizon": row["ticks_requested"],
                },
            )
            episode["balance_sum"] += row["balance"]
            if row["tick"] > episode["last_tick"]:
                episode["last_tick"] = row["tick"]
                episode["alive"] = row["alive"]
                episode["death_cause"] = row.get("death_cause")
    summary = {}
    for policy, stats in sorted(per_policy.items()):
        policy_episodes = [
            e for e in episodes.values() if e["policy"] == policy
        ]
        survivors = sum(1 for e in policy_episodes if e["alive"])
        death_causes: dict[str, int] = {}
        for episode in policy_episodes:
            if not episode["alive"] and episode["death_cause"]:
                death_causes[episode["death_cause"]] = (
                    death_causes.get(episode["death_cause"], 0) + 1
                )
        summary[policy] = {
            "ticks": stats["ticks"],
            "episodes": len(policy_episodes),
            # Raw per-tick mean over LIVED ticks (dead episodes stop
            # contributing) — reported, but NOT the engine's statistic.
            "mean_balance_per_lived_tick": round(
                stats["balance_sum"] / stats["ticks"], 6
            ),
            # The ENGINE-FAITHFUL statistic: run_episode's need_balance
            # scores the FULL requested horizon with missing post-death
            # ticks as 0.0 ("early death can never inflate the score by
            # shortening the horizon") — reconstructed exactly:
            # sum(balances) / horizon per episode, averaged.
            "mean_episode_need_balance": round(
                sum(
                    e["balance_sum"] / e["horizon"] for e in policy_episodes
                )
                / len(policy_episodes),
                6,
            ),
            "survival_rate": round(survivors / len(policy_episodes), 6),
            "mean_survival_ticks": round(
                sum(e["last_tick"] for e in policy_episodes)
                / len(policy_episodes),
                6,
            ),
            "death_causes": dict(sorted(death_causes.items())),
        }
    ordered = sorted(
        summary, key=lambda p: -summary[p]["mean_episode_need_balance"]
    )
    return {
        "tick_count": tick_count,
        "episode_count": len(episodes),
        "by_policy": summary,
        "need_balance_ranking": ordered,
        "switchboard_beats_all_on_need_balance": bool(ordered)
        and ordered[0] == "switchboard",
        "statistic_note": (
            "the ranking uses the engine-faithful episode need_balance "
            "(full-horizon, post-death ticks as 0.0 — run_episode's own "
            "rule); the raw per-lived-tick mean is reported alongside "
            "because the two can DISAGREE when survival differs"
        ),
    }


def build_consumers_report(bench_eval: dict, replay_eval: dict) -> dict:
    return {
        "artifact_id": ARTIFACT_ID,
        "status": "stage0_complete",
        "date": REPORT_DATE,
        "purpose": (
            "E3: the R6 corpora gain their first real consumers — the R3 "
            "learned-readability model evaluated on mutationbench_5000's "
            "REAL mutation outcomes via R3's own physics-verification "
            "method, and a per-policy behaviour evaluation streamed from "
            "replay_100k_ticks with no simulation."
        ),
        "source_artifacts": [
            "data/datasets/mutationbench_5000/mutationbench_5000.jsonl",
            "data/datasets/replay_100k_ticks/replay_100k_ticks.jsonl.gz",
            "data/datasets/slip_corpus_r6.json",
            "research/decision_records/0019-learned-readability.md",
        ],
        "metrics": {
            "mutationbench_evaluation": bench_eval,
            "replay_corpus_evaluation": replay_eval,
        },
        "closed_states": [
            "mutationbench_consumed_with_signature_verification",
            "real_mutation_pairs_physics_labeled_by_the_r3_rule",
            "replay_corpus_consumed_as_stored_data_no_simulation",
        ],
        "blocked_states": [],
        "decision": {
            "status": "datasets_are_live_fuel",
            "adoption": "lab_only_dataset_consumer_evidence",
            "reason": (
                "Both corpora are consumed by real evaluations: the "
                "learned model scores "
                + (
                    f"{bench_eval['pairwise_accuracy']}"
                    if bench_eval["pairwise_accuracy"] is not None
                    else "n/a"
                )
                + " pairwise accuracy on "
                + str(bench_eval["labeled_count"])
                + " physics-labeled REAL mutation pairs (coverage "
                + str(bench_eval["coverage"])
                + " of 5000 — real mutations are rarely monotone, "
                "reported not hidden), and the stored replay corpus "
                "yields the per-policy behaviour comparison with zero "
                "simulation (switchboard "
                + (
                    "ranks first"
                    if replay_eval["switchboard_beats_all_on_need_balance"]
                    else "does NOT rank first"
                )
                + " on mean need balance). Verdicts are the numbers; "
                "both honest either way."
            ),
        },
        "next_research_step": (
            "E4 (the slip module disposition) and E5 (the five "
            "player-notices audit); if the real-mutation accuracy is "
            "judged low, the bench's physics-labeled pairs are a ready "
            "fine-tuning corpus for the R3 trainer."
        ),
    }


def write_consumers_artifacts(output_dir: str | Path, report: dict) -> None:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "dataset_consumers_stage0.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the R6 dataset consumers (E3)."
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    seeds = build_seed_grids()
    seeds_by_id = {seed["grid_id"]: seed for seed in seeds}
    slip_profile = json.loads(
        CORPUS_PROFILE_PATH.read_text(encoding="utf-8")
    )
    generation_model = train_generation_model(seeds)
    model_report = build_learned_readability_report(rng_seed=20260706)
    model = {
        "weights": model_report["model"]["weights"],
        "reference_features": model_report["model"]["reference_features"],
    }
    rows = load_bench_rows()
    bench_eval = evaluate_learned_on_mutationbench(
        rows, seeds_by_id, generation_model, slip_profile, model
    )
    replay_eval = evaluate_replay_corpus()
    report = build_consumers_report(bench_eval, replay_eval)
    write_consumers_artifacts(args.output_dir, report)
    print(
        json.dumps(
            {
                "artifact_id": report["artifact_id"],
                "decision": report["decision"]["status"],
                "pairwise_accuracy": bench_eval["pairwise_accuracy"],
                "labeled": bench_eval["labeled_count"],
                "coverage": bench_eval["coverage"],
                "signature_mismatches": bench_eval["signature_mismatches"],
                "replay_ranking": replay_eval["need_balance_ranking"],
                "switchboard_first": replay_eval[
                    "switchboard_beats_all_on_need_balance"
                ],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
