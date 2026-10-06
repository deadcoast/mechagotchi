"""F4 gates — the Keeper's campaign is engine truth end to end.

One era = one promoted `runtime.evolve` run; founders chain from the
previous era's elites (DR 0021's spine); unlock facts are earned from
era-report metrics against the lab-calibrated thresholds (falsifiable:
met must unlock, unmet must not, earned never re-earned); an extinct
bloodline's successor carries only the unlocks; the campaign persists
through the storage module's ledger. The tiny era configuration here
is for suite speed — the evidence artifact runs the A4 session scale.
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
    SUCCESSOR_SEED_OFFSET,
    KeeperCampaign,
    evaluate_unlocks,
    legibility_blend_for,
    load_campaign_inputs,
)

SEED_DIR = ROOT / "data" / "seed_grids_16x16"
SLIP_PATH = ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json"
ADOPTED = (
    ROOT / "data" / "readability_benchmark" / "adopted_readability_model.json"
)
TINY_ERA = {
    "generations": 2,
    "population": 6,
    "damage_cycles": 1,
    "ticks": 8,
    "dropout_rate": 0.2,
}


def _fixture_era(**overrides) -> dict:
    era = {
        "era_index": 0,
        "report": {
            "summary": {
                "archive": {"filled_niches": 16, "qd_score": 8.0},
                "max_lineage_generation": 1,
            }
        },
        "derived": {
            "max_dropout_multiplier_survived": None,
            "elite_mean_learned_readability": 0.2,
        },
    }
    for path, value in overrides.items():
        node = era
        keys = path.split(".")
        for key in keys[:-1]:
            node = node[key]
        node[keys[-1]] = value
    return era


class UnlockTests(unittest.TestCase):
    def test_met_threshold_must_unlock(self):
        facts = evaluate_unlocks(_fixture_era(), [])
        self.assertEqual(
            [("niche_mastery", 1)],
            [(fact["axis"], fact["tier"]) for fact in facts],
        )
        self.assertEqual(16, facts[0]["metric_value"])
        self.assertEqual(16, facts[0]["threshold"])

    def test_unmet_threshold_must_not_unlock(self):
        era = _fixture_era(**{"report.summary.archive.filled_niches": 15})
        self.assertEqual([], evaluate_unlocks(era, []))

    def test_earned_facts_are_never_re_earned(self):
        first = evaluate_unlocks(_fixture_era(), [])
        second = evaluate_unlocks(_fixture_era(), first)
        self.assertEqual([], second)

    def test_none_metrics_are_skipped(self):
        # A calm era has no storm record — no storm fact, no crash.
        facts = evaluate_unlocks(_fixture_era(), [])
        self.assertNotIn(
            "storm_record", [fact["axis"] for fact in facts]
        )

    def test_legibility_blend_steps_with_earned_tiers(self):
        self.assertEqual(0.7, legibility_blend_for([]))
        facts = [{"axis": "legibility", "tier": 2}]
        self.assertEqual(0.8, legibility_blend_for(facts))


class CampaignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = load_campaign_inputs(
            SEED_DIR,
            SLIP_PATH,
            ADOPTED,
            repair_epochs=6,
            seed_limit=12,
        )
        cls.campaign = KeeperCampaign(
            cls.inputs, era_config=TINY_ERA, campaign_id="test_campaign"
        )
        cls.first_era = cls.campaign.advance_era("calm")
        cls.second_era = cls.campaign.advance_era("stable_soup")

    def test_an_era_is_one_engine_run(self):
        era = self.first_era
        self.assertEqual(0, era["era_index"])
        self.assertEqual(
            self.campaign.campaign["base_seed"], era["rng_seed"]
        )
        self.assertIn("summary", era["report"])
        self.assertTrue(era["elites"])
        self.assertEqual("calm", era["weather"]["forecast"])
        self.assertEqual([], era["weather"]["snapshot_ids"])

    def test_founders_chain_from_the_previous_eras_elites(self):
        expected = [
            elite["grid"]["grid_id"] for elite in self.first_era["elites"]
        ]
        self.assertEqual(
            expected, self.second_era["founders_submitted"]
        )
        self.assertEqual(
            self.campaign.campaign["base_seed"] + ERA_SEED_STRIDE,
            self.second_era["rng_seed"],
        )

    def test_weather_rides_the_engine_report(self):
        self.assertTrue(self.second_era["weather"]["snapshot_ids"])
        self.assertTrue(
            all(
                snapshot.startswith("weather_stable_")
                for snapshot in self.second_era["weather"]["snapshot_ids"]
            )
        )

    def test_species_memory_is_report_fields_verbatim(self):
        memory = self.campaign.species_memory()
        self.assertEqual(2, memory["eras_run"])
        last = memory["last_era"]
        self.assertEqual(
            self.second_era["report"]["summary"]["archive"][
                "filled_niches"
            ],
            last["filled_niches"],
        )
        self.assertIsInstance(memory["unlocks"], list)

    def test_best_elite_is_adoptable_through_the_engine_gate(self):
        from mecha_engine.lifecycle import initial_state

        grid = self.campaign.best_elite_grid()
        self.assertIsNotNone(grid)
        state = initial_state(grid, self.inputs["slip_profile"])
        self.assertTrue(state["alive"])

    def test_succession_is_extinctions_door(self):
        self.assertIsNone(self.campaign.plan_succession())
        with self.assertRaises(ValueError):
            self.campaign.successor()
        ended = KeeperCampaign(
            self.inputs, era_config=TINY_ERA, campaign_id="ended"
        )
        ended.campaign["status"] = "extinct"
        successor = ended.successor()
        self.assertEqual(
            "ended", successor.campaign["predecessor_campaign_id"]
        )
        self.assertEqual(
            ended.campaign["base_seed"] + SUCCESSOR_SEED_OFFSET,
            successor.campaign["base_seed"],
        )
        self.assertEqual("active", successor.status)

    def test_ledger_round_trip(self):
        from mecha_engine.storage import campaign_history, open_ledger

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "campaign.sqlite3"
            self.campaign.save(path)
            # Idempotent re-save: no duplicate era rows.
            self.campaign.save(path)
            conn = open_ledger(path)
            try:
                history = campaign_history(conn, "test_campaign")
            finally:
                conn.close()
        self.assertEqual(2, len(history["eras"]))
        self.assertEqual(
            self.first_era["report"], history["eras"][0]["report"]
        )

    def test_model_cache_is_byte_equal_to_fresh_training(self):
        # F11: the repair model is the slow trainer; the cache must be
        # invisible — byte-equal results, keyed on corpus+epochs+seed.
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            cached_inputs = load_campaign_inputs(
                SEED_DIR,
                SLIP_PATH,
                ADOPTED,
                repair_epochs=6,
                seed_limit=12,
                cache_dir=tmp,
            )
            self.assertEqual(
                json.dumps(self.inputs["repair_model"], sort_keys=True),
                json.dumps(
                    cached_inputs["repair_model"], sort_keys=True
                ),
            )
            cache_files = list(Path(tmp).glob("repair_model_*.json"))
            self.assertEqual(1, len(cache_files))
            # The second load HITS the cache (mtime untouched).
            before = cache_files[0].stat().st_mtime_ns
            reloaded = load_campaign_inputs(
                SEED_DIR,
                SLIP_PATH,
                ADOPTED,
                repair_epochs=6,
                seed_limit=12,
                cache_dir=tmp,
            )
            self.assertEqual(
                before, cache_files[0].stat().st_mtime_ns
            )
            self.assertEqual(
                json.dumps(self.inputs["repair_model"], sort_keys=True),
                json.dumps(reloaded["repair_model"], sort_keys=True),
            )

    def test_eras_are_deterministic(self):
        twin = KeeperCampaign(
            self.inputs, era_config=TINY_ERA, campaign_id="twin"
        )
        era = twin.advance_era("calm")
        self.assertEqual(self.first_era['report'], era['report'])
        self.assertEqual(self.first_era['elites'], era['elites'])
        self.assertEqual('test_campaign', self.first_era['execution']['manifest']['campaign_id'])
        self.assertEqual('twin', era['execution']['manifest']['campaign_id'])
        # Campaign identity is new evidence, not an evolution parameter. Every
        # other result and immutable input byte still compares in full.
        era['execution']['manifest']['campaign_id'] = 'test_campaign'
        self.assertEqual(
            json.dumps(self.first_era, sort_keys=True),
            json.dumps(era, sort_keys=True),
        )


if __name__ == "__main__":
    unittest.main()
