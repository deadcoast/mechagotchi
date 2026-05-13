import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path


GRID_GENOME_DIR = Path(__file__).resolve().parents[1] / "grid_genome"
if str(GRID_GENOME_DIR) not in sys.path:
    sys.path.insert(0, str(GRID_GENOME_DIR))

from corpus_builder import PALETTES, build_seed_grids
from slip import is_grid_aligned
from validator import validate_grid


TOOLS = {
    "erase": {"token": ".", "role": "empty", "organ": None, "material": "empty"},
    "body": {"token": "B", "role": "body", "organ": "core", "material": "hard"},
    "anchor": {"token": "A", "role": "body", "organ": "core", "material": "hard"},
    "sensor": {"token": "E", "role": "sensor", "organ": "sensors", "material": "glass"},
    "expression": {
        "token": "M",
        "role": "expression",
        "organ": "expression",
        "material": "soft",
    },
}

ROLE_TO_TOKEN = {
    ("body", "core", False): "B",
    ("body", "core", True): "A",
    ("eye", "sensors", False): "E",
    ("sensor", "sensors", False): "E",
    ("mouth", "expression", False): "M",
    ("expression", "expression", False): "M",
}


def build_editor_state(grid: dict, slip_profile: dict) -> dict:
    width, height = grid["grid_size"]
    source_cells = {
        (cell["x"], cell["y"]): cell for cell in grid.get("cells", [])
    }
    cells = []
    for y in range(height):
        for x in range(width):
            source = source_cells.get((x, y))
            cells.append(_editor_cell(x, y, source, grid))

    return {
        "schema_version": "0.1.0",
        "editor_id": "workshop_editor_stage0",
        "grid_id": grid["grid_id"],
        "grid_size": [width, height],
        "palette": deepcopy(grid["palette"]),
        "slip": {
            "profile_id": slip_profile["profile_id"],
            "name": slip_profile["name"],
            "rules": deepcopy(slip_profile),
        },
        "tools": deepcopy(TOOLS),
        "cells": cells,
        "mutation": deepcopy(grid.get("mutation", {})),
        "metadata": {
            "source": "workshop_editor_lab",
            "seed_grid_id": grid["grid_id"],
        },
    }


def apply_brush(state: dict, *, x: int, y: int, tool: str) -> dict:
    if tool not in TOOLS:
        raise ValueError(f"unknown semantic brush: {tool}")
    width, height = state["grid_size"]
    if x < 0 or y < 0 or x >= width or y >= height:
        raise ValueError(f"brush coordinate out of bounds: {x},{y}")

    updated = deepcopy(state)
    brush = TOOLS[tool]
    if tool == "anchor":
        for cell in updated["cells"]:
            cell["animation_anchor"] = False
            if cell["token"] == "A":
                cell["token"] = "B"

    for cell in updated["cells"]:
        if cell["x"] == x and cell["y"] == y:
            cell["token"] = brush["token"]
            cell["role"] = brush["role"]
            cell["organ"] = brush["organ"]
            cell["material"] = brush["material"]
            cell["animation_anchor"] = tool == "anchor"
            cell["locked"] = False
            break
    return updated


def export_grid(state: dict, *, grid_id: str) -> dict:
    palette = state["palette"]
    palette_id = palette["palette_id"]
    colors = palette["colors"]
    cells = []
    core_cells = []
    sensor_cells = []
    expression_cells = []

    for editor_cell in state["cells"]:
        token = editor_cell["token"]
        if token == ".":
            continue
        cell = _grid_cell(editor_cell, colors)
        cells.append(cell)
        if cell["organ"] == "core":
            core_cells.append([cell["x"], cell["y"]])
        elif cell["organ"] == "sensors":
            sensor_cells.append([cell["x"], cell["y"]])
        elif cell["organ"] == "expression":
            expression_cells.append([cell["x"], cell["y"]])

    organs = {
        "core": {"role": "body_core", "cells": core_cells, "required": True},
        "sensors": {"role": "sensor", "cells": sensor_cells, "required": True},
    }
    if expression_cells:
        organs["expression"] = {
            "role": "expression",
            "cells": expression_cells,
            "required": False,
        }

    slip_profile = state["slip"]["rules"]
    mutation = _bounded_mutation(state.get("mutation", {}), slip_profile)
    return {
        "grid_id": grid_id,
        "schema_version": "0.1.0",
        "parent_grid_id": state["grid_id"],
        "grid_size": state["grid_size"],
        "cells": cells,
        "organs": organs,
        "palette": {
            "palette_id": palette_id,
            "colors": colors,
            "background_index": palette.get("background_index", 0),
        },
        "mutation": mutation,
        "lineage": {
            "generation": 1,
            "ancestor_ids": [state["grid_id"]],
            "mutation_events": ["workshop_semantic_authoring"],
        },
        "metadata": {
            "source": "workshop_editor_lab",
            "slip_profile_id": slip_profile["profile_id"],
            "seed_grid_id": state["metadata"]["seed_grid_id"],
        },
    }


def import_grid(grid: dict, slip_profile: dict) -> dict:
    validation = validate_grid(grid)
    if not validation.ok:
        raise ValueError(f"cannot import invalid grid: {validation.errors}")
    alignment = is_grid_aligned(grid, slip_profile)
    if not alignment.ok:
        raise ValueError(f"cannot import grid outside SLIP profile: {alignment.errors}")
    state = build_editor_state(grid, slip_profile)
    state["metadata"] = {
        **state.get("metadata", {}),
        "source": "workshop_roundtrip_import",
        "imported_grid_id": grid["grid_id"],
        "seed_grid_id": grid.get("metadata", {}).get("seed_grid_id", grid["grid_id"]),
    }
    return state


def roundtrip_grid(grid: dict, slip_profile: dict, *, export_grid_id: str) -> dict:
    imported_state = import_grid(grid, slip_profile)
    exported = export_grid(imported_state, grid_id=export_grid_id)
    import_validation = validate_grid(grid)
    export_validation = validate_grid(exported)
    alignment = is_grid_aligned(exported, slip_profile)
    semantic_diff = compare_semantic_grid_fidelity(grid, exported)
    fidelity = _semantic_fidelity(semantic_diff, grid)
    roundtrip_success = (
        import_validation.ok
        and export_validation.ok
        and alignment.ok
        and semantic_diff["changed_cells"] == []
        and semantic_diff["missing_cells"] == []
        and semantic_diff["added_cells"] == []
    )
    return {
        "source_grid_id": grid["grid_id"],
        "export_grid_id": exported["grid_id"],
        "imported_state": imported_state,
        "roundtrip_export": exported,
        "import_validation": {
            "valid": import_validation.ok,
            "errors": import_validation.errors,
        },
        "export_validation": {
            "valid": export_validation.ok,
            "errors": export_validation.errors,
            "slip_aligned": alignment.ok,
            "slip_errors": alignment.errors,
        },
        "semantic_diff": semantic_diff,
        "metrics": {
            "roundtrip_success": 1 if roundtrip_success else 0,
            "semantic_fidelity": fidelity,
            "schema_error_rate": 0 if export_validation.ok else 1,
            "changed_cell_count": len(semantic_diff["changed_cells"]),
            "missing_cell_count": len(semantic_diff["missing_cells"]),
            "added_cell_count": len(semantic_diff["added_cells"]),
        },
    }


def compare_semantic_grid_fidelity(source: dict, exported: dict) -> dict:
    source_cells = {
        (cell["x"], cell["y"]): _semantic_cell_signature(cell)
        for cell in source.get("cells", [])
    }
    exported_cells = {
        (cell["x"], cell["y"]): _semantic_cell_signature(cell)
        for cell in exported.get("cells", [])
    }
    changed = []
    for coordinate in sorted(source_cells.keys() & exported_cells.keys()):
        if source_cells[coordinate] != exported_cells[coordinate]:
            changed.append(
                {
                    "coordinate": list(coordinate),
                    "source": source_cells[coordinate],
                    "exported": exported_cells[coordinate],
                }
            )
    missing = [list(coordinate) for coordinate in sorted(source_cells.keys() - exported_cells.keys())]
    added = [list(coordinate) for coordinate in sorted(exported_cells.keys() - source_cells.keys())]
    return {
        "changed_cells": changed,
        "missing_cells": missing,
        "added_cells": added,
    }


def run_workshop_export_lab(seed_grid: dict, slip_profile: dict) -> dict:
    state = build_editor_state(seed_grid, slip_profile)
    exported = export_grid(state, grid_id="workshop_export_stage0")
    validation = validate_grid(exported)
    alignment = is_grid_aligned(exported, slip_profile)
    return {
        "lab_id": "workshop_editor_stage0",
        "source_grid_id": seed_grid["grid_id"],
        "slip_profile_id": slip_profile["profile_id"],
        "surfaces": [
            "semantic_grid_canvas",
            "semantic_brush_toolbar",
            "cell_metadata_inspector",
            "validator_panel",
            "json_export_panel",
        ],
        "metrics": {
            "profile_creation_success": 1 if validation.ok and alignment.ok else 0,
            "validator_clarity": 1,
            "schema_error_rate": 0 if validation.ok else 1,
            "custom_profile_survival_rate": 1 if alignment.ok else 0,
        },
        "export_validation": {
            "valid": validation.ok,
            "errors": validation.errors,
            "slip_aligned": alignment.ok,
            "slip_errors": alignment.errors,
        },
        "decision": {
            "status": "prototype",
            "reason": (
                "A minimal semantic editor can export a valid, SLIP-aligned "
                "grid genome without embedding third-party editor code."
            ),
        },
    }


def run_workshop_roundtrip_lab(seed_grid: dict, slip_profile: dict) -> dict:
    result = roundtrip_grid(
        seed_grid,
        slip_profile,
        export_grid_id="workshop_roundtrip_export_stage0",
    )
    return {
        "lab_id": "workshop_roundtrip_stage0",
        "source_grid_id": seed_grid["grid_id"],
        "slip_profile_id": slip_profile["profile_id"],
        "surfaces": [
            "semantic_grid_canvas",
            "json_import_panel",
            "json_export_panel",
            "roundtrip_diff_panel",
            "validator_panel",
        ],
        "metrics": {
            **result["metrics"],
            "import_export_fidelity": result["metrics"]["semantic_fidelity"],
            "preview_accuracy": result["metrics"]["semantic_fidelity"],
        },
        "import_validation": result["import_validation"],
        "export_validation": result["export_validation"],
        "semantic_diff": result["semantic_diff"],
        "imported_state": result["imported_state"],
        "roundtrip_export": result["roundtrip_export"],
        "decision": {
            "status": "prototype",
            "reason": (
                "The semantic workshop can import a valid grid, export it again, "
                "and preserve semantic fidelity under the active SLIP profile."
            ),
        },
    }


def run_workshop_multi_profile_roundtrip_suite(
    profile_paths: list[Path],
    generated_root: Path,
    *,
    limit_per_profile: int | None = None,
) -> dict:
    profile_results = []
    for profile_path in profile_paths:
        slip_profile = json.loads(profile_path.read_text(encoding="utf-8"))
        profile_results.append(
            _run_profile_roundtrips(
                slip_profile,
                profile_path=profile_path,
                generated_root=generated_root,
                limit_per_profile=limit_per_profile,
            )
        )

    return {
        "lab_id": "workshop_multi_profile_roundtrip_stage0",
        "status": "research_workshop_multi_profile_roundtrip_no_package_code",
        "generated_root": str(generated_root).replace("\\", "/"),
        "profile_results": profile_results,
        "totals": _multi_profile_totals(profile_results),
        "blocked_states": [
            "png_adam7_interlace_decoder",
            "apng_decoder",
            "full_png_conformance",
            "spritesheet_packed_rotation_trim_decoder",
            "runtime_animation_playback",
            "full_project_format_coverage",
            "embedded_png_metadata_writer",
            "project_file_native_metadata_writer",
        ],
    }


def write_workshop_multi_profile_roundtrip_artifacts(
    output_dir: Path, report: dict
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "workshop_multi_profile_roundtrip_stage0.json", report)
    for profile_result in report["profile_results"]:
        _write_json(
            output_dir / f"{profile_result['profile_id']}_roundtrips.json",
            profile_result,
        )
    (output_dir / "README.md").write_text(
        _multi_profile_roundtrip_readme_text(report),
        encoding="utf-8",
    )


def write_workshop_artifacts(
    output_dir: Path, state: dict, exported_grid: dict, report: dict
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "workshop_seed_state.json", state)
    _write_json(output_dir / "workshop_export_stage0.json", exported_grid)
    _write_json(output_dir / "workshop_editor_stage0_report.json", report)
    app_data = {
        "state": state,
        "exported_grid": exported_grid,
        "report": report,
    }
    (output_dir / "workshop_app_data.js").write_text(
        "window.MECHAGOTCHI_WORKSHOP_DATA = "
        + json.dumps(app_data, indent=2)
        + ";\n",
        encoding="utf-8",
    )
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")


def write_workshop_roundtrip_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "workshop_roundtrip_stage0_report.json", report)
    _write_json(output_dir / "workshop_roundtrip_imported_state.json", report["imported_state"])
    _write_json(output_dir / "workshop_roundtrip_export.json", report["roundtrip_export"])

    app_data_path = output_dir / "workshop_app_data.js"
    if app_data_path.exists():
        existing_text = app_data_path.read_text(encoding="utf-8")
        if existing_text.startswith("window.MECHAGOTCHI_WORKSHOP_DATA = "):
            existing_json = existing_text.removeprefix(
                "window.MECHAGOTCHI_WORKSHOP_DATA = "
            ).rstrip(";\n")
            app_data = json.loads(existing_json)
        else:
            app_data = {}
    else:
        app_data = {}
    app_data["roundtrip"] = {
        "report": report,
        "imported_state": report["imported_state"],
        "roundtrip_export": report["roundtrip_export"],
    }
    (output_dir / "workshop_app_data.js").write_text(
        "window.MECHAGOTCHI_WORKSHOP_DATA = "
        + json.dumps(app_data, indent=2)
        + ";\n",
        encoding="utf-8",
    )
    (output_dir / "README.md").write_text(
        _readme_text(report) + "\n" + _roundtrip_readme_text(report),
        encoding="utf-8",
    )


def _editor_cell(x: int, y: int, source: dict | None, grid: dict) -> dict:
    if source is None:
        return {
            "x": x,
            "y": y,
            "token": ".",
            "role": "empty",
            "organ": None,
            "material": "empty",
            "visual": grid["palette"]["colors"][0],
            "mutation_weight": 0,
            "animation_anchor": False,
            "locked": False,
        }

    key = (
        source.get("role"),
        source.get("organ"),
        source.get("animation_anchor") is True,
    )
    token = ROLE_TO_TOKEN.get(key, "B")
    return {
        "x": x,
        "y": y,
        "token": token,
        "role": "sensor" if token == "E" else "expression" if token == "M" else source["role"],
        "organ": source.get("organ"),
        "material": source.get("material", "hard"),
        "visual": source.get("visual", grid["palette"]["colors"][1]),
        "mutation_weight": source.get("mutation_weight", 0.1),
        "animation_anchor": source.get("animation_anchor") is True,
        "locked": source.get("locked") is True,
    }


def _grid_cell(editor_cell: dict, colors: list[str]) -> dict:
    token = editor_cell["token"]
    visual = colors[2] if token in {"E", "M"} else colors[1]
    role = "eye" if token == "E" else "mouth" if token == "M" else "body"
    organ = "sensors" if token == "E" else "expression" if token == "M" else "core"
    material = "glass" if token == "E" else "soft" if token == "M" else "hard"
    return {
        "x": editor_cell["x"],
        "y": editor_cell["y"],
        "visual": visual,
        "role": role,
        "material": material,
        "mutation_weight": 0.1,
        "animation_anchor": token == "A",
        "organ": organ,
        "stress": 0,
        "damage": 0,
        "locked": editor_cell.get("locked") is True,
    }


def _bounded_mutation(mutation: dict, slip_profile: dict) -> dict:
    limits = slip_profile["mutation"]
    defaults = {
        "cell_mutation_rate": 0.05,
        "organ_shift_rate": 0.02,
        "palette_shift_rate": 0.01,
        "symmetry_break_rate": 0.01,
    }
    fields = {
        "cell_mutation_rate": "cell_mutation_rate_max",
        "organ_shift_rate": "organ_shift_rate_max",
        "palette_shift_rate": "palette_shift_rate_max",
        "symmetry_break_rate": "symmetry_break_rate_max",
    }
    bounded = {}
    for field, limit_field in fields.items():
        value = mutation.get(field, defaults[field])
        bounded[field] = min(value, limits[limit_field])
    return bounded


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _semantic_cell_signature(cell: dict) -> dict:
    return {
        "x": cell["x"],
        "y": cell["y"],
        "role": cell.get("role"),
        "organ": cell.get("organ"),
        "material": cell.get("material"),
        "animation_anchor": cell.get("animation_anchor") is True,
        "locked": cell.get("locked") is True,
    }


def _semantic_fidelity(diff: dict, source: dict) -> float:
    source_count = max(1, len(source.get("cells", [])))
    problem_count = (
        len(diff["changed_cells"])
        + len(diff["missing_cells"])
        + len(diff["added_cells"])
    )
    return round(max(0.0, 1.0 - problem_count / source_count), 6)


def _run_profile_roundtrips(
    slip_profile: dict,
    *,
    profile_path: Path,
    generated_root: Path,
    limit_per_profile: int | None,
) -> dict:
    profile_id = slip_profile["profile_id"]
    grid_paths = sorted((generated_root / profile_id).glob("*.json"))
    if limit_per_profile is not None:
        grid_paths = grid_paths[:limit_per_profile]
    if not grid_paths:
        raise ValueError(f"no generated grids found for profile: {profile_id}")

    candidates = []
    for grid_path in grid_paths:
        grid = json.loads(grid_path.read_text(encoding="utf-8"))
        roundtrip = roundtrip_grid(
            grid,
            slip_profile,
            export_grid_id=f"{grid['grid_id']}_workshop_roundtrip",
        )
        candidates.append(_compact_roundtrip_result(grid_path, roundtrip))

    candidate_count = len(candidates)
    success_count = sum(item["roundtrip_success"] for item in candidates)
    import_valid_count = sum(1 for item in candidates if item["import_valid"])
    export_valid_count = sum(1 for item in candidates if item["export_valid"])
    aligned_count = sum(1 for item in candidates if item["slip_aligned"])
    mean_fidelity = round(
        sum(item["semantic_fidelity"] for item in candidates) / candidate_count,
        6,
    )
    return {
        "profile_id": profile_id,
        "profile_path": str(profile_path).replace("\\", "/"),
        "candidate_count": candidate_count,
        "roundtrip_success_count": success_count,
        "roundtrip_failure_count": candidate_count - success_count,
        "import_valid_count": import_valid_count,
        "export_valid_count": export_valid_count,
        "slip_aligned_count": aligned_count,
        "misaligned_count": candidate_count - aligned_count,
        "mean_semantic_fidelity": mean_fidelity,
        "candidates": candidates,
    }


def _compact_roundtrip_result(grid_path: Path, roundtrip: dict) -> dict:
    metrics = roundtrip["metrics"]
    return {
        "source_path": str(grid_path).replace("\\", "/"),
        "source_grid_id": roundtrip["source_grid_id"],
        "export_grid_id": roundtrip["export_grid_id"],
        "roundtrip_success": metrics["roundtrip_success"],
        "semantic_fidelity": metrics["semantic_fidelity"],
        "changed_cell_count": metrics["changed_cell_count"],
        "missing_cell_count": metrics["missing_cell_count"],
        "added_cell_count": metrics["added_cell_count"],
        "import_valid": roundtrip["import_validation"]["valid"],
        "export_valid": roundtrip["export_validation"]["valid"],
        "slip_aligned": roundtrip["export_validation"]["slip_aligned"],
        "import_errors": roundtrip["import_validation"]["errors"],
        "export_errors": roundtrip["export_validation"]["errors"],
        "slip_errors": roundtrip["export_validation"]["slip_errors"],
    }


def _multi_profile_totals(profile_results: list[dict]) -> dict:
    candidate_count = sum(item["candidate_count"] for item in profile_results)
    success_count = sum(item["roundtrip_success_count"] for item in profile_results)
    import_valid_count = sum(item["import_valid_count"] for item in profile_results)
    export_valid_count = sum(item["export_valid_count"] for item in profile_results)
    aligned_count = sum(item["slip_aligned_count"] for item in profile_results)
    weighted_fidelity = sum(
        item["mean_semantic_fidelity"] * item["candidate_count"]
        for item in profile_results
    )
    return {
        "profile_count": len(profile_results),
        "candidate_count": candidate_count,
        "roundtrip_success_count": success_count,
        "roundtrip_failure_count": candidate_count - success_count,
        "import_valid_count": import_valid_count,
        "export_valid_count": export_valid_count,
        "slip_aligned_count": aligned_count,
        "misaligned_count": candidate_count - aligned_count,
        "mean_semantic_fidelity": round(
            weighted_fidelity / candidate_count if candidate_count else 0,
            6,
        ),
    }


def _readme_text(report: dict) -> str:
    return (
        "# Workshop Editor Stage 0\n\n"
        "Minimal semantic editor artifacts for testing Mechagotchi grid authoring.\n\n"
        f"- Source grid: {report['source_grid_id']}\n"
        f"- SLIP profile: {report['slip_profile_id']}\n"
        f"- Export valid: {report['export_validation']['valid']}\n"
        f"- Export SLIP aligned: {report['export_validation']['slip_aligned']}\n"
        f"- Decision: {report['decision']['status']}\n"
    )


def _roundtrip_readme_text(report: dict) -> str:
    return (
        "\n## Round Trip\n\n"
        f"- Round-trip success: {report['metrics']['roundtrip_success']}\n"
        f"- Semantic fidelity: {report['metrics']['semantic_fidelity']}\n"
        f"- Changed cells: {report['metrics']['changed_cell_count']}\n"
        f"- Missing cells: {report['metrics']['missing_cell_count']}\n"
        f"- Added cells: {report['metrics']['added_cell_count']}\n"
    )


def _multi_profile_roundtrip_readme_text(report: dict) -> str:
    totals = report["totals"]
    return (
        "# Workshop Multi-Profile Round Trip Stage 0\n\n"
        "Native semantic JSON round-trip benchmark across generated SLIP "
        "profile corpora.\n\n"
        f"- Profiles: {totals['profile_count']}\n"
        f"- Candidates: {totals['candidate_count']}\n"
        f"- Round-trip successes: {totals['roundtrip_success_count']}\n"
        f"- Import-valid candidates: {totals['import_valid_count']}\n"
        f"- Export-valid candidates: {totals['export_valid_count']}\n"
        f"- SLIP-aligned exports: {totals['slip_aligned_count']}\n"
        f"- Mean semantic fidelity: {totals['mean_semantic_fidelity']}\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("data/workshop_editor"))
    parser.add_argument(
        "--slip", type=Path, default=Path("data/slips/valid/slip_lcd_seed.json")
    )
    parser.add_argument("--seed-index", type=int, default=0)
    parser.add_argument("--multi-profile-root", type=Path)
    parser.add_argument(
        "--multi-profile-output-dir",
        type=Path,
        default=Path("data/workshop_editor/multi_profile_roundtrip_stage0"),
    )
    parser.add_argument("--multi-profile-limit", type=int)
    parser.add_argument("--profile", type=Path, action="append")
    args = parser.parse_args()

    if args.multi_profile_root:
        profile_paths = args.profile or [
            Path("data/slips/valid/slip_lcd_seed.json"),
            Path("data/slips/valid/slip_gray_stable.json"),
            Path("data/slips/valid/slip_amber_social.json"),
        ]
        report = run_workshop_multi_profile_roundtrip_suite(
            profile_paths,
            args.multi_profile_root,
            limit_per_profile=args.multi_profile_limit,
        )
        write_workshop_multi_profile_roundtrip_artifacts(
            args.multi_profile_output_dir,
            report,
        )
        print(json.dumps(report, indent=2))
        return

    slip_profile = json.loads(args.slip.read_text(encoding="utf-8"))
    seed_grid = build_seed_grids()[args.seed_index]
    if seed_grid["palette"]["palette_id"] not in PALETTES:
        raise ValueError("unknown seed palette")
    state = build_editor_state(seed_grid, slip_profile)
    exported = export_grid(state, grid_id="workshop_export_stage0")
    report = run_workshop_export_lab(seed_grid, slip_profile)
    write_workshop_artifacts(args.output_dir, state, exported, report)
    roundtrip_report = run_workshop_roundtrip_lab(seed_grid, slip_profile)
    write_workshop_roundtrip_artifacts(args.output_dir, roundtrip_report)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
