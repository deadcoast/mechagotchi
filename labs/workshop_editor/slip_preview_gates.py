import argparse
import json
import math
import sys
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GRID_GENOME_DIR = ROOT / "labs" / "grid_genome"
if str(GRID_GENOME_DIR) not in sys.path:
    sys.path.insert(0, str(GRID_GENOME_DIR))

from slip import is_grid_aligned
from validator import validate_grid

from slip_authoring_panel import validate_authoring_draft


REPORT_PATH = Path("data/workshop_editor/slip_behavior_mutation_preview_stage0.json")
PREVIEW_DATA_PATH = Path("data/workshop_editor/slip_preview_gate_data.js")


def validate_preview_request(profile: dict, grid: dict) -> dict:
    profile_validation = validate_authoring_draft(profile)
    grid_validation = validate_grid(grid)
    alignment = {"ok": False, "errors": []}
    if profile_validation["ok"] and grid_validation.ok:
        alignment_result = is_grid_aligned(grid, profile)
        alignment = {
            "ok": alignment_result.ok,
            "errors": alignment_result.errors,
        }

    errors = _profile_errors(profile_validation)
    if not grid_validation.ok:
        errors.extend(
            {
                "source": "grid_validator",
                "family": "grid_validation",
                "path": "$",
                "message": error,
            }
            for error in grid_validation.errors
        )
    if profile_validation["ok"] and grid_validation.ok and not alignment["ok"]:
        errors.extend(
            {
                "source": "slip_alignment",
                "family": "slip_alignment",
                "path": "$",
                "message": error,
            }
            for error in alignment["errors"]
        )

    ok = profile_validation["ok"] and grid_validation.ok and alignment["ok"]
    return {
        "ok": ok,
        "profile_id": profile.get("profile_id"),
        "grid_id": grid.get("grid_id"),
        "profile_validation": profile_validation,
        "grid_validation": {
            "ok": grid_validation.ok,
            "errors": grid_validation.errors,
        },
        "alignment": alignment,
        "preview_surfaces": ["behavior_preview", "mutation_preview"] if ok else [],
        "errors": errors,
        "error_families": sorted({error["family"] for error in errors}),
    }


def build_behavior_preview(profile: dict) -> dict:
    behavior = profile["behavior"]
    survival = profile["survival_weights"]
    curiosity = _unit(behavior["curiosity"])
    neediness = _unit(behavior["neediness"])
    sleepiness = _unit(behavior["sleepiness"])
    stability = _unit(survival["stability"])
    novelty = _unit(survival["novelty"])
    bond = _unit(survival["bond"])

    signals = {
        "social_pull": _round(neediness * 0.55 + bond * 0.30 + curiosity * 0.15),
        "exploration_pull": _round(curiosity * 0.50 + novelty * 0.35 + (1 - sleepiness) * 0.15),
        "rest_pull": _round(sleepiness * 0.55 + stability * 0.35 + (1 - curiosity) * 0.10),
        "mutation_pressure": _round(novelty * 0.45 + curiosity * 0.35 + (1 - stability) * 0.20),
        "mutation_caution": _round(stability * 0.55 + sleepiness * 0.20 + (1 - novelty) * 0.25),
    }
    scenarios = [
        _behavior_scenario(
            "attention_gap",
            {
                "play": signals["social_pull"] * 0.62 + signals["exploration_pull"] * 0.28,
                "idle": signals["mutation_caution"] * 0.30 + signals["rest_pull"] * 0.18,
                "sleep": signals["rest_pull"] * 0.58,
                "mutate": signals["mutation_pressure"] * 0.42,
            },
            "Neediness and bond raise the user-facing play prompt.",
        ),
        _behavior_scenario(
            "low_energy_tick",
            {
                "sleep": signals["rest_pull"] * 0.74 + signals["mutation_caution"] * 0.18,
                "idle": signals["rest_pull"] * 0.34,
                "play": signals["social_pull"] * 0.18,
                "mutate": signals["mutation_pressure"] * 0.18,
            },
            "Sleepiness and stability raise the rest response.",
        ),
        _behavior_scenario(
            "safe_novelty_window",
            {
                "mutate": signals["mutation_pressure"] * 0.54 - signals["mutation_caution"] * 0.16,
                "play": signals["exploration_pull"] * 0.34 + signals["social_pull"] * 0.18,
                "idle": signals["mutation_caution"] * 0.24,
                "sleep": signals["rest_pull"] * 0.22,
            },
            "Curiosity and novelty raise mutation interest while stability tempers it.",
        ),
    ]
    return {
        "profile_id": profile["profile_id"],
        "preview_model": "deterministic_profile_weight_proxy",
        "scenario_count": len(scenarios),
        "signals": signals,
        "scenarios": scenarios,
        "effect_fingerprint": [
            signals["social_pull"],
            signals["exploration_pull"],
            signals["rest_pull"],
            signals["mutation_pressure"],
            signals["mutation_caution"],
        ],
        "limitations": [
            "Preview only: no lifecycle state is mutated.",
            "Preview only: no reinforcement-learning policy is trained or adopted.",
        ],
    }


def build_mutation_preview(profile: dict, grid: dict) -> dict:
    mutation = profile["mutation"]
    allowed_palettes = profile["grid"]["allowed_palettes"]
    active_cells = [cell for cell in grid.get("cells", [])]
    mutable_cells = [cell for cell in active_cells if not cell.get("locked", False)]
    body_cells = [cell for cell in active_cells if cell.get("organ") == "core"]
    organ_cells = [cell for cell in active_cells if cell.get("organ") != "core"]

    cell_cap = _unit(mutation["cell_mutation_rate_max"])
    organ_cap = _unit(mutation["organ_shift_rate_max"])
    palette_cap = _unit(mutation["palette_shift_rate_max"])
    symmetry_cap = _unit(mutation["symmetry_break_rate_max"])
    cell_budget_cap = _ceil_budget(len(mutable_cells), cell_cap)
    organ_budget_cap = _ceil_budget(len(organ_cells), organ_cap)
    symmetry_budget_cap = _ceil_budget(len(body_cells), symmetry_cap)
    cell_candidates = _mutation_candidates(mutable_cells, cell_budget_cap)
    organ_candidates = _mutation_candidates(organ_cells, organ_budget_cap)
    palette_allowed = len(allowed_palettes) > 1 and palette_cap > 0
    palette_reason = (
        "multiple_allowed_palettes_available"
        if palette_allowed
        else "single_allowed_palette_blocks_preview_shift"
        if len(allowed_palettes) <= 1
        else "palette_shift_cap_zero"
    )
    caps_respected = (
        len(cell_candidates) <= cell_budget_cap
        and len(organ_candidates) <= organ_budget_cap
        and cell_budget_cap <= len(mutable_cells)
        and organ_budget_cap <= len(organ_cells)
        and symmetry_budget_cap <= len(body_cells)
    )
    return {
        "profile_id": profile["profile_id"],
        "grid_id": grid["grid_id"],
        "preview_model": "deterministic_cap_projection_no_mutation_applied",
        "body_mass": len(body_cells),
        "mutable_cell_count": len(mutable_cells),
        "organ_cell_count": len(organ_cells),
        "budgets": {
            "cell_mutation_budget": len(cell_candidates),
            "cell_mutation_budget_cap": cell_budget_cap,
            "organ_shift_budget": len(organ_candidates),
            "organ_shift_budget_cap": organ_budget_cap,
            "symmetry_break_budget": symmetry_budget_cap,
            "symmetry_break_budget_cap": symmetry_budget_cap,
        },
        "caps": {
            "cell_mutation_rate_max": cell_cap,
            "organ_shift_rate_max": organ_cap,
            "palette_shift_rate_max": palette_cap,
            "symmetry_break_rate_max": symmetry_cap,
        },
        "cell_mutation_candidates": cell_candidates,
        "organ_shift_candidates": organ_candidates,
        "palette_shift": {
            "allowed": palette_allowed,
            "current_palette": grid.get("palette", {}).get("palette_id"),
            "allowed_palettes": allowed_palettes,
            "reason": palette_reason,
        },
        "caps_respected": caps_respected,
        "limitations": [
            "Preview only: no grid cells are changed.",
            "Preview only: does not prove offspring validity or archive impact.",
        ],
    }


def run_slip_preview_gate_lab(profile_paths: list[Path], generated_root: Path) -> dict:
    profile_results = []
    for profile_path in profile_paths:
        profile = _read_json(profile_path)
        grid_path = _first_grid_path(profile, generated_root)
        grid = _read_json(grid_path)
        validation = validate_preview_request(profile, grid)
        if not validation["ok"]:
            raise ValueError(
                f"preview request should be valid for {profile['profile_id']}: "
                f"{validation['errors']}"
            )
        profile_results.append(
            {
                "profile_id": profile["profile_id"],
                "profile_path": _portable(profile_path),
                "grid_path": _portable(grid_path),
                "validation": validation,
                "behavior_preview": build_behavior_preview(profile),
                "mutation_preview": build_mutation_preview(profile, grid),
            }
        )

    invalid_probe_results = _invalid_preview_probes(profile_paths[0], generated_root)
    behavior_preview_count = sum(
        1 for result in profile_results if result["behavior_preview"]["scenario_count"] > 0
    )
    mutation_preview_count = sum(
        1 for result in profile_results if result["mutation_preview"]["caps_respected"]
    )
    invalid_rejected_count = sum(1 for result in invalid_probe_results if not result["ok"])
    profile_weight_effects = _profile_weight_effects_observed(profile_results)
    mutation_caps_respected = all(
        result["mutation_preview"]["caps_respected"] for result in profile_results
    )
    return {
        "artifact_id": "slip_behavior_mutation_preview_stage0",
        "status": "research_slip_behavior_mutation_preview_no_package_code",
        "date": "2026-05-12",
        "purpose": (
            "Prove current valid SLIP profiles can drive deterministic workshop "
            "behavior previews and bounded mutation previews without claiming "
            "runtime lifecycle integration or profile-weighted evolution."
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
            "labs/workshop_editor/slip_authoring_panel.py",
            "labs/workshop_editor/index.html",
            "labs/workshop_editor/app.js",
            "labs/workshop_editor/styles.css",
        ],
        "external_anchors": [
            {
                "source": "Procedural Content Generation in Games",
                "url": "https://www.pcgbook.com/",
                "used_for": "Mutation preview is framed as bounded candidate generation, not unbounded random change.",
            },
            {
                "source": "Reinforcement Learning: An Introduction, MIT Press page",
                "url": "https://mitpress.mit.edu/9780262039246/reinforcement-learning/",
                "used_for": "Behavior preview is kept as a deterministic action-value proxy, not a trained RL policy.",
            },
            {
                "source": "MDN output element",
                "url": "https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/output",
                "used_for": "Static workshop preview panels render calculated results through output surfaces.",
            },
        ],
        "profile_count": len(profile_results),
        "behavior_preview_count": behavior_preview_count,
        "mutation_preview_count": mutation_preview_count,
        "invalid_probe_count": len(invalid_probe_results),
        "invalid_probe_rejected_count": invalid_rejected_count,
        "metrics": {
            "preview_gate_success_rate": _ratio(
                min(behavior_preview_count, mutation_preview_count),
                len(profile_results),
            ),
            "profile_weight_effects_observed": profile_weight_effects,
            "mutation_caps_respected": mutation_caps_respected,
            "invalid_probe_rejection_rate": _ratio(
                invalid_rejected_count,
                len(invalid_probe_results),
            ),
            "palette_shift_blocked_by_single_palette_profiles": sum(
                1
                for result in profile_results
                if not result["mutation_preview"]["palette_shift"]["allowed"]
                and result["mutation_preview"]["palette_shift"]["reason"]
                == "single_allowed_palette_blocks_preview_shift"
            ),
        },
        "profile_results": profile_results,
        "invalid_probe_results": invalid_probe_results,
        "closed_states": [
            "behavior_preview_gate",
            "mutation_preview_gate",
            "profile_weights_drive_preview_outputs",
            "mutation_caps_bound_preview_outputs",
            "invalid_profile_rejected_before_preview",
        ],
        "blocked_states": [
            "runtime_jsonschema_validation",
            "declared_dependency_manifest",
            "profile_weighted_evolution",
            "engine_lifecycle_behavior_integration",
            "external_image_project_metadata_sidecar_strategy",
            "profile_authoring_usability_pilot",
            "community_profile_packs",
        ],
        "decision": "prototype_behavior_mutation_preview_gate",
        "next_research_step": (
            "Either define the external metadata sidecar strategy for non-native "
            "imports or connect the preview gate to measured lifecycle/archive "
            "effects before claiming profile-weighted evolution."
        ),
    }


def write_slip_preview_gate_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "slip_behavior_mutation_preview_stage0.json", report)
    for result in report["profile_results"]:
        _write_json(output_dir / f"{result['profile_id']}_preview_gate.json", result)
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")
    (output_dir / "slip_preview_gate_data.js").write_text(
        "window.MECHAGOTCHI_SLIP_PREVIEW_GATES = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )


def _profile_errors(profile_validation: dict) -> list[dict]:
    return [
        {
            "source": error["source"],
            "family": error["family"],
            "path": error["path"],
            "message": error["message"],
        }
        for error in profile_validation["errors"]
    ]


def _behavior_scenario(scenario_id: str, raw_scores: dict[str, float], explanation: str) -> dict:
    scores = {action: _round(max(0.0, value)) for action, value in raw_scores.items()}
    selected_action = max(scores, key=scores.get)
    return {
        "scenario_id": scenario_id,
        "selected_action": selected_action,
        "action_scores": dict(sorted(scores.items())),
        "confidence": _round(scores[selected_action]),
        "explanation": explanation,
    }


def _mutation_candidates(cells: list[dict], budget: int) -> list[dict]:
    sorted_cells = sorted(
        cells,
        key=lambda cell: (
            -float(cell.get("mutation_weight", 0)),
            str(cell.get("organ", "")),
            int(cell.get("y", 0)),
            int(cell.get("x", 0)),
        ),
    )
    return [
        {
            "coordinate": [int(cell["x"]), int(cell["y"])],
            "organ": cell.get("organ"),
            "role": cell.get("role"),
            "mutation_weight": _round(float(cell.get("mutation_weight", 0))),
        }
        for cell in sorted_cells[:budget]
    ]


def _invalid_preview_probes(profile_path: Path, generated_root: Path) -> list[dict]:
    profile = _read_json(profile_path)
    grid = _read_json(_first_grid_path(profile, generated_root))
    unsupported_version = deepcopy(profile)
    unsupported_version["slip_version"] = "0.2.0"
    excessive_cap = deepcopy(profile)
    excessive_cap["mutation"]["cell_mutation_rate_max"] = 1.25
    return [
        validate_preview_request(unsupported_version, grid),
        validate_preview_request(excessive_cap, grid),
    ]


def _profile_weight_effects_observed(profile_results: list[dict]) -> bool:
    by_profile = {
        result["profile_id"]: result["behavior_preview"]["signals"]
        for result in profile_results
    }
    fingerprints = {
        tuple(result["behavior_preview"]["effect_fingerprint"])
        for result in profile_results
    }
    return (
        by_profile["slip_amber_social"]["social_pull"]
        > by_profile["slip_lcd_seed"]["social_pull"]
        > by_profile["slip_gray_stable"]["social_pull"]
        and by_profile["slip_gray_stable"]["rest_pull"]
        > by_profile["slip_lcd_seed"]["rest_pull"]
        > by_profile["slip_amber_social"]["rest_pull"]
        and len(fingerprints) == len(profile_results)
    )


def _first_grid_path(profile: dict, generated_root: Path) -> Path:
    grid_paths = sorted((generated_root / profile["profile_id"]).glob("*.json"))
    if not grid_paths:
        raise ValueError(f"no generated grids found for profile: {profile['profile_id']}")
    return grid_paths[0]


def _app_payload(report: dict) -> dict:
    return {
        "report": {
            key: report[key]
            for key in [
                "artifact_id",
                "status",
                "profile_count",
                "behavior_preview_count",
                "mutation_preview_count",
                "invalid_probe_count",
                "invalid_probe_rejected_count",
                "metrics",
                "closed_states",
                "blocked_states",
                "decision",
            ]
        },
        "profile_results": report["profile_results"],
    }


def _readme_text(report: dict) -> str:
    metrics = report["metrics"]
    return (
        "# SLIP Behavior and Mutation Preview Stage 0\n\n"
        "Deterministic workshop preview-gate evidence for current SLIP profiles.\n\n"
        f"- Profiles: {report['profile_count']}\n"
        f"- Behavior previews: {report['behavior_preview_count']}\n"
        f"- Mutation previews: {report['mutation_preview_count']}\n"
        f"- Invalid probes rejected: {report['invalid_probe_rejected_count']}"
        f"/{report['invalid_probe_count']}\n"
        f"- Profile weight effects observed: {metrics['profile_weight_effects_observed']}\n"
        f"- Mutation caps respected: {metrics['mutation_caps_respected']}\n"
        f"- Decision: {report['decision']}\n"
    )


def _ceil_budget(population: int, rate: float) -> int:
    if population <= 0 or rate <= 0:
        return 0
    return min(population, int(math.ceil(population * rate)))


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _portable(path: Path) -> str:
    return str(path).replace("\\", "/")


def _ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return _round(numerator / denominator)


def _round(value: float) -> float:
    return round(float(value), 6)


def _unit(value: object) -> float:
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
        default=Path("data/workshop_editor/slip_behavior_mutation_preview_stage0"),
    )
    parser.add_argument(
        "--generated-root",
        type=Path,
        default=Path("data/slips/multi_profile_generation_stage0"),
    )
    parser.add_argument("--profile", type=Path, action="append")
    args = parser.parse_args()
    profile_paths = args.profile or [
        Path("data/slips/valid/slip_lcd_seed.json"),
        Path("data/slips/valid/slip_gray_stable.json"),
        Path("data/slips/valid/slip_amber_social.json"),
    ]
    report = run_slip_preview_gate_lab(profile_paths, args.generated_root)
    write_slip_preview_gate_artifacts(args.output_dir, report)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _write_json(REPORT_PATH, report)
    PREVIEW_DATA_PATH.write_text(
        "window.MECHAGOTCHI_SLIP_PREVIEW_GATES = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
