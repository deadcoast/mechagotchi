"""F8 gates — species generation in the client (MVP 0.2's rung).

Founders are GENERATED in the product through the promoted constrained
surfaces: profile-weighted (the covenant filters the parent pool and
alignment holds), validator-gated (every candidate passes the engine's
own validation), deterministic under seeds, and LEGIBLE — every
hatched creature carries `explain_generation`'s verbatim trace, and
its origin line shows only trace fields. Released grids LEAD the next
era's founder pool (the lab's founders-lead rule, DR 0016's admission
gates doing the judging inside evolve).
"""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for _src in (ROOT / "game" / "src", ROOT / "packages" / "mecha_engine" / "src"):
    if str(_src) not in sys.path:
        sys.path.insert(0, str(_src))

from mecha_game.campaign import (  # noqa: E402
    TINY_ERA_CONFIG,
    KeeperCampaign,
    load_campaign_inputs,
)
from mecha_game.hatchery import hatch_founders, origin_summary  # noqa: E402

SEED_DIR = ROOT / "data" / "seed_grids_16x16"
SLIP_PATH = ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json"
ADOPTED = (
    ROOT / "data" / "readability_benchmark" / "adopted_readability_model.json"
)


class HatcheryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = load_campaign_inputs(
            SEED_DIR, SLIP_PATH, ADOPTED, repair_epochs=6, seed_limit=12
        )

    def test_hatched_founders_are_engine_truth(self):
        from mecha_engine.lifecycle import initial_state
        from mecha_engine.slip import is_grid_aligned

        hatched = hatch_founders(
            self.inputs["seed_grids"],
            self.inputs["slip_profile"],
            count=2,
            rng_seed=7,
        )
        self.assertEqual(2, len(hatched))
        ids = {entry["grid"]["grid_id"] for entry in hatched}
        self.assertEqual(2, len(ids))
        for entry in hatched:
            # Adoption through the engine's own gate; covenant holds.
            state = initial_state(
                entry["grid"], self.inputs["slip_profile"]
            )
            self.assertTrue(state["alive"])
            self.assertTrue(
                is_grid_aligned(
                    entry["grid"], self.inputs["slip_profile"]
                )
            )

    def test_the_origin_is_legible_and_verbatim(self):
        hatched = hatch_founders(
            self.inputs["seed_grids"],
            self.inputs["slip_profile"],
            count=1,
            rng_seed=7,
        )[0]
        explanation = hatched["explanation"]
        self.assertEqual(
            hatched["grid"]["grid_id"], explanation["grid_id"]
        )
        self.assertIn("generator_strategy", explanation)
        line = origin_summary(explanation)
        self.assertIn(explanation["generator_strategy"], line)
        self.assertIn(str(explanation["parent_grid_id"]), line)

    def test_hatching_is_deterministic_under_seeds(self):
        first = hatch_founders(
            self.inputs["seed_grids"],
            self.inputs["slip_profile"],
            count=2,
            rng_seed=11,
        )
        second = hatch_founders(
            self.inputs["seed_grids"],
            self.inputs["slip_profile"],
            count=2,
            rng_seed=11,
        )
        self.assertEqual(
            json.dumps(first, sort_keys=True),
            json.dumps(second, sort_keys=True),
        )

    def test_released_grids_lead_the_next_eras_founder_pool(self):
        campaign = KeeperCampaign(
            self.inputs, era_config=TINY_ERA_CONFIG, campaign_id="rel"
        )
        campaign.advance_era("calm")
        hatched = hatch_founders(
            self.inputs["seed_grids"],
            self.inputs["slip_profile"],
            count=1,
            rng_seed=13,
        )[0]["grid"]
        era = campaign.advance_era("calm", released_grids=[hatched])
        self.assertEqual(
            hatched["grid_id"], era["founders_submitted"][0]
        )
        # The elites still follow (the founders-lead rule).
        self.assertGreater(len(era["founders_submitted"]), 1)


if __name__ == "__main__":
    unittest.main()
