import argparse
import hashlib
import json
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
from workshop_editor import compare_semantic_grid_fidelity


SIDECAR_VERSION = "0.1.0"
REPORT_PATH = Path("data/workshop_editor/external_metadata_sidecar_stage0.json")
SIDECAR_DATA_PATH = Path("data/workshop_editor/external_metadata_sidecar_data.js")

FORMAT_POLICIES = {
    "png": {
        "media_type": "image/png",
        "semantic_policy": "sidecar_required",
        "native_semantic_capacity": "pixels_only_no_mechagotchi_organs",
        "code_reuse_policy": "standard_format_safe_to_decode_later",
        "anchor": "W3C PNG specification",
    },
    "spritesheet_png": {
        "media_type": "image/png",
        "semantic_policy": "sidecar_required",
        "native_semantic_capacity": "frames_and_pixels_only_no_semantic_cells",
        "code_reuse_policy": "standard_format_safe_to_decode_later",
        "anchor": "W3C PNG specification",
    },
    "piskel_project": {
        "media_type": "application/json",
        "semantic_policy": "sidecar_required",
        "native_semantic_capacity": "sprite_project_data_not_mechagotchi_schema",
        "code_reuse_policy": "study_reference_possible_apache_2_review_before_embedding",
        "anchor": "Piskel GitHub",
    },
    "pixelorama_pxo": {
        "media_type": "application/octet-stream",
        "semantic_policy": "sidecar_required",
        "native_semantic_capacity": "editor_project_metadata_not_mechagotchi_schema",
        "code_reuse_policy": "study_and_interop_possible_mit_review_before_embedding",
        "anchor": "Pixelorama documentation",
    },
    "libresprite_project": {
        "media_type": "application/octet-stream",
        "semantic_policy": "sidecar_required",
        "native_semantic_capacity": "animation_project_data_not_mechagotchi_schema",
        "code_reuse_policy": "study_only_do_not_embed",
        "anchor": "LibreSprite GitHub",
    },
}


def build_external_asset_stub(grid: dict, format_id: str) -> dict:
    if format_id not in FORMAT_POLICIES:
        raise ValueError(f"unsupported external format: {format_id}")
    width, height = grid["grid_size"]
    policy = FORMAT_POLICIES[format_id]
    return {
        "asset_id": f"{grid['grid_id']}.{format_id}",
        "format_id": format_id,
        "media_type": policy["media_type"],
        "uri": f"external://workshop/{grid['grid_id']}.{format_id}",
        "width": width,
        "height": height,
        "frame_count": 1,
        "content_hash": _hash_payload(_render_payload(grid)),
        "semantic_policy": policy["semantic_policy"],
    }


def build_sidecar_for_grid(grid: dict, slip_profile: dict, asset: dict) -> dict:
    semantic_overlay = {
        "cells": deepcopy(grid.get("cells", [])),
        "organs": deepcopy(grid.get("organs", {})),
        "palette": deepcopy(grid.get("palette", {})),
        "mutation": deepcopy(grid.get("mutation", {})),
        "lineage": deepcopy(grid.get("lineage", {})),
        "metadata": deepcopy(grid.get("metadata", {})),
    }
    profile_snapshot = deepcopy(slip_profile)
    pixel_bindings = _pixel_bindings(grid)
    semantic_hash = _hash_payload(semantic_overlay)
    profile_hash = _hash_payload(profile_snapshot)
    return {
        "sidecar_version": SIDECAR_VERSION,
        "sidecar_id": f"{grid['grid_id']}_external_sidecar",
        "asset_binding": {
            "asset_id": asset["asset_id"],
            "format_id": asset["format_id"],
            "media_type": asset["media_type"],
            "uri": asset["uri"],
            "width": asset["width"],
            "height": asset["height"],
            "frame_count": asset["frame_count"],
            "content_hash": asset["content_hash"],
            "semantic_policy": "sidecar_required",
        },
        "grid_contract": {
            "grid_id": grid["grid_id"],
            "schema_version": grid["schema_version"],
            "grid_size": deepcopy(grid["grid_size"]),
            "cell_count": len(grid.get("cells", [])),
            "semantic_cell_encoding": "coordinate_overlay_v1",
            "pixel_binding_count": len(pixel_bindings),
        },
        "slip_binding": {
            "profile_id": slip_profile["profile_id"],
            "slip_version": slip_profile["slip_version"],
            "profile_hash": profile_hash,
            "profile_snapshot": profile_snapshot,
        },
        "semantic_overlay": semantic_overlay,
        "pixel_bindings": pixel_bindings,
        "integrity": {
            "asset_content_hash": asset["content_hash"],
            "semantic_overlay_hash": semantic_hash,
            "profile_hash": profile_hash,
            "binding_hash": _hash_payload(
                {
                    "asset_hash": asset["content_hash"],
                    "semantic_hash": semantic_hash,
                    "profile_hash": profile_hash,
                }
            ),
        },
        "limitations": [
            "Sidecar strategy only: decoder labs are tracked as separate evidence.",
            "Sidecar strategy only: semantic metadata must travel with the asset.",
        ],
    }


def validate_sidecar_binding(sidecar: dict, asset: dict) -> dict:
    errors = []
    if sidecar.get("sidecar_version") != SIDECAR_VERSION:
        errors.append(_error("sidecar_version", "unsupported_sidecar_version"))

    binding = sidecar.get("asset_binding", {})
    grid_contract = sidecar.get("grid_contract", {})
    if binding.get("asset_id") != asset.get("asset_id"):
        errors.append(_error("asset_binding.asset_id", "asset_id_mismatch"))
    if binding.get("format_id") != asset.get("format_id"):
        errors.append(_error("asset_binding.format_id", "asset_format_mismatch"))
    if binding.get("content_hash") != asset.get("content_hash"):
        errors.append(_error("asset_binding.content_hash", "asset_hash_mismatch"))
    if binding.get("width") != asset.get("width") or binding.get("height") != asset.get("height"):
        errors.append(_error("asset_binding.dimensions", "asset_dimension_mismatch"))
    if binding.get("frame_count") != asset.get("frame_count"):
        errors.append(_error("asset_binding.frame_count", "asset_frame_count_mismatch"))

    grid_size = grid_contract.get("grid_size", [])
    if len(grid_size) == 2 and (
        grid_size[0] != binding.get("width") or grid_size[1] != binding.get("height")
    ):
        errors.append(_error("grid_contract.grid_size", "grid_asset_size_mismatch"))

    overlay = sidecar.get("semantic_overlay", {})
    profile = sidecar.get("slip_binding", {}).get("profile_snapshot", {})
    profile_validation = validate_authoring_draft(profile) if profile else {"ok": False}
    if not profile_validation["ok"]:
        errors.append(_error("slip_binding.profile_snapshot", "profile_validation_failed"))

    coordinate_errors = _coordinate_errors(overlay.get("cells", []), grid_size)
    errors.extend(coordinate_errors)
    if not errors:
        restored = restore_grid_from_sidecar(sidecar, asset, validate=False)
        grid_validation = validate_grid(restored)
        if not grid_validation.ok:
            errors.extend(_error("$", "restored_grid_invalid", message) for message in grid_validation.errors)
        alignment = is_grid_aligned(restored, profile)
        if not alignment.ok:
            errors.extend(_error("$", "restored_grid_not_slip_aligned", message) for message in alignment.errors)

    return {
        "ok": len(errors) == 0,
        "errors": errors,
        "error_families": sorted({error["family"] for error in errors}),
    }


def restore_grid_from_sidecar(sidecar: dict, asset: dict, *, validate: bool = True) -> dict:
    if validate:
        result = validate_sidecar_binding(sidecar, asset)
        if not result["ok"]:
            raise ValueError(f"invalid sidecar binding: {result['errors']}")

    overlay = sidecar["semantic_overlay"]
    metadata = deepcopy(overlay.get("metadata", {}))
    metadata["source"] = "external_sidecar_restore"
    metadata["external_asset_id"] = asset["asset_id"]
    metadata["sidecar_id"] = sidecar["sidecar_id"]
    return {
        "grid_id": sidecar["grid_contract"]["grid_id"],
        "schema_version": sidecar["grid_contract"]["schema_version"],
        "parent_grid_id": metadata.get("seed_grid_id"),
        "grid_size": deepcopy(sidecar["grid_contract"]["grid_size"]),
        "cells": deepcopy(overlay["cells"]),
        "organs": deepcopy(overlay["organs"]),
        "palette": deepcopy(overlay["palette"]),
        "mutation": deepcopy(overlay["mutation"]),
        "lineage": deepcopy(overlay["lineage"]),
        "metadata": metadata,
    }


def run_external_metadata_sidecar_lab(
    profile_paths: list[Path], generated_root: Path
) -> dict:
    sidecar_results = []
    for profile_path in profile_paths:
        profile = _read_json(profile_path)
        grid_path = _first_grid_path(profile, generated_root)
        grid = _read_json(grid_path)
        asset = build_external_asset_stub(grid, "png")
        sidecar = build_sidecar_for_grid(grid, profile, asset)
        validation = validate_sidecar_binding(sidecar, asset)
        restored = restore_grid_from_sidecar(sidecar, asset)
        diff = compare_semantic_grid_fidelity(grid, restored)
        fidelity = _semantic_fidelity(diff, grid)
        sidecar_results.append(
            {
                "profile_id": profile["profile_id"],
                "profile_path": _portable(profile_path),
                "grid_path": _portable(grid_path),
                "asset": asset,
                "sidecar": sidecar,
                "validation": validation,
                "restored_grid_validation": {
                    "valid": validate_grid(restored).ok,
                    "errors": validate_grid(restored).errors,
                    "slip_aligned": is_grid_aligned(restored, profile).ok,
                    "slip_errors": is_grid_aligned(restored, profile).errors,
                },
                "semantic_diff": diff,
                "semantic_fidelity": fidelity,
            }
        )

    invalid_probes = _invalid_probe_results(sidecar_results[0])
    success_count = sum(
        1
        for result in sidecar_results
        if result["validation"]["ok"]
        and result["restored_grid_validation"]["valid"]
        and result["restored_grid_validation"]["slip_aligned"]
        and result["semantic_fidelity"] == 1.0
    )
    invalid_rejected_count = sum(1 for result in invalid_probes if not result["ok"])
    mean_fidelity = round(
        sum(result["semantic_fidelity"] for result in sidecar_results)
        / max(1, len(sidecar_results)),
        6,
    )
    return {
        "artifact_id": "external_metadata_sidecar_stage0",
        "status": "research_external_metadata_sidecar_strategy_no_package_code",
        "date": "2026-05-12",
        "purpose": (
            "Define and test a JSON sidecar strategy that preserves Mechagotchi "
            "semantic grid metadata when visual assets or third-party project "
            "files cannot natively carry SLIP organs, mutation weights, and "
            "profile constraints."
        ),
        "source_artifacts": [
            "docs/01-brainstorming.md",
            "docs/02-research_plan.md",
            "research/slip/profile_compatibility_tests.md",
            "data/slips/slip_profile_compatibility_matrix_stage0.json",
            "data/slips/multi_profile_generation_stage0/",
            "labs/workshop_editor/workshop_editor.py",
            "labs/workshop_editor/external_metadata_sidecar.py",
        ],
        "external_anchors": [
            {
                "source": "W3C PNG specification",
                "url": "https://www.w3.org/TR/png-3/",
                "used_for": "PNG is treated as a visual carrier; Mechagotchi semantics are kept in a sidecar rather than assumed recoverable from pixels.",
            },
            {
                "source": "Piskel GitHub",
                "url": "https://github.com/piskelapp/piskel",
                "used_for": "Browser sprite-editor project reference; Mechagotchi semantics remain sidecar-bound.",
            },
            {
                "source": "Pixelorama documentation",
                "url": "https://www.pixelorama.org/user_manual/Import/",
                "used_for": "Import/export workflow reference; no assumption that Pixelorama metadata equals Mechagotchi schema.",
            },
            {
                "source": "LibreSprite GitHub",
                "url": "https://github.com/LibreSprite/LibreSprite",
                "used_for": "Animation workflow reference kept study-only because of GPL-oriented reuse constraints.",
            },
        ],
        "profile_count": len(sidecar_results),
        "sidecar_roundtrip_success_count": success_count,
        "invalid_probe_count": len(invalid_probes),
        "invalid_probe_rejected_count": invalid_rejected_count,
        "metrics": {
            "sidecar_roundtrip_success_rate": _ratio(success_count, len(sidecar_results)),
            "mean_semantic_fidelity": mean_fidelity,
            "invalid_probe_rejection_rate": _ratio(
                invalid_rejected_count,
                len(invalid_probes),
            ),
            "adapter_formats_requiring_sidecar": len(
                [item for item in _adapter_matrix() if item["semantic_policy"] == "sidecar_required"]
            ),
        },
        "adapter_matrix": _adapter_matrix(),
        "sidecar_results": sidecar_results,
        "invalid_probe_results": invalid_probes,
        "closed_states": [
            "external_metadata_sidecar_strategy",
            "sidecar_asset_binding_integrity",
            "sidecar_restores_semantic_grid",
            "sidecar_preserves_slip_alignment",
            "format_adapter_policy_matrix",
        ],
        "blocked_states": [
            "png_adam7_interlace_decoder",
            "apng_decoder",
            "full_png_conformance",
            "spritesheet_packed_rotation_trim_decoder",
            "runtime_animation_playback",
            "full_project_format_coverage",
            "embedded_png_metadata_writer",
            "project_file_native_metadata_writer",
            "profile_weighted_evolution",
        ],
        "decision": "prototype_external_metadata_sidecar_strategy",
        "next_research_step": (
            "Run held-out long-horizon behavior tests and manual readability "
            "calibration before profile-weighted evolution claims."
        ),
    }


def write_external_metadata_sidecar_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "external_metadata_sidecar_stage0.json", report)
    _write_json(output_dir / "adapter_matrix.json", report["adapter_matrix"])
    for result in report["sidecar_results"]:
        _write_json(
            output_dir / f"{result['profile_id']}_external_sidecar.json",
            result["sidecar"],
        )
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")
    (output_dir / "external_metadata_sidecar_data.js").write_text(
        "window.MECHAGOTCHI_EXTERNAL_METADATA_SIDECAR = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )


def _adapter_matrix() -> list[dict]:
    return [
        {"format_id": format_id, **deepcopy(policy)}
        for format_id, policy in FORMAT_POLICIES.items()
    ]


def _pixel_bindings(grid: dict) -> list[dict]:
    width, height = grid["grid_size"]
    cells_by_coordinate = {
        (cell["x"], cell["y"]): cell for cell in grid.get("cells", [])
    }
    bindings = []
    for y in range(height):
        for x in range(width):
            cell = cells_by_coordinate.get((x, y))
            bindings.append(
                {
                    "coordinate": [x, y],
                    "frame_index": 0,
                    "semantic_cell_present": cell is not None,
                    "organ": cell.get("organ") if cell else None,
                    "role": cell.get("role") if cell else "empty",
                }
            )
    return bindings


def _render_payload(grid: dict) -> dict:
    width, height = grid["grid_size"]
    background = grid["palette"]["colors"][grid["palette"].get("background_index", 0)]
    cells_by_coordinate = {
        (cell["x"], cell["y"]): cell for cell in grid.get("cells", [])
    }
    pixels = []
    for y in range(height):
        for x in range(width):
            cell = cells_by_coordinate.get((x, y))
            pixels.append(
                {
                    "x": x,
                    "y": y,
                    "visual": cell.get("visual", background) if cell else background,
                }
            )
    return {
        "grid_size": deepcopy(grid["grid_size"]),
        "palette_id": grid["palette"]["palette_id"],
        "pixels": pixels,
    }


def _coordinate_errors(cells: list[dict], grid_size: list[int]) -> list[dict]:
    errors = []
    if len(grid_size) != 2:
        return [_error("grid_contract.grid_size", "grid_size_invalid")]
    width, height = grid_size
    seen = set()
    for cell in cells:
        coordinate = (cell.get("x"), cell.get("y"))
        if coordinate in seen:
            errors.append(_error("semantic_overlay.cells", "duplicate_semantic_cell"))
        seen.add(coordinate)
        if not isinstance(coordinate[0], int) or not isinstance(coordinate[1], int):
            errors.append(_error("semantic_overlay.cells", "coordinate_type_invalid"))
        elif coordinate[0] < 0 or coordinate[1] < 0 or coordinate[0] >= width or coordinate[1] >= height:
            errors.append(_error("semantic_overlay.cells", "coordinate_out_of_bounds"))
    return errors


def _invalid_probe_results(reference_result: dict) -> list[dict]:
    sidecar = reference_result["sidecar"]
    asset = reference_result["asset"]
    wrong_hash_asset = {**asset, "content_hash": "sha256:not-the-bound-asset"}
    wrong_size_asset = {**asset, "width": asset["width"] + 1}
    return [
        validate_sidecar_binding(sidecar, wrong_hash_asset),
        validate_sidecar_binding(sidecar, wrong_size_asset),
    ]


def _first_grid_path(profile: dict, generated_root: Path) -> Path:
    grid_paths = sorted((generated_root / profile["profile_id"]).glob("*.json"))
    if not grid_paths:
        raise ValueError(f"no generated grids found for profile: {profile['profile_id']}")
    return grid_paths[0]


def _semantic_fidelity(diff: dict, source: dict) -> float:
    source_count = max(1, len(source.get("cells", [])))
    problem_count = (
        len(diff["changed_cells"])
        + len(diff["missing_cells"])
        + len(diff["added_cells"])
    )
    return round(max(0.0, 1.0 - problem_count / source_count), 6)


def _hash_payload(payload: object) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _error(path: str, family: str, message: str | None = None) -> dict:
    return {
        "path": path,
        "family": family,
        "message": message or family.replace("_", " "),
    }


def _app_payload(report: dict) -> dict:
    return {
        "report": {
            key: report[key]
            for key in [
                "artifact_id",
                "status",
                "profile_count",
                "sidecar_roundtrip_success_count",
                "invalid_probe_count",
                "invalid_probe_rejected_count",
                "metrics",
                "closed_states",
                "blocked_states",
                "decision",
            ]
        },
        "adapter_matrix": report["adapter_matrix"],
        "sidecar_summaries": [
            {
                "profile_id": result["profile_id"],
                "asset": result["asset"],
                "semantic_fidelity": result["semantic_fidelity"],
                "validation": result["validation"],
            }
            for result in report["sidecar_results"]
        ],
    }


def _readme_text(report: dict) -> str:
    metrics = report["metrics"]
    return (
        "# External Metadata Sidecar Stage 0\n\n"
        "JSON sidecar strategy for preserving Mechagotchi semantic grid "
        "metadata across non-native visual assets and third-party project files.\n\n"
        f"- Profiles: {report['profile_count']}\n"
        f"- Sidecar round-trip successes: {report['sidecar_roundtrip_success_count']}\n"
        f"- Invalid probes rejected: {report['invalid_probe_rejected_count']}"
        f"/{report['invalid_probe_count']}\n"
        f"- Mean semantic fidelity: {metrics['mean_semantic_fidelity']}\n"
        f"- Adapter formats requiring sidecar: {metrics['adapter_formats_requiring_sidecar']}\n"
        f"- Decision: {report['decision']}\n"
    )


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _portable(path: Path) -> str:
    return str(path).replace("\\", "/")


def _ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 6)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/workshop_editor/external_metadata_sidecar_stage0"),
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
    report = run_external_metadata_sidecar_lab(profile_paths, args.generated_root)
    write_external_metadata_sidecar_artifacts(args.output_dir, report)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _write_json(REPORT_PATH, report)
    SIDECAR_DATA_PATH.write_text(
        "window.MECHAGOTCHI_EXTERNAL_METADATA_SIDECAR = "
        + json.dumps(_app_payload(report), indent=2)
        + ";\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
