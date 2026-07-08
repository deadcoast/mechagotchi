import json
import tempfile
import unittest
from pathlib import Path

from stress_probe_scaling import (
    DENOMINATOR_LAWS,
    build_stress_probe_scaling_report,
    load_for,
    write_stress_probe_scaling_artifacts,
)


class StressProbeScalingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = build_stress_probe_scaling_report()

    def test_every_law_reproduces_the_8x8_denominator(self):
        # The 8x8 identity gate: at the proven scale every candidate law
        # must reproduce the engine's shipped /16 constant, so 8x8
        # behavior is byte-identical no matter which law is adopted.
        for name, law in DENOMINATOR_LAWS.items():
            with self.subTest(law=name):
                self.assertEqual(16, law(8, 8))

    def test_load_for_reproduces_the_engine_formula_at_denominator_16(self):
        # Engine-truth guard: with the shipped denominator, load_for must
        # equal the engine's own lifecycle_probe_grid stress on the same
        # grid (the exact statistic, reconstructed not approximated).
        import sys

        package_src = (
            Path(__file__).resolve().parents[2]
            / "packages"
            / "mecha_engine"
            / "src"
        )
        if str(package_src) not in sys.path:
            sys.path.insert(0, str(package_src))
        from mecha_engine.archive._metrics import lifecycle_probe_grid

        from corpus_builder import build_seed_grids

        for grid in build_seed_grids()[:5]:
            probe = lifecycle_probe_grid(grid)
            engine_load = probe["cells"][0]["stress"]
            self.assertAlmostEqual(
                engine_load, round(load_for(grid, 16), 6), places=9,
                msg=grid["grid_id"],
            )

    def test_report_is_deterministic_and_complete(self):
        again = build_stress_probe_scaling_report()
        self.assertEqual(
            json.dumps(self.report, sort_keys=True),
            json.dumps(again, sort_keys=True),
        )
        for key in [
            "artifact_id",
            "status",
            "date",
            "purpose",
            "source_artifacts",
            "metrics",
            "closed_states",
            "blocked_states",
            "decision",
            "next_research_step",
        ]:
            self.assertIn(key, self.report)
        self.assertEqual(
            "stress_probe_scaling_stage0", self.report["artifact_id"]
        )

    def test_baseline_and_all_candidate_laws_are_measured(self):
        metrics = self.report["metrics"]
        self.assertIn("baseline_8x8", metrics)
        baseline = metrics["baseline_8x8"]
        self.assertEqual(16, baseline["denominator"])
        self.assertEqual(50, baseline["population"])
        self.assertGreaterEqual(baseline["survival_bins_covered"], 1)
        candidates = metrics["candidates_16x16"]
        self.assertEqual(sorted(DENOMINATOR_LAWS), sorted(candidates))
        for name, row in candidates.items():
            with self.subTest(law=name):
                self.assertEqual(50, row["population"])
                self.assertIn("load", row)
                self.assertIn("survival_bins_covered", row)
                self.assertIn("saturated_fraction", row)
                self.assertIn("gates", row)

    def test_exactly_one_law_is_adopted_and_it_beats_the_status_quo(self):
        adopted = self.report["metrics"]["adopted"]
        self.assertIn(adopted["law"], DENOMINATOR_LAWS)
        row = self.report["metrics"]["candidates_16x16"][adopted["law"]]
        for gate, ok in row["gates"].items():
            self.assertTrue(ok, f"{adopted['law']} gate {gate}")
        status_quo = self.report["metrics"]["candidates_16x16"]["status_quo_16"]
        self.assertGreaterEqual(
            row["survival_bins_covered"],
            status_quo["survival_bins_covered"],
        )
        self.assertGreaterEqual(row["survival_bins_covered"], 2)

    def test_engine_probe_ships_the_adopted_law_at_both_scales(self):
        # Adoption pin: lifecycle_probe_grid must apply the adopted
        # denominator law — 16 at 8x8 (byte-identical history) and the
        # adopted value at 16x16.
        import sys

        package_src = (
            Path(__file__).resolve().parents[2]
            / "packages"
            / "mecha_engine"
            / "src"
        )
        if str(package_src) not in sys.path:
            sys.path.insert(0, str(package_src))
        from mecha_engine.archive._metrics import lifecycle_probe_grid

        from corpus_builder import build_seed_grids, build_seed_grids_16

        adopted = self.report["metrics"]["adopted"]
        for grid in build_seed_grids()[:5]:
            probe = lifecycle_probe_grid(grid)
            self.assertAlmostEqual(
                probe["cells"][0]["stress"],
                round(load_for(grid, adopted["denominator_8x8"]), 6),
                places=9,
                msg=grid["grid_id"],
            )
        for grid in build_seed_grids_16()[:8]:
            probe = lifecycle_probe_grid(grid)
            self.assertAlmostEqual(
                probe["cells"][0]["stress"],
                round(load_for(grid, adopted["denominator_16x16"]), 6),
                places=9,
                msg=grid["grid_id"],
            )

    def test_artifact_writer_round_trips(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            write_stress_probe_scaling_artifacts(output_dir, self.report)
            artifact = output_dir / "stress_probe_scaling_stage0.json"
            self.assertTrue(artifact.exists())
            loaded = json.loads(artifact.read_text(encoding="utf-8"))
            self.assertEqual(self.report["metrics"], loaded["metrics"])


if __name__ == "__main__":
    unittest.main()
