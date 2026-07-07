"""Runtime contract probe driver executed against the package surface.

Traceability: research/package_specs/mecha_engine_runtime_interface_spec.md
("Proposed public surface", "Hard gates for the port", "Non-goals"),
research/package_specs/mecha_engine_contract_traceability_matrix.md
(the "Runtime" row and "Cross-Cut Negative Tests"), and
research/decision_records/0008-propose-mecha-engine-runtime-target.md.
``tests/test_runtime_contract.py`` launches this script in a subprocess
whose PYTHONPATH points at the package ``src`` directory (the same
documented import mechanics as ``tests/test_package_imports.py``), so
every probe exercises ``mecha_engine.runtime`` and its promoted
dependencies (``genome``, ``generation``, ``lifecycle``, ``archive``,
``repair``) — never repository-root or research lab modules — and the
test module itself never touches the interpreter module search path.

The driver prints a single JSON report on stdout; the unittest module
asserts on it. Fixtures are the frozen repository corpora:
``data/seed_grids/mg_seed_001..050.json`` and
``data/slips/valid/slip_lcd_seed.json``. Models are trained through the
package surfaces (``mecha_engine.generation.train_generation_model`` over
the frozen seeds; ``mecha_engine.repair.train_repair_model`` with small
epochs). The readability scorer is an injected constant (``0.6``) — the
verbatim benchmark reproduction with the lab's proxy scorer is the
lab-side parity pin (``labs/runtime_integration/
test_package_runtime_parity.py``); this suite proves the package contract
directly.
"""

from __future__ import annotations

import argparse
import inspect
import json
import sys
from copy import deepcopy
from pathlib import Path

import mecha_engine.runtime as runtime_module
from mecha_engine.generation import train_generation_model
from mecha_engine.repair import train_repair_model
from mecha_engine.runtime import evolve, live_cycle


# Small but complete contract configuration: two generations (so archive
# elites genuinely become parents), every stage runs for every creature.
EVOLVE_CONFIG = {
    "generations": 2,
    "population": 2,
    "damage_cycles": 1,
    "ticks": 12,
    "dropout_rate": 0.2,
    "rng_seed": 20260512,
}
CONSTANT_READABILITY = 0.6
REPAIR_EPOCHS = 40
REPAIR_TRAINING_COUNT = 12


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _raised(callable_probe) -> str | None:
    try:
        callable_probe()
    except Exception as error:
        return f"{type(error).__name__}: {error}"
    return None


def _json_roundtrip(payload: dict) -> bool:
    try:
        return json.loads(json.dumps(payload)) == payload
    except (TypeError, ValueError):
        return False


def _token_map(grid: dict) -> dict[str, str]:
    # JSON-safe keys: "x,y" -> "role/organ" (live-token content compare).
    return {
        f"{cell['x']},{cell['y']}": f"{cell['role']}/{cell.get('organ')}"
        for cell in grid["cells"]
    }


def _probe_sites(grid: dict, count: int) -> list[list[int]]:
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
    sites = [[x, y] for index, (y, x) in enumerate(positions) if index % 3 == 0]
    return sites[:count]


def probe_surface() -> dict:
    defaults: dict[str, dict] = {}
    keyword_only: dict[str, list[str]] = {}
    for name in runtime_module.__all__:
        signature = inspect.signature(getattr(runtime_module, name))
        defaults[name] = {
            parameter_name: (
                repr(parameter.default)
                if parameter.default is not inspect.Parameter.empty
                else "REQUIRED"
            )
            for parameter_name, parameter in signature.parameters.items()
        }
        keyword_only[name] = [
            parameter_name
            for parameter_name, parameter in signature.parameters.items()
            if parameter.kind is inspect.Parameter.KEYWORD_ONLY
        ]
    return {
        "public_all": sorted(runtime_module.__all__),
        "signature_defaults": defaults,
        "keyword_only_parameters": keyword_only,
    }


def probe_evolve(
    seed_grids: list[dict],
    slip_profile: dict,
    generation_model,
    repair_model: dict,
) -> dict:
    def scorer(grid: dict) -> float:
        return CONSTANT_READABILITY

    first_archive, first_report = evolve(
        seed_grids,
        slip_profile,
        generation_model,
        repair_model,
        readability_scorer=scorer,
        **EVOLVE_CONFIG,
    )
    second_archive, second_report = evolve(
        seed_grids,
        slip_profile,
        generation_model,
        repair_model,
        readability_scorer=scorer,
        **EVOLVE_CONFIG,
    )

    creatures = [
        creature
        for generation in first_report["generations"]
        for creature in generation["creatures"]
    ]
    return {
        "deterministic_reports_equal": first_report == second_report,
        "deterministic_archives_equal": first_archive == second_archive,
        "report_json_roundtrip": _json_roundtrip(first_report),
        "archive_json_roundtrip": _json_roundtrip(first_archive),
        "generation_count": len(first_report["generations"]),
        "generation_0_parent_source": first_report["generations"][0][
            "parent_source"
        ],
        "generation_1_parent_source": first_report["generations"][1][
            "parent_source"
        ],
        "readability_manual_rating_statuses": first_report["readability"][
            "manual_rating_statuses"
        ],
        "archived_creature_count": first_report["summary"][
            "archived_creature_count"
        ],
        "creature_count": first_report["summary"]["creature_count"],
        "every_creature_scored": all(
            creature["stages"]["scored"] for creature in creatures
        ),
        "elite_count": len(first_archive["elites"]),
        "decision_status": first_report["decision"]["status"],
        "readability_scorer_required_keyword": _raised(
            lambda: evolve(
                seed_grids,
                slip_profile,
                generation_model,
                repair_model,
                **EVOLVE_CONFIG,
            )
        ),
        "empty_seed_grids_raised": _raised(
            lambda: evolve(
                [],
                slip_profile,
                generation_model,
                repair_model,
                readability_scorer=scorer,
                **EVOLVE_CONFIG,
            )
        ),
    }


def probe_invalid_repair_boundary(
    seed_grids: list[dict],
    slip_profile: dict,
    generation_model,
) -> dict:
    """The aligned-but-invalid boundary (promotion-drift fix, 2026-07-07).

    Under damage heavy enough that wound-site repair returns a grid that
    is SLIP-aligned yet lifecycle-invalid, the lab loop had gated
    episodes on ``valid and aligned`` since T1 (commit d382805); the
    first port pre-dated that gate and crashed inside the episode run.
    Boundary configuration measured over THIS frozen corpus (probe
    2026-07-07): rng_seed 20260703, dropout 0.95, 4 cycles produce at
    least one invalid repair. The probe pins: no crash, invalid cycles
    carry no episode, aligned-but-invalid creatures record
    ``skipped_invalid`` and never score.
    """

    def scorer(grid: dict) -> float:
        return CONSTANT_READABILITY

    boundary_seed = 20260703
    repair_model = train_repair_model(
        seed_grids[:40], epochs=20, rng_seed=boundary_seed
    )
    crash = _raised(
        lambda: evolve(
            seed_grids,
            slip_profile,
            generation_model,
            repair_model,
            readability_scorer=scorer,
            generations=2,
            population=2,
            damage_cycles=4,
            ticks=8,
            dropout_rate=0.95,
            rng_seed=boundary_seed,
        )
    )
    if crash is not None:
        return {"crashed": crash}
    _, report = evolve(
        seed_grids,
        slip_profile,
        generation_model,
        repair_model,
        readability_scorer=scorer,
        generations=2,
        population=2,
        damage_cycles=4,
        ticks=8,
        dropout_rate=0.95,
        rng_seed=boundary_seed,
    )
    creatures = [
        creature
        for generation in report["generations"]
        for creature in generation["creatures"]
    ]
    aligned_but_invalid = [
        creature
        for creature in creatures
        if creature["stages"]["all_cycles_aligned"]
        and not creature["stages"]["all_cycles_valid"]
    ]
    return {
        "crashed": None,
        "invalid_repair_observed": any(
            not creature["stages"]["all_cycles_valid"]
            for creature in creatures
        ),
        "invalid_cycles_carry_no_episode": all(
            cycle["episode"] is None
            for creature in creatures
            for cycle in creature["cycles"]
            if not cycle["valid"]
        ),
        "aligned_but_invalid_decisions": sorted(
            {
                creature["archive_decision"]
                for creature in aligned_but_invalid
            }
        ),
        "aligned_but_invalid_never_scored": all(
            creature["score"] is None
            and creature["stages"]["scored"] is False
            for creature in aligned_but_invalid
        ),
    }


def probe_evolve_v2(
    seed_grids: list[dict],
    slip_profile: dict,
    generation_model,
    repair_model: dict,
) -> dict:
    """SLIP v0.2 lineage preferences (decision record 0013, rung T3.4):
    fitness_weighted elite parenting vs the frozen niche-key round-robin.

    The lab's own rung test configuration (two generations, population 4)
    is used, with a deterministic grid-dependent readability scorer: a
    constant scorer ties every elite fitness, which makes the two
    orderings coincide and would mask the rung.
    """

    def scorer(grid: dict) -> float:
        return round((sum(ord(c) for c in grid["grid_id"]) % 97) / 96, 6)

    def v2_profile(parent_selection: str) -> dict:
        profile = deepcopy(slip_profile)
        profile["slip_version"] = "0.2.0"
        profile["lineage_preferences"] = {"parent_selection": parent_selection}
        return profile

    config = dict(EVOLVE_CONFIG, population=4, damage_cycles=1, ticks=8)

    # A generations=1 pre-run reproduces the archive exactly as it stands
    # when generation 1 selects parents, so both orderings are pinned
    # against the lab's own selection expressions.
    generation_0_archive, _ = evolve(
        seed_grids,
        slip_profile,
        generation_model,
        repair_model,
        readability_scorer=scorer,
        **dict(config, generations=1),
    )
    elites = generation_0_archive["elites"]
    niche_order = sorted(elites)
    fitness_order = sorted(
        elites, key=lambda niche: (-elites[niche]["fitness"], niche)
    )
    population = config["population"]
    expected_uniform = [
        elites[niche_order[index % len(niche_order)]]["grid"]["grid_id"]
        for index in range(population)
    ]
    expected_weighted = [
        elites[fitness_order[index % len(fitness_order)]]["grid"]["grid_id"]
        for index in range(population)
    ]

    _, default_report = evolve(
        seed_grids,
        slip_profile,
        generation_model,
        repair_model,
        readability_scorer=scorer,
        **config,
    )
    weighted_profile = v2_profile("fitness_weighted")
    weighted_pristine = deepcopy(weighted_profile)
    _, weighted_report = evolve(
        seed_grids,
        weighted_profile,
        generation_model,
        repair_model,
        readability_scorer=scorer,
        **config,
    )
    _, uniform_report = evolve(
        seed_grids,
        v2_profile("uniform"),
        generation_model,
        repair_model,
        readability_scorer=scorer,
        **config,
    )

    def generation_1_parents(report: dict) -> list[str]:
        return [
            creature["parent_grid_id"]
            for creature in report["generations"][1]["creatures"]
        ]

    invalid_mode_raised = _raised(
        lambda: evolve(
            seed_grids,
            v2_profile("strongest"),
            generation_model,
            repair_model,
            readability_scorer=scorer,
            **config,
        )
    )

    return {
        "orderings_genuinely_differ": expected_uniform != expected_weighted,
        "expected_uniform_parents": expected_uniform,
        "expected_weighted_parents": expected_weighted,
        "default_generation_1_parents": generation_1_parents(default_report),
        "weighted_generation_1_parents": generation_1_parents(weighted_report),
        "uniform_generation_1_parents": generation_1_parents(uniform_report),
        "default_report_has_parent_selection": "parent_selection"
        in default_report,
        "weighted_parent_selection": weighted_report.get("parent_selection"),
        "uniform_parent_selection": uniform_report.get("parent_selection"),
        "default_generation_1_source": default_report["generations"][1][
            "parent_source"
        ],
        "weighted_generation_1_source": weighted_report["generations"][1][
            "parent_source"
        ],
        "uniform_generation_1_source": uniform_report["generations"][1][
            "parent_source"
        ],
        "weighted_profile_mutated": weighted_profile != weighted_pristine,
        "invalid_mode_raised": invalid_mode_raised,
    }


def probe_live_cycle(seed_grid: dict, slip_profile: dict, repair_model: dict) -> dict:
    first = live_cycle(
        seed_grid,
        slip_profile,
        repair_model,
        damage_cycles=2,
        ticks=12,
        dropout_rate=0.2,
        rng_seed=20260512,
    )
    second = live_cycle(
        seed_grid,
        slip_profile,
        repair_model,
        damage_cycles=2,
        ticks=12,
        dropout_rate=0.2,
        rng_seed=20260512,
    )
    return {
        "deterministic_repeat_identical": first == second,
        "result_json_roundtrip": _json_roundtrip(first),
        "damage_source": first["damage_source"],
        "cycle_count": len(first["cycles"]),
        "cycles_requested": first["cycles_requested"],
        "cycle_fields": sorted(first["cycles"][0]),
        "every_cycle_reports_removed_cells": all(
            isinstance(cycle["removed_cell_count"], int)
            for cycle in first["cycles"]
        ),
        "final_state_fields": sorted(first["final_state"]),
        "final_state_valid": first["final_state"]["valid"],
        "final_state_aligned": first["final_state"]["aligned"],
        "final_grid_id_reassigned": first["final_grid"]["grid_id"]
        == f"{seed_grid['grid_id']}_c{len(first['cycles']):02d}",
        "aligned_cycles_have_episodes": all(
            cycle["episode"] is not None
            for cycle in first["cycles"]
            if cycle["aligned"]
        ),
    }


def probe_injected_events(
    seed_grid: dict, slip_profile: dict, repair_model: dict
) -> dict:
    wound = _probe_sites(seed_grid, 2)
    events = [{"removed_cells": wound}, {"removed_cells": []}]
    events_pristine = deepcopy(events)

    result = live_cycle(
        seed_grid,
        slip_profile,
        repair_model,
        ticks=12,
        rng_seed=20260512,
        damage_events=events,
    )
    again = live_cycle(
        seed_grid,
        slip_profile,
        repair_model,
        ticks=12,
        rng_seed=20260512,
        damage_events=events,
    )

    # The pure no-op path: a single empty event on the pristine grid must
    # leave the creature's live tokens exactly as they were.
    noop = live_cycle(
        seed_grid,
        slip_profile,
        repair_model,
        ticks=12,
        rng_seed=20260512,
        damage_events=[{"removed_cells": []}],
    )

    wound_cycle = result["cycles"][0]
    empty_cycle = result["cycles"][1]
    return {
        "damage_source": result["damage_source"],
        "events_define_cycle_count": len(result["cycles"]) == len(events)
        and result["cycles_requested"] == len(events),
        "deterministic_repeat_identical": result == again,
        "wound_cycle_removed_cell_count": wound_cycle["removed_cell_count"],
        "wound_cycle_position_restoration": wound_cycle["position_restoration"],
        "empty_event_removed_cell_count": empty_cycle["removed_cell_count"],
        "empty_event_position_restoration": empty_cycle["position_restoration"],
        "empty_event_token_restoration": empty_cycle["token_restoration"],
        "empty_event_guard_substitutions": empty_cycle["guard_substitutions"],
        "noop_tokens_unchanged": _token_map(noop["final_grid"])
        == _token_map(seed_grid),
        "events_mutated": events != events_pristine,
        "missing_removed_cells_raised": _raised(
            lambda: live_cycle(
                seed_grid,
                slip_profile,
                repair_model,
                ticks=12,
                rng_seed=20260512,
                damage_events=[{}],
            )
        ),
        "out_of_range_position_raised": _raised(
            lambda: live_cycle(
                seed_grid,
                slip_profile,
                repair_model,
                ticks=12,
                rng_seed=20260512,
                damage_events=[{"removed_cells": [[99, 99]]}],
            )
        ),
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
        _load(seed_dir / f"mg_seed_{index:03d}.json") for index in range(1, 51)
    ]
    slip_profile = _load(
        repo_root / "data" / "slips" / "valid" / "slip_lcd_seed.json"
    )

    generation_model = train_generation_model(seed_grids)
    repair_model = train_repair_model(
        seed_grids[:REPAIR_TRAINING_COUNT],
        epochs=REPAIR_EPOCHS,
        rng_seed=20260512,
    )

    fixtures_pristine = deepcopy([seed_grids, slip_profile, repair_model])
    generation_model_pristine = deepcopy(generation_model)

    # mg_seed_001 is a frozen profile-aligned creature (the lcd_green seed
    # family) — the live-cycle probe subject.
    live_subject = seed_grids[0]

    report = {
        "surface": probe_surface(),
        "evolve": probe_evolve(
            seed_grids, slip_profile, generation_model, repair_model
        ),
        "evolve_v2": probe_evolve_v2(
            seed_grids, slip_profile, generation_model, repair_model
        ),
        "invalid_repair_boundary": probe_invalid_repair_boundary(
            seed_grids, slip_profile, generation_model
        ),
        "live_cycle": probe_live_cycle(live_subject, slip_profile, repair_model),
        "injected_events": probe_injected_events(
            live_subject, slip_profile, repair_model
        ),
        "fixtures_mutated": fixtures_pristine
        != [seed_grids, slip_profile, repair_model],
        "generation_model_mutated": generation_model != generation_model_pristine,
        "lab_modules_loaded": probe_loaded_lab_modules(),
    }
    json.dump(report, sys.stdout)


if __name__ == "__main__":
    main()
