import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PROTOCOLS_DIR = ROOT / "workshop" / "protocols"
if str(PROTOCOLS_DIR) not in sys.path:
    sys.path.insert(0, str(PROTOCOLS_DIR))

from first_session_protocol import (  # noqa: E402
    FIRST_SESSION_BOUND_SECONDS,
    run_first_session_protocol,
    write_first_session_artifacts,
)


class FirstSessionProtocolTests(unittest.TestCase):
    """H5: the documented <=45-minute first-session goal, measured
    honestly — the scripted pass proves the whole path exists and is
    labeled a PROXY; the human pass is prepared, not blocking (the
    calibration pattern)."""

    @classmethod
    def setUpClass(cls):
        cls.report = run_first_session_protocol()

    def test_the_whole_first_session_path_exists(self):
        self.assertEqual("complete", self.report["status"])
        self.assertTrue(self.report["steps"], "the protocol must have steps")
        for step in self.report["steps"]:
            self.assertTrue(step["ok"], f"{step['name']}: {step.get('evidence')}")

    def test_the_journey_covers_the_documented_surfaces(self):
        names = [step["name"] for step in self.report["steps"]]
        for required in [
            "open_the_workshop",
            "first_marks_and_first_refusal",
            "author_the_creature",
            "author_the_species_slip",
            "save_the_creature",
            "see_it_move",
            "release_into_the_ecosystem",
            "share_it",
        ]:
            self.assertIn(required, names)

    def test_the_refusal_step_records_the_validators_words(self):
        step = next(
            s
            for s in self.report["steps"]
            if s["name"] == "first_marks_and_first_refusal"
        )
        self.assertTrue(step["evidence"]["errors"])

    def test_the_scripted_time_is_a_labeled_proxy_under_the_bound(self):
        metrics = self.report["metrics"]
        self.assertTrue(metrics["scripted_proxy"])
        self.assertEqual(2700, FIRST_SESSION_BOUND_SECONDS)
        self.assertLess(
            metrics["total_elapsed_seconds"], FIRST_SESSION_BOUND_SECONDS
        )
        self.assertGreater(metrics["interaction_count"], 0)

    def test_the_human_pass_is_prepared_not_blocking(self):
        self.assertTrue(self.report["human_pass"]["prepared"])
        self.assertFalse(self.report["human_pass"]["blocking"])
        self.assertTrue(self.report["human_pass"]["steps"])
        self.assertTrue(
            any(
                "manual" in state or "human" in state
                for state in self.report["blocked_states"]
            )
        )

    def test_write_artifacts_emits_valid_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            write_first_session_artifacts(output_dir, self.report)
            artifact = output_dir / "first_session_stage0.json"
            self.assertTrue(artifact.exists())
            persisted = json.loads(artifact.read_text(encoding="utf-8"))
            self.assertEqual(self.report["metrics"], persisted["metrics"])


if __name__ == "__main__":
    unittest.main()
