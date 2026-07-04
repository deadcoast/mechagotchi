"""Archive contract probe driver executed against the package surface.

Traceability: research/package_specs/mecha_engine_archive_contract_gate.md
("Mathematical Contract", "Candidate Acceptance", "Descriptor Acceptance",
"Fitness Acceptance", "Insertion Acceptance", "Summary Acceptance",
"Negative Checks"),
research/package_specs/mecha_engine_contract_traceability_matrix.md
("Archive Test Obligations"), and
research/package_specs/mecha_engine_property_negative_test_strategy.md (P5
archive niche correctness, P2/P7 invalid-candidate rejection, the archive
metamorphic checks, and the scalar-top-k separation rule).
``tests/test_archive_contract.py`` launches this script in a subprocess
whose PYTHONPATH points at the package ``src`` directory (the same
documented import mechanics as ``tests/test_package_imports.py``), so every
probe exercises ``mecha_engine.archive`` and validates grids through
``mecha_engine.genome`` — never repository-root or research lab modules —
and the test module itself never mutates the interpreter module search
path.

The driver prints a single JSON report on stdout; the unittest module
asserts on it. Fixtures are the frozen repository corpora fixed by the
test fixture manifest: ``data/seed_grids/*.json`` (mg_seed_001 first),
``data/invalid_grids/*.json``, and ``data/slips/valid/slip_lcd_seed.json``.
Readability values are synthetic driver inputs because readability is an
archive metrics *input* per the interface spec (the lab-side parity test
feeds the real proxy scorer output); lifecycle survival oracles restate the
contracted stress-probe formula and run it through
``mecha_engine.lifecycle`` directly.
"""

from __future__ import annotations

import argparse
import inspect
import json
import sys
from copy import deepcopy
from pathlib import Path

import mecha_engine.archive as archive_module
from mecha_engine.archive import (
    archive_summary,
    build_archive,
    descriptor_for_candidate,
    insert_candidate,
    score_candidate,
)
from mecha_engine.lifecycle import run_episode


EXPECTED_PUBLIC_SURFACE = [
    "archive_summary",
    "build_archive",
    "descriptor_for_candidate",
    "insert_candidate",
    "score_candidate",
]
EXTENDED_NAMES = [
    "body_mass",
    "sensor_count",
    "symmetry",
    "readability",
    "lifecycle_survival",
    "mutation_stability",
    "behavior_neediness",
]
BASELINE_NAMES = EXTENDED_NAMES[:3]
FITNESS_WEIGHTS = {
    "survival": 0.28,
    "readability": 0.24,
    "validity": 0.18,
    "bond": 0.12,
    "mutation_stability": 0.1,
    "slip_alignment": 0.08,
}
SCALAR_SURFACE_TOKENS = ("top", "scalar", "rank", "leaderboard", "select")
REQUIRED_SUMMARY_FIELDS = [
    "archive_kind",
    "best_fitness",
    "blocked_invalid_count",
    "candidate_count",
    "coverage",
    "descriptor_bin_spread",
    "descriptor_cardinalities",
    "descriptor_dimensions",
    "descriptor_mode",
    "descriptor_names",
    "final_descriptor_thresholds_locked",
    "mean_elite_fitness",
    "occupied_niches",
    "qd_score",
    "readability_calibration_status",
    "skipped_missing_metrics_count",
    "total_possible_niches",
]
REQUIRED_ELITE_FIELDS = [
    "descriptor",
    "fitness",
    "fitness_components",
    "grid",
    "grid_id",
    "provenance",
    "validation",
]


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


def _candidate(grid: dict, provenance: dict | None = None) -> dict:
    candidate = {"grid": grid}
    if provenance is not None:
        candidate["provenance"] = provenance
    return candidate


def _metrics(readability: float, slip: dict | None = None, **extra) -> dict:
    metrics: dict = {"readability": readability}
    if slip is not None:
        metrics["slip_profile"] = slip
        metrics["slip_alignment"] = {"ok": True}
    metrics.update(extra)
    return metrics


# -- Contracted formula oracles (restated from the contract gate) -----------


def _oracle_body_mass(grid: dict) -> int:
    return sum(1 for cell in grid.get("cells", []) if cell.get("organ") == "core")


def _oracle_sensor_count(grid: dict) -> int:
    return len(grid.get("organs", {}).get("sensors", {}).get("cells", []))


def _oracle_symmetry(grid: dict) -> float:
    width = grid.get("grid_size", [0, 0])[0]
    occupied = {(cell["x"], cell["y"], cell["role"]) for cell in grid.get("cells", [])}
    if not occupied:
        return 0.0
    mirrored = sum(
        1 for x, y, role in occupied if (width - 1 - x, y, role) in occupied
    )
    return mirrored / len(occupied)


def _oracle_clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def _oracle_bin(value: float, thresholds: list[float]) -> int:
    for index, threshold in enumerate(thresholds):
        if value <= threshold:
            return index
    return len(thresholds)


def _oracle_stress_probe(grid: dict) -> dict:
    """Contracted morphology-derived lifecycle stress probe."""
    probe = deepcopy(grid)
    load = _oracle_clamp(
        _oracle_body_mass(grid) / 16
        + (1 - _oracle_symmetry(grid)) * 0.65
        - _oracle_sensor_count(grid) * 0.08
    )
    for cell in probe.get("cells", []):
        cell["stress"] = round(load, 6)
    return probe


# -- Probes ------------------------------------------------------------------


def probe_surface() -> dict:
    public_names = sorted(
        name for name in dir(archive_module) if not name.startswith("_")
    )
    signature = inspect.signature(descriptor_for_candidate)
    build_signature = inspect.signature(build_archive)
    return {
        "public_all": sorted(archive_module.__all__),
        "public_names": public_names,
        "scalar_named_public_surface": [
            name
            for name in public_names
            if any(token in name.lower() for token in SCALAR_SURFACE_TOKENS)
        ],
        "descriptor_mode_default": signature.parameters["mode"].default,
        "descriptor_mode_keyword_only": signature.parameters["mode"].kind.name,
        "build_archive_mode_default": build_signature.parameters["mode"].default,
    }


def probe_descriptors(grid: dict, slip: dict) -> dict:
    candidate = _candidate(grid)
    candidate_pristine = deepcopy(candidate)
    metrics = _metrics(0.62, slip, lifecycle_ticks=24, rng_seed=20260512)
    metrics_pristine = deepcopy(metrics)

    extended = descriptor_for_candidate(candidate, metrics)
    extended_repeat = descriptor_for_candidate(candidate, metrics)
    baseline = descriptor_for_candidate(candidate, metrics, mode="baseline")
    baseline_no_metric_values = descriptor_for_candidate(candidate, {}, mode="baseline")

    # Readability bin edges (provisional Stage 0 thresholds
    # 0.35/0.55/0.7/0.85, value <= edge maps into the lower bin).
    readability_bins = {}
    for value in [0.0, 0.35, 0.36, 0.55, 0.56, 0.7, 0.71, 0.85, 0.86, 1.0]:
        descriptor = descriptor_for_candidate(candidate, _metrics(value))
        readability_bins[str(value)] = descriptor[3]
    expected_readability_bins = {
        str(value): _oracle_bin(value, [0.35, 0.55, 0.7, 0.85])
        for value in [0.0, 0.35, 0.36, 0.55, 0.56, 0.7, 0.71, 0.85, 0.86, 1.0]
    }

    # Lifecycle survival axis: internal computation must equal the
    # contracted stress probe run through mecha_engine.lifecycle, and both
    # explicit lifecycle-summary shapes must resolve identically.
    episode = run_episode(
        _oracle_stress_probe(grid),
        slip,
        policy="switchboard",
        ticks=24,
        rng_seed=20260512,
    )
    survival_ratio = round(episode["survival_ticks"] / 24, 6)
    expected_survival_bin = _oracle_bin(survival_ratio, [0.2, 0.4, 0.6, 0.8])
    with_full_summary = descriptor_for_candidate(
        candidate, _metrics(0.62, slip, lifecycle=episode)
    )
    with_reduced_summary = descriptor_for_candidate(
        candidate,
        _metrics(
            0.62,
            slip,
            lifecycle={
                "survival_ratio": survival_ratio,
                "need_balance": episode["need_balance"],
                "recovery_events": episode["recovery_events"],
                "final_state": episode["final_state"],
            },
        ),
    )

    return {
        "extended_is_tuple": isinstance(extended, tuple),
        "extended_length": len(extended),
        "extended_all_int": all(
            isinstance(value, int) and not isinstance(value, bool)
            for value in extended
        ),
        "extended_deterministic": extended == extended_repeat,
        "baseline_length": len(baseline),
        "baseline_matches_extended_prefix": baseline == extended[:3],
        "baseline_needs_no_metric_values": (
            baseline_no_metric_values == baseline
        ),
        "readability_bins": readability_bins,
        "expected_readability_bins": expected_readability_bins,
        "survival_bin": extended[4],
        "expected_survival_bin": expected_survival_bin,
        "full_summary_matches_internal": with_full_summary == extended,
        "reduced_summary_matches_internal": with_reduced_summary == extended,
        "missing_readability_raised": _raised_message(
            lambda: descriptor_for_candidate(candidate, {})
        ),
        "missing_slip_alignment_raised": _raised_message(
            lambda: descriptor_for_candidate(
                candidate, {"readability": 0.62, "slip_profile": slip}
            )
        ),
        "non_mapping_candidate_raised": _raised_message(
            lambda: descriptor_for_candidate("not a candidate", metrics)
        ),
        "candidate_without_grid_raised": _raised_message(
            lambda: descriptor_for_candidate({"fitness": 1.0}, metrics)
        ),
        "non_mapping_metrics_raised": _raised_message(
            lambda: descriptor_for_candidate(candidate, "not metrics")
        ),
        "unsupported_mode_raised": _raised_message(
            lambda: descriptor_for_candidate(candidate, metrics, mode="hyper")
        ),
        "candidate_mutated": candidate != candidate_pristine,
        "metrics_mutated": metrics != metrics_pristine,
    }


def probe_metadata() -> dict:
    extended_archive = build_archive([], {})
    baseline_archive = build_archive([], {}, mode="baseline")
    extended_summary = archive_summary(extended_archive)
    baseline_summary = archive_summary(baseline_archive)
    return {
        "extended": {
            "names": extended_summary["descriptor_names"],
            "cardinalities": extended_summary["descriptor_cardinalities"],
            "dimensions": extended_summary["descriptor_dimensions"],
            "total_possible_niches": extended_summary["total_possible_niches"],
        },
        "baseline": {
            "names": baseline_summary["descriptor_names"],
            "cardinalities": baseline_summary["descriptor_cardinalities"],
            "dimensions": baseline_summary["descriptor_dimensions"],
            "total_possible_niches": baseline_summary["total_possible_niches"],
        },
        "empty_summary": {
            key: extended_summary[key]
            for key in [
                "occupied_niches",
                "coverage",
                "best_fitness",
                "mean_elite_fitness",
                "qd_score",
                "candidate_count",
                "blocked_invalid_count",
                "skipped_missing_metrics_count",
            ]
        },
        "readability_calibration_status": extended_summary[
            "readability_calibration_status"
        ],
        "final_descriptor_thresholds_locked": extended_summary[
            "final_descriptor_thresholds_locked"
        ],
        "archive_kind": extended_summary["archive_kind"],
    }


def probe_scoring(grid: dict, slip: dict, invalid_grid: dict) -> dict:
    candidate = _candidate(grid, provenance={"source": "driver", "parent": None})
    candidate_pristine = deepcopy(candidate)
    metrics = _metrics(0.62, slip)
    metrics_pristine = deepcopy(metrics)

    score = score_candidate(candidate, metrics)
    score_repeat = score_candidate(candidate, metrics)

    components = score["components"]
    recomputed = _oracle_clamp(
        sum(components[name] * FITNESS_WEIGHTS[name] for name in FITNESS_WEIGHTS)
    )

    readability_low = score_candidate(_candidate(grid), _metrics(0.5, slip))
    readability_high = score_candidate(_candidate(grid), _metrics(0.75, slip))

    invalid_score = score_candidate(_candidate(invalid_grid), _metrics(0.62))
    misaligned_score = score_candidate(
        _candidate(grid),
        {"readability": 0.62, "slip_profile": slip, "slip_alignment": {"ok": False}},
    )
    no_provenance_score = score_candidate(_candidate(grid), _metrics(0.62))
    supplied_readability_record = score_candidate(
        _candidate(grid),
        _metrics(
            {
                "proxy_readability_score": 0.62,
                "manual_rating_status": "not_collected",
                "human_readability_rating": None,
            }
        ),
    )

    try:
        json_roundtrip = json.loads(json.dumps(score)) == score
    except (TypeError, ValueError):
        json_roundtrip = False

    return {
        "required_fields_present": [
            field
            for field in [
                "fitness",
                "components",
                "validation",
                "readability",
                "lifecycle",
                "slip_alignment",
                "provenance",
            ]
            if field in score
        ],
        "component_names": sorted(components),
        "components_bounded": all(0.0 <= value <= 1.0 for value in components.values()),
        "fitness_bounded": 0.0 <= score["fitness"] <= 1.0,
        "fitness_matches_weighted_components": abs(score["fitness"] - recomputed)
        <= 2e-6,
        "readability_weight_delta": round(
            readability_high["fitness"] - readability_low["fitness"], 6
        ),
        "deterministic": score == score_repeat,
        "json_roundtrip": json_roundtrip,
        "validation_ok": score["validation"]["ok"],
        "bond_component_from_lifecycle_final_state": components["bond"]
        == round(_oracle_clamp(score["lifecycle"]["final_state"].get("bond", 0.0)), 6),
        "proxy_marking_default": score["readability"].get("manual_rating_status"),
        "proxy_marking_preserved": supplied_readability_record["readability"].get(
            "manual_rating_status"
        ),
        "human_rating_absent": score["readability"].get("human_readability_rating")
        is None,
        "provenance_provided": score["provenance"],
        "provenance_missing_marked": no_provenance_score["provenance"],
        "invalid_scored_as_failure": {
            "validity_component": invalid_score["components"]["validity"],
            "survival_component": invalid_score["components"]["survival"],
            "bond_component": invalid_score["components"]["bond"],
            "validation_ok": invalid_score["validation"]["ok"],
            "validation_errors_nonempty": bool(invalid_score["validation"]["errors"]),
            "fitness_below_valid": invalid_score["fitness"] < score["fitness"],
            "fitness_bounded": 0.0 <= invalid_score["fitness"] <= 1.0,
        },
        "misaligned_slip_component_zero": (
            misaligned_score["components"]["slip_alignment"] == 0.0
            and misaligned_score["slip_alignment"]["ok"] is False
        ),
        "aligned_slip_component_one": components["slip_alignment"] == 1.0,
        "candidate_mutated": candidate != candidate_pristine,
        "metrics_mutated": metrics != metrics_pristine,
    }


def probe_insertion(grid: dict, second_grid: dict) -> dict:
    empty = build_archive([], {})
    empty_pristine = deepcopy(empty)

    lower_candidate = _candidate(grid, provenance={"source": "driver"})
    lower_metrics = _metrics(0.56)
    higher_candidate = _candidate(deepcopy(grid))
    higher_candidate["grid"]["grid_id"] = grid["grid_id"] + "_twin"
    higher_metrics = _metrics(0.6)

    lower_descriptor = descriptor_for_candidate(lower_candidate, lower_metrics)
    lower_score = score_candidate(lower_candidate, lower_metrics)
    higher_descriptor = descriptor_for_candidate(higher_candidate, higher_metrics)
    higher_score = score_candidate(higher_candidate, higher_metrics)
    same_niche = lower_descriptor == higher_descriptor

    first = insert_candidate(empty, lower_candidate, lower_score, lower_descriptor)
    niche_key = ",".join(str(value) for value in lower_descriptor)
    elite = first["elites"].get(niche_key, {})

    replaced = insert_candidate(
        first, higher_candidate, higher_score, higher_descriptor
    )
    replaced_elite = replaced["elites"].get(niche_key, {})

    tie = insert_candidate(replaced, higher_candidate, higher_score, higher_descriptor)
    weaker_after = insert_candidate(
        replaced, lower_candidate, lower_score, lower_descriptor
    )

    # A different-morphology candidate lands in its own niche.
    other_candidate = _candidate(second_grid)
    other_metrics = _metrics(0.62)
    other_descriptor = descriptor_for_candidate(other_candidate, other_metrics)
    other_score = score_candidate(other_candidate, other_metrics)
    two_niche = insert_candidate(replaced, other_candidate, other_score, other_descriptor)

    bad_descriptor_raised = _raised_message(
        lambda: insert_candidate(empty, lower_candidate, lower_score, (1, 2))
    )
    non_int_descriptor_raised = _raised_message(
        lambda: insert_candidate(
            empty, lower_candidate, lower_score, (0, 1, 2, 3, 4, 0, 1.5)
        )
    )
    out_of_range_raised = _raised_message(
        lambda: insert_candidate(
            empty, lower_candidate, lower_score, (0, 1, 2, 3, 4, 0, 9)
        )
    )
    bad_fitness_raised = _raised_message(
        lambda: insert_candidate(
            empty, lower_candidate, {**lower_score, "fitness": 1.5}, lower_descriptor
        )
    )
    missing_validation_raised = _raised_message(
        lambda: insert_candidate(
            empty,
            lower_candidate,
            {"fitness": 0.5, "components": {}},
            lower_descriptor,
        )
    )
    bad_archive_raised = _raised_message(
        lambda: insert_candidate(
            {"elites": {}}, lower_candidate, lower_score, lower_descriptor
        )
    )

    log_events = [entry.get("event") for entry in weaker_after["insertion_log"]]
    log_complete = all(
        {"event", "niche", "grid_id", "fitness", "reason"}.issubset(entry)
        for entry in weaker_after["insertion_log"]
    )
    replace_event = next(
        (
            entry
            for entry in replaced["insertion_log"]
            if entry["event"] == "replaced_elite"
        ),
        {},
    )

    return {
        "same_niche_fixture": same_niche,
        "fitness_ordering_fixture": higher_score["fitness"] > lower_score["fitness"],
        "empty_archive_preserved": empty == empty_pristine,
        "returns_new_object": first is not empty,
        "inserted_into_empty_niche": niche_key in first["elites"],
        "elite_fields": sorted(elite),
        "elite_grid_id": elite.get("grid_id"),
        "elite_descriptor_key_matches": elite.get("descriptor", {}).get("key")
        == niche_key,
        "elite_descriptor_values": elite.get("descriptor", {}).get("values"),
        "expected_descriptor_values": list(lower_descriptor),
        "higher_fitness_replaced": replaced_elite.get("grid_id")
        == higher_candidate["grid"]["grid_id"],
        "replace_event_audits_incumbent": (
            replace_event.get("incumbent_grid_id") == grid["grid_id"]
            and replace_event.get("incumbent_fitness") == lower_score["fitness"]
        ),
        "tie_keeps_incumbent": tie["elites"] == replaced["elites"],
        "tie_event": tie["insertion_log"][-1]["event"],
        "weaker_keeps_incumbent": weaker_after["elites"] == replaced["elites"],
        "weaker_event": weaker_after["insertion_log"][-1]["event"],
        "previous_archive_preserved_after_loss": replaced["elites"]
        == {
            key: value
            for key, value in weaker_after["elites"].items()
        },
        "input_archive_not_mutated_by_insert": first["elites"] != {}
        and empty == empty_pristine,
        "distinct_morphology_opens_second_niche": (
            other_descriptor != lower_descriptor
            and len(two_niche["elites"]) == 2
        ),
        "candidate_count_accounting": weaker_after["candidate_count"] == 3,
        "log_events": log_events,
        "log_entries_complete": log_complete,
        "bad_descriptor_raised": bad_descriptor_raised,
        "non_int_descriptor_raised": non_int_descriptor_raised,
        "out_of_range_descriptor_raised": out_of_range_raised,
        "bad_fitness_raised": bad_fitness_raised,
        "missing_validation_raised": missing_validation_raised,
        "bad_archive_raised": bad_archive_raised,
    }


def probe_build(seed_grids: list[dict], invalid_grid: dict) -> dict:
    readabilities = [0.3, 0.45, 0.62, 0.62, 0.75, 0.9]
    candidates = []
    metrics_by_grid_id = {}
    for grid, readability in zip(seed_grids, readabilities):
        candidates.append(_candidate(grid, provenance={"source": "seed_corpus"}))
        metrics_by_grid_id[grid["grid_id"]] = _metrics(readability)

    invalid_candidate = _candidate(invalid_grid)
    invalid_grid_id = (
        invalid_grid.get("grid_id", "unknown_grid")
        if isinstance(invalid_grid, dict)
        else "unknown_grid"
    )
    metrics_by_grid_id[invalid_grid_id] = _metrics(0.62)
    candidates.append(invalid_candidate)

    orphan = _candidate(deepcopy(seed_grids[0]))
    orphan["grid"]["grid_id"] = "driver_orphan_no_metrics"
    candidates.append(orphan)

    incomplete = _candidate(deepcopy(seed_grids[1]))
    incomplete["grid"]["grid_id"] = "driver_incomplete_metrics"
    metrics_by_grid_id["driver_incomplete_metrics"] = {"lifecycle_ticks": 24}
    candidates.append(incomplete)

    candidates_pristine = deepcopy(candidates)
    metrics_pristine = deepcopy(metrics_by_grid_id)

    archive = build_archive(candidates, metrics_by_grid_id)
    archive_repeat = build_archive(candidates, metrics_by_grid_id)
    summary = archive_summary(archive)

    # Oracles recomputed through the public per-candidate functions.
    expected_elites: dict[str, float] = {}
    expected_bins: dict[str, set] = {name: set() for name in EXTENDED_NAMES}
    for grid, readability in zip(seed_grids, readabilities):
        descriptor = descriptor_for_candidate(_candidate(grid), _metrics(readability))
        score = score_candidate(_candidate(grid), _metrics(readability))
        key = ",".join(str(value) for value in descriptor)
        for name, value in zip(EXTENDED_NAMES, descriptor):
            expected_bins[name].add(value)
        if key not in expected_elites or score["fitness"] > expected_elites[key]:
            expected_elites[key] = score["fitness"]
    invalid_descriptor = descriptor_for_candidate(invalid_candidate, _metrics(0.62))
    for name, value in zip(EXTENDED_NAMES, invalid_descriptor):
        expected_bins[name].add(value)

    elites = archive["elites"]
    elite_fitnesses = [elite["fitness"] for elite in elites.values()]
    qd = sum(elite_fitnesses)

    try:
        json_roundtrip = (
            json.loads(json.dumps(archive)) == archive
            and json.loads(json.dumps(summary)) == summary
        )
    except (TypeError, ValueError):
        json_roundtrip = False

    return {
        "presented_candidates": len(candidates),
        "candidate_count": summary["candidate_count"],
        "blocked_invalid_count": summary["blocked_invalid_count"],
        "skipped_missing_metrics_count": summary["skipped_missing_metrics_count"],
        "deterministic_rebuild_identical": archive == archive_repeat,
        "occupied_niches": summary["occupied_niches"],
        "expected_occupied_niches": len(expected_elites),
        "elite_keys_match_descriptors": sorted(elites) == sorted(expected_elites),
        "elite_fitness_match": all(
            elites[key]["fitness"] == expected_elites[key] for key in expected_elites
        ),
        "elite_entries_complete": all(
            sorted(entry) == REQUIRED_ELITE_FIELDS for entry in elites.values()
        ),
        "invalid_grid_not_elite": all(
            entry["grid_id"] != invalid_grid_id for entry in elites.values()
        ),
        "all_elites_valid": all(
            entry["validation"]["ok"] is True for entry in elites.values()
        ),
        "summary_fields": sorted(summary),
        "coverage_matches": summary["coverage"]
        == round(len(elites) / summary["total_possible_niches"], 6),
        "qd_score_matches": summary["qd_score"] == round(qd, 6),
        "mean_elite_fitness_matches": summary["mean_elite_fitness"]
        == (round(qd / len(elites), 6) if elites else 0),
        "best_fitness_matches": summary["best_fitness"]
        == (max(elite_fitnesses) if elite_fitnesses else 0),
        "bin_spread_matches": summary["descriptor_bin_spread"]
        == {name: len(expected_bins[name]) for name in EXTENDED_NAMES},
        "json_roundtrip": json_roundtrip,
        "candidates_mutated": candidates != candidates_pristine,
        "metrics_mutated": metrics_by_grid_id != metrics_pristine,
    }


def probe_scalar_top_k_separation(grid: dict) -> dict:
    """Scalar top-k stays a comparator: diversity survives ranked pressure.

    Three copies of one grid so every non-readability component is
    identical: two strong candidates share one niche while a strictly
    weaker candidate owns another (readability bin 0); a scalar top-2
    keeps only the strong pair (one niche), but the archive must keep the
    weaker unique-niche elite.
    """
    strong_a = _candidate(grid)
    strong_b = _candidate(deepcopy(grid))
    strong_b["grid"]["grid_id"] = grid["grid_id"] + "_twin"
    weak = _candidate(deepcopy(grid))
    weak["grid"]["grid_id"] = grid["grid_id"] + "_weak"

    metrics_by_grid_id = {
        strong_a["grid"]["grid_id"]: _metrics(0.6),
        strong_b["grid"]["grid_id"]: _metrics(0.56),
        weak["grid"]["grid_id"]: _metrics(0.05),
    }
    candidates = [strong_a, strong_b, weak]
    scores = {
        candidate["grid"]["grid_id"]: score_candidate(
            candidate, metrics_by_grid_id[candidate["grid"]["grid_id"]]
        )["fitness"]
        for candidate in candidates
    }
    descriptors = {
        candidate["grid"]["grid_id"]: descriptor_for_candidate(
            candidate, metrics_by_grid_id[candidate["grid"]["grid_id"]]
        )
        for candidate in candidates
    }
    ranked = sorted(scores, key=lambda grid_id: scores[grid_id], reverse=True)
    top_two_niches = {descriptors[grid_id] for grid_id in ranked[:2]}

    archive = build_archive(candidates, metrics_by_grid_id)
    elite_grid_ids = sorted(entry["grid_id"] for entry in archive["elites"].values())

    return {
        "weak_is_last_ranked": ranked[-1] == weak["grid"]["grid_id"],
        "strong_pair_shares_one_niche": len(top_two_niches) == 1,
        "weak_niche_distinct": descriptors[weak["grid"]["grid_id"]]
        not in top_two_niches,
        "occupied_niches": len(archive["elites"]),
        "weak_candidate_kept_as_elite": weak["grid"]["grid_id"] in elite_grid_ids,
        "archive_beats_scalar_niche_count": len(archive["elites"])
        > len(top_two_niches),
    }


def probe_invalid_corpus(invalid_paths: list[Path]) -> dict:
    """P2 sweep: no invalid-corpus grid can ever become an elite."""
    archive = build_archive([], {})
    scored = 0
    structurally_rejected = 0
    unexpected = []
    for path in invalid_paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        candidate = {"grid": payload}
        metrics = _metrics(0.62)
        try:
            score = score_candidate(candidate, metrics)
            descriptor = descriptor_for_candidate(candidate, metrics)
        except ValueError:
            structurally_rejected += 1
            continue
        except Exception as error:  # unexpected exception type is trace-worthy
            unexpected.append(f"{path.name}: {type(error).__name__}: {error}")
            continue
        scored += 1
        if score["validation"]["ok"] or score["components"]["validity"] != 0.0:
            unexpected.append(f"{path.name}: invalid grid reported valid")
            continue
        archive = insert_candidate(archive, candidate, score, descriptor)
    return {
        "invalid_grid_count": len(invalid_paths),
        "scored_as_failures": scored,
        "structurally_rejected": structurally_rejected,
        "unexpected_errors": unexpected,
        "elites_after_sweep": len(archive["elites"]),
        "blocked_invalid_count": archive["blocked_invalid_count"],
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

    seed_paths = sorted((repo_root / "data" / "seed_grids").glob("*.json"))
    seed_grids = [_load(path) for path in seed_paths[:6]]
    invalid_paths = sorted((repo_root / "data" / "invalid_grids").glob("*.json"))
    invalid_grid = _load(invalid_paths[0])
    profile = _load(repo_root / "data" / "slips" / "valid" / "slip_lcd_seed.json")

    grid = seed_grids[0]
    grid_baseline_bins = (
        _oracle_bin(_oracle_body_mass(grid), [6, 9, 12, 16]),
        _oracle_bin(_oracle_sensor_count(grid), [1, 2, 3, 4]),
        _oracle_bin(_oracle_symmetry(grid), [0.25, 0.5, 0.75, 0.9]),
    )
    second_grid = next(
        candidate_grid
        for candidate_grid in (_load(path) for path in seed_paths[1:])
        if (
            _oracle_bin(_oracle_body_mass(candidate_grid), [6, 9, 12, 16]),
            _oracle_bin(_oracle_sensor_count(candidate_grid), [1, 2, 3, 4]),
            _oracle_bin(_oracle_symmetry(candidate_grid), [0.25, 0.5, 0.75, 0.9]),
        )
        != grid_baseline_bins
    )

    fixtures_pristine = deepcopy([seed_grids, invalid_grid, profile])
    report = {
        "surface": probe_surface(),
        "descriptors": probe_descriptors(grid, profile),
        "metadata": probe_metadata(),
        "scoring": probe_scoring(grid, profile, invalid_grid),
        "insertion": probe_insertion(grid, second_grid),
        "build": probe_build(seed_grids, invalid_grid),
        "scalar_separation": probe_scalar_top_k_separation(grid),
        "invalid_corpus": probe_invalid_corpus(invalid_paths),
        "fixtures_mutated": [seed_grids, invalid_grid, profile] != fixtures_pristine,
        "lab_modules_loaded": probe_loaded_lab_modules(),
    }
    json.dump(report, sys.stdout)


if __name__ == "__main__":
    main()
