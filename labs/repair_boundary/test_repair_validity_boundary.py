"""C6: the repair-validity boundary is measured on the production
surface, the failing invariant is named, and the verdict is
evidence-backed (deterministic; scaled-down regime for test speed)."""

import sys
import unittest
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
ROOT = LAB_DIR.parents[1]
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

import repair_validity_boundary as study  # noqa: E402
from repair_validity_boundary import (  # noqa: E402
    build_seed_grids,
    diagnose_causes,
    measure_regime,
)

from mecha_engine.generation import train_generation_model  # noqa: E402
from mecha_engine.repair import train_repair_model  # noqa: E402


class RepairBoundaryStudyTests(unittest.TestCase):
    seeds: list[dict]

    @classmethod
    def setUpClass(cls):
        import json

        cls.seeds = build_seed_grids()
        cls.slip = json.loads(
            (
                ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json"
            ).read_text(encoding="utf-8")
        )
        cls.generation_model = train_generation_model(cls.seeds)
        cls.repair_model = train_repair_model(
            cls.seeds[:40], epochs=20, rng_seed=study.RNG_SEED
        )
        # A tiny seed set keeps the production evolve runs fast.
        cls._saved_seeds = study.EVOLVE_SEEDS
        study.EVOLVE_SEEDS = (20260700, 20260703, 20260709)

    @classmethod
    def tearDownClass(cls):
        study.EVOLVE_SEEDS = cls._saved_seeds

    def test_measurement_runs_on_the_production_evolve_surface(self):
        regime = measure_regime(
            self.seeds,
            self.slip,
            self.generation_model,
            self.repair_model,
            dropout_rate=0.9,
            damage_cycles=4,
        )
        # Every creature is accounted for by a decision.
        self.assertEqual(
            regime["total_creatures"],
            regime["skipped_invalid"]
            + regime["skipped_unaligned"]
            + regime["survived_to_archive"],
        )
        # Harsh damage produces at least one mortal wound (the boundary
        # exists — otherwise the study has nothing to measure).
        self.assertGreater(regime["skipped_invalid"], 0)

    def test_measurement_is_deterministic(self):
        kw = dict(dropout_rate=0.6, damage_cycles=2)
        first = measure_regime(
            self.seeds, self.slip, self.generation_model, self.repair_model, **kw
        )
        second = measure_regime(
            self.seeds, self.slip, self.generation_model, self.repair_model, **kw
        )
        self.assertEqual(first, second)

    def test_the_failing_invariant_is_the_disconnected_body_core(self):
        # The mortal-wound claim is evidence-backed, not assumed: the
        # only invariant the diagnosis finds broken is the core.
        saved = study.EVOLVE_SEEDS
        study.EVOLVE_SEEDS = (20260700, 20260703)
        try:
            diagnosis = diagnose_causes(
                self.seeds,
                self.slip,
                self.generation_model,
                self.repair_model,
            )
        finally:
            study.EVOLVE_SEEDS = saved
        self.assertTrue(diagnosis["final_grid_invalid_causes"])
        for cause in diagnosis["final_grid_invalid_causes"]:
            self.assertIn("body core", cause)
        self.assertTrue(diagnosis["core_disconnect_is_the_only_cause"])

    def test_report_records_the_refuted_hypothesis_and_verdict(self):
        saved = study.EVOLVE_SEEDS
        study.EVOLVE_SEEDS = (20260700, 20260703)
        try:
            report = study.build_boundary_report(
                self.seeds,
                self.slip,
                self.repair_model,
                self.generation_model,
            )
        finally:
            study.EVOLVE_SEEDS = saved
        self.assertEqual(
            "REFUTED", report["metrics"]["hypothesis_extreme_damage_only"]
        )
        self.assertEqual(
            "boundary_is_a_mortal_wound_gradient_skip_retained",
            report["decision"]["status"],
        )
        self.assertIn("REJECTED", report["decision"]["reason"])
        # JSON-serializable end to end.
        import json

        json.dumps(report)


if __name__ == "__main__":
    unittest.main()
