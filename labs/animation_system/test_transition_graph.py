import json
import sys
import tempfile
import unittest
from pathlib import Path

from clip_model import clip_names
from transition_graph import (
    TRANSITIONS,
    boundary_delta,
    build_transition_report,
    transition_is_valid,
    write_transition_artifacts,
)

LAB_DIR = Path(__file__).resolve().parent
REPO_ROOT = LAB_DIR.parents[1]
GRID_GENOME = REPO_ROOT / "labs" / "grid_genome"
if str(GRID_GENOME) not in sys.path:
    sys.path.insert(0, str(GRID_GENOME))

from corpus_builder import build_seed_grids_16  # noqa: E402


class GraphShapeTests(unittest.TestCase):
    def test_idle_is_the_hub_and_every_clip_loops(self):
        clips = set(clip_names())
        edges = set(TRANSITIONS)
        # Every clip is reachable from idle and returns to idle.
        for clip in clips - {"idle"}:
            self.assertIn(("idle", clip), edges)
            self.assertIn((clip, "idle"), edges)
        # Every clip may loop on itself (the repeat boundary is judged
        # by the same validity metric as any transition).
        for clip in clips:
            self.assertIn((clip, clip), edges)
        # No edge names an unknown clip.
        for source, target in edges:
            self.assertIn(source, clips)
            self.assertIn(target, clips)

    def test_transition_validity_is_deterministic(self):
        beetle = next(
            grid
            for grid in build_seed_grids_16()
            if grid["grid_id"].endswith("beetle")
        )
        first = transition_is_valid(beetle, "idle", "blink")
        second = transition_is_valid(beetle, "idle", "blink")
        self.assertEqual(first, second)
        delta = boundary_delta(beetle, "idle", "blink")
        self.assertGreaterEqual(delta, 0.0)
        self.assertLessEqual(delta, 1.0)


class TransitionReportTests(unittest.TestCase):
    report: dict

    @classmethod
    def setUpClass(cls):
        cls.report = build_transition_report()

    def test_report_is_deterministic_and_complete(self):
        again = build_transition_report()
        self.assertEqual(
            json.dumps(self.report, sort_keys=True),
            json.dumps(again, sort_keys=True),
        )
        self.assertEqual(
            "transition_graph_stage0", self.report["artifact_id"]
        )
        metrics = self.report["metrics"]
        self.assertEqual(50, metrics["corpus_size"])
        self.assertEqual(len(TRANSITIONS), metrics["edge_count"])
        self.assertEqual(
            50 * len(TRANSITIONS), metrics["transitions_measured"]
        )

    def test_the_dossier_bar_holds(self):
        # The documented gate: transition validity >= 80%, under the
        # pre-registered metric (boundary no jerkier than the jerkiest
        # intra-clip step of either clip involved).
        metrics = self.report["metrics"]
        self.assertGreaterEqual(metrics["transition_validity_rate"], 0.8)
        self.assertEqual("complete", self.report["status"])

    def test_per_edge_rates_are_reported_not_hidden(self):
        per_edge = self.report["metrics"]["per_edge_validity"]
        self.assertEqual(len(TRANSITIONS), len(per_edge))
        for edge_key, rate in per_edge.items():
            with self.subTest(edge=edge_key):
                self.assertGreaterEqual(rate, 0.0)
                self.assertLessEqual(rate, 1.0)

    def test_artifact_round_trips(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            write_transition_artifacts(output_dir, self.report)
            loaded = json.loads(
                (output_dir / "transition_graph_stage0.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(self.report["metrics"], loaded["metrics"])


if __name__ == "__main__":
    unittest.main()
