import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parents[2]
WORKSHOP_DIR = ROOT / "labs" / "workshop_editor"
LIFECYCLE_DIR = ROOT / "labs" / "lifecycle_sim"
for path in [WORKSHOP_DIR, LIFECYCLE_DIR]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from lifecycle_sim import run_lifecycle_simulation  # noqa: E402
from slip_offspring_lineage_gate import (  # noqa: E402
    _build_offspring_candidates,
    _read_parent_grid,
    run_profile_offspring_lineage_probe,
)
from slip_preview_gates import (  # noqa: E402
    build_mutation_preview,
    validate_preview_request,
)


ARTIFACT_ID = "slip_long_horizon_behavior_gate_stage0"
REPORT_PATH = ROOT / "data/workshop_editor/slip_long_horizon_behavior_gate_stage0.json"
APP_DATA_PATH = ROOT / "data/workshop_editor/slip_long_horizon_behavior_gate_data.js"
DEFAULT_PROFILE_PATHS = [
    ROOT / "data/slips/valid/slip_lcd_seed.json",
    ROOT / "data/slips/valid/slip_gray_stable.json",
    ROOT / "data/slips/valid/slip_amber_social.json",
]
DEFAULT_GENERATED_ROOT = ROOT / "data/slips/multi_profile_generation_stage0"
DEFAULT_READABILITY_PATH = ROOT / "data/readability/readability_stage0.json"


def run_profile_long_horizon_probe(
    profile_path: Path,
    generated_root: Path,
    *,
    candidate_limit: int = 12,
    heldout_count: int = 6,
    short_ticks: int = 24,
    long_ticks: int = 96,
    rng_seed: int = 20260513,
    candidate_profile_id: str | None = None,
    profile_override: dict | None = None,
    probe_id: str | None = None,
    manual_readability_path: Path = DEFAULT_READABILITY_PATH,
) -> dict:
    profile = deepcopy(profile_override) if profile_override is not None else _read_json(profile_path)
    profile_id = profile.get("profile_id", "unknown_profile")
    corpus_profile_id = candidate_profile_id or profile_id
    result = {
        "probe_id": probe_id or f"{profile_id}_long_horizon_behavior_gate",
        "profile_id": profile_id,
        "profile_path": _portable(profile_path),
        "candidate_profile_id": corpus_profile_id,
        "candidate_limit": candidate_limit,
        "heldout_count": heldout_count,
        "short_horizon_ticks": short_ticks,
        "long_horizon_ticks": long_ticks,
        "gate_started": False,
    }

    offspring_probe = run_profile_offspring_lineage_probe(
        profile_path,
        generated_root,
        candidate_limit=candidate_limit,
        lifecycle_ticks=short_ticks,
        rng_seed=rng_seed,
        candidate_profile_id=corpus_profile_id,
        profile_override=profile,
        probe_id=f"{profile_id}_offspring_for_long_horizon_gate",
    )
    result["offspring_lineage"] = _compact_offspring_probe(offspring_probe)
    validation = offspring_probe.get("validation") or _validation_failure(
        "offspring_lineage_selection_failed",
        "offspring lineage probe did not produce a validation result",
    )
    result["validation"] = validation
    if not validation.get("ok") or not offspring_probe.get("gate_started"):
        return result

    result["gate_started"] = True
    parent_record = offspring_probe["runtime_parent"]
    parent_grid = _read_parent_grid(generated_root, corpus_profile_id, parent_record["grid_id"])
    mutation_preview = build_mutation_preview(profile, parent_grid)
    selected_grid = _selected_offspring_grid(
        profile,
        parent_grid,
        mutation_preview,
        offspring_probe["selected_offspring"]["grid_id"],
        rng_seed=rng_seed,
    )
    selected_validation = validate_preview_request(profile, selected_grid)
    result["validation"] = selected_validation
    if not selected_validation["ok"]:
        return result

    held_out_records = _held_out_records(
        profile,
        generated_root,
        corpus_profile_id,
        candidate_limit=candidate_limit,
        heldout_count=heldout_count,
        long_ticks=long_ticks,
        rng_seed=rng_seed + 1000,
    )
    held_out_summary = _held_out_summary(held_out_records, long_ticks)
    selected_switchboard = run_lifecycle_simulation(
        selected_grid,
        profile,
        ticks=long_ticks,
        policy="switchboard",
        rng_seed=rng_seed + 2000,
    )
    selected_idle = run_lifecycle_simulation(
        selected_grid,
        profile,
        ticks=long_ticks,
        policy="idle",
        rng_seed=rng_seed + 2001,
    )
    result.update(
        {
            "policy": {
                "policy_id": "long_horizon_behavior_gate_v0",
                "selected_offspring_source": "offspring_lineage_gate_v0",
                "held_out_source": "multi_profile_generation_stage0_after_parent_candidate_window",
                "comparison_policies": ["switchboard", "idle"],
                "full_horizon_scoring": "post_death_missing_ticks_count_as_zero_need_balance",
            },
            "selected_offspring_grid_id": selected_grid["grid_id"],
            "selected_offspring_long_horizon": {
                "switchboard": _runtime_summary(selected_switchboard),
                "idle": _runtime_summary(selected_idle),
                "need_balance_delta_vs_idle": _round(
                    selected_switchboard["need_balance"] - selected_idle["need_balance"]
                ),
            },
            "held_out_candidate_count": len(held_out_records),
            "held_out_candidates": held_out_records,
            "held_out_summary": held_out_summary,
            "manual_readability_calibration": _manual_readability_calibration(
                manual_readability_path
            ),
            "closed_policy_boundary": (
                "Stage 0 proves current selected offspring and held-out generated "
                "candidates survive the long switchboard horizon while neglect still "
                "fails; it does not collect human readability ratings or run a "
                "persistent multigeneration runtime."
            ),
        }
    )
    return result


def run_slip_long_horizon_behavior_gate_lab(
    profile_paths: list[Path],
    generated_root: Path,
    *,
    candidate_limit: int = 12,
    heldout_count: int = 6,
    short_ticks: int = 24,
    long_ticks: int = 96,
    rng_seed: int = 20260513,
    manual_readability_path: Path = DEFAULT_READABILITY_PATH,
) -> dict:
    profile_results = [
        run_profile_long_horizon_probe(
            profile_path,
            generated_root,
            candidate_limit=candidate_limit,
            heldout_count=heldout_count,
            short_ticks=short_ticks,
            long_ticks=long_ticks,
            rng_seed=rng_seed + index,
            manual_readability_path=manual_readability_path,
        )
        for index, profile_path in enumerate(profile_paths)
    ]
    invalid_probe_results = _invalid_long_horizon_probes(
        profile_paths,
        generated_root,
        candidate_limit=candidate_limit,
        heldout_count=heldout_count,
        short_ticks=short_ticks,
        long_ticks=long_ticks,
        rng_seed=rng_seed + 100,
        manual_readability_path=manual_readability_path,
    )
    successful_results = [
        result
        for result in profile_results
        if result.get("validation", {}).get("ok")
        and result.get("gate_started")
        and _selected_switchboard_full_survival(result, long_ticks)
        and result.get("held_out_summary", {}).get("switchboard_full_survival_count")
        == result.get("held_out_candidate_count", 0)
        and result.get("held_out_candidate_count", 0) == heldout_count
    ]
    invalid_rejected_count = sum(
        1
        for result in invalid_probe_results
        if not result.get("validation", {}).get("ok") and not result["gate_started"]
    )
    selected_switchboards = [
        result["selected_offspring_long_horizon"]["switchboard"]
        for result in successful_results
    ]
    selected_idles = [
        result["selected_offspring_long_horizon"]["idle"]
        for result in successful_results
    ]
    held_out_records = [
        record
        for result in successful_results
        for record in result.get("held_out_candidates", [])
    ]
    manual_statuses = [
        result.get("manual_readability_calibration", {})
        for result in profile_results
        if result.get("manual_readability_calibration")
    ]
    manual_ready = bool(manual_statuses) and all(
        status.get("ratings_collected") for status in manual_statuses
    )
    report = {
        "artifact_id": ARTIFACT_ID,
        "status": "research_slip_long_horizon_behavior_gate_no_package_code",
        "date": "2026-05-13",
        "purpose": (
            "Run held-out long-horizon behavior probes for current SLIP-selected "
            "offspring and generated candidates without claiming manual "
            "readability calibration or profile-weighted evolution."
        ),
        "source_artifacts": [
            "docs/01-brainstorming.md",
            "docs/02-research_plan.md",
            "research/slip/profile_compatibility_tests.md",
            "data/slips/slip_profile_compatibility_matrix_stage0.json",
            "research/experiment_reports/2026-05-13-slip-offspring-lineage-gate.md",
            "data/workshop_editor/slip_offspring_lineage_gate_stage0.json",
            "labs/workshop_editor/slip_offspring_lineage_gate.py",
            "labs/lifecycle_sim/lifecycle_sim.py",
            "data/readability/readability_stage0.json",
            "data/slips/multi_profile_generation_stage0/",
        ],
        "external_anchors": [
            {
                "source": "Avida Digital Evolution Platform",
                "url": "https://avida.devosoft.org/",
                "used_for": "Long-horizon behavior gates are treated as explicit experimental protocols over evolving digital artifacts.",
            },
            {
                "source": "JaxLife: An Open-Ended Agentic Simulator",
                "url": "https://arxiv.org/abs/2409.00853",
                "used_for": "Survival and emergent behavior are measured in an artificial-life simulator rather than inferred from static morphology.",
            },
            {
                "source": "Reinforcement Learning: An Introduction, second edition",
                "url": "https://mitpress.mit.edu/9780262039246/reinforcement-learning/",
                "used_for": "Switchboard-vs-idle comparison is framed as long-running agent-environment reward evidence.",
            },
        ],
        "profile_count": len(profile_results),
        "long_horizon_success_count": len(successful_results),
        "selected_offspring_full_survival_count": sum(
            1 for result in profile_results if _selected_switchboard_full_survival(result, long_ticks)
        ),
        "held_out_candidate_count": sum(
            result.get("held_out_candidate_count", 0) for result in profile_results
        ),
        "held_out_switchboard_full_survival_count": sum(
            result.get("held_out_summary", {}).get("switchboard_full_survival_count", 0)
            for result in profile_results
        ),
        "held_out_idle_death_count": sum(
            result.get("held_out_summary", {}).get("idle_death_count", 0)
            for result in profile_results
        ),
        "invalid_probe_count": len(invalid_probe_results),
        "invalid_probe_rejected_count": invalid_rejected_count,
        "parameters": {
            "candidate_limit": candidate_limit,
            "heldout_count": heldout_count,
            "short_ticks": short_ticks,
            "long_ticks": long_ticks,
            "rng_seed": rng_seed,
        },
        "metrics": {
            "long_horizon_success_rate": _ratio(
                len(successful_results),
                len(profile_results),
            ),
            "invalid_probe_rejection_rate": _ratio(
                invalid_rejected_count,
                len(invalid_probe_results),
            ),
            "mean_switchboard_survival_ratio": _mean_key(
                selected_switchboards,
                "survival_ratio",
            ),
            "mean_idle_survival_ratio": _mean_key(selected_idles, "survival_ratio"),
            "mean_switchboard_need_balance": _mean_key(
                selected_switchboards,
                "need_balance",
            ),
            "mean_idle_need_balance": _mean_key(selected_idles, "need_balance"),
            "mean_need_balance_delta_vs_idle": _round(
                _mean_key(selected_switchboards, "need_balance")
                - _mean_key(selected_idles, "need_balance")
            ),
            "mean_held_out_switchboard_survival_ratio": _mean_nested_records(
                held_out_records,
                ["switchboard", "survival_ratio"],
            ),
            "mean_held_out_idle_survival_ratio": _mean_nested_records(
                held_out_records,
                ["idle", "survival_ratio"],
            ),
            "long_horizon_behavior_tests_specified": (
                len(successful_results) == len(profile_results)
                and invalid_rejected_count == len(invalid_probe_results)
            ),
            "manual_readability_calibration_ready": manual_ready,
        },
        "profile_results": profile_results,
        "invalid_probe_results": invalid_probe_results,
        "closed_states": [
            "held_out_long_horizon_behavior_tests",
            "offspring_long_horizon_survival_probe",
            "invalid_profile_rejected_before_long_horizon",
        ],
        "blocked_states": [
            "runtime_jsonschema_validation",
            "declared_dependency_manifest",
            "profile_weighted_evolution",
            "package_runtime_lifecycle_integration",
            "manual_readability_calibration",
            "persistent_multigeneration_lineage_runner",
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
        "decision": "prototype_slip_long_horizon_behavior_gate",
        "next_research_step": (
            "Collect manual readability ratings and calibrate proxy readability "
            "thresholds before claiming profile-weighted evolution."
        ),
    }
    return report


def write_slip_long_horizon_behavior_gate_artifacts(
    output_dir: Path,
    report: dict,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / f"{ARTIFACT_ID}.json", report)
    for result in report["profile_results"]:
        if result.get("gate_started"):
            _write_json(
                output_dir / f"{result['profile_id']}_long_horizon_behavior_gate.json",
                result,
            )
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")
    (output_dir / "slip_long_horizon_behavior_gate_data.js").write_text(
        "window.MECHAGOTCHI_SLIP_LONG_HORIZON_BEHAVIOR_GATE = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )


def _selected_offspring_grid(
    profile: dict,
    parent_grid: dict,
    mutation_preview: dict,
    selected_grid_id: str,
    *,
    rng_seed: int,
) -> dict:
    for candidate in _build_offspring_candidates(
        profile,
        parent_grid,
        mutation_preview,
        rng_seed=rng_seed,
    ):
        if candidate["grid_id"] == selected_grid_id:
            return candidate
    raise ValueError(f"selected offspring grid was not reconstructed: {selected_grid_id}")


def _held_out_records(
    profile: dict,
    generated_root: Path,
    corpus_profile_id: str,
    *,
    candidate_limit: int,
    heldout_count: int,
    long_ticks: int,
    rng_seed: int,
) -> list[dict]:
    candidates = sorted((generated_root / corpus_profile_id).glob("*.json"))
    held_out_paths = candidates[candidate_limit : candidate_limit + heldout_count]
    records = []
    for index, path in enumerate(held_out_paths):
        grid = _read_json(path)
        validation = validate_preview_request(profile, grid)
        record = {
            "grid_id": grid.get("grid_id", path.stem),
            "path": _portable(path),
            "validation": validation,
        }
        if validation["ok"]:
            switchboard = run_lifecycle_simulation(
                grid,
                profile,
                ticks=long_ticks,
                policy="switchboard",
                rng_seed=rng_seed + index * 2,
            )
            idle = run_lifecycle_simulation(
                grid,
                profile,
                ticks=long_ticks,
                policy="idle",
                rng_seed=rng_seed + index * 2 + 1,
            )
            record.update(
                {
                    "switchboard": _runtime_summary(switchboard),
                    "idle": _runtime_summary(idle),
                    "need_balance_delta_vs_idle": _round(
                        switchboard["need_balance"] - idle["need_balance"]
                    ),
                }
            )
        records.append(record)
    return records


def _held_out_summary(records: list[dict], long_ticks: int) -> dict:
    valid = [
        record
        for record in records
        if record.get("validation", {}).get("ok")
        and "switchboard" in record
        and "idle" in record
    ]
    switchboard = [record["switchboard"] for record in valid]
    idle = [record["idle"] for record in valid]
    return {
        "candidate_count": len(records),
        "valid_candidate_count": len(valid),
        "switchboard_full_survival_count": sum(
            1 for record in switchboard if record["survival_ticks"] == long_ticks
        ),
        "idle_death_count": sum(
            1 for record in idle if record["survival_ticks"] < long_ticks
        ),
        "mean_switchboard_survival_ratio": _mean_key(
            switchboard,
            "survival_ratio",
        ),
        "mean_idle_survival_ratio": _mean_key(idle, "survival_ratio"),
        "mean_switchboard_need_balance": _mean_key(switchboard, "need_balance"),
        "mean_idle_need_balance": _mean_key(idle, "need_balance"),
        "mean_need_balance_delta_vs_idle": _round(
            _mean_key(switchboard, "need_balance")
            - _mean_key(idle, "need_balance")
        ),
    }


def _manual_readability_calibration(path: Path) -> dict:
    if not path.exists():
        return {
            "status": "missing",
            "ratings_collected": False,
            "human_rating_count": 0,
            "source_path": _portable(path),
            "proxy_only": True,
            "blocks_profile_weighted_evolution": True,
        }
    payload = _read_json(path)
    samples = payload.get("samples", [])
    human_rating_count = sum(
        1
        for sample in samples
        if sample.get("manual_rating") is not None
        or sample.get("readability", {}).get("human_readability_rating") is not None
    )
    protocol = payload.get("manual_rating_protocol", {})
    ratings_collected = bool(protocol.get("ratings_collected")) and human_rating_count > 0
    return {
        "status": "collected" if ratings_collected else "not_collected",
        "ratings_collected": ratings_collected,
        "human_rating_count": human_rating_count,
        "minimum_reviewers": protocol.get("minimum_reviewers"),
        "protocol_status": protocol.get("status"),
        "source_path": _portable(path),
        "proxy_only": not ratings_collected,
        "blocks_profile_weighted_evolution": not ratings_collected,
    }


def _invalid_long_horizon_probes(
    profile_paths: list[Path],
    generated_root: Path,
    *,
    candidate_limit: int,
    heldout_count: int,
    short_ticks: int,
    long_ticks: int,
    rng_seed: int,
    manual_readability_path: Path,
) -> list[dict]:
    profile = _read_json(profile_paths[0])
    unsupported_version = deepcopy(profile)
    unsupported_version["slip_version"] = "9.9.9"
    return [
        run_profile_long_horizon_probe(
            profile_paths[0],
            generated_root,
            candidate_limit=candidate_limit,
            heldout_count=heldout_count,
            short_ticks=short_ticks,
            long_ticks=long_ticks,
            rng_seed=rng_seed,
            profile_override=unsupported_version,
            probe_id="unsupported_version_rejected_before_long_horizon",
            manual_readability_path=manual_readability_path,
        ),
        run_profile_long_horizon_probe(
            profile_paths[0],
            generated_root,
            candidate_limit=candidate_limit,
            heldout_count=heldout_count,
            short_ticks=short_ticks,
            long_ticks=long_ticks,
            rng_seed=rng_seed + 1,
            candidate_profile_id="slip_gray_stable",
            probe_id="mismatched_candidate_corpus_rejected_before_long_horizon",
            manual_readability_path=manual_readability_path,
        ),
    ]


def _compact_offspring_probe(offspring_probe: dict) -> dict:
    selected = offspring_probe.get("selected_offspring")
    decision = offspring_probe.get("lineage_decision")
    return {
        "probe_id": offspring_probe.get("probe_id"),
        "profile_id": offspring_probe.get("profile_id"),
        "gate_started": offspring_probe.get("gate_started", False),
        "validation_ok": offspring_probe.get("validation", {}).get("ok", False),
        "runtime_parent_grid_id": offspring_probe.get("runtime_parent", {}).get("grid_id"),
        "selected_offspring_grid_id": selected.get("grid_id") if isinstance(selected, dict) else None,
        "selected_offspring_score": selected.get("offspring_score") if isinstance(selected, dict) else None,
        "lineage_action": decision.get("action") if isinstance(decision, dict) else None,
    }


def _runtime_summary(runtime: dict) -> dict:
    return {
        "policy": runtime["policy"],
        "ticks_requested": runtime["ticks_requested"],
        "survival_ticks": runtime["survival_ticks"],
        "survival_ratio": _ratio(runtime["survival_ticks"], runtime["ticks_requested"]),
        "alive": runtime["alive"],
        "death_cause": runtime["death_cause"],
        "need_balance": runtime["need_balance"],
        "recovery_events": runtime["recovery_events"],
        "action_counts": runtime["action_counts"],
        "final_state": {
            "hunger": _round(runtime["final_state"].get("hunger", 0)),
            "energy": _round(runtime["final_state"].get("energy", 0)),
            "stress": _round(runtime["final_state"].get("stress", 0)),
            "bond": _round(runtime["final_state"].get("bond", 0)),
            "grid_stability": _round(runtime["final_state"].get("grid_stability", 0)),
        },
    }


def _selected_switchboard_full_survival(result: dict, long_ticks: int) -> bool:
    switchboard = result.get("selected_offspring_long_horizon", {}).get("switchboard", {})
    return switchboard.get("survival_ticks") == long_ticks


def _app_payload(report: dict) -> dict:
    return {
        "artifact_id": report["artifact_id"],
        "status": report["status"],
        "date": report["date"],
        "metrics": report["metrics"],
        "profile_results": [
            _compact_profile_result(result) for result in report["profile_results"]
        ],
        "closed_states": report["closed_states"],
        "blocked_states": report["blocked_states"],
        "decision": report["decision"],
        "next_research_step": report["next_research_step"],
    }


def _compact_profile_result(result: dict) -> dict:
    selected = result.get("selected_offspring_long_horizon", {})
    held_out = result.get("held_out_summary", {})
    return {
        "profile_id": result["profile_id"],
        "gate_started": result.get("gate_started", False),
        "validation_ok": result.get("validation", {}).get("ok", False),
        "selected_offspring_grid_id": result.get("selected_offspring_grid_id"),
        "selected_switchboard_survival_ratio": selected.get("switchboard", {}).get(
            "survival_ratio"
        ),
        "selected_idle_survival_ratio": selected.get("idle", {}).get("survival_ratio"),
        "held_out_candidate_count": result.get("held_out_candidate_count"),
        "held_out_switchboard_full_survival_count": held_out.get(
            "switchboard_full_survival_count"
        ),
        "held_out_idle_death_count": held_out.get("idle_death_count"),
        "manual_readability_status": result.get("manual_readability_calibration", {}).get(
            "status"
        ),
    }


def _readme_text(report: dict) -> str:
    metrics = report["metrics"]
    return (
        "# SLIP Long-Horizon Behavior Gate Stage 0\n\n"
        "Held-out long-horizon switchboard-vs-idle behavior evidence.\n\n"
        f"- Profiles: {report['profile_count']}\n"
        f"- Long-horizon successes: {report['long_horizon_success_count']}\n"
        f"- Selected offspring full-survival count: {report['selected_offspring_full_survival_count']}\n"
        f"- Held-out candidates: {report['held_out_candidate_count']}\n"
        f"- Held-out switchboard full survival: {report['held_out_switchboard_full_survival_count']}\n"
        f"- Held-out idle deaths: {report['held_out_idle_death_count']}\n"
        f"- Mean switchboard survival ratio: {metrics['mean_switchboard_survival_ratio']}\n"
        f"- Mean idle survival ratio: {metrics['mean_idle_survival_ratio']}\n"
        f"- Manual readability calibration ready: {metrics['manual_readability_calibration_ready']}\n"
    )


def _validation_failure(family: str, message: str) -> dict:
    return {
        "ok": False,
        "errors": [{"path": "long_horizon", "family": family, "message": message}],
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


def _mean_key(records: list[dict], key: str) -> float:
    if not records:
        return 0.0
    return _round(mean(float(record[key]) for record in records))


def _mean_nested_records(records: list[dict], path: list[str]) -> float:
    if not records:
        return 0.0
    values = []
    for record in records:
        cursor = record
        for key in path:
            cursor = cursor[key]
        values.append(float(cursor))
    return _round(mean(values))


def _ratio(numerator: int | float, denominator: int | float) -> float:
    if denominator == 0:
        return 0.0
    return _round(numerator / denominator)


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
    parser.add_argument(
        "--generated-root",
        type=Path,
        default=DEFAULT_GENERATED_ROOT,
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "data/workshop_editor/slip_long_horizon_behavior_gate_stage0",
    )
    parser.add_argument("--candidate-limit", type=int, default=12)
    parser.add_argument("--heldout-count", type=int, default=6)
    parser.add_argument("--short-ticks", type=int, default=24)
    parser.add_argument("--long-ticks", type=int, default=96)
    parser.add_argument("--rng-seed", type=int, default=20260513)
    args = parser.parse_args()
    profile_paths = args.profile or DEFAULT_PROFILE_PATHS
    report = run_slip_long_horizon_behavior_gate_lab(
        profile_paths,
        args.generated_root,
        candidate_limit=args.candidate_limit,
        heldout_count=args.heldout_count,
        short_ticks=args.short_ticks,
        long_ticks=args.long_ticks,
        rng_seed=args.rng_seed,
    )
    _write_json(REPORT_PATH, report)
    APP_DATA_PATH.write_text(
        "window.MECHAGOTCHI_SLIP_LONG_HORIZON_BEHAVIOR_GATE = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )
    write_slip_long_horizon_behavior_gate_artifacts(args.output_dir, report)


if __name__ == "__main__":
    main()
