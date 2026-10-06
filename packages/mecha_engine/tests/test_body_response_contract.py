"""Workload-v1 through only the promoted package surface (stdlib subprocess)."""
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PROBE = r'''import json, sys
from pathlib import Path
from mecha_engine.lifecycle import initial_state, advance_tick, run_episode
root = Path(sys.argv[1])
grid = json.loads((root / "data/seed_grids/mg_seed_001.json").read_text(encoding="utf-8"))
base = initial_state(grid)
active = initial_state(grid, body_response="workload-v1")
newborn = initial_state(grid, body_response="workload-v1")
projection = active["body_workload"]
step = advance_tick(active, "play")
report = run_episode(grid, actions=["play", "feed", "sleep"], ticks=3, body_response="workload-v1")
checks = {
    "legacy_unchanged": base == initial_state(grid, body_response="legacy") and "body_workload" not in base,
    "body_bound": projection["occupied_mass"] == len(grid["cells"]) and .07 <= projection["play_energy_cost"] <= .34,
    "applied_cost": step["energy"] == round(max(0, active["energy"] - .028 - projection["play_energy_cost"]), 6),
    "receipt_identity": report["body_response"] == "workload-v1" and report["body_workload"] == projection,
    "history_truth": step["history"][-1]["action_energy_effect"] == -projection["play_energy_cost"],
    "newborn_cold": newborn == active and newborn["age_ticks"] == 0 and newborn["history"] == [],
    "package_only": not any(name == "body_response" or name == "lifecycle_sim" for name in sys.modules),
}
print(json.dumps(checks))
'''


class BodyResponsePackageContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        environment = dict(os.environ, PYTHONPATH=str(ROOT / "packages/mecha_engine/src"))
        result = subprocess.run([sys.executable, "-B", "-c", PROBE, str(ROOT)],
                                env=environment, text=True, capture_output=True, timeout=30)
        if result.returncode:
            raise AssertionError(result.stderr)
        cls.checks = json.loads(result.stdout)

    def test_legacy_default_and_explicit_off_are_identical(self):
        self.assertTrue(self.checks["legacy_unchanged"])

    def test_actual_body_and_registered_cost_are_used(self):
        self.assertTrue(self.checks["body_bound"])
        self.assertTrue(self.checks["applied_cost"])

    def test_episode_and_history_report_real_action_effect(self):
        self.assertTrue(self.checks["receipt_identity"])
        self.assertTrue(self.checks["history_truth"])

    def test_newborn_has_no_lived_or_learned_state(self):
        self.assertTrue(self.checks["newborn_cold"])

    def test_active_runtime_does_not_load_research_modules(self):
        self.assertTrue(self.checks["package_only"])


if __name__ == "__main__": unittest.main()
