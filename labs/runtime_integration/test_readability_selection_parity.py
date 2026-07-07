"""Parity pin: lab readability-selection vs mecha_engine.runtime.evolve
(C1, decision record 0025 — R3's live consumer promoted).

The frozen v0.1 pin stays untouched; this file adds the DR 0025
surface: a ``readability_selection`` arm must steer package ``evolve``
parenting exactly as it steers the lab loop (blend of learned
readability and min-max-normalized fitness, ``archive_elites_
readability_blend`` parent source, per-generation candidate means), the
directional R3 claim must hold on the PROMOTED surface (same seed,
blend 0.7 vs 0.0 — identical machinery, only the model's influence
differs), and the default ``None`` flow stays byte-identical."""

import sys
import unittest
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
REPO_ROOT = LAB_DIR.parents[1]
GRID_GENOME = REPO_ROOT / "labs" / "grid_genome"
READABILITY = REPO_ROOT / "labs" / "readability_benchmark"
PACKAGE_SRC = REPO_ROOT / "packages" / "mecha_engine" / "src"
for path in [LAB_DIR, GRID_GENOME, READABILITY]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from corpus_builder import build_seed_grids  # noqa: E402
from learned_readability import (  # noqa: E402
    build_learned_readability_report,
)
from readability_benchmark import score_readability  # noqa: E402

from mecha_engine_runtime_loop import (  # noqa: E402
    run_mecha_engine_evolution_loop,
)

from mecha_engine.generation import train_generation_model  # noqa: E402
from mecha_engine.repair import train_repair_model  # noqa: E402
from mecha_engine.runtime import evolve  # noqa: E402


PARITY_RNG_SEED = 20260706
PARITY_KW = dict(
    generations=4,
    population=6,
    damage_cycles=2,
    ticks=16,
    rng_seed=PARITY_RNG_SEED,
)
REPAIR_EPOCHS = 20
REPAIR_TRAINING_COUNT = 40  # the lab loop's fixed training split


def _trained_arm() -> dict:
    model = build_learned_readability_report(rng_seed=20260706)["model"]
    return {
        "weights": model["weights"],
        "reference_features": model["reference_features"],
    }


ARM = _trained_arm()


class PackageReadabilitySelectionParityTests(unittest.TestCase):
    seeds: list[dict]

    @classmethod
    def setUpClass(cls):
        cls.seeds = build_seed_grids()
        cls.generation_model = train_generation_model(cls.seeds)
        cls.repair_model = train_repair_model(
            cls.seeds[:REPAIR_TRAINING_COUNT],
            epochs=REPAIR_EPOCHS,
            rng_seed=PARITY_RNG_SEED,
        )

    def _package_report(self, blend: float | None) -> dict:
        import json

        slip_profile = json.loads(
            (
                REPO_ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json"
            ).read_text(encoding="utf-8")
        )
        _, report = evolve(
            self.seeds,
            slip_profile,
            self.generation_model,
            self.repair_model,
            readability_scorer=score_readability,
            dropout_rate=0.2,
            readability_selection=(
                {**ARM, "blend": blend} if blend is not None else None
            ),
            **PARITY_KW,
        )
        return report

    def _lab_report(self, blend: float | None) -> dict:
        return run_mecha_engine_evolution_loop(
            repair_epochs=REPAIR_EPOCHS,
            readability_selection=(
                {**ARM, "blend": blend} if blend is not None else None
            ),
            **PARITY_KW,
        )

    def test_readability_selection_records_match_the_lab(self):
        lab_report = self._lab_report(0.7)
        package_report = self._package_report(0.7)
        self.assertEqual(
            "archive_elites_readability_blend",
            package_report["generations"][1]["parent_source"],
        )
        self.assertEqual(
            lab_report["generations"], package_report["generations"]
        )
        self.assertEqual(lab_report["summary"], package_report["summary"])
        self.assertEqual(
            lab_report["readability_selection"],
            package_report["readability_selection"],
        )

    def test_the_model_measurably_steers_the_promoted_surface(self):
        # blend 0.0 = identical machinery, pure normalized fitness;
        # blend 0.7 = the learned model steering. Same seed — any
        # difference is the model's influence (the R3 A/B, promoted).
        on = self._package_report(0.7)["readability_selection"][
            "mean_learned_readability_by_generation"
        ]
        off = self._package_report(0.0)["readability_selection"][
            "mean_learned_readability_by_generation"
        ]
        self.assertGreater(
            sum(on[1:]) / len(on[1:]), sum(off[1:]) / len(off[1:])
        )

    def test_default_flow_is_byte_identical_frozen(self):
        report = self._package_report(None)
        self.assertNotIn("readability_selection", report)
        lab_report = self._lab_report(None)
        self.assertEqual(lab_report["generations"], report["generations"])
        self.assertEqual(lab_report["summary"], report["summary"])

    def test_readability_wins_over_lineage_preferences_like_the_lab(self):
        import json

        profile = json.loads(
            (
                REPO_ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json"
            ).read_text(encoding="utf-8")
        )
        profile["slip_version"] = "0.2.0"
        profile["lineage_preferences"] = {"parent_selection": "fitness_weighted"}
        _, report = evolve(
            self.seeds,
            profile,
            self.generation_model,
            self.repair_model,
            readability_scorer=score_readability,
            dropout_rate=0.2,
            readability_selection={**ARM, "blend": 0.7},
            **PARITY_KW,
        )
        lab_report = run_mecha_engine_evolution_loop(
            repair_epochs=REPAIR_EPOCHS,
            slip_profile=profile,
            readability_selection={**ARM, "blend": 0.7},
            **PARITY_KW,
        )
        self.assertEqual(
            "archive_elites_readability_blend",
            report["generations"][1]["parent_source"],
        )
        self.assertEqual(
            lab_report["generations"], report["generations"]
        )

    def test_invalid_arm_is_rejected(self):
        with self.assertRaises(ValueError):
            self._package_report_invalid()

    def _package_report_invalid(self):
        import json

        slip_profile = json.loads(
            (
                REPO_ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json"
            ).read_text(encoding="utf-8")
        )
        return evolve(
            self.seeds,
            slip_profile,
            self.generation_model,
            self.repair_model,
            readability_scorer=score_readability,
            readability_selection={"blend": 0.7},  # no weights
            **PARITY_KW,
        )


if __name__ == "__main__":
    unittest.main()
