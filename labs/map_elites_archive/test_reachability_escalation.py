"""K3 (cycle 21): the escalation on the last unreached bins.

Pins the escalation protocol's contract: targets default to the
committed probe artifact's unreached bins verbatim, witnesses are
validator-passing and bin-verified, bounded bins carry the
blocking-axis instrument (required octile interval + conditional
attainment), the temperature ladder is the registered one, twin runs
are byte-equal, and artifacts round-trip.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from reachability_probe import (  # noqa: E402
    DEFAULT_ESCALATION_BUDGET,
    ESCALATION_ARTIFACT_ID,
    TEMPERATURE_LADDER,
    _committed_unreached_bins,
    build_escalation_report,
    write_escalation_artifacts,
)

# Tiny protocol for tests: a small pool, one target the generators
# plausibly reach (a mid-space bin) and one octile corner at a
# hopeless budget so both verdict paths are exercised.
TINY = dict(
    derivation_count=60,
    pool_count=120,
    per_bin_budget=12,
    elite_size=4,
    rng_seed=20260709,
)


class EscalationProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = build_escalation_report(
            targets=[(3, 3, 3), (7, 0, 0)], **TINY
        )

    def test_report_identity_and_registered_protocol(self):
        self.assertEqual(ESCALATION_ARTIFACT_ID, self.report["artifact_id"])
        parameters = self.report["parameters"]
        self.assertEqual(
            [None, 0.5, 1.0, 1.5, 2.0], parameters["temperature_ladder"]
        )
        self.assertEqual(list(TEMPERATURE_LADDER), parameters["temperature_ladder"])
        self.assertEqual(2000, DEFAULT_ESCALATION_BUDGET)
        self.assertEqual(
            [[3, 3, 3], [7, 0, 0]], parameters["targets"]
        )

    def test_every_bin_carries_a_first_class_verdict(self):
        for record in self.report["metrics"]["per_bin"]:
            with self.subTest(bin=record["bin"]):
                self.assertIn(
                    record["verdict"], {"reached", "bounded_sharper"}
                )
                self.assertEqual(
                    record["verdict"] == "reached", record["reached"]
                )
                if record["reached"]:
                    self.assertTrue(record["witness_bin_verified"])
                    self.assertIn("witness", record)
                else:
                    blocking = record["blocking"]
                    self.assertIn("axes", blocking)
                    for name in blocking["axes"]:
                        per_axis = blocking["per_axis"][name]
                        self.assertIn("required_octile", per_axis)
                        self.assertEqual(2, len(per_axis["required_interval"]))
                        self.assertIn("conditional_candidates", per_axis)

    def test_counts_are_consistent(self):
        metrics = self.report["metrics"]
        self.assertEqual(2, metrics["targets_probed"])
        self.assertEqual(
            metrics["targets_probed"],
            metrics["newly_reached"] + metrics["bounded_sharper"],
        )

    def test_twin_runs_are_identical(self):
        twin = build_escalation_report(
            targets=[(3, 3, 3), (7, 0, 0)], **TINY
        )
        self.assertEqual(self.report, twin)

    def test_artifacts_round_trip(self):
        with tempfile.TemporaryDirectory() as temp:
            path = write_escalation_artifacts(Path(temp), self.report)
            self.assertEqual(
                self.report,
                json.loads(path.read_text(encoding="utf-8")),
            )


class CommittedTargetTests(unittest.TestCase):
    def test_default_targets_are_the_committed_unreached_bins_verbatim(self):
        targets = _committed_unreached_bins()
        self.assertEqual(9, len(targets))
        for target in targets:
            with self.subTest(bin=target):
                self.assertEqual(3, len(target))
        committed = json.loads(
            (
                LAB_DIR.parents[1]
                / "data"
                / "archives"
                / "reachability_probe_stage0.json"
            ).read_text(encoding="utf-8")
        )
        expected = [
            tuple(record["bin"])
            for record in committed["metrics"]["per_bin"]
            if not record["reached"]
        ]
        self.assertEqual(expected, targets)


if __name__ == "__main__":
    unittest.main()
