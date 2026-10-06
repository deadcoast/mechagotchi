"""Registered workload-v1 arithmetic and lifecycle contracts; no outcome holdouts."""
import json
import math
import sys
import unittest
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages/mecha_engine/src"))
from body_response import project_body_workload, validate_body_response, workload_for_state
from lifecycle_sim import initial_lifecycle_state, run_lifecycle_simulation, advance_tick as lab_tick
from mecha_engine.lifecycle import initial_state, advance_tick, run_episode


def grid_fixture(size=8):
    # Enough connected mandatory core for the incumbent size-dependent floor.
    count = max(4, 18 * size * size // 256)
    core = [[i % size, i // size] for i in range(count)]
    sensor = [count % size, count // size]
    cells = [{"x": x, "y": y, "visual": "#5dbb63", "role": "body",
              "material": "hard", "mutation_weight": .1,
              "animation_anchor": i == 0, "organ": "core", "stress": 0,
              "damage": 0, "locked": False} for i, (x, y) in enumerate(core)]
    cells.append({**cells[-1], "x": sensor[0], "y": sensor[1], "role": "eye",
                  "material": "glass", "organ": "sensors", "animation_anchor": False})
    return {"grid_id": "body_workload_fixture", "schema_version": "0.1.0",
            "grid_size": [size, size], "cells": cells,
            "organs": {"core": {"role": "body_core", "cells": core, "required": True},
                       "sensors": {"role": "sensor", "cells": [sensor], "required": True}},
            "palette": {"palette_id": "lcd_green", "colors": ["#07140d", "#5dbb63", "#d8ffd6"]},
            "mutation": {"cell_mutation_rate": .1, "organ_shift_rate": .1,
                         "palette_shift_rate": .1, "symmetry_break_rate": .1},
            "lineage": {"generation": 0, "ancestor_ids": [], "mutation_events": []}}


def physiology(state):
    return {key: state[key] for key in ("hunger", "energy", "stress", "bond", "grid_stability", "alive", "death_cause", "age_ticks")}


class BodyResponseTests(unittest.TestCase):
    def test_exact_normalization_and_species_priors(self):
        grid = grid_fixture()
        state = initial_state(grid, body_response="workload-v1")
        self.assertEqual(state["body_response"], "workload-v1")
        self.assertEqual(state["body_workload"], {"occupied_mass": 5, "functional_capacity": 4.0,
                         "capacity_floor": max(1., 5*.07/.34), "play_energy_cost": .0875})
        old = initial_state(grid)
        self.assertEqual({key: state[key] for key in ("neediness", "sleepiness", "curiosity", "action_rewards")},
                         {key: old[key] for key in ("neediness", "sleepiness", "curiosity", "action_rewards")})
        self.assertEqual(physiology(state), physiology(old))

    def test_only_play_energy_effect_changes(self):
        grid = grid_fixture()
        for action in ("feed", "sleep", "play", "idle", "mutate"):
            old = advance_tick(initial_state(grid), action)
            current = advance_tick(initial_state(grid, body_response="workload-v1"), action)
            expected = physiology(old)
            if action == "play":
                expected["energy"] = round(old["energy"] - .0175, 6)
            self.assertEqual(physiology(current), expected)
            entry = current["history"][-1]
            self.assertEqual(entry["play_energy_cost"], .0875)
            self.assertEqual(entry["action_energy_effect"], {"feed": .01, "sleep": .34, "play": -.0875, "idle": -.012, "mutate": -.045}[action])

    def test_real_energy_death_boundary_and_no_rescue(self):
        grid = grid_fixture()
        for cell in grid["cells"]:
            if cell["organ"] == "core": cell["damage"] = .5
        old = initial_state(grid)
        current = initial_state(grid, body_response="workload-v1")
        old["energy"] = current["energy"] = .15
        self.assertTrue(advance_tick(old, "play")["alive"])
        dead = advance_tick(current, "play")
        self.assertFalse(dead["alive"])
        self.assertEqual(dead["death_cause"], "energy_collapse")
        self.assertEqual(advance_tick(dead, "sleep"), dead)

    def test_semantic_names_order_and_duplicate_references_are_null(self):
        grid = grid_fixture()
        expected = project_body_workload(grid)
        changed = deepcopy(grid)
        changed["organs"]["motor_support"] = changed["organs"].pop("core")
        changed["organs"]["motor_support"]["cells"] *= 2
        changed["cells"].reverse()
        for cell in changed["cells"]:
            if cell["organ"] == "core": cell["organ"] = "motor_support"
        self.assertEqual(project_body_workload(changed), expected)
        self.assertEqual(initial_state(changed, body_response="workload-v1")["body_workload"], expected)

    def test_semantic_union_counts_overlaps_once_and_locomotion_counts(self):
        grid = grid_fixture()
        point = [grid["cells"][-1]["x"], grid["cells"][-1]["y"]]
        grid["cells"][-1]["organ"] = None
        grid["organs"]["drive"] = {"role": "locomotion", "cells": [point, point], "required": False}
        self.assertEqual(initial_state(grid, body_response="workload-v1")["body_workload"]["play_energy_cost"], .07)
        grid["organs"]["overlap"] = {"role": "body_core", "cells": [point], "required": False}
        self.assertEqual(project_body_workload(grid)["functional_capacity"], 5.)

    def test_empty_or_void_coordinates_do_not_create_mass_or_capacity(self):
        grid = grid_fixture()
        expected = project_body_workload(grid)
        for role, material in (("empty", "hard"), ("body", "void"), ("empty", "void")):
            cell = {**grid["cells"][0], "x": 7, "y": 7, "role": role, "material": material, "animation_anchor": False, "organ": None}
            changed = deepcopy(grid)
            changed["cells"].append(cell)
            changed["organs"]["ignored"] = {"role": "locomotion", "cells": [[7, 7]], "required": False}
            self.assertEqual(project_body_workload(changed), expected)

    def test_damage_only_integrity_and_cost_cap(self):
        grid = grid_fixture()
        clean = project_body_workload(grid)
        for cell in grid["cells"]: cell["stress"] = .9
        self.assertEqual(project_body_workload(grid), clean)
        for damage in (0., .25, .5, 1.):
            for cell in grid["cells"]: cell["damage"] = damage
            projection = project_body_workload(grid)
            self.assertEqual(projection["functional_capacity"], 4 * (1 - damage))
            self.assertGreaterEqual(projection["play_energy_cost"], .07)
            self.assertLessEqual(projection["play_energy_cost"], .34)
        self.assertEqual(projection["play_energy_cost"], .34)

    def test_full_precision_capacity_and_supported_sizes(self):
        grid = grid_fixture()
        grid["cells"][0]["damage"] = .1234567890123
        projection = project_body_workload(grid)
        self.assertEqual(projection["functional_capacity"], math.fsum([1-.1234567890123, 1., 1., 1.]))
        for size in (8, 16, 64):
            state = initial_state(grid_fixture(size), body_response="workload-v1")
            self.assertEqual(state["body_workload"], project_body_workload(grid_fixture(size)))

    def test_unknown_versions_and_bad_integrity_refuse(self):
        grid = grid_fixture()
        for version in (None, "", "workload-v2", True, {}):
            with self.assertRaises(ValueError): initial_state(grid, body_response=version)
        for damage in (float("nan"), float("inf"), 10**400, -.1, 1.1):
            changed = deepcopy(grid)
            changed["cells"][0]["damage"] = damage
            with self.assertRaises(ValueError): project_body_workload(changed)
        for cell in grid["cells"]: cell["role"] = "empty"
        with self.assertRaises(ValueError): project_body_workload(grid)

    def test_reserved_state_fields_fail_closed(self):
        original = initial_state(grid_fixture(), body_response="workload-v1")
        alterations = [lambda s: s.update(body_response="workload-v2"),
                       lambda s: s.pop("body_response"), lambda s: s.pop("body_workload"),
                       lambda s: s["body_workload"].update(play_energy_cost=.01),
                       lambda s: s["body_workload"].update(functional_capacity=float("nan")),
                       lambda s: s["body_workload"].update(functional_capacity=10**400),
                       lambda s: s["body_workload"].update(capacity_floor=0),
                       lambda s: s["body_workload"].update(occupied_mass=True),
                       lambda s: s["body_workload"].update(unregistered=1)]
        for change in alterations:
            state = deepcopy(original)
            change(state)
            with self.assertRaises(ValueError): advance_tick(state, "idle")

    def test_no_input_mutation_or_shared_effect_table_change(self):
        grid = grid_fixture()
        original = deepcopy(grid)
        state = initial_state(grid, body_response="workload-v1")
        old_state = deepcopy(state)
        advance_tick(state, "play")
        self.assertEqual(state, old_state)
        self.assertEqual(grid, original)
        self.assertEqual(advance_tick(initial_state(grid), "play")["energy"], .582)

    def test_legacy_omits_all_new_keys_and_explicit_off_is_identical(self):
        grid = grid_fixture()
        state = initial_state(grid)
        self.assertNotIn("body_response", state)
        self.assertNotIn("body_workload", state)
        self.assertEqual(state, initial_state(grid, body_response="legacy"))
        for policy in ("switchboard", "idle", "random"):
            report = run_episode(grid, policy=policy)
            self.assertEqual(report, run_episode(grid, policy=policy, body_response="legacy"))
            self.assertNotIn("body_response", report)
            self.assertNotIn("play_energy_cost", report["history"][0])

    def test_lab_package_initial_transition_and_episode_parity(self):
        grid = grid_fixture()
        for version in ("legacy", "workload-v1"):
            self.assertEqual(initial_lifecycle_state(grid, body_response=version), initial_state(grid, body_response=version))
            for action in ("feed", "play", "sleep", "idle", "mutate"):
                self.assertEqual(lab_tick(initial_lifecycle_state(grid, body_response=version), action),
                                 advance_tick(initial_state(grid, body_response=version), action))
            for policy in ("switchboard", "idle", "random"):
                self.assertEqual(run_lifecycle_simulation(grid, policy=policy, body_response=version),
                                 run_episode(grid, policy=policy, body_response=version))

    def test_private_projection_mirror_is_byte_exact(self):
        self.assertEqual((ROOT / "labs/lifecycle_sim/body_response.py").read_bytes(),
                         (ROOT / "packages/mecha_engine/src/mecha_engine/lifecycle/_body_response.py").read_bytes())

    def test_cleanliness_composes_without_changing_the_other_axes(self):
        grid = grid_fixture()
        old = run_episode(grid, actions=["clean", "feed", "sleep"] * 3, ticks=9, mechanics=("cleanliness",))
        current = run_episode(grid, actions=["clean", "feed", "sleep"] * 3, ticks=9, mechanics=("cleanliness",), body_response="workload-v1")
        self.assertEqual(old["final_state"], current["final_state"])
        self.assertEqual(old["final_cleanliness"], current["final_cleanliness"])
        self.assertEqual(current["history"][0]["action_energy_effect"], 0.)


if __name__ == "__main__": unittest.main()
