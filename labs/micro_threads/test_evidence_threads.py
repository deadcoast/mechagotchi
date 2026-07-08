import json
import tempfile
import unittest
from pathlib import Path

from evidence_threads import (
    build_evidence_bundle,
    build_evidence_thread_report,
    write_evidence_thread_artifacts,
)


class EvidenceBundleTests(unittest.TestCase):
    def test_bundle_matches_the_canonical_surfaces_for_a_seed(self):
        # The wiring pin: bundle values ARE the canonical functions'
        # outputs (checked exhaustively in the report; spot-checked here).
        import sys

        lab_dir = Path(__file__).resolve().parent
        repo_root = lab_dir.parents[1]
        for path in [
            repo_root / "labs" / "grid_genome",
            repo_root / "packages" / "mecha_engine" / "src",
        ]:
            if str(path) not in sys.path:
                sys.path.insert(0, str(path))
        from corpus_builder import build_seed_grids

        from mecha_engine.archive._metrics import mutation_stability
        from mecha_engine.slip import is_grid_aligned

        grid = build_seed_grids()[0]
        slip_profile = json.loads(
            (repo_root / "data" / "slips" / "valid" / "slip_lcd_seed.json").read_text(
                encoding="utf-8"
            )
        )
        bundle = build_evidence_bundle(grid, slip_profile)
        self.assertEqual(
            mutation_stability(grid, slip_profile),
            bundle["mutation_stability"],
        )
        self.assertEqual(
            is_grid_aligned(grid, slip_profile).ok, bundle["slip_aligned"]
        )
        self.assertIn("readability_score", bundle)


class ReportTests(unittest.TestCase):
    report: dict

    @classmethod
    def setUpClass(cls):
        cls.report = build_evidence_thread_report()

    def test_report_shape_and_serializability(self):
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
            "evidence_threads_stage0", self.report["artifact_id"]
        )
        self.assertEqual("complete", self.report["status"])
        self.assertEqual(self.report, json.loads(json.dumps(self.report)))
        self.assertTrue(self.report["blocked_states"])

    def test_every_thread_pins_byte_equal_to_its_canonical_surface(self):
        # 50 seed creatures, four threads: the thread's streamed output
        # must equal the canonical function's number for every creature.
        pins = self.report["metrics"]["wiring_pins"]
        self.assertEqual(pins["creatures"], 50)
        for key in [
            "mutation_stability_equal",
            "readability_equal",
            "slip_compat_equal",
        ]:
            with self.subTest(pin=key):
                self.assertEqual(pins[key], pins["creatures"])
        self.assertEqual(
            pins["lineage_equal"], pins["lineage_records_found"]
        )
        self.assertGreater(pins["lineage_records_found"], 0)

    def test_distributions_are_recorded(self):
        distributions = self.report["metrics"]["distributions"]
        self.assertIn("readability_mean", distributions)
        self.assertIn("mutation_stability_mean", distributions)
        self.assertIn("slip_aligned_count", distributions)

    def test_write_artifacts_round_trips(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            write_evidence_thread_artifacts(output_dir, self.report)
            written = output_dir / "evidence_threads_stage0.json"
            self.assertTrue(written.exists())
            self.assertEqual(
                self.report,
                json.loads(written.read_text(encoding="utf-8")),
            )


if __name__ == "__main__":
    unittest.main()
