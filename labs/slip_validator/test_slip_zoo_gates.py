import json
import tempfile
import unittest
from pathlib import Path

from slip_zoo_gates import (
    ARCHETYPES,
    build_slip_zoo_gates_report,
    write_slip_zoo_artifacts,
)

ROOT = Path(__file__).resolve().parents[2]


class SlipZooGatesTests(unittest.TestCase):
    """T3.6: the og gates for the completed SLIP ladder."""

    @classmethod
    def setUpClass(cls):
        cls.report = build_slip_zoo_gates_report()

    def test_twenty_archetypes_spanning_the_og_axes(self):
        self.assertEqual(20, len(ARCHETYPES))
        ids = [archetype["archetype_id"] for archetype in ARCHETYPES]
        self.assertEqual(len(ids), len(set(ids)))

    def test_expressiveness_gate_measures_and_names_gaps(self):
        gate = self.report["gates"]["expressiveness"]
        self.assertEqual(20, gate["archetype_count"])
        self.assertEqual(
            gate["representable_count"],
            sum(
                1
                for entry in self.report["archetype_results"]
                if entry["representable"]
            ),
        )
        # Every non-representable archetype must name its missing
        # capability AND map to an already-queued decision (no
        # unplanned gaps) — that is the gate's real question.
        for entry in self.report["archetype_results"]:
            if not entry["representable"]:
                self.assertTrue(entry["missing_capability"])
                self.assertTrue(entry["queued_in"])
        self.assertIsInstance(gate["unplanned_gap_count"], int)
        self.assertEqual(
            gate["unplanned_gap_count"] == 0, gate["no_unplanned_gaps"]
        )

    def test_fuzz_pack_false_pass_rate_meets_the_og_bar(self):
        gate = self.report["gates"]["fuzz"]
        self.assertGreaterEqual(gate["case_count"], 150)
        self.assertLessEqual(gate["false_pass_rate"], 0.01)
        self.assertEqual(
            gate["false_pass_rate"],
            round(gate["false_pass_count"] / gate["case_count"], 6),
        )
        # Both validators agree on every fuzz case (outcome-level).
        self.assertEqual(0, gate["validator_disagreements"])

    def test_zoo_grows_to_one_hundred_valid_unique_profiles(self):
        gate = self.report["gates"]["zoo"]
        self.assertEqual(100, gate["profile_count"])
        self.assertEqual(100, gate["valid_count"])
        self.assertEqual(100, gate["unique_profile_ids"])

    def test_artifacts_write_the_zoo_and_report(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir)
            write_slip_zoo_artifacts(output, self.report)
            zoo_files = sorted((output / "zoo").glob("*.json"))
            self.assertEqual(100, len(zoo_files))
            sample = json.loads(zoo_files[0].read_text(encoding="utf-8"))
            self.assertIn("profile_id", sample)
            artifact = output / "slip_zoo_gates_stage0.json"
            self.assertTrue(artifact.exists())

    def test_deterministic(self):
        self.assertEqual(self.report, build_slip_zoo_gates_report())


if __name__ == "__main__":
    unittest.main()
