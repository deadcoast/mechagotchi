"""Generation contract probe driver executed against the package surface.

Traceability: research/package_specs/mecha_engine_generation_contract_gate.md
("Model Acceptance", "Candidate Acceptance", "Batch Acceptance",
"SLIP Acceptance", "Explanation Acceptance", "Negative Checks") and
research/package_specs/mecha_engine_property_negative_test_strategy.md (P3,
invalid-parent propagation, deterministic batches, generation metamorphic
checks). ``tests/test_generation_contract.py`` launches this script in a
subprocess whose PYTHONPATH points at the package ``src`` directory (the
same documented import mechanics as ``tests/test_package_imports.py``), so
every probe exercises ``mecha_engine.generation`` and validates candidates
through ``mecha_engine.genome`` — never repository-root or research lab
modules — and the test module itself never touches the interpreter module
search path.

The driver prints a single JSON report on stdout; the unittest module
asserts on it. Fixtures are the frozen repository corpora fixed by the test
fixture manifest: ``data/seed_grids/*.json`` (50),
``data/invalid_grids/*.json`` (200), and the valid SLIP profile
``data/slips/valid/slip_lcd_seed.json``.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from copy import deepcopy
from pathlib import Path

import mecha_engine.generation as generation_module
from mecha_engine.generation import (
    GenerationModel,
    explain_generation,
    generate_batch,
    generate_candidate,
    train_generation_model,
)
from mecha_engine.genome import grid_signature, validate_grid


GRID_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]{2,63}$")

REQUIRED_EXPLANATION_FIELDS = [
    "grid_id",
    "parent_grid_id",
    "generator_strategy",
    "rng_seed",
    "mutation_events",
    "validation",
    "slip_alignment",
    "accepted_proposals",
    "rejected_proposals",
]

SLIP_RATE_CAP_KEYS = {
    "cell_mutation_rate": "cell_mutation_rate_max",
    "organ_shift_rate": "organ_shift_rate_max",
    "palette_shift_rate": "palette_shift_rate_max",
    "symmetry_break_rate": "symmetry_break_rate_max",
}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _raised_message(callable_probe) -> str | None:
    try:
        callable_probe()
    except ValueError as error:
        return str(error)
    except Exception as error:  # unexpected exception type is trace-worthy
        return f"UNEXPECTED {type(error).__name__}: {error}"
    return None


def _model_surface(model: GenerationModel) -> tuple:
    return (model.width, model.height, model.adjacency, model.token_counts,
            model.total_pairs, model.metadata)


def _grid_slip_aligned(grid: dict, profile: dict) -> bool:
    """Driver-side structural alignment oracle, independent of package internals."""
    if grid["palette"]["palette_id"] not in profile["grid"]["allowed_palettes"]:
        return False
    body_mass = sum(1 for cell in grid["cells"] if cell.get("organ") == "core")
    if not (
        profile["grid"]["body_mass_min"]
        <= body_mass
        <= profile["grid"]["body_mass_max"]
    ):
        return False
    present_roles = {organ.get("role") for organ in grid["organs"].values()}
    if not set(profile["grid"]["required_organ_roles"]).issubset(present_roles):
        return False
    for rate_key, cap_key in SLIP_RATE_CAP_KEYS.items():
        if grid["mutation"][rate_key] > profile["mutation"][cap_key]:
            return False
    return True


def probe_model(seed_grids: list[dict], invalid_grid: dict) -> dict:
    pristine = deepcopy(seed_grids)
    model = train_generation_model(seed_grids)
    remodel = train_generation_model(seed_grids)

    empty_raised = _raised_message(lambda: train_generation_model([]))
    tainted_corpus = deepcopy(seed_grids[:3]) + [deepcopy(invalid_grid)]
    invalid_raised = _raised_message(lambda: train_generation_model(tainted_corpus))

    return {
        "is_generation_model": isinstance(model, GenerationModel),
        "strategy": model.metadata.get("strategy"),
        "proposal_source": model.metadata.get("proposal_source"),
        "seed_count_recorded": model.metadata.get("seed_count"),
        "seed_grid_ids_match_corpus": model.metadata.get("seed_grid_ids")
        == [grid["grid_id"] for grid in seed_grids],
        "corpus_digest_present": bool(model.metadata.get("seed_corpus_sha256")),
        "total_pairs_positive": model.total_pairs > 0,
        "adjacency_directions": sorted(model.adjacency),
        "training_deterministic": _model_surface(model) == _model_surface(remodel),
        "seeds_mutated": seed_grids != pristine,
        "empty_corpus_raised": empty_raised,
        "invalid_corpus_raised": invalid_raised,
    }


def probe_candidate(seed_grids: list[dict], model: GenerationModel) -> dict:
    parent = seed_grids[0]
    parent_pristine = deepcopy(parent)
    model_pristine = deepcopy(_model_surface(model))

    first = generate_candidate(parent, model, rng_seed=101)
    repeat = generate_candidate(parent, model, rng_seed=101)
    reseeded = generate_candidate(parent, model, rng_seed=202)
    chained = generate_candidate(first, model, rng_seed=303)

    validation = validate_grid(first)
    lineage = first["lineage"]
    parent_lineage = parent_pristine.get("lineage", {})

    broken_parent = deepcopy(parent)
    broken_parent["schema_version"] = "0.9.9"
    invalid_parent_raised = _raised_message(
        lambda: generate_candidate(broken_parent, model, rng_seed=101)
    )
    non_model_raised = _raised_message(
        lambda: generate_candidate(parent, {"width": 8}, rng_seed=101)
    )

    try:
        json_roundtrip_equal = json.loads(json.dumps(first)) == first
    except (TypeError, ValueError):
        json_roundtrip_equal = False

    return {
        "candidate_valid_through_genome": validation.ok,
        "candidate_validation_errors": list(validation.errors),
        "deterministic_repeat_identical": first == repeat,
        "deterministic_repeat_signature_equal": grid_signature(first)
        == grid_signature(repeat),
        "reseeded_differs": reseeded != first
        or reseeded["metadata"]["generation_trace"]["rng_seed"]
        != first["metadata"]["generation_trace"]["rng_seed"],
        "parent_grid_id_preserved": first["parent_grid_id"] == parent_pristine["grid_id"],
        "generation_incremented": lineage["generation"]
        == parent_lineage.get("generation", 0) + 1,
        "ancestor_ids_extend_parent_chain": lineage["ancestor_ids"]
        == [*parent_lineage.get("ancestor_ids", []), parent_pristine["grid_id"]],
        "mutation_events_present": bool(lineage["mutation_events"]),
        "grid_id_pattern_ok": bool(GRID_ID_PATTERN.match(first["grid_id"])),
        "grid_id_stable_across_repeats": first["grid_id"] == repeat["grid_id"],
        "schema_version_preserved": first["schema_version"] == "0.1.0",
        "json_roundtrip_equal": json_roundtrip_equal,
        "chained_generation_incremented": chained["lineage"]["generation"]
        == lineage["generation"] + 1,
        "chained_ancestors_extend_chain": chained["lineage"]["ancestor_ids"]
        == [*lineage["ancestor_ids"], first["grid_id"]],
        "parent_mutated": parent != parent_pristine,
        "model_mutated": deepcopy(_model_surface(model)) != model_pristine,
        "invalid_parent_raised": invalid_parent_raised,
        "non_model_raised": non_model_raised,
    }


def probe_slip_candidate(
    seed_grids: list[dict], model: GenerationModel, profile: dict
) -> dict:
    profile_pristine = deepcopy(profile)
    aligned_parent = next(
        grid
        for grid in seed_grids
        if grid["palette"]["palette_id"] in profile["grid"]["allowed_palettes"]
    )
    misaligned_parent = next(
        grid
        for grid in seed_grids
        if grid["palette"]["palette_id"] not in profile["grid"]["allowed_palettes"]
    )

    candidate = generate_candidate(aligned_parent, model, slip_profile=profile, rng_seed=404)
    trace = candidate["metadata"]["generation_trace"]

    misaligned_raised = _raised_message(
        lambda: generate_candidate(
            misaligned_parent, model, slip_profile=profile, rng_seed=404
        )
    )
    invalid_profile = deepcopy(profile)
    invalid_profile["behavior"]["curiosity"] = 1.2
    invalid_profile_raised = _raised_message(
        lambda: generate_candidate(
            aligned_parent, model, slip_profile=invalid_profile, rng_seed=404
        )
    )

    return {
        "candidate_valid_through_genome": validate_grid(candidate).ok,
        "structurally_aligned": _grid_slip_aligned(candidate, profile_pristine),
        "trace_alignment_checked": trace["slip_alignment"]["checked"] is True,
        "trace_alignment_ok": trace["slip_alignment"]["ok"] is True,
        "trace_alignment_profile_id": trace["slip_alignment"]["profile_id"],
        "misaligned_parent_raised": misaligned_raised,
        "invalid_profile_raised": invalid_profile_raised,
        "profile_mutated": profile != profile_pristine,
    }


def probe_slip_v2(
    seed_grids: list[dict], model: GenerationModel, profile: dict
) -> dict:
    """SLIP v0.2 acceptance (decision record 0013): dual-version validation
    and forbidden-traits enforcement through the generation surface."""
    aligned_parent = next(
        grid
        for grid in seed_grids
        if grid["palette"]["palette_id"] in profile["grid"]["allowed_palettes"]
    )

    def v2_profile(**ladder_fields) -> dict:
        v2 = deepcopy(profile)
        v2["slip_version"] = "0.2.0"
        v2.update(ladder_fields)
        return v2

    full_ladder = v2_profile(
        forbidden_traits={"roles": ["shell"], "materials": ["light"]},
        risk_tolerances={"mutation": 0.6},
        learning_switches={"mutation_risk_scorer": True},
        lineage_preferences={"parent_selection": "fitness_weighted"},
    )
    full_ladder_pristine = deepcopy(full_ladder)
    candidate = generate_candidate(
        aligned_parent, model, slip_profile=full_ladder, rng_seed=404
    )

    v1_with_ladder = deepcopy(profile)
    v1_with_ladder["learning_switches"] = {"mutation_risk_scorer": True}
    version_gate_raised = _raised_message(
        lambda: generate_candidate(
            aligned_parent, model, slip_profile=v1_with_ladder, rng_seed=404
        )
    )

    unknown_version = deepcopy(profile)
    unknown_version["slip_version"] = "1.0.0"
    unknown_version_raised = _raised_message(
        lambda: generate_candidate(
            aligned_parent, model, slip_profile=unknown_version, rng_seed=404
        )
    )

    forbidden_binding_raised = _raised_message(
        lambda: generate_candidate(
            aligned_parent,
            model,
            slip_profile=v2_profile(forbidden_traits={"roles": ["body"]}),
            rng_seed=404,
        )
    )
    contradiction_raised = _raised_message(
        lambda: generate_candidate(
            aligned_parent,
            model,
            slip_profile=v2_profile(forbidden_traits={"roles": ["mouth"]}),
            rng_seed=404,
        )
    )

    return {
        "v2_candidate_valid": validate_grid(candidate).ok,
        "v2_candidate_aligned": _grid_slip_aligned(candidate, full_ladder_pristine),
        "version_gate_raised": version_gate_raised,
        "unknown_version_raised": unknown_version_raised,
        "forbidden_binding_raised": forbidden_binding_raised,
        "contradiction_raised": contradiction_raised,
        "v2_profile_mutated": full_ladder != full_ladder_pristine,
    }


def probe_batch(seed_grids: list[dict], baseline_valid_per_100: int) -> dict:
    seed_ids = {grid["grid_id"] for grid in seed_grids}
    batch = generate_batch(seed_grids, 100, rng_seed=77)

    valid_count = sum(1 for grid in batch if validate_grid(grid).ok)
    traces_present = sum(
        1
        for grid in batch
        if isinstance(grid.get("metadata", {}).get("generation_trace"), dict)
    )
    lineage_complete = sum(
        1
        for grid in batch
        if grid.get("parent_grid_id") in seed_ids
        and grid.get("lineage", {}).get("ancestor_ids")
    )

    determinism_first = generate_batch(seed_grids, 10, rng_seed=5)
    determinism_second = generate_batch(seed_grids, 10, rng_seed=5)
    reseeded = generate_batch(seed_grids, 10, rng_seed=6)

    negative_count_raised = _raised_message(lambda: generate_batch(seed_grids, -1))

    return {
        "count_requested": 100,
        "count_returned": len(batch),
        "unique_candidate_ids": len({grid["grid_id"] for grid in batch}),
        "valid_count": valid_count,
        "unique_signatures": len({grid_signature(grid) for grid in batch}),
        "beats_random_mutation_baseline": valid_count > baseline_valid_per_100,
        "traces_present": traces_present,
        "lineage_complete": lineage_complete,
        "deterministic_batches_identical": determinism_first == determinism_second,
        "reseeded_batch_differs": reseeded != determinism_first,
        "zero_count_returns_empty": generate_batch(seed_grids, 0, rng_seed=5) == [],
        "negative_count_raised": negative_count_raised,
    }


def probe_slip_batch(seed_grids: list[dict], profile: dict) -> dict:
    profile_pristine = deepcopy(profile)
    batch = generate_batch(seed_grids, 50, slip_profile=profile, rng_seed=313)

    valid_count = sum(1 for grid in batch if validate_grid(grid).ok)
    aligned_count = sum(1 for grid in batch if _grid_slip_aligned(grid, profile_pristine))
    trace_aligned_count = sum(
        1
        for grid in batch
        if grid["metadata"]["generation_trace"]["slip_alignment"]["ok"] is True
    )

    unsatisfiable = deepcopy(profile)
    unsatisfiable["grid"]["body_mass_min"] = 25
    unsatisfiable["grid"]["body_mass_max"] = 30
    unsatisfiable_raised = _raised_message(
        lambda: generate_batch(seed_grids, 5, slip_profile=unsatisfiable, rng_seed=313)
    )
    invalid_profile = deepcopy(profile)
    del invalid_profile["mutation"]["cell_mutation_rate_max"]
    invalid_profile_raised = _raised_message(
        lambda: generate_batch(seed_grids, 5, slip_profile=invalid_profile, rng_seed=313)
    )

    return {
        "count_requested": 50,
        "count_returned": len(batch),
        "unique_candidate_ids": len({grid["grid_id"] for grid in batch}),
        "valid_count": valid_count,
        "aligned_count": aligned_count,
        "trace_aligned_count": trace_aligned_count,
        "unsatisfiable_profile_raised": unsatisfiable_raised,
        "invalid_profile_raised": invalid_profile_raised,
        "profile_mutated": profile != profile_pristine,
    }


def probe_explanation(
    seed_grids: list[dict], model: GenerationModel, profile: dict
) -> dict:
    parent = seed_grids[0]
    candidate = generate_candidate(parent, model, rng_seed=101)
    slip_candidate = generate_candidate(parent, model, slip_profile=profile, rng_seed=404)

    candidate_pristine = deepcopy(candidate)
    explanation = explain_generation(candidate)
    slip_explanation = explain_generation(slip_candidate)

    try:
        json_serializable = (
            json.loads(json.dumps(explanation)) == explanation
            and json.loads(json.dumps(slip_explanation)) == slip_explanation
        )
    except (TypeError, ValueError):
        json_serializable = False

    untraced_raised = _raised_message(lambda: explain_generation(deepcopy(parent)))

    return {
        "keys": sorted(explanation),
        "required_fields_present": [
            field for field in REQUIRED_EXPLANATION_FIELDS if field in explanation
        ],
        "grid_id_matches": explanation["grid_id"] == candidate["grid_id"],
        "parent_matches": explanation["parent_grid_id"] == parent["grid_id"],
        "rng_seed_matches": explanation["rng_seed"] == 101,
        "mutation_events_match_lineage": explanation["mutation_events"]
        == candidate["lineage"]["mutation_events"],
        "validation_ok": explanation["validation"]["ok"] is True,
        "proposals_accounted": explanation["accepted_proposals"]
        + explanation["rejected_proposals"]
        == explanation["proposal_attempts"],
        "unconstrained_alignment_unchecked": explanation["slip_alignment"]["checked"]
        is False,
        "slip_alignment_checked": slip_explanation["slip_alignment"]["checked"] is True,
        "slip_alignment_ok": slip_explanation["slip_alignment"]["ok"] is True,
        "slip_alignment_profile_id": slip_explanation["slip_alignment"]["profile_id"],
        "json_serializable": json_serializable,
        "candidate_mutated_by_explain": candidate != candidate_pristine,
        "untraced_candidate_raised": untraced_raised,
    }


def probe_markov_exposure(model: GenerationModel, batch_probe: dict) -> dict:
    public_names = sorted(
        name for name in dir(generation_module) if not name.startswith("_")
    )
    return {
        "public_all": sorted(generation_module.__all__),
        "public_names": public_names,
        "markov_named_public_surface": [
            name for name in public_names if "markov" in name.lower()
        ],
        "model_strategy_is_constrained": model.metadata.get("strategy")
        == "constrained_wfc_style_stabilizer",
        "proposal_source_is_markov_proposals_only": model.metadata.get("proposal_source")
        == "markov_local_adjacency_proposals",
        "all_batch_candidates_validator_gated": batch_probe["traces_present"]
        == batch_probe["count_returned"]
        and batch_probe["valid_count"] == batch_probe["count_returned"],
    }


def probe_loaded_lab_modules() -> list[str]:
    lab_root = "la" "bs"
    return sorted(
        name
        for name in sys.modules
        if name == lab_root or name.startswith(lab_root + ".")
    )


def probe_scale_16(seed_grids_16: list[dict], seed_grid_8: dict) -> dict:
    """DR 0029 / cycle 09 A3: generation at the ratified 16x16 default.

    The model must derive its dimensions from the corpus, the constrained
    stabilizer must emit valid 16x16 candidates whose required core clears
    the size-parametric floor (18 at 16x16), and a mixed-size corpus must
    fail loudly instead of silently training 8x8 statistics.
    """
    model = train_generation_model(seed_grids_16)
    batch = generate_batch(seed_grids_16, count=25, rng_seed=9)

    def _core_mass(grid: dict) -> int:
        return sum(
            len(organ["cells"])
            for organ in grid["organs"].values()
            if organ.get("role") == "body_core" and organ.get("required") is True
        )

    return {
        "corpus_size": len(seed_grids_16),
        "model_width": model.width,
        "model_height": model.height,
        "batch_count": len(batch),
        "all_valid": all(validate_grid(grid).ok for grid in batch),
        "all_16x16": all(grid["grid_size"] == [16, 16] for grid in batch),
        "core_floor_met": all(_core_mass(grid) >= 18 for grid in batch),
        "unique_ids": len({grid["grid_id"] for grid in batch}) == len(batch),
        "mixed_size_corpus_raised": _raised_message(
            lambda: train_generation_model(
                [deepcopy(seed_grid_8), deepcopy(seed_grids_16[0])]
            )
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()

    seed_dir = repo_root / "data" / "seed_grids"
    invalid_dir = repo_root / "data" / "invalid_grids"
    seed16_dir = repo_root / "data" / "seed_grids_16x16"
    profile_path = repo_root / "data" / "slips" / "valid" / "slip_lcd_seed.json"

    seed_grids = [_load(path) for path in sorted(seed_dir.glob("*.json"))]
    seeds_pristine = deepcopy(seed_grids)
    invalid_grid = _load(sorted(invalid_dir.glob("*.json"))[0])
    seed_grids_16 = [_load(path) for path in sorted(seed16_dir.glob("*.json"))]
    profile = _load(profile_path)

    model_report = probe_model(seed_grids, invalid_grid)
    model = train_generation_model(seed_grids)
    batch_report = probe_batch(seed_grids, baseline_valid_per_100=42)

    report = {
        "seed_corpus_size": len(seed_grids),
        "model": model_report,
        "candidate": probe_candidate(seed_grids, model),
        "slip_candidate": probe_slip_candidate(seed_grids, model, profile),
        "slip_v2": probe_slip_v2(seed_grids, model, profile),
        "batch": batch_report,
        "slip_batch": probe_slip_batch(seed_grids, profile),
        "explanation": probe_explanation(seed_grids, model, profile),
        "markov_exposure": probe_markov_exposure(model, batch_report),
        "scale_16": probe_scale_16(seed_grids_16, seed_grids[0]),
        "seed_corpus_mutated": seed_grids != seeds_pristine,
        "lab_modules_loaded": probe_loaded_lab_modules(),
    }
    json.dump(report, sys.stdout)


if __name__ == "__main__":
    main()
