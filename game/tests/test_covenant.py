"""F7 gates — the progression is FELT: unlock facts SPEND into the
covenant, inside the earned budget, under the engine's own authority.

The session lab's `covenant_budget`/`apply_covenant_change` semantics
mirrored (DR 0021's Covenant step): the budget is a PURE function of
the base covenant, the base engine parameters, and the earned facts;
over-budget requests are rejected with named violations and NOTHING
is applied; every accepted covenant passes `mecha_engine.slip`'s
validator (refusals verbatim); a successor bloodline inherits the
Keeper's unlock state (roguelite: only the unlocks carry over).
"""

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
from mecha_game.covenant import (  # noqa: E402
    PALETTE_UNLOCK_ORDER,
    apply_covenant_change,
    covenant_budget,
    spend_deliberation_to_budget,
    spend_next_palette,
    spend_population_to_cap,
)

SEED_DIR = ROOT / "data" / "seed_grids_16x16"
SLIP_PATH = ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json"
ADOPTED = (
    ROOT / "data" / "readability_benchmark" / "adopted_readability_model.json"
)


def _fact(axis: str, tier: int) -> dict:
    return {
        "axis": axis,
        "tier": tier,
        "earned_era_index": 0,
        "metric_path": "test",
        "metric_value": 1,
        "threshold": 1,
    }


class BudgetTests(unittest.TestCase):
    def setUp(self):
        self.base_profile = {"grid": {"allowed_palettes": ["lcd_green"]}}
        self.base_parameters = {"population": 16, "generations": 6}

    def test_no_facts_no_budget(self):
        budget = covenant_budget(
            self.base_profile, self.base_parameters, []
        )
        self.assertEqual(["lcd_green"], budget["allowed_palettes"])
        self.assertEqual(0, budget["deliberation_max_ticks"])
        self.assertEqual(16, budget["population_cap"])
        self.assertEqual(6, budget["generation_cap"])
        self.assertEqual(0.7, budget["legibility_blend"])
        self.assertIn("organ_role_budget", budget["deferred"])

    def test_niche_tiers_unlock_palettes_in_order(self):
        budget = covenant_budget(
            self.base_profile,
            self.base_parameters,
            [_fact("niche_mastery", 2)],
        )
        self.assertEqual(
            ["lcd_green", *PALETTE_UNLOCK_ORDER[:2]],
            budget["allowed_palettes"],
        )

    def test_bloodline_tiers_deepen_thinking_on_the_real_floor(self):
        # Tier 1 = the authority's 2-tick floor; +1 per further tier.
        for tier, expected in [(1, 2), (2, 3), (3, 4)]:
            budget = covenant_budget(
                self.base_profile,
                self.base_parameters,
                [_fact("bloodline_depth", tier)],
            )
            self.assertEqual(
                expected, budget["deliberation_max_ticks"], tier
            )

    def test_qd_tiers_double_the_caps(self):
        budget = covenant_budget(
            self.base_profile,
            self.base_parameters,
            [_fact("quality_diversity", 2)],
        )
        self.assertEqual(64, budget["population_cap"])
        self.assertEqual(24, budget["generation_cap"])


class SpendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = load_campaign_inputs(
            SEED_DIR, SLIP_PATH, ADOPTED, repair_epochs=6, seed_limit=12
        )

    def _campaign(self, facts: list[dict]) -> KeeperCampaign:
        campaign = KeeperCampaign(
            self.inputs, era_config=TINY_ERA_CONFIG, campaign_id="spend"
        )
        campaign.campaign["unlocks"].extend(facts)
        return campaign

    def test_over_budget_is_refused_and_nothing_applied(self):
        campaign = self._campaign([])
        before = dict(campaign.campaign["slip_profile"])
        result = apply_covenant_change(
            campaign, deliberation_max_ticks=2
        )
        self.assertFalse(result["ok"])
        self.assertTrue(result["violations"])
        self.assertEqual(before, campaign.campaign["slip_profile"])

    def test_earned_deliberation_spends_and_validates(self):
        campaign = self._campaign([_fact("bloodline_depth", 1)])
        result = apply_covenant_change(
            campaign, deliberation_max_ticks=2
        )
        self.assertTrue(result["ok"], result.get("violations"))
        profile = campaign.campaign["slip_profile"]
        self.assertEqual(2, profile["deliberation"]["max_ticks"])
        self.assertEqual("0.2.0", profile["slip_version"])

    def test_unearned_palette_is_a_named_violation(self):
        campaign = self._campaign([])
        result = apply_covenant_change(
            campaign,
            allowed_palettes=["lcd_green", PALETTE_UNLOCK_ORDER[0]],
        )
        self.assertFalse(result["ok"])
        self.assertIn(
            f"palette {PALETTE_UNLOCK_ORDER[0]} is not in the earned "
            "budget",
            result["violations"],
        )

    def test_earned_palette_spends(self):
        campaign = self._campaign([_fact("niche_mastery", 1)])
        base = campaign.campaign["slip_profile"]["grid"][
            "allowed_palettes"
        ]
        result = apply_covenant_change(
            campaign,
            allowed_palettes=[*base, PALETTE_UNLOCK_ORDER[0]],
        )
        self.assertTrue(result["ok"], result.get("violations"))
        self.assertIn(
            PALETTE_UNLOCK_ORDER[0],
            campaign.campaign["slip_profile"]["grid"][
                "allowed_palettes"
            ],
        )

    def test_population_spends_within_the_earned_cap(self):
        campaign = self._campaign([_fact("quality_diversity", 1)])
        result = apply_covenant_change(campaign, population=12)
        self.assertTrue(result["ok"])
        self.assertEqual(12, campaign.era_config["population"])
        refused = apply_covenant_change(campaign, population=13)
        self.assertFalse(refused["ok"])
        self.assertEqual(12, campaign.era_config["population"])

    def test_the_spent_covenant_governs_the_next_era(self):
        campaign = self._campaign([_fact("bloodline_depth", 1)])
        result = apply_covenant_change(
            campaign, deliberation_max_ticks=2
        )
        self.assertTrue(result["ok"])
        era = campaign.advance_era("calm")
        self.assertEqual(
            2,
            era["report"]["slip_profile"]["deliberation"]["max_ticks"]
            if "slip_profile" in era["report"]
            else campaign.campaign["slip_profile"]["deliberation"][
                "max_ticks"
            ],
        )
        self.assertTrue(era["elites"])

    def test_one_key_spends_apply_or_refuse_honestly(self):
        campaign = self._campaign(
            [
                _fact("niche_mastery", 1),
                _fact("bloodline_depth", 1),
                _fact("quality_diversity", 1),
            ]
        )
        palette = spend_next_palette(campaign)
        self.assertTrue(palette["ok"], palette.get("violations"))
        again = spend_next_palette(campaign)
        self.assertFalse(again["ok"])
        thinking = spend_deliberation_to_budget(campaign)
        self.assertTrue(thinking["ok"], thinking.get("violations"))
        deeper = spend_deliberation_to_budget(campaign)
        self.assertFalse(deeper["ok"])
        population = spend_population_to_cap(campaign)
        self.assertTrue(population["ok"])
        self.assertEqual(12, campaign.era_config["population"])

    def test_a_successor_inherits_the_unlock_state(self):
        campaign = self._campaign(
            [_fact("niche_mastery", 1), _fact("bloodline_depth", 1)]
        )
        campaign.campaign["status"] = "extinct"
        successor = campaign.successor()
        self.assertEqual([], successor.unlocks)  # own facts start empty
        budget = successor.budget()
        self.assertIn(
            PALETTE_UNLOCK_ORDER[0], budget["allowed_palettes"]
        )
        self.assertEqual(2, budget["deliberation_max_ticks"])


if __name__ == "__main__":
    unittest.main()
