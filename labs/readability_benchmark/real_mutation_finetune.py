"""Real-mutation fine-tune of the readability ranker (F3, E3's follow-up).

E3 measured the shipped R3 model at 0.983 on physics-DEGRADED real
mutation pairs but 0.849 on physics-IMPROVED ones — exactly what
training exclusively on synthetic degradations predicts. F3 asks the
falsifiable question: does AUGMENTING the training corpus with
mutationbench_5000's physics-labeled REAL pairs produce a better model
— without regressing the original synthetic gates?

Method (verdict recorded, not asserted; adopt only if it wins ALL):

1. **The real corpus** — E3's labeling verbatim: every bench case is
   regenerated deterministically (signatures re-verified) and admitted
   only when monotone across the four physics-verified metrics.
   Held out BY PARENT (the last ten seed parents' cases) so the
   evaluation is cross-parent generalization, never memorization.
2. **The models** — original: R3's exact recipe (pairs_per_family=3,
   seed 20260706, 80/20 split). Augmented: the SAME synthetic training
   pairs plus the real training pairs, same trainer, same seed, same
   corpus-mean anchor (comparable absolute scores by construction).
3. **The gates** —
   (a) real heldout pairwise accuracy must IMPROVE;
   (b) the synthetic evaluation must NOT regress (heldout accuracy and
       per-family accuracy over the full synthetic corpus);
   (c) a live physics A/B at the same seed: `evolve` steered by each
       model, both arms' elites judged by the NEUTRAL physics composite
       (the mean of the four verified metrics) — the augmented arm must
       not produce physically less-legible elites.

The manual rating system remains the fallback throughout (DR 0019).
Deterministic; stdlib + package surfaces + the lab authorities.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GRID_GENOME = ROOT / "labs" / "grid_genome"
DATASETS = ROOT / "labs" / "datasets"
LAB_DIR = Path(__file__).resolve().parent
PACKAGE_SRC = ROOT / "packages" / "mecha_engine" / "src"
for path in [LAB_DIR, GRID_GENOME, DATASETS, PACKAGE_SRC]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from corpus_builder import build_seed_grids  # noqa: E402
from dataset_consumers import (  # noqa: E402
    PHYSICS_METRICS,
    _physics_label,
    load_bench_rows,
)
from learned_readability import (  # noqa: E402
    DEGRADATION_FAMILIES,
    FEATURE_NAMES,
    _pairwise_accuracy,
    build_degradation_pairs,
    extract_readability_features,
    train_pairwise_ranker,
)
from readability_benchmark import score_readability  # noqa: E402

from mecha_engine.generation import (  # noqa: E402
    generate_candidate,
    train_generation_model,
)
from mecha_engine.genome import grid_signature  # noqa: E402
from mecha_engine.repair import train_repair_model  # noqa: E402
from mecha_engine.runtime import evolve  # noqa: E402

ARTIFACT_ID = "real_mutation_finetune_stage0"
REPORT_DATE = "2026-07-07"
DEFAULT_OUTPUT_DIR = ROOT / "data" / "readability_benchmark"
RNG_SEED = 20260706  # the shipped model's seed — same everywhere
HELDOUT_PARENT_PREFIXES = tuple(
    f"mg_seed_{index:03d}" for index in range(41, 51)
)
LIVE_AB_SEED = 20260707
LIVE_AB_KW = dict(
    generations=3, population=4, damage_cycles=2, ticks=16, dropout_rate=0.2
)


def build_real_pairs(
    seeds_by_id: dict[str, dict],
    generation_model: dict,
    slip_profile: dict,
) -> tuple[list[dict], list[dict]]:
    """(train_pairs, heldout_pairs) from mutationbench, physics-labeled
    by E3's rule, held out by PARENT."""
    train: list[dict] = []
    heldout: list[dict] = []
    for row in load_bench_rows():
        parent = seeds_by_id[row["parent_grid_id"]]
        child = generate_candidate(
            parent, generation_model, slip_profile, rng_seed=row["rng_seed"]
        )
        if grid_signature(child) != row["candidate_signature"]:
            raise AssertionError(
                f"dataset integrity: {row['case_id']} signature mismatch"
            )
        parent_features = extract_readability_features(parent)
        child_features = extract_readability_features(child)
        label = _physics_label(parent_features, child_features)
        if label == "unlabeled":
            continue
        if label == "physics_degraded":
            pair = {
                "family": "real_degraded",
                "better_features": parent_features,
                "worse_features": child_features,
            }
        else:
            pair = {
                "family": "real_improved",
                "better_features": child_features,
                "worse_features": parent_features,
            }
        bucket = (
            heldout
            if row["parent_grid_id"].startswith(HELDOUT_PARENT_PREFIXES)
            else train
        )
        bucket.append(pair)
    return train, heldout


def train_models(seeds: list[dict], real_train: list[dict]) -> dict:
    """The shipped-recipe original and the augmented sibling, sharing
    the synthetic split, the trainer, the seed, and the anchor."""
    import random

    synthetic = build_degradation_pairs(
        seeds, pairs_per_family=3, rng_seed=RNG_SEED
    )
    rng = random.Random(RNG_SEED)
    shuffled = list(synthetic)
    rng.shuffle(shuffled)
    split = int(len(shuffled) * 0.8)
    synthetic_train, synthetic_heldout = shuffled[:split], shuffled[split:]

    anchor = {
        name: round(
            sum(
                extract_readability_features(grid)[name] for grid in seeds
            )
            / len(seeds),
            6,
        )
        for name in FEATURE_NAMES
    }
    original = train_pairwise_ranker(synthetic_train, rng_seed=RNG_SEED)
    original["reference_features"] = anchor
    augmented = train_pairwise_ranker(
        synthetic_train + real_train, rng_seed=RNG_SEED
    )
    augmented["reference_features"] = anchor
    return {
        "original": original,
        "augmented": augmented,
        "synthetic_all": synthetic,
        "synthetic_heldout": synthetic_heldout,
    }


def physics_composite(grid: dict) -> float:
    features = extract_readability_features(grid)
    return round(
        sum(features[m] for m in PHYSICS_METRICS) / len(PHYSICS_METRICS), 6
    )


def live_physics_ab(
    seeds: list[dict],
    slip_profile: dict,
    generation_model: dict,
    models: dict,
) -> dict:
    """One evolve run per arm at the same seed; each arm's elites judged
    by the NEUTRAL physics composite."""
    repair_model = train_repair_model(
        seeds[:40], epochs=20, rng_seed=LIVE_AB_SEED
    )
    arms = {}
    for arm_name in ("original", "augmented"):
        model = models[arm_name]
        archive, _ = evolve(
            seeds,
            slip_profile,
            generation_model,
            repair_model,
            readability_scorer=score_readability,
            rng_seed=LIVE_AB_SEED,
            readability_selection={
                "weights": model["weights"],
                "reference_features": model["reference_features"],
                "blend": 0.7,
            },
            **LIVE_AB_KW,
        )
        elites = [
            archive["elites"][niche]["grid"]
            for niche in sorted(archive["elites"])
        ]
        arms[arm_name] = {
            "elite_count": len(elites),
            "mean_physics_composite": round(
                sum(physics_composite(grid) for grid in elites)
                / len(elites),
                6,
            )
            if elites
            else None,
        }
    return arms


def build_finetune_report() -> dict:
    seeds = build_seed_grids()
    seeds_by_id = {seed["grid_id"]: seed for seed in seeds}
    slip_profile = json.loads(
        (ROOT / "data" / "datasets" / "slip_corpus_r6.json").read_text(
            encoding="utf-8"
        )
    )
    generation_model = train_generation_model(seeds)
    real_train, real_heldout = build_real_pairs(
        seeds_by_id, generation_model, slip_profile
    )
    models = train_models(seeds, real_train)

    evaluation = {}
    for arm in ("original", "augmented"):
        model = models[arm]
        per_family = {
            family: _pairwise_accuracy(
                model,
                [p for p in models["synthetic_all"] if p["family"] == family],
            )
            for family in DEGRADATION_FAMILIES
        }
        evaluation[arm] = {
            "real_heldout_accuracy": _pairwise_accuracy(model, real_heldout),
            "real_heldout_by_direction": {
                direction: _pairwise_accuracy(
                    model,
                    [p for p in real_heldout if p["family"] == direction],
                )
                for direction in ("real_degraded", "real_improved")
            },
            "synthetic_heldout_accuracy": _pairwise_accuracy(
                model, models["synthetic_heldout"]
            ),
            "synthetic_per_family_accuracy": per_family,
        }

    live = live_physics_ab(seeds, slip_profile, generation_model, models)

    original = evaluation["original"]
    augmented = evaluation["augmented"]
    gates = {
        "real_heldout_improves": augmented["real_heldout_accuracy"]
        > original["real_heldout_accuracy"],
        "synthetic_heldout_no_regression": augmented[
            "synthetic_heldout_accuracy"
        ]
        >= original["synthetic_heldout_accuracy"],
        "synthetic_families_no_regression": all(
            augmented["synthetic_per_family_accuracy"][family]
            >= original["synthetic_per_family_accuracy"][family]
            for family in DEGRADATION_FAMILIES
        ),
        "live_physics_not_worse": (
            live["augmented"]["mean_physics_composite"] is not None
            and live["original"]["mean_physics_composite"] is not None
            and live["augmented"]["mean_physics_composite"]
            >= live["original"]["mean_physics_composite"]
        ),
    }
    adopt = all(gates.values())

    return {
        "artifact_id": ARTIFACT_ID,
        "status": "stage0_complete",
        "date": REPORT_DATE,
        "purpose": (
            "F3: augment the R3 ranker with mutationbench_5000's "
            "physics-labeled REAL pairs and decide by measurement — "
            "adopt only if the real heldout improves, the synthetic "
            "gates hold, and the live physics A/B is not worse."
        ),
        "source_artifacts": [
            "research/experiment_reports/2026-07-07-dataset-consumers.md",
            "data/datasets/mutationbench_5000/mutationbench_5000.jsonl",
            "research/decision_records/0019-learned-readability.md",
        ],
        "corpus": {
            "real_train_pairs": len(real_train),
            "real_heldout_pairs": len(real_heldout),
            "heldout_parents": list(HELDOUT_PARENT_PREFIXES),
            "synthetic_pairs": len(models["synthetic_all"]),
        },
        "evaluation": evaluation,
        "live_physics_ab": live,
        "gates": gates,
        "closed_states": [
            "real_pairs_built_by_the_e3_rule_with_signature_verification",
            "heldout_by_parent_cross_parent_generalization",
            "same_recipe_same_seed_same_anchor_comparable_models",
            "verdict_decided_by_the_three_gates_not_asserted",
        ],
        "blocked_states": [],
        "decision": {
            "status": "adopt_augmented_model"
            if adopt
            else "keep_original_model",
            "adoption": "lab_only_readability_evidence",
            "reason": (
                "Gates: real heldout "
                + f"{original['real_heldout_accuracy']} -> "
                + f"{augmented['real_heldout_accuracy']} "
                + ("(improved)" if gates["real_heldout_improves"] else "(NOT improved)")
                + "; synthetic heldout "
                + f"{original['synthetic_heldout_accuracy']} -> "
                + f"{augmented['synthetic_heldout_accuracy']}"
                + "; live physics "
                + f"{live['original']['mean_physics_composite']} -> "
                + f"{live['augmented']['mean_physics_composite']}. "
                + (
                    "All gates green: the augmented model wins and is "
                    "adopted."
                    if adopt
                    else "At least one gate failed: the ORIGINAL model "
                    "stays — the verdict is the measurement, and the "
                    "physics-labeled real corpus remains available for "
                    "future training work."
                )
            ),
        },
        "next_research_step": (
            "If adopted, the session's legibility trainer switches to "
            "the augmented recipe (its own follow-through with artifact "
            "regeneration); if kept, nothing changes and the corpus "
            "stands ready."
        ),
    }


def build_adopted_model_artifact(report: dict) -> dict | None:
    """When the gates adopt the augmented model, freeze its weights as a
    committed, auditable artifact (the R3 doctrine: learned weights are
    inspectable data) — the session's legibility trainer LOADS this
    instead of retraining, and this lab is its regenerator."""
    if report["decision"]["status"] != "adopt_augmented_model":
        return None
    seeds = build_seed_grids()
    real_train, _ = build_real_pairs(
        {seed["grid_id"]: seed for seed in seeds},
        train_generation_model(seeds),
        json.loads(
            (ROOT / "data" / "datasets" / "slip_corpus_r6.json").read_text(
                encoding="utf-8"
            )
        ),
    )
    models = train_models(seeds, real_train)
    augmented = models["augmented"]
    return {
        "model_id": "readability_ranker_real_augmented_v1",
        "date": REPORT_DATE,
        "provenance": {
            "recipe": (
                "R3 synthetic training pairs (pairs_per_family=3, seed "
                "20260706, 80% split) + mutationbench real pairs "
                "(physics-labeled, heldout parents excluded), "
                "train_pairwise_ranker at the same seed, corpus-mean "
                "anchor"
            ),
            "adopted_by": "data/readability_benchmark/real_mutation_finetune_stage0.json",
            "regenerator": "labs/readability_benchmark/real_mutation_finetune.py",
        },
        "weights": augmented["weights"],
        "reference_features": augmented["reference_features"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fine-tune the readability ranker on real mutations (F3)."
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    report = build_finetune_report()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "real_mutation_finetune_stage0.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    adopted = build_adopted_model_artifact(report)
    if adopted is not None:
        (args.output_dir / "adopted_readability_model.json").write_text(
            json.dumps(adopted, indent=2) + "\n", encoding="utf-8"
        )
    print(
        json.dumps(
            {
                "artifact_id": report["artifact_id"],
                "decision": report["decision"]["status"],
                "gates": report["gates"],
                "real_heldout": {
                    arm: report["evaluation"][arm]["real_heldout_accuracy"]
                    for arm in ("original", "augmented")
                },
                "live_physics": {
                    arm: report["live_physics_ab"][arm][
                        "mean_physics_composite"
                    ]
                    for arm in ("original", "augmented")
                },
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
