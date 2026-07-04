"""Genome contract probe driver executed against the package import surface.

Traceability: research/package_specs/mecha_engine_genome_contract_gate.md and
research/package_specs/mecha_engine_property_negative_test_strategy.md (P1,
P2, genome metamorphic checks). ``tests/test_genome_contract.py`` launches
this script in a subprocess whose PYTHONPATH points at the package ``src``
directory (the same documented import mechanics as
``tests/test_package_imports.py``), so every probe below exercises
``mecha_engine.genome`` — never repository-root or research lab modules —
and the test module itself never touches the interpreter module search path.

The driver prints a single JSON report on stdout; the unittest module
asserts on it. Fixture corpora come from the repository paths fixed by
research/package_specs/mecha_engine_test_fixture_manifest.md:
``data/seed_grids/*.json`` and ``data/invalid_grids/*.json``.
"""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path

from mecha_engine.genome import (
    REQUIRED_TOP_LEVEL_FIELDS,
    grid_signature,
    render_packet_from_grid,
    validate_grid,
    validate_grid_file,
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _result_payload(result) -> dict:
    return {"ok": result.ok, "errors": list(result.errors)}


def probe_corpus(seed_dir: Path, invalid_dir: Path) -> dict:
    """P2 fixture regression: full frozen corpora through the package API."""
    report: dict = {
        "seed_total": 0,
        "seed_accepted": 0,
        "invalid_total": 0,
        "invalid_rejected": 0,
        "rejected_seed_files": [],
        "accepted_invalid_files": [],
        "mutated_input_files": [],
        "file_api_mismatch_files": [],
        "revalidation_mismatch_files": [],
        "empty_error_invalid_files": [],
        "seed_render_packets_built": 0,
        "seed_render_packet_failures": [],
        "seed_signature_nondeterministic_files": [],
    }

    for path in sorted(seed_dir.glob("*.json")):
        report["seed_total"] += 1
        grid = _load(path)
        pristine = deepcopy(grid)
        result = validate_grid(grid)
        if result.ok:
            report["seed_accepted"] += 1
        else:
            report["rejected_seed_files"].append(
                {"file": path.name, "errors": list(result.errors)}
            )
        if validate_grid(grid).errors != result.errors:
            report["revalidation_mismatch_files"].append(path.name)
        file_result = validate_grid_file(path)
        if (file_result.ok, file_result.errors) != (result.ok, result.errors):
            report["file_api_mismatch_files"].append(path.name)
        if grid_signature(grid) != grid_signature(deepcopy(grid)):
            report["seed_signature_nondeterministic_files"].append(path.name)
        try:
            render_packet_from_grid(grid)
            report["seed_render_packets_built"] += 1
        except ValueError as error:
            report["seed_render_packet_failures"].append(
                {"file": path.name, "error": str(error)}
            )
        if grid != pristine:
            report["mutated_input_files"].append(path.name)

    for path in sorted(invalid_dir.glob("*.json")):
        report["invalid_total"] += 1
        grid = _load(path)
        pristine = deepcopy(grid)
        result = validate_grid(grid)
        if not result.ok:
            report["invalid_rejected"] += 1
        else:
            report["accepted_invalid_files"].append(path.name)
        if not result.ok and not result.errors:
            report["empty_error_invalid_files"].append(path.name)
        if validate_grid(grid).errors != result.errors:
            report["revalidation_mismatch_files"].append(path.name)
        file_result = validate_grid_file(path)
        if (file_result.ok, file_result.errors) != (result.ok, result.errors):
            report["file_api_mismatch_files"].append(path.name)
        if grid != pristine:
            report["mutated_input_files"].append(path.name)

    return report


def probe_ordinary_invalid_payloads() -> list[dict]:
    """Structured errors without throwing for ordinary invalid payloads."""
    payloads = {
        "empty_object": {},
        "wrong_value_types": {
            "grid_id": 17,
            "schema_version": 1,
            "grid_size": "8x8",
            "cells": "not-a-list",
            "organs": [],
            "palette": 7,
            "mutation": [],
        },
        "cell_entries_not_objects": {
            "grid_id": "probe_grid",
            "schema_version": "0.1.0",
            "grid_size": [8, 8],
            "cells": ["cell", 3, None],
            "organs": {},
            "palette": {"palette_id": "probe_palette", "colors": ["#000000", "#ffffff"]},
            "mutation": {},
        },
    }
    outcomes = []
    for name, payload in payloads.items():
        pristine = deepcopy(payload)
        raised: str | None = None
        ok = None
        error_count = 0
        try:
            result = validate_grid(payload)
            ok = result.ok
            error_count = len(result.errors)
        except Exception as error:  # contract: must not throw
            raised = f"{type(error).__name__}: {error}"
        outcomes.append(
            {
                "name": name,
                "ok": ok,
                "error_count": error_count,
                "raised": raised,
                "mutated": payload != pristine,
            }
        )
    return outcomes


def probe_schema_alignment(schema_path: Path, seed_grid: dict) -> dict:
    """Schema Acceptance: 2020-12 contract and schema/semantic alignment."""
    schema = _load(schema_path)
    removal_failures: dict[str, bool] = {}
    for field in schema.get("required", []):
        variant = deepcopy(seed_grid)
        variant.pop(field, None)
        removal_failures[field] = not validate_grid(variant).ok
    return {
        "schema_draft": schema.get("$schema"),
        "schema_required": schema.get("required", []),
        "package_required": list(REQUIRED_TOP_LEVEL_FIELDS),
        "schema_version_const": schema.get("properties", {})
        .get("schema_version", {})
        .get("const"),
        "required_field_removal_fails": removal_failures,
    }


def _occupied(grid: dict) -> set[tuple[int, int]]:
    return {(cell["x"], cell["y"]) for cell in grid["cells"]}


def _free_isolated_coordinate(grid: dict, avoid: set[tuple[int, int]]) -> tuple[int, int]:
    width, height = grid["grid_size"]
    occupied = _occupied(grid)
    for y in range(height):
        for x in range(width):
            point = (x, y)
            if point in occupied:
                continue
            neighborhood = {
                (x + dx, y + dy)
                for dx in (-1, 0, 1)
                for dy in (-1, 0, 1)
                if (dx, dy) != (0, 0)
            }
            if neighborhood.isdisjoint(avoid):
                return point
    raise RuntimeError("no isolated free coordinate available in fixture grid")


def _required_body_core(grid: dict) -> tuple[str, dict]:
    for name, organ in grid["organs"].items():
        if organ.get("role") == "body_core" and organ.get("required") is True:
            return name, organ
    raise RuntimeError("fixture grid has no required body core")


def build_single_fault_variants(seed_grid: dict) -> list[tuple[str, dict, str]]:
    """P1 single-fault derivation: (fault_id, variant, expected error text)."""
    variants: list[tuple[str, dict, str]] = []

    def variant() -> dict:
        return deepcopy(seed_grid)

    faulted = variant()
    faulted["cells"][0]["x"] = faulted["grid_size"][0]
    variants.append(("coordinate_out_of_bounds", faulted, "cell out of bounds"))

    faulted = variant()
    faulted["cells"].append(deepcopy(faulted["cells"][0]))
    variants.append(("duplicate_occupied_coordinate", faulted, "duplicate coordinate"))

    faulted = variant()
    faulted["cells"][0]["role"] = "wing"
    variants.append(("unknown_semantic_role", faulted, "cell role is unknown"))

    faulted = variant()
    faulted["cells"][0]["material"] = "plasma"
    variants.append(("unknown_material", faulted, "cell material is unknown"))

    faulted = variant()
    faulted["mutation"]["cell_mutation_rate"] = -0.2
    variants.append(("mutation_weight_below_minimum", faulted, "outside 0..1"))

    faulted = variant()
    faulted["mutation"]["cell_mutation_rate"] = 1.2
    variants.append(("mutation_weight_above_maximum", faulted, "outside 0..1"))

    faulted = variant()
    faulted["cells"][0]["mutation_weight"] = 1.5
    variants.append(("cell_mutation_weight_above_maximum", faulted, "outside 0..1"))

    faulted = variant()
    for cell in faulted["cells"]:
        cell["animation_anchor"] = False
    variants.append(("missing_animation_anchor", faulted, "missing animation anchor"))

    faulted = variant()
    faulted["organs"] = {
        name: organ
        for name, organ in faulted["organs"].items()
        if organ.get("role") == "body_core"
    }
    variants.append(
        (
            "missing_required_sensor_or_expression",
            faulted,
            "missing required sensor or expression organ",
        )
    )

    faulted = variant()
    core_name, core = _required_body_core(faulted)
    missing_point = _free_isolated_coordinate(faulted, avoid=set())
    core["cells"].append(list(missing_point))
    variants.append(("organ_references_absent_cell", faulted, "references missing cell"))

    faulted = variant()
    core_name, core = _required_body_core(faulted)
    core["cells"] = core["cells"][:3]
    variants.append(("body_mass_below_minimum", faulted, "body mass below minimum"))

    faulted = variant()
    core_name, core = _required_body_core(faulted)
    kept_points = {tuple(point) for point in core["cells"][:-1]}
    moved_from = tuple(core["cells"][-1])
    far_point = _free_isolated_coordinate(faulted, avoid=kept_points)
    for cell in faulted["cells"]:
        if (cell["x"], cell["y"]) == moved_from:
            cell["x"], cell["y"] = far_point
            break
    core["cells"][-1] = list(far_point)
    variants.append(
        ("disconnected_required_body_core", faulted, "required body core is disconnected")
    )

    faulted = variant()
    faulted["palette"]["colors"][0] = "not-a-color"
    variants.append(("palette_color_not_hex", faulted, "palette color must be #RRGGBB hex"))

    faulted = variant()
    faulted["palette"]["palette_id"] = "Bad Palette Id"
    variants.append(("palette_id_invalid", faulted, "palette_id must match"))

    faulted = variant()
    faulted["grid_size"] = [4, 8]
    variants.append(("grid_size_outside_schema_range", faulted, "grid_size dimension outside"))

    faulted = variant()
    faulted["schema_version"] = "0.2.0"
    variants.append(("schema_version_mismatch", faulted, "schema_version must be"))

    faulted = variant()
    faulted["grid_id"] = "Bad Id"
    variants.append(("grid_id_pattern_violation", faulted, "grid_id must match"))

    return variants


def probe_single_faults(seed_grid: dict) -> list[dict]:
    outcomes = []
    for fault_id, faulted, expected_error in build_single_fault_variants(seed_grid):
        pristine = deepcopy(faulted)
        result = validate_grid(faulted)
        outcomes.append(
            {
                "fault": fault_id,
                "rejected": not result.ok,
                "expected_error_present": any(
                    expected_error in error for error in result.errors
                ),
                "errors": list(result.errors),
                "mutated": faulted != pristine,
            }
        )
    return outcomes


def probe_signature(seed_grid: dict) -> dict:
    base = grid_signature(seed_grid)
    roundtrip = grid_signature(json.loads(json.dumps(seed_grid)))

    def changed(mutate) -> bool:
        variant = deepcopy(seed_grid)
        mutate(variant)
        return grid_signature(variant) != base

    def unchanged(mutate) -> bool:
        variant = deepcopy(seed_grid)
        mutate(variant)
        return grid_signature(variant) == base

    def _reorder(variant: dict) -> None:
        reordered = {key: variant[key] for key in sorted(variant, reverse=True)}
        variant.clear()
        variant.update(reordered)

    def _bump_coordinate(variant: dict) -> None:
        variant["cells"][0]["x"] = variant["cells"][0]["x"] + 1

    def _metadata(variant: dict) -> None:
        variant["metadata"] = {
            "notes": "review pass two",
            "timestamp": "2026-07-04T00:00:00Z",
            "reviewer": "reviewer-2",
        }

    pristine = deepcopy(seed_grid)
    grid_signature(seed_grid)
    return {
        "deterministic": grid_signature(seed_grid) == base,
        "json_roundtrip_stable": roundtrip == base,
        "input_mutated": seed_grid != pristine,
        "changes_on": {
            "cell_coordinates": changed(_bump_coordinate),
            "cell_role": changed(
                lambda variant: variant["cells"][0].__setitem__("role", "shell")
            ),
            "cell_organ": changed(
                lambda variant: variant["cells"][0].__setitem__("organ", "other_organ")
            ),
            "palette_id": changed(
                lambda variant: variant["palette"].__setitem__(
                    "palette_id", "other_palette"
                )
            ),
            "palette_colors": changed(
                lambda variant: variant["palette"]["colors"].__setitem__(0, "#123456")
            ),
            "grid_size": changed(
                lambda variant: variant.__setitem__("grid_size", [16, 16])
            ),
            "schema_version": changed(
                lambda variant: variant.__setitem__("schema_version", "0.2.0")
            ),
        },
        "ignores": {
            "reviewer_metadata": unchanged(_metadata),
            "top_level_key_order": unchanged(_reorder),
        },
    }


def probe_render_packet(seed_grid: dict, invalid_grid: dict) -> dict:
    grid = deepcopy(seed_grid)
    pristine = deepcopy(grid)
    packet = render_packet_from_grid(grid)
    state = {"pose": "idle", "tick": 3}
    state_pristine = deepcopy(state)
    stateful_packet = render_packet_from_grid(grid, state)

    packet["cells"][0]["x"] = 999
    packet["palette"]["palette_id"] = "aliased"
    stateful_packet["state"]["tick"] = 999

    invalid_rejected = False
    invalid_error = None
    try:
        render_packet_from_grid(deepcopy(invalid_grid))
    except ValueError as error:
        invalid_rejected = True
        invalid_error = str(error)

    fresh_packet = render_packet_from_grid(grid, state)
    try:
        serialized = json.dumps(fresh_packet)
        json_serializable = True
    except (TypeError, ValueError):
        serialized = ""
        json_serializable = False

    return {
        "keys": sorted(fresh_packet),
        "grid_id_matches": fresh_packet["grid_id"] == pristine["grid_id"],
        "cell_count_matches": len(fresh_packet["cells"]) == len(pristine["cells"]),
        "stateless_state_is_null": render_packet_from_grid(grid)["state"] is None,
        "state_passthrough": fresh_packet["state"] == state_pristine,
        "json_serializable": json_serializable,
        "json_roundtrip_equal": json_serializable
        and json.loads(serialized) == fresh_packet,
        "grid_not_mutated": grid == pristine,
        "state_not_mutated": state == state_pristine,
        "invalid_grid_rejected": invalid_rejected,
        "invalid_grid_error": invalid_error,
    }


def probe_loaded_lab_modules() -> list[str]:
    lab_root = "la" "bs"
    return sorted(
        name
        for name in sys.modules
        if name == lab_root or name.startswith(lab_root + ".")
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()

    seed_dir = repo_root / "data" / "seed_grids"
    invalid_dir = repo_root / "data" / "invalid_grids"
    schema_path = repo_root / "research" / "grid_genome" / "grid_genome.schema.json"

    seed_grid = _load(sorted(seed_dir.glob("*.json"))[0])
    invalid_grid = _load(sorted(invalid_dir.glob("*.json"))[0])

    report = {
        "corpus": probe_corpus(seed_dir, invalid_dir),
        "ordinary_invalid_payloads": probe_ordinary_invalid_payloads(),
        "schema": probe_schema_alignment(schema_path, seed_grid),
        "single_faults": probe_single_faults(seed_grid),
        "signature": probe_signature(seed_grid),
        "render_packet": probe_render_packet(seed_grid, invalid_grid),
        "lab_modules_loaded": probe_loaded_lab_modules(),
    }
    json.dump(report, sys.stdout)


if __name__ == "__main__":
    main()
