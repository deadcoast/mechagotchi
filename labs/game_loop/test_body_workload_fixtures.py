"""Operational checks of the predeclared synthetic repair fixture, not holdouts."""
import sys
import unittest
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages/mecha_engine/src"))
from body_workload_fixtures import causal_fixture
from mecha_engine.genome import validate_grid
from mecha_engine.lifecycle import initial_state, run_episode
from mecha_engine.repair import repair_wound_sites
from mecha_engine.runtime import live_cycle
from mecha_engine.runtime._damage import apply_damage_event
from mecha_engine.slip import is_grid_aligned, validate_slip


class BodyWorkloadFixtureTests(unittest.TestCase):
    def test_fixture_payload_is_deterministic_and_independent(self):
        one, two = causal_fixture(), causal_fixture()
        self.assertEqual(one, two)
        one["grid"]["cells"].clear()
        self.assertEqual(two, causal_fixture())

    def test_fixture_has_registered_mass_semantics_and_valid_covenant(self):
        data = causal_fixture()
        self.assertTrue(validate_grid(data["grid"]).ok)
        self.assertTrue(validate_slip(data["covenant"]).ok)
        self.assertTrue(is_grid_aligned(data["grid"], data["covenant"]).ok)
        state = initial_state(data["grid"], data["covenant"], body_response="workload-v1")
        self.assertEqual(state["body_workload"]["occupied_mass"], 6)
        self.assertEqual(state["body_workload"]["functional_capacity"], 4.)
        self.assertEqual(data["damage_event"], {"removed_cells": [[4, 3]]})

    def test_declared_repair_biases_are_only_fixed_biases(self):
        data = causal_fixture()
        for key, token in (("changed", "B"), ("null", "D")):
            model = data["repair_models"][key]
            nonzero = [(i, j, value) for i, row in enumerate(model["weights"]) for j, value in enumerate(row) if value]
            self.assertEqual(nonzero, [(model["class_tokens"].index(token), model["feature_count"]-1, 8.)])
            self.assertEqual(model["source_mode"], "engineered_constant_bias_causal_fixture")
            self.assertFalse(model["target_template_used"])

    def test_production_repair_restores_positions_and_changes_only_registered_capacity(self):
        data = causal_fixture()
        saved = deepcopy(data)
        before = initial_state(data["grid"], data["covenant"], body_response="workload-v1")["body_workload"]
        wound = apply_damage_event(data["grid"], data["damage_event"])
        positions = {(cell["x"], cell["y"]) for cell in data["grid"]["cells"]}
        for key, capacity in (("changed", 5.), ("null", 4.)):
            repaired = repair_wound_sites(wound, data["repair_models"][key], slip_profile=data["covenant"])
            projection = initial_state(repaired, data["covenant"], body_response="workload-v1")["body_workload"]
            self.assertEqual({(cell["x"], cell["y"]) for cell in repaired["cells"]}, positions)
            self.assertEqual(projection["occupied_mass"], 6)
            self.assertEqual(projection["functional_capacity"], capacity)
            self.assertEqual(projection["play_energy_cost"], .084 if capacity == 5 else .105)
            if key == "null": self.assertEqual(projection, before)
        self.assertEqual(data, saved)

    def test_real_runtime_consumes_repaired_projection(self):
        data = causal_fixture()
        for key in ("changed", "null"):
            result = live_cycle(data["grid"], data["covenant"], data["repair_models"][key],
                                damage_events=[data["damage_event"]], ticks=data["repair_ticks"], rng_seed=data["rng_seed"],
                                record_frames=True, body_response="workload-v1")
            cycle = result["cycles"][0]
            self.assertTrue(cycle["valid"] and cycle["aligned"])
            repaired = cycle["frames"]["repaired_grid"]
            expected = run_episode(repaired, data["covenant"], policy="switchboard", ticks=data["repair_ticks"],
                                   rng_seed=data["rng_seed"], body_response="workload-v1")
            self.assertEqual(cycle["episode"]["body_workload"], expected["body_workload"])
            self.assertEqual(cycle["frames"]["episode_history"], expected["history"])


if __name__ == "__main__": unittest.main()
