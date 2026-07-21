"""The 11-class regrowth head study (K1, DR 0041) — can repair learn
to spell what it preserves?

Trains the LEGACY head (5-class + the DR 0039 perception coarsening)
and the RICH head (the full ratified live alphabet, identity
perception) on the same committed 16x16 seed corpus — the ratified
default scale and the measured rich corpus (probed before the design
was fixed: all eleven live tokens present, 49/50 grids rich) — wounds
the held-out grids with seeded stochastic damage at the boundary
study's rates, repairs each wound through `repair_with_wound_sites`
(guard on), and measures restoration AT THE WOUND SITES:

- exact-token restoration (the refilled token equals the destroyed
  token — the thing the legacy head cannot do for seven of the eleven
  tokens),
- family-level restoration (both arms' outputs judged after the
  DR 0039 palette-family coarsening — the shape prior must not
  regress),
- post-repair validator validity and guard substitutions per arm.

The DR 0041 gates are pre-registered; this lab fills them from its own
measurements and records the adoption verdict the rule dictates. The
in-run G5 component trains the promoted `mecha_engine.repair` beside
the lab authority and requires byte-identical models (labs may import
the package; the reverse stays forbidden). Deterministic; stdlib plus
the package surface; run-once wall-clock bound registered at 900 s
(DR 0028 — an overage is cited, never silent).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GRID_GENOME = ROOT / "labs" / "grid_genome"
PACKAGE_SRC = ROOT / "packages" / "mecha_engine" / "src"
for path in [Path(__file__).resolve().parent, GRID_GENOME]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from ca_nca_growth_repair import (  # noqa: E402
    PERCEPTION_LIVE,
    apply_stochastic_damage,
    matrix_from_grid,
    repair_with_wound_sites,
    train_neighborhood_repair_model,
)
from corpus_builder import build_seed_grids_16  # noqa: E402
from validator import validate_grid  # noqa: E402

from mecha_engine.repair import (  # noqa: E402
    train_repair_model as package_train_repair_model,
)

ARTIFACT_ID = "regrowth_head11_stage0"
REPORT_DATE = "2026-07-21"
DEFAULT_OUTPUT_DIR = ROOT / "data" / "cellular_automata"
TRAINING_COUNT = 40
HELD_OUT_COUNT = 10
DROPOUT_RATES = (0.2, 0.4, 0.6)
DAMAGE_INSTANCES = 3
DAMAGE_RNG_SEED = 20260720
RUN_ONCE_BOUND_SECONDS = 900
# DR 0041 pre-registered bars (fixed before any run).
G1_EXACT_GAIN_BAR = 0.10
G2_FAMILY_TOLERANCE = 0.02

SOURCE_ARTIFACTS = [
    "research/decision_records/0041-eleven-class-regrowth-head.md",
    "research/decision_records/0039-repair-vocabulary-preservation.md",
    "labs/cellular_automata/ca_nca_growth_repair.py",
    "labs/grid_genome/corpus_builder.py",
    "packages/mecha_engine/src/mecha_engine/repair/",
]


def _family(token: str) -> str:
    return PERCEPTION_LIVE.get(token, token)


def measure_arm(
    model: dict,
    held_out: list[dict],
    *,
    dropout_rates: tuple[float, ...],
    damage_instances: int,
    damage_seed: int,
) -> dict:
    """Wound every held-out grid and measure restoration at the sites."""
    sites_measured = 0
    exact = 0
    family = 0
    valid = 0
    events = 0
    substitutions = 0
    # Observation, not a gate: restoration split by what was destroyed
    # (legacy-token sites vs rich-token sites) — the instrument that
    # measures the pooled metric's dilution rather than guessing at it.
    rich_sites = 0
    rich_exact = 0
    legacy_sites = 0
    legacy_exact = 0
    per_rate: dict[str, dict] = {}
    for rate_index, rate in enumerate(dropout_rates):
        rate_sites = 0
        rate_exact = 0
        for grid_index, grid in enumerate(held_out):
            original = matrix_from_grid(grid)
            for instance in range(damage_instances):
                seed = (
                    damage_seed
                    + grid_index * 1000
                    + rate_index * 100
                    + instance
                )
                damaged = apply_stochastic_damage(
                    grid,
                    dropout_rate=rate,
                    rng_seed=seed,
                    event_index=1,
                )
                repaired = repair_with_wound_sites(damaged, model)
                repaired_matrix = matrix_from_grid(repaired)
                events += 1
                substitutions += repaired["metadata"][
                    "validity_guard_substitutions"
                ]
                if validate_grid(repaired).ok:
                    valid += 1
                for x, y in damaged["metadata"]["removed_cells"]:
                    sites_measured += 1
                    rate_sites += 1
                    refilled = repaired_matrix[y][x]
                    destroyed = original[y][x]
                    destroyed_is_rich = destroyed not in {
                        "B", "A", "E", "M",
                    }
                    if destroyed_is_rich:
                        rich_sites += 1
                    else:
                        legacy_sites += 1
                    if refilled == destroyed:
                        exact += 1
                        rate_exact += 1
                        if destroyed_is_rich:
                            rich_exact += 1
                        else:
                            legacy_exact += 1
                    if _family(refilled) == _family(destroyed):
                        family += 1
        per_rate[str(rate)] = {
            "wound_sites": rate_sites,
            "exact_restoration": round(rate_exact / rate_sites, 6)
            if rate_sites
            else None,
        }
    return {
        "model_id": model["model_id"],
        "class_count": len(model["class_tokens"]),
        "wound_events": events,
        "wound_sites_measured": sites_measured,
        "exact_restoration": round(exact / sites_measured, 6)
        if sites_measured
        else None,
        "family_restoration": round(family / sites_measured, 6)
        if sites_measured
        else None,
        "valid_rate": round(valid / events, 6) if events else None,
        "guard_substitutions": substitutions,
        "per_dropout_rate": per_rate,
        "site_breakdown": {
            "rich_token_sites": rich_sites,
            "rich_site_exact_restoration": round(
                rich_exact / rich_sites, 6
            )
            if rich_sites
            else None,
            "legacy_token_sites": legacy_sites,
            "legacy_site_exact_restoration": round(
                legacy_exact / legacy_sites, 6
            )
            if legacy_sites
            else None,
        },
    }


def build_regrowth_head11_report(
    *,
    training_count: int = TRAINING_COUNT,
    held_out_count: int = HELD_OUT_COUNT,
    dropout_rates: tuple[float, ...] = DROPOUT_RATES,
    damage_instances: int = DAMAGE_INSTANCES,
    epochs: int = 150,
    rng_seed: int = 20260512,
    damage_seed: int = DAMAGE_RNG_SEED,
) -> dict:
    seeds = build_seed_grids_16()
    training = seeds[:training_count]
    held_out = seeds[training_count : training_count + held_out_count]

    legacy = train_neighborhood_repair_model(
        training, epochs=epochs, rng_seed=rng_seed
    )
    rich = train_neighborhood_repair_model(
        training, epochs=epochs, rng_seed=rng_seed, vocabulary="rich"
    )
    package_legacy = package_train_repair_model(
        training, epochs=epochs, rng_seed=rng_seed
    )
    package_rich = package_train_repair_model(
        training, epochs=epochs, rng_seed=rng_seed, vocabulary="rich"
    )

    legacy_metrics = measure_arm(
        legacy,
        held_out,
        dropout_rates=dropout_rates,
        damage_instances=damage_instances,
        damage_seed=damage_seed,
    )
    rich_metrics = measure_arm(
        rich,
        held_out,
        dropout_rates=dropout_rates,
        damage_instances=damage_instances,
        damage_seed=damage_seed,
    )

    exact_gain = round(
        rich_metrics["exact_restoration"]
        - legacy_metrics["exact_restoration"],
        6,
    )
    family_delta = round(
        rich_metrics["family_restoration"]
        - legacy_metrics["family_restoration"],
        6,
    )
    validity_delta = round(
        rich_metrics["valid_rate"] - legacy_metrics["valid_rate"], 6
    )
    gates = {
        "g1_exact_gain": {
            "bar": f">= +{G1_EXACT_GAIN_BAR}",
            "measured": exact_gain,
            "met": exact_gain >= G1_EXACT_GAIN_BAR,
        },
        "g2_family_held": {
            "bar": f">= -{G2_FAMILY_TOLERANCE}",
            "measured": family_delta,
            "met": family_delta >= -G2_FAMILY_TOLERANCE,
        },
        "g3_validity_held": {
            "bar": ">= 0.0",
            "measured": validity_delta,
            "met": validity_delta >= 0.0,
        },
        "g4_legacy_byte_identity": {
            "bar": "legacy model dict unchanged (no vocabulary key, "
            "historical classes and model_id)",
            "measured": {
                "vocabulary_key_absent": "vocabulary" not in legacy,
                "class_tokens": legacy["class_tokens"],
                "model_id": legacy["model_id"],
            },
            "met": "vocabulary" not in legacy
            and legacy["class_tokens"] == [".", "B", "A", "E", "M"]
            and legacy["model_id"]
            == "neighborhood_softmax_repair_model_stage0",
        },
        "g5_parity": {
            "bar": "lab and package train byte-identical models, "
            "both vocabularies",
            "measured": {
                "legacy_identical": legacy == package_legacy,
                "rich_identical": rich == package_rich,
            },
            "met": legacy == package_legacy and rich == package_rich,
        },
    }
    all_met = all(gate["met"] for gate in gates.values())
    verdict = "adopt_rich_head" if all_met else "withhold_adoption"

    return {
        "artifact_id": ARTIFACT_ID,
        "status": "complete",
        "date": REPORT_DATE,
        "purpose": (
            "DR 0041 K1: measure whether the 11-class regrowth head "
            "restores the rich vocabulary the repair stack preserves, "
            "without regressing the shape prior, validity, legacy "
            "byte-identity, or cross-site parity."
        ),
        "source_artifacts": SOURCE_ARTIFACTS,
        "configuration": {
            "corpus": "build_seed_grids_16 (the committed rich corpus)",
            "training_count": training_count,
            "held_out_count": held_out_count,
            "dropout_rates": list(dropout_rates),
            "damage_instances": damage_instances,
            "epochs": epochs,
            "rng_seed": rng_seed,
            "damage_seed": damage_seed,
            "run_once_bound_seconds": RUN_ONCE_BOUND_SECONDS,
        },
        "metrics": {"legacy": legacy_metrics, "rich": rich_metrics},
        "gates": gates,
        "decision": {
            "verdict": verdict,
            "rule": (
                "pre-registered (DR 0041): adopt only if G1-G5 all "
                "pass; the era-loop consumer then trains "
                "vocabulary='rich' and the coarsening retires from "
                "the rich path; any refusal is a first-class finding."
            ),
        },
        "closed_states": [
            "eleven_class_head_trainable_at_both_sites",
            "restoration_measured_per_arm_at_wound_sites",
        ],
        "blocked_states": [
            "adoption_execution_and_era_regression_recorded_in_the_"
            "experiment_report_not_here",
            "linear_softmax_architecture_ceiling_unmeasured_beyond_"
            "these_gates",
        ],
        "decision_note": (
            "The artifact records the measured verdict; the K1 "
            "experiment report executes (or withholds) the adoption "
            "per the rule and carries the era regression evidence."
        ),
        "next_research_step": (
            "If adopted: the boundary study re-measures under the "
            "rich head. If withheld: the refusal's numbers name the "
            "next lever (architecture, corpus, or training budget)."
        ),
    }


def write_regrowth_head11_artifacts(
    output_dir: str | Path, report: dict
) -> dict:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / f"{ARTIFACT_ID}.json"
    report_path.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    return {"report": str(report_path)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="directory for the stage-0 artifact",
    )
    args = parser.parse_args()
    report = build_regrowth_head11_report()
    paths = write_regrowth_head11_artifacts(args.output_dir, report)
    print(json.dumps({"written": paths, "gates": report["gates"],
                      "decision": report["decision"]}, indent=2))


if __name__ == "__main__":
    main()
