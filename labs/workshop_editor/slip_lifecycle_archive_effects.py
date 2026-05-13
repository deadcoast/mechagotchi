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

from extended_descriptors import build_extended_map_elites_archive
from lifecycle_sim import run_lifecycle_simulation
from slip_preview_gates import (
    build_behavior_preview,
    build_mutation_preview,
    validate_preview_request,
)


ARTIFACT_ID = "slip_lifecycle_archive_effects_stage0"
REPORT_PATH = Path("data/workshop_editor/slip_lifecycle_archive_effects_stage0.json")
EFFECT_DATA_PATH = Path("data/workshop_editor/slip_lifecycle_archive_effects_data.js")
DEFAULT_PROFILE_PATHS = [
    Path("data/slips/valid/slip_lcd_seed.json"),
    Path("data/slips/valid/slip_gray_stable.json"),
    Path("data/slips/valid/slip_amber_social.json"),
]
DEFAULT_GENERATED_ROOT = Path("data/slips/multi_profile_generation_stage0")
ACTIONS = ["feed", "play", "sleep", "idle", "mutate"]


def run_profile_effect_probe(
    profile_path: Path,
    generated_root: Path,
    *,
    candidate_limit: int = 12,
    lifecycle_ticks: int = 24,
    archive_lifecycle_ticks: int = 12,
    rng_seed: int = 20260512,
    grid_path: Path | None = None,
    profile_override: dict | None = None,
    probe_id: str | None = None,
) -> dict:
    profile = deepcopy(profile_override) if profile_override is not None else _read_json(profile_path)
    selected_grid_path = grid_path or _first_grid_path(profile, generated_root)
    grid = _read_json(selected_grid_path)
    validation = validate_preview_request(profile, grid)
    result = {
        "probe_id": probe_id or f"{profile.get('profile_id', 'unknown')}_effect_probe",
        "profile_id": profile.get("profile_id"),
        "grid_id": grid.get("grid_id"),
        "profile_path": _portable(profile_path),
        "grid_path": _portable(selected_grid_path),
        "validation": validation,
        "effects_started": False,
    }
    if not validation["ok"]:
        return result

    behavior_preview = build_behavior_preview(profile)
    mutation_preview = build_mutation_preview(profile, grid)
    lifecycle = run_lifecycle_simulation(
        grid,
        profile,
        ticks=lifecycle_ticks,
        policy="switchboard",
        rng_seed=rng_seed,
    )
    candidates = _candidate_grids(profile, generated_root, candidate_limit)
    archive = build_extended_map_elites_archive(
        candidates,
        slip_profile=profile,
        lifecycle_ticks=archive_lifecycle_ticks,
        rng_seed=rng_seed,
    )
    lifecycle_effect = _lifecycle_effect(profile, grid, lifecycle, lifecycle_ticks)
    archive_effect = _archive_effect(profile, archive)
    preview_signals = behavior_preview["signals"]
    result.update(
        {
            "effects_started": True,
            "behavior_preview": behavior_preview,
            "mutation_preview": mutation_preview,
            "preview_signals": preview_signals,
            "lifecycle_effect": lifecycle_effect,
            "archive_effect": archive_effect,
            "preview_to_lifecycle_links": _preview_to_lifecycle_links(
                preview_signals,
                mutation_preview,
                lifecycle_effect,
                archive_effect,
            ),
            "preview_effect_fingerprint": behavior_preview["effect_fingerprint"],
            "lifecycle_effect_fingerprint": _lifecycle_fingerprint(lifecycle_effect),
            "archive_effect_fingerprint": _archive_fingerprint(archive_effect),
        }
    )
    result["measured_effect_fingerprint"] = _measured_effect_fingerprint(result)
    return result


def run_slip_lifecycle_archive_effect_lab(
    profile_paths: list[Path],
    generated_root: Path,
    *,
    candidate_limit: int = 12,
    lifecycle_ticks: int = 24,
    archive_lifecycle_ticks: int = 12,
    rng_seed: int = 20260512,
) -> dict:
    profile_results = [
        run_profile_effect_probe(
            profile_path,
            generated_root,
            candidate_limit=candidate_limit,
            lifecycle_ticks=lifecycle_ticks,
            archive_lifecycle_ticks=archive_lifecycle_ticks,
            rng_seed=rng_seed + index,
        )
        for index, profile_path in enumerate(profile_paths)
    ]
    invalid_probe_results = _invalid_effect_probes(
        profile_paths,
        generated_root,
        candidate_limit=candidate_limit,
        lifecycle_ticks=lifecycle_ticks,
        archive_lifecycle_ticks=archive_lifecycle_ticks,
        rng_seed=rng_seed + 100,
    )

    valid_results = [result for result in profile_results if result["validation"]["ok"]]
    lifecycle_effect_count = sum(1 for result in valid_results if "lifecycle_effect" in result)
    archive_effect_count = sum(1 for result in valid_results if "archive_effect" in result)
    invalid_rejected_count = sum(
        1
        for result in invalid_probe_results
        if not result["validation"]["ok"] and not result["effects_started"]
    )
    distinct_preview = _distinct_count(
        result["preview_effect_fingerprint"] for result in valid_results
    )
    distinct_lifecycle = _distinct_count(
        result["lifecycle_effect_fingerprint"] for result in valid_results
    )
    distinct_archive = _distinct_count(
        result["archive_effect_fingerprint"] for result in valid_results
    )
    profile_weight_effects_measured = (
        len(valid_results) == len(profile_paths)
        and distinct_preview == len(valid_results)
        and distinct_lifecycle >= 2
        and distinct_archive >= 1
    )
    report = {
        "artifact_id": ARTIFACT_ID,
        "status": "research_slip_lifecycle_archive_effects_no_package_code",
        "date": "2026-05-12",
        "purpose": (
            "Connect deterministic SLIP behavior/mutation preview signals to "
            "measured lifecycle and extended MAP-Elites archive effects for "
            "the current valid profile corpus without claiming package runtime "
            "integration or full profile-weighted evolution."
        ),
        "source_artifacts": [
            "docs/01-brainstorming.md",
            "docs/02-research_plan.md",
            "research/slip/profile_compatibility_tests.md",
            "data/slips/slip_profile_compatibility_matrix_stage0.json",
            "data/slips/valid/slip_lcd_seed.json",
            "data/slips/valid/slip_gray_stable.json",
            "data/slips/valid/slip_amber_social.json",
            "data/slips/multi_profile_generation_stage0/",
            "data/workshop_editor/slip_behavior_mutation_preview_stage0.json",
            "labs/workshop_editor/slip_preview_gates.py",
            "labs/lifecycle_sim/lifecycle_sim.py",
            "labs/map_elites_archive/extended_descriptors.py",
        ],
        "external_anchors": [
            {
                "source": "Reinforcement Learning: An Introduction, official online draft",
                "url": "http://incompleteideas.net/book/the-book-2nd.html",
                "used_for": "Action-value and bandit vocabulary is kept as evaluation context, not as a claim that a trained RL policy exists.",
            },
            {
                "source": "Illuminating search spaces by mapping elites",
                "url": "https://arxiv.org/abs/1504.04909",
                "used_for": "Archive effects are reported as MAP-Elites quality-diversity measurements over descriptors.",
            },
            {
                "source": "A Contextual-Bandit Approach to Personalized News Article Recommendation",
                "url": "https://arxiv.org/abs/1003.0146",
                "used_for": "Personalized action choice remains future work; this lab records deterministic profile effects before online learning.",
            },
        ],
        "profile_count": len(profile_results),
        "preview_request_success_count": len(valid_results),
        "lifecycle_effect_count": lifecycle_effect_count,
        "archive_effect_count": archive_effect_count,
        "invalid_probe_count": len(invalid_probe_results),
        "invalid_probe_rejected_count": invalid_rejected_count,
        "parameters": {
            "candidate_limit": candidate_limit,
            "lifecycle_ticks": lifecycle_ticks,
            "archive_lifecycle_ticks": archive_lifecycle_ticks,
            "rng_seed": rng_seed,
        },
        "metrics": {
            "preview_request_success_rate": _ratio(len(valid_results), len(profile_results)),
            "lifecycle_effect_success_rate": _ratio(lifecycle_effect_count, len(profile_results)),
            "archive_effect_success_rate": _ratio(archive_effect_count, len(profile_results)),
            "invalid_probe_rejection_rate": _ratio(
                invalid_rejected_count,
                len(invalid_probe_results),
            ),
            "distinct_preview_fingerprints": distinct_preview,
            "distinct_lifecycle_fingerprints": distinct_lifecycle,
            "distinct_archive_fingerprints": distinct_archive,
            "profile_weight_effects_measured": profile_weight_effects_measured,
            "preview_to_lifecycle_archive_effects_measured": (
                profile_weight_effects_measured
                and lifecycle_effect_count == len(profile_results)
                and archive_effect_count == len(profile_results)
            ),
            "mean_lifecycle_need_balance": _mean_metric(
                valid_results,
                ["lifecycle_effect", "need_balance"],
            ),
            "mean_lifecycle_survival_ratio": _mean_metric(
                valid_results,
                ["lifecycle_effect", "survival_ratio"],
            ),
            "mean_archive_qd_score": _mean_metric(
                valid_results,
                ["archive_effect", "qd_score"],
            ),
        },
        "profile_results": profile_results,
        "invalid_probe_results": invalid_probe_results,
        "closed_states": [
            "profile_preview_signal_measurement",
            "slip_preview_lifecycle_effect_probe",
            "slip_preview_archive_effect_probe",
            "invalid_profile_rejected_before_lifecycle_archive",
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
        "decision": "prototype_slip_lifecycle_archive_effect_probe",
        "next_research_step": (
            "Promote profile-weighted evolution only after held-out "
            "long-horizon behavior tests and manual readability calibration pass."
        ),
    }
    return report


def write_slip_lifecycle_archive_effect_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / f"{ARTIFACT_ID}.json", report)
    for result in report["profile_results"]:
        _write_json(
            output_dir / f"{result['profile_id']}_lifecycle_archive_effects.json",
            result,
        )
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")
    (output_dir / "slip_lifecycle_archive_effects_data.js").write_text(
        "window.MECHAGOTCHI_SLIP_LIFECYCLE_ARCHIVE_EFFECTS = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )


def _invalid_effect_probes(
    profile_paths: list[Path],
    generated_root: Path,
    *,
    candidate_limit: int,
    lifecycle_ticks: int,
    archive_lifecycle_ticks: int,
    rng_seed: int,
) -> list[dict]:
    base_profile = _read_json(profile_paths[0])
    base_grid_path = _first_grid_path(base_profile, generated_root)
    unsupported_version = deepcopy(base_profile)
    unsupported_version["slip_version"] = "0.2.0"
    mismatched_profile = _read_json(profile_paths[1])
    return [
        run_profile_effect_probe(
            profile_paths[0],
            generated_root,
            candidate_limit=candidate_limit,
            lifecycle_ticks=lifecycle_ticks,
            archive_lifecycle_ticks=archive_lifecycle_ticks,
            rng_seed=rng_seed,
            grid_path=base_grid_path,
            profile_override=unsupported_version,
            probe_id="unsupported_version_rejected_before_effects",
        ),
        run_profile_effect_probe(
            profile_paths[1],
            generated_root,
            candidate_limit=candidate_limit,
            lifecycle_ticks=lifecycle_ticks,
            archive_lifecycle_ticks=archive_lifecycle_ticks,
            rng_seed=rng_seed + 1,
            grid_path=base_grid_path,
            profile_override=mismatched_profile,
            probe_id="mismatched_profile_grid_rejected_before_effects",
        ),
    ]


def _lifecycle_effect(
    profile: dict,
    grid: dict,
    lifecycle: dict,
    lifecycle_ticks: int,
) -> dict:
    action_counts = {
        action: int(lifecycle["action_counts"].get(action, 0)) for action in ACTIONS
    }
    final_state = lifecycle["final_state"]
    return {
        "profile_id": profile["profile_id"],
        "grid_id": grid["grid_id"],
        "policy": lifecycle["policy"],
        "ticks_requested": lifecycle_ticks,
        "survival_ticks": lifecycle["survival_ticks"],
        "survival_ratio": _ratio(lifecycle["survival_ticks"], lifecycle_ticks),
        "alive": lifecycle["alive"],
        "death_cause": lifecycle["death_cause"],
        "need_balance": lifecycle["need_balance"],
        "recovery_events": lifecycle["recovery_events"],
        "action_counts": action_counts,
        "action_ratios": {
            action: _ratio(count, max(1, lifecycle["survival_ticks"]))
            for action, count in action_counts.items()
        },
        "final_state": {
            key: _round(final_state.get(key, 0.0))
            for key in ["hunger", "energy", "stress", "bond", "grid_stability"]
        },
    }


def _archive_effect(profile: dict, archive: dict) -> dict:
    component_means = _score_component_means(archive)
    descriptor_metric_means = _descriptor_metric_means(archive)
    return {
        "profile_id": profile["profile_id"],
        "archive_id": archive["archive_id"],
        "descriptor_names": archive["descriptor_names"],
        "descriptor_dimensions": archive["descriptor_dimensions"],
        "candidate_count": archive["parameters"]["candidate_count"],
        "lifecycle_ticks": archive["parameters"]["lifecycle_ticks"],
        "occupied_niches": archive["occupied_niches"],
        "coverage": archive["coverage"],
        "best_fitness": archive["best_fitness"],
        "mean_elite_fitness": archive["mean_elite_fitness"],
        "qd_score": archive["qd_score"],
        "elite_count": len(archive["elites"]),
        "score_component_means": component_means,
        "descriptor_metric_means": descriptor_metric_means,
        "representative_elites": list(archive["elites"].values())[:3],
    }


def _preview_to_lifecycle_links(
    preview_signals: dict,
    mutation_preview: dict,
    lifecycle_effect: dict,
    archive_effect: dict,
) -> dict:
    action_counts = lifecycle_effect["action_counts"]
    action_ratios = lifecycle_effect["action_ratios"]
    descriptor_means = archive_effect["descriptor_metric_means"]
    return {
        "social_pull_to_play": {
            "preview_signal": preview_signals["social_pull"],
            "lifecycle_action": "play",
            "action_count": action_counts["play"],
            "action_ratio": action_ratios["play"],
            "final_bond": lifecycle_effect["final_state"]["bond"],
        },
        "rest_pull_to_sleep": {
            "preview_signal": preview_signals["rest_pull"],
            "lifecycle_action": "sleep",
            "action_count": action_counts["sleep"],
            "action_ratio": action_ratios["sleep"],
            "final_energy": lifecycle_effect["final_state"]["energy"],
        },
        "mutation_pressure_to_archive": {
            "preview_signal": preview_signals["mutation_pressure"],
            "cell_mutation_budget": mutation_preview["budgets"]["cell_mutation_budget"],
            "organ_shift_budget": mutation_preview["budgets"]["organ_shift_budget"],
            "archive_mutation_stability_mean": descriptor_means.get(
                "mutation_stability",
                0.0,
            ),
        },
        "mutation_caution_to_archive": {
            "preview_signal": preview_signals["mutation_caution"],
            "caps_respected": mutation_preview["caps_respected"],
            "archive_best_fitness": archive_effect["best_fitness"],
            "archive_qd_score": archive_effect["qd_score"],
        },
    }


def _lifecycle_fingerprint(lifecycle_effect: dict) -> list[float]:
    action_ratios = lifecycle_effect["action_ratios"]
    final_state = lifecycle_effect["final_state"]
    return [
        lifecycle_effect["survival_ratio"],
        lifecycle_effect["need_balance"],
        _ratio(lifecycle_effect["recovery_events"], lifecycle_effect["ticks_requested"]),
        action_ratios["feed"],
        action_ratios["play"],
        action_ratios["sleep"],
        action_ratios["idle"],
        action_ratios["mutate"],
        final_state["bond"],
        final_state["energy"],
    ]


def _archive_fingerprint(archive_effect: dict) -> list[float]:
    descriptor_means = archive_effect["descriptor_metric_means"]
    component_means = archive_effect["score_component_means"]
    return [
        _round(archive_effect["occupied_niches"]),
        archive_effect["coverage"],
        archive_effect["best_fitness"],
        archive_effect["mean_elite_fitness"],
        archive_effect["qd_score"],
        descriptor_means.get("lifecycle_survival", 0.0),
        descriptor_means.get("behavior_neediness", 0.0),
        descriptor_means.get("mutation_stability", 0.0),
        component_means.get("slip_alignment", 0.0),
    ]


def _measured_effect_fingerprint(result: dict) -> dict:
    lifecycle = result["lifecycle_effect"]
    archive = result["archive_effect"]
    return {
        "lifecycle_survival_ratio": lifecycle["survival_ratio"],
        "lifecycle_need_balance": lifecycle["need_balance"],
        "lifecycle_recovery_rate": _ratio(
            lifecycle["recovery_events"],
            lifecycle["ticks_requested"],
        ),
        "lifecycle_play_ratio": lifecycle["action_ratios"]["play"],
        "lifecycle_sleep_ratio": lifecycle["action_ratios"]["sleep"],
        "archive_occupied_niches": archive["occupied_niches"],
        "archive_best_fitness": archive["best_fitness"],
        "archive_qd_score": archive["qd_score"],
    }


def _candidate_grids(profile: dict, generated_root: Path, candidate_limit: int) -> list[dict]:
    grid_paths = sorted((generated_root / profile["profile_id"]).glob("*.json"))
    if not grid_paths:
        raise ValueError(f"no generated grids found for profile: {profile['profile_id']}")
    selected = grid_paths[: max(1, candidate_limit)]
    return [_read_json(path) for path in selected]


def _first_grid_path(profile: dict, generated_root: Path) -> Path:
    grid_paths = sorted((generated_root / profile["profile_id"]).glob("*.json"))
    if not grid_paths:
        raise ValueError(f"no generated grids found for profile: {profile['profile_id']}")
    return grid_paths[0]


def _score_component_means(archive: dict) -> dict:
    elites = list(archive["elites"].values())
    keys = sorted(
        {
            key
            for elite in elites
            for key in elite.get("score_components", {})
        }
    )
    return {
        key: _round(mean(elite["score_components"].get(key, 0.0) for elite in elites))
        for key in keys
    }


def _descriptor_metric_means(archive: dict) -> dict:
    elites = list(archive["elites"].values())
    keys = sorted(
        {
            key
            for elite in elites
            for key in elite.get("descriptor", {}).get("metrics", {})
        }
    )
    return {
        key: _round(
            mean(elite["descriptor"]["metrics"].get(key, 0.0) for elite in elites)
        )
        for key in keys
    }


def _mean_metric(results: list[dict], path: list[str]) -> float:
    values = []
    for result in results:
        cursor = result
        for key in path:
            cursor = cursor[key]
        values.append(float(cursor))
    if not values:
        return 0.0
    return _round(mean(values))


def _distinct_count(values) -> int:
    return len({json.dumps(value, sort_keys=True) for value in values})


def _app_payload(report: dict) -> dict:
    return {
        "report": {
            key: report[key]
            for key in [
                "artifact_id",
                "status",
                "profile_count",
                "preview_request_success_count",
                "lifecycle_effect_count",
                "archive_effect_count",
                "invalid_probe_count",
                "invalid_probe_rejected_count",
                "metrics",
                "parameters",
                "closed_states",
                "blocked_states",
                "decision",
            ]
        },
        "profile_results": report["profile_results"],
        "invalid_probe_results": report["invalid_probe_results"],
    }


def _readme_text(report: dict) -> str:
    metrics = report["metrics"]
    return (
        "# SLIP Lifecycle and Archive Effects Stage 0\n\n"
        "Measured bridge from SLIP preview signals to lifecycle and archive effects.\n\n"
        f"- Profiles: {report['profile_count']}\n"
        f"- Valid preview requests: {report['preview_request_success_count']}\n"
        f"- Lifecycle effects: {report['lifecycle_effect_count']}\n"
        f"- Archive effects: {report['archive_effect_count']}\n"
        f"- Invalid probes rejected: {report['invalid_probe_rejected_count']}"
        f"/{report['invalid_probe_count']}\n"
        f"- Distinct preview fingerprints: {metrics['distinct_preview_fingerprints']}\n"
        f"- Distinct lifecycle fingerprints: {metrics['distinct_lifecycle_fingerprints']}\n"
        f"- Distinct archive fingerprints: {metrics['distinct_archive_fingerprints']}\n"
        f"- Profile-weight effects measured: {metrics['profile_weight_effects_measured']}\n"
        f"- Decision: {report['decision']}\n"
    )


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict) -> None:
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/workshop_editor/slip_lifecycle_archive_effects_stage0"),
    )
    parser.add_argument("--generated-root", type=Path, default=DEFAULT_GENERATED_ROOT)
    parser.add_argument("--profile", type=Path, action="append")
    parser.add_argument("--candidate-limit", type=int, default=12)
    parser.add_argument("--lifecycle-ticks", type=int, default=24)
    parser.add_argument("--archive-lifecycle-ticks", type=int, default=12)
    parser.add_argument("--rng-seed", type=int, default=20260512)
    args = parser.parse_args()

    report = run_slip_lifecycle_archive_effect_lab(
        args.profile or DEFAULT_PROFILE_PATHS,
        args.generated_root,
        candidate_limit=args.candidate_limit,
        lifecycle_ticks=args.lifecycle_ticks,
        archive_lifecycle_ticks=args.archive_lifecycle_ticks,
        rng_seed=args.rng_seed,
    )
    write_slip_lifecycle_archive_effect_artifacts(args.output_dir, report)
    _write_json(REPORT_PATH, report)
    EFFECT_DATA_PATH.write_text(
        "window.MECHAGOTCHI_SLIP_LIFECYCLE_ARCHIVE_EFFECTS = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )
    print(json.dumps({"artifact_id": report["artifact_id"], "metrics": report["metrics"]}, indent=2))


if __name__ == "__main__":
    main()
