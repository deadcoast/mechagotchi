import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAB_DIR = Path(__file__).resolve().parent
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from mecha_engine_runtime_loop import (  # noqa: E402
    run_mecha_engine_evolution_loop,
)


def _v2_profile(**ladder) -> dict:
    profile = json.loads(
        (ROOT / "data/slips/valid/slip_lcd_seed.json").read_text(
            encoding="utf-8"
        )
    )
    profile["slip_version"] = "0.2.0"
    profile["profile_id"] = "slip_v2_retirement_test"
    profile.update(ladder)
    return profile


class ProjectionRetirementTests(unittest.TestCase):
    """DR 0013 follow-up: the loop passes full v0.2 profiles natively."""

    KW = dict(
        generations=1,
        population=3,
        damage_cycles=1,
        ticks=16,
        repair_epochs=20,
        rng_seed=20260512,
    )

    def test_ladder_fields_reach_package_episodes_natively(self):
        # rules_only switches must change episode behavior INSIDE the
        # package lifecycle — only possible without the projection.
        default_run = run_mecha_engine_evolution_loop(**self.KW)
        switched_run = run_mecha_engine_evolution_loop(
            slip_profile=_v2_profile(
                learning_switches={
                    "recent_interaction_ewma": False,
                    "hidden_mood_estimator": False,
                    "action_preference_bandit": False,
                    "mutation_risk_scorer": False,
                }
            ),
            **self.KW,
        )
        default_scores = [
            c["score"]["fitness"]
            for c in default_run["generations"][0]["creatures"]
            if c["score"]
        ]
        switched_scores = [
            c["score"]["fitness"]
            for c in switched_run["generations"][0]["creatures"]
            if c["score"]
        ]
        self.assertNotEqual(default_scores, switched_scores)

    def test_default_v1_flow_is_untouched(self):
        report = run_mecha_engine_evolution_loop(**self.KW)
        self.assertEqual(
            "mecha_engine_evolution_loop_stage0", report["lab_id"]
        )
        self.assertNotIn("parent_selection", report)


if __name__ == "__main__":
    unittest.main()
