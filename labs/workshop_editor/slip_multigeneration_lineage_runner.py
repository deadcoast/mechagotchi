import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parents[2]
WORKSHOP_DIR = ROOT / "labs" / "workshop_editor"
GRID_GENOME_DIR = ROOT / "labs" / "grid_genome"
for path in [WORKSHOP_DIR, GRID_GENOME_DIR]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from lineage_tracker import build_lineage_graph, summarize_lineage_graph  # noqa: E402
from slip_offspring_lineage_gate import (  # noqa: E402
    _build_offspring_candidates,
    _evaluate_offspring_candidates,
    _lineage_decision,
    _read_parent_grid,
)
from slip_preview_gates import build_mutation_preview  # noqa: E402
from slip_runtime_selection_policy import (  # noqa: E402
    _runtime_summary,
    run_profile_runtime_selection_probe,
)


ARTIFACT_ID = "slip_multigeneration_lineage_runner_stage0"
REPORT_PATH = ROOT / "data/workshop_editor/slip_multigeneration_lineage_runner_stage0.json"
APP_DATA_PATH = ROOT / "data/workshop_editor/slip_multigeneration_lineage_runner_data.js"
DEFAULT_PROFILE_PATHS = [
    ROOT / "data/slips/valid/slip_lcd_seed.json",
    ROOT / "data/slips/valid/slip_gray_stable.json",
    ROOT / "data/slips/valid/slip_amber_social.json",
]
DEFAULT_GENERATED_ROOT = ROOT / "data/slips/multi_profile_generation_stage0"


def run_profile_multigeneration_lineage_probe(
    profile_path: Path,
    generated_root: Path,
    *,
    generations: int = 3,
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
    result = {
        "probe_id": probe_id or f"{profile_id}_multigeneration_lineage_runner",
        "profile_id": profile_id,
        "profile_path": _portable(profile_path),
        "candidate_profile_id": corpus_profile_id,
        "generation_count": generations,
        "candidate_limit": candidate_limit,
        "lifecycle_ticks": lifecycle_ticks,
        "runner_started": False,
    }
    runtime_probe = run_profile_runtime_selection_probe(
        profile_path,
        generated_root,
        candidate_limit=candidate_limit,
        lifecycle_ticks=lifecycle_ticks,
        rng_seed=rng_seed,
        candidate_profile_id=corpus_profile_id,
        profile_override=profile,
        probe_id=f"{profile_id}_runtime_parent_for_multigeneration_runner",
    )
    result["runtime_selection"] = _compact_runtime_probe(runtime_probe)
    validation = runtime_probe.get("validation") or _validation_failure(
        "runtime_parent_selection_failed",
        "runtime selection did not produce a validation result",
    )
    result["validation"] = validation
    if not validation.get("ok") or not runtime_probe.get("selection_started"):
        return result

    result["runner_started"] = True
    initial_parent_record = deepcopy(runtime_probe["selected"])
    active_parent_record = deepcopy(initial_parent_record)
    active_parent_grid = _read_parent_grid(
        generated_root,
        corpus_profile_id,
        active_parent_record["grid_id"],
    )
    initial_parent_grid = deepcopy(active_parent_grid)
    archive_records = [deepcopy(record) for record in runtime_probe["candidate_records"]]
    generated_candidates: list[dict] = []
    accepted_frontier_ids = {active_parent_record["grid_id"]}
    generation_records = []

    for generation_index in range(1, generations + 1):
        generation_seed = rng_seed + generation_index * 100
        mutation_preview = build_mutation_preview(profile, active_parent_grid)
        offspring_grids = _build_offspring_candidates(
            profile,
            active_parent_grid,
            mutation_preview,
            rng_seed=generation_seed,
        )
        generated_candidates.extend(deepcopy(offspring_grids))
        offspring_records = _evaluate_offspring_candidates(
            profile,
            offspring_grids,
            active_parent_record,
            {"candidate_records": archive_records},
            mutation_preview,
            lifecycle_ticks=lifecycle_ticks,
            rng_seed=generation_seed,
        )
        selected = offspring_records[0]
        lineage_decision = _lineage_decision(
            active_parent_record,
            selected,
            {"candidate_records": archive_records},
        )
        archive_update = _apply_archive_update(
            archive_records,
            active_parent_record,
            selected,
            lineage_decision,
        )
        selected_grid = _grid_by_id(offspring_grids, selected["grid_id"])
        selected_qualified = _selected_qualified(selected, lineage_decision)
        if selected_qualified:
            active_parent_grid = deepcopy(selected_grid)
            active_parent_record = _parent_record_from_selected(selected)
            accepted_frontier_ids.add(selected["grid_id"])

        generation_records.append(
            {
                "generation_index": generation_index,
                "parent_grid_id": selected["parent_grid_id"],
                "parent_generation": selected["lineage"]["generation"] - 1,
                "offspring_candidate_count": len(offspring_records),
                "offspring_candidates": offspring_records,
                "selected_offspring": selected,
                "lineage_decision": lineage_decision,
                "archive_update": archive_update,
                "continuation_parent_grid_id": active_parent_record["grid_id"],
                "selected_child_continued": selected_qualified,
                "frontier_policy": (
                    "qualified selected offspring continues the candidate "
                    "lineage even when the archive action holds the parent"
                ),
            }
        )

    graph = build_lineage_graph(
        [initial_parent_grid],
        generated_candidates,
        elite_ids=accepted_frontier_ids
        | {record["grid_id"] for record in archive_records},
    )
    graph_summary = summarize_lineage_graph(graph)
    selected_records = [record["selected_offspring"] for record in generation_records]
    result.update(
        {
            "policy": {
                "policy_id": "multigeneration_lineage_runner_v0",
                "parent_selection_policy": "profile_weighted_archive_elite_v0",
                "offspring_mutation_policy": "bounded_stage0_grid_mutation_from_slip_caps",
                "archive_update_policy": "reuse_offspring_lineage_decision_without_package_runtime_claims",
                "frontier_policy": "continue_qualified_selected_child_for_lineage_stress_test",
            },
            "initial_parent": _parent_grid_summary(initial_parent_grid, initial_parent_record),
            "final_frontier_parent": {
                "grid_id": active_parent_record["grid_id"],
                "archive_niche": active_parent_record["archive_niche"],
                "selection_score": active_parent_record["selection_score"],
                "archive_fitness": active_parent_record["archive_fitness"],
            },
            "generation_records": generation_records,
            "lineage_graph": {
                "summary": graph_summary,
                "edges": graph["edges"],
                "orphans": graph["orphans"],
            },
            "archive_summary": {
                "initial_record_count": len(runtime_probe["candidate_records"]),
                "final_record_count": len(archive_records),
                "initial_niche_count": len(
                    {record["archive_niche"] for record in runtime_probe["candidate_records"]}
                ),
                "final_niche_count": len(
                    {record["archive_niche"] for record in archive_records}
                ),
                "final_archive_grid_ids": sorted(
                    {record["grid_id"] for record in archive_records}
                ),
            },
            "metrics": _profile_metrics(
                generation_records,
                graph_summary,
                initial_parent_grid,
            ),
            "closed_policy_boundary": (
                "Stage 0 persists a candidate lineage for multiple generations "
                "inside the lab. It does not create package runtime state, "
                "collect human readability ratings, or claim profile-weighted "
                "evolution."
            ),
        }
    )
    return result


def run_slip_multigeneration_lineage_runner_lab(
    profile_paths: list[Path],
    generated_root: Path,
    *,
    generations: int = 3,
    candidate_limit: int = 12,
    lifecycle_ticks: int = 24,
    rng_seed: int = 20260513,
) -> dict:
    profile_results = [
        run_profile_multigeneration_lineage_probe(
            profile_path,
            generated_root,
            generations=generations,
            candidate_limit=candidate_limit,
            lifecycle_ticks=lifecycle_ticks,
            rng_seed=rng_seed + index,
        )
        for index, profile_path in enumerate(profile_paths)
    ]
    invalid_probe_results = _invalid_multigeneration_probes(
        profile_paths,
        generated_root,
        generations=generations,
        candidate_limit=candidate_limit,
        lifecycle_ticks=lifecycle_ticks,
        rng_seed=rng_seed + 100,
    )
    successful_results = [
        result
        for result in profile_results
        if result.get("validation", {}).get("ok")
        and result.get("runner_started")
        and result.get("metrics", {}).get("lineage_continuity_verified")
    ]
    invalid_rejected_count = sum(
        1
        for result in invalid_probe_results
        if not result.get("validation", {}).get("ok") and not result["runner_started"]
    )
    all_generation_records = [
        record
        for result in successful_results
        for record in result.get("generation_records", [])
    ]
    report = {
        "artifact_id": ARTIFACT_ID,
        "status": "research_slip_multigeneration_lineage_runner_no_package_code",
        "date": "2026-05-13",
        "purpose": (
            "Run a lab-only persistent multigeneration SLIP lineage runner over "
            "current profiles without claiming package runtime integration, "
            "manual readability calibration, or profile-weighted evolution."
        ),
        "source_artifacts": [
            "docs/01-brainstorming.md",
            "docs/02-research_plan.md",
            "research/slip/profile_compatibility_tests.md",
            "research/experiment_reports/2026-05-13-slip-offspring-lineage-gate.md",
            "research/experiment_reports/2026-05-13-slip-long-horizon-behavior-gate.md",
            "research/experiment_reports/2026-05-13-slip-readability-calibration-gate.md",
            "labs/workshop_editor/slip_runtime_selection_policy.py",
            "labs/workshop_editor/slip_offspring_lineage_gate.py",
            "labs/grid_genome/lineage_tracker.py",
            "data/slips/multi_profile_generation_stage0/",
        ],
        "external_anchors": [
            {
                "source": "Illuminating search spaces by mapping elites",
                "url": "https://arxiv.org/abs/1504.04909",
                "used_for": (
                    "Archive updates are tracked as niche-preserving "
                    "quality-diversity decisions instead of scalar winner-only "
                    "selection."
                ),
            },
            {
                "source": "Avida Digital Evolution Platform",
                "url": "https://avida.devosoft.org/",
                "used_for": (
                    "Lineage records and generation-by-generation outcomes are "
                    "treated as experimental artifacts, not implicit runtime state."
                ),
            },
        ],
        "profile_count": len(profile_results),
        "multigeneration_success_count": len(successful_results),
        "total_generation_records": len(all_generation_records),
        "invalid_probe_count": len(invalid_probe_results),
        "invalid_probe_rejected_count": invalid_rejected_count,
        "parameters": {
            "generations": generations,
            "candidate_limit": candidate_limit,
            "lifecycle_ticks": lifecycle_ticks,
            "rng_seed": rng_seed,
        },
        "metrics": _lab_metrics(
            successful_results,
            invalid_rejected_count,
            len(invalid_probe_results),
            generations,
        ),
        "profile_results": profile_results,
        "invalid_probe_results": invalid_probe_results,
        "closed_states": [
            "persistent_multigeneration_lineage_runner",
            "multigeneration_lineage_graph_continuity",
            "invalid_profile_rejected_before_multigeneration_lineage",
        ],
        "blocked_states": [
            "runtime_jsonschema_validation",
            "declared_dependency_manifest",
            "profile_weighted_evolution",
            "package_runtime_lifecycle_integration",
            "manual_readability_calibration",
            "final_descriptor_threshold_lock",
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
        "decision": "prototype_slip_multigeneration_lineage_runner",
        "next_research_step": (
            "Integrate package/runtime lifecycle boundaries and collect manual "
            "readability ratings before claiming profile-weighted evolution."
        ),
    }
    return report


def write_slip_multigeneration_lineage_runner_artifacts(
    output_dir: Path,
    report: dict,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / f"{ARTIFACT_ID}.json", report)
    for result in report["profile_results"]:
        if result.get("runner_started"):
            _write_json(
                output_dir / f"{result['profile_id']}_multigeneration_lineage_runner.json",
                result,
            )
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")
    (output_dir / "slip_multigeneration_lineage_runner_data.js").write_text(
        "window.MECHAGOTCHI_SLIP_MULTIGENERATION_LINEAGE_RUNNER = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )


def _apply_archive_update(
    archive_records: list[dict],
    parent_record: dict,
    selected: dict,
    lineage_decision: dict,
) -> dict:
    action = lineage_decision["action"]
    before_records = deepcopy(archive_records)
    before_count = len(archive_records)
    before_niches = {record["archive_niche"] for record in archive_records}
    selected_record = _parent_record_from_selected(selected)
    if action == "replace_parent":
        archive_records[:] = [
            record
            for record in archive_records
            if record["archive_niche"] != selected["archive_niche"]
        ]
        archive_records.append(selected_record)
    elif action == "add_archive_niche":
        matching = [
            record
            for record in archive_records
            if record["archive_niche"] == selected["archive_niche"]
        ]
        if not matching:
            archive_records.append(selected_record)
        elif selected_record["archive_fitness"] > matching[0]["archive_fitness"]:
            archive_records[:] = [
                record
                for record in archive_records
                if record["archive_niche"] != selected["archive_niche"]
            ]
            archive_records.append(selected_record)
    return {
        "action": action,
        "parent_grid_id": parent_record["grid_id"],
        "offspring_grid_id": selected["grid_id"],
        "archive_record_count_before": before_count,
        "archive_record_count_after": len(archive_records),
        "archive_niche_count_before": len(before_niches),
        "archive_niche_count_after": len(
            {record["archive_niche"] for record in archive_records}
        ),
        "archive_mutated": archive_records != before_records,
    }


def _parent_record_from_selected(selected: dict) -> dict:
    return {
        "grid_id": selected["grid_id"],
        "archive_niche": selected["archive_niche"],
        "archive_fitness": selected["extended_score"]["fitness"],
        "selection_score": selected["offspring_score"],
        "components": selected["components"],
        "component_weights": selected["component_weights"],
        "runtime_episode": selected["runtime_episode"],
        "descriptor_metrics": selected["descriptor_metrics"],
        "score_components": selected["extended_score"]["components"],
    }


def _selected_qualified(selected: dict, lineage_decision: dict) -> bool:
    return (
        lineage_decision["qualified_for_lineage"]
        and selected["validation"]["ok"]
        and selected["validation"].get("alignment", {}).get("ok")
        and selected["cap_compliance"]["caps_respected"]
        and selected["runtime_episode"]["survival_ratio"] >= 1.0
    )


def _profile_metrics(
    generation_records: list[dict],
    graph_summary: dict,
    initial_parent_grid: dict,
) -> dict:
    selected = [record["selected_offspring"] for record in generation_records]
    decision_actions = [record["lineage_decision"]["action"] for record in generation_records]
    initial_generation = int(initial_parent_grid.get("lineage", {}).get("generation", 0))
    return {
        "generation_records": len(generation_records),
        "offspring_candidate_count": sum(
            record["offspring_candidate_count"] for record in generation_records
        ),
        "selected_offspring_count": len(selected),
        "continued_child_count": sum(
            1 for record in generation_records if record["selected_child_continued"]
        ),
        "replace_parent_count": decision_actions.count("replace_parent"),
        "add_archive_niche_count": decision_actions.count("add_archive_niche"),
        "hold_parent_count": decision_actions.count("hold_parent"),
        "mean_selected_offspring_score": _mean_selected(selected, "offspring_score"),
        "mean_selected_runtime_survival_ratio": _mean_nested(
            selected,
            ["runtime_episode", "survival_ratio"],
        ),
        "all_selected_offspring_valid": all(
            record["validation"]["ok"] for record in selected
        ),
        "all_selected_offspring_aligned": all(
            record["validation"].get("alignment", {}).get("ok") for record in selected
        ),
        "all_mutation_caps_respected": all(
            record["cap_compliance"]["caps_respected"] for record in selected
        ),
        "lineage_continuity_verified": (
            graph_summary["orphan_count"] == 0
            and graph_summary["max_generation"] >= initial_generation + len(generation_records)
            and graph_summary["edge_count"] >= len(generation_records)
        ),
        "max_generation": graph_summary["max_generation"],
        "dominant_lineage_share": graph_summary["dominant_lineage_share"],
    }


def _lab_metrics(
    successful_results: list[dict],
    invalid_rejected_count: int,
    invalid_probe_count: int,
    generations: int,
) -> dict:
    profile_metrics = [result["metrics"] for result in successful_results]
    return {
        "persistent_multigeneration_lineage_runner_specified": (
            bool(successful_results)
            and all(
                metrics["generation_records"] == generations
                and metrics["lineage_continuity_verified"]
                for metrics in profile_metrics
            )
            and invalid_rejected_count == invalid_probe_count
        ),
        "invalid_probe_rejection_rate": _ratio(invalid_rejected_count, invalid_probe_count),
        "total_generation_records": sum(
            metrics["generation_records"] for metrics in profile_metrics
        ),
        "total_selected_offspring": sum(
            metrics["selected_offspring_count"] for metrics in profile_metrics
        ),
        "continued_child_count": sum(
            metrics["continued_child_count"] for metrics in profile_metrics
        ),
        "replace_parent_count": sum(
            metrics["replace_parent_count"] for metrics in profile_metrics
        ),
        "add_archive_niche_count": sum(
            metrics["add_archive_niche_count"] for metrics in profile_metrics
        ),
        "hold_parent_count": sum(metrics["hold_parent_count"] for metrics in profile_metrics),
        "max_generation_reached": max(
            (metrics["max_generation"] for metrics in profile_metrics),
            default=0,
        ),
        "mean_selected_offspring_score": _mean_key(
            profile_metrics,
            "mean_selected_offspring_score",
        ),
        "mean_selected_runtime_survival_ratio": _mean_key(
            profile_metrics,
            "mean_selected_runtime_survival_ratio",
        ),
        "mean_dominant_lineage_share": _mean_key(
            profile_metrics,
            "dominant_lineage_share",
        ),
    }


def _invalid_multigeneration_probes(
    profile_paths: list[Path],
    generated_root: Path,
    *,
    generations: int,
    candidate_limit: int,
    lifecycle_ticks: int,
    rng_seed: int,
) -> list[dict]:
    if len(profile_paths) < 2:
        return []
    base_profile = _read_json(profile_paths[0])
    unsupported = deepcopy(base_profile)
    unsupported["slip_version"] = "9.9.9"
    mismatch = deepcopy(base_profile)
    return [
        run_profile_multigeneration_lineage_probe(
            profile_paths[0],
            generated_root,
            generations=generations,
            candidate_limit=candidate_limit,
            lifecycle_ticks=lifecycle_ticks,
            rng_seed=rng_seed,
            profile_override=unsupported,
            probe_id="unsupported_version_rejected_before_multigeneration_lineage",
        ),
        run_profile_multigeneration_lineage_probe(
            profile_paths[0],
            generated_root,
            generations=generations,
            candidate_limit=candidate_limit,
            lifecycle_ticks=lifecycle_ticks,
            rng_seed=rng_seed + 1,
            profile_override=mismatch,
            candidate_profile_id=_read_json(profile_paths[1])["profile_id"],
            probe_id="mismatched_candidate_corpus_rejected_before_multigeneration_lineage",
        ),
    ]


def _parent_grid_summary(parent_grid: dict, parent_record: dict) -> dict:
    return {
        "grid_id": parent_grid["grid_id"],
        "archive_niche": parent_record["archive_niche"],
        "archive_fitness": parent_record["archive_fitness"],
        "selection_score": parent_record["selection_score"],
        "lineage": parent_grid.get("lineage", {}),
        "runtime_episode": parent_record.get("runtime_episode"),
    }


def _compact_runtime_probe(runtime_probe: dict) -> dict:
    selected = runtime_probe.get("selected", {})
    return {
        "probe_id": runtime_probe.get("probe_id"),
        "profile_id": runtime_probe.get("profile_id"),
        "selection_started": runtime_probe.get("selection_started", False),
        "validation_ok": runtime_probe.get("validation", {}).get("ok", False),
        "candidate_record_count": len(runtime_probe.get("candidate_records", [])),
        "selected_grid_id": selected.get("grid_id") if isinstance(selected, dict) else None,
        "selected_archive_niche": selected.get("archive_niche") if isinstance(selected, dict) else None,
        "selected_score": selected.get("selection_score") if isinstance(selected, dict) else None,
    }


def _app_payload(report: dict) -> dict:
    return {
        "artifact_id": report["artifact_id"],
        "status": report["status"],
        "profile_count": report["profile_count"],
        "multigeneration_success_count": report["multigeneration_success_count"],
        "total_generation_records": report["total_generation_records"],
        "metrics": report["metrics"],
        "profiles": [
            _compact_profile_result(result) for result in report["profile_results"]
        ],
        "blocked_states": report["blocked_states"],
        "decision": report["decision"],
    }


def _compact_profile_result(result: dict) -> dict:
    metrics = result.get("metrics", {})
    return {
        "profile_id": result.get("profile_id"),
        "runner_started": result.get("runner_started", False),
        "initial_parent_id": result.get("initial_parent", {}).get("grid_id"),
        "final_frontier_parent_id": result.get("final_frontier_parent", {}).get("grid_id"),
        "generation_records": metrics.get("generation_records"),
        "continued_child_count": metrics.get("continued_child_count"),
        "max_generation": metrics.get("max_generation"),
        "mean_selected_offspring_score": metrics.get("mean_selected_offspring_score"),
    }


def _readme_text(report: dict) -> str:
    metrics = report["metrics"]
    return (
        "# SLIP Multigeneration Lineage Runner Stage 0\n\n"
        "Lab-only persistent multigeneration lineage runner for current SLIP profiles.\n\n"
        "Key results:\n\n"
        f"- Profiles: {report['profile_count']}\n"
        f"- Successful multigeneration profiles: {report['multigeneration_success_count']}\n"
        f"- Total generation records: {report['total_generation_records']}\n"
        f"- Continued child count: {metrics['continued_child_count']}\n"
        f"- Max generation reached: {metrics['max_generation_reached']}\n"
        f"- Mean selected offspring score: {metrics['mean_selected_offspring_score']}\n"
        f"- Decision: {report['decision']}\n\n"
        "This artifact is still lab evidence, not package runtime integration "
        "or profile-weighted evolution.\n"
    )


def _grid_by_id(grids: list[dict], grid_id: str) -> dict:
    for grid in grids:
        if grid["grid_id"] == grid_id:
            return grid
    raise ValueError(f"grid not found: {grid_id}")


def _validation_failure(family: str, message: str) -> dict:
    return {
        "ok": False,
        "errors": [{"path": "multigeneration_lineage", "family": family, "message": message}],
        "error_families": [family],
    }


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _portable(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _mean_selected(records: list[dict], key: str) -> float:
    return _round(mean(record[key] for record in records)) if records else 0.0


def _mean_key(records: list[dict], key: str) -> float:
    values = [record[key] for record in records if record.get(key) is not None]
    return _round(mean(values)) if values else 0.0


def _mean_nested(records: list[dict], path: list[str]) -> float:
    values = []
    for record in records:
        cursor = record
        for key in path:
            cursor = cursor.get(key, {}) if isinstance(cursor, dict) else {}
        if isinstance(cursor, (int, float)):
            values.append(float(cursor))
    return _round(mean(values)) if values else 0.0


def _ratio(numerator: int | float, denominator: int | float) -> float:
    if denominator == 0:
        return 0.0
    return _round(float(numerator) / float(denominator))


def _round(value: int | float) -> float:
    return round(float(value), 6)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--profile",
        action="append",
        type=Path,
        default=None,
        help="Path to a valid SLIP profile. Repeat for multiple profiles.",
    )
    parser.add_argument("--generated-root", type=Path, default=DEFAULT_GENERATED_ROOT)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "data/workshop_editor/slip_multigeneration_lineage_runner_stage0",
    )
    parser.add_argument("--generations", type=int, default=3)
    parser.add_argument("--candidate-limit", type=int, default=12)
    parser.add_argument("--lifecycle-ticks", type=int, default=24)
    parser.add_argument("--rng-seed", type=int, default=20260513)
    args = parser.parse_args()
    profile_paths = args.profile or DEFAULT_PROFILE_PATHS
    report = run_slip_multigeneration_lineage_runner_lab(
        profile_paths,
        args.generated_root,
        generations=args.generations,
        candidate_limit=args.candidate_limit,
        lifecycle_ticks=args.lifecycle_ticks,
        rng_seed=args.rng_seed,
    )
    _write_json(REPORT_PATH, report)
    APP_DATA_PATH.write_text(
        "window.MECHAGOTCHI_SLIP_MULTIGENERATION_LINEAGE_RUNNER = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )
    write_slip_multigeneration_lineage_runner_artifacts(args.output_dir, report)
    print(json.dumps(report["metrics"], indent=2))


if __name__ == "__main__":
    main()
