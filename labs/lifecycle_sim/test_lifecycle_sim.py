import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GRID_GENOME = ROOT / "labs" / "grid_genome"
for path in [ROOT, GRID_GENOME]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from corpus_builder import build_seed_grids
from lifecycle_sim import (
    advance_tick,
    initial_lifecycle_state,
    run_lifecycle_lab,
    run_lifecycle_simulation,
    write_lifecycle_artifacts,
)


def load_lcd_slip() -> dict:
    return json.loads(
        (ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json").read_text(
            encoding="utf-8"
        )
    )


class LifecycleSimulatorTests(unittest.TestCase):
    def test_initial_state_uses_grid_and_slip_identity(self):
        grid = build_seed_grids()[0]
        slip = load_lcd_slip()

        state = initial_lifecycle_state(grid, slip)

        self.assertEqual(grid["grid_id"], state["grid_id"])
        self.assertEqual(slip["profile_id"], state["slip_profile_id"])
        self.assertTrue(state["alive"])
        self.assertEqual(0, state["age_ticks"])
        for key in ["hunger", "energy", "stress", "bond", "grid_stability"]:
            self.assertGreaterEqual(state[key], 0)
            self.assertLessEqual(state[key], 1)

    def test_feed_tick_recovers_dangerous_hunger_and_records_action(self):
        state = initial_lifecycle_state(build_seed_grids()[0], load_lcd_slip())
        state["hunger"] = 0.86
        state["energy"] = 0.44
        state["stress"] = 0.3

        next_state = advance_tick(state, "feed")

        self.assertEqual(1, next_state["age_ticks"])
        self.assertLess(next_state["hunger"], state["hunger"])
        self.assertEqual(1, next_state["action_counts"]["feed"])
        self.assertEqual("feed", next_state["history"][-1]["action"])
        self.assertIn("hunger", next_state["history"][-1]["recoveries"])

    def test_switchboard_policy_beats_idle_policy_on_need_balance(self):
        grid = build_seed_grids()[0]
        slip = load_lcd_slip()

        switchboard = run_lifecycle_simulation(
            grid, slip, ticks=72, policy="switchboard", rng_seed=20260512
        )
        idle = run_lifecycle_simulation(
            grid, slip, ticks=72, policy="idle", rng_seed=20260512
        )

        self.assertTrue(switchboard["alive"])
        self.assertGreaterEqual(
            switchboard["survival_ticks"], idle["survival_ticks"]
        )
        self.assertGreater(switchboard["need_balance"], idle["need_balance"])
        self.assertGreater(switchboard["recovery_events"], idle["recovery_events"])

    def test_lifecycle_lab_report_contains_required_metrics(self):
        report = run_lifecycle_lab(ticks=48, rng_seed=20260512)

        self.assertEqual("lifecycle_sim_stage0", report["lab_id"])
        self.assertEqual(48, report["ticks_requested"])
        for policy in ["switchboard", "idle", "random"]:
            self.assertIn(policy, report["policies"])
            metrics = report["policies"][policy]
            self.assertIn("survival_ticks", metrics)
            self.assertIn("need_balance", metrics)
            self.assertIn("recovery_events", metrics)
            self.assertIn("action_counts", metrics)

    def test_write_lifecycle_artifacts_creates_json_report(self):
        report = run_lifecycle_lab(ticks=12, rng_seed=7)
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "lifecycle_stage0.json"

            write_lifecycle_artifacts(output_path, report)

            self.assertTrue(output_path.exists())
            written = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(report["lab_id"], written["lab_id"])


if __name__ == "__main__":
    unittest.main()
