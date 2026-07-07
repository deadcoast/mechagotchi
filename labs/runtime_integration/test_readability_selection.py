import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAB_DIR = Path(__file__).resolve().parent
READABILITY = ROOT / "labs" / "readability_benchmark"
for path in [LAB_DIR, READABILITY]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from learned_readability import (  # noqa: E402
    build_degradation_pairs,
    build_learned_readability_report,
    train_pairwise_ranker,
)

from mecha_engine_runtime_loop import (  # noqa: E402
    run_mecha_engine_evolution_loop,
)


def _trained_model() -> dict:
    report = build_learned_readability_report(rng_seed=20260706)
    return report["model"]


MODEL = _trained_model()
ARM = {
    "weights": MODEL["weights"],
    "reference_features": MODEL["reference_features"],
}


class ReadabilitySelectionTests(unittest.TestCase):
    """R3 live consumer (DR 0019): evolution selects parents by a blend
    of archive fitness and LEARNED readability."""

    KW = dict(
        generations=4,
        population=6,
        damage_cycles=2,
        ticks=16,
        repair_epochs=20,
        rng_seed=20260706,
    )

    def test_arm_records_per_generation_readability_and_lab_id(self):
        report = run_mecha_engine_evolution_loop(
            readability_selection={**ARM, "blend": 0.7},
            **self.KW,
        )
        self.assertEqual(
            "mecha_engine_evolution_readability_selection_stage0",
            report["lab_id"],
        )
        block = report["readability_selection"]
        self.assertEqual(0.7, block["blend"])
        self.assertEqual(
            "learned_model_primary_manual_rating_fallback",
            block["readability_authority"],
        )
        means = block["mean_learned_readability_by_generation"]
        self.assertEqual(4, len(means))
        for value in means:
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)

    def test_learned_readability_moves_selection_measurably(self):
        # blend 0.0 = identical machinery, pure normalized fitness;
        # blend 0.7 = the learned model steering parenting. Same seed —
        # any difference is the model's influence.
        with_model = run_mecha_engine_evolution_loop(
            readability_selection={**ARM, "blend": 0.7},
            **self.KW,
        )
        without_model = run_mecha_engine_evolution_loop(
            readability_selection={**ARM, "blend": 0.0},
            **self.KW,
        )
        on = with_model["readability_selection"][
            "mean_learned_readability_by_generation"
        ]
        off = without_model["readability_selection"][
            "mean_learned_readability_by_generation"
        ]
        # Post-founder generations (selection acts from generation 1).
        self.assertGreater(sum(on[1:]) / len(on[1:]), sum(off[1:]) / len(off[1:]))

    def test_deterministic(self):
        first = run_mecha_engine_evolution_loop(
            readability_selection={**ARM, "blend": 0.7},
            **self.KW,
        )
        second = run_mecha_engine_evolution_loop(
            readability_selection={**ARM, "blend": 0.7},
            **self.KW,
        )
        self.assertEqual(first, second)

    def test_absent_arm_is_byte_identical_frozen(self):
        report = run_mecha_engine_evolution_loop(**self.KW)
        self.assertNotIn("readability_selection", report)
        self.assertEqual(
            "mecha_engine_evolution_loop_stage0", report["lab_id"]
        )


if __name__ == "__main__":
    unittest.main()
