"""X7 pre-RED behavioral contracts for observed care selection."""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from observed_care_selection import (
    care_context_sha256, care_grid_sha256, care_structure_sha256,
    observed_care_episode, select_care_successor, validate_care_context,
)
from mecha_engine.generation import generate_candidate, train_generation_model
from mecha_engine.genome import validate_grid

ROOT = Path(__file__).resolve().parents[2]


def context(events=12):
    tape = [{"tick": i + 1, "session_tick": i + 1, "actor": "keeper",
             "action": "feed" if i % 3 == 0 else "idle", "begging": False,
             "alive": True, "death_cause": None} for i in range(events)]
    counts = {}
    for row in tape: counts[row["action"]] = counts.get(row["action"], 0) + 1
    return {"format": "keeper_care_context_v1", "keeper_id": "keeper-test",
            "life_id": "keeper-test:life-1", "grid_id": "test-parent", "grid_sha256": "a" * 64,
            "care_summary": {"history": "complete", "from_age_ticks": 0,
                             "ticks_observed": events, "keeper_actions": counts,
                             "companion_actions": {}, "beg_requests": 0},
            "events": tape, "events_omitted": 0, "last_age_ticks": events,
            "last_session_tick": events, "outcome": "alive"}


class ObservedCareTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grid = json.loads((ROOT / "data/seed_grids/mg_seed_001.json").read_text())
        cls.slip = json.loads((ROOT / "data/slips/valid/slip_lcd_seed.json").read_text())
        cls.model = train_generation_model([cls.grid])

    def test_off_and_absent_and_empty_are_exact_incumbent(self):
        old = generate_candidate(self.grid, self.model, self.slip, rng_seed=31415)
        for policy, ctx in (("off", context()), ("observed_care_selection_v1", None),
                            ("observed_care_selection_v1", context(0))):
            grid, receipt = select_care_successor(self.grid, self.model, self.slip,
                context=ctx, rng_seed=31415, policy=policy)
            self.assertEqual(grid, old)
            self.assertIsNone(receipt)

    def test_selection_is_valid_pristine_and_inputs_immutable(self):
        ctx = context()
        before = deepcopy((self.grid, self.slip, ctx))
        grid, receipt = select_care_successor(self.grid, self.model, self.slip,
            context=ctx, rng_seed=31415, policy="observed_care_selection_v1")
        self.assertTrue(validate_grid(grid).ok)
        self.assertEqual(before, (self.grid, self.slip, ctx))
        self.assertTrue(all(c["stress"] == 0 and c["damage"] == 0 for c in grid["cells"]))
        self.assertEqual(receipt["pool_size"], 8)
        self.assertEqual(receipt["selected_grid_sha256"], care_grid_sha256(grid))
        self.assertEqual(receipt["context_sha256"], care_context_sha256(ctx))
        row = receipt["candidates"][receipt["selected_index"]]
        self.assertEqual(row["grid_sha256"], care_grid_sha256(grid))
        self.assertGreaterEqual(row["need_balance"], receipt["candidates"][0]["need_balance"])

    def test_same_tape_labels_and_cumulative_metadata_do_not_select(self):
        ctx = context()
        renamed = deepcopy(ctx)
        renamed.update(keeper_id="different", life_id="different:life-12", grid_id="other")
        for key in ("last_age_ticks", "last_session_tick"): renamed[key] += 10
        for event in renamed["events"]:
            event["tick"] += 10
            event["session_tick"] += 10
        renamed["events_omitted"] = 10
        renamed["care_summary"]["ticks_observed"] += 10
        renamed["care_summary"]["keeper_actions"]["play"] = 10
        a, ra = select_care_successor(self.grid, self.model, self.slip,
            context=ctx, rng_seed=31415, policy="observed_care_selection_v1")
        b, rb = select_care_successor(self.grid, self.model, self.slip,
            context=renamed, rng_seed=31415, policy="observed_care_selection_v1")
        self.assertEqual(a, b)
        self.assertEqual(ra["candidates"], rb["candidates"])

    def test_companion_cannot_feed_and_cold_state_cannot_inherit_q(self):
        ctx = context(30)
        for row in ctx["events"]:
            row.update(actor="companion", action="idle")
        ctx["care_summary"].update(keeper_actions={}, companion_actions={"idle": 30})
        result = observed_care_episode(self.grid, self.slip, ctx, evaluator="pristine")
        self.assertEqual(result["action_counts"]["feed"], 0)
        self.assertGreater(result["beg_requests"], 0)
        self.assertNotIn("qtable_policy", result["final_state"].get("thread_states", {}))
        self.assertLess(result["survival_ticks"], result["ticks_requested"])
        self.assertEqual(result["need_balance"], round(sum(r["balance"] for r in result["history"]) / 30, 6))

    def test_malformed_or_noncontiguous_tapes_refuse(self):
        for mutation in (lambda c: c["events"][1].update(tick=7),
                         lambda c: c.update(events_omitted=-1),
                         lambda c: c["events"][0].update(action="teleport"),
                         lambda c: c["events"][0].update(alive=0),
                         lambda c: c.update(outcome="revived")):
            ctx = context()
            mutation(ctx)
            with self.assertRaises(ValueError): validate_care_context(ctx)

    def test_structural_signature_ignores_labels_and_mutation_metadata(self):
        other = deepcopy(self.grid)
        other.update(grid_id="other", metadata={"context": "other"})
        other["lineage"] = {"generation": 99}
        self.assertEqual(care_structure_sha256(other), care_structure_sha256(self.grid))
        other["cells"][0]["role"] = "different"
        self.assertNotEqual(care_structure_sha256(other), care_structure_sha256(self.grid))

    def test_pristine_matches_real_product_beyond_history_trim(self):
        from mecha_game.session import CompanionSession
        from mecha_game.care_history import capture_care_context
        pet = CompanionSession(self.grid, self.slip, model=self.model)
        original_history = []
        for _ in range(60):
            if not pet.alive: break
            action = "feed" if pet.state["hunger"] > .5 else "sleep" if pet.state["energy"] < .6 else None
            pet.advance(action)
            original_history.append(deepcopy(pet.state["history"][-1]))
        self.assertGreater(pet.state["age_ticks"], 32)
        episode = observed_care_episode(self.grid, self.slip, capture_care_context(pet), evaluator="pristine")
        self.assertEqual(episode["history"], original_history)
        actual_state = deepcopy(episode["final_state"])
        expected_state = deepcopy(pet.state)
        for state in (actual_state, expected_state):
            for key in ("qtable_policy", "qtable_consumer"):
                if state["learning_switches"].get(key) is False:
                    state["learning_switches"].pop(key)
        self.assertEqual(actual_state, expected_state)

    def test_empty_life_suffix_is_not_an_identity(self):
        ctx = context()
        ctx["life_id"] = ctx["keeper_id"] + ":life-"
        with self.assertRaises(ValueError): validate_care_context(ctx)

    def test_lab_package_private_mirror_is_byte_exact(self):
        self.assertEqual((ROOT / "labs/runtime_integration/observed_care_selection.py").read_bytes(),
                         (ROOT / "packages/mecha_engine/src/mecha_engine/runtime/_observed_care.py").read_bytes())

if __name__ == "__main__": unittest.main()
