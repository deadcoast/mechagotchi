"""CuBFF pressure contract probe driver (R2.5, decision record 0020).

``tests/test_runtime_cubff_contract.py`` launches this script in a
subprocess whose PYTHONPATH points at the package ``src`` directory
(the same documented import mechanics as every contract suite), so the
probes exercise ``mecha_engine.runtime.evolve`` and its promoted
dependencies only — never research lab modules. The lab-side parity pin
(``labs/cubff_transducer/test_package_cubff_parity.py``) proves the
``runtime/_cubff.py`` mirror matches the lab authority verbatim; this
driver proves the package contract directly.

Fixtures: the frozen seed corpus and SLIP profile, plus hand-built
stable/chaotic CuBFF snapshots (real ingested exports are absent —
``data/cubff_real_ingest`` reports ``awaiting_real_cubff_snapshots`` —
so the real-snapshot clause is a recorded blocked state, not a probe).
"""

from __future__ import annotations

import inspect
import json
import sys
from pathlib import Path

from mecha_engine.generation import train_generation_model
from mecha_engine.repair import train_repair_model
from mecha_engine.runtime import evolve


EVOLVE_CONFIG = {
    "generations": 3,
    "population": 2,
    "damage_cycles": 2,
    "ticks": 12,
    "dropout_rate": 0.2,
    "rng_seed": 20260512,
}
CONSTANT_READABILITY = 0.6
REPAIR_EPOCHS = 40
REPAIR_TRAINING_COUNT = 12


def _stable_snapshot(index: int) -> dict:
    return {
        "snapshot_id": f"stable_{index:03d}",
        "epoch": 100 + index,
        "language": "bff_noheads",
        "program_size": 64,
        "tape": [7, 7, 7, 8, 7, 7, 7, 8] * 8,
        "replication_scores": [64, 64, 64, 48, 64, 64, 48, 64],
        "brotli_size": 12,
        "lineage_events": [{"parent": 0, "child": 0}],
    }


def _chaotic_snapshot(index: int) -> dict:
    return {
        "snapshot_id": f"chaotic_{index:03d}",
        "epoch": 100 + index,
        "language": "bff_noheads",
        "program_size": 64,
        "tape": [(index * 13 + p * 31) % 64 for p in range(64)],
        "replication_scores": [0, 4, 8, 0, 4, 8, 0, 4],
        "brotli_size": 57,
        "lineage_events": [
            {"parent": p % 8, "child": (p + 1) % 8} for p in range(8)
        ],
    }


def _total_removed(report: dict) -> int:
    return sum(
        cycle["removed_cell_count"]
        for generation in report["generations"]
        for creature in generation["creatures"]
        for cycle in creature["cycles"]
    )


def main() -> None:
    repo_root = Path(sys.argv[1]).resolve()
    seeds = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((repo_root / "data" / "seed_grids").glob("*.json"))
    ]
    slip_profile = json.loads(
        (repo_root / "data" / "slips" / "valid" / "slip_lcd_seed.json")
        .read_text(encoding="utf-8")
    )
    generation_model = train_generation_model(seeds)
    repair_model = train_repair_model(
        seeds[:REPAIR_TRAINING_COUNT], epochs=REPAIR_EPOCHS
    )

    def run(**extra):
        _, report = evolve(
            seeds,
            slip_profile,
            generation_model,
            repair_model,
            readability_scorer=lambda grid: CONSTANT_READABILITY,
            **EVOLVE_CONFIG,
            **extra,
        )
        return report

    checks: dict[str, object] = {}

    signature = inspect.signature(evolve)
    checks["accepts_cubff_pressure_source_keyword"] = (
        "cubff_pressure_source" in signature.parameters
        and signature.parameters["cubff_pressure_source"].kind
        is inspect.Parameter.KEYWORD_ONLY
        and signature.parameters["cubff_pressure_source"].default is None
    )

    baseline = run()
    explicit_none = run(cubff_pressure_source=None)
    checks["absent_source_byte_identical"] = (
        baseline == explicit_none and "cubff_pressure" not in baseline
    )

    chaotic = [_chaotic_snapshot(i) for i in range(2)]
    stable = [_stable_snapshot(i) for i in range(2)]
    active = run(cubff_pressure_source=chaotic)
    block = active.get("cubff_pressure", {})
    by_generation = block.get("by_generation", [])
    checks["report_block_present"] = (
        block.get("semantic_rule")
        == "lineage_dynamics_to_mutation_weights_pipeline_c"
        and block.get("pressure_gain") == 1.1
        and block.get("multiplier_band") == [0.5, 1.6]
        and block.get("source_snapshot_count") == 2
        and len(by_generation) == EVOLVE_CONFIG["generations"]
    )
    checks["scalars_only_cross_the_boundary"] = all(
        set(entry) == {"snapshot_id", "mutation_pressure", "dropout_multiplier"}
        and isinstance(entry["snapshot_id"], str)
        and isinstance(entry["mutation_pressure"], float)
        and isinstance(entry["dropout_multiplier"], float)
        and 0.5 <= entry["dropout_multiplier"] <= 1.6
        for entry in by_generation
    )
    checks["snapshots_cycle_in_order"] = [
        entry["snapshot_id"] for entry in by_generation
    ] == ["chaotic_000", "chaotic_001", "chaotic_000"]

    checks["deterministic"] = active == run(cubff_pressure_source=chaotic)

    calm = run(cubff_pressure_source=stable)
    checks["directional_effect"] = _total_removed(active) > _total_removed(calm)
    checks["directional_detail"] = {
        "chaotic_removed": _total_removed(active),
        "stable_removed": _total_removed(calm),
        "chaotic_multiplier": by_generation[0]["dropout_multiplier"],
        "stable_multiplier": calm["cubff_pressure"]["by_generation"][0][
            "dropout_multiplier"
        ],
    }

    for label, bad in [
        ("rejects_non_list_source", "not-a-list"),
        ("rejects_empty_source", []),
    ]:
        try:
            run(cubff_pressure_source=bad)
            checks[label] = False
        except ValueError:
            checks[label] = True

    print(json.dumps(checks))


if __name__ == "__main__":
    main()
