import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parents[2]
WORKSHOP_DIR = ROOT / "labs" / "workshop_editor"
GRID_GENOME_DIR = ROOT / "labs" / "grid_genome"
LIFECYCLE_DIR = ROOT / "labs" / "lifecycle_sim"
MAP_ELITES_DIR = ROOT / "labs" / "map_elites_archive"
for path in [WORKSHOP_DIR, GRID_GENOME_DIR, LIFECYCLE_DIR, MAP_ELITES_DIR]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from extended_descriptors import (  # noqa: E402
    build_extended_map_elites_archive,
    extended_descriptor_for_grid,
)
from lifecycle_sim import run_lifecycle_simulation  # noqa: E402
from slip_preview_gates import build_behavior_preview, validate_preview_request  # noqa: E402


ARTIFACT_ID = "slip_runtime_selection_policy_stage0"
REPORT_PATH = Path("data/workshop_editor/slip_runtime_selection_policy_stage0.json")
APP_DATA_PATH = Path("data/workshop_editor/slip_runtime_selection_policy_data.js")
DEFAULT_PROFILE_PATHS = [
    Path("data/slips/valid/slip_lcd_seed.json"),
    Path("data/slips/valid/slip_gray_stable.json"),
    Path("data/slips/valid/slip_amber_social.json"),
]
DEFAULT_GENERATED_ROOT = Path("data/slips/multi_profile_generation_stage0")


def run_profile_runtime_selection_probe(
    profile_path: Path,
    generated_root: Path,
    *,
    candidate_limit: int = 12,
    lifecycle_ticks: int = 24,
    rng_seed: int = 20260513,
    candidate_profile_id: str | None = None,
    profile_override: dict | None = None,
    probe_id: str | None = None,
) -> dict:
    profile = deepcopy(profile_override) if profile_override is not None else _read_json(profile_path)
    profile_id = profile.get("profile_id", "unknown_profile")
    corpus_profile_id = candidate_profile_id or profile_id
    candidate_paths = sorted((generated_root / corpus_profile_id).glob("*.json"))[
        : max(1, candidate_limit)
    ]

    result = {
        "probe_id": probe_id or f"{profile_id}_runtime_selection_policy",
        "profile_id": profile_id,
        "profile_path": _portable(profile_path),
        "candidate_profile_id": corpus_profile_id,
        "candidate_limit": candidate_limit,
        "lifecycle_ticks": lifecycle_ticks,
        "selection_started": False,
    }
    if not candidate_paths:
        result["validation"] = _validation_failure(
            "candidate_corpus_missing",
            f"no generated candidates found for profile corpus: {corpus_profile_id}",
        )
        return result

    first_grid = _read_json(candidate_paths[0])
    validation = validate_preview_request(profile, first_grid)
    result.update(
        {
            "grid_id": first_grid.get("grid_id"),
            "grid_path": _portable(candidate_paths[0]),
            "validation": validation,
        }
    )
    if not validation["ok"]:
        return result

    candidates = []
    candidate_errors = []
    for path in candidate_paths:
        grid = _read_json(path)
        candidate_validation = validate_preview_request(profile, grid)
        if candidate_validation["ok"]:
            candidates.append(grid)
        else:
            candidate_errors.append(
                {
                    "grid_id": grid.get("grid_id"),
                    "path": _portable(path),
                    "error_families": candidate_validation["error_families"],
                }
            )
    if not candidates:
        result["validation"] = _validation_failure(
            "aligned_candidate_corpus_empty",
            "candidate corpus exists but no candidate aligns with the active SLIP profile",
        )
        result["candidate_errors"] = candidate_errors
        return result

    result["selection_started"] = True
    behavior_preview = build_behavior_preview(profile)
    archive = build_extended_map_elites_archive(
        candidates,
        slip_profile=profile,
        lifecycle_ticks=lifecycle_ticks,
        rng_seed=rng_seed,
    )
    candidate_records = _candidate_selection_records(
        profile,
        candidates,
        archive,
        lifecycle_ticks=lifecycle_ticks,
        rng_seed=rng_seed,
    )
    selected = max(
        candidate_records,
        key=lambda record: (
            record["selection_score"],
            record["archive_fitness"],
            record["grid_id"],
        ),
    )
    result.update(
        {
            "policy": {
                "policy_id": "profile_weighted_archive_elite_v0",
                "runtime_lifecycle_policy": "switchboard",
                "archive_policy": "extended_map_elites_elite_pool",
                "selection_rule": (
                    "weighted average over runtime survival, need balance, bond, "
                    "mutation stability, niche rarity, readability, and SLIP alignment"
                ),
            },
            "behavior_preview": behavior_preview,
            "archive_summary": _archive_summary(archive),
            "candidate_error_count": len(candidate_errors),
            "candidate_errors": candidate_errors,
            "candidate_records": candidate_records,
            "selected": selected,
            "selection_trace": _selection_trace(profile, selected, candidate_records),
            "closed_policy_boundary": (
                "runtime lifecycle metrics and archive elite selection are connected "
                "for Stage 0; bounded offspring and lineage decisions are recorded "
                "by the separate slip_offspring_lineage_gate lab"
            ),
        }
    )
    return result


def run_slip_runtime_selection_policy_lab(
    profile_paths: list[Path],
    generated_root: Path,
    *,
    candidate_limit: int = 12,
    lifecycle_ticks: int = 24,
    rng_seed: int = 20260513,
) -> dict:
    profile_results = [
        run_profile_runtime_selection_probe(
            profile_path,
            generated_root,
            candidate_limit=candidate_limit,
            lifecycle_ticks=lifecycle_ticks,
            rng_seed=rng_seed + index,
        )
        for index, profile_path in enumerate(profile_paths)
    ]
    invalid_probe_results = _invalid_selection_probes(
        profile_paths,
        generated_root,
        candidate_limit=candidate_limit,
        lifecycle_ticks=lifecycle_ticks,
        rng_seed=rng_seed + 100,
    )
    selected_results = [
        result
        for result in profile_results
        if result.get("validation", {}).get("ok") and result.get("selection_started")
    ]
    selected_records = [result["selected"] for result in selected_results]
    invalid_rejected_count = sum(
        1
        for result in invalid_probe_results
        if not result.get("validation", {}).get("ok") and not result["selection_started"]
    )
    report = {
        "artifact_id": ARTIFACT_ID,
        "status": "research_slip_runtime_selection_policy_no_package_code",
        "date": "2026-05-13",
        "purpose": (
            "Specify and test a Stage 0 runtime lifecycle/archive selection "
            "policy that consumes current SLIP profiles, switchboard lifecycle "
            "episodes, and extended MAP-Elites archive elites without running "
            "offspring mutation or claiming profile-weighted evolution."
        ),
        "source_artifacts": [
            "docs/01-brainstorming.md",
            "docs/02-research_plan.md",
            "research/slip/profile_compatibility_tests.md",
            "data/slips/slip_profile_compatibility_matrix_stage0.json",
            "research/package_specs/mecha_engine_lifecycle_contract_gate.md",
            "research/package_specs/mecha_engine_archive_contract_gate.md",
            "research/experiment_reports/2026-05-12-slip-lifecycle-archive-effects.md",
            "research/experiment_reports/2026-05-13-slip-offspring-lineage-gate.md",
            "labs/workshop_editor/slip_lifecycle_archive_effects.py",
            "labs/workshop_editor/slip_offspring_lineage_gate.py",
            "labs/lifecycle_sim/lifecycle_sim.py",
            "labs/map_elites_archive/extended_descriptors.py",
            "data/slips/multi_profile_generation_stage0/",
        ],
        "external_anchors": [
            {
                "source": "Illuminating search spaces by mapping elites",
                "url": "https://arxiv.org/abs/1504.04909",
                "used_for": "Archive selection remains a quality-diversity elite selection policy, not scalar top-k replacement.",
            },
            {
                "source": "Reinforcement Learning: An Introduction, MIT Press page",
                "url": "https://mitpress.mit.edu/9780262039246/reinforcement-learning/",
                "used_for": "Runtime policy consumes reward-like lifecycle measurements without claiming trained RL.",
            },
            {
                "source": "A Contextual-Bandit Approach to Personalized News Article Recommendation",
                "url": "https://arxiv.org/abs/1003.0146",
                "used_for": "Profile-conditioned action/selection context is treated as future online learning context.",
            },
            {
                "source": "JaxLife: An Open-Ended Agentic Simulator",
                "url": "https://arxiv.org/abs/2409.00853",
                "used_for": "Lifecycle survival is kept as an artificial-life measurement axis.",
            },
        ],
        "profile_count": len(profile_results),
        "selection_success_count": len(selected_results),
        "selected_elite_count": len(selected_records),
        "invalid_probe_count": len(invalid_probe_results),
        "invalid_probe_rejected_count": invalid_rejected_count,
        "parameters": {
            "candidate_limit": candidate_limit,
            "lifecycle_ticks": lifecycle_ticks,
            "rng_seed": rng_seed,
        },
        "metrics": {
            "selection_success_rate": _ratio(len(selected_results), len(profile_results)),
            "invalid_probe_rejection_rate": _ratio(
                invalid_rejected_count,
                len(invalid_probe_results),
            ),
            "distinct_selected_grid_ids": _distinct_count(
                record["grid_id"] for record in selected_records
            ),
            "distinct_selected_archive_niches": _distinct_count(
                record["archive_niche"] for record in selected_records
            ),
            "mean_selected_selection_score": _mean_selected(
                selected_records,
                "selection_score",
            ),
            "mean_selected_need_balance": _mean_selected_component(
                selected_records,
                "need_balance",
            ),
            "mean_selected_survival_ratio": _mean_selected_component(
                selected_records,
                "survival_ratio",
            ),
            "runtime_lifecycle_archive_selection_specified": (
                len(selected_results) == len(profile_results)
                and invalid_rejected_count == len(invalid_probe_results)
            ),
        },
        "profile_results": profile_results,
        "invalid_probe_results": invalid_probe_results,
        "closed_states": [
            "runtime_lifecycle_archive_selection_policy",
            "profile_weighted_archive_elite_selection_trace",
            "invalid_profile_rejected_before_runtime_selection",
        ],
        "blocked_states": [
            "runtime_jsonschema_validation",
            "declared_dependency_manifest",
            "profile_weighted_evolution",
            "package_runtime_lifecycle_integration",
            "held_out_long_horizon_behavior_tests",
            "manual_readability_calibration",
            "png_adam7_interlace_decoder",
            "apng_decoder",
            "full_png_conformance",
            "spritesheet_packed_rotation_trim_decoder",
            "runtime_animation_playback",
            "full_project_format_coverage",
            "embedded_png_metadata_writer",
            "project_file_native_metadata_writer",
            "profile_authoring_usability_pilot",
            "community_profile_packs",
        ],
        "decision": "prototype_slip_runtime_selection_policy",
        "next_research_step": (
            "Run held-out long-horizon behavior tests and manual readability "
            "calibration before claiming profile-weighted evolution."
        ),
    }
    return report


def write_slip_runtime_selection_policy_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / f"{ARTIFACT_ID}.json", report)
    for result in report["profile_results"]:
        if result.get("selection_started"):
            _write_json(
                output_dir / f"{result['profile_id']}_runtime_selection_policy.json",
                result,
            )
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")
    (output_dir / "slip_runtime_selection_policy_data.js").write_text(
        "window.MECHAGOTCHI_SLIP_RUNTIME_SELECTION_POLICY = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )


def _candidate_selection_records(
    profile: dict,
    candidates: list[dict],
    archive: dict,
    *,
    lifecycle_ticks: int,
    rng_seed: int,
) -> list[dict]:
    grids_by_id = {grid["grid_id"]: grid for grid in candidates}
    descriptor_counts = _candidate_descriptor_counts(
        profile,
        candidates,
        lifecycle_ticks=lifecycle_ticks,
        rng_seed=rng_seed,
    )
    weights = _profile_selection_weights(profile)
    records = []
    for index, elite in enumerate(archive["elites"].values()):
        grid = grids_by_id[elite["grid_id"]]
        runtime = run_lifecycle_simulation(
            grid,
            profile,
            ticks=lifecycle_ticks,
            policy="switchboard",
            rng_seed=rng_seed + 1000 + index,
        )
        components = _selection_components(
            elite,
            runtime,
            descriptor_counts,
            lifecycle_ticks=lifecycle_ticks,
        )
        score = _weighted_average(components, weights)
        records.append(
            {
                "grid_id": elite["grid_id"],
                "archive_niche": elite["descriptor"]["key"],
                "archive_fitness": elite["fitness"],
                "selection_score": score,
                "components": components,
                "component_weights": weights,
                "runtime_episode": _runtime_summary(runtime, lifecycle_ticks),
                "descriptor_metrics": elite["descriptor"]["metrics"],
                "score_components": elite["score_components"],
            }
        )
    return sorted(
        records,
        key=lambda record: (
            record["selection_score"],
            record["archive_fitness"],
            record["grid_id"],
        ),
        reverse=True,
    )


def _selection_components(
    elite: dict,
    runtime: dict,
    descriptor_counts: dict[str, int],
    *,
    lifecycle_ticks: int,
) -> dict[str, float]:
    descriptor = elite["descriptor"]
    descriptor_metrics = descriptor["metrics"]
    score_components = elite["score_components"]
    niche_count = descriptor_counts.get(descriptor["key"], 1)
    return {
        "survival_ratio": _ratio(runtime["survival_ticks"], lifecycle_ticks),
        "need_balance": _round(runtime["need_balance"]),
        "bond": _round(runtime["final_state"].get("bond", 0.0)),
        "mutation_stability": _round(descriptor_metrics.get("mutation_stability", 0.0)),
        "archive_niche_rarity": _round(1.0 / max(1, niche_count)),
        "readability": _round(score_components.get("readability", 0.0)),
        "slip_alignment": _round(score_components.get("slip_alignment", 0.0)),
    }


def _profile_selection_weights(profile: dict) -> dict[str, float]:
    behavior = profile.get("behavior", {})
    survival = profile.get("survival_weights", {})
    curiosity = _clamp(behavior.get("curiosity", 0.5))
    neediness = _clamp(behavior.get("neediness", 0.5))
    sleepiness = _clamp(behavior.get("sleepiness", 0.5))
    stability = _clamp(survival.get("stability", 0.5))
    novelty = _clamp(survival.get("novelty", 0.25))
    bond = _clamp(survival.get("bond", 0.25))
    return {
        "survival_ratio": _round(0.35 + stability * 0.65),
        "need_balance": _round(0.2 + ((neediness + sleepiness) / 2) * 0.5),
        "bond": _round(0.2 + bond * 0.7),
        "mutation_stability": _round(0.2 + stability * 0.5),
        "archive_niche_rarity": _round(0.15 + novelty * 0.8 + curiosity * 0.1),
        "readability": _round(0.15 + curiosity * 0.35),
        "slip_alignment": 0.4,
    }


def _candidate_descriptor_counts(
    profile: dict,
    candidates: list[dict],
    *,
    lifecycle_ticks: int,
    rng_seed: int,
) -> dict[str, int]:
    counts: dict[str, int] = {}
    for index, grid in enumerate(candidates):
        descriptor = extended_descriptor_for_grid(
            grid,
            slip_profile=profile,
            lifecycle_ticks=lifecycle_ticks,
            rng_seed=rng_seed + index,
        )
        counts[descriptor["key"]] = counts.get(descriptor["key"], 0) + 1
    return counts


def _invalid_selection_probes(
    profile_paths: list[Path],
    generated_root: Path,
    *,
    candidate_limit: int,
    lifecycle_ticks: int,
    rng_seed: int,
) -> list[dict]:
    base_profile = _read_json(profile_paths[0])
    unsupported_version = deepcopy(base_profile)
    unsupported_version["slip_version"] = "0.2.0"
    mismatched_profile = _read_json(profile_paths[1])
    return [
        run_profile_runtime_selection_probe(
            profile_paths[0],
            generated_root,
            candidate_limit=candidate_limit,
            lifecycle_ticks=lifecycle_ticks,
            rng_seed=rng_seed,
            profile_override=unsupported_version,
            probe_id="unsupported_version_rejected_before_runtime_selection",
        ),
        run_profile_runtime_selection_probe(
            profile_paths[1],
            generated_root,
            candidate_limit=candidate_limit,
            lifecycle_ticks=lifecycle_ticks,
            rng_seed=rng_seed + 1,
            candidate_profile_id=base_profile["profile_id"],
            profile_override=mismatched_profile,
            probe_id="mismatched_candidate_corpus_rejected_before_runtime_selection",
        ),
    ]


def _selection_trace(profile: dict, selected: dict, records: list[dict]) -> dict:
    return {
        "profile_id": profile["profile_id"],
        "profile_weights": {
            "behavior": profile.get("behavior", {}),
            "survival_weights": profile.get("survival_weights", {}),
        },
        "profile_weighted_score": selected["selection_score"],
        "selected_grid_id": selected["grid_id"],
        "selected_archive_niche": selected["archive_niche"],
        "selected_components": selected["components"],
        "selected_component_weights": selected["component_weights"],
        "ranked_elite_count": len(records),
        "top_ranked_elites": [
            {
                "rank": index + 1,
                "grid_id": record["grid_id"],
                "archive_niche": record["archive_niche"],
                "selection_score": record["selection_score"],
                "archive_fitness": record["archive_fitness"],
            }
            for index, record in enumerate(records[:5])
        ],
    }


def _archive_summary(archive: dict) -> dict:
    return {
        "archive_id": archive["archive_id"],
        "descriptor_names": archive["descriptor_names"],
        "descriptor_dimensions": archive["descriptor_dimensions"],
        "candidate_count": archive["parameters"]["candidate_count"],
        "occupied_niches": archive["occupied_niches"],
        "coverage": archive["coverage"],
        "best_fitness": archive["best_fitness"],
        "mean_elite_fitness": archive["mean_elite_fitness"],
        "qd_score": archive["qd_score"],
        "elite_grid_ids": sorted(elite["grid_id"] for elite in archive["elites"].values()),
    }


def _runtime_summary(runtime: dict, lifecycle_ticks: int) -> dict:
    return {
        "policy": runtime["policy"],
        "ticks_requested": lifecycle_ticks,
        "survival_ticks": runtime["survival_ticks"],
        "survival_ratio": _ratio(runtime["survival_ticks"], lifecycle_ticks),
        "alive": runtime["alive"],
        "death_cause": runtime["death_cause"],
        "need_balance": runtime["need_balance"],
        "recovery_events": runtime["recovery_events"],
        "action_counts": runtime["action_counts"],
        "final_state": runtime["final_state"],
    }


def _app_payload(report: dict) -> dict:
    return {
        "report": {
            key: report[key]
            for key in [
                "artifact_id",
                "status",
                "profile_count",
                "selection_success_count",
                "selected_elite_count",
                "invalid_probe_count",
                "invalid_probe_rejected_count",
                "metrics",
                "parameters",
                "closed_states",
                "blocked_states",
                "decision",
            ]
        },
        "profile_results": [
            _compact_profile_result(result) for result in report["profile_results"]
        ],
        "invalid_probe_results": report["invalid_probe_results"],
    }


def _compact_profile_result(result: dict) -> dict:
    return {
        "probe_id": result["probe_id"],
        "profile_id": result["profile_id"],
        "validation": result["validation"],
        "selection_started": result["selection_started"],
        "policy": result.get("policy"),
        "archive_summary": result.get("archive_summary"),
        "selected": result.get("selected"),
        "selection_trace": result.get("selection_trace"),
    }


def _readme_text(report: dict) -> str:
    metrics = report["metrics"]
    return (
        "# SLIP Runtime Selection Policy Stage 0\n\n"
        "Lab-only bridge from SLIP profiles to switchboard lifecycle episodes "
        "and extended MAP-Elites archive elite selection.\n\n"
        f"- Profiles: {report['profile_count']}\n"
        f"- Selection successes: {report['selection_success_count']}\n"
        f"- Selected elites: {report['selected_elite_count']}\n"
        f"- Invalid probes rejected: {report['invalid_probe_rejected_count']}"
        f"/{report['invalid_probe_count']}\n"
        f"- Distinct selected grid ids: {metrics['distinct_selected_grid_ids']}\n"
        f"- Mean selected selection score: {metrics['mean_selected_selection_score']}\n"
        f"- Mean selected need balance: {metrics['mean_selected_need_balance']}\n"
        f"- Decision: {report['decision']}\n"
    )


def _validation_failure(family: str, message: str) -> dict:
    return {
        "ok": False,
        "errors": [{"path": "runtime_selection", "family": family, "message": message}],
        "error_families": [family],
        "preview_surfaces": [],
    }


def _weighted_average(components: dict[str, float], weights: dict[str, float]) -> float:
    weighted_sum = 0.0
    weight_sum = 0.0
    for key, value in components.items():
        weight = weights.get(key, 0.0)
        weighted_sum += _clamp(value) * weight
        weight_sum += weight
    return _round(weighted_sum / weight_sum if weight_sum else 0.0)


def _mean_selected(records: list[dict], key: str) -> float:
    if not records:
        return 0.0
    return _round(mean(record[key] for record in records))


def _mean_selected_component(records: list[dict], key: str) -> float:
    if not records:
        return 0.0
    return _round(mean(record["components"][key] for record in records))


def _distinct_count(values) -> int:
    return len({json.dumps(value, sort_keys=True) for value in values})


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _portable(path: Path) -> str:
    return str(path).replace("\\", "/")


def _ratio(numerator: int | float, denominator: int | float) -> float:
    if denominator == 0:
        return 0.0
    return _round(float(numerator) / float(denominator))


def _round(value: int | float) -> float:
    return round(float(value), 6)


def _clamp(value: object) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = 0.0
    return max(0.0, min(1.0, number))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/workshop_editor/slip_runtime_selection_policy_stage0"),
    )
    parser.add_argument("--generated-root", type=Path, default=DEFAULT_GENERATED_ROOT)
    parser.add_argument("--profile", type=Path, action="append")
    parser.add_argument("--candidate-limit", type=int, default=12)
    parser.add_argument("--lifecycle-ticks", type=int, default=24)
    parser.add_argument("--rng-seed", type=int, default=20260513)
    args = parser.parse_args()

    report = run_slip_runtime_selection_policy_lab(
        args.profile or DEFAULT_PROFILE_PATHS,
        args.generated_root,
        candidate_limit=args.candidate_limit,
        lifecycle_ticks=args.lifecycle_ticks,
        rng_seed=args.rng_seed,
    )
    write_slip_runtime_selection_policy_artifacts(args.output_dir, report)
    _write_json(REPORT_PATH, report)
    APP_DATA_PATH.write_text(
        "window.MECHAGOTCHI_SLIP_RUNTIME_SELECTION_POLICY = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )
    print(json.dumps({"artifact_id": report["artifact_id"], "metrics": report["metrics"]}, indent=2))


if __name__ == "__main__":
    main()
