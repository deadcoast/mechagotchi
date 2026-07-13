"""F13 gates — the repertoire browser: species memory made visible.

The era archive's elites (the engine's MAP-Elites records, verbatim)
become a browsable product surface: page through niches in the
archive's own deterministic order, every caption built from record
fields (the descriptor's NAMED axes, fitness and its components, the
lineage generation), every body a real render packet. The browser
never re-derives a statistic.
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
from mecha_game.repertoire import RepertoireBrowser  # noqa: E402

SEED_DIR = ROOT / "data" / "seed_grids_16x16"
SLIP_PATH = ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json"
ADOPTED = (
    ROOT / "data" / "readability_benchmark" / "adopted_readability_model.json"
)


class RepertoireBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = load_campaign_inputs(
            SEED_DIR, SLIP_PATH, ADOPTED, repair_epochs=6, seed_limit=12
        )
        cls.campaign = KeeperCampaign(
            cls.inputs, era_config=TINY_ERA_CONFIG, campaign_id="rep"
        )
        cls.campaign.advance_era("calm")
        cls.campaign.advance_era("stable_soup")
        cls.browser = RepertoireBrowser(cls.campaign)

    def test_the_browser_opens_on_the_latest_era(self):
        browser = RepertoireBrowser(self.campaign)
        self.assertEqual(1, browser.era_index)
        self.assertEqual(
            len(self.campaign.eras[1]["elites"]), browser.count
        )
        self.assertEqual(0, browser.index)

    def test_paging_is_niche_order_and_clamps(self):
        browser = RepertoireBrowser(self.campaign)
        keys = [
            elite["niche_key"]
            for elite in self.campaign.eras[1]["elites"]
        ]
        self.assertEqual(keys[0], browser.current()["niche_key"])
        browser.back()
        self.assertEqual(0, browser.index)
        for _ in range(browser.count + 5):
            browser.step()
        self.assertEqual(browser.count - 1, browser.index)
        self.assertEqual(keys[-1], browser.current()["niche_key"])

    def test_era_switching_walks_the_campaign(self):
        browser = RepertoireBrowser(self.campaign)
        browser.previous_era()
        self.assertEqual(0, browser.era_index)
        self.assertEqual(
            len(self.campaign.eras[0]["elites"]), browser.count
        )
        self.assertEqual(0, browser.index)  # reset on switch
        browser.previous_era()
        self.assertEqual(0, browser.era_index)  # clamps
        browser.next_era()
        self.assertEqual(1, browser.era_index)

    def test_captions_are_record_fields_verbatim(self):
        browser = RepertoireBrowser(self.campaign)
        elite = browser.current()
        caption = browser.caption()
        self.assertIn(elite["grid_id"], caption)
        self.assertIn(f"{elite['fitness']:.3f}", caption)
        self.assertIn(f"1/{browser.count}", caption)
        axes = browser.axes_line()
        descriptor = elite["descriptor"]
        for name, value in zip(
            descriptor["names"], descriptor["values"]
        ):
            self.assertIn(f"{name} {value}", axes)

    def test_every_elite_renders_a_real_packet(self):
        browser = RepertoireBrowser(self.campaign)
        for _ in range(browser.count):
            packet = browser.packet()
            self.assertEqual(
                browser.current()["grid_id"], packet["grid_id"]
            )
            self.assertIn("cells", packet)
            self.assertIn("scanline", packet["effects"])
            browser.step()

    def test_an_empty_campaign_refuses_honestly(self):
        empty = KeeperCampaign(
            self.inputs, era_config=TINY_ERA_CONFIG, campaign_id="empty"
        )
        with self.assertRaises(ValueError):
            RepertoireBrowser(empty)


if __name__ == "__main__":
    unittest.main()
