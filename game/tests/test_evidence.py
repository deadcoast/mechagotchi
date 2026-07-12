"""F1 gates — the evidence harness measures, never asserts by fiat."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for _src in (
    ROOT / "game",
    ROOT / "game" / "src",
    ROOT / "packages" / "mecha_engine" / "src",
):
    if str(_src) not in sys.path:
        sys.path.insert(0, str(_src))

from evidence import (  # noqa: E402
    build_companion_loop_report,
    build_front_end_skeleton_report,
    build_render_bridge_report,
    run_composition_session,
    write_companion_loop_artifacts,
    write_front_end_skeleton_artifacts,
    write_render_bridge_artifacts,
)


class EvidenceTests(unittest.TestCase):
    def test_report_is_complete_and_deterministic(self):
        report = build_front_end_skeleton_report(ticks=8, cell_px=1)
        self.assertEqual("complete", report["status"])
        self.assertTrue(report["metrics"]["twin_run_byte_equal"])
        self.assertTrue(
            report["metrics"]["idle_clip_cycles_documented_frames"]
        )
        self.assertEqual([], report["metrics"]["declared_effects_skipped"])
        self.assertTrue(report["blocked_states"])

    def test_ghosting_makes_frames_distinct_across_the_cycle(self):
        session = run_composition_session(ticks=8, cell_px=1)
        # Four clip frames, but persistence means a frame's pixels
        # depend on history — more distinct frames than clip frames.
        self.assertGreater(session["distinct_frames"], 4)

    def test_artifacts_write_valid_json(self):
        report = build_front_end_skeleton_report(ticks=4, cell_px=1)
        with tempfile.TemporaryDirectory() as tmp:
            path = write_front_end_skeleton_artifacts(tmp, report)
            self.assertEqual(
                report, json.loads(path.read_text(encoding="utf-8"))
            )

    def test_companion_loop_report_measures_the_stakes(self):
        report = build_companion_loop_report(budget=400)
        self.assertEqual("complete", report["status"])
        metrics = report["metrics"]
        self.assertTrue(metrics["twin_run_equal"])
        self.assertTrue(metrics["neglect_dies_within_budget"])
        self.assertTrue(metrics["tending_saves"])
        self.assertTrue(
            metrics["succession"]["child_parent_link_holds"]
        )
        self.assertEqual(2, metrics["lineage_document_records"])
        with tempfile.TemporaryDirectory() as tmp:
            path = write_companion_loop_artifacts(tmp, report)
            self.assertEqual(
                report, json.loads(path.read_text(encoding="utf-8"))
            )

    def test_render_bridge_report_proves_the_full_contract(self):
        report = build_render_bridge_report(cell_px=1)
        self.assertEqual("complete", report["status"])
        metrics = report["metrics"]
        self.assertTrue(metrics["every_cut_is_a_graph_edge"])
        self.assertTrue(metrics["full_effects_contract_rasterized"])
        self.assertTrue(metrics["nothing_declared_skipped"])
        self.assertTrue(metrics["twin_run_byte_equal"])
        self.assertEqual(0, metrics["session"]["illegal_cuts"])
        with tempfile.TemporaryDirectory() as tmp:
            path = write_render_bridge_artifacts(tmp, report)
            self.assertEqual(
                report, json.loads(path.read_text(encoding="utf-8"))
            )


if __name__ == "__main__":
    unittest.main()
