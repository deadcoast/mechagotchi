"""F9 gates — the Contribute step: workshop releases enter the eras.

The bridge is a FILE handoff (the lab's release-directory rule:
deterministic file order, backups skipped, a missing inbox is simply
no releases) into the era seam F8 built; ADMISSION IS THE ENGINE'S
VERDICT (DR 0016/DR 0029 gates inside evolve): a matching release is
admitted and leads the pool, a mismatched one is rejected VERBATIM —
both shown, never smoothed. The committed workshop releases are 8×8,
so a 16×16 era rejects them on size coherence — the honest recorded
outcome, pinned here.
"""

import json
import sys
import tempfile
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
from mecha_game.contribute import (  # noqa: E402
    default_release_inboxes,
    founders_verdict,
    gather_releases,
    load_released_grids,
)

SEED_DIR = ROOT / "data" / "seed_grids_16x16"
SLIP_PATH = ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json"
ADOPTED = (
    ROOT / "data" / "readability_benchmark" / "adopted_readability_model.json"
)
WORKSHOP_RELEASED = ROOT / "data" / "workshop" / "released"


class LoadTests(unittest.TestCase):
    def test_missing_inbox_is_no_releases(self):
        self.assertEqual([], load_released_grids(None))
        self.assertEqual(
            [], load_released_grids(Path("does") / "not" / "exist")
        )

    def test_deterministic_file_order_and_backups_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            inbox = Path(tmp)
            (inbox / "b_second.json").write_text(
                json.dumps({"grid_id": "second"}), encoding="utf-8"
            )
            (inbox / "a_first.json").write_text(
                json.dumps({"grid_id": "first"}), encoding="utf-8"
            )
            (inbox / "a_first.bak.json").write_text(
                json.dumps({"grid_id": "backup"}), encoding="utf-8"
            )
            grids = load_released_grids(inbox)
        self.assertEqual(
            ["first", "second"], [grid["grid_id"] for grid in grids]
        )

    def test_the_committed_workshop_releases_load(self):
        grids = load_released_grids(WORKSHOP_RELEASED)
        self.assertEqual(2, len(grids))
        self.assertEqual(
            ["released_tall_wisp", "released_wide_sentinel"],
            sorted(grid["grid_id"] for grid in grids),
        )

    def test_default_inboxes_find_the_workshop_and_the_keeper(self):
        with tempfile.TemporaryDirectory() as tmp:
            keeper = Path(tmp)
            inboxes = default_release_inboxes(keeper, start=ROOT / "game")
            self.assertIn(WORKSHOP_RELEASED, inboxes)
            self.assertIn(keeper / "released", inboxes)
            (keeper / "released").mkdir()
            (keeper / "released" / "mine.json").write_text(
                json.dumps({"grid_id": "mine"}), encoding="utf-8"
            )
            grids = gather_releases(keeper, start=ROOT / "game")
            ids = [grid["grid_id"] for grid in grids]
            self.assertIn("mine", ids)
            self.assertIn("released_tall_wisp", ids)


class AdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = load_campaign_inputs(
            SEED_DIR, SLIP_PATH, ADOPTED, repair_epochs=6, seed_limit=12
        )

    def test_mismatched_releases_are_rejected_verbatim(self):
        campaign = KeeperCampaign(
            self.inputs, era_config=TINY_ERA_CONFIG, campaign_id="rej"
        )
        releases = load_released_grids(WORKSHOP_RELEASED)
        era = campaign.advance_era("calm", released_grids=releases)
        verdict = founders_verdict(era)
        self.assertIsNotNone(verdict)
        self.assertEqual([], verdict["admitted_ids"])
        rejected_ids = [r["grid_id"] for r in verdict["rejected"]]
        self.assertIn("released_tall_wisp", rejected_ids)
        self.assertTrue(
            any(
                "8x8" in error and "16x16" in error
                for rejection in verdict["rejected"]
                for error in rejection["errors"]
            )
        )
        # The era itself survives on the seed pool.
        self.assertTrue(era["elites"])

    def test_matching_releases_are_admitted_and_lead(self):
        campaign = KeeperCampaign(
            self.inputs, era_config=TINY_ERA_CONFIG, campaign_id="adm"
        )
        # An LCD-covenant-aligned body (the wisp — only some corpus
        # species satisfy this covenant; the moth, e.g., would be
        # honestly rejected on alignment).
        release = json.loads(
            json.dumps(self.inputs["seed_grids"][1])
        )
        release["grid_id"] = "released_workshop_16"
        era = campaign.advance_era("calm", released_grids=[release])
        verdict = founders_verdict(era)
        self.assertIn("released_workshop_16", verdict["admitted_ids"])
        self.assertEqual(
            "released_workshop_16", era["founders_submitted"][0]
        )

    def test_no_releases_means_no_verdict_block(self):
        campaign = KeeperCampaign(
            self.inputs, era_config=TINY_ERA_CONFIG, campaign_id="none"
        )
        era = campaign.advance_era("calm")
        self.assertIsNone(founders_verdict(era))


if __name__ == "__main__":
    unittest.main()
