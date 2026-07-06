"""Repair contract probe driver executed against the package surface.

Traceability: research/package_specs/mecha_engine_repair_interface_spec.md
("The observability contract", "Data contracts", "Required public
surface", "Validity-guard semantics", "Hard gates for a future package
port"), research/package_specs/mecha_engine_contract_traceability_matrix.md
(the "Repair" row and "Cross-Cut Negative Tests"), and
research/decision_records/0006-create-mecha-engine-repair-target.md.
``tests/test_repair_contract.py`` launches this script in a subprocess
whose PYTHONPATH points at the package ``src`` directory (the same
documented import mechanics as ``tests/test_package_imports.py``), so
every probe exercises ``mecha_engine.repair`` and validates grids through
``mecha_engine.genome`` — never repository-root or research lab modules —
and the test module itself never touches the interpreter module search
path.

The driver prints a single JSON report on stdout; the unittest module
asserts on it. Fixtures are the frozen repository corpora fixed by the
test fixture manifest: ``data/seed_grids/mg_seed_*.json`` (training
corpus subsets, the held-out probe grid ``mg_seed_046``, and the
adversarial validity-guard fixture ``mg_seed_001`` with the probed wound
``[[2, 3], [3, 3]]`` whose expression-cell refill disconnects the required
body core). Damaged probe grids are handcrafted from those frozen files —
never produced by research lab code.
"""

from __future__ import annotations

import argparse
import inspect
import json
import sys
from copy import deepcopy
from pathlib import Path

import mecha_engine.repair as repair_module
from mecha_engine.genome import validate_grid
from mecha_engine.repair import (
    repair_blind,
    repair_wound_sites,
    train_repair_model,
)


TEMPLATE_PARAM_TOKENS = ("template", "target")
REQUIRED_MODEL_FIELDS = [
    "model_id",
    "source_mode",
    "weights",
    "training_grid_ids",
    "example_count",
    "feature_count",
    "class_tokens",
    "rng_seed",
    "epochs",
    "learning_rate",
    "live_class_weight",
    "initial_loss",
    "final_loss",
    "target_template_used",
]
REQUIRED_RESULT_METADATA_FIELDS = [
    "learned_model_id",
    "target_template_used",
    "wound_site_count",
    "validity_guard_substitutions",
]


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _raised(callable_probe) -> str | None:
    try:
        callable_probe()
    except Exception as error:
        return f"{type(error).__name__}: {error}"
    return None


def _token_for_cell(cell: dict) -> str:
    # Grid-genome data-format fact (research/grid_genome/grid_genome.schema.json):
    # core cells are body ("A" when animation_anchor) and organs otherwise
    # classify the token. Used only to compare cell content across grids.
    if cell.get("organ") == "core":
        return "A" if cell.get("animation_anchor") is True else "B"
    if cell.get("organ") == "sensors" or cell.get("role") == "eye":
        return "E"
    if cell.get("organ") == "expression" or cell.get("role") == "mouth":
        return "M"
    return "B"


def _token_map(grid: dict) -> dict[tuple[int, int], str]:
    return {(cell["x"], cell["y"]): _token_for_cell(cell) for cell in grid["cells"]}


def _live_set(grid: dict) -> set[tuple[int, int]]:
    return {(cell["x"], cell["y"]) for cell in grid["cells"]}


def _construct_damaged(grid: dict, sites: list[list[int]], grid_id: str) -> dict:
    """Handcraft a damage event over a frozen seed grid.

    The event carries exactly what the observability contract allows:
    the destroyed positions (``removed_cells``) — never the destroyed
    tokens, never a template.
    """
    site_set = {(x, y) for x, y in sites}
    damaged = deepcopy(grid)
    damaged["grid_id"] = grid_id
    damaged["parent_grid_id"] = grid["grid_id"]
    damaged["cells"] = [
        cell for cell in damaged["cells"] if (cell["x"], cell["y"]) not in site_set
    ]
    for organ in damaged.get("organs", {}).values():
        organ["cells"] = [
            cell for cell in organ["cells"] if (cell[0], cell[1]) not in site_set
        ]
    damaged["metadata"] = {
        "source": "handcrafted_damage_probe",
        "damage_pattern": "handcrafted_probe",
        "damage_event_index": 1,
        "removed_cell_count": len(sites),
        "removed_cells": [list(site) for site in sites],
    }
    return damaged


def _probe_sites(grid: dict) -> list[list[int]]:
    """Deterministic wound choice: every third non-anchor live position."""
    anchor = next(
        (cell["x"], cell["y"])
        for cell in grid["cells"]
        if cell.get("animation_anchor") is True
    )
    positions = sorted(
        (cell["y"], cell["x"])
        for cell in grid["cells"]
        if (cell["x"], cell["y"]) != anchor
    )
    return [[x, y] for index, (y, x) in enumerate(positions) if index % 3 == 0]


def probe_surface(sample_damaged: dict, sample_model: dict) -> dict:
    template_params: dict[str, list[str]] = {}
    defaults: dict[str, dict] = {}
    for name in repair_module.__all__:
        signature = inspect.signature(getattr(repair_module, name))
        template_params[name] = [
            parameter
            for parameter in signature.parameters
            if any(token in parameter.lower() for token in TEMPLATE_PARAM_TOKENS)
        ]
        defaults[name] = {
            parameter_name: (
                repr(parameter.default)
                if parameter.default is not inspect.Parameter.empty
                else "REQUIRED"
            )
            for parameter_name, parameter in signature.parameters.items()
        }
    blind_doc = (repair_blind.__doc__ or "") + (
        sys.modules[repair_blind.__module__].__doc__ or ""
    )
    return {
        "public_all": sorted(repair_module.__all__),
        "template_named_parameters": template_params,
        "signature_defaults": defaults,
        "template_kwarg_rejected": _raised(
            lambda: repair_wound_sites(
                sample_damaged, sample_model, target_template=sample_damaged
            )
        ),
        "pre_damage_grid_kwarg_rejected": _raised(
            lambda: repair_wound_sites(
                sample_damaged, sample_model, target_grid=sample_damaged
            )
        ),
        "blind_doc_labels_benchmark_comparator": "benchmark comparator"
        in blind_doc.lower(),
        "blind_doc_labels_below_bar": "below" in blind_doc.lower()
        and "bar" in blind_doc.lower(),
        "attractor_surface_absent": [
            name
            for name in dir(repair_module)
            if "attractor" in name.lower() or "template" in name.lower()
        ],
    }


def probe_training(seed_grids: list[dict]) -> dict:
    corpus = deepcopy(seed_grids[:8])
    corpus_pristine = deepcopy(corpus)

    first = train_repair_model(corpus, epochs=20, rng_seed=20260512)
    second = train_repair_model(corpus, epochs=20, rng_seed=20260512)
    reseeded = train_repair_model(corpus, epochs=20, rng_seed=7)

    try:
        json_roundtrip = json.loads(json.dumps(first)) == first
    except (TypeError, ValueError):
        json_roundtrip = False

    return {
        "identical_inputs_identical_weights": first["weights"] == second["weights"],
        "identical_inputs_identical_model": first == second,
        "reseeded_weights_differ": first["weights"] != reseeded["weights"],
        "target_template_used_false": first["target_template_used"] is False,
        "final_loss_below_initial": first["final_loss"] < first["initial_loss"],
        "training_grid_ids_recorded": first["training_grid_ids"]
        == [grid["grid_id"] for grid in corpus_pristine],
        "example_count_positive": first["example_count"] > 0,
        "required_fields_present": [
            field for field in REQUIRED_MODEL_FIELDS if field in first
        ],
        "empty_corpus_raised": _raised(lambda: train_repair_model([])),
        "inputs_mutated": corpus != corpus_pristine,
        "model_json_roundtrip": json_roundtrip,
    }


def probe_wound_repair(model: dict, target: dict) -> dict:
    sites = _probe_sites(target)
    damaged = _construct_damaged(target, sites, f"{target['grid_id']}_probe_damage")
    damaged_pristine = deepcopy(damaged)
    model_pristine = deepcopy(model)

    repaired = repair_wound_sites(damaged, model)
    again = repair_wound_sites(damaged, model)
    explicit_sites = repair_wound_sites(damaged, model, wound_sites=sites)

    site_set = {(x, y) for x, y in sites}
    damaged_tokens = _token_map(damaged_pristine)
    repaired_tokens = _token_map(repaired)

    no_removed_cells = deepcopy(damaged)
    del no_removed_cells["metadata"]["removed_cells"]

    try:
        json_roundtrip = json.loads(json.dumps(repaired)) == repaired
    except (TypeError, ValueError):
        json_roundtrip = False

    return {
        "site_count": len(sites),
        "every_site_refilled_live": site_set <= _live_set(repaired),
        "live_set_is_damaged_plus_sites": _live_set(repaired)
        == _live_set(damaged_pristine) | site_set,
        "live_positions_restored": _live_set(repaired) == _live_set(target),
        "non_site_cells_unchanged": all(
            repaired_tokens.get(position) == token
            for position, token in damaged_tokens.items()
        ),
        "deterministic_repeat_identical": repaired == again,
        "default_sites_match_explicit_sites": repaired["cells"]
        == explicit_sites["cells"],
        "metadata_fields_present": [
            field
            for field in REQUIRED_RESULT_METADATA_FIELDS
            if field in repaired["metadata"]
        ],
        "learned_model_id_recorded": repaired["metadata"]["learned_model_id"]
        == model_pristine["model_id"],
        "target_template_used_false": repaired["metadata"]["target_template_used"]
        is False,
        "wound_site_count_matches": repaired["metadata"]["wound_site_count"]
        == len(sites),
        "substitutions_are_int": isinstance(
            repaired["metadata"]["validity_guard_substitutions"], int
        ),
        "source_label": repaired["metadata"]["source"],
        "grid_id_suffix_ok": repaired["grid_id"]
        == f"{damaged_pristine['grid_id']}_wound_repaired",
        "parent_grid_id_is_damaged_grid": repaired["parent_grid_id"]
        == damaged_pristine["grid_id"],
        "repaired_valid": validate_grid(repaired).ok,
        "missing_removed_cells_raised": _raised(
            lambda: repair_wound_sites(no_removed_cells, model)
        ),
        "damaged_grid_mutated": damaged != damaged_pristine,
        "model_mutated": model != model_pristine,
        "result_json_roundtrip": json_roundtrip,
    }


def probe_validity_guard(seed_001: dict, trained_model: dict) -> dict:
    """The adversarial guard fixture from the research benchmark failure mode.

    Wound ``(2, 3)`` + ``(3, 3)`` on ``mg_seed_001``: both are body-core
    cells, and a model biased to refill every site as an expression cell
    ("M") disconnects the required body core. Guard off must reproduce the
    invalid refill; guard on must recover a valid grid by substituting
    tokens at wound sites only, leaving the live set unchanged.
    """
    wound_sites = [[2, 3], [3, 3]]
    fixture_cells_are_body_core = all(
        any(
            cell["x"] == x and cell["y"] == y and cell.get("organ") == "core"
            for cell in seed_001["cells"]
        )
        for x, y in wound_sites
    )
    damaged = _construct_damaged(seed_001, wound_sites, "mg_seed_001_guard_case")

    # Adversarial model: bias weights force every fill toward "M". The
    # feature layout is read from the trained model's public fields.
    feature_count = trained_model["feature_count"]
    class_tokens = trained_model["class_tokens"]
    bias_index = feature_count - 1
    weights = [[0.0] * feature_count for _ in class_tokens]
    weights[0][bias_index] = -10.0
    weights[class_tokens.index("M")][bias_index] = 10.0
    biased_model = {"model_id": "biased_probe_model", "weights": weights}

    naive = repair_wound_sites(damaged, biased_model, validity_guard=False)
    naive_again = repair_wound_sites(damaged, biased_model, validity_guard=False)
    guarded = repair_wound_sites(damaged, biased_model)
    guarded_again = repair_wound_sites(damaged, biased_model)

    return {
        "fixture_cells_are_body_core": fixture_cells_are_body_core,
        "guard_off_invalid": not validate_grid(naive).ok,
        "guard_off_substitutions_zero": naive["metadata"][
            "validity_guard_substitutions"
        ]
        == 0,
        "guard_on_valid": validate_grid(guarded).ok,
        "guard_on_substitutions": guarded["metadata"][
            "validity_guard_substitutions"
        ],
        "live_sets_equal_guard_on_off": _live_set(naive) == _live_set(guarded),
        "guard_off_deterministic": naive == naive_again,
        "guard_on_deterministic": guarded == guarded_again,
        "naive_target_template_used_false": naive["metadata"][
            "target_template_used"
        ]
        is False,
        "guarded_target_template_used_false": guarded["metadata"][
            "target_template_used"
        ]
        is False,
    }


def probe_slip_aware_guard(
    seed_001: dict, trained_model: dict, slip_profile: dict
) -> dict:
    """The runtime integration seam (2026-07-05): SLIP-aware guarding.

    Wound ``(5, 3)`` on ``mg_seed_001`` destroys its only expression cell;
    a model biased to refill every site as body ("B") leaves a
    validator-valid but SLIP-unaligned creature that
    ``mecha_engine.lifecycle.initial_state`` refuses (the PUBLIC
    cross-module oracle for alignment). With the active profile supplied,
    the guard must refill back into an aligned, simulatable creature. The
    profile is an engine-native constraint set, not a template.
    """
    from mecha_engine.lifecycle import initial_state

    wound_sites = [[5, 3]]
    fixture_cell_is_expression = any(
        cell["x"] == 5 and cell["y"] == 3 and cell.get("organ") == "expression"
        for cell in seed_001["cells"]
    )
    damaged = _construct_damaged(
        seed_001, wound_sites, "mg_seed_001_slip_guard_case"
    )

    feature_count = trained_model["feature_count"]
    class_tokens = trained_model["class_tokens"]
    bias_index = feature_count - 1
    weights = [[0.0] * feature_count for _ in class_tokens]
    weights[0][bias_index] = -10.0
    weights[class_tokens.index("B")][bias_index] = 10.0
    biased_model = {"model_id": "biased_probe_model", "weights": weights}

    unaware = repair_wound_sites(damaged, biased_model)
    aware = repair_wound_sites(damaged, biased_model, slip_profile=slip_profile)
    aware_again = repair_wound_sites(
        damaged, biased_model, slip_profile=slip_profile
    )

    return {
        "fixture_cell_is_expression": fixture_cell_is_expression,
        "unaware_valid": validate_grid(unaware).ok,
        "unaware_rejected_by_lifecycle": _raised(
            lambda: initial_state(unaware, slip_profile)
        )
        is not None,
        "aware_valid": validate_grid(aware).ok,
        "aware_accepted_by_lifecycle": _raised(
            lambda: initial_state(aware, slip_profile)
        )
        is None,
        "aware_substitutions": aware["metadata"]["validity_guard_substitutions"],
        "live_sets_equal": _live_set(unaware) == _live_set(aware),
        "aware_deterministic": aware == aware_again,
        "aware_target_template_used_false": aware["metadata"][
            "target_template_used"
        ]
        is False,
    }


def probe_slip_v2_guard(
    seed_001: dict, trained_model: dict, slip_profile: dict
) -> dict:
    """SLIP v0.2 acceptance for the guard (decision record 0013): the
    dual-version ``_slip`` mirror accepts v0.2 profiles, and a v0.2
    extension whose ladder fields do not bind on the creature repairs
    byte-identically to the frozen v0.1 baseline."""
    v2_profile = deepcopy(slip_profile)
    v2_profile["slip_version"] = "0.2.0"
    v2_profile["forbidden_traits"] = {"roles": ["shell"], "materials": ["light"]}
    v2_profile["risk_tolerances"] = {"mutation": 0.6}
    v2_pristine = deepcopy(v2_profile)

    wound_sites = [[5, 3]]
    damaged = _construct_damaged(
        seed_001, wound_sites, "mg_seed_001_slip_v2_guard_case"
    )

    feature_count = trained_model["feature_count"]
    class_tokens = trained_model["class_tokens"]
    bias_index = feature_count - 1
    weights = [[0.0] * feature_count for _ in class_tokens]
    weights[0][bias_index] = -10.0
    weights[class_tokens.index("B")][bias_index] = 10.0
    biased_model = {"model_id": "biased_probe_model", "weights": weights}

    v1_repaired = repair_wound_sites(
        damaged, biased_model, slip_profile=slip_profile
    )
    v2_repaired = repair_wound_sites(damaged, biased_model, slip_profile=v2_profile)

    return {
        "v2_repaired_valid": validate_grid(v2_repaired).ok,
        "v2_equals_v1_baseline_repair": v2_repaired == v1_repaired,
        "v2_substitutions": v2_repaired["metadata"][
            "validity_guard_substitutions"
        ],
        "v2_profile_mutated": v2_profile != v2_pristine,
    }


def probe_blind(model: dict, target: dict) -> dict:
    sites = _probe_sites(target)
    damaged = _construct_damaged(target, sites, f"{target['grid_id']}_blind_damage")
    damaged_pristine = deepcopy(damaged)

    repaired = repair_blind(damaged, model)
    again = repair_blind(damaged, model)

    return {
        "deterministic_repeat_identical": repaired == again,
        "target_template_used_false": repaired["metadata"]["target_template_used"]
        is False,
        "learned_model_id_recorded": repaired["metadata"]["learned_model_id"]
        == model["model_id"],
        "source_label": repaired["metadata"]["source"],
        "repair_steps_recorded": repaired["metadata"]["repair_steps"],
        "grid_id_suffix_ok": repaired["grid_id"]
        == f"{damaged_pristine['grid_id']}_trained_repaired",
        "damaged_grid_mutated": damaged != damaged_pristine,
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
    seed_grids = [
        _load(seed_dir / f"mg_seed_{index:03d}.json") for index in range(1, 13)
    ]
    seed_001 = _load(seed_dir / "mg_seed_001.json")
    heldout = _load(seed_dir / "mg_seed_046.json")
    slip_profile = _load(
        repo_root / "data" / "slips" / "valid" / "slip_lcd_seed.json"
    )
    fixtures_pristine = deepcopy([seed_grids, seed_001, heldout, slip_profile])

    # One trained model for the repair probes (frozen files in, epochs kept
    # small; the full 150-epoch benchmark pin lives in the lab-side parity
    # test over the research corpus).
    model = train_repair_model(seed_grids, epochs=60, rng_seed=20260512)

    sample_sites = _probe_sites(heldout)
    sample_damaged = _construct_damaged(
        heldout, sample_sites, f"{heldout['grid_id']}_surface_probe"
    )

    report = {
        "surface": probe_surface(sample_damaged, model),
        "training": probe_training(seed_grids),
        "wound_repair": probe_wound_repair(model, heldout),
        "validity_guard": probe_validity_guard(seed_001, model),
        "blind": probe_blind(model, heldout),
        "slip_aware_guard": probe_slip_aware_guard(
            seed_001, model, slip_profile
        ),
        "slip_v2_guard": probe_slip_v2_guard(seed_001, model, slip_profile),
        "fixtures_mutated": fixtures_pristine
        != [seed_grids, seed_001, heldout, slip_profile],
        "lab_modules_loaded": probe_loaded_lab_modules(),
    }
    json.dump(report, sys.stdout)


if __name__ == "__main__":
    main()
