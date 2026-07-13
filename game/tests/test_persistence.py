"""F17 gates — the carried remainders close.

Replay persistence: the ledger's `record_replay` gains its consumer —
the artifact stays a FILE, the ledger stores the pointer and the
sha256 (DR 0022), and a loaded replay is hash-verified (tampering
refused verbatim). Campaign resume: the ACTIVE state (the spent
covenant, the earned facts, the era chain position) survives restart —
the next era's founders come from the LEDGER's own pool, era indices
and seeds continue exactly, and the ledger append stays idempotent
across the resume boundary.
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
    ERA_SEED_STRIDE,
    TINY_ERA_CONFIG,
    KeeperCampaign,
    load_campaign_inputs,
)
from mecha_game.covenant import apply_covenant_change  # noqa: E402

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
        "metric_value": 2,
        "threshold": 2,
    }


class ReplayPersistenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = load_campaign_inputs(
            SEED_DIR, SLIP_PATH, ADOPTED, repair_epochs=6, seed_limit=12
        )

    def test_reviews_survive_restart_hash_verified(self):
        campaign = KeeperCampaign(
            self.inputs, era_config=TINY_ERA_CONFIG, campaign_id="rp"
        )
        campaign.advance_era("calm")
        replay = campaign.record_review_replay()
        with tempfile.TemporaryDirectory() as tmp:
            keeper = Path(tmp)
            ledger = keeper / "campaign.sqlite3"
            campaign.save(ledger)
            path = campaign.save_review_replay(replay, keeper, ledger)
            self.assertTrue(path.is_file())
            loaded = campaign.load_review_replay(keeper, ledger, 0)
            self.assertEqual(replay, loaded)
            # Saving again records no duplicate pointer row.
            campaign.save_review_replay(replay, keeper, ledger)
            from mecha_engine.storage import (
                load_replay_rows,
                open_ledger,
            )

            conn = open_ledger(ledger)
            try:
                rows = load_replay_rows(conn, "rp")
            finally:
                conn.close()
            self.assertEqual(1, len(rows))
            # A tampered artifact is refused with the hash named.
            path.write_text(
                json.dumps({**replay, "frames": []}),
                encoding="utf-8",
            )
            with self.assertRaises(ValueError) as caught:
                campaign.load_review_replay(keeper, ledger, 0)
            self.assertIn("sha256", str(caught.exception))

    def test_a_missing_replay_row_returns_none(self):
        campaign = KeeperCampaign(
            self.inputs, era_config=TINY_ERA_CONFIG, campaign_id="none"
        )
        with tempfile.TemporaryDirectory() as tmp:
            keeper = Path(tmp)
            ledger = keeper / "campaign.sqlite3"
            campaign.save(ledger)
            self.assertIsNone(
                campaign.load_review_replay(keeper, ledger, 0)
            )


class CampaignResumeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = ReplayPersistenceTests.inputs = (
            load_campaign_inputs(
                SEED_DIR,
                SLIP_PATH,
                ADOPTED,
                repair_epochs=6,
                seed_limit=12,
            )
        )

    def test_the_spent_campaign_resumes_and_continues_exactly(self):
        with tempfile.TemporaryDirectory() as tmp:
            keeper = Path(tmp)
            ledger = keeper / "campaign.sqlite3"
            state = keeper / "campaign_state.json"

            first = KeeperCampaign(
                self.inputs,
                era_config=TINY_ERA_CONFIG,
                campaign_id="resume",
            )
            first.campaign["unlocks"].append(
                _fact("bloodline_depth", 1)
            )
            spend = apply_covenant_change(
                first, deliberation_max_ticks=2
            )
            self.assertTrue(spend["ok"])
            era0 = first.advance_era("calm")
            first.save(ledger)
            first.save_state(state)

            resumed = KeeperCampaign.load_state(
                self.inputs, state, ledger
            )
            # The SPENT covenant survives restart.
            self.assertEqual(
                first.campaign["slip_profile"],
                resumed.campaign["slip_profile"],
            )
            self.assertEqual(
                2,
                resumed.campaign["slip_profile"]["deliberation"][
                    "max_ticks"
                ],
            )
            self.assertEqual(first.unlocks, resumed.unlocks)
            # The next era continues the chain exactly: founders are
            # era 0's elites (from the LEDGER), index and seed follow.
            era1 = resumed.advance_era("calm")
            self.assertEqual(1, era1["era_index"])
            self.assertEqual(
                resumed.campaign["base_seed"] + ERA_SEED_STRIDE,
                era1["rng_seed"],
            )
            self.assertEqual(
                [e["grid"]["grid_id"] for e in era0["elites"]],
                era1["founders_submitted"],
            )
            # The ledger append stays idempotent across the boundary.
            resumed.save(ledger)
            from mecha_engine.storage import (
                campaign_history,
                open_ledger,
            )

            conn = open_ledger(ledger)
            try:
                history = campaign_history(conn, "resume")
            finally:
                conn.close()
            self.assertEqual(2, len(history["eras"]))
            self.assertEqual(
                era1["report"], history["eras"][1]["report"]
            )

    def test_a_resumed_continuation_matches_the_unbroken_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            keeper = Path(tmp)
            ledger = keeper / "campaign.sqlite3"
            state = keeper / "campaign_state.json"
            broken = KeeperCampaign(
                self.inputs,
                era_config=TINY_ERA_CONFIG,
                campaign_id="twin",
            )
            broken.advance_era("calm")
            broken.save(ledger)
            broken.save_state(state)
            resumed = KeeperCampaign.load_state(
                self.inputs, state, ledger
            )
            resumed_era = resumed.advance_era("stable_soup")

        unbroken = KeeperCampaign(
            self.inputs, era_config=TINY_ERA_CONFIG, campaign_id="twin"
        )
        unbroken.advance_era("calm")
        unbroken_era = unbroken.advance_era("stable_soup")
        self.assertEqual(
            json.dumps(unbroken_era, sort_keys=True),
            json.dumps(resumed_era, sort_keys=True),
        )


if __name__ == "__main__":
    unittest.main()
