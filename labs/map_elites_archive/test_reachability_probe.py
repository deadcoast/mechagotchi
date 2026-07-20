"""Cycle 20 J1 gates — descriptor-bin reachability under the engine's

own move set. The probe may only use promoted surfaces (the trained
generation model + ``generate_candidate`` + package validation) and
the geometry's own descriptors: a bin counts as REACHED only with a
validator-passing witness whose descriptor recomputes into that exact
bin, and an unreached bin is honestly "unreached within budget" —
a measured bound, never an impossibility proof.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
REPO_ROOT = LAB_DIR.parents[1]
PACKAGE_SRC = REPO_ROOT / "packages" / "mecha_engine" / "src"
for _path in (LAB_DIR, str(PACKAGE_SRC)):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

from reachability_probe import (  # noqa: E402
    build_reachability_report,
    write_reachability_artifacts,
)
from niche_scale_archive import (  # noqa: E402
    scale_axis_values,
    scale_descriptor_for_values,
    _load_default_slip,
)

from mecha_engine.genome import validate_grid  # noqa: E402


class ReachabilityProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Tiny deterministic scale: the honesty rules and arithmetic
        # are the pins; the full-scale numbers live in the committed
        # artifact (H-01: never pin per-run scale observations).
        cls.report = build_reachability_report(
            derivation_count=64,
            pool_count=64,
            per_bin_budget=6,
            probe_limit=4,
            rng_seed=23,
        )

    def test_the_bin_arithmetic_is_conserved(self):
        metrics = self.report["metrics"]
        self.assertEqual(512, metrics["total_niches"])
        self.assertEqual(
            metrics["total_niches"],
            metrics["reached_by_generators"]
            + metrics["probed"]["newly_reached"]
            + metrics["probed"]["unreached_within_budget"]
            + metrics["unprobed_bins"],
        )

    def test_witnesses_pass_the_validator_and_land_in_their_bins(self):
        slip = _load_default_slip()
        edges = self.report["metrics"]["edges"]
        for record in self.report["metrics"]["per_bin"]:
            if not record["reached"]:
                continue
            witness = record["witness"]
            with self.subTest(bin=record["bin"]):
                self.assertTrue(validate_grid(witness).ok)
                descriptor = scale_descriptor_for_values(
                    scale_axis_values(witness, slip_profile=slip),
                    edges,
                )
                self.assertEqual(tuple(record["bin"]), descriptor)

    def test_unreached_bins_record_the_budget_and_best_distance(self):
        for record in self.report["metrics"]["per_bin"]:
            if record["reached"]:
                continue
            with self.subTest(bin=record["bin"]):
                self.assertEqual(6, record["attempts"])
                self.assertGreaterEqual(record["best_distance"], 1)

    def test_the_probe_limit_is_a_named_cap_never_silent(self):
        self.assertLessEqual(
            len(self.report["metrics"]["per_bin"]), 4
        )
        self.assertGreater(self.report["metrics"]["unprobed_bins"], 0)
        blocked = " ".join(self.report["blocked_states"])
        self.assertIn("probe_limit", blocked)

    def test_the_report_is_deterministic(self):
        twin = build_reachability_report(
            derivation_count=64,
            pool_count=64,
            per_bin_budget=6,
            probe_limit=4,
            rng_seed=23,
        )
        self.assertEqual(
            json.dumps(self.report, sort_keys=True),
            json.dumps(twin, sort_keys=True),
        )

    def test_artifacts_are_written(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_reachability_artifacts(Path(tmp), self.report)
            payload = json.loads(
                (
                    Path(tmp) / "reachability_probe_stage0.json"
                ).read_text(encoding="utf-8")
            )
        self.assertEqual(
            "reachability_probe_stage0", payload["artifact_id"]
        )
        self.assertIn("decision", payload)


if __name__ == "__main__":
    unittest.main()
