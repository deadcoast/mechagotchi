"""G4 gates — real weather: the zero-seam-change promise, verified.

The G2-ingested REAL snapshot records drop into the engine's
`cubff_pressure_source` seam UNMODIFIED (the records verbatim from
the committed ingest report; the seam reads every field defensively —
DR 0018/0020's design). A real-weather era runs, and the era record's
weather provenance carries the REAL snapshot ids the engine itself
reported per generation.
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
    WEATHER_NAMES,
    KeeperCampaign,
    build_weather_source,
    load_campaign_inputs,
    load_real_weather_source,
)

SEED_DIR = ROOT / "data" / "seed_grids_16x16"
SLIP_PATH = ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json"
ADOPTED = (
    ROOT / "data" / "readability_benchmark" / "adopted_readability_model.json"
)
INGEST_REPORT = (
    ROOT / "data" / "cubff_real_ingest" / "real_snapshot_ingest_stage0_report.json"
)


class RealWeatherSourceTests(unittest.TestCase):
    def test_real_is_a_named_forecast(self):
        self.assertIn("real", WEATHER_NAMES)

    def test_the_source_is_the_ingested_records_verbatim(self):
        report = json.loads(INGEST_REPORT.read_text(encoding="utf-8"))
        source = load_real_weather_source()
        self.assertEqual(
            len(report["ingested_snapshots"]), len(source)
        )
        by_epoch = sorted(
            report["ingested_snapshots"], key=lambda s: s["epoch"]
        )
        self.assertEqual(by_epoch, source)  # verbatim, epoch order
        for record in source:
            self.assertEqual(
                "real_cubff_checkpoint", record["source_type"]
            )
        self.assertEqual(source, build_weather_source("real"))


class RealWeatherEraTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = load_campaign_inputs(
            SEED_DIR, SLIP_PATH, ADOPTED, repair_epochs=6, seed_limit=12
        )
        cls.campaign = KeeperCampaign(
            cls.inputs, era_config=TINY_ERA_CONFIG, campaign_id="rw"
        )
        cls.era = cls.campaign.advance_era("real")

    def test_a_real_weather_era_runs(self):
        self.assertEqual("real", self.era["weather"]["forecast"])
        self.assertEqual(
            len(self.era["report"]["generations"]),
            self.era["derived"]["generations_ran"],
        )

    def test_provenance_is_the_engines_own_per_generation_report(self):
        real_ids = {
            record["snapshot_id"]
            for record in load_real_weather_source()
        }
        reported = self.era["weather"]["snapshot_ids"]
        self.assertTrue(reported)
        for snapshot_id in reported:
            self.assertIn(snapshot_id, real_ids)
        by_generation = self.era["report"]["cubff_pressure"][
            "by_generation"
        ]
        self.assertEqual(
            [entry["snapshot_id"] for entry in by_generation],
            reported,
        )
        for entry in by_generation:
            self.assertIn("dropout_multiplier", entry)

    def test_real_weather_is_deterministic(self):
        twin = KeeperCampaign(
            self.inputs, era_config=TINY_ERA_CONFIG, campaign_id="rw"
        )
        era = twin.advance_era("real")
        self.assertEqual(
            json.dumps(self.era, sort_keys=True),
            json.dumps(era, sort_keys=True),
        )


if __name__ == "__main__":
    unittest.main()
