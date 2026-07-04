import argparse
import json
import sys
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parents[2]
WORKSHOP_DIR = ROOT / "labs" / "workshop_editor"
LIFECYCLE_DIR = ROOT / "labs" / "lifecycle_sim"
MAP_ELITES_DIR = ROOT / "labs" / "map_elites_archive"
for path in [WORKSHOP_DIR, LIFECYCLE_DIR, MAP_ELITES_DIR]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from extended_descriptors import (  # noqa: E402
    extended_descriptor_for_grid,
    score_extended_candidate,
)
from lifecycle_sim import run_lifecycle_simulation  # noqa: E402
from slip_preview_gates import (  # noqa: E402
    build_mutation_preview,
    validate_preview_request,
)
from slip_runtime_selection_policy import run_profile_runtime_selection_probe  # noqa: E402


ARTIFACT_ID = "slip_offspring_lineage_gate_stage0"
REPORT_PATH = Path("data/workshop_editor/slip_offspring_lineage_gate_stage0.json")
APP_DATA_PATH = Path("data/workshop_editor/slip_offspring_lineage_gate_data.js")
DEFAULT_PROFILE_PATHS = [
    Path("data/slips/valid/slip_lcd_seed.json"),
    Path("data/slips/valid/slip_gray_stable.json"),
    Path("data/slips/valid/slip_amber_social.json"),
]
DEFAULT_GENERATED_ROOT = Path("data/slips/multi_profile_generation_stage0")


def run_profile_offspring_lineage_probe(
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
    result = {
        "probe_id": probe_id or f"{profile_id}_offspring_lineage_gate",
        "profile_id": profile_id,
        "profile_path": _portable(profile_path),
        "candidate_profile_id": corpus_profile_id,
        "candidate_limit": candidate_limit,
        "lifecycle_ticks": lifecycle_ticks,
        "gate_started": False,
    }

    runtime_probe = run_profile_runtime_selection_probe(
        profile_path,
        generated_root,
        candidate_limit=candidate_limit,
        lifecycle_ticks=lifecycle_ticks,
        rng_seed=rng_seed,
        candidate_profile_id=corpus_profile_id,
        profile_override=profile,
        probe_id=f"{profile_id}_runtime_parent_for_offspring_gate",
    )
    result["runtime_selection"] = _compact_runtime_probe(runtime_probe)
    validation = runtime_probe.get("validation") or _validation_failure(
        "runtime_parent_selection_failed",
        "runtime selection did not produce a validation result",
    )
    result["validation"] = validation
    if not validation.get("ok") or not runtime_probe.get("selection_started"):
        return result

    parent_record = runtime_probe["selected"]
    parent_grid = _read_parent_grid(generated_root, corpus_profile_id, parent_record["grid_id"])
    parent_validation = validate_preview_request(profile, parent_grid)
    result["validation"] = parent_validation
    if not parent_validation["ok"]:
        return result

    result["gate_started"] = True
    mutation_preview = build_mutation_preview(profile, parent_grid)
    offspring_grids = _build_offspring_candidates(
        profile,
        parent_grid,
        mutation_preview,
        rng_seed=rng_seed,
    )
    offspring_records = _evaluate_offspring_candidates(
        profile,
        offspring_grids,
        parent_record,
        runtime_probe,
        mutation_preview,
        lifecycle_ticks=lifecycle_ticks,
        rng_seed=rng_seed,
    )
    selected = max(
        offspring_records,
        key=lambda record: (
            record["offspring_score"],
            record["extended_score"]["fitness"],
            record["grid_id"],
        ),
    )
    lineage_decision = _lineage_decision(parent_record, selected, runtime_probe)
    result.update(
        {
            "policy": {
                "policy_id": "offspring_lineage_gate_v0",
                "parent_selection_policy": "profile_weighted_archive_elite_v0",
                "offspring_mutation_policy": "bounded_stage0_grid_mutation_from_slip_caps",
                "lineage_policy": "replace_only_if_child_beats_parent_or_opens_qualified_niche",
            },
            "runtime_parent": _runtime_parent(parent_grid, parent_record),
            "mutation_preview": mutation_preview,
            "offspring_candidate_count": len(offspring_records),
            "offspring_candidates": offspring_records,
            "selected_offspring": selected,
            "mutation_gate": _mutation_gate(mutation_preview, offspring_records, selected),
            "lineage_decision": lineage_decision,
            "closed_policy_boundary": (
                "Stage 0 selects bounded offspring and emits a lineage decision; "
                "it still does not run persistent multigeneration evolution."
            ),
        }
    )
    return result


def run_slip_offspring_lineage_gate_lab(
    profile_paths: list[Path],
    generated_root: Path,
    *,
    candidate_limit: int = 12,
    lifecycle_ticks: int = 24,
    rng_seed: int = 20260513,
) -> dict:
    profile_results = [
        run_profile_offspring_lineage_probe(
            profile_path,
            generated_root,
            candidate_limit=candidate_limit,
            lifecycle_ticks=lifecycle_ticks,
            rng_seed=rng_seed + index,
        )
        for index, profile_path in enumerate(profile_paths)
    ]
    invalid_probe_results = _invalid_offspring_lineage_probes(
        profile_paths,
        generated_root,
        candidate_limit=candidate_limit,
        lifecycle_ticks=lifecycle_ticks,
        rng_seed=rng_seed + 100,
    )
    successful_results = [
        result
        for result in profile_results
        if result.get("validation", {}).get("ok")
        and result.get("gate_started")
        and result.get("mutation_gate", {}).get("selected_offspring_valid")
        and result.get("mutation_gate", {}).get("selected_offspring_aligned")
    ]
    selected_offspring = [result["selected_offspring"] for result in successful_results]
    lineage_decisions = [result["lineage_decision"] for result in successful_results]
    invalid_rejected_count = sum(
        1
        for result in invalid_probe_results
        if not result.get("validation", {}).get("ok") and not result["gate_started"]
    )
    report = {
        "artifact_id": ARTIFACT_ID,
        "status": "research_slip_offspring_lineage_gate_no_package_code",
        "date": "2026-05-13",
        "purpose": (
            "Specify and test bounded Stage 0 offspring mutation selection and "
            "lineage replacement decisions after runtime lifecycle/archive parent "
            "selection, without claiming persistent profile-weighted evolution."
        ),
        "source_artifacts": [
            "docs/01-brainstorming.md",
            "docs/02-research_plan.md",
            "research/slip/profile_compatibility_tests.md",
            "data/slips/slip_profile_compatibility_matrix_stage0.json",
            "research/experiment_reports/2026-05-13-slip-runtime-selection-policy.md",
            "data/workshop_editor/slip_runtime_selection_policy_stage0.json",
            "labs/workshop_editor/slip_runtime_selection_policy.py",
            "labs/workshop_editor/slip_preview_gates.py",
            "labs/lifecycle_sim/lifecycle_sim.py",
            "labs/map_elites_archive/extended_descriptors.py",
            "data/slips/multi_profile_generation_stage0/",
        ],
        "external_anchors": [
            {
                "source": "Illuminating search spaces by mapping elites",
                "url": "https://arxiv.org/abs/1504.04909",
                "used_for": "Lineage replacement is evaluated against archive niches instead of scalar top-k alone.",
            },
            {
                "source": "Essentials of Metaheuristics",
                "url": "https://people.cs.gmu.edu/~sean/book/metaheuristics/",
                "used_for": "Offspring mutation and replacement are treated as evolutionary operators that need explicit gates.",
            },
            {
                "source": "Introduction to Evolutionary Computing online accompaniment",
                "url": "https://www.evolutionarycomputation.org/part-one/fitness-selection-and-population-management/",
                "used_for": "Survivor selection and replacement are kept separate from parent selection.",
            },
        ],
        "profile_count": len(profile_results),
        "offspring_gate_success_count": len(successful_results),
        "lineage_decision_count": len(lineage_decisions),
        "offspring_candidate_count": sum(
            result.get("offspring_candidate_count", 0) for result in profile_results
        ),
        "invalid_probe_count": len(invalid_probe_results),
        "invalid_probe_rejected_count": invalid_rejected_count,
        "parameters": {
            "candidate_limit": candidate_limit,
            "lifecycle_ticks": lifecycle_ticks,
            "rng_seed": rng_seed,
        },
        "metrics": {
            "offspring_gate_success_rate": _ratio(
                len(successful_results),
                len(profile_results),
            ),
            "invalid_probe_rejection_rate": _ratio(
                invalid_rejected_count,
                len(invalid_probe_results),
            ),
            "mean_selected_offspring_score": _mean_selected(
                selected_offspring,
                "offspring_score",
            ),
            "mean_selected_offspring_need_balance": _mean_nested(
                selected_offspring,
                ["runtime_episode", "need_balance"],
            ),
            "mean_selected_offspring_survival_ratio": _mean_nested(
                selected_offspring,
                ["runtime_episode", "survival_ratio"],
            ),
            "distinct_selected_offspring_ids": _distinct_count(
                record["grid_id"] for record in selected_offspring
            ),
            "distinct_selected_offspring_niches": _distinct_count(
                record["archive_niche"] for record in selected_offspring
            ),
            "replace_parent_count": _decision_count(lineage_decisions, "replace_parent"),
            "add_archive_niche_count": _decision_count(lineage_decisions, "add_archive_niche"),
            "hold_parent_count": _decision_count(lineage_decisions, "hold_parent"),
            "offspring_mutation_selection_specified": (
                len(successful_results) == len(profile_results)
                and invalid_rejected_count == len(invalid_probe_results)
            ),
            "lineage_replacement_policy_specified": (
                len(lineage_decisions) == len(successful_results)
                and all(decision.get("action") for decision in lineage_decisions)
            ),
        },
        "profile_results": profile_results,
        "invalid_probe_results": invalid_probe_results,
        "closed_states": [
            "offspring_mutation_selection",
            "lineage_replacement_policy",
            "invalid_profile_rejected_before_offspring_lineage",
            "runtime_parent_to_offspring_selection_trace",
        ],
        "blocked_states": [
            "runtime_jsonschema_validation",
            "declared_dependency_manifest",
            "profile_weighted_evolution",
            "package_runtime_lifecycle_integration",
            "held_out_long_horizon_behavior_tests",
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
        "decision": "prototype_slip_offspring_lineage_gate",
        "next_research_step": (
            "Run held-out long-horizon behavior tests and manual readability "
            "calibration before claiming profile-weighted evolution."
        ),
    }
    return report


def write_slip_offspring_lineage_gate_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / f"{ARTIFACT_ID}.json", report)
    for result in report["profile_results"]:
        if result.get("gate_started"):
            _write_json(
                output_dir / f"{result['profile_id']}_offspring_lineage_gate.json",
                result,
            )
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")
    (output_dir / "slip_offspring_lineage_gate_data.js").write_text(
        "window.MECHAGOTCHI_SLIP_OFFSPRING_LINEAGE_GATE = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )


def _build_offspring_candidates(
    profile: dict,
    parent_grid: dict,
    mutation_preview: dict,
    *,
    rng_seed: int,
) -> list[dict]:
    builders = [
        _offspring_core_growth,
        _offspring_stability_tune,
        _offspring_expression_tune,
    ]
    candidates = []
    for index, builder in enumerate(builders):
        candidates.append(builder(profile, parent_grid, mutation_preview, rng_seed + index))
    return candidates


def _offspring_core_growth(
    profile: dict,
    parent_grid: dict,
    mutation_preview: dict,
    rng_seed: int,
) -> dict:
    child = _offspring_base(parent_grid, "core_growth", "offspring_core_growth")
    max_body_mass = int(profile["grid"]["body_mass_max"])
    current_body_mass = sum(1 for cell in child.get("cells", []) if cell.get("organ") == "core")
    cell_budget = mutation_preview["budgets"]["cell_mutation_budget_cap"]
    point = _first_open_core_neighbor(child, offset=rng_seed)
    if point is not None and current_body_mass < max_body_mass and cell_budget >= 1:
        x, y = point
        visual = _body_visual(child)
        cell = {
            "x": x,
            "y": y,
            "visual": visual,
            "role": "body",
            "material": "hard",
            "mutation_weight": _round(min(1.0, _mean_cell_weight(child) + 0.03)),
            "animation_anchor": False,
            "organ": "core",
            "stress": 0,
            "damage": 0,
            "locked": False,
        }
        child.setdefault("cells", []).append(cell)
        child["organs"]["core"]["cells"].append([x, y])
        child["_mutation_delta"] = {
            "cell_mutation_count": 1,
            "organ_shift_count": 0,
            "palette_shift_count": 0,
            "symmetry_break_count": _symmetry_break_delta(parent_grid, child),
            "changed_cells": [[x, y]],
        }
    else:
        _tune_first_mutable_cell(child, -0.02)
        child["_mutation_delta"] = {
            "cell_mutation_count": 1,
            "organ_shift_count": 0,
            "palette_shift_count": 0,
            "symmetry_break_count": 0,
            "changed_cells": [_first_mutable_coordinate(child)],
        }
    _scale_mutation_rates(child, profile, 0.9)
    return _strip_private(child)


def _offspring_stability_tune(
    profile: dict,
    parent_grid: dict,
    mutation_preview: dict,
    rng_seed: int,
) -> dict:
    child = _offspring_base(parent_grid, "stability_tune", "offspring_stability_tune")
    _tune_first_mutable_cell(child, -0.03)
    _scale_mutation_rates(child, profile, 0.75)
    child["_mutation_delta"] = {
        "cell_mutation_count": 1 if mutation_preview["budgets"]["cell_mutation_budget_cap"] >= 1 else 0,
        "organ_shift_count": 0,
        "palette_shift_count": 0,
        "symmetry_break_count": 0,
        "changed_cells": [_first_mutable_coordinate(child)],
    }
    return _strip_private(child)


def _offspring_expression_tune(
    profile: dict,
    parent_grid: dict,
    mutation_preview: dict,
    rng_seed: int,
) -> dict:
    child = _offspring_base(parent_grid, "expression_tune", "offspring_expression_tune")
    candidates = [
        cell
        for cell in child.get("cells", [])
        if cell.get("organ") in {"expression", "sensors"} and not cell.get("locked", False)
    ]
    target = candidates[0] if candidates else next(
        (cell for cell in child.get("cells", []) if not cell.get("locked", False)),
        None,
    )
    changed = []
    if target is not None:
        target["mutation_weight"] = _round(min(1.0, float(target.get("mutation_weight", 0)) + 0.04))
        colors = child.get("palette", {}).get("colors", [])
        if len(colors) > 2:
            target["visual"] = colors[2]
        changed.append([target["x"], target["y"]])
    _scale_mutation_rates(child, profile, 1.0)
    child["_mutation_delta"] = {
        "cell_mutation_count": 1 if changed else 0,
        "organ_shift_count": 0,
        "palette_shift_count": 0,
        "symmetry_break_count": 0,
        "changed_cells": changed,
    }
    return _strip_private(child)


def _offspring_grid_id(parent_id: str, variant_id: str) -> str:
    # grid_id must match the schema pattern ^[a-z0-9][a-z0-9_-]{2,63}$ (64
    # chars max). Multigeneration runs compound "_offspring_<variant>" per
    # generation, so long ids are compressed deterministically: the ancestry
    # stays in lineage.ancestor_ids, the id keeps a stable hashed suffix.
    candidate = f"{parent_id}_offspring_{variant_id}"
    if len(candidate) <= 64:
        return candidate
    digest = sha256(candidate.encode("utf-8")).hexdigest()[:10]
    prefix = candidate[: 64 - 1 - len(digest)].rstrip("_-")
    return f"{prefix}_{digest}"


def _offspring_base(parent_grid: dict, variant_id: str, event_id: str) -> dict:
    parent_id = parent_grid["grid_id"]
    child = deepcopy(parent_grid)
    child["grid_id"] = _offspring_grid_id(parent_id, variant_id)
    child["parent_grid_id"] = parent_id
    parent_lineage = parent_grid.get("lineage", {})
    parent_generation = int(parent_lineage.get("generation", 0))
    ancestors = list(parent_lineage.get("ancestor_ids", []))
    if parent_id not in ancestors:
        ancestors.append(parent_id)
    events = list(parent_lineage.get("mutation_events", []))
    events.append(event_id)
    child["lineage"] = {
        "generation": parent_generation + 1,
        "ancestor_ids": ancestors,
        "mutation_events": events,
    }
    metadata = deepcopy(child.get("metadata", {}))
    metadata.update(
        {
            "source": "slip_offspring_lineage_gate",
            "parent_grid_id": parent_id,
            "offspring_variant": variant_id,
        }
    )
    child["metadata"] = metadata
    return child


def _evaluate_offspring_candidates(
    profile: dict,
    offspring_grids: list[dict],
    parent_record: dict,
    runtime_probe: dict,
    mutation_preview: dict,
    *,
    lifecycle_ticks: int,
    rng_seed: int,
) -> list[dict]:
    records = []
    existing_niches = {
        record["archive_niche"] for record in runtime_probe.get("candidate_records", [])
    }
    for index, grid in enumerate(offspring_grids):
        validation = validate_preview_request(profile, grid)
        descriptor = extended_descriptor_for_grid(
            grid,
            slip_profile=profile,
            lifecycle_ticks=lifecycle_ticks,
            rng_seed=rng_seed + 200 + index,
        )
        extended_score = score_extended_candidate(
            grid,
            slip_profile=profile,
            lifecycle_ticks=lifecycle_ticks,
            rng_seed=rng_seed + 400 + index,
        )
        runtime = run_lifecycle_simulation(
            grid,
            profile,
            ticks=lifecycle_ticks,
            policy="switchboard",
            rng_seed=rng_seed + 600 + index,
        )
        delta = grid.get("mutation_delta", {})
        cap_compliance = _cap_compliance(delta, mutation_preview)
        components = _offspring_components(
            parent_record,
            descriptor,
            extended_score,
            runtime,
            validation,
            cap_compliance,
            existing_niches,
        )
        weights = _offspring_weights(profile)
        record = {
            "grid_id": grid["grid_id"],
            "parent_grid_id": grid["parent_grid_id"],
            "lineage": grid["lineage"],
            "archive_niche": descriptor["key"],
            "parent_archive_niche": parent_record["archive_niche"],
            "opens_new_archive_niche": descriptor["key"] not in existing_niches,
            "offspring_score": _weighted_average(components, weights),
            "components": components,
            "component_weights": weights,
            "runtime_episode": _runtime_summary(runtime, lifecycle_ticks),
            "descriptor_metrics": descriptor["metrics"],
            "extended_score": {
                "fitness": extended_score["fitness"],
                "components": extended_score["components"],
            },
            "mutation_delta": delta,
            "cap_compliance": cap_compliance,
            "validation": validation,
        }
        records.append(record)
    return sorted(
        records,
        key=lambda record: (
            record["offspring_score"],
            record["extended_score"]["fitness"],
            record["grid_id"],
        ),
        reverse=True,
    )


def _offspring_components(
    parent_record: dict,
    descriptor: dict,
    extended_score: dict,
    runtime: dict,
    validation: dict,
    cap_compliance: dict,
    existing_niches: set[str],
) -> dict:
    parent_score = parent_record["selection_score"]
    child_fitness = extended_score["fitness"]
    novelty = 1.0 if descriptor["key"] not in existing_niches else 0.55
    parent_delta = _clamp(0.5 + (child_fitness - parent_record["archive_fitness"]))
    return {
        "survival_ratio": _ratio(runtime["survival_ticks"], runtime["ticks_requested"]),
        "need_balance": _clamp(runtime["need_balance"]),
        "bond": _clamp(runtime["final_state"].get("bond", 0)),
        "archive_fitness": _clamp(child_fitness),
        "parent_score_continuity": _clamp(1.0 - max(0.0, parent_score - child_fitness)),
        "qualified_novelty": novelty,
        "mutation_budget_compliance": 1.0 if cap_compliance["caps_respected"] else 0.0,
        "validity": 1.0 if validation["ok"] else 0.0,
        "slip_alignment": 1.0 if validation.get("alignment", {}).get("ok") else 0.0,
        "parent_archive_delta": parent_delta,
    }


def _offspring_weights(profile: dict) -> dict[str, float]:
    survival = profile["survival_weights"]
    behavior = profile["behavior"]
    stability = _clamp(survival["stability"])
    novelty = _clamp(survival["novelty"])
    bond = _clamp(survival["bond"])
    curiosity = _clamp(behavior["curiosity"])
    neediness = _clamp(behavior["neediness"])
    return {
        "survival_ratio": 0.55 + stability * 0.25,
        "need_balance": 0.35 + neediness * 0.15,
        "bond": 0.25 + bond * 0.2,
        "archive_fitness": 0.35,
        "parent_score_continuity": 0.3 + stability * 0.15,
        "qualified_novelty": 0.25 + novelty * 0.25 + curiosity * 0.1,
        "mutation_budget_compliance": 0.5,
        "validity": 0.55,
        "slip_alignment": 0.55,
        "parent_archive_delta": 0.2,
    }


def _lineage_decision(parent_record: dict, selected: dict, runtime_probe: dict) -> dict:
    parent_score = parent_record["selection_score"]
    child_score = selected["offspring_score"]
    score_delta = _round(child_score - parent_score)
    qualified = (
        selected["validation"]["ok"]
        and selected["cap_compliance"]["caps_respected"]
        and selected["runtime_episode"]["survival_ratio"] >= 1.0
    )
    if qualified and selected["archive_niche"] == parent_record["archive_niche"] and score_delta >= 0.005:
        action = "replace_parent"
        reason = "child beats parent in the same archive niche"
    elif qualified and selected["opens_new_archive_niche"] and child_score >= parent_score - 0.05:
        action = "add_archive_niche"
        reason = "child opens a qualified archive niche without displacing parent"
    else:
        action = "hold_parent"
        reason = "parent remains elite until child beats replacement threshold"
    return {
        "action": action,
        "reason": reason,
        "parent_grid_id": parent_record["grid_id"],
        "offspring_grid_id": selected["grid_id"],
        "parent_archive_niche": parent_record["archive_niche"],
        "offspring_archive_niche": selected["archive_niche"],
        "parent_selection_score": parent_score,
        "offspring_score": selected["offspring_score"],
        "score_delta": score_delta,
        "qualified_for_lineage": qualified,
        "replacement_threshold": 0.005,
        "existing_archive_niche_count": len(
            {record["archive_niche"] for record in runtime_probe.get("candidate_records", [])}
        ),
    }


def _mutation_gate(
    mutation_preview: dict,
    offspring_records: list[dict],
    selected: dict,
) -> dict:
    return {
        "profile_id": mutation_preview["profile_id"],
        "parent_grid_id": mutation_preview["grid_id"],
        "candidate_count": len(offspring_records),
        "budgets": mutation_preview["budgets"],
        "caps": mutation_preview["caps"],
        "caps_respected": all(
            record["cap_compliance"]["caps_respected"] for record in offspring_records
        ),
        "selected_offspring_id": selected["grid_id"],
        "selected_offspring_valid": selected["validation"]["ok"],
        "selected_offspring_aligned": selected["validation"]["alignment"]["ok"],
        "selection_rule": (
            "rank by bounded offspring score over survival, need balance, bond, "
            "archive fitness, novelty, parent continuity, cap compliance, "
            "validity, and SLIP alignment"
        ),
    }


def _cap_compliance(delta: dict, mutation_preview: dict) -> dict:
    budgets = mutation_preview["budgets"]
    checks = {
        "cell_mutation_count_within_cap": delta.get("cell_mutation_count", 0)
        <= budgets["cell_mutation_budget_cap"],
        "organ_shift_count_within_cap": delta.get("organ_shift_count", 0)
        <= budgets["organ_shift_budget_cap"],
        "symmetry_break_count_within_cap": delta.get("symmetry_break_count", 0)
        <= budgets["symmetry_break_budget_cap"],
        "palette_shift_count_within_cap": delta.get("palette_shift_count", 0)
        <= (1 if mutation_preview["palette_shift"]["allowed"] else 0),
    }
    return {
        "checks": checks,
        "caps_respected": all(checks.values()),
    }


def _invalid_offspring_lineage_probes(
    profile_paths: list[Path],
    generated_root: Path,
    *,
    candidate_limit: int,
    lifecycle_ticks: int,
    rng_seed: int,
) -> list[dict]:
    profile = _read_json(profile_paths[0])
    unsupported_version = deepcopy(profile)
    unsupported_version["slip_version"] = "9.9.9"
    return [
        run_profile_offspring_lineage_probe(
            profile_paths[0],
            generated_root,
            candidate_limit=candidate_limit,
            lifecycle_ticks=lifecycle_ticks,
            rng_seed=rng_seed,
            profile_override=unsupported_version,
            probe_id="unsupported_version_rejected_before_offspring_lineage",
        ),
        run_profile_offspring_lineage_probe(
            profile_paths[0],
            generated_root,
            candidate_limit=candidate_limit,
            lifecycle_ticks=lifecycle_ticks,
            rng_seed=rng_seed + 1,
            candidate_profile_id="slip_gray_stable",
            probe_id="mismatched_candidate_corpus_rejected_before_offspring_lineage",
        ),
    ]


def _runtime_parent(parent_grid: dict, parent_record: dict) -> dict:
    return {
        "grid_id": parent_record["grid_id"],
        "archive_niche": parent_record["archive_niche"],
        "archive_fitness": parent_record["archive_fitness"],
        "selection_score": parent_record["selection_score"],
        "components": parent_record["components"],
        "runtime_episode": parent_record["runtime_episode"],
        "lineage": parent_grid.get("lineage", {"generation": 0, "ancestor_ids": []}),
    }


def _compact_runtime_probe(runtime_probe: dict) -> dict:
    selected = runtime_probe.get("selected")
    return {
        "probe_id": runtime_probe.get("probe_id"),
        "profile_id": runtime_probe.get("profile_id"),
        "selection_started": runtime_probe.get("selection_started", False),
        "validation_ok": runtime_probe.get("validation", {}).get("ok", False),
        "selected_grid_id": selected.get("grid_id") if isinstance(selected, dict) else None,
        "selected_archive_niche": selected.get("archive_niche") if isinstance(selected, dict) else None,
        "selected_selection_score": selected.get("selection_score") if isinstance(selected, dict) else None,
    }


def _runtime_summary(runtime: dict, lifecycle_ticks: int) -> dict:
    return {
        "policy": runtime.get("policy", "switchboard"),
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


def _read_parent_grid(generated_root: Path, profile_id: str, grid_id: str) -> dict:
    path = generated_root / profile_id / f"{grid_id}.json"
    if not path.exists():
        matches = sorted((generated_root / profile_id).glob(f"{grid_id}.json"))
        if not matches:
            raise FileNotFoundError(path)
        path = matches[0]
    return _read_json(path)


def _first_open_core_neighbor(grid: dict, *, offset: int) -> tuple[int, int] | None:
    width, height = grid["grid_size"]
    occupied = {(cell["x"], cell["y"]) for cell in grid.get("cells", [])}
    core = sorted(
        (cell["x"], cell["y"])
        for cell in grid.get("cells", [])
        if cell.get("organ") == "core"
    )
    neighbors = []
    for x, y in core:
        for dx, dy in [
            (0, -1),
            (1, 0),
            (0, 1),
            (-1, 0),
            (1, -1),
            (1, 1),
            (-1, 1),
            (-1, -1),
        ]:
            point = (x + dx, y + dy)
            if (
                0 <= point[0] < width
                and 0 <= point[1] < height
                and point not in occupied
            ):
                neighbors.append(point)
    if not neighbors:
        return None
    unique = sorted(set(neighbors), key=lambda point: (point[1], point[0]))
    return unique[offset % len(unique)]


def _tune_first_mutable_cell(grid: dict, delta: float) -> None:
    target = next(
        (cell for cell in grid.get("cells", []) if not cell.get("locked", False)),
        None,
    )
    if target is not None:
        target["mutation_weight"] = _round(
            _clamp(float(target.get("mutation_weight", 0)) + delta)
        )


def _scale_mutation_rates(grid: dict, profile: dict, factor: float) -> None:
    field_map = {
        "cell_mutation_rate": "cell_mutation_rate_max",
        "organ_shift_rate": "organ_shift_rate_max",
        "palette_shift_rate": "palette_shift_rate_max",
        "symmetry_break_rate": "symmetry_break_rate_max",
    }
    mutation = grid.setdefault("mutation", {})
    for grid_key, max_key in field_map.items():
        current = float(mutation.get(grid_key, 0))
        cap = float(profile["mutation"][max_key])
        mutation[grid_key] = _round(min(cap, max(0.0, current * factor)))


def _strip_private(grid: dict) -> dict:
    delta = grid.pop("_mutation_delta", {})
    grid["mutation_delta"] = delta
    return grid


def _first_mutable_coordinate(grid: dict) -> list[int] | None:
    target = next(
        (cell for cell in grid.get("cells", []) if not cell.get("locked", False)),
        None,
    )
    if target is None:
        return None
    return [target["x"], target["y"]]


def _body_visual(grid: dict) -> str:
    for cell in grid.get("cells", []):
        if cell.get("organ") == "core":
            return cell.get("visual", grid.get("palette", {}).get("colors", ["#ffffff"])[-1])
    colors = grid.get("palette", {}).get("colors", ["#ffffff"])
    return colors[min(1, len(colors) - 1)]


def _mean_cell_weight(grid: dict) -> float:
    weights = [
        float(cell.get("mutation_weight", 0))
        for cell in grid.get("cells", [])
        if isinstance(cell.get("mutation_weight", 0), int | float)
    ]
    return mean(weights) if weights else 0.0


def _symmetry_break_delta(parent_grid: dict, child_grid: dict) -> int:
    parent_mass = sum(1 for cell in parent_grid.get("cells", []) if cell.get("organ") == "core")
    child_mass = sum(1 for cell in child_grid.get("cells", []) if cell.get("organ") == "core")
    return 1 if child_mass != parent_mass else 0


def _validation_failure(family: str, message: str) -> dict:
    return {
        "ok": False,
        "errors": [{"path": "offspring_lineage", "family": family, "message": message}],
        "error_families": [family],
    }


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
    selected = result.get("selected_offspring", {})
    decision = result.get("lineage_decision", {})
    return {
        "profile_id": result["profile_id"],
        "gate_started": result.get("gate_started", False),
        "validation_ok": result.get("validation", {}).get("ok", False),
        "parent_grid_id": result.get("runtime_parent", {}).get("grid_id"),
        "selected_offspring_id": selected.get("grid_id"),
        "selected_offspring_score": selected.get("offspring_score"),
        "selected_archive_niche": selected.get("archive_niche"),
        "lineage_action": decision.get("action"),
        "lineage_reason": decision.get("reason"),
    }


def _readme_text(report: dict) -> str:
    metrics = report["metrics"]
    return (
        "# SLIP Offspring Lineage Gate Stage 0\n\n"
        "Bounded Stage 0 offspring mutation and lineage-decision evidence.\n\n"
        f"- Profiles: {report['profile_count']}\n"
        f"- Offspring gate successes: {report['offspring_gate_success_count']}\n"
        f"- Lineage decisions: {report['lineage_decision_count']}\n"
        f"- Invalid probes rejected: {report['invalid_probe_rejected_count']}\n"
        f"- Mean selected offspring score: {metrics['mean_selected_offspring_score']}\n"
        f"- Replace parent count: {metrics['replace_parent_count']}\n"
        f"- Add archive niche count: {metrics['add_archive_niche_count']}\n"
        f"- Hold parent count: {metrics['hold_parent_count']}\n"
    )


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _portable(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _weighted_average(components: dict[str, float], weights: dict[str, float]) -> float:
    total = sum(weights.values())
    if total == 0:
        return 0.0
    return _round(sum(components[key] * weights[key] for key in weights) / total)


def _mean_selected(records: list[dict], key: str) -> float:
    if not records:
        return 0.0
    return _round(mean(float(record[key]) for record in records))


def _mean_nested(records: list[dict], path: list[str]) -> float:
    if not records:
        return 0.0
    values = []
    for record in records:
        cursor = record
        for key in path:
            cursor = cursor[key]
        values.append(float(cursor))
    return _round(mean(values))


def _decision_count(decisions: list[dict], action: str) -> int:
    return sum(1 for decision in decisions if decision.get("action") == action)


def _distinct_count(values) -> int:
    return len({value for value in values if value is not None})


def _ratio(numerator: int | float, denominator: int | float) -> float:
    if denominator == 0:
        return 0.0
    return _round(numerator / denominator)


def _round(value: int | float) -> float:
    return round(float(value), 6)


def _clamp(value: object) -> float:
    if not isinstance(value, int | float) or isinstance(value, bool):
        return 0.0
    return max(0.0, min(1.0, float(value)))


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
        default=Path("data/workshop_editor/slip_offspring_lineage_gate_stage0"),
    )
    parser.add_argument("--candidate-limit", type=int, default=12)
    parser.add_argument("--lifecycle-ticks", type=int, default=24)
    parser.add_argument("--rng-seed", type=int, default=20260513)
    args = parser.parse_args()
    profile_paths = args.profile or DEFAULT_PROFILE_PATHS
    report = run_slip_offspring_lineage_gate_lab(
        profile_paths,
        args.generated_root,
        candidate_limit=args.candidate_limit,
        lifecycle_ticks=args.lifecycle_ticks,
        rng_seed=args.rng_seed,
    )
    _write_json(REPORT_PATH, report)
    APP_DATA_PATH.write_text(
        "window.MECHAGOTCHI_SLIP_OFFSPRING_LINEAGE_GATE = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )
    write_slip_offspring_lineage_gate_artifacts(args.output_dir, report)


if __name__ == "__main__":
    main()
